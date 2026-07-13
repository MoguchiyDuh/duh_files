mod emit;
mod pulse;
mod sink;
mod source;

use std::process::ExitCode;

fn main() -> ExitCode {
    let mut args = std::env::args();
    let program = args.next().unwrap_or_else(|| "soundbar".to_string());

    match args.next().as_deref() {
        Some("sink") => sink::run(),
        Some("source") => source::run(),
        _ => {
            eprintln!("usage: {program} <sink|source>");
            return ExitCode::FAILURE;
        }
    }
}
