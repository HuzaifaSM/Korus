#![allow(non_snake_case)]

use std::collections::HashMap;
use crate::error::{KorusError, KorusResult};

const WINDOW_SIZE: usize = 4096;
const MIN_MATCH: usize = 3;
const MAX_MATCH: usize = 18;
const MAX_CHAIN: usize = 64; // bounded search depth so worst case stays fast

pub fn compress(data: &[u8]) -> Vec<u8> {
    let mut out = Vec::with_capacity(data.len() / 2 + 8);
    out.extend_from_slice(&(data.len() as u32).to_le_bytes());

    // map a 3-byte prefix to every position its been seen at (most recent last)
    let mut chains: HashMap<[u8; 3], Vec<usize>> = HashMap::new();

    let mut pos = 0usize;
    let mut flagByte: u8 = 0;
    let mut flagBit = 0u8;
    let mut tokenBuf: Vec<u8> = Vec::with_capacity(16);

    macro_rules! flush {
        () => {
            if flagBit > 0 {
                out.push(flagByte);
                out.extend_from_slice(&tokenBuf);
                flagByte = 0;
                flagBit = 0;
                tokenBuf.clear();
            }
        };
    }

    while pos < data.len() {
        let mut bestLen = 0usize;
        let mut bestOffset = 0usize;

        if pos + MIN_MATCH <= data.len() {
            let key = [data[pos], data[pos + 1], data[pos + 2]];
            if let Some(candidates) = chains.get(&key) {
                let windowStart = pos.saturating_sub(WINDOW_SIZE);
                for &candidatePos in candidates.iter().rev().take(MAX_CHAIN) {
                    if candidatePos < windowStart {
                        break;
                    }
                    let maxLen = (data.len() - pos).min(MAX_MATCH);
                    let mut len = 0;
                    while len < maxLen && data[candidatePos + len] == data[pos + len] {
                        len += 1;
                    }
                    if len > bestLen {
                        bestLen = len;
                        bestOffset = pos - candidatePos;
                    }
                }
            }
        }

        if bestLen >= MIN_MATCH {
            let offsetMinusOne = (bestOffset - 1) as u16;
            let lengthCode = (bestLen - MIN_MATCH) as u8;
            tokenBuf.push((offsetMinusOne >> 4) as u8);
            tokenBuf.push(((offsetMinusOne & 0xF) << 4) as u8 | lengthCode);
            flagByte |= 1 << flagBit;

            for i in pos..(pos + bestLen).min(data.len().saturating_sub(2)) {
                let key = [data[i], data[i + 1], data[i + 2]];
                chains.entry(key).or_default().push(i);
            }
            pos += bestLen;
        } else {
            tokenBuf.push(data[pos]);
            if pos + 2 < data.len() {
                let key = [data[pos], data[pos + 1], data[pos + 2]];
                chains.entry(key).or_default().push(pos);
            }
            pos += 1;
        }

        flagBit += 1;
        if flagBit == 8 {
            flush!();
        }
    }
    flush!();

    out
}

pub fn decompress(data: &[u8]) -> KorusResult<Vec<u8>> {
    if data.len() < 4 {
        return Err(KorusError::DecompressionFailed);
    }
    let origLen = u32::from_le_bytes(data[0..4].try_into().unwrap()) as usize;
    let mut out = Vec::with_capacity(origLen);

    let mut i = 4usize;
    while out.len() < origLen {
        if i >= data.len() {
            return Err(KorusError::DecompressionFailed);
        }
        let flagByte = data[i];
        i += 1;

        for bit in 0..8 {
            if out.len() >= origLen {
                break;
            }
            let isMatch = (flagByte >> bit) & 1 == 1;
            if isMatch {
                if i + 2 > data.len() {
                    return Err(KorusError::DecompressionFailed);
                }
                let offsetMinusOne = ((data[i] as u16) << 4) | ((data[i + 1] as u16) >> 4);
                let lengthCode  = data[i + 1] & 0xF;
                i += 2;

                let offset = offsetMinusOne as usize + 1;
                let length = lengthCode as usize + MIN_MATCH;

                if offset > out.len() {
                    return Err(KorusError::DecompressionFailed);
                }
                let start = out.len() - offset;
                for k in 0..length {
                    let byte = out[start + k]; // may reference bytes just written (overlapping runes)
                    out.push(byte);
                }
            } else {
                if i >= data.len() {
                    return Err(KorusError::DecompressionFailed);
                }
                out.push(data[i]);
                i += 1;
            }
        }
    }

    Ok(out)
}