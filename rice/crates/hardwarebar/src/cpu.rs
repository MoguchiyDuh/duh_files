use crate::emit;
use crate::sysfs::read_u64;
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::thread;
use std::time::{Duration, Instant};

enum PowerSource {
    Rapl {
        energy_path: PathBuf,
        max_range_uj: u64,
    },
    Hwmon {
        path: PathBuf,
    },
    None,
}

/// Facts that never change for the lifetime of the daemon: resolved once at
/// startup so the hot loop never re-globs /sys/class/hwmon or /proc/cpuinfo.
struct Static {
    model: String,
    physical_cores: u32,
    threads: u32,
    temp_path: Option<PathBuf>,
    power_source: PowerSource,
}

pub fn run(interval: Duration) -> ! {
    let facts = Static::detect();

    // One blocking bootstrap sample pays the 150ms cost exactly once, ever.
    // Every subsequent tick diffs against the previous loop iteration instead.
    let mut prev_stat = read_stat();
    let mut prev_energy = match &facts.power_source {
        PowerSource::Rapl { energy_path, .. } => {
            read_u64(energy_path).map(|value| (value, Instant::now()))
        }
        _ => None,
    };
    thread::sleep(Duration::from_millis(150));

    loop {
        let tick_start = Instant::now();

        let stat = read_stat();
        let usage = usage_percent(prev_stat, stat);
        prev_stat = stat;

        let speed = read_speed();
        let temperature = facts.temp_path.as_deref().and_then(read_temperature);
        let power = sample_power(&facts.power_source, &mut prev_energy);
        let uptime = read_uptime();
        let procs = count_processes();

        let mut fields: Vec<(&str, String)> = vec![("Utilization", format!("{usage}%"))];
        if let Some((current, max)) = speed {
            fields.push(("Speed", format!("{current:.1}/{max:.1} GHz")));
        }
        if let Some(celsius) = temperature {
            fields.push(("Temp", format!("{celsius:.0}\u{b0}C")));
        }
        if let Some(watts) = power {
            fields.push(("Power", format!("{watts:.0} W")));
        }
        fields.push((
            "Cores",
            format!("{}/{}", facts.physical_cores, facts.threads),
        ));
        fields.push(("Procs", procs.to_string()));
        fields.push(("Up", format_duration(uptime)));

        let classes: &[&str] = if usage >= 90 { &["high"] } else { &[] };
        emit::emit(
            &format!("\u{f2db} {usage}%"),
            &facts.model,
            &fields,
            "LMB  btop",
            classes,
        );

        sleep_remainder(tick_start, interval);
    }
}

impl Static {
    fn detect() -> Self {
        let (model, physical_cores, threads) = read_topology();
        return Static {
            model,
            physical_cores,
            threads,
            temp_path: detect_temp_path(),
            power_source: detect_power_source(),
        };
    }
}

fn read_topology() -> (String, u32, u32) {
    let text = fs::read_to_string("/proc/cpuinfo").unwrap_or_default();
    let mut model = String::from("CPU");
    let mut cores_by_socket: HashMap<u32, u32> = HashMap::new();
    let mut current_socket: Option<u32> = None;
    let mut threads = 0u32;

    for line in text.lines() {
        let Some((key, value)) = line.split_once(':') else {
            continue;
        };
        let key = key.trim();
        let value = value.trim();
        match key {
            "processor" => threads += 1,
            "model name" if model == "CPU" => model = value.to_string(),
            "physical id" => current_socket = value.parse().ok(),
            "cpu cores" => {
                if let (Some(socket), Ok(cores)) = (current_socket, value.parse::<u32>()) {
                    cores_by_socket.insert(socket, cores);
                }
            }
            _ => {}
        }
    }

    let physical_cores = if cores_by_socket.is_empty() {
        threads
    } else {
        cores_by_socket.values().sum()
    };
    return (model, physical_cores, threads);
}

fn detect_temp_path() -> Option<PathBuf> {
    let mut preferred: Vec<PathBuf> = Vec::new();
    let mut fallback: Vec<PathBuf> = Vec::new();
    let entries = fs::read_dir("/sys/class/hwmon").ok()?;

    for entry in entries.flatten() {
        let dir = entry.path();
        let name = crate::sysfs::read_trimmed(dir.join("name")).unwrap_or_default();
        let Ok(files) = fs::read_dir(&dir) else {
            continue;
        };
        let temp_paths = files
            .flatten()
            .map(|file| file.path())
            .filter(|path| is_temp_input(path));
        if matches!(name.as_str(), "k10temp" | "coretemp" | "zenpower") {
            preferred.extend(temp_paths);
        } else {
            fallback.extend(temp_paths);
        }
    }

    return preferred
        .into_iter()
        .chain(fallback)
        .find(|path| read_temperature(path).is_some());
}

fn is_temp_input(path: &std::path::Path) -> bool {
    return path
        .file_name()
        .and_then(|name| name.to_str())
        .is_some_and(|name| name.starts_with("temp") && name.ends_with("_input"));
}

fn read_temperature(path: &std::path::Path) -> Option<f64> {
    let millidegrees = read_u64(path)? as f64;
    let celsius = millidegrees / 1000.0;
    if celsius > 0.0 && celsius < 130.0 {
        return Some(celsius);
    }
    return None;
}

