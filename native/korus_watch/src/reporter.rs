use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;
use std::sync::{Arc, Mutex};
use crate::differ::LineDiff;

// thread-safe reporter that writes to terminal and a log file
// Arc<Mutex<T>> lets mutliple threads share ownership of the log file handle safely
pub struct Reporter {
    logFile: Arc<Mutex<std::fs::File>>,
    silent: bool,
}

impl Reporter {
    pub fn new(logPath: &str, silent: bool) -> std::io::Result<Self> {
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(logPath)?;

        Ok(Self {
            logFile: Arc::new(Mutex::new(file)),
            silent,
        })
    }

    // reports a file change - prints to terminal with different colour and writes to log
    pub fn reportChange(&self, filePath: &str, diffs: &[LineDiff], timestamp: &str) {
        let fileName = Path::new(filePath)
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or(filePath);

        // terminal header
        if !self.silent {
            println!("\n\x1b[36m[{}]\x1b[0m Change detected: \x1b[1m{}\x1b[0m", timestamp, fileName);
        }

        let mut logLine = format!("\n[{}] Change Detected: {}\n", timestamp, filePath);

        for diff in diffs {
            match (&diff.prev, &diff.next) {
                // line was modified
                (Some(prev), Some(next)) => {
                    if !self.silent {
                        println!("  Line {:>4}  \x1b[33mPREV\x1b[0m >> {}", diff.line_number, prev);
                        println!("            \x1b[32mNEW \x1b[0m >> {}", next);
                    }
                    logLine.push_str(&format!(
                        "  Line {:>4}  PREV >> {}\n            NEW  >> {}\n",
                        diff.line_number, prev, next
                    ));
                }
                // line was added
                (None, Some(next)) => {
                    if !self.silent {
                        println!("  Line {:>4}  \x1b[32mADDED  \x1b[0m >> {}", diff.line_number, next);
                    }
                    logLine.push_str(&format!(
                        "  Line {:>4}  ADDED   >> {}\n",
                        diff.line_number, next
                    ));
                }
                // line was removed
                (Some(prev), None) => {
                    if !self.silent {
                        println!("  Line {:>4}  \x1b[31mREMOVED\x1b[0m >> {}", diff.line_number, prev);
                    }
                    logLine.push_str(&format!(
                        "  Line {:>4}  REMOVED >> {}\n",
                        diff.line_number, prev
                    ));
                }
                (None, None) => {}
            }
        }

        // write to log file - lock the mutex, then write, then lock drops automatically
        if let Ok(mut file) = self.logFile.lock() {
            let _ = file.write_all(logLine.as_bytes());
        }
    }

    // reports that a new file was created in the watched folder
    pub fn reportCreated(&self, filePath: &str, timestamp: &str) {
        let fileName = Path::new(filePath)
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or(filePath);

        if !self.silent {
            println!("\n\x1b[36m[{}]\x1b[0m \x1b[32mCreated:\x1b[0m {}", timestamp, fileName);
        }

        let logLine = format!("\n[{}] Created: {}\n", timestamp, filePath);
        if let Ok(mut file) = self.logFile.lock() {
            let _ = file.write_all(logLine.as_bytes());
        }
    }

    // reports that a file was deleted in the watched folder
    pub fn reportDeleted(&self, filePath: &str, timestamp: &str) {
        let fileName = Path::new(filePath)
            .file_name()
            .and_then(|n| n.to_str())
            .unwrap_or(filePath);

        if !self.silent {
            println!("\n\x1b[36m[{}]\x1b[0m \x1b[31mDeleted:\x1b[0m {}", timestamp, fileName);
        }

        let logLine = format!("\n[{}] Deleted: {}\n", timestamp, filePath);
        if let Ok(mut file) = self.logFile.lock() {
            let _ = file.write_all(logLine.as_bytes());
        }
    }
}
