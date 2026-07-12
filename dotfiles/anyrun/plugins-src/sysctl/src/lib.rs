use std::{fs, process::Command};

use abi_stable::std_types::{ROption, RString, RVec};
use anyrun_plugin::*;
use common::{capture, match_entry, spawn_detached, spawn_shell};

const VOL_SET: u64 = 0;
const VOL_PLUS: u64 = 1;
const VOL_MINUS: u64 = 2;
const VOL_MUTE: u64 = 3;
const BRIGHT_SET: u64 = 4;
const BRIGHT_PLUS: u64 = 5;
const BRIGHT_MINUS: u64 = 6;

#[derive(Clone, Copy)]
enum VolumeBackend {
    None,
    Wpctl,
    Pactl,
}

#[derive(Clone, Copy)]
enum BrightnessBackend {
    None,
    Backlight,
    Ddc { bus: Option<u32> },
}

struct State {
    volume: VolumeBackend,
    brightness: BrightnessBackend,
    volume_percent: Option<u8>,
    muted: bool,
    brightness_percent: Option<u8>,
}

#[derive(Clone, Copy)]
enum Argument {
    Exact(u8),
    Plus(u8),
    Minus(u8),
}

#[init]
fn init(_config_dir: RString) -> State {
    let volume = if have("wpctl") {
        VolumeBackend::Wpctl
    } else if have("pactl") {
        VolumeBackend::Pactl
    } else {
        VolumeBackend::None
    };
    let (volume_percent, muted) = volume_current(volume);

    let brightness = if have("brightnessctl") && has_backlight() {
        BrightnessBackend::Backlight
    } else if have("ddcutil") {
        // Keep launcher initialization bounded even when a DDC adapter is wedged.
        BrightnessBackend::Ddc {
            bus: ddc_bus_with_timeout(1),
        }
    } else {
        BrightnessBackend::None
    };
    let brightness_percent = match brightness {
        BrightnessBackend::Backlight => backlight_current(),
        BrightnessBackend::Ddc { bus: Some(bus) } => ddc_current(bus, 1),
        _ => None,
    };

    State {
        volume,
        brightness,
        volume_percent,
        muted,
        brightness_percent,
    }
}

#[info]
fn info() -> PluginInfo {
    PluginInfo {
        name: "System controls".into(),
        icon: "preferences-system".into(),
    }
}

#[get_matches]
fn get_matches(input: RString, state: &State) -> RVec<Match> {
    let query = input.to_lowercase();
    let is_mute = query.contains("mute");
    let is_volume = is_mute || query.contains("volume") || query.contains("vol");
    let is_brightness = query.contains("brightness") || query.contains("bright");
    if !is_volume && !is_brightness {
        return RVec::new();
    }

    let argument = parse_argument(&query);
    let mut matches = Vec::new();
    if is_volume {
        volume_matches(&mut matches, state, argument, is_mute);
    }
    if is_brightness && !is_mute {
        brightness_matches(&mut matches, state, argument);
    }
    matches.into()
}

#[handler]
fn handler(selection: Match, state: &State) -> HandleResult {
    let ROption::RSome(id) = selection.id else {
        return HandleResult::Close;
    };
    let kind = id >> 8;
    let value = (id & 0xff).min(100);
    match kind {
        VOL_SET => set_volume(state.volume, value),
        VOL_PLUS => relative_volume(state.volume, value, true),
        VOL_MINUS => relative_volume(state.volume, value, false),
        VOL_MUTE => mute_volume(state.volume),
        BRIGHT_SET => set_brightness(state.brightness, value),
        BRIGHT_PLUS => relative_brightness(state.brightness, value, true),
        BRIGHT_MINUS => relative_brightness(state.brightness, value, false),
        _ => HandleResult::Close,
    }
}

fn volume_matches(matches: &mut Vec<Match>, state: &State, argument: Option<Argument>, mute_only: bool) {
    if matches!(state.volume, VolumeBackend::None) {
        return;
    }
    let description = volume_description(state);
    if mute_only {
        matches.push(match_entry(
            if state.muted { "Unmute" } else { "Mute" },
            description,
            Some(if state.muted { "audio-volume-muted" } else { "audio-volume-high" }),
            Some(pack(VOL_MUTE, 0)),
        ));
        return;
    }
    match argument {
        Some(Argument::Exact(value)) => matches.push(match_entry(format!("Set volume to {value}%"), description, Some("audio-volume-high"), Some(pack(VOL_SET, value)))),
        Some(Argument::Plus(value)) => matches.push(volume_relative_entry(state, value, true)),
        Some(Argument::Minus(value)) => matches.push(volume_relative_entry(state, value, false)),
        None => {
            if let Some(percent) = state.volume_percent {
                matches.push(match_entry(
                    format!("Current volume: {percent}%"),
                    description.clone(),
                    Some("audio-volume-high"),
                    None,
                ));
            }
            for percent in [0, 25, 50, 75, 100] {
                matches.push(match_entry(
                    format!("Volume {percent}%"),
                    description.clone(),
                    Some("audio-volume-high"),
                    Some(pack(VOL_SET, percent)),
                ));
            }
            matches.push(match_entry(
                if state.muted { "Unmute" } else { "Mute" },
                description,
                Some(if state.muted { "audio-volume-muted" } else { "audio-volume-high" }),
                Some(pack(VOL_MUTE, 0)),
            ));
        }
    }
}

