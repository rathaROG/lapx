// Copyright (c) 2016 Vadim Markovtsev (source{d})
// Copyright (c) 2026 Ratha SIV
// JV adapted from LAPX JVS. MIT; see ../LICENSE.

use super::*;

// Reuse four complete rows to choose between the existing JV warm starts.
// A large spread of row minima favors zero column potentials. Congested
// blocks also use that start when their sampled rows span the cost range.
// This O(n) hint changes initialization only; both paths solve every edge.
#[inline(never)]
fn prefer_row_reduction<T: Cost>(costs: &[T], n: usize) -> bool {
    let mut minimum_cost = f64::INFINITY;
    let mut largest_row_minimum = f64::NEG_INFINITY;
    let mut cheapest_row_maximum = f64::NEG_INFINITY;
    let mut maximum_cost = f64::NEG_INFINITY;
    for sample in 0..4 {
        let i = sample * (n - 1) / 3;
        let mut low = T::INF;
        let mut high = T::from_f64(f64::NEG_INFINITY);
        for &cost in &costs[i * n..(i + 1) * n] {
            if cost < low {
                low = cost;
            }
            if cost > high {
                high = cost;
            }
        }
        if !low.finite() || !high.finite() {
            return false;
        }
        if low.to_f64() < minimum_cost {
            minimum_cost = low.to_f64();
            cheapest_row_maximum = high.to_f64();
        }
        largest_row_minimum = largest_row_minimum.max(low.to_f64());
        maximum_cost = maximum_cost.max(high.to_f64());
    }
    let range = maximum_cost - minimum_cost;
    range.is_finite()
        && (largest_row_minimum - minimum_cost > range * 0.5
            || (cheapest_row_maximum - minimum_cost > range * 0.75
                && sampled_block_conflicts(costs, n, minimum_cost, range)))
}

// Detect separated cost blocks using the same four sampled rows. Require
// complementary column choices and a majority competing for fewer than half
// the columns. Random costs, balanced blocks, and repeated rows keep column
// initialization. This only selects an initialization; no edges are excluded.
#[inline(never)]
fn sampled_block_conflicts<T: Cost>(costs: &[T], n: usize, minimum: f64, range: f64) -> bool {
    let rows: [&[T]; 4] = std::array::from_fn(|sample| {
        let start = sample * (n - 1) / 3 * n;
        &costs[start..start + n]
    });
    let cheap = minimum + range * 0.25;
    let expensive = minimum + range * 0.75;
    let mut cheap_columns = [0usize; 4];
    for j in 0..n {
        let mut has_cheap = false;
        let mut has_expensive = false;
        for (row, count) in rows.iter().zip(&mut cheap_columns) {
            let cost = row[j].to_f64();
            if cost < cheap {
                *count += 1;
                has_cheap = true;
            } else if cost > expensive {
                has_expensive = true;
            } else {
                return false;
            }
        }
        if !has_cheap || !has_expensive {
            return false;
        }
    }
    if cheap_columns
        .iter()
        .filter(|&&count| count < n - count)
        .count()
        < 3
    {
        return false;
    }
    for i in 0..rows.len() {
        if rows[..i].contains(&rows[i]) {
            return false;
        }
    }
    true
}

impl Workspace {
    /// Solve a square, flat row-major matrix; assignments remain in this workspace.
    /// NaN and negative infinity are excluded by the caller's cost contract.
    pub fn solve<T: Cost>(&mut self, costs: &[T], n: usize) -> Result<&[usize], Error> {
        self.solve_with(costs, n, Completion::Rust)
    }

