#![allow(non_snake_case)]

// magic bytes that identify a valid .korus file
pub const MAGIC: &[u8; 4] = b"KORS";
pub const VERSION_V1: u32 = 1;
pub const VERSION: u32 = 2;

// v1: XOR payload, XOR-fold checksum, no compression (legacy, decode-only)
// v2: LZSS-compressed payload, XOR'd, real CRC32 checksum

// XOR key baked into binary, not stored in file
// each byte of payload is XORed against repeating key
const XOR_KEY: &[u8] = b"K0ru5_5av3_k3y_v1"; // Korus Save Key v1

// XOR-encrypts or decrypts a byte slice in place
// XOR is its own inverse - calling twice returns original data
pub fn xorTransform(data: &mut Vec<u8>) {
    let keyLen = XOR_KEY.len();
    for (i, byte) in data.iter_mut().enumerate() {
        *byte ^= XOR_KEY[i % keyLen];
    }
}

// legacy v1 checksum: XOR-fold of every byte. kept only for decoding old saves
// computes a simple checksum by XORing all bytes together
// used to detect tampering - any change to payload changes the checksum
pub fn computeChecksum(data: &[u8]) -> u32 {
    data.iter().fold(0u32, |acc, &b| acc ^ b as u32)
}

// CRC-32 (IEEE 802.3), reflected polynomial 0xEDB88320), computed bit-by-bit
pub fn crc32(data: &[u8]) -> u32 {
    const POLY: u32 = 0xEDB88320;
    let mut crc: u32 = 0xFFFFFFFF;

    for &byte in data {
        crc ^= byte as u32;
        for _ in 0..8 {
            let mask = (crc & 1).wrapping_neg(); // 0xFFFFFFFF if lsb set, else 0
            crc = (crc >> 1) ^ (POLY & mask);
        }
    }

    !crc
}
