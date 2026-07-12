use std::process::Command;

use abi_stable::std_types::{ROption, RString, RVec};
use anyrun_plugin::*;

struct State {
    entries: Vec<(String, String)>,
}

#[init]
fn init(_config_dir: RString) -> State {
    let entries = common::capture("cliphist", &["list"])
        .lines()
        .filter_map(|line| {
            let (id, preview) = line.split_once('\t')?;
            Some((id.to_owned(), preview.to_owned()))
        })
        .collect();

    State { entries }
}

#[info]
fn info() -> PluginInfo {
    PluginInfo {
        name: "Clipboard".into(),
        icon: "edit-paste".into(),
    }
}

#[get_matches]
fn get_matches(input: RString, state: &State) -> RVec<Match> {
    let query = input.as_str();
    let matcher = common::matcher();
    let mut matches: Vec<_> = state
        .entries
        .iter()
        .enumerate()
        .filter_map(|(index, (_, preview))| {
            common::fuzzy(&matcher, preview, query).map(|score| (score, index, preview))
        })
        .collect();

    matches.sort_unstable_by(|left, right| right.0.cmp(&left.0));
    matches
        .into_iter()
        .take(12)
        .map(|(_, index, preview)| {
            let title = truncate_preview(preview, 80);
            common::match_entry(title, Some("clipboard".to_owned()), Some("edit-paste"), Some(index as u64))
        })
        .collect::<Vec<_>>()
        .into()
}

#[handler]
fn handler(selection: Match, state: &State) -> HandleResult {
    let ROption::RSome(index) = selection.id else {
        return HandleResult::Close;
    };
    let Some((id, _)) = usize::try_from(index)
        .ok()
        .and_then(|index| state.entries.get(index))
    else {
        return HandleResult::Close;
    };
    let Ok(output) = Command::new("cliphist").args(["decode", id]).output() else {
        return HandleResult::Close;
    };

    if output.status.success() {
        HandleResult::Copy(output.stdout.into())
    } else {
        HandleResult::Close
    }
}

fn truncate_preview(preview: &str, limit: usize) -> String {
    let mut chars = preview.chars();
    let title: String = chars.by_ref().take(limit).collect();
    if chars.next().is_some() {
        format!("{title}…")
    } else {
        title
    }
}
