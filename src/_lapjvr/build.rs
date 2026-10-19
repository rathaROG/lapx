#[cfg(feature = "cpp-completion")]
fn main() {
    println!("cargo:rerun-if-changed=src/cpp_completion.cpp");
    let mut build = cc::Build::new();
    build.cpp(true).std("c++17").file("src/cpp_completion.cpp");
    if build.get_compiler().is_like_msvc() {
        // Ordinary COFF objects can be bundled in Rust's static archive.
        // MSVC /GL objects cannot participate in Rust ThinLTO.
        build.flag("/fp:precise").flag("/GL-");
    } else {
        build.flag("-fno-fast-math").flag("-ffp-contract=off");
    }
    build.compile("lapjvr_completion");
}

#[cfg(not(feature = "cpp-completion"))]
fn main() {}
