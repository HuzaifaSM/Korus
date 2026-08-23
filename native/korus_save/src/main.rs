mod format;
mod error;
mod codec;

use std::env;

fn print_usage() {
    eprintln!("Usage:");
    eprintln!("  korus_save --encode <input.json> <output.korus>");
    eprintln!("  korus_save --decode <input.korus> <output.json>");
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 4 {
        eprintln!("Error: wrong number of arguments.");
        eprintln!();
        print_usage();
        std::process::exit(1);
    }

    let mode = &args[1];
    let input = &args[2];
    let output = &args[3];

    let result = match mode.as_str() {
        "--encode" => codec::encode(input, output),
        "--decode" => codec::decode(input, output),
        other => {
            eprintln!("Error: unknown mode '{}'", other);
            eprintln!();
            print_usage();
            std::process::exit(1);
        }
    };

    match result {
        Ok(()) => {
            // success, print nothing so Python can use stdout cleanly
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    }
}