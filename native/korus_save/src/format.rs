// magic bytes that identify a valid .korus file
pub const MAGIC: &[u8; 4] = b"KORS";
pub const VERSION: u32 = 1;

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

// computes a simple checksum by XORing all bytes together
// used to detect tampering - any change to payload changes the checksum
pub fn computeChecksum(data: &[u8]) -> u32 {
    data.iter().fold(0u32, |acc, &b| acc ^ b as u32)
}
