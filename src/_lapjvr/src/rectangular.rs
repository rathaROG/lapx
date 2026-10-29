// Copyright (c) 2026 Ratha SIV | MIT License
// Rectangular JV: row reductions adapted from LAPX's scalar lapjvs strategy,
// followed by a shortest augmenting path with rectangular dual constraints.

use super::{required_row_minima, resize, Cost, Error, FREE};
use std::marker::PhantomData;

#[derive(Default)]
pub(crate) struct Rectangular<T> {
    #[cfg(feature = "profile")]
    pub(crate) profile: super::profile::Profile,
    pub(crate) x: Vec<usize>,
    pub(crate) y: Vec<usize>,
    free_rows: Vec<usize>,
    columns: Vec<usize>,
    predecessor: Vec<usize>,
    // Keep float32 cost storage while reducing cancellation in reduced costs
    // when a legitimate finite cost is much larger than the differences.
    distance: Vec<f64>,
    row_dual: Vec<f64>,
    column_dual: Vec<f64>,
    cost_type: PhantomData<T>,
}

struct Minimum {
    cost: f64,
    column: usize,
}

// The implicit unmatched choice wins ties and bounds both minima.
#[inline(always)]
fn scan_optional_row<T: Cost, const GROUPED: bool>(
    row: &[T],
    dual: &[f64],
    penalty: f64,
) -> [Minimum; 2] {
    let mut min = penalty;
    let mut second = penalty;
    let mut first_column = FREE;
    let mut second_column = FREE;
    let mut scan = |start: usize, costs: &[T], potentials: &[f64]| {
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
        // Eight columns per group reduce loop overhead while preserving
        // column order and deterministic tie handling. Scan the tail below.
        const GROUP_SIZE: usize = 8;
        let count = row.len().min(dual.len());
        let grouped = count / GROUP_SIZE * GROUP_SIZE;
        for start in (0..grouped).step_by(GROUP_SIZE) {
            scan(
                start,
                &row[start..start + GROUP_SIZE],
                &dual[start..start + GROUP_SIZE],
            );
        }
        scan(grouped, &row[grouped..count], &dual[grouped..count]);
    } else {
        scan(0, row, dual);
    }
    [
        Minimum {
            cost: min,
            column: first_column,
        },
        Minimum {
            cost: second,
            column: second_column,
        },
    ]
}

// Keep the larger scan independent of allocation and shortest-path state.
#[inline(never)]
fn grouped_optional_row_minima<T: Cost>(row: &[T], dual: &[f64], penalty: f64) -> [Minimum; 2] {
    scan_optional_row::<T, true>(row, dual, penalty)
}

#[inline(always)]
fn optional_row_minima<T: Cost>(row: &[T], dual: &[f64], penalty: f64) -> [Minimum; 2] {
    // A helper call per row costs more than it saves on very short scans.
    if row.len() <= 16 {
        scan_optional_row::<T, false>(row, dual, penalty)
    } else {
        grouped_optional_row_minima(row, dual, penalty)
    }
}

impl<T: Cost> Rectangular<T> {
    /// Match every row of a flat rows <= cols matrix, leaving extra columns
    /// unused. Scratch is O(rows + cols); no square cost buffer is created.
    pub(crate) fn solve(&mut self, costs: &[T], rows: usize, cols: usize) -> Result<(), Error> {
        self.solve_impl::<false>(costs, rows, cols, T::INF)
    }

    /// Each row may instead remain unmatched at `penalty`. The implicit sink
    /// replaces all dummy columns; no dummy costs or dummy assignments exist.
    pub(crate) fn solve_optional(
        &mut self,
        costs: &[T],
        rows: usize,
        cols: usize,
        penalty: T,
    ) -> Result<(), Error> {
        if !penalty.finite() {
            return Err(Error::Infeasible);
        }
        self.solve_impl::<true>(costs, rows, cols, penalty)
    }

