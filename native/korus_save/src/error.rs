#![allow(non_snake_case)]

use std::fmt;

#[derive(Debug)]
pub enum KorusError {
    Io(std::io::Error),
    InvalidMagic,
    VersionMismatch(u32),
    ChecksumFailed,
    InvalidUtf8,
    DecompressionFailed,
}

impl fmt::Display for KorusError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            KorusError::Io(e)                => write!(f, "IO error: {}", e),
            KorusError::InvalidMagic         => write!(f, "Not a valid .korus file (invalid magic bytes)"),
            KorusError::VersionMismatch(v)   => write!(f, "Unsupported .korus version: {}", v),
            KorusError::ChecksumFailed       => write!(f, "Checksum failed — file may be corrupted or tampered with"),
            KorusError::InvalidUtf8          => write!(f, "Payload is not valid UTF-8"),
            KorusError::DecompressionFailed  => write!(f, "Payload is corrupt (decompression failed)"),
        }
    }
}

// allows ? use on std::io::Error inside functions returning Result<'_, KorusError>
impl From<std::io::Error> for KorusError {
    fn from(e: std::io::Error) -> Self {
        KorusError::Io(e)
    }
}

pub type KorusResult<T> = Result<T, KorusError>;
