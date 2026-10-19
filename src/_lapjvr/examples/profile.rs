use lapjvr_core::{profile, Cost};

fn run<T: Cost>(costs: &[T], rows: usize, cols: usize, mode: &str, repeats: usize, limit: f64) {
    let (profiles, total, count) = profile::run(costs, rows, cols, mode, repeats, limit).unwrap();
    println!("total,count,initial_ns,transfer_ns,reduction_ns,augment_ns,reduction_rows,augmentations,minimum_columns,relaxation_columns,square_ns,certificate_ns,optional_ns,dispatch_ns,square_accepted");
    for p in profiles {
        println!(
            "{total},{count},{},{},{},{},{},{},{},{},{},{},{},{},{}",
            p.initial_ns,
            p.transfer_ns,
            p.reduction_ns,
            p.augment_ns,
            p.reduction_rows,
            p.augmentations,
            p.minimum_columns,
            p.relaxation_columns,
            p.square_ns,
            p.certificate_ns,
            p.optional_ns,
            p.dispatch_ns,
            p.square_accepted
        );
    }
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert!(
        matches!(args.len(), 7 | 8),
        "profile FILE ROWS COLS DTYPE MODE REPEATS [LIMIT]"
    );
    let bytes = std::fs::read(&args[1]).unwrap();
    let rows = args[2].parse().unwrap();
    let cols = args[3].parse().unwrap();
    let repeats = args[6].parse().unwrap();
    let limit = args.get(7).map_or(0.5, |v| v.parse().unwrap());
    match args[4].as_str() {
        "float64" => run(
            &bytes
                .chunks_exact(8)
                .map(|a| f64::from_le_bytes(a.try_into().unwrap()))
                .collect::<Vec<_>>(),
            rows,
            cols,
            &args[5],
            repeats,
            limit,
        ),
        "float32" => run(
            &bytes
                .chunks_exact(4)
                .map(|a| f32::from_le_bytes(a.try_into().unwrap()))
                .collect::<Vec<_>>(),
            rows,
            cols,
            &args[5],
            repeats,
            limit,
        ),
        _ => panic!("invalid dtype"),
    }
}
