mod error;
mod differ;
mod reporter;
mod watcher;

use std::sync::mpsc;
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};
use reporter::Reporter;
use watcher::{watchFolder, FileEvent};
use differ::diffLines;

fn timestamp() -> String {
    // format current time as HH:MM:SS using standard library only
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs();

    let s = secs % 60;
    let m = (secs / 60) % 60;
    let h = (secs / 3600) % 60;
    format!("{:02}:{:02}:{:02}", h, m, s)
}

fn printUsage() {
    eprintln!("Usage: korus_watch <folder> [--log <logfile>] [--interval <seconds>] [--silent]");
    eprintln!();
    eprintln!("  folder              Path to the folder to watch.");
    eprintln!("  --log <path>        Path to the log file (default: korus_watch.log)");
    eprintln!("  --interval <secs>   Poll interval in seconds (default: 1)");
    eprintln!("  --silent            Suppress terminal output; still writes to the log file (default: false)");
}

fn parseArgs() -> Result<(String, String, u64, bool), String> {
    let args: Vec<String> = std::env::args().collect();

    if args.len() < 2 {
        return Err("No folder specified.".to_string());
    }

    let folder = args[1].clone();
    let mut log = "korus_watch.log".to_string();
    let mut interval: u64 = 1;
    let mut silent = false;

    let mut i = 2;
    while i < args.len() {
        match args[i].as_str() {
            "--log" => {
                i += 1;
                log = args.get(i)
                    .ok_or("--log requires a value".to_string())?
                    .clone();
            }
            "--interval" => {
                i += 1;
                interval = args.get(i)
                    .ok_or("--interval requires a value".to_string())?
                    .parse::<u64>()
                    .map_err(|_| "--interval must be a positive integer".to_string())?;
            }
            "--silent" => {
                silent = true;
            }
            other => return Err(format!("Unknown argument: {}", other)),
        }
        i += 1;
    }

    Ok((folder, log, interval, silent))
}

fn main() {
    let (folder, logPath, interval, silent) = match parseArgs() {
        Ok(args) => args,
        Err(e) => {
            eprintln!("Error: {}", e);
            eprintln!();
            printUsage();
            std::process::exit(1);
        }
    };

    // validate folder exists
    if !std::path::Path::new(&folder).is_dir() {
        eprintln!("Error: '{}' is not a valid directory.", folder);
        std::process::exit(1);
    }

    // set up reporter
    let reporter = match Reporter::new(&logPath, silent) {
        Ok(r) => r,
        Err(e) => {
            eprintln!("Failed to open log file '{}': {}", logPath, e);
            std::process::exit(1);
        }
    };

    if !silent {
        println!("korus_watch started");
        println!("Log file: {}", logPath);
    }

    // mpsc channel - watcher thread sends events, main thread receives them
    // mpsc = multi-processor single-consumer : multiple senders, one reciever
    let (tx, rx) = mpsc::channel::<FileEvent>();

    // spawn the watcher thread - takes owner of tx and folder
    let folderClone = folder.clone();
    thread::spawn(move || {
        watchFolder(folderClone, interval, tx);
    });

    // main thread receives events and reports them
    // rx.recv() blocks until an event arrives - no busy waiting
    for event in rx {
        let ts = timestamp();
        match event {
            FileEvent::Changed { path, prev, next } => {
                let diffs = diffLines(&prev, &next);
                if !diffs.is_empty() {
                    reporter.reportChange(&path, &diffs, &ts);
                }
            }
            FileEvent::Created { path } => {
                reporter.reportCreated(&path, &ts);
            }
            FileEvent::Deleted { path } => {
                reporter.reportDeleted(&path, &ts);
            }
        }
    }
}
