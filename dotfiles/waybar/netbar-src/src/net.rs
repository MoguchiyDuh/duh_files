use serde_json::Value;
use std::collections::HashMap;
use std::env;
use std::fs;
use std::process::Command;
use std::time::{Duration, Instant};

use crate::emit;

const INTERVAL: Duration = Duration::from_secs(5);

pub fn run() -> ! {
    let mut previous: HashMap<String, (u64, u64)> = HashMap::new();
    let mut last = Instant::now();

    loop {
        let tick_start = Instant::now();
        let elapsed = tick_start.duration_since(last).as_secs_f64().max(0.001);
        previous = tick(&previous, elapsed);
        last = tick_start;

        let spent = tick_start.elapsed();
        if spent < INTERVAL {
            std::thread::sleep(INTERVAL - spent);
        }
    }
}

struct Active {
    name: String,
    address: String,
    down_bps: f64,
    up_bps: f64,
    device_type: String,
    connection: String,
}

fn tick(previous: &HashMap<String, (u64, u64)>, elapsed: f64) -> HashMap<String, (u64, u64)> {
    let mut current: HashMap<String, (u64, u64)> = HashMap::new();
    let device_info = nmcli_devices();
    let mut active: Vec<Active> = Vec::new();

    for iface in ip_addresses() {
        let Some(name) = iface.get("ifname").and_then(Value::as_str) else {
            continue;
        };
        let address = ipv4_of(&iface);
        let (device_type, connection) = device_info
            .get(name)
            .cloned()
            .unwrap_or_else(|| ("".to_string(), name.to_string()));
        if matches!(device_type.as_str(), "loopback" | "bridge" | "wifi-p2p") || address.is_empty()
        {
            continue;
        }
        let Some(stats) = counters(name) else {
            continue;
        };
        current.insert(name.to_string(), stats);
        let old = previous.get(name).copied().unwrap_or(stats);
        let down_bps = (stats.0.saturating_sub(old.0) as f64 * 8.0) / elapsed / 1_000_000.0;
        let up_bps = (stats.1.saturating_sub(old.1) as f64 * 8.0) / elapsed / 1_000_000.0;
        active.push(Active {
            name: name.to_string(),
            address,
            down_bps,
            up_bps,
            device_type,
            connection,
        });
    }

    let default_name = default_interface();
    let primary_idx = active.iter().position(|item| item.name == default_name);

    render(primary_idx.map(|i| &active[i]), &active, primary_idx);

    return current;
}

fn render(primary: Option<&Active>, active: &[Active], primary_idx: Option<usize>) {
    let (icon, title, mut fields): (char, String, Vec<(String, String)>) = match primary {
        Some(p) if p.device_type == "wifi" => {
            let (ssid, strength, dbm, freq) = wireless_info(&p.name, &p.connection);
            let icons = [
                '\u{f092f}',
                '\u{f091f}',
                '\u{f0922}',
                '\u{f0925}',
                '\u{f0928}',
            ];
            let icon = icons[(strength as usize * (icons.len() - 1) / 100).min(icons.len() - 1)];
            let mut fields = vec![("Signal".to_string(), format!("{strength}% ({dbm} dBm)"))];
            if freq > 0 {
                let band = if freq >= 5925 {
                    "6 GHz"
                } else if freq >= 5000 {
                    "5 GHz"
                } else {
                    "2.4 GHz"
                };
                fields.push(("Band".to_string(), band.to_string()));
            }
            (icon, ssid, fields)
        }
        Some(p) => ('\u{f0200}', kind(&p.device_type), Vec::new()),
        None => ('\u{f092d}', "Network disconnected".to_string(), Vec::new()),
    };

    if let Some(p) = primary {
        fields.push(("Address".to_string(), p.address.clone()));
        fields.push(("Interface".to_string(), p.name.clone()));
        fields.push(("MAC".to_string(), mac_address(&p.name)));
        fields.push((
            "Traffic".to_string(),
            format!("\u{2193}{} \u{2191}{}", rate(p.down_bps), rate(p.up_bps)),
        ));
    }

    let mut extra: Vec<String> = Vec::new();
    for (idx, item) in active.iter().enumerate() {
        if Some(idx) == primary_idx {
            continue;
        }
        let identity = if item.connection != item.name {
            format!("{}  {}", item.connection, item.name)
        } else {
            item.name.clone()
        };
        extra.push(format!(
            "{}  {}  {}  \u{2193}{} \u{2191}{}",
            kind(&item.device_type),
            identity,
            item.address,
            rate(item.down_bps),
            rate(item.up_bps)
        ));
    }
    if let Some(proxy) = proxy_status() {
        extra.push(proxy);
    }

    let classes: &[&str] = if primary.is_some() {
        &[]
    } else {
        &["disconnected"]
    };
    let text = format!("{icon}");
    emit::emit(&text, &title, &fields, &extra, "LMB  Connections", classes);
}

fn rate(mbps: f64) -> String {
    return if mbps >= 0.01 {
        format!("{mbps:.2} Mbps")
    } else {
        "0 Mbps".to_string()
    };
}

fn kind(device_type: &str) -> String {
    return match device_type {
        "wifi" => "Wi-Fi".to_string(),
        "ethernet" => "Ethernet".to_string(),
        "wireguard" => "WireGuard".to_string(),
        "tun" | "ip-tunnel" => "Tunnel".to_string(),
        "vpn" => "VPN".to_string(),
        other if !other.is_empty() => title_case(&other.replace('-', " ")),
        _ => "Adapter".to_string(),
    };
}

fn title_case(text: &str) -> String {
    return text
        .split_whitespace()
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
                None => String::new(),
            }
        })
        .collect::<Vec<_>>()
        .join(" ");
}

