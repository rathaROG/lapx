// Copyright (c) 2026 Ratha SIV | MIT License
// One foreign call per completion phase; all memory remains owned by Rust.
use super::{Cost, Error, Workspace};

extern "C" {
    fn lapjvr_hybrid_augment(
        costs: *const std::ffi::c_void,
        float32: i32,
        n: usize,
        count: usize,
        x: *mut usize,
        y: *mut usize,
        columns: *mut usize,
        free_rows: *const usize,
        pred: *mut usize,
        distance: *mut f64,
        potential: *mut f64,
        counters: *mut u64,
    ) -> i32;
}

impl Workspace {
    pub(crate) fn augment_cpp<T: Cost>(
        &mut self,
        costs: &[T],
        n: usize,
        count: usize,
    ) -> Result<(), Error> {
        use std::any::TypeId;
        let float32 = if TypeId::of::<T>() == TypeId::of::<f32>() {
            1
        } else if TypeId::of::<T>() == TypeId::of::<f64>() {
            0
        } else {
            return Err(Error::Internal);
        };
        #[cfg(feature = "profile")]
        let mut counters = [0u64; 3];
        #[cfg(feature = "profile")]
        let counter_ptr = counters.as_mut_ptr();
        #[cfg(not(feature = "profile"))]
        let counter_ptr = std::ptr::null_mut();
        // SAFETY: solve checked n*n costs and resized every workspace to n.
        // The dtype check above establishes the foreign cost representation.
        // Distinct Vecs provide disjoint mutable arrays. Matching indices and
        // the free-row list come from the unchanged Rust initialization and
        // reduction. C++ retains no pointers, allocates nothing and never throws.
        let status = unsafe {
            lapjvr_hybrid_augment(
                costs.as_ptr().cast(),
                float32,
                n,
                count,
                self.x.as_mut_ptr(),
                self.y.as_mut_ptr(),
                self.columns.as_mut_ptr(),
                self.matches.as_ptr(),
                self.predecessor.as_mut_ptr(),
                self.distance.as_mut_ptr(),
                self.potential.as_mut_ptr(),
                counter_ptr,
            )
        };
        #[cfg(feature = "profile")]
        {
            self.profile.augmentations += counters[0];
            self.profile.minimum_columns += counters[1];
            self.profile.relaxation_columns += counters[2];
        }
        match status {
            0 => Ok(()),
            1 => Err(Error::Infeasible),
            _ => Err(Error::Internal),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Completion;

    // Compare the complete primal/dual state, not only a rounded objective.
    // One reused workspace alternates families; neither may leave a mode behind.
    fn compare<T: Cost>() {
        let mut rust = Workspace::default();
        let mut shared = Workspace::default();
        for n in [96, 7, 128, 1, 33] {
            for pattern in 0..3 {
                let mut seed = 20261019u64;
                let mut costs: Vec<T> = (0..n * n)
                    .map(|_| {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        T::from_f64(((seed >> 32) % 1024) as f64 / 1024.0)
                    })
                    .collect();
                for i in 1..n {
                    for j in 0..n {
                        if pattern == 1 && i < 3 * n / 4 {
                            costs[i * n + j] = costs[j];
                        } else if pattern == 2 {
                            costs[i * n + j] = costs[i * n + j] + T::from_f64(i as f64);
                        }
                    }
                }
                rust.solve(&costs, n).unwrap();
                for completion in [Completion::Cpp, Completion::Rust, Completion::Cpp] {
                    shared.solve_with(&costs, n, completion).unwrap();
                    assert_eq!(shared.x[..n], rust.x[..n]);
                    assert_eq!(shared.y[..n], rust.y[..n]);
                    assert_eq!(shared.potential[..n], rust.potential[..n]);
                    #[cfg(feature = "profile")]
                    {
                        let a = shared.profile;
                        let b = rust.profile;
                        assert_eq!(a.reduction_rows, b.reduction_rows);
                        assert_eq!(a.augmentations, b.augmentations);
                        assert_eq!(a.minimum_columns, b.minimum_columns);
                        assert_eq!(a.relaxation_columns, b.relaxation_columns);
                        if pattern == 1 && n >= 33 {
                            assert!(a.augmentations > 0);
                        }
                    }
                }
            }
        }
    }

    #[test]
    fn mixed_completion_preserves_f32_primal_dual_state() {
        compare::<f32>();
    }

    #[test]
    fn mixed_completion_preserves_f64_primal_dual_state() {
        compare::<f64>();
    }
}