    /// Select completion once per solve, outside the search loops. The choice
    /// belongs to this call, so alternating/concurrent families share no mode.
    #[inline(never)]
    pub fn solve_with<T: Cost>(
        &mut self,
        costs: &[T],
        n: usize,
        completion: Completion,
    ) -> Result<&[usize], Error> {
        #[cfg(feature = "profile")]
        let mut phase_timer = std::time::Instant::now();
        #[cfg(feature = "profile")]
        {
            self.profile = profile::Profile::default();
        }
        if n.checked_mul(n) != Some(costs.len()) {
            return Err(Error::Dimensions);
        }
        if n == 0 {
            return Ok(&self.x[..0]);
        }
        resize(&mut self.x, n, FREE)?;
        resize(&mut self.y, n, FREE)?;
        resize(&mut self.columns, n, 0)?;
        resize(&mut self.matches, n, 0)?;
        resize(&mut self.predecessor, n, 0)?;
        resize(&mut self.distance, n, 0.0)?;
        resize(&mut self.potential, n, 0.0)?;
        let Self {
            x,
            y,
            matches,
            potential: v,
            ..
        } = self;
        // Slice once to the active size so bounds proofs stay local to the
        // hot loops even when a previous solve retained larger buffers.
        let x = &mut x[..n];
        let y = &mut y[..n];
        let matches = &mut matches[..n];
        let v = &mut v[..n];
        x.fill(FREE);
        matches.fill(0);

        if prefer_row_reduction(costs, n) {
            // Start row reduction with empty assignments and zero column
            // potentials. The same reduction and search phases finish either
            // initialization, using this workspace and the original costs.
            v.fill(0.0);
            y.fill(FREE);
        } else {
            initialize_columns(costs, n, v, y);
            for j in (0..n).rev() {
                if !v[j].finite() {
                    return Err(Error::Infeasible);
                }
                let i = y[j];
                matches[i] += 1;
                if matches[i] == 1 {
                    x[i] = j;
                } else {
                    y[j] = FREE;
                }
            }
        }
        if n == 1 {
            return Ok(&self.x[..1]);
        }
        profile_phase!(self, initial_ns, phase_timer);

        // Reduction transfer; reuse the match counts for the free-row list.
        let mut num_free = 0;
        for (i, row) in costs.chunks_exact(n).enumerate() {
            if matches[i] == 0 {
                matches[num_free] = i;
                num_free += 1;
            } else if matches[i] == 1 {
                let j1 = x[i];
                let mut min = f64::INFINITY;
                for j in 0..n {
                    if j != j1 {
                        let candidate = row[j].to_f64() - v[j];
                        if candidate < min {
                            min = candidate;
                        }
                    }
                }
                // A uniquely permitted edge needs no reduction to -infinity.
                if min.finite() {
                    v[j1] -= min;
                }
            }
        }
        profile_phase!(self, transfer_ns, phase_timer);

        // Use the established large-square reduction policy at every size.
        let limit = 8;
        for _ in 0..2 {
            let previous = num_free;
            num_free = 0;
            let mut k = 0;
            let mut reductions = 0usize;
            while k < previous {
                profile_count!(self, reduction_rows, 1);
                let i = matches[k];
                k += 1;
                reductions += 1;
                let row = &costs[i * n..(i + 1) * n];
                let (min, second, mut j1, j2) = T::square_minima(row, v);
                if !min.finite() {
                    return Err(Error::Infeasible);
                }
                // Prefer a free minimum on tied problems, as the
                // near-square core does, to avoid needless row displacement.
                if min == second && y[j1] != FREE {
                    for j in 0..n {
                        if y[j] == FREE && row[j].to_f64() - v[j] == min {
                            j1 = j;
                            break;
                        }
                    }
                }
                let mut displaced = y[j1];
                let budget = k.saturating_mul(limit);
                let reduce = reductions < budget;
                let new_v = v[j1] - (second - min);
                let lowers = reduce && new_v.finite() && new_v < v[j1];
                if lowers {
                    v[j1] = new_v;
                } else if reduce && second.finite() && displaced != FREE && j2 != FREE {
                    j1 = j2;
                    displaced = y[j2];
                }
                x[i] = j1;
                y[j1] = i;
                if displaced != FREE {
                    if lowers {
                        k -= 1;
                        matches[k] = displaced;
                    } else {
                        matches[num_free] = displaced;
                        num_free += 1;
                    }
                }
            }
        }
        profile_phase!(self, reduction_ns, phase_timer);

        match completion {
            Completion::Rust => self.augment(costs, n, num_free)?,
            #[cfg(feature = "cpp-completion")]
            Completion::Cpp => self.augment_cpp(costs, n, num_free)?,
        }
        profile_finish!(self, augment_ns, phase_timer);
        for (i, &j) in self.x[..n].iter().enumerate() {
            if j >= n || !costs[i * n + j].finite() {
                return Err(Error::Infeasible);
            }
            if self.y[j] != i {
                return Err(Error::Internal);
            }
        }
        Ok(&self.x[..n])
    }

