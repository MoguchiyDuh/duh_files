use crate::emit;
use crate::sysfs::cache_dir;
use std::collections::HashMap;
use std::fs;
use std::thread;
use std::time::{Duration, Instant};

const GIB: f64 = 1024.0 * 1024.0 * 1024.0;

pub fn run(interval: Duration) -> ! {
    // DIMM title comes from a cache file populated by setup-hardware.sh, which
    // reads it once via `sudo dmidecode` at install time. The daemon itself
    // never touches dmidecode (no runtime sudo).
    let title = read_title();

    loop {
        let tick_start = Instant::now();

        if let Some(snapshot) = read_meminfo() {
            let fields = [
                (
                    "In use",
                    format!(
                        "{:.1}/{:.1} GiB ({}%)",
                        snapshot.used as f64 / GIB,
                        snapshot.total as f64 / GIB,
                        snapshot.percentage
                    ),
                ),
                (
                    "Free",
                    format!("{:.1} GiB", snapshot.available as f64 / GIB),
                ),
                (
                    "Swap",
                    format!(
                        "{:.1}/{:.1} GiB",
                        snapshot.swap_used as f64 / GIB,
                        snapshot.swap_total as f64 / GIB
                    ),
                ),
            ];
            let classes: &[&str] = if snapshot.percentage >= 90 {
                &["high"]
            } else {
                &[]
            };
            emit::emit(
                &format!("\u{efc5} {}%", snapshot.percentage),
                &title,
                &fields,
                "LMB  btop",
                classes,
            );
        }

        sleep_remainder(tick_start, interval);
    }
}

fn read_title() -> String {
    return crate::sysfs::read_trimmed(cache_dir().join("waybar/memory-title"))
        .unwrap_or_else(|| "Memory".to_string());
}

struct Snapshot {
    used: u64,
    total: u64,
    available: u64,
    swap_used: u64,
    swap_total: u64,
    percentage: u32,
}

fn read_meminfo() -> Option<Snapshot> {
    let text = fs::read_to_string("/proc/meminfo").ok()?;
    let mut values: HashMap<&str, u64> = HashMap::new();

    for line in text.lines() {
        let Some((key, rest)) = line.split_once(':') else {
            continue;
        };
        let Some(first) = rest.split_whitespace().next() else {
            continue;
        };
        let Ok(kib) = first.parse::<u64>() else {
            continue;
        };
        values.insert(key, kib * 1024);
    }

    let total = *values.get("MemTotal")?;
    let available = *values.get("MemAvailable")?;
    let used = total.saturating_sub(available);
    let percentage = if total > 0 {
        (used * 100 / total) as u32
    } else {
        0
    };
    let swap_total = values.get("SwapTotal").copied().unwrap_or(0);
    let swap_used = swap_total.saturating_sub(values.get("SwapFree").copied().unwrap_or(0));

    return Some(Snapshot {
        used,
        total,
        available,
        swap_used,
        swap_total,
        percentage,
    });
}

fn sleep_remainder(tick_start: Instant, interval: Duration) {
    let elapsed = tick_start.elapsed();
    if elapsed < interval {
        thread::sleep(interval - elapsed);
    }
}
