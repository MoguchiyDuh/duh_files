use abi_stable::std_types::{RString, RVec};
use anyrun_plugin::*;

struct State;

#[init]
fn init(_config_dir: RString) -> State {
    State
}

#[info]
fn info() -> PluginInfo {
    PluginInfo {
        name: "Transform".into(),
        icon: "edit-copy".into(),
    }
}

#[get_matches]
fn get_matches(input: RString, _state: &State) -> RVec<Match> {
    let Some(source) = input.as_str().strip_prefix('~').map(str::trim) else {
        return RVec::new();
    };
    if source.is_empty() {
        return RVec::new();
    }

    transforms(source)
        .into_iter()
        .take(20)
        .enumerate()
        .map(|(index, (name, value))| {
            common::match_entry(value, Some(name.to_owned()), Some("edit-copy"), Some(index as u64))
        })
        .collect::<Vec<_>>()
        .into()
}

#[handler]
fn handler(selection: Match, _state: &State) -> HandleResult {
    HandleResult::Copy(String::from(selection.title).into_bytes().into())
}

fn transforms(source: &str) -> Vec<(&'static str, String)> {
    let words = split_words(source);
    let mut result = vec![
        ("UPPERCASE", source.to_uppercase()),
        ("lowercase", source.to_lowercase()),
        ("Title Case", title_case(&words)),
        ("Sentence case", sentence_case(source)),
        ("camelCase", camel_case(&words)),
        ("PascalCase", pascal_case(&words)),
        ("snake_case", join_case(&words, "_", Case::Lower)),
        ("kebab-case", join_case(&words, "-", Case::Lower)),
        ("CONSTANT_CASE", join_case(&words, "_", Case::Upper)),
        ("slug", slug(source)),
        ("base64 encode", base64_encode(source.as_bytes())),
        ("url encode", url_encode(source)),
        ("hex encode", hex_encode(source.as_bytes())),
        ("sha256 hex", sha256_hex(source.as_bytes())),
        ("sha512 hex", sha512_hex(source.as_bytes())),
    ];

    if let Some(decoded) = base64_decode(source).and_then(|bytes| String::from_utf8(bytes).ok()) {
        result.push(("base64 decode", decoded));
    }
    if let Some(decoded) = url_decode(source) {
        result.push(("url decode", decoded));
    }
    if let Some((red, green, blue, alpha)) = parse_color(source) {
        result.push(("HEX", format!("#{red:02X}{green:02X}{blue:02X}")));
        result.push(("rgb", format!("rgb({red}, {green}, {blue})")));
        result.push(("rgba", format!("rgba({red}, {green}, {blue}, {})", alpha_string(alpha))));
        let (hue, saturation, lightness) = rgb_to_hsl(red, green, blue);
        result.push(("hsl", format!("hsl({hue}, {saturation}%, {lightness}%)")));
    }
    result
}

fn split_words(text: &str) -> Vec<String> {
    let chars: Vec<char> = text.chars().collect();
    let mut words = Vec::new();
    let mut word = String::new();
    for (index, &character) in chars.iter().enumerate() {
        if !character.is_alphanumeric() {
            if !word.is_empty() {
                words.push(std::mem::take(&mut word));
            }
            continue;
        }
        let previous = index.checked_sub(1).and_then(|i| chars.get(i)).copied();
        let next = chars.get(index + 1).copied();
        let hump = character.is_uppercase()
            && previous.is_some_and(char::is_alphanumeric)
            && (previous.is_some_and(char::is_lowercase)
                || (previous.is_some_and(char::is_uppercase) && next.is_some_and(char::is_lowercase)));
        if hump && !word.is_empty() {
            words.push(std::mem::take(&mut word));
        }
        word.push(character);
    }
    if !word.is_empty() {
        words.push(word);
    }
    words
}

fn capitalize(word: &str) -> String {
    let mut characters = word.chars();
    let Some(first) = characters.next() else {
        return String::new();
    };
    first.to_uppercase().chain(characters.flat_map(char::to_lowercase)).collect()
}

fn title_case(words: &[String]) -> String {
    words.iter().map(|word| capitalize(word)).collect::<Vec<_>>().join(" ")
}

fn sentence_case(text: &str) -> String {
    let lower = text.to_lowercase();
    let mut characters = lower.chars();
    let Some(first) = characters.next() else {
        return lower;
    };
    first.to_uppercase().chain(characters).collect()
}

fn camel_case(words: &[String]) -> String {
    let Some((first, rest)) = words.split_first() else {
        return String::new();
    };
    let mut value = first.to_lowercase();
    for word in rest {
        value.push_str(&capitalize(word));
    }
    value
}