    fn solve_impl<const OPTIONAL: bool>(
        &mut self,
        costs: &[T],
        rows: usize,
        cols: usize,
        penalty: T,
    ) -> Result<(), Error> {
        #[cfg(feature = "profile")]
        let mut phase_timer = std::time::Instant::now();
        #[cfg(feature = "profile")]
        {
            self.profile = super::profile::Profile::default();
        }
        if rows > cols || rows.checked_mul(cols) != Some(costs.len()) {
            return Err(Error::Dimensions);
        }
        if rows == 0 {
            return Ok(());
        }
        // The caller rounds each half-limit and their sum in the cost type.
        // Promote that represented penalty, rather than recomputing it here.
        let penalty = penalty.to_f64();
        resize(&mut self.x, rows, FREE)?;
        resize(&mut self.y, cols, FREE)?;
        resize(&mut self.free_rows, rows, 0)?;
        resize(&mut self.columns, cols, 0)?;
        resize(&mut self.predecessor, cols, FREE)?;
        resize(&mut self.distance, cols, f64::INFINITY)?;
        resize(&mut self.row_dual, rows, 0.0)?;
        resize(&mut self.column_dual, cols, 0.0)?;
        let x = &mut self.x[..rows];
        let y = &mut self.y[..cols];
        let free = &mut self.free_rows[..rows];
        let columns = &mut self.columns[..cols];
        let pred = &mut self.predecessor[..cols];
        let d = &mut self.distance[..cols];
        let u = &mut self.row_dual[..rows];
        let v = &mut self.column_dual[..cols];
        x.fill(FREE);
        y.fill(FREE);
        u.fill(0.0);
        v.fill(0.0);
        for (i, slot) in free.iter_mut().enumerate() {
            *slot = i;
        }
        profile_phase!(self, initial_ns, phase_timer);

        // Rectangular duals require v[j] <= 0, and unused columns must have
        // v[j] == 0. Square column reduction does not preserve that constraint.
        // Bounded row reductions do: a lowered column is assigned immediately
        // and stays occupied, even when its row is displaced.
        let mut num_free = rows;
        // The q < k*B allowance bounds each pass to B times its starting free
        // row count in full row scans. One extra tie scan per row preserves
        // O(rows*cols) initialization work with the default B <= 4.
        #[cfg(feature = "profile")]
        let reduction_limit = super::profile::reduction_limit(cols.min(4));
        #[cfg(not(feature = "profile"))]
        let reduction_limit = cols.min(4);
        #[cfg(feature = "profile")]
        let prefer_free_ties = super::profile::prefer_free_ties();
        #[cfg(not(feature = "profile"))]
        let prefer_free_ties = true;
        // Track required-mode displacement stalls across both passes. Once a
        // window expires, later assignments cannot re-enable lowering. Optional
        // mode retains the B=4 allowance without a displacement-stall cutoff.
        let window = if OPTIONAL { usize::MAX } else { rows.max(8) };
        let mut stalled = 0usize;
        let mut reduction_active = true;
        for _ in 0..2 {
            let previous = num_free;
            num_free = 0;
            let mut k = 0;
            let mut reductions = 0usize;
            while k < previous {
                profile_count!(self, reduction_rows, 1);
                let i = free[k];
                k += 1;
                reductions += 1;
                let row = &costs[i * cols..(i + 1) * cols];
                let (min, second, mut j1, j2) = if OPTIONAL {
                    let [first, runner_up] = optional_row_minima(row, v, penalty);
                    (first.cost, runner_up.cost, first.column, runner_up.column)
                } else {
                    required_row_minima(row, v)
                };
                if !min.finite() {
                    return Err(Error::Infeasible);
                }
                if OPTIONAL && j1 == FREE {
                    x[i] = FREE;
                    u[i] = penalty;
                    stalled = 0;
                    continue;
                }
                // Resolve tied occupied minima outside the hot minimum scan.
                // An equally cheap free column avoids a needless displacement.
                // The implicit unmatched choice above keeps priority on ties.
                if prefer_free_ties && min == second && y[j1] != FREE {
                    if j2 != FREE && y[j2] == FREE {
                        j1 = j2;
                    } else {
                        for j in 0..cols {
                            if y[j] == FREE && row[j].to_f64() - v[j] == min {
                                j1 = j;
                                break;
                            }
                        }
                    }
                }
                let mut displaced = y[j1];
                let reduce = reduction_active && reductions < k.saturating_mul(reduction_limit);
                let new_v = v[j1] - (second - min);
                // Do not choose a nonminimal fallback merely because the
                // potential update exceeds the working type's finite range.
                if reduce && second.finite() && !new_v.finite() {
                    return Err(Error::Infeasible);
                }
                let lowers = reduce && new_v.finite() && new_v < v[j1];
                if lowers {
                    v[j1] = new_v;
                } else if reduce && second.finite() && displaced != FREE && (OPTIONAL || j2 != FREE)
                {
                    j1 = j2;
                    if OPTIONAL && j1 == FREE {
                        x[i] = FREE;
                        u[i] = penalty;
                        stalled = 0;
                        continue;
                    }
                    displaced = y[j1];
                }
                x[i] = j1;
                y[j1] = i;
                u[i] = row[j1].to_f64() - v[j1];
                if !u[i].finite() {
                    return Err(Error::Infeasible);
                }
                if displaced == FREE {
                    stalled = 0;
                } else {
                    stalled += 1;
                    if reduction_active && stalled >= window {
                        reduction_active = false;
                    }
                }
                if displaced != FREE {
                    if lowers {
                        k -= 1;
                        free[k] = displaced;
                    } else {
                        free[num_free] = displaced;
                        num_free += 1;
                    }
                }
            }
        }
        profile_phase!(self, reduction_ns, phase_timer);

        for &root in free.iter().take(num_free) {
            profile_count!(self, augmentations, 1);
            // Tighten this free row's dual, including rows that have never
            // been assigned and can contain negative costs.
            // Keep root's reduced costs in d; the first relaxation below
            // reuses them instead of reading the row again.
            let row = &costs[root * cols..(root + 1) * cols];
            let mut min = if OPTIONAL { penalty } else { f64::INFINITY };
            for j in 0..cols {
                let value = row[j].to_f64() - v[j];
                d[j] = value;
                if value < min {
                    min = value;
                }
                columns[j] = j;
            }
            if !min.finite() {
                return Err(Error::Infeasible);
            }
            u[root] = min;
            x[root] = FREE;
            let mut low = 0;
            let mut current = root;
            let mut distance = 0.0;
            let mut dummy_distance = f64::INFINITY;
            let mut dummy_row = FREE;
            let sink = loop {
                if OPTIONAL {
                    let candidate = distance + (penalty - u[current]);
                    if candidate < dummy_distance {
                        dummy_distance = candidate;
                        dummy_row = current;
                    }
                }
                let row = &costs[current * cols..(current + 1) * cols];
                let row_potential = u[current];
                let mut best = f64::INFINITY;
                let mut best_pos = FREE;
                profile_count!(self, relaxation_columns, cols - low);
                if low == 0 {
                    // Root relaxation in identity order: same values as relaxing
                    // from d = inf. Infinite columns get pred = root, but cannot
                    // be selected while their distance remains infinite.
                    for j in 0..cols {
                        let candidate = distance + (d[j] - row_potential);
                        d[j] = candidate;
                        pred[j] = current;
                        if candidate < best || (candidate == best && y[j] == FREE) {
                            best = candidate;
                            best_pos = j;
                        }
                    }
                } else {
                    for (offset, &j) in columns[low..].iter().enumerate() {
                        let candidate = distance + (row[j].to_f64() - v[j] - row_potential);
                        if candidate < d[j] {
                            d[j] = candidate;
                            pred[j] = current;
                        }
                        // On equal distances prefer a free column to terminate the
                        // search promptly. This choice is independent of workers.
                        if d[j] < best || (d[j] == best && y[j] == FREE) {
                            best = d[j];
                            best_pos = low + offset;
                        }
                    }
                }
                if OPTIONAL && dummy_distance.finite() && dummy_distance <= best {
                    distance = dummy_distance;
                    break FREE;
                }
                if !best.finite() || best_pos == FREE {
                    return Err(Error::Infeasible);
                }
                distance = best;
                columns.swap(low, best_pos);
                let j = columns[low];
                low += 1;
                if y[j] == FREE {
                    break j;
                }
                current = y[j];
            };

            // Maintain feasible row duals and non-positive column duals.
            u[root] += distance;
            if !u[root].finite() {
                return Err(Error::Infeasible);
            }
            for &j in &columns[..low] {
                let adjustment = distance - d[j];
                if y[j] != FREE {
                    u[y[j]] += adjustment;
                    if !u[y[j]].finite() {
                        return Err(Error::Infeasible);
                    }
                }
                v[j] -= adjustment;
                if !v[j].finite() {
                    return Err(Error::Infeasible);
                }
            }
            let mut j = sink;
            let mut reached_root = false;
            for _ in 0..rows {
                let i = if OPTIONAL && j == FREE {
                    dummy_row
                } else {
                    pred[j]
                };
                if i == FREE {
                    return Err(Error::Internal);
                }
                let old = x[i];
                if j != FREE {
                    y[j] = i;
                }
                x[i] = j;
                if i == root {
                    reached_root = true;
                    break;
                }
                if old == FREE {
                    return Err(Error::Internal);
                }
                j = old;
            }
            // An augmenting path visits each row at most once.
            if !reached_root {
                return Err(Error::Internal);
            }
        }
        profile_finish!(self, augment_ns, phase_timer);
        for (i, &j) in x.iter().enumerate() {
            if OPTIONAL && j == FREE {
                continue;
            }
            if j >= cols || !costs[i * cols + j].finite() {
                return Err(Error::Infeasible);
            }
            if y[j] != i {
                return Err(Error::Internal);
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn assert_float32_certificate(
        solver: &Rectangular<f32>,
        costs: &[f32],
        rows: usize,
        cols: usize,
        penalty: Option<f64>,
        expected: f64,
    ) {
        let primal: f64 = solver.x[..rows]
            .iter()
            .enumerate()
            .map(|(i, &j)| {
                if j == FREE {
                    penalty.expect("required rows must be assigned")
                } else {
                    assert_eq!(solver.y[j], i);
                    assert_eq!(
                        solver.row_dual[i] + solver.column_dual[j],
                        costs[i * cols + j].to_f64()
                    );
                    costs[i * cols + j].to_f64()
                }
            })
            .sum();
        let dual: f64 = solver.row_dual[..rows]
            .iter()
            .chain(&solver.column_dual[..cols])
            .sum();
        assert_eq!(primal, expected);
        assert_eq!(primal, dual);
        for i in 0..rows {
            if let Some(penalty) = penalty {
                assert!(solver.row_dual[i] <= penalty);
                if solver.x[i] == FREE {
                    assert_eq!(solver.row_dual[i], penalty);
                }
            }
            for j in 0..cols {
                assert!(solver.row_dual[i] + solver.column_dual[j] <= costs[i * cols + j].to_f64());
            }
        }
        for j in 0..cols {
            assert!(solver.column_dual[j] <= 0.0);
            if solver.y[j] == FREE {
                assert_eq!(solver.column_dual[j], 0.0);
            }
        }
    }

    #[test]
    fn float32_storage_preserves_small_rectangular_assignment_differences() {
        let mut solver = Rectangular::<f32>::default();
        for (large, small) in [
            (2_902_499.0_f32 / 16.0, 1.0_f32 / 4096.0),
            (16777216.0, 0.125),
        ] {
            // Both rows compete for the middle column. Its two exactly
            // representable small costs must remain distinguishable after a
            // large column-potential update; the other row pays `large`.
            let original = [large, 2.0 * small, large, large, small, large];
            for reverse_rows in [false, true] {
                let costs: Vec<f32> = if reverse_rows {
                    original[3..]
                        .iter()
                        .chain(&original[..3])
                        .copied()
                        .collect()
                } else {
                    original.to_vec()
                };
                solver.solve(&costs, 2, 3).unwrap();
                assert_float32_certificate(
                    &solver,
                    &costs,
                    2,
                    3,
                    None,
                    large.to_f64() + small.to_f64(),
                );
                // A high finite penalty retains the required optimum. A low
                // penalty exercises the implicit sink and leaves one row out.
                for penalty in [2.0 * large, 4.0 * small] {
                    solver.solve_optional(&costs, 2, 3, penalty).unwrap();
                    assert_float32_certificate(
                        &solver,
                        &costs,
                        2,
                        3,
                        Some(penalty.to_f64()),
                        penalty.to_f64().min(large.to_f64()) + small.to_f64(),
                    );
                }
            }
        }
    }

    #[test]
    fn float32_small_differences_survive_rectangular_sap_relaxation() {
        let mut solver = Rectangular::<f32>::default();
        for (large, small) in [
            (2_902_499.0_f32 / 16.0, 1.0_f32 / 4096.0),
            (16_777_216.0_f32, 0.125_f32),
        ] {
            // Three rows compete for two cheap columns. Initialization leaves
            // one row unresolved; later SAP relaxation must preserve H-2s.
            // The exact optimum H+s makes row 0 take either large-cost column.
            let costs = [
                2.0 * small,
                2.0 * small,
                large,
                large,
                small,
                small,
                large,
                large,
                0.0,
                0.0,
                large,
                large,
            ];
            let expected = large.to_f64() + small.to_f64();
            for optional in [false, true] {
                let penalty = 2.0 * large;
                if optional {
                    solver.solve_optional(&costs, 3, 4, penalty).unwrap();
                } else {
                    solver.solve(&costs, 3, 4).unwrap();
                }
                assert_float32_certificate(
                    &solver,
                    &costs,
                    3,
                    4,
                    if optional {
                        Some(penalty.to_f64())
                    } else {
                        None
                    },
                    expected,
                );
                assert!((2..4).contains(&solver.x[0]));
                assert!(solver.x[1] < 2 && solver.x[2] < 2);
                assert_ne!(solver.x[1], solver.x[2]);
                #[cfg(feature = "profile")]
                {
                    assert_eq!(solver.profile.reduction_rows, 4);
                    assert_eq!(solver.profile.augmentations, 1);
                    assert_eq!(solver.profile.relaxation_columns, 9);
                }
            }
        }
    }

    #[test]
    fn displacement_window_only_interrupts_required_reduction() {
        // Four rows compete for three cheap columns. A long displacement
        // chain can finish optional initialization, while required matching
        // stops lowering and resolves the remaining row by augmentation.
        let costs = [
            19.0_f32, 83.0, 84.0, 270.0, 202.0, 50.0, 85.0, 13.0, 261.0, 267.0, 25.0, 90.0, 20.0,
            263.0, 205.0, 88.0, 67.0, 75.0, 296.0, 290.0,
        ];
        let mut solver = Rectangular::<f32>::default();
        solver.solve(&costs, 4, 5).unwrap();
        assert_float32_certificate(&solver, &costs, 4, 5, None, 304.0);
        #[cfg(feature = "profile")]
        {
            assert_eq!(solver.profile.reduction_rows, 14);
            assert_eq!(solver.profile.augmentations, 1);
        }
        // The penalty exceeds every edge cost, so both modes have the same
        // fully matched optimum [0, 2, 4, 1]. Only the stopping policy differs.
        solver.solve_optional(&costs, 4, 5, 10_000.0).unwrap();
        assert_float32_certificate(&solver, &costs, 4, 5, Some(10_000.0), 304.0);
        #[cfg(feature = "profile")]
        {
            assert_eq!(solver.profile.reduction_rows, 15);
            assert_eq!(solver.profile.augmentations, 0);
        }
    }

    fn brute(costs: &[f64], r: usize, c: usize, row: usize, used: usize) -> f64 {
        if row == r {
            return 0.0;
        }
        (0..c)
            .filter(|&j| used & (1 << j) == 0)
            .map(|j| costs[row * c + j] + brute(costs, r, c, row + 1, used | (1 << j)))
            .fold(f64::INFINITY, f64::min)
    }

    #[test]
    fn rectangular_optimum_and_dual_certificate() {
        let mut solver = Rectangular::<f64>::default();
        let mut seed = 123u64;
        for r in 1..=5 {
            for c in r + 1..=7 {
                for _ in 0..100 {
                    let a: Vec<f64> = (0..r * c)
                        .map(|_| {
                            seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                            if seed % 7 == 0 {
                                f64::INFINITY
                            } else {
                                ((seed >> 32) % 21) as f64 - 10.0
                            }
                        })
                        .collect();
                    let expected = brute(&a, r, c, 0, 0);
                    let result = solver.solve(&a, r, c);
                    if !expected.is_finite() {
                        assert_eq!(result, Err(Error::Infeasible));
                        continue;
                    }
                    result.unwrap_or_else(|e| panic!("{e:?}, {r}x{c}, {a:?}"));
                    let actual: f64 = solver.x[..r]
                        .iter()
                        .enumerate()
                        .map(|(i, &j)| a[i * c + j])
                        .sum();
                    assert_eq!(actual, expected, "{r}x{c}, {a:?}");
                    let dual: f64 = solver.row_dual[..r]
                        .iter()
                        .chain(&solver.column_dual[..c])
                        .sum();
                    assert_eq!(actual, dual);
                    for (i, row) in a.chunks_exact(c).enumerate() {
                        for (j, &cost) in row.iter().enumerate() {
                            assert!(solver.row_dual[i] + solver.column_dual[j] <= cost);
                        }
                    }
                    for j in 0..c {
                        assert!(solver.column_dual[j] <= 0.0);
                        if solver.y[j] == FREE {
                            assert_eq!(solver.column_dual[j], 0.0);
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn rectangular_storage_is_linear_and_recovers_after_error() {
        let mut solver = Rectangular::<f64>::default();
        let a = vec![1.0; 3 * 10000];
        solver.solve(&a, 3, 10000).unwrap();
        assert_eq!(solver.x.len(), 3);
        assert_eq!(solver.y.len(), 10000);
        assert_eq!(solver.distance.len(), 10000);
        assert_eq!(
            solver.solve(
                &[
                    0.0,
                    f64::INFINITY,
                    f64::INFINITY,
                    0.0,
                    f64::INFINITY,
                    f64::INFINITY
                ],
                2,
                3
            ),
            Err(Error::Infeasible)
        );
        solver.solve(&[2., 1., 9., 1., 2., 9.], 2, 3).unwrap();
        assert_eq!(solver.x[..2], [1, 0]);
    }

    fn brute_optional(a: &[f64], r: usize, c: usize, row: usize, used: usize, p: f64) -> f64 {
        if row == r {
            return 0.0;
        }
        let unmatched = p + brute_optional(a, r, c, row + 1, used, p);
        (0..c)
            .filter(|&j| used & (1 << j) == 0)
            .map(|j| a[row * c + j] + brute_optional(a, r, c, row + 1, used | (1 << j), p))
            .fold(unmatched, f64::min)
    }

    #[test]
    fn optional_optimum_and_dual_certificate() {
        let mut solver = Rectangular::<f64>::default();
        let mut seed = 901u64;
        for r in 1..=5 {
            for c in r..=7 {
                for p in [-4.0, 0.0, 4.0] {
                    for _ in 0..100 {
                        let a: Vec<f64> = (0..r * c)
                            .map(|_| {
                                seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                                if seed % 5 == 0 {
                                    f64::INFINITY
                                } else {
                                    ((seed >> 32) % 21) as f64 - 10.0
                                }
                            })
                            .collect();
                        let expected = brute_optional(&a, r, c, 0, 0, p);
                        solver.solve_optional(&a, r, c, p).unwrap();
                        let actual: f64 = solver.x[..r]
                            .iter()
                            .enumerate()
                            .map(|(i, &j)| if j == FREE { p } else { a[i * c + j] })
                            .sum();
                        assert_eq!(actual, expected, "{r}x{c}, p={p}, {a:?}");
                        let dual: f64 = solver.row_dual[..r]
                            .iter()
                            .chain(&solver.column_dual[..c])
                            .sum();
                        assert_eq!(actual, dual);
                        for (i, row) in a.chunks_exact(c).enumerate() {
                            assert!(solver.row_dual[i] <= p);
                            if solver.x[i] == FREE {
                                assert_eq!(solver.row_dual[i], p);
                            }
                            for (j, &cost) in row.iter().enumerate() {
                                assert!(solver.row_dual[i] + solver.column_dual[j] <= cost);
                            }
                        }
                        for j in 0..c {
                            assert!(solver.column_dual[j] <= 0.0);
                            if solver.y[j] == FREE {
                                assert_eq!(solver.column_dual[j], 0.0);
                            }
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn large_near_square_and_dispatch_boundary_duals() {
        let mut solver = Rectangular::<f64>::default();
        let mut seed = 439u64;
        for (r, c) in [(129, 130), (256, 288), (256, 289)] {
            for _ in 0..8 {
                let a: Vec<f64> = (0..r * c)
                    .map(|k| {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        if k / c != k % c && seed % 11 == 0 {
                            f64::INFINITY
                        } else {
                            ((seed >> 32) % 13) as f64 - 5.
                        }
                    })
                    .collect();
                solver.solve(&a, r, c).unwrap();
                let primal: f64 = solver.x[..r]
                    .iter()
                    .enumerate()
                    .map(|(i, &j)| a[i * c + j])
                    .sum();
                let dual: f64 = solver.row_dual[..r]
                    .iter()
                    .chain(&solver.column_dual[..c])
                    .sum();
                assert_eq!(primal, dual);
                for i in 0..r {
                    assert_eq!(solver.y[solver.x[i]], i);
                    for j in 0..c {
                        assert!(solver.row_dual[i] + solver.column_dual[j] <= a[i * c + j]);
                    }
                }
                for j in 0..c {
                    assert!(solver.column_dual[j] <= 0.);
                    if solver.y[j] == FREE {
                        assert_eq!(solver.column_dual[j], 0.);
                    }
                }
            }
        }
    }

    fn check_optional_square_duals<T: Cost>() {
        let mut solver = Rectangular::<T>::default();
        let mut seed = 891u64;
        for n in [31, 32, 33, 64, 129, 250] {
            for penalty in [-2., 0., 2.] {
                for sparse in [false, true] {
                    let a: Vec<T> = (0..n * n)
                        .map(|k| {
                            seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                            let affordable = !sparse || (k / n < 3 * n / 4) == (k % n < n / 4);
                            T::from_f64(if seed % 11 == 0 {
                                f64::INFINITY
                            } else if affordable {
                                ((seed >> 32) % 33) as f64 / 8. - 2.
                            } else {
                                4.
                            })
                        })
                        .collect();
                    solver
                        .solve_optional(&a, n, n, T::from_f64(penalty))
                        .unwrap();
                    let primal: f64 = solver.x[..n]
                        .iter()
                        .enumerate()
                        .map(|(i, &j)| {
                            if j == FREE {
                                penalty
                            } else {
                                a[i * n + j].to_f64()
                            }
                        })
                        .sum();
                    let dual: f64 = solver.row_dual[..n]
                        .iter()
                        .chain(&solver.column_dual[..n])
                        .map(|v| v.to_f64())
                        .sum();
                    assert_eq!(primal, dual);
                    for i in 0..n {
                        let u = solver.row_dual[i].to_f64();
                        assert!(u <= penalty);
                        if solver.x[i] == FREE {
                            assert_eq!(u, penalty);
                        } else {
                            assert_eq!(solver.y[solver.x[i]], i);
                        }
                        for j in 0..n {
                            assert!(u + solver.column_dual[j].to_f64() <= a[i * n + j].to_f64());
                        }
                    }
                    for j in 0..n {
                        assert!(solver.column_dual[j].to_f64() <= 0.);
                        if solver.y[j] == FREE {
                            assert_eq!(solver.column_dual[j].to_f64(), 0.);
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn bounded_optional_square_primal_dual_certificates() {
        check_optional_square_duals::<f32>();
        check_optional_square_duals::<f64>();
    }

    fn check_optional_minima<T: Cost>() {
        let mut seed = 20261018u64;
        for n in [
            0, 1, 4, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 31, 32, 33, 50, 64, 129,
        ] {
            for penalty in [-2.0, 0.0, 2.0] {
                let penalty = T::from_f64(penalty);
                for pattern in 0..6 {
                    let mut row = Vec::new();
                    let mut dual = Vec::new();
                    for _ in 0..n {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        let cost = match pattern {
                            0 => T::INF,
                            1 => penalty,
                            2 => T::from_f64(4.0),
                            _ if seed % 3 == 0 => T::INF,
                            _ => T::from_f64(((seed >> 32) % 33) as f64 / 4.0 - 4.0),
                        };
                        row.push(cost);
                        dual.push(-(((seed >> 16) % 9) as f64) / 4.0);
                    }
                    if n > 1 && pattern >= 4 {
                        row[0] = if pattern == 4 { T::INF } else { penalty };
                        row[n - 1] = row[0];
                    }
                    // Stable sorting is independent of the scan. Put the two
                    // unmatched choices first so they retain priority on ties.
                    let penalty = penalty.to_f64();
                    let mut expected = vec![(penalty, FREE), (penalty, FREE)];
                    expected.extend(
                        row.iter()
                            .zip(&dual)
                            .enumerate()
                            .map(|(j, (&cost, &potential))| (cost.to_f64() - potential, j)),
                    );
                    expected.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
                    let actual = optional_row_minima(&row, &dual, penalty);
                    for (found, &(cost, column)) in actual.iter().zip(&expected) {
                        assert_eq!(found.cost.to_f64(), cost.to_f64());
                        assert_eq!(found.column, column);
                    }
                }
            }
        }
    }

    #[test]
    fn optional_minima_preserve_order_and_unmatched_ties() {
        check_optional_minima::<f32>();
        check_optional_minima::<f64>();
    }
}
