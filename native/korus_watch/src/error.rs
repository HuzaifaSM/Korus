use std::fmt;

#[derive(Debug)]
pub enum WatchError {
    Io(std::io::Error),
    InvalidPath(String),
}

impl fmt::Display for WatchError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            WatchError::Io(e) => write!(f, "IO error: {}", e),
            WatchError::InvalidPath(p) => write!(f, "Invalid Path: {}", p)
        }
    }
}

impl From<std::io::Error> for WatchError {
    fn from(e: std::io::Error) -> Self {
        WatchError::Io(e)
    }
}

pub type WatchResult<T> = Result<T, WatchError>;
