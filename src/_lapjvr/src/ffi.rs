use super::*;
use rayon::prelude::*;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::slice;
use std::sync::{Arc, Mutex, OnceLock};

// R/H share at most two cached worker configurations, for automatic and
// explicit counts alike. Use process spawning rather than fork after use.
type PoolCache = Mutex<Vec<(usize, Arc<rayon::ThreadPool>)>>;
static POOLS: OnceLock<PoolCache> = OnceLock::new();

fn pool(threads: usize, batch: usize) -> Result<Arc<rayon::ThreadPool>, Error> {
    pool_from_cache(POOLS.get_or_init(|| Mutex::new(Vec::new())), threads, batch)
}

fn pool_from_cache(
    pools: &PoolCache,
    threads: usize,
    batch: usize,
) -> Result<Arc<rayon::ThreadPool>, Error> {
    let threads = threads.max(1).min(batch.max(1));
    let mut cache = pools.lock().map_err(|_| Error::Internal)?;
    if let Some((_, pool)) = cache.iter().find(|(n, _)| *n == threads) {
        return Ok(pool.clone());
    }
    let new = Arc::new(
        rayon::ThreadPoolBuilder::new()
            .num_threads(threads)
            .build()
            .map_err(|_| Error::Allocation)?,
    );
    let evicted = if cache.len() == 2 {
        Some(cache.remove(0))
    } else {
        None
    };
    cache.push((threads, new.clone()));
    drop(cache);
    drop(evicted);
    Ok(new)
}

fn auto_parallel(rows: usize, cols: usize, batch: usize) -> bool {
    // Cheap, overflow-safe work estimate. Weight the actual cost size by the
    // smaller dimension, capped to avoid treating every large problem as cubic.
    // Keep this independent of cost values and never perform trial solves.
    let elements = rows.saturating_mul(cols).saturating_mul(batch);
    let work = elements.saturating_mul(rows.min(cols).min(32));
    let near = rows.max(cols) <= rows.min(cols).saturating_mul(2);
    // Rectangles with scarce spare columns can do substantial row reduction
    // even in small batches; square initialization often finishes more cheaply.
    let competitive = rows != cols && rows.max(cols) - rows.min(cols) <= rows.min(cols) / 8;
    let threshold = if batch < 8 && !competitive {
        524_288
    } else {
        262_144
    };
    batch > 1 && (elements >= 65_536 || (near && work >= threshold))
}

enum Original<'a> {
    F32(&'a [f32]),
    F64(&'a [f64]),
}
impl Original<'_> {
    fn at(&self, i: usize) -> f64 {
        match self {
            Self::F32(a) => a[i] as f64,
            Self::F64(a) => a[i],
        }
    }
}

struct Problem {
    rows: usize,
    cols: usize,
    limit: f64,
    pairs: bool,
    total: bool,
    completion: Completion,
}

fn transpose_into<T: Copy>(input: &[T], rows: usize, cols: usize, output: &mut [T]) {
    // Keep a small tile of both matrices in cache. Reading a whole strided
    // column at once repeatedly evicts the cache lines needed by its neighbors.
    const TILE: usize = 32;
    for col_start in (0..cols).step_by(TILE) {
        for row_start in (0..rows).step_by(TILE) {
            let col_end = (col_start + TILE).min(cols);
            let row_end = (row_start + TILE).min(rows);
            for col in col_start..col_end {
                for row in row_start..row_end {
                    output[col * rows + row] = input[row * cols + col];
                }
            }
        }
    }
}

