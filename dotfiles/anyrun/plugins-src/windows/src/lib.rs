//! Hyprland window switcher plugin for anyrun.
//!
//! Lists open windows via `hyprctl clients -j` and focuses the selected one.
//! Prefix-free: results show up alongside apps. Bind a dedicated key to
//! `anyrun --plugins libwindows.so` for a focused switcher.

use abi_stable::std_types::{ROption, RString, RVec};
use anyrun_plugin::*;
use common::{capture, match_entry, matcher};
use fuzzy_matcher::skim::SkimMatcherV2;
use serde::Deserialize;

#[derive(Deserialize, Clone, Default)]
struct Workspace {
    #[serde(default)]
    name: String,
}

#[derive(Deserialize, Clone)]
struct Client {
    address: String,
    #[serde(default)]
    title: String,
    #[serde(default)]
    class: String,
    #[serde(default)]
    workspace: Workspace,
    #[serde(default)]
    mapped: bool,
}

struct State {
    clients: Vec<Client>,
    matcher: SkimMatcherV2,
}

#[init]
fn init(_config_dir: RString) -> State {
    let json = capture("hyprctl", &["clients", "-j"]);
    let clients: Vec<Client> = serde_json::from_str(&json).unwrap_or_default();
    let clients = clients
        .into_iter()
        .filter(|c| c.mapped && !c.title.is_empty())
        .collect();
    State {
        clients,
        matcher: matcher(),
    }
}

#[info]
fn info() -> PluginInfo {
    PluginInfo {
        name: "Windows".into(),
        icon: "preferences-system-windows".into(),
    }
}

#[get_matches]
fn get_matches(input: RString, state: &State) -> RVec<Match> {
    let query = input.trim();
    let mut scored: Vec<(usize, i64)> = state
        .clients
        .iter()
        .enumerate()
        .filter_map(|(i, c)| {
            let hay = format!("{} {} {}", c.title, c.class, c.workspace.name);
            common::fuzzy(&state.matcher, &hay, query).map(|s| (i, s))
        })
        .collect();

    scored.sort_by(|a, b| b.1.cmp(&a.1));
    scored.truncate(12);

    scored
        .into_iter()
        .map(|(i, _)| {
            let c = &state.clients[i];
            let desc = format!("{}  ·  ws {}", c.class, c.workspace.name);
            match_entry(c.title.clone(), Some(desc), Some("window"), Some(i as u64))
        })
        .collect::<Vec<_>>()
        .into()
}

#[handler]
fn handler(selection: Match, state: &State) -> HandleResult {
    if let ROption::RSome(id) = selection.id {
        if let Some(c) = state.clients.get(id as usize) {
            let addr = format!("address:{}", c.address);
            return common::spawn_detached("hyprctl", &["dispatch", "focuswindow", &addr]);
        }
    }
    HandleResult::Close
}