fn detect_power_source() -> PowerSource {
    let energy_path = PathBuf::from("/sys/class/powercap/intel-rapl:0/energy_uj");
    if read_u64(&energy_path).is_some() {
        let max_range_uj =
            read_u64("/sys/class/powercap/intel-rapl:0/max_energy_range_uj").unwrap_or(u64::MAX);
        return PowerSource::Rapl {
            energy_path,
            max_range_uj,
        };
    }

    if let Ok(entries) = fs::read_dir("/sys/class/hwmon") {
        for entry in entries.flatten() {
            let dir = entry.path();
            let name = crate::sysfs::read_trimmed(dir.join("name")).unwrap_or_default();
            if !matches!(
                name.as_str(),
                "zenpower" | "zenpower3" | "zenpower5" | "k10temp" | "coretemp"
            ) {
                continue;
            }
            for candidate in ["power1_average", "power1_input"] {
                let path = dir.join(candidate);
                if read_u64(&path).is_some() {
                    return PowerSource::Hwmon { path };
                }
            }
        }
    }

    return PowerSource::None;
}

fn sample_power(source: &PowerSource, prev: &mut Option<(u64, Instant)>) -> Option<f64> {
    match source {
        PowerSource::Rapl {
            energy_path,
            max_range_uj,
        } => {
            let now = Instant::now();
            let current = read_u64(energy_path)?;
            let watts = prev.and_then(|(prev_value, prev_time)| {
                let elapsed = now.duration_since(prev_time).as_secs_f64();
                if elapsed <= 0.0 {
                    return None;
                }
                let delta = if current >= prev_value {
                    current - prev_value
                } else {
                    (max_range_uj - prev_value) + current
                };
                return Some(delta as f64 / elapsed / 1_000_000.0);
            });
            *prev = Some((current, now));
            return watts;
        }
        PowerSource::Hwmon { path } => {
            return read_u64(path).map(|value| value as f64 / 1_000_000.0);
        }
        PowerSource::None => return None,
    }
}

fn read_stat() -> (u64, u64) {
    let text = fs::read_to_string("/proc/stat").unwrap_or_default();
    let first_line = text.lines().next().unwrap_or_default();
    let values: Vec<u64> = first_line
        .split_whitespace()
        .skip(1)
        .filter_map(|value| value.parse().ok())
        .collect();
    let total: u64 = values.iter().sum();
    let idle = values.get(3).copied().unwrap_or(0) + values.get(4).copied().unwrap_or(0);
    return (total, idle);
}

fn usage_percent(prev: (u64, u64), current: (u64, u64)) -> u32 {
    let total_delta = current.0.saturating_sub(prev.0);
    let idle_delta = current.1.saturating_sub(prev.1);
    if total_delta == 0 {
        return 0;
    }
    return (100 * total_delta.saturating_sub(idle_delta) / total_delta) as u32;
}

/// Live (current, max) speed pair in GHz. Both come from cpufreq every tick,
/// deliberately not cached: scaling_max_freq changes with the active power
/// profile (e.g. eco caps it to the base clock), so a cached value would lie.
fn read_speed() -> Option<(f64, f64)> {
    let entries = fs::read_dir("/sys/devices/system/cpu").ok()?;
    let mut currents: Vec<f64> = Vec::new();
    let mut max_khz: u64 = 0;

    for entry in entries.flatten() {
        let name = entry.file_name();
        let name = name.to_string_lossy();
        if !name.starts_with("cpu")
            || !name[3..]
                .chars()
                .all(|character| character.is_ascii_digit())
        {
            continue;
        }
        let cpufreq = entry.path().join("cpufreq");
        if let Some(current) = read_u64(cpufreq.join("scaling_cur_freq")) {
            currents.push(current as f64);
        }
        if let Some(max) = read_u64(cpufreq.join("scaling_max_freq")) {
            max_khz = max_khz.max(max);
        }
    }

    if currents.is_empty() {
        return None;
    }
    let avg_khz = currents.iter().sum::<f64>() / currents.len() as f64;
    return Some((avg_khz / 1_000_000.0, max_khz as f64 / 1_000_000.0));
}

fn read_uptime() -> u64 {
    return fs::read_to_string("/proc/uptime")
        .ok()
        .and_then(|text| {
            text.split_whitespace()
                .next()
                .and_then(|value| value.parse::<f64>().ok())
        })
        .map(|value| value as u64)
        .unwrap_or(0);
}

fn count_processes() -> usize {
    return fs::read_dir("/proc")
        .map(|entries| {
            entries
                .flatten()
                .filter(|entry| {
                    entry
                        .file_name()
                        .to_string_lossy()
                        .bytes()
                        .all(|byte| byte.is_ascii_digit())
                })
                .count()
        })
        .unwrap_or(0);
}

fn format_duration(seconds: u64) -> String {
    let days = seconds / 86400;
    let hours = (seconds % 86400) / 3600;
    let minutes = (seconds % 3600) / 60;
    if days > 0 {
        return format!("{days}d {hours}h");
    }
    return format!("{hours}h {minutes}m");
}

fn sleep_remainder(tick_start: Instant, interval: Duration) {
    let elapsed = tick_start.elapsed();
    if elapsed < interval {
        thread::sleep(interval - elapsed);
    }
}
