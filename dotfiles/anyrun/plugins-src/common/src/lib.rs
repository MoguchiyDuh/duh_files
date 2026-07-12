//! Shared helpers for the custom anyrun plugins.

use std::process::{Command, Stdio};

use abi_stable::std_types::{ROption, RString};
use anyrun_plugin::{HandleResult, Match};
use fuzzy_matcher::skim::SkimMatcherV2;
use fuzzy_matcher::FuzzyMatcher;

/// Build a `Match` with the common fields defaulted.
pub fn match_entry(
    title: impl Into<String>,
    description: Option<String>,
    icon: Option<&str>,
    id: Option<u64>,
) -> Match {
    Match {
        title: RString::from(title.into()),
        description: description.map(RString::from).map_or(ROption::RNone, ROption::RSome),
        use_pango: false,
        icon: icon.map(RString::from).map_or(ROption::RNone, ROption::RSome),
        id: id.map_or(ROption::RNone, ROption::RSome),
    }
}

/// Fuzzy-score `text` against `query`. Empty query always matches with score 0.
pub fn fuzzy(matcher: &SkimMatcherV2, text: &str, query: &str) -> Option<i64> {
    if query.is_empty() {
        return Some(0);
    }
    matcher.fuzzy_match(text, query)
}

/// A reusable smart-case fuzzy matcher.
pub fn matcher() -> SkimMatcherV2 {
    SkimMatcherV2::default().smart_case()
}

/// Spawn a detached command (fire-and-forget), returning a `Close` result.
pub fn spawn_detached(program: &str, args: &[&str]) -> HandleResult {
    let _ = Command::new(program)
        .args(args)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();
    HandleResult::Close
}

/// Run a command through `sh -c`, detached. Returns `Close`.
pub fn spawn_shell(command: &str) -> HandleResult {
    let _ = Command::new("/usr/bin/env")
        .args(["sh", "-c", command])
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();
    HandleResult::Close
}

/// Run a command and capture stdout as a UTF-8 string (lossy). Returns empty on failure.
pub fn capture(program: &str, args: &[&str]) -> String {
    Command::new(program)
        .args(args)
        .output()
        .ok()
        .map(|o| String::from_utf8_lossy(&o.stdout).into_owned())
        .unwrap_or_default()
}
