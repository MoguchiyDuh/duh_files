use abi_stable::std_types::{RString, RVec};
use anyrun_plugin::*;
use common::{capture, match_entry, matcher};
use fuzzy_matcher::skim::SkimMatcherV2;
use serde::Deserialize;

#[derive(Deserialize, Default)]
#[serde(default)]
struct HyprBind {
    modmask: i64,
    key: String,
    keycode: i64,
    dispatcher: String,
    arg: String,
    description: String,
}

struct Bind {
    shortcut: String,
    action: String,
}

struct State {
    binds: Vec<Bind>,
    matcher: SkimMatcherV2,
}

#[init]
fn init(_config_dir: RString) -> State {
    let json = capture("hyprctl", &["binds", "-j"]);
    let hypr_binds: Vec<HyprBind> = serde_json::from_str(&json).unwrap_or_default();

    let binds = hypr_binds
        .iter()
        .map(|b| Bind {
            shortcut: build_shortcut(b),
            action: build_action(b),
        })
        .collect();

    State {
        binds,
        matcher: matcher(),
    }
}

#[info]
fn info() -> PluginInfo {
    PluginInfo {
        name: "Keybinds".into(),
        icon: "preferences-desktop-keyboard-shortcuts".into(),
    }
}

#[get_matches]
fn get_matches(input: RString, state: &State) -> RVec<Match> {
    let query = input.trim();
    let mut scored: Vec<(usize, i64)> = state
        .binds
        .iter()
        .enumerate()
        .filter_map(|(i, b)| {
            let hay = format!("{} {}", b.shortcut, b.action);
            common::fuzzy(&state.matcher, &hay, query).map(|s| (i, s))
        })
        .collect();

    scored.sort_by(|a, b| b.1.cmp(&a.1));
    scored.truncate(15);

    scored
        .into_iter()
        .map(|(i, _)| {
            let b = &state.binds[i];
            match_entry(
                b.shortcut.clone(),
                Some(b.action.clone()),
                Some("preferences-desktop-keyboard-shortcuts"),
                None,
            )
        })
        .collect::<Vec<_>>()
        .into()
}

#[handler]
fn handler(selection: Match, _state: &State) -> HandleResult {
    HandleResult::Copy(selection.title.into_bytes().into())
}

fn decode_modmask(mask: i64) -> Vec<&'static str> {
    let mut mods = Vec::new();
    if mask & 64 != 0 {
        mods.push("Super");
    }
    if mask & 4 != 0 {
        mods.push("Ctrl");
    }
    if mask & 8 != 0 {
        mods.push("Alt");
    }
    if mask & 1 != 0 {
        mods.push("Shift");
    }
    mods
}

fn build_shortcut(bind: &HyprBind) -> String {
    let mods = decode_modmask(bind.modmask);
    let key = if bind.key.is_empty() {
        format!("code:{}", bind.keycode)
    } else {
        bind.key.clone()
    };
    if mods.is_empty() {
        key
    } else {
        format!("{}+{}", mods.join("+"), key)
    }
}

fn build_action(bind: &HyprBind) -> String {
    if !bind.description.is_empty() {
        bind.description.clone()
    } else {
        let s = format!("{} {}", bind.dispatcher, bind.arg).trim().to_string();
        if s.is_empty() {
            "unknown".to_string()
        } else {
            s
        }
    }
}