fn brightness_matches(matches: &mut Vec<Match>, state: &State, argument: Option<Argument>) {
    if matches!(state.brightness, BrightnessBackend::None) {
        return;
    }
    let description = state.brightness_percent.map(|p| format!("current: {p}%"));
    match argument {
        Some(Argument::Exact(value)) => matches.push(match_entry(format!("Set brightness to {value}%"), description, Some("display-brightness"), Some(pack(BRIGHT_SET, value)))),
        Some(Argument::Plus(value)) => matches.push(brightness_relative_entry(state, value, true)),
        Some(Argument::Minus(value)) => matches.push(brightness_relative_entry(state, value, false)),
        None => {
            if let Some(percent) = state.brightness_percent {
                matches.push(match_entry(
                    format!("Current brightness: {percent}%"),
                    description.clone(),
                    Some("display-brightness"),
                    None,
                ));
            }
            for percent in [0, 25, 50, 75, 100] {
                matches.push(match_entry(
                    format!("Brightness {percent}%"),
                    description.clone(),
                    Some("display-brightness"),
                    Some(pack(BRIGHT_SET, percent)),
                ));
            }
        }
    }
}

fn volume_relative_entry(state: &State, value: u8, plus: bool) -> Match {
    let sign = if plus { '+' } else { '-' };
    let preview = state.volume_percent.map(|current| {
        if plus { current.saturating_add(value).min(100) } else { current.saturating_sub(value) }
    });
    let title = preview.map_or_else(
        || format!("Volume {sign}{value}%"),
        |next| format!("Volume {sign}{value}% -> {next}%"),
    );
    match_entry(title, volume_description(state), Some("audio-volume-high"), Some(pack(if plus { VOL_PLUS } else { VOL_MINUS }, value)))
}

fn brightness_relative_entry(state: &State, value: u8, plus: bool) -> Match {
    let sign = if plus { '+' } else { '-' };
    let title = state.brightness_percent.map_or_else(
        || format!("Brightness {sign}{value}%"),
        |current| format!("Brightness {sign}{value}% -> {}%", if plus { current.saturating_add(value).min(100) } else { current.saturating_sub(value) }),
    );
    match_entry(title, state.brightness_percent.map(|p| format!("current: {p}%")), Some("display-brightness"), Some(pack(if plus { BRIGHT_PLUS } else { BRIGHT_MINUS }, value)))
}

fn pack(kind: u64, value: u8) -> u64 { (kind << 8) | u64::from(value) }

fn parse_argument(query: &str) -> Option<Argument> {
    query.split_whitespace().find_map(|word| {
        let (kind, digits): (fn(u8) -> Argument, &str) = match word.as_bytes().first() {
            Some(b'+') => (Argument::Plus, &word[1..]),
            Some(b'-') => (Argument::Minus, &word[1..]),
            _ => (Argument::Exact, word),
        };
        let value = digits.parse::<u8>().ok()?;
        (value <= 100).then_some(kind(value))
    })
}

fn volume_description(state: &State) -> Option<String> {
    state.volume_percent.map(|p| format!("current: {p}%{}", if state.muted { " (muted)" } else { "" }))
}

fn have(bin: &str) -> bool {
    Command::new("sh").args(["-c", &format!("command -v {bin} >/dev/null 2>&1")]).status().map(|status| status.success()).unwrap_or(false)
}

fn has_backlight() -> bool {
    fs::read_dir("/sys/class/backlight").ok().into_iter().flatten().any(|entry| entry.ok().is_some_and(|entry| entry.path().join("brightness").is_file()))
}

fn volume_current(backend: VolumeBackend) -> (Option<u8>, bool) {
    match backend {
        VolumeBackend::Wpctl => {
            let output = capture("wpctl", &["get-volume", "@DEFAULT_AUDIO_SINK@"]);
            (output.split_whitespace().find_map(|word| word.parse::<f32>().ok()).map(|v| (v * 100.0).round().clamp(0.0, 100.0) as u8), output.contains("MUTED"))
        }
        VolumeBackend::Pactl => {
            let volume = capture("pactl", &["get-sink-volume", "@DEFAULT_SINK@"]).split_whitespace().find_map(|word| word.strip_suffix('%').and_then(|v| v.parse::<u8>().ok()));
            let muted = capture("pactl", &["get-sink-mute", "@DEFAULT_SINK@"]).to_lowercase().contains("yes");
            (volume, muted)
        }
        VolumeBackend::None => (None, false),
    }
}

