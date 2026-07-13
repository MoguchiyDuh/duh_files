#!/usr/bin/env bash
# Clipboard history: wl-paste watchers pipe through `store` so the waybar
# pill count updates instantly (signal-driven), no polling interval needed.

set -uo pipefail

refresh_waybar() {
    pkill -RTMIN+2 waybar 2>/dev/null || true
}

case "$1" in
    store)
        cliphist store
        refresh_waybar
        ;;
    wipe)
        cliphist wipe
        notify-send "Clipboard history wiped."
        refresh_waybar
        ;;
    *)
        printf 'Usage: %s <store|wipe>\n' "$0" >&2
        exit 1
        ;;
esac
