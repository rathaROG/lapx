// Copyright (c) 2016 Vadim Markovtsev (source{d})
// Copyright (c) 2026 Ratha SIV
// Scalar JV adapted from src/_lapjvs/lapjvs.h. See ../LICENSE.

use std::cell::RefCell;
use std::ops::{Add, Sub};

macro_rules! profile_count {
    ($solver:expr, $field:ident, $count:expr) => {
        #[cfg(feature = "profile")]
        {
            $solver.profile.$field += $count as u64;
        }
    };
}
macro_rules! profile_phase {
    ($solver:expr, $field:ident, $timer:ident) => {
        #[cfg(feature = "profile")]
        {
            $solver.profile.$field += $timer.elapsed().as_nanos() as u64;
            $timer = std::time::Instant::now();
        }
    };
}
macro_rules! profile_finish {
    ($solver:expr, $field:ident, $timer:ident) => {
        #[cfg(feature = "profile")]
        {
            $solver.profile.$field += $timer.elapsed().as_nanos() as u64;
        }
    };
}

#[cfg(feature = "cpp-completion")]
mod cpp_completion;
mod ffi;
#[cfg(feature = "profile")]
pub mod profile;
mod rectangular;

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Error {
    Infeasible = 1,
    Allocation = 2,
    Internal = 3,
    Dimensions = 4,
    BackendUnavailable = 5,
}

/// Completion strategy for required square assignments. Both families share
/// initialization, row reduction, rectangular solving, and workspace storage.
#[derive(Clone, Copy)]
pub enum Completion {
    Rust,
    #[cfg(feature = "cpp-completion")]
    Cpp,
}

pub trait Cost:
    'static + Copy + Default + PartialOrd + Add<Output = Self> + Sub<Output = Self>
{
    const INF: Self;
    const EPSILON: f64;
    fn finite(self) -> bool;
    fn from_f64(value: f64) -> Self;
    fn to_f64(self) -> f64;
    fn square_minima(row: &[Self], dual: &[f64]) -> (f64, f64, usize, usize);
}

macro_rules! cost_type {
    ($t:ty, $minima:ident) => {
        impl Cost for $t {
            const INF: Self = Self::INFINITY;
            const EPSILON: f64 = Self::EPSILON as f64;
            fn finite(self) -> bool {
                self.is_finite()
            }
            fn from_f64(value: f64) -> Self {
                value as Self
            }
            fn to_f64(self) -> f64 {
                self as f64
            }
            #[inline(always)]
            fn square_minima(row: &[Self], dual: &[f64]) -> (f64, f64, usize, usize) {
                $minima(row, dual)
            }
        }
    };
}
cost_type!(f32, float32_row_minima);
cost_type!(f64, required_row_minima);

fn resize<T: Clone>(v: &mut Vec<T>, n: usize, value: T) -> Result<(), Error> {
    if n > v.len() {
        v.try_reserve(n - v.len()).map_err(|_| Error::Allocation)?;
        v.resize(n, value);
    }
    Ok(())
}

#[derive(Default)]
pub struct Workspace {
    #[cfg(feature = "profile")]
    pub profile: profile::Profile,
    x: Vec<usize>,
    y: Vec<usize>,
    columns: Vec<usize>,
    matches: Vec<usize>,
    predecessor: Vec<usize>,
    // Keep cancellation in reduced costs out of float32 arithmetic. Inputs
    // remain borrowed in their original precision; only linear scratch widens.
    distance: Vec<f64>,
    potential: Vec<f64>,
}

const FREE: usize = usize::MAX;

// Share the required scan without inlining it into the larger solver bodies:
// their register pressure otherwise makes this hot loop compiler-sensitive.
// Starting at infinity preserves column order, including a forbidden column 0.
#[inline(never)]
fn required_row_minima<T: Cost>(row: &[T], dual: &[T]) -> (T, T, usize, usize) {
    let mut min = T::INF;
    let mut second = T::INF;
    let mut first_column = FREE;
    let mut second_column = FREE;
    for (j, (&cost, &potential)) in row.iter().zip(dual).enumerate() {
        let value = cost - potential;
        if value < second {
            if value >= min {
                second = value;
                second_column = j;
            } else {
                second = min;
                min = value;
                second_column = first_column;
                first_column = j;
            }
        }
    }
    (min, second, first_column, second_column)
}

