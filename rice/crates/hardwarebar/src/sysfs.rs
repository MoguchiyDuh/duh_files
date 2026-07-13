use std::fs;
use std::path::{Path, PathBuf};

pub fn read_trimmed(path: impl AsRef<Path>) -> Option<String> {
    return fs::read_to_string(path)
        .ok()
        .map(|text| text.trim().to_string());
}

pub fn read_u64(path: impl AsRef<Path>) -> Option<u64> {
    return read_trimmed(path)?.parse().ok();
}

pub fn home_dir() -> PathBuf {
    return std::env::var_os("HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("/"));
}

pub fn cache_dir() -> PathBuf {
    if let Some(xdg) = std::env::var_os("XDG_CACHE_HOME") {
        return PathBuf::from(xdg);
    }
    return home_dir().join(".cache");
}