fn pascal_case(words: &[String]) -> String {
    words.iter().map(|word| capitalize(word)).collect()
}

enum Case { Lower, Upper }

fn join_case(words: &[String], separator: &str, case: Case) -> String {
    words.iter().map(|word| match case { Case::Lower => word.to_lowercase(), Case::Upper => word.to_uppercase() }).collect::<Vec<_>>().join(separator)
}

fn slug(text: &str) -> String {
    let mut value = String::new();
    let mut dash = false;
    for character in text.chars() {
        if character.is_alphanumeric() {
            value.extend(character.to_lowercase());
            dash = false;
        } else if !value.is_empty() && !dash {
            value.push('-');
            dash = true;
        }
    }
    value.trim_end_matches('-').to_owned()
}

const BASE64: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

fn base64_encode(bytes: &[u8]) -> String {
    let mut output = String::with_capacity(bytes.len().div_ceil(3) * 4);
    for chunk in bytes.chunks(3) {
        let value = (u32::from(chunk[0]) << 16) | (u32::from(*chunk.get(1).unwrap_or(&0)) << 8) | u32::from(*chunk.get(2).unwrap_or(&0));
        output.push(BASE64[((value >> 18) & 63) as usize] as char);
        output.push(BASE64[((value >> 12) & 63) as usize] as char);
        output.push(if chunk.len() > 1 { BASE64[((value >> 6) & 63) as usize] as char } else { '=' });
        output.push(if chunk.len() > 2 { BASE64[(value & 63) as usize] as char } else { '=' });
    }
    output
}

fn base64_decode(text: &str) -> Option<Vec<u8>> {
    let bytes = text.as_bytes();
    if bytes.is_empty() || bytes.len() % 4 != 0 { return None; }
    let mut output = Vec::with_capacity(bytes.len() / 4 * 3);
    for (chunk_index, chunk) in bytes.chunks_exact(4).enumerate() {
        let last = chunk_index + 1 == bytes.len() / 4;
        let padding = usize::from(chunk[2] == b'=') + usize::from(chunk[3] == b'=');
        if padding > 0 && (!last || (padding == 1 && chunk[2] == b'=') || chunk[0] == b'=' || chunk[1] == b'=') { return None; }
        let a = base64_value(chunk[0])?; let b = base64_value(chunk[1])?;
        let c = if chunk[2] == b'=' { 0 } else { base64_value(chunk[2])? };
        let d = if chunk[3] == b'=' { 0 } else { base64_value(chunk[3])? };
        let value = (u32::from(a) << 18) | (u32::from(b) << 12) | (u32::from(c) << 6) | u32::from(d);
        output.push((value >> 16) as u8);
        if padding < 2 { output.push((value >> 8) as u8); }
        if padding == 0 { output.push(value as u8); }
    }
    Some(output)
}

fn base64_value(byte: u8) -> Option<u8> {
    match byte { b'A'..=b'Z' => Some(byte - b'A'), b'a'..=b'z' => Some(byte - b'a' + 26), b'0'..=b'9' => Some(byte - b'0' + 52), b'+' => Some(62), b'/' => Some(63), _ => None }
}

fn url_encode(text: &str) -> String {
    let mut output = String::new();
    for byte in text.bytes() {
        if byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.' | b'~') { output.push(byte as char); } else { output.push('%'); output.push_str(&format!("{byte:02X}")); }
    }
    output
}

fn url_decode(text: &str) -> Option<String> {
    let bytes = text.as_bytes(); let mut output = Vec::with_capacity(bytes.len()); let mut index = 0;
    while index < bytes.len() { if bytes[index] == b'%' { let high = *bytes.get(index + 1)?; let low = *bytes.get(index + 2)?; output.push(hex_value(high)? << 4 | hex_value(low)?); index += 3; } else { output.push(bytes[index]); index += 1; } }
    String::from_utf8(output).ok()
}

fn hex_encode(bytes: &[u8]) -> String { bytes.iter().map(|byte| format!("{byte:02x}")).collect() }
fn hex_value(byte: u8) -> Option<u8> { match byte { b'0'..=b'9' => Some(byte - b'0'), b'a'..=b'f' => Some(byte - b'a' + 10), b'A'..=b'F' => Some(byte - b'A' + 10), _ => None } }