#[inline(always)]
fn scan_float32_row<const GROUPED: bool>(row: &[f32], dual: &[f64]) -> (f64, f64, usize, usize) {
    let mut min = f64::INFINITY;
    let mut second = f64::INFINITY;
    let mut first_column = FREE;
    let mut second_column = FREE;
    let count = row.len().min(dual.len());
    let mut scan = |start: usize, costs: &[f32], potentials: &[f64], screen: bool| {
        if screen {
            let mut possible = false;
            for (&cost, &potential) in costs.iter().zip(potentials) {
                possible |= cost.to_f64() - potential < second;
            }
            if !possible {
                return;
            }
        }
        for (offset, (&cost, &potential)) in costs.iter().zip(potentials).enumerate() {
            let j = start + offset;
            let value = cost.to_f64() - potential;
            if value < second {
                if value >= min {
                    second = value;
                    second_column = j;
                } else {
                    second = min;
                    min = value;
                    second_column = first_column;
                    first_column = j;
                }
            }
        }
    };
    if GROUPED {
        // Screen fixed-size groups in float64 so the compiler can widen and
        // compare several costs together. A skipped group cannot improve
        // either minimum. Scan promising groups in order to preserve ties.
        const GROUP_SIZE: usize = 8;
        let grouped = count / GROUP_SIZE * GROUP_SIZE;
        for start in (0..grouped).step_by(GROUP_SIZE) {
            let costs = &row[start..start + GROUP_SIZE];
            let potentials = &dual[start..start + GROUP_SIZE];
            scan(start, costs, potentials, true);
        }
        scan(grouped, &row[grouped..count], &dual[grouped..count], false);
    } else {
        scan(0, row, dual, false);
    }
    (min, second, first_column, second_column)
}

// Keep long scans separate from allocation and shortest-path state.
#[inline(never)]
fn grouped_float32_row_minima(row: &[f32], dual: &[f64]) -> (f64, f64, usize, usize) {
    scan_float32_row::<true>(row, dual)
}

#[inline(always)]
fn float32_row_minima(row: &[f32], dual: &[f64]) -> (f64, f64, usize, usize) {
    // Avoid a helper call per row on very small matrices.
    if row.len() <= 16 {
        scan_float32_row::<false>(row, dual)
    } else {
        grouped_float32_row_minima(row, dual)
    }
}

#[inline(always)]
fn column_minima<T: Cost, D: Cost>(costs: &[T], n: usize, dual: &mut [D], owners: &mut [usize]) {
    for (value, &cost) in dual.iter_mut().zip(costs) {
        *value = D::from_f64(cost.to_f64());
    }
    owners.fill(0);
    for (i, row) in costs.chunks_exact(n).enumerate().skip(1) {
        for ((value, owner), &cost) in dual.iter_mut().zip(owners.iter_mut()).zip(row) {
            let cost = D::from_f64(cost.to_f64());
            if cost < *value {
                *value = cost;
                *owner = i;
            }
        }
    }
}

#[inline(never)]
fn initialize_columns<T: Cost>(costs: &[T], n: usize, dual: &mut [f64], owners: &mut [usize]) {
    // Finding a column minimum needs comparisons, not subtraction.
    // For small float32 squares, compare in float32 before widening the
    // minima. Isolate the temporary array from the main solver stack frame.
    if T::EPSILON == f32::EPSILON as f64 && n <= 128 {
        let mut initial = [0.0f32; 128];
        column_minima(costs, n, &mut initial[..n], owners);
        for (value, &cost) in dual.iter_mut().zip(initial.iter()) {
            *value = cost as f64;
        }
    } else {
        column_minima(costs, n, dual, owners);
    }
}

