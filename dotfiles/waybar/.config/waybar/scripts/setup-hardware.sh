#!/usr/bin/env bash
# One-time (install-time) setup for waybar hardware modules.
#   - Caches the DIMM part-number title via `sudo dmidecode` (a runtime
#     daemon has no business holding root; this runs once and caches to disk).
#   - hardwarebar itself handles RAPL capability grants via its own build.sh.

set -euo pipefail

cache_dir=${XDG_CACHE_HOME:-$HOME/.cache}/waybar

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