fn parse_color(text: &str) -> Option<(u8, u8, u8, u8)> {
    let hex = text.strip_prefix('#').unwrap_or(text);
    if !matches!(hex.len(), 3 | 4 | 6 | 8) || !hex.bytes().all(|byte| hex_value(byte).is_some()) { return None; }
    let value = |index| hex_value(hex.as_bytes()[index]).unwrap_or(0);
    let pair = |index| value(index) << 4 | value(index + 1);
    Some(match hex.len() { 3 => { let r = value(0) * 17; let g = value(1) * 17; let b = value(2) * 17; (r, g, b, 255) }, 4 => { let r = value(0) * 17; let g = value(1) * 17; let b = value(2) * 17; (r, g, b, value(3) * 17) }, 6 => (pair(0), pair(2), pair(4), 255), 8 => (pair(0), pair(2), pair(4), pair(6)), _ => return None })
}

fn alpha_string(alpha: u8) -> String { let value = f64::from(alpha) / 255.0; format!("{value:.3}").trim_end_matches('0').trim_end_matches('.').to_owned() }

fn rgb_to_hsl(red: u8, green: u8, blue: u8) -> (u16, u16, u16) {
    let (red, green, blue) = (f64::from(red) / 255.0, f64::from(green) / 255.0, f64::from(blue) / 255.0);
    let max = red.max(green).max(blue); let min = red.min(green).min(blue); let delta = max - min; let lightness = (max + min) / 2.0;
    if delta == 0.0 { return (0, 0, (lightness * 100.0).round() as u16); }
    let saturation = delta / (1.0 - (2.0 * lightness - 1.0).abs());
    let hue = if max == red { 60.0 * ((green - blue) / delta).rem_euclid(6.0) } else if max == green { 60.0 * ((blue - red) / delta + 2.0) } else { 60.0 * ((red - green) / delta + 4.0) };
    (hue.round() as u16 % 360, (saturation * 100.0).round() as u16, (lightness * 100.0).round() as u16)
}

fn sha256_hex(input: &[u8]) -> String { sha256(input).iter().map(|byte| format!("{byte:02x}")).collect() }
fn sha512_hex(input: &[u8]) -> String { sha512(input).iter().map(|byte| format!("{byte:02x}")).collect() }