fn command(program: &str, args: &[&str]) -> String {
    let output = Command::new(program).args(args).output();
    return match output {
        Ok(out) if out.status.success() => String::from_utf8_lossy(&out.stdout).trim().to_string(),
        _ => String::new(),
    };
}

fn ip_addresses() -> Vec<Value> {
    let output = command("ip", &["-j", "address", "show"]);
    if output.is_empty() {
        return Vec::new();
    }
    return serde_json::from_str(&output).unwrap_or_default();
}

fn ipv4_of(iface: &Value) -> String {
    let Some(addr_info) = iface.get("addr_info").and_then(Value::as_array) else {
        return String::new();
    };
    for addr in addr_info {
        let family = addr.get("family").and_then(Value::as_str);
        let scope = addr.get("scope").and_then(Value::as_str);
        if family == Some("inet") && scope == Some("global") {
            if let Some(local) = addr.get("local").and_then(Value::as_str) {
                return local.to_string();
            }
        }
    }
    return String::new();
}

fn default_interface() -> String {
    let output = command("ip", &["-j", "route", "show", "default"]);
    if output.is_empty() {
        return String::new();
    }
    let routes: Vec<Value> = serde_json::from_str(&output).unwrap_or_default();
    return routes
        .first()
        .and_then(|route| route.get("dev"))
        .and_then(Value::as_str)
        .unwrap_or("")
        .to_string();
}

fn nmcli_devices() -> HashMap<String, (String, String)> {
    let output = command(
        "nmcli",
        &[
            "-t",
            "--escape",
            "no",
            "-f",
            "DEVICE,TYPE,STATE,CONNECTION",
            "device",
            "status",
        ],
    );
    let mut result = HashMap::new();
    for line in output.lines() {
        let fields: Vec<&str> = line.splitn(4, ':').collect();
        if fields.len() == 4 {
            result.insert(
                fields[0].to_string(),
                (fields[1].to_string(), fields[3].to_string()),
            );
        }
    }
    return result;
}

fn counters(name: &str) -> Option<(u64, u64)> {
    let base = format!("/sys/class/net/{name}/statistics");
    let rx = fs::read_to_string(format!("{base}/rx_bytes"))
        .ok()?
        .trim()
        .parse()
        .ok()?;
    let tx = fs::read_to_string(format!("{base}/tx_bytes"))
        .ok()?
        .trim()
        .parse()
        .ok()?;
    return Some((rx, tx));
}

fn mac_address(name: &str) -> String {
    return fs::read_to_string(format!("/sys/class/net/{name}/address"))
        .map(|s| s.trim().to_uppercase())
        .unwrap_or_else(|_| "Unknown".to_string());
}

/// Returns (ssid, strength 0-100, dBm, frequency MHz).
fn wireless_info(name: &str, connection: &str) -> (String, u32, i32, u32) {
    let mut frequency = 0u32;
    let output = command(
        "nmcli",
        &[
            "-t",
            "--escape",
            "no",
            "-f",
            "IN-USE,SIGNAL,FREQ",
            "device",
            "wifi",
            "list",
            "ifname",
            name,
        ],
    );
    for line in output.lines() {
        if !line.starts_with("*:") {
            continue;
        }
        let fields: Vec<&str> = line.split(':').collect();
        if fields.len() >= 3 {
            frequency = fields[2]
                .split_whitespace()
                .next()
                .and_then(|s| s.parse().ok())
                .unwrap_or(0);
        }
        break;
    }

    let Ok(wireless) = fs::read_to_string("/proc/net/wireless") else {
        return (connection.to_string(), 0, 0, frequency);
    };
    let Some(line) = wireless
        .lines()
        .find(|line| line.trim_start().starts_with(&format!("{name}:")))
    else {
        return (connection.to_string(), 0, 0, frequency);
    };
    let cleaned = line.replace('.', "");
    let fields: Vec<&str> = cleaned.split_whitespace().collect();
    let Some(raw) = fields.get(3) else {
        return (connection.to_string(), 0, 0, frequency);
    };
    let Ok(dbm) = raw.parse::<i32>() else {
        return (connection.to_string(), 0, 0, frequency);
    };
    let strength = (2 * (dbm + 100)).clamp(0, 100) as u32;
    return (connection.to_string(), strength, dbm, frequency);
}

fn proxy_status() -> Option<String> {
    for var in [
        "ALL_PROXY",
        "HTTPS_PROXY",
        "HTTP_PROXY",
        "all_proxy",
        "https_proxy",
        "http_proxy",
    ] {
        if let Ok(value) = env::var(var) {
            if !value.is_empty() {
                return Some(format!("Proxy  {var}={value}"));
            }
        }
    }
    let mode = command("gsettings", &["get", "org.gnome.system.proxy", "mode"]);
    if mode.trim_matches('\'') != "manual" {
        return None;
    }
    let mut endpoints: Vec<String> = Vec::new();
    for protocol in ["http", "https", "socks"] {
        let host = command(
            "gsettings",
            &["get", &format!("org.gnome.system.proxy.{protocol}"), "host"],
        )
        .trim_matches('\'')
        .to_string();
        let port = command(
            "gsettings",
            &["get", &format!("org.gnome.system.proxy.{protocol}"), "port"],
        );
        if !host.is_empty() && host != "''" && !port.is_empty() && port != "0" {
            let endpoint = format!("{host}:{port}");
            if !endpoints.contains(&endpoint) {
                endpoints.push(endpoint);
            }
        }
    }
    return if endpoints.is_empty() {
        Some("System proxy".to_string())
    } else {
        Some(format!("System proxy  {}", endpoints.join(" \u{b7} ")))
    };
}