fn solve_one<T: Cost>(
    worker: &mut Worker<T>,
    input: &[T],
    original: &Original<'_>,
    base: usize,
    p: &Problem,
    output: &mut [i64],
) -> Result<(usize, f64), Error> {
    let Worker {
        orientation,
        scratch,
        rectangular,
        ..
    } = worker;
    let r = p.rows.min(p.cols);
    let c = p.rows.max(p.cols);
    let transpose = p.rows > p.cols;
    let finite_limit = p.limit.is_finite();
    // Round each half-limit just as the padded checkpoint did. The optional
    // row penalty is their sum; extra unmatched columns add only a constant.
    let reject = T::from_f64(p.limit / 2.0);
    let penalty = reject + reject;
    // Required squares use the square core. Finite limits use the optional
    // core directly, with a fixed row-reduction bound for square inputs.
    let use_square = r == c && !finite_limit;
    if use_square {
        scratch.solve_with(input, c, p.completion)?;
    }
    let (assignment, inverse) = if use_square {
        (&scratch.x[..r], &scratch.y[..c])
    } else {
        // Wide input can be borrowed directly. Tall input needs only an R*C
        // orientation copy, never a C*C padded matrix.
        let oriented = if transpose {
            resize(orientation, input.len(), T::default())?;
            transpose_into(input, p.rows, p.cols, &mut orientation[..input.len()]);
            &orientation[..input.len()]
        } else {
            input
        };
        if finite_limit {
            // The augmented objective is sum(real) + (R+C-2K)*reject.
            // Equivalently, charge 2*reject per unmatched real row and add
            // the constant (C-R)*reject. Preserve the old working-precision
            // rounding of each half-limit before combining the penalties.
            rectangular.solve_optional(oriented, r, c, penalty)?;
        } else {
            rectangular.solve(oriented, r, c)?;
        }
        (&rectangular.x[..r], &rectangular.y[..c])
    };
    let mut count = 0;
    let mut total = 0.0;
    // Tall input is enumerated through the inverse map to keep original rows sorted.
    if transpose {
        for (row, &col) in inverse.iter().enumerate() {
            if col < p.cols {
                write_pair(output, r, count, row, col, p.pairs);
                count += 1;
                if p.total {
                    total += original.at(base + row * p.cols + col);
                }
            }
        }
    } else {
        for (row, &col) in assignment.iter().enumerate() {
            if col < p.cols {
                write_pair(output, r, count, row, col, p.pairs);
                count += 1;
                if p.total {
                    total += original.at(base + row * p.cols + col);
                }
            }
        }
    }
    Ok((count, total))
}

#[cfg(feature = "profile")]
pub(crate) fn profile_finite<T: Cost>(
    costs: &[T],
    rows: usize,
    cols: usize,
    repeats: usize,
    limit: f64,
) -> Result<(Vec<super::profile::Profile>, f64, usize), Error> {
    let mut worker = Worker::default();
    let original: Vec<f64> = costs.iter().map(|v| v.to_f64()).collect();
    let p = Problem {
        rows,
        cols,
        limit,
        pairs: true,
        total: true,
        completion: Completion::Rust,
    };
    let mut out = vec![0; 2 * rows.min(cols)];
    let mut samples = Vec::new();
    let mut result = (0, 0.);
    for sample in 0..=repeats {
        worker.scratch.profile = super::profile::Profile::default();
        worker.rectangular.profile = super::profile::Profile::default();
        let started = std::time::Instant::now();
        result = solve_one(
            &mut worker,
            costs,
            &Original::F64(&original),
            0,
            &p,
            &mut out,
        )?;
        let optional = worker.rectangular.profile;
        let profile = super::profile::Profile {
            optional_ns: optional.initial_ns
                + optional.transfer_ns
                + optional.reduction_ns
                + optional.augment_ns,
            dispatch_ns: started.elapsed().as_nanos() as u64,
            ..optional
        };
        if sample > 0 {
            samples.push(profile);
        }
    }
    Ok((samples, result.1, result.0))
}

fn write_pair(out: &mut [i64], capacity: usize, i: usize, row: usize, col: usize, pairs: bool) {
    if pairs {
        out[2 * i] = row as i64;
        out[2 * i + 1] = col as i64;
    } else {
        out[i] = row as i64;
        out[capacity + i] = col as i64;
    }
}