fn sha256(input: &[u8]) -> [u8; 32] {
    const K: [u32; 64] = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
    let mut data = input.to_vec(); let bits = (data.len() as u64).wrapping_mul(8); data.push(0x80); while data.len() % 64 != 56 { data.push(0); } data.extend_from_slice(&bits.to_be_bytes());
    let mut hash = [0x6a09e667u32,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    for chunk in data.chunks_exact(64) { let mut w = [0u32; 64]; for (i, word) in w.iter_mut().take(16).enumerate() { *word = u32::from_be_bytes(chunk[i * 4..i * 4 + 4].try_into().unwrap_or([0; 4])); } for i in 16..64 { w[i] = w[i-16].wrapping_add(w[i-15].rotate_right(7) ^ w[i-15].rotate_right(18) ^ (w[i-15] >> 3)).wrapping_add(w[i-7]).wrapping_add(w[i-2].rotate_right(17) ^ w[i-2].rotate_right(19) ^ (w[i-2] >> 10)); } let (mut a,mut b,mut c,mut d,mut e,mut f,mut g,mut h) = (hash[0],hash[1],hash[2],hash[3],hash[4],hash[5],hash[6],hash[7]); for i in 0..64 { let s1=e.rotate_right(6)^e.rotate_right(11)^e.rotate_right(25); let choice=(e&f)^(!e&g); let t1=h.wrapping_add(s1).wrapping_add(choice).wrapping_add(K[i]).wrapping_add(w[i]); let s0=a.rotate_right(2)^a.rotate_right(13)^a.rotate_right(22); let majority=(a&b)^(a&c)^(b&c); let t2=s0.wrapping_add(majority); h=g;g=f;f=e;e=d.wrapping_add(t1);d=c;c=b;b=a;a=t1.wrapping_add(t2); } for (value, add) in hash.iter_mut().zip([a,b,c,d,e,f,g,h]) { *value = value.wrapping_add(add); } }
    let mut output = [0u8; 32]; for (index, value) in hash.iter().enumerate() { output[index * 4..index * 4 + 4].copy_from_slice(&value.to_be_bytes()); } output
}

fn sha512(input: &[u8]) -> [u8; 64] {
    const K: [u64; 80] = [0x428a2f98d728ae22,0x7137449123ef65cd,0xb5c0fbcfec4d3b2f,0xe9b5dba58189dbbc,0x3956c25bf348b538,0x59f111f1b605d019,0x923f82a4af194f9b,0xab1c5ed5da6d8118,0xd807aa98a3030242,0x12835b0145706fbe,0x243185be4ee4b28c,0x550c7dc3d5ffb4e2,0x72be5d74f27b896f,0x80deb1fe3b1696b1,0x9bdc06a725c71235,0xc19bf174cf692694,0xe49b69c19ef14ad2,0xefbe4786384f25e3,0x0fc19dc68b8cd5b5,0x240ca1cc77ac9c65,0x2de92c6f592b0275,0x4a7484aa6ea6e483,0x5cb0a9dcbd41fbd4,0x76f988da831153b5,0x983e5152ee66dfab,0xa831c66d2db43210,0xb00327c898fb213f,0xbf597fc7beef0ee4,0xc6e00bf33da88fc2,0xd5a79147930aa725,0x06ca6351e003826f,0x142929670a0e6e70,0x27b70a8546d22ffc,0x2e1b21385c26c926,0x4d2c6dfc5ac42aed,0x53380d139d95b3df,0x650a73548baf63de,0x766a0abb3c77b2a8,0x81c2c92e47edaee6,0x92722c851482353b,0xa2bfe8a14cf10364,0xa81a664bbc423001,0xc24b8b70d0f89791,0xc76c51a30654be30,0xd192e819d6ef5218,0xd69906245565a910,0xf40e35855771202a,0x106aa07032bbd1b8,0x19a4c116b8d2d0c8,0x1e376c085141ab53,0x2748774cdf8eeb99,0x34b0bcb5e19b48a8,0x391c0cb3c5c95a63,0x4ed8aa4ae3418acb,0x5b9cca4f7763e373,0x682e6ff3d6b2b8a3,0x748f82ee5defb2fc,0x78a5636f43172f60,0x84c87814a1f0ab72,0x8cc702081a6439ec,0x90befffa23631e28,0xa4506cebde82bde9,0xbef9a3f7b2c67915,0xc67178f2e372532b,0xca273eceea26619c,0xd186b8c721c0c207,0xeada7dd6cde0eb1e,0xf57d4f7fee6ed178,0x06f067aa72176fba,0x0a637dc5a2c898a6,0x113f9804bef90dae,0x1b710b35131c471b,0x28db77f523047d84,0x32caab7b40c72493,0x3c9ebe0a15c9bebc,0x431d67c49c100d4c,0x4cc5d4becb3e42b6,0x597f299cfc657e2a,0x5fcb6fab3ad6faec,0x6c44198c4a475817];
    let mut data = input.to_vec(); let bits = (data.len() as u128).wrapping_mul(8); data.push(0x80); while data.len() % 128 != 112 { data.push(0); } data.extend_from_slice(&bits.to_be_bytes());
    let mut hash = [0x6a09e667f3bcc908u64,0xbb67ae8584caa73b,0x3c6ef372fe94f82b,0xa54ff53a5f1d36f1,0x510e527fade682d1,0x9b05688c2b3e6c1f,0x1f83d9abfb41bd6b,0x5be0cd19137e2179];
    for chunk in data.chunks_exact(128) { let mut w = [0u64; 80]; for (i, word) in w.iter_mut().take(16).enumerate() { *word = u64::from_be_bytes(chunk[i * 8..i * 8 + 8].try_into().unwrap_or([0; 8])); } for i in 16..80 { w[i] = w[i-16].wrapping_add(w[i-15].rotate_right(1)^w[i-15].rotate_right(8)^(w[i-15]>>7)).wrapping_add(w[i-7]).wrapping_add(w[i-2].rotate_right(19)^w[i-2].rotate_right(61)^(w[i-2]>>6)); } let (mut a,mut b,mut c,mut d,mut e,mut f,mut g,mut h) = (hash[0],hash[1],hash[2],hash[3],hash[4],hash[5],hash[6],hash[7]); for i in 0..80 { let t1=h.wrapping_add(e.rotate_right(14)^e.rotate_right(18)^e.rotate_right(41)).wrapping_add((e&f)^(!e&g)).wrapping_add(K[i]).wrapping_add(w[i]); let t2=(a.rotate_right(28)^a.rotate_right(34)^a.rotate_right(39)).wrapping_add((a&b)^(a&c)^(b&c)); h=g;g=f;f=e;e=d.wrapping_add(t1);d=c;c=b;b=a;a=t1.wrapping_add(t2); } for (value, add) in hash.iter_mut().zip([a,b,c,d,e,f,g,h]) { *value = value.wrapping_add(add); } }
    let mut output = [0u8; 64]; for (index, value) in hash.iter().enumerate() { output[index * 8..index * 8 + 8].copy_from_slice(&value.to_be_bytes()); } output
}
