use std::fs;
use std::io::{Read, Write};
use crate::format::{MAGIC, VERSION, xorTransform, computeChecksum};
use crate::error::{KorusError, KorusResult};

// encodes a json file into a .korus binary file
//
// file layout:
//  [4] magic number "KORS"
//  [4] version (u32, little-endian)
//  [4] checksum of ENCRYPTED payload (u32, little-endian)
//  [N] XOR-encrypted payload bytes
pub fn encode(jsonPath: &str, korusPath: &str) -> KorusResult<()> {
    // read raw json bytes
    let jsonBytes = fs::read(jsonPath)?;

    // encrypt a copy of the payload
    let mut payload = jsonBytes.clone();
    xorTransform(&mut payload);

    // checksum computed AFTER encryption
    // therefore, tampering with file changes decrypted content AND checksum
    let checksum = computeChecksum(&payload);
    let payloadSize = payload.len() as u32;

    // write everything out
    let mut outFile = fs::File::create(korusPath)?;
    outFile.write_all(MAGIC)?;
    outFile.write_all(&VERSION.to_le_bytes())?;
    outFile.write_all(&checksum.to_le_bytes())?;
    outFile.write_all(&payloadSize.to_le_bytes())?;
    outFile.write_all(&payload)?;

    Ok(())
}

// decodes a .korus binary file back into JSON
// returns an error if file is: invalid, wrong version, tampered with
pub fn decode(korusPath: &str, jsonPath: &str) -> KorusResult<()> {
    let mut inFile = fs::File::open(korusPath)?;
    let mut fileBytes = Vec::new();
    inFile.read_to_end(&mut fileBytes);

    // need at least 16 bytes for the header
    if fileBytes.len() < 16 {
        return Err(KorusError::InvalidMagic);
    }

    // validate magic
    if fileBytes[0..4] != *MAGIC {
        return Err(KorusError::InvalidMagic);
    }

    // validate version
    let version = u32::from_le_bytes(fileBytes[4..8].try_into().unwrap());
    if version != VERSION {
        return Err(KorusError::VersionMismatch(version));
    }

    // read header files
    let storedChecksum = u32::from_le_bytes(fileBytes[8..12].try_into().unwrap());
    let payloadSize = u32::from_le_bytes(fileBytes[12..16].try_into().unwrap()) as usize;

    // extract payload
    if fileBytes.len() < 16 + payloadSize {
        return Err(KorusError::ChecksumFailed);
    }
    let mut payload = fileBytes[16..16 + payloadSize].to_vec();

    // verify checksum BEFORE decrypting - catches tampering
    let actualChecksum = computeChecksum(&payload);
    if actualChecksum != storedChecksum {
        return Err(KorusError::ChecksumFailed);
    }

    // decrypt
    xorTransform(&mut payload);

    // validate utf-8 to know it's actually JSON
    let jsonStr = std::str::from_utf8(&payload)
        .map_err(|_| KorusError::InvalidUtf8)?;
    
    // write the JSON output
    fs::write(jsonPath, jsonStr);

    Ok(())
}