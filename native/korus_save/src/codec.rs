#![allow(non_snake_case)]

use std::fs;
use std::io::{Read, Write};
use crate::format::{MAGIC, VERSION_V1, VERSION, computeChecksum, crc32, xorTransform};
use crate::compress;
use crate::error::{KorusError, KorusResult};

// encodes a json file into a .korus binary file (always writes current version)
// v1 file layout:
//  [4] magic number "KORS"
//  [4] version (u32, little-endian)
//  [4] checksum of ENCRYPTED payload (u32, little-endian)
//  [N] XOR-encrypted payload bytes

// v2 file layout
//  [4] magic number "KORS"
//  [4] version (u32, little-endian) = 2
//  [4] CRC32 of ENCRYPTED payload (u32, little-endian)
//  [4] payload size (u32, little-endian)
//  [N] XOR-encrypted, LZSS-compressed payload bytes
pub fn encode(jsonPath: &str, korusPath: &str) -> KorusResult<()> {
    let jsonBytes = fs::read(jsonPath)?;

    let mut payload = compress::compress(&jsonBytes);
    xorTransform(&mut payload);

    let checksum = crc32(&payload);
    let payloadSize = payload.len() as u32;

    let mut outFile = fs::File::create(korusPath)?;
    outFile.write_all(MAGIC)?;
    outFile.write_all(&VERSION.to_le_bytes())?;
    outFile.write_all(&checksum.to_le_bytes())?;
    outFile.write_all(&payloadSize.to_le_bytes())?;
    outFile.write_all(&payload)?;

    Ok(())
}

// decodes a .korus binary file back into JSON
// supports both v1 (legacy, uncompressed) and v2 (compressed) files
pub fn decode(korusPath: &str, jsonPath: &str) -> KorusResult<()> {
    let mut inFile = fs::File::open(korusPath)?;
    let mut fileBytes = Vec::new();
    inFile.read_to_end(&mut fileBytes);

    if fileBytes.len() < 16 {
        return Err(KorusError::InvalidMagic);
    }

    if fileBytes[0..4] != *MAGIC {
        return Err(KorusError::InvalidMagic);
    }

    let version = u32::from_le_bytes(fileBytes[4..8].try_into().unwrap());
    if version != VERSION && version != VERSION_V1 {
        return Err(KorusError::VersionMismatch(version));
    }

    let storedChecksum = u32::from_le_bytes(fileBytes[8..12].try_into().unwrap());
    let payloadSize = u32::from_le_bytes(fileBytes[12..16].try_into().unwrap()) as usize;

    if fileBytes.len() < 16 + payloadSize {
        return Err(KorusError::ChecksumFailed);
    }
    let mut payload = fileBytes[16..16 + payloadSize].to_vec();

    let jsonBytes = if version == VERSION_V1 {
        let actualChecksum = computeChecksum(&payload);
        if actualChecksum != storedChecksum {
            return Err(KorusError::ChecksumFailed);
        }
        xorTransform(&mut payload);
        payload
    } else {
        let actualChecksum = crc32(&payload);
        if actualChecksum != storedChecksum {
            return Err(KorusError::ChecksumFailed);
        }
        xorTransform(&mut payload);
        compress::decompress(&payload)?
    };

    let jsonStr = std::str::from_utf8(&jsonBytes)
        .map_err(|_| KorusError::InvalidUtf8)?;

    fs::write(jsonPath, jsonStr);

    Ok(())
}
