//! Opt-in diagnostic instrumentation. Absent from normal library builds.

use super::{rectangular::Rectangular, Cost, Error, Workspace, FREE};

pub(crate) fn reduction_limit(default: usize) -> usize {
    std::env::var("LAPJVR_PROFILE_REDUCTION_LIMIT")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(default)
}

pub(crate) fn prefer_free_ties() -> bool {
    std::env::var("LAPJVR_PROFILE_FREE_TIES").as_deref() != Ok("0")
}

#[derive(Clone, Copy, Default)]
pub struct Profile {
    pub initial_ns: u64,
    pub transfer_ns: u64,
    pub reduction_ns: u64,
    pub augment_ns: u64,
    pub reduction_rows: u64,
    pub augmentations: u64,
    pub minimum_columns: u64,
    pub relaxation_columns: u64,
    pub square_ns: u64,
    pub certificate_ns: u64,
    pub optional_ns: u64,
    pub dispatch_ns: u64,
    pub square_accepted: u64,
}

pub fn run<T: Cost>(
    costs: &[T],
    rows: usize,
    cols: usize,
    mode: &str,
    repeats: usize,
    limit: f64,
) -> Result<(Vec<Profile>, f64, usize), Error> {
    if mode == "finite" {
        return super::ffi::profile_finite(costs, rows, cols, repeats, limit);
    }
    let mut square = Workspace::default();
    let mut rectangle = Rectangular::default();
    let mut profiles = Vec::new();
    let mut total = 0.;
    let mut count = 0;
    for sample in 0..=repeats {
        let (x, profile) = match mode {
            "square" => {
                square.solve(costs, rows)?;
                (&square.x[..rows], square.profile)
            }
            #[cfg(feature = "cpp-completion")]
            "hybrid" => {
                square.solve_with(costs, rows, super::Completion::Cpp)?;
                (&square.x[..rows], square.profile)
            }
            "rectangular" => {
                rectangle.solve(costs, rows, cols)?;
                (&rectangle.x[..rows], rectangle.profile)
            }
            "optional" => {
                let half = T::from_f64(limit / 2.0);
                rectangle.solve_optional(costs, rows, cols, half + half)?;
                (&rectangle.x[..rows], rectangle.profile)
            }
            _ => return Err(Error::Dimensions),
        };
        total = 0.;
        count = 0;
        for (i, &j) in x.iter().enumerate() {
            if j != FREE {
                total += costs[i * cols + j].to_f64();
                count += 1;
            }
        }
        if sample > 0 {
            profiles.push(profile);
        }
    }
    Ok((profiles, total, count))
}
