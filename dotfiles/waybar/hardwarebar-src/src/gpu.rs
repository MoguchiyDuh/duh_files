use crate::emit;
use crate::sysfs::{read_trimmed, read_u64};
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::thread;
use std::time::{Duration, Instant};

/// Vendor is resolved exactly once at startup and cached for the daemon's
/// lifetime: it cannot change at runtime, so re-probing nvidia-smi / hwmon
/// on every tick would be pure waste (subprocess spawn + sysfs globbing).
enum Backend {
    Nvidia,
    Amd { device: PathBuf, hwmon: PathBuf },
    None,
}

pub fn run(interval: Duration) -> ! {
    let backend = detect_backend();

    loop {
        let tick_start = Instant::now();
        match &backend {
            Backend::Nvidia => sample_nvidia(),
            Backend::Amd { device, hwmon } => sample_amd(device, hwmon),
            Backend::None => emit::hidden(),
        }
        sleep_remainder(tick_start, interval);
    }
}

fn detect_backend() -> Backend {
    let nvidia_ok = Command::new("nvidia-smi")
        .arg("--query-gpu=name")
        .arg("--format=csv,noheader")
        .output()
        .is_ok_and(|output| output.status.success());
    if nvidia_ok {
        return Backend::Nvidia;
    }

    if let Ok(entries) = fs::read_dir("/sys/class/hwmon") {
        for entry in entries.flatten() {
            let dir = entry.path();
            if read_trimmed(dir.join("name")).as_deref() != Some("amdgpu") {
                continue;
            }
            let device = dir.join("device");
            if device.is_dir() {
                return Backend::Amd { device, hwmon: dir };
            }
        }
    }

    return Backend::None;
}

fn sample_nvidia() {
    let query = "name,utilization.gpu,memory.used,memory.total,temperature.gpu,\
                  clocks.current.graphics,clocks.current.memory,power.draw,power.limit";
    let output = Command::new("nvidia-smi")
        .arg(format!("--query-gpu={query}"))
        .arg("--format=csv,noheader,nounits")
        .output();

    let Ok(output) = output else {
        return emit::hidden();
    };
    if !output.status.success() {
        return emit::hidden();
    }
    let text = String::from_utf8_lossy(&output.stdout);
    let Some(row) = text.lines().next() else {
        return emit::hidden();
    };
    let columns: Vec<&str> = row.split(", ").collect();
    if columns.len() != 9 {
        return emit::hidden();
    }

    let name = columns[0];
    let Ok(usage) = columns[1].trim().parse::<f64>() else {
        return emit::hidden();
    };
    let used = columns[2].trim().parse::<f64>().unwrap_or(0.0);
    let total = columns[3].trim().parse::<f64>().unwrap_or(0.0);
    let temperature = columns[4].trim().parse::<f64>().unwrap_or(0.0);
    let core_clock = columns[5].trim().parse::<f64>().unwrap_or(0.0);
    let memory_clock = columns[6].trim().parse::<f64>().unwrap_or(0.0);
    let power = columns[7].trim().parse::<f64>().unwrap_or(0.0);
    let power_limit = columns[8].trim().parse::<f64>().unwrap_or(0.0);
    let usage = usage.round() as u32;

    let fields = [
        ("Utilization", format!("{usage}%")),
        (
            "VRAM",
            format!("{:.1}/{:.1} GiB", used / 1024.0, total / 1024.0),
        ),
        ("Temp", format!("{temperature:.0}\u{b0}C")),
        ("Clocks", format!("{core_clock:.0}/{memory_clock:.0} MHz")),
        ("Power", format!("{power:.1}/{power_limit:.0} W")),
    ];
    let classes: &[&str] = if usage >= 90 { &["high"] } else { &[] };
    emit::emit(
        &format!("\u{f08ae} {usage}%"),
        name,
        &fields,
        "LMB  LACT",
        classes,
    );
}

fn sample_amd(device: &Path, hwmon: &Path) {
    let Some(usage) =
        read_trimmed(device.join("gpu_busy_percent")).and_then(|text| text.parse::<u32>().ok())
    else {
        return emit::hidden();
    };

    let mut fields: Vec<(&str, String)> = vec![("Utilization", format!("{usage}%"))];

    let used = read_u64(device.join("mem_info_vram_used"));
    let total = read_u64(device.join("mem_info_vram_total"));
    if let (Some(used), Some(total)) = (used, total) {
        fields.push((
            "VRAM",
            format!(
                "{:.1}/{:.1} GiB",
                used as f64 / 1024f64.powi(3),
                total as f64 / 1024f64.powi(3)
            ),
        ));
    }

    if let Some(millidegrees) = read_u64(hwmon.join("temp1_input")) {
        fields.push((
            "Temp",
            format!("{:.0}\u{b0}C", millidegrees as f64 / 1000.0),
        ));
    }

    let core_clock = parse_active_clock(&device.join("pp_dpm_sclk"));
    let memory_clock = parse_active_clock(&device.join("pp_dpm_mclk"));
    if let (Some(core), Some(memory)) = (core_clock, memory_clock) {
        fields.push(("Clocks", format!("{core:.0}/{memory:.0} MHz")));
    }

    if let Some(microwatts) = read_u64(hwmon.join("power1_average")) {
        fields.push(("Power", format!("{:.1} W", microwatts as f64 / 1_000_000.0)));
    }

    let name = read_trimmed(device.join("product_name")).unwrap_or_else(|| "AMD GPU".to_string());
    let classes: &[&str] = if usage >= 90 { &["high"] } else { &[] };
    emit::emit(
        &format!("\u{f08ae} {usage}%"),
        &name,
        &fields,
        "LMB  LACT",
        classes,
    );
}

/// AMD's pp_dpm_{sclk,mclk} list every available power state, one per line,
/// with the currently active one marked by a trailing '*' (e.g. "1: 1800Mhz *").
fn parse_active_clock(path: &Path) -> Option<f64> {
    let text = fs::read_to_string(path).ok()?;
    for line in text.lines() {
        if !line.trim_end().ends_with('*') {
            continue;
        }
        let mhz_field = line.split_whitespace().nth(1)?;
        let digits: String = mhz_field
            .chars()
            .take_while(|character| character.is_ascii_digit())
            .collect();
        return digits.parse().ok();
    }
    return None;
}

fn sleep_remainder(tick_start: Instant, interval: Duration) {
    let elapsed = tick_start.elapsed();
    if elapsed < interval {
        thread::sleep(interval - elapsed);
    }
}