trait Kernel: Cost + Send + Sync {
    fn with_worker<R>(f: impl FnOnce(&mut Worker<Self>) -> R) -> R;
}
impl Kernel for f32 {
    fn with_worker<R>(f: impl FnOnce(&mut Worker<Self>) -> R) -> R {
        F32_WORKER.with(|w| {
            let mut worker = w.borrow_mut();
            let result = f(&mut worker);
            worker.release_large_buffers();
            result
        })
    }
}
impl Kernel for f64 {
    fn with_worker<R>(f: impl FnOnce(&mut Worker<Self>) -> R) -> R {
        F64_WORKER.with(|w| {
            let mut worker = w.borrow_mut();
            let result = f(&mut worker);
            worker.release_large_buffers();
            result
        })
    }
}

fn batch<T: Kernel>(
    input: &[T],
    original: &Original<'_>,
    p: &Problem,
    workers: (usize, bool),
    output: &mut [i64],
    counts: &mut [usize],
    totals: &mut [f64],
) -> Result<(), (usize, Error)> {
    let (threads, automatic) = workers;
    let elements = p.rows * p.cols;
    let stride = 2 * p.rows.min(p.cols);
    if threads <= 1
        || counts.len() <= 1
        || (automatic && !auto_parallel(p.rows, p.cols, counts.len()))
    {
        return T::with_worker(|worker| {
            for (b, ((out, count), total)) in output
                .chunks_exact_mut(stride)
                .zip(counts)
                .zip(totals)
                .enumerate()
            {
                let base = b * elements;
                let result = solve_one(
                    worker,
                    &input[base..base + elements],
                    original,
                    base,
                    p,
                    out,
                )
                .map_err(|e| (b, e))?;
                *count = result.0;
                *total = result.1;
            }
            Ok(())
        });
    }
    let pool = pool(threads, counts.len()).map_err(|e| (0, e))?;
    let statuses: Vec<Result<(), Error>> = pool.install(|| {
        output
            .par_chunks_mut(stride)
            .zip(counts.par_iter_mut())
            .zip(totals.par_iter_mut())
            .enumerate()
            .map(|(b, ((out, count), total))| {
                T::with_worker(|worker| {
                    let base = b * elements;
                    let (n, cost) = solve_one(
                        worker,
                        &input[base..base + elements],
                        original,
                        base,
                        p,
                        out,
                    )?;
                    *count = n;
                    *total = cost;
                    Ok(())
                })
            })
            .collect()
    });
    for (b, status) in statuses.into_iter().enumerate() {
        status.map_err(|e| (b, e))?;
    }
    Ok(())
}