fn backlight_current() -> Option<u8> {
    capture("brightnessctl", &["-c", "backlight", "-m"]).lines().find_map(|line| line.split(',').nth(3)?.trim().strip_suffix('%')?.parse().ok())
}

fn capture_sh(command: &str) -> String {
    Command::new("sh").args(["-c", command]).output().ok().map(|output| String::from_utf8_lossy(&output.stdout).into_owned()).unwrap_or_default()
}

fn ddc_bus_with_timeout(seconds: u8) -> Option<u32> {
    let output = capture_sh(&format!("timeout {seconds} ddcutil detect --terse 2>/dev/null"));
    output.split("/dev/i2c-").skip(1).find_map(|part| part.chars().take_while(|c| c.is_ascii_digit()).collect::<String>().parse().ok())
}

fn ddc_current(bus: u32, timeout: u8) -> Option<u8> {
    let output = capture_sh(&format!("timeout {timeout} ddcutil --bus {bus} getvcp 10 --terse 2>/dev/null"));
    let values: Vec<u16> = output.split_whitespace().filter_map(|word| word.parse().ok()).collect();
    let (current, maximum) = (*values.get(values.len().checked_sub(2)?)?, *values.last()?);
    (maximum > 0).then(|| ((u32::from(current) * 100) / u32::from(maximum)).min(100) as u8)
}

fn set_volume(backend: VolumeBackend, value: u64) -> HandleResult {
    match backend {
        VolumeBackend::Wpctl => spawn_detached("wpctl", &["set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", &format!("{value}%")]),
        VolumeBackend::Pactl => spawn_detached("pactl", &["set-sink-volume", "@DEFAULT_SINK@", &format!("{value}%")]),
        VolumeBackend::None => HandleResult::Close,
    }
}

fn relative_volume(backend: VolumeBackend, value: u64, plus: bool) -> HandleResult {
    let amount = format!("{value}%{}", if plus { "+" } else { "-" });
    match backend {
        VolumeBackend::Wpctl => spawn_detached("wpctl", &["set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", &amount]),
        VolumeBackend::Pactl => spawn_detached("pactl", &["set-sink-volume", "@DEFAULT_SINK@", &amount]),
        VolumeBackend::None => HandleResult::Close,
    }
}

fn mute_volume(backend: VolumeBackend) -> HandleResult {
    match backend {
        VolumeBackend::Wpctl => spawn_detached("wpctl", &["set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"]),
        VolumeBackend::Pactl => spawn_detached("pactl", &["set-sink-mute", "@DEFAULT_SINK@", "toggle"]),
        VolumeBackend::None => HandleResult::Close,
    }
}

fn set_brightness(backend: BrightnessBackend, value: u64) -> HandleResult {
    match backend {
        BrightnessBackend::Backlight => spawn_detached("brightnessctl", &["-c", "backlight", "set", &format!("{value}%")]),
        BrightnessBackend::Ddc { bus } => ddc_set(bus, value),
        BrightnessBackend::None => HandleResult::Close,
    }
}

fn relative_brightness(backend: BrightnessBackend, value: u64, plus: bool) -> HandleResult {
    match backend {
        BrightnessBackend::Backlight => spawn_detached("brightnessctl", &["-c", "backlight", "set", &format!("{value}%{}", if plus { "+" } else { "-" })]),
        BrightnessBackend::Ddc { bus } => {
            let bus = bus.or_else(|| ddc_bus_with_timeout(3));
            let Some(bus) = bus else { return HandleResult::Close; };
            let Some(current) = ddc_current(bus, 3) else { return HandleResult::Close; };
            ddc_set(Some(bus), if plus { u64::from(current).saturating_add(value).min(100) } else { u64::from(current).saturating_sub(value) })
        }
        BrightnessBackend::None => HandleResult::Close,
    }
}

fn ddc_set(bus: Option<u32>, value: u64) -> HandleResult {
    if let Some(bus) = bus {
        return spawn_shell(&format!("timeout 3 ddcutil --bus {bus} setvcp 10 {value} >/dev/null 2>&1"));
    }
    // A lazy bus probe keeps exact brightness controls available after a slow init probe.
    spawn_shell(&format!("bus=$(timeout 3 ddcutil detect --terse 2>/dev/null | sed -n 's#.*\\/dev\\/i2c-\\([0-9][0-9]*\\).*#\\1#p' | head -n1); [ -n \"$bus\" ] && timeout 3 ddcutil --bus \"$bus\" setvcp 10 {value} >/dev/null 2>&1"))
}