    // Complete the matching with shortest paths for rows left free by reduction.
    #[inline(never)]
    fn augment<T: Cost>(&mut self, costs: &[T], n: usize, num_free: usize) -> Result<(), Error> {
        let x = &mut self.x[..n];
        let y = &mut self.y[..n];
        let columns = &mut self.columns[..n];
        let matches = &self.matches[..n];
        let pred = &mut self.predecessor[..n];
        let d = &mut self.distance[..n];
        let v = &mut self.potential[..n];
        for &free_row in matches.iter().take(num_free) {
            profile_count!(self, augmentations, 1);
            for j in 0..n {
                d[j] = costs[free_row * n + j].to_f64() - v[j];
                pred[j] = free_row;
                columns[j] = j;
            }
            let mut low = 0;
            let mut up = 0;
            let mut scanned = 0;
            let mut min = 0.0;
            let end = 'search: loop {
                if up == low {
                    scanned = low;
                    if up == n {
                        return Err(Error::Infeasible);
                    }
                    min = d[columns[up]];
                    up += 1;
                    let remaining_start = up;
                    profile_count!(self, minimum_columns, n - remaining_start);
                    for k in remaining_start..n {
                        let j = columns[k];
                        let h = d[j];
                        if h <= min {
                            if h < min {
                                up = low;
                                min = h;
                            }
                            columns[k] = columns[up];
                            columns[up] = j;
                            up += 1;
                        }
                    }
                    if !min.finite() {
                        return Err(Error::Infeasible);
                    }
                    for &j in &columns[low..up] {
                        if y[j] == FREE {
                            break 'search j;
                        }
                    }
                }
                let j1 = columns[low];
                low += 1;
                let i = y[j1];
                let row = &costs[i * n..(i + 1) * n];
                let h = row[j1].to_f64() - v[j1] - min;
                let remaining_start = up;
                profile_count!(self, relaxation_columns, n - remaining_start);
                for k in remaining_start..n {
                    let j = columns[k];
                    let candidate = row[j].to_f64() - v[j] - h;
                    if candidate < d[j] {
                        pred[j] = i;
                        if candidate == min {
                            if y[j] == FREE {
                                #[cfg(feature = "profile")]
                                {
                                    self.profile.relaxation_columns -= (n - k - 1) as u64;
                                }
                                break 'search j;
                            }
                            columns[k] = columns[up];
                            columns[up] = j;
                            up += 1;
                        }
                        d[j] = candidate;
                    }
                }
            };
            for &j in &columns[..scanned] {
                v[j] = v[j] + d[j] - min;
            }
            let mut j = end;
            let mut reached_root = false;
            for _ in 0..n {
                let i = pred[j];
                y[j] = i;
                let previous = x[i];
                x[i] = j;
                if i == free_row {
                    reached_root = true;
                    break;
                }
                if previous == FREE {
                    return Err(Error::Internal);
                }
                j = previous;
            }
            // An augmenting path visits each row at most once.
            if !reached_root {
                return Err(Error::Internal);
            }
        }
        Ok(())
    }
}
