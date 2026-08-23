use std::collections::HashMap;
use std::fs;
use std::path::Path;
use std::sync::mpsc::Sender;
use std::time::{Duration, SystemTime};
use std::thread;

// an event sent through the channel when a file change is detected
pub enum FileEvent {
    Changed { path: String, prev: String, next: String },
    Created { path: String },
    Deleted { path: String },
}

// holds the last known state of a file
struct FileSnapshot {
    content: String,
    lastModified: SystemTime,
}

// watches a folder for changes by polling every 'intervalSecs' seconds
// sends FileEvents through 'tx' when changes are detected
// this runs its own thread - loops forever until process exits
pub fn watchFolder(folderPath: String, intervalSecs: u64, tx: Sender<FileEvent>) {
    let mut snapshots: HashMap<String, FileSnapshot> = HashMap::new();

    // take an initial snapshot of all files so no false alarms on setup
    if let Ok(entries) = fs::read_dir(&folderPath) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.is_file() {
                let pathStr = path.to_string_lossy().to_string();
                if let Ok(content) = fs::read_to_string(&path) {
                    if let Ok(meta) = fs::metadata(&path) {
                        if let Ok(modified) = meta.modified() {
                            snapshots.insert(pathStr, FileSnapshot { content, lastModified: modified });
                        }
                    }
                }
            }
        }
    }

    println!("Watching: {}", folderPath);
    println!("Press Ctrl+C to stop.\n");

    loop {
        thread::sleep(Duration::from_secs(intervalSecs));

        // collect current files
        let currentFiles: Vec<String> = fs::read_dir(&folderPath)
            .map(|entries| {
                entries
                    .flatten()
                    .filter(|e| e.path().is_file())
                    .map(|e| e.path().to_string_lossy().to_string())
                    .collect()
            })
            .unwrap_or_default();

        for pathStr in &currentFiles {
            let path = Path::new(pathStr);
            let meta = match fs::metadata(path) {
                Ok(m) => m,
                Err(_) => continue,
            };
            let modified = match meta.modified() {
                Ok(t) => t,
                Err(_) => continue,
            };

            match snapshots.get(pathStr) {
                None => {
                    // file didn't exist before - it was created
                    let content = fs::read_to_string(path).unwrap_or_default();
                    snapshots.insert(pathStr.clone(), FileSnapshot {
                        content,
                        lastModified: modified,
                    });
                    let _ = tx.send(FileEvent::Created { path: pathStr.clone() });
                }
                Some(snapshot) if modified > snapshot.lastModified => {
                    // modification time changed - read and compare content
                    let newContent = fs::read_to_string(path).unwrap_or_default();
                    if newContent != snapshot.content {
                        let prevContent = snapshot.content.clone();
                        snapshots.insert(pathStr.clone(), FileSnapshot {
                            content: newContent.clone(),
                            lastModified: modified,
                        });
                        let _ = tx.send(FileEvent::Changed {
                            path: pathStr.clone(),
                            prev: prevContent,
                            next: newContent,
                        });
                    } else {
                        // content unchanged despite mtime difference - update timestamp only
                        if let Some(s) = snapshots.get_mut(pathStr) {
                            s.lastModified = modified;
                        }
                    }
                }
                _ => {}
            }
        }

        // check for deleted files
        let deletedPaths: Vec<String> = snapshots
            .keys()
            .filter(|p| !currentFiles.contains(p))
            .cloned()
            .collect();

        for pathStr in deletedPaths {
            snapshots.remove(&pathStr);
            let _ = tx.send(FileEvent::Deleted { path: pathStr });
        }
    }
}
