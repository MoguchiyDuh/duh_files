mod cpu;
mod emit;
mod gpu;
mod memory;
mod sysfs;

use std::process::ExitCode;
use std::time::Duration;

const INTERVAL: Duration = Duration::from_secs(5);

fn main() -> ExitCode {
    let mut args = std::env::args();
    let program = args.next().unwrap_or_else(|| "hardwarebar".to_string());

    match args.next().as_deref() {
        Some("cpu") => cpu::run(INTERVAL),
        Some("memory") => memory::run(INTERVAL),
        Some("gpu") => gpu::run(INTERVAL),
        _ => {
            eprintln!("usage: {program} <cpu|memory|gpu>");
            return ExitCode::FAILURE;
        }
    }
}
