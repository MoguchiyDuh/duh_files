#!/usr/bin/env bash
# Optional privileged setup for Waybar hardware modules.
# Grants hardwarebar access to a root-only RAPL counter and caches the DIMM
# identity so runtime processes never need elevated privileges.

set -euo pipefail

cache_dir=${XDG_CACHE_HOME:-$HOME/.cache}/waybar
hardwarebar=$HOME/.local/bin/hardwarebar
rapl=/sys/class/powercap/intel-rapl:0/energy_uj

if [[ -e "$rapl" && ! -r "$rapl" ]]; then
    [[ -x "$hardwarebar" ]] || {
        printf 'missing executable: %s\n' "$hardwarebar" >&2
        exit 1
    }
    sudo setcap cap_dac_read_search=ep "$hardwarebar"
    printf 'Enabled RAPL power reads for %s\n' "$hardwarebar"
fi

memory_title=$(sudo dmidecode --type 17 | awk '
    BEGIN { RS = ""; FS = "\n" }
    /Memory Device/ && $0 !~ /Size: No Module Installed/ {
        manufacturer = ""
        part = ""
        for (i = 1; i <= NF; i++) {
            if ($i ~ /^[[:space:]]*Manufacturer:/) {
                sub(/^[[:space:]]*Manufacturer:[[:space:]]*/, "", $i)
                manufacturer = $i
            }
            if ($i ~ /^[[:space:]]*Part Number:/) {
                sub(/^[[:space:]]*Part Number:[[:space:]]*/, "", $i)
                sub(/[[:space:]]+$/, "", $i)
                part = $i
            }
        }
        if (manufacturer != "" && part != "") {
            print manufacturer " " part
            exit
        }
    }
')

mkdir -p "$cache_dir"
printf '%s\n' "${memory_title:-Memory}" >"$cache_dir/memory-title"
printf 'Memory: %s\n' "${memory_title:-Memory}"