mod square;

#[derive(Default)]
struct Worker<T> {
    orientation: Vec<T>,
    scratch: Workspace,
    rectangular: rectangular::Rectangular<T>,
}

impl<T: Cost> Worker<T> {
    fn release_large_buffers(&mut self) {
        // Bound retained orientation copies per native thread.
        if self.orientation.capacity() > 8 * 1024 * 1024 / std::mem::size_of::<T>() {
            self.orientation = Vec::new();
        }
        if self.scratch.x.capacity() > 65536 {
            self.scratch = Workspace::default();
        }
        if self.rectangular.y.capacity() > 65536 {
            self.rectangular = rectangular::Rectangular::default();
        }
    }
}

thread_local! {
    static F32_WORKER: RefCell<Worker<f32>> = RefCell::new(Worker::default());
    static F64_WORKER: RefCell<Worker<f64>> = RefCell::new(Worker::default());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn grouped_square_minima_match_full_precision_scan() {
        let mut seed = 1384u64;
        for n in (0..=80).chain([511, 512, 1000]) {
            for sample in 0..24 {
                let mut row = Vec::new();
                let mut dual = Vec::new();
                for j in 0..n {
                    seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                    let cost = ((seed >> 32) % 101) as f32 - 50.0;
                    row.push(if j % 13 == 0 { f32::INFINITY } else { cost });
                    // Include exact ties, cancellation, and potentials beyond
                    // float32's range. Screening must never hide a minimum.
                    dual.push(match sample % 4 {
                        0 => cost as f64,
                        1 => cost as f64 + (j % 3) as f64 * 1e-8,
                        2 => -1e100,
                        _ => 1e100,
                    });
                }
                let mut ordered: Vec<(f64, usize)> = row
                    .iter()
                    .zip(&dual)
                    .enumerate()
                    .map(|(j, (&cost, &v))| (cost as f64 - v, j))
                    .filter(|&(value, _)| value.is_finite())
                    .collect();
                ordered.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap().then(a.1.cmp(&b.1)));
                ordered.extend([(f64::INFINITY, FREE); 2]);
                assert_eq!(
                    float32_row_minima(&row, &dual),
                    (ordered[0].0, ordered[1].0, ordered[0].1, ordered[1].1)
                );
            }
        }
    }

    fn brute_force(a: &[f64], n: usize, row: usize, used: usize) -> f64 {
        if row == n {
            return 0.0;
        }
        (0..n)
            .filter(|&j| used & (1 << j) == 0)
            .map(|j| a[row * n + j] + brute_force(a, n, row + 1, used | (1 << j)))
            .fold(f64::INFINITY, f64::min)
    }

    #[test]
    #[allow(clippy::manual_is_multiple_of)] // Keep tests usable on older Rust compilers.
    fn seeded_ties_negative_and_forbidden_against_enumeration() {
        let mut workspace = Workspace::default();
        let mut seed = 19u64;
        for n in 1..=7 {
            for sample in 0..90 {
                let a: Vec<f64> = (0..n * n)
                    .map(|k| {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        if sample % 3 == 0 && k / n != k % n && seed % 5 == 0 {
                            f64::INFINITY
                        } else {
                            ((seed >> 32) % 21) as f64 - 10.0
                        }
                    })
                    .collect();
                let expected = brute_force(&a, n, 0, 0);
                let assignment = workspace.solve(&a, n).unwrap_or_else(|error| {
                    panic!("{error:?}: n={n}, sample={sample}, costs={a:?}")
                });
                let actual: f64 = assignment
                    .iter()
                    .enumerate()
                    .map(|(i, &j)| a[i * n + j])
                    .sum();
                assert_eq!(actual, expected, "n={n}, sample={sample}, costs={a:?}");
            }
        }
    }

    #[test]
    fn infeasible_then_reuse_and_singleton_large_cost() {
        let mut workspace = Workspace::default();
        assert_eq!(
            workspace.solve(&[1.0, f64::INFINITY, 2.0, f64::INFINITY], 2),
            Err(Error::Infeasible)
        );
        assert_eq!(workspace.solve(&[1e100], 1).unwrap(), &[0]);
        assert_eq!(workspace.solve(&[1.0, 8.0, 8.0, 1.0], 2).unwrap(), &[0, 1]);
    }

    #[test]
    fn larger_square_primal_dual_certificate() {
        let mut workspace = Workspace::default();
        let mut seed = 883u64;
        for n in [8, 9, 16, 32, 64] {
            for _ in 0..40 {
                let a: Vec<f64> = (0..n * n)
                    .map(|k| {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        if k / n != k % n && seed % 7 == 0 {
                            f64::INFINITY
                        } else {
                            ((seed >> 32) % 101) as f64 - 50.
                        }
                    })
                    .collect();
                workspace.solve(&a, n).unwrap();
                let mut primal = 0.;
                let mut dual: f64 = workspace.potential[..n].iter().sum();
                for i in 0..n {
                    let j = workspace.x[i];
                    assert_eq!(workspace.y[j], i);
                    let u = a[i * n + j] - workspace.potential[j];
                    primal += a[i * n + j];
                    dual += u;
                    for k in 0..n {
                        assert!(u + workspace.potential[k] <= a[i * n + k]);
                    }
                }
                assert_eq!(primal, dual);
            }
        }
    }

    #[test]
    fn conflicting_blocks_primal_dual_certificate() {
        let mut workspace = Workspace::default();
        for mut seed in [883u64, 97031, 1384] {
            for n in [250, 129, 128, 127] {
                let costs: Vec<f64> = (0..n * n)
                    .map(|k| {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        if (k / n < 3 * n / 4) == (k % n < n / 4) {
                            ((seed >> 32) % 8) as f64
                        } else {
                            80.0
                        }
                    })
                    .collect();
                workspace.solve(&costs, n).unwrap();
                let mut primal = 0.0;
                let mut dual: f64 = workspace.potential[..n].iter().sum();
                for (i, row) in costs.chunks_exact(n).enumerate() {
                    let j = workspace.x[i];
                    assert_eq!(workspace.y[j], i);
                    let u = row[j] - workspace.potential[j];
                    primal += row[j];
                    dual += u;
                    for (k, &cost) in row.iter().enumerate() {
                        assert!(u + workspace.potential[k] <= cost);
                    }
                }
                assert_eq!(primal, dual);
            }
        }
    }

    #[test]
    fn heterogeneous_rows_primal_dual_certificate() {
        let mut workspace = Workspace::default();
        let mut row_workspace = rectangular::Rectangular::<f64>::default();
        let mut seed = 97031u64;
        for n in [750, 513, 512, 511] {
            for offset in [-100., 0., 100.] {
                let mut costs: Vec<f64> = (0..n * n)
                    .map(|_| {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        offset + 80. + ((seed >> 32) % 21) as f64
                    })
                    .collect();
                for i in 0..3 * n / 4 {
                    costs[i * n + (i * 7 + 3) % n] = offset;
                }
                workspace.solve(&costs, n).unwrap();
                let mut primal = 0.;
                let mut dual: f64 = workspace.potential[..n].iter().sum();
                for i in 0..n {
                    let j = workspace.x[i];
                    assert_eq!(workspace.y[j], i);
                    let u = costs[i * n + j] - workspace.potential[j];
                    primal += costs[i * n + j];
                    dual += u;
                    for k in 0..n {
                        assert!(u + workspace.potential[k] <= costs[i * n + k]);
                    }
                }
                assert_eq!(primal, dual);
                row_workspace.solve(&costs, n, n).unwrap();
                let row_primal: f64 = row_workspace.x[..n]
                    .iter()
                    .enumerate()
                    .map(|(i, &j)| costs[i * n + j])
                    .sum();
                assert_eq!(row_primal, primal);
            }
        }
    }
}