/// C boundary for the Cython adapter. Every pointer must be aligned, non-null,
/// and valid for its described length; inputs must remain immutable throughout
/// this call, outputs must be disjoint and exclusively owned by this call.
/// Panics are contained here and never unwind through Python/C++ frames.
#[no_mangle]
pub unsafe extern "C" fn lapjvr_run(
    costs: *const std::ffi::c_void,
    cost32: i32,
    original: *const std::ffi::c_void,
    original32: i32,
    b: usize,
    rows: usize,
    cols: usize,
    limit: f64,
    threads: usize,
    automatic: i32,
    pairs: i32,
    return_cost: i32,
    hybrid: i32,
    output: *mut i64,
    counts: *mut usize,
    totals: *mut f64,
    error_index: *mut usize,
) -> i32 {
    let result = catch_unwind(AssertUnwindSafe(|| {
        let completion = match hybrid {
            0 => Completion::Rust,
            #[cfg(feature = "cpp-completion")]
            1 => Completion::Cpp,
            _ => return Err((0, Error::BackendUnavailable)),
        };
        if b == 0 || rows == 0 || cols == 0 {
            return Ok(());
        }
        let length = rows
            .checked_mul(cols)
            .and_then(|n| n.checked_mul(b))
            .ok_or((0, Error::Dimensions))?;
        let out_len = rows
            .min(cols)
            .checked_mul(2)
            .and_then(|n| n.checked_mul(b))
            .ok_or((0, Error::Dimensions))?;
        if length > isize::MAX as usize / 8 || out_len > isize::MAX as usize / 8 {
            return Err((0, Error::Dimensions));
        }
        let original = if original32 != 0 {
            Original::F32(slice::from_raw_parts(original.cast::<f32>(), length))
        } else {
            Original::F64(slice::from_raw_parts(original.cast::<f64>(), length))
        };
        let out = slice::from_raw_parts_mut(output, out_len);
        let counts = slice::from_raw_parts_mut(counts, b);
        let totals = slice::from_raw_parts_mut(totals, b);
        let problem = Problem {
            rows,
            cols,
            limit,
            pairs: pairs != 0,
            total: return_cost != 0,
            completion,
        };
        if cost32 != 0 {
            batch(
                slice::from_raw_parts(costs.cast::<f32>(), length),
                &original,
                &problem,
                (threads, automatic != 0),
                out,
                counts,
                totals,
            )
        } else {
            batch(
                slice::from_raw_parts(costs.cast::<f64>(), length),
                &original,
                &problem,
                (threads, automatic != 0),
                out,
                counts,
                totals,
            )
        }
    }));
    match result {
        Ok(Ok(())) => 0,
        Ok(Err((b, error))) => {
            *error_index = b;
            error as i32
        }
        Err(_) => {
            *error_index = 0;
            Error::Internal as i32
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn worker_pool_cache_reuses_entries_and_keeps_evicted_pools_usable() {
        // Other native tests may evict shared pools between calls. Check
        // identity with a private cache using the same production code.
        let cache = Mutex::new(Vec::new());
        let first = pool_from_cache(&cache, 2, 32).unwrap();
        assert!(Arc::ptr_eq(
            &first,
            &pool_from_cache(&cache, 2, 100).unwrap()
        ));

        let second = pool_from_cache(&cache, 3, 32).unwrap();
        let third = pool_from_cache(&cache, 4, 32).unwrap();
        assert_eq!(cache.lock().unwrap().len(), 2);
        assert!(Arc::ptr_eq(
            &second,
            &pool_from_cache(&cache, 3, 100).unwrap()
        ));
        assert!(Arc::ptr_eq(
            &third,
            &pool_from_cache(&cache, 4, 100).unwrap()
        ));

        // Eviction releases only the cache's reference. A held pool still
        // runs, and requesting its count again creates a different pool.
        assert_eq!(first.install(rayon::current_num_threads), 2);
        let replacement = pool_from_cache(&cache, 2, 32).unwrap();
        assert!(!Arc::ptr_eq(&first, &replacement));
        assert_eq!(replacement.install(rayon::current_num_threads), 2);
        assert_eq!(cache.lock().unwrap().len(), 2);
    }

    #[test]
    fn worker_pools_honor_counts_above_eight_and_cap_at_batch_size() {
        let first = pool(16, 32).unwrap();
        assert_eq!(first.current_num_threads(), 16);
        assert_eq!(first.install(rayon::current_num_threads), 16);
        for (requested, batch, expected) in [(24, 12, 12), (256, 3, 3), (128, 1, 1)] {
            let selected = pool(requested, batch).unwrap();
            assert_eq!(selected.current_num_threads(), expected);
            assert_eq!(selected.install(rayon::current_num_threads), expected);
        }
        std::thread::scope(|scope| {
            for threads in [3, 12, 16, 24] {
                scope.spawn(move || {
                    let selected = pool(threads, 32).unwrap();
                    assert_eq!(selected.install(rayon::current_num_threads), threads);
                });
            }
        });
        // Eviction only drops the cache's reference; an in-flight call can
        // still use the original pool while other counts are requested.
        assert_eq!(first.install(rayon::current_num_threads), 16);
        assert!(POOLS.get().unwrap().lock().unwrap().len() <= 2);
    }

    #[test]
    fn auto_estimate_handles_overflow_orientation_and_singleton_batches() {
        for (r, c) in [
            (0, 0),
            (1, 100),
            (16, 128),
            (100, 150),
            (usize::MAX, usize::MAX),
        ] {
            for b in [0, 1, 2, 8, 64, usize::MAX] {
                assert_eq!(auto_parallel(r, c, b), auto_parallel(c, r, b));
                if b <= 1 {
                    assert!(!auto_parallel(r, c, b));
                }
            }
        }
        assert!(auto_parallel(usize::MAX, usize::MAX, usize::MAX));
    }

    #[test]
    fn auto_worker_releases_oversized_orientation_and_linear_scratch() {
        let mut worker = Worker::<f64> {
            orientation: vec![0.; 8 * 1024 * 1024 / 8 + 1],
            ..Worker::default()
        };
        worker.scratch.x = vec![0; 65537];
        worker.rectangular.y = vec![0; 65537];
        worker.release_large_buffers();
        assert_eq!(worker.orientation.capacity(), 0);
        assert_eq!(worker.scratch.x.capacity(), 0);
        assert_eq!(worker.rectangular.y.capacity(), 0);
    }

    #[test]
    fn ordinary_rectangles_do_not_allocate_a_square_cost_matrix() {
        for (rows, cols) in [(3, 10000), (10000, 3)] {
            let input = vec![1.0; rows * cols];
            let original = Original::F64(&input);
            let p = Problem {
                rows,
                cols,
                limit: f64::INFINITY,
                pairs: true,
                total: true,
                completion: Completion::Rust,
            };
            let mut worker = Worker::<f64>::default();
            let mut output = vec![0; 2 * rows.min(cols)];
            let (count, total) =
                solve_one(&mut worker, &input, &original, 0, &p, &mut output).unwrap();
            assert_eq!(count, 3);
            assert_eq!(total, 3.0);
            assert!(worker.scratch.x.is_empty());
            assert_eq!(
                worker.orientation.len(),
                if rows > cols { rows * cols } else { 0 }
            );
            assert_eq!(worker.rectangular.x.len(), 3);
            assert_eq!(worker.rectangular.y.len(), 10000);
        }
    }

    #[test]
    fn finite_limits_do_not_allocate_dummy_costs_or_assignments() {
        for (rows, cols) in [(3, 10000), (10000, 3), (10, 10)] {
            let input = vec![1.0; rows * cols];
            let original = Original::F64(&input);
            let p = Problem {
                rows,
                cols,
                limit: 0.5,
                pairs: true,
                total: true,
                completion: Completion::Rust,
            };
            let mut worker = Worker::<f64>::default();
            let mut output = vec![0; 2 * rows.min(cols)];
            assert_eq!(
                solve_one(&mut worker, &input, &original, 0, &p, &mut output).unwrap(),
                (0, 0.0)
            );
            assert!(worker.scratch.x.is_empty());
            assert_eq!(
                worker.orientation.len(),
                if rows > cols { rows * cols } else { 0 }
            );
            assert_eq!(worker.rectangular.x.len(), rows.min(cols));
            assert_eq!(worker.rectangular.y.len(), rows.max(cols));
        }
    }

    #[test]
    fn dense_conflicts_bypass_square_initialization_without_new_cost_storage() {
        let n = 64;
        let mut input = vec![0.75; n * n];
        for i in 0..n {
            for j in 0..n {
                if (i < 3 * n / 4) == (j < n / 4) {
                    input[i * n + j] = 0.125;
                }
            }
        }
        let mut worker = Worker::<f64>::default();
        let p = Problem {
            rows: n,
            cols: n,
            limit: 0.5,
            pairs: true,
            total: true,
            completion: Completion::Rust,
        };
        let mut output = vec![0; 2 * n];
        let (count, total) = solve_one(
            &mut worker,
            &input,
            &Original::F64(&input),
            0,
            &p,
            &mut output,
        )
        .unwrap();
        assert_eq!(count, n / 2);
        assert_eq!(total, count as f64 * 0.125);
        assert!(worker.scratch.x.is_empty());
        assert!(worker.orientation.is_empty());
        assert_eq!(worker.rectangular.x.len(), n);
        assert_eq!(worker.rectangular.y.len(), n);
    }
}
