#!/usr/bin/env bash
# Progressive idle dim / restore for hypridle.
#
# Dims only via HARDWARE methods that actually reduce backlight power draw:
#   1. sysfs backlight (/sys/class/backlight/*) via brightnessctl  -- laptop panels
#   2. DDC/CI (ddcutil) for external monitors that support it       -- real backlight
# If neither is available (e.g. a desktop monitor with no software backlight and
# no DDC/CI), display dimming is SKIPPED. Software gamma dimming is intentionally
# not used because it does not save any power (the backlight stays at full).
#
# Peripheral LEDs (keyboard lock LEDs, NIC LEDs) are dimmed as a cosmetic idle
# cue regardless of display support.
#
# On battery the dim level is more aggressive than on AC, mirroring Windows/macOS.
#
# Usage: idle-dim.sh {dim|restore}
#
# Safe to call when tools are missing: it degrades gracefully and can never
# wedge hypridle.

set -uo pipefail

DDC_BRIGHTNESS_VCP="10"                 # standard VCP feature code for brightness
STATE_DIR="${XDG_RUNTIME_DIR:-/tmp}/idle-dim"
LED_STATE="$STATE_DIR/leds"
BL_STATE="$STATE_DIR/backlight"
DDC_STATE="$STATE_DIR/ddc"

mkdir -p "$STATE_DIR"

has() { command -v "$1" >/dev/null 2>&1; }

# --- power source -> dim level -------------------------------------------
# Returns the dim percentage for the current power state.
dim_level() {
    local online=1
    if [[ -d /sys/class/power_supply/BAT0 || -d /sys/class/power_supply/BAT1 ]]; then
        online=$(cat /sys/class/power_supply/AC*/online 2>/dev/null | head -n1 || echo 1)
    fi
    if [[ "$online" == "0" ]]; then
        printf '5'      # on battery: aggressive
    else
        printf '30'     # on AC: gentle
    fi
}

# --- tier 1: sysfs backlight (laptop internal panel) ----------------------
backlight_available() {
    has brightnessctl && ls /sys/class/backlight/*/brightness >/dev/null 2>&1
}

backlight_dim() {
    brightnessctl -s >/dev/null 2>&1 || true          # save current
    brightnessctl set "$(dim_level)%" >/dev/null 2>&1 || true
    : > "$BL_STATE"
}

backlight_restore() {
    [[ -f "$BL_STATE" ]] || return 0
    brightnessctl -r >/dev/null 2>&1 || true
    rm -f "$BL_STATE"
}

# --- tier 2: DDC/CI external monitor (real hardware backlight) -------------
# A full `ddcutil detect` scan is slow (~400 ms), so the I2C bus is detected
# once and cached; every subsequent call targets it with --bus (~175 ms) and
# falls back to a fresh detect only if the cached bus stops responding.
DDC_BUS_CACHE="$STATE_DIR/ddc-bus"

ddc_detect_bus() {
    ddcutil detect --terse 2>/dev/null \
        | grep -oP '/dev/i2c-\K[0-9]+' | head -n1
}

ddc_bus() {
    local bus
    if [[ -f "$DDC_BUS_CACHE" ]]; then
        bus=$(cat "$DDC_BUS_CACHE" 2>/dev/null)
        # cheap liveness probe on the cached bus
        if [[ -n "$bus" ]] && ddcutil --bus "$bus" getvcp "$DDC_BRIGHTNESS_VCP" --terse >/dev/null 2>&1; then
            printf '%s' "$bus"
            return 0
        fi
    fi
    bus=$(ddc_detect_bus)
    [[ -n "$bus" ]] || return 1
    printf '%s' "$bus" | tee "$DDC_BUS_CACHE"
}

ddc_available() {
    has ddcutil || return 1
    [[ -n "$(ddc_bus)" ]]
}

ddc_dim() {
    local bus cur
    bus=$(ddc_bus) || return 0
    cur=$(ddcutil --bus "$bus" getvcp "$DDC_BRIGHTNESS_VCP" --terse 2>/dev/null | awk '{print $4}')
    [[ -n "$cur" ]] && printf '%s\n' "$cur" > "$DDC_STATE"
    ddcutil --bus "$bus" setvcp "$DDC_BRIGHTNESS_VCP" "$(dim_level)" >/dev/null 2>&1 || true
}

ddc_restore() {
    [[ -f "$DDC_STATE" ]] || return 0
    local bus prev
    prev=$(cat "$DDC_STATE" 2>/dev/null)
    bus=$(cat "$DDC_BUS_CACHE" 2>/dev/null)
    [[ -n "$prev" && -n "$bus" ]] && ddcutil --bus "$bus" setvcp "$DDC_BRIGHTNESS_VCP" "$prev" >/dev/null 2>&1 || true
    rm -f "$DDC_STATE"
}

# --- display dim dispatch: best available hardware method, else skip ------
display_dim() {
    if backlight_available; then
        backlight_dim
    elif ddc_available; then
        ddc_dim
    fi
    # else: no hardware dimming available -> skip silently
}

display_restore() {
    backlight_restore
    ddc_restore
}

# --- peripheral LEDs (cosmetic) ------------------------------------------
leds_dim() {
    has brightnessctl || return 0
    : > "$LED_STATE"
    brightnessctl -l 2>/dev/null | grep -oP "Device '\K[^']+' of class 'leds" \
        | sed "s/' of class 'leds//" | while read -r dev; do
        local cur
        cur=$(brightnessctl -d "$dev" get 2>/dev/null) || continue
        printf '%s=%s\n' "$dev" "$cur" >> "$LED_STATE"
        brightnessctl -d "$dev" set 0 >/dev/null 2>&1 || true
    done
}

leds_restore() {
    has brightnessctl || return 0
    [[ -f "$LED_STATE" ]] || return 0
    while IFS='=' read -r dev val; do
        [[ -n "$dev" ]] || continue
        brightnessctl -d "$dev" set "$val" >/dev/null 2>&1 || true
    done < "$LED_STATE"
    rm -f "$LED_STATE"
}

case "${1:-}" in
    dim)
        display_dim
        leds_dim
        ;;
    restore)
        display_restore
        leds_restore
        ;;
    *)
        printf 'Usage: %s {dim|restore}\n' "$0" >&2
        exit 2
        ;;
esac
