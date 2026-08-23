#!/usr/bin/env bash

set -euo pipefail

state_dir="${XDG_STATE_HOME:-$HOME/.local/state}/power"
state_file="$state_dir/states"
awake_unit="awake-inhibit.service"

refresh_waybar() {
    pkill -RTMIN+1 waybar 2>/dev/null || true
}

state() {
    awk -F= -v mode="$1" '$1 == mode { print $2; exit }' "$state_file" 2>/dev/null || true
}

enabled() {
    [[ "$(state "$1")" == "enabled" ]]
}

set_state() {
    local mode="$1"
    local value="$2"
    local temporary

    mkdir -p "$state_dir"
    temporary=$(mktemp "$state_dir/states.XXXXXX")

    for candidate in suspend hibernate; do
        if [[ "$candidate" == "$mode" ]]; then
            printf '%s=%s\n' "$candidate" "$value" >> "$temporary"
        elif enabled "$candidate"; then
            printf '%s=enabled\n' "$candidate" >> "$temporary"
        else
            printf '%s=disabled\n' "$candidate" >> "$temporary"
        fi
    done

    mv "$temporary" "$state_file"
}

failures=()

require() {
    local condition="$1"
    local message="$2"

    if ! eval "$condition"; then
        failures+=("$message")
    fi
}

check_suspend() {
    failures=()
    require "grep -qw mem /sys/power/state" "kernel does not expose suspend-to-RAM"
    if lsmod | grep -q '^nvidia '; then
        require "grep -q '^UseKernelSuspendNotifiers: 1' /proc/driver/nvidia/params" "nvidia kernel suspend notifiers are not enabled"
        local tmp_path
        tmp_path=$(awk -F'"' '/^TemporaryFilePath:/ { print $2; exit }' /proc/driver/nvidia/params 2>/dev/null)
        require "[[ -n '$tmp_path' && '$tmp_path' != '/tmp' ]]" "nvidia TemporaryFilePath is unset or tmpfs-backed /tmp"
    fi
}

check_hibernate() {
    local memory_bytes
    local disk_swap_bytes

    failures=()
    memory_bytes=$(awk '/MemTotal:/ { print $2 * 1024 }' /proc/meminfo)
    disk_swap_bytes=$(swapon --noheadings --bytes --show=NAME,TYPE,SIZE | awk '$1 !~ /^\/dev\/zram/ { total += $3 } END { print total + 0 }')

    require "grep -qw disk /sys/power/state" "kernel does not expose hibernation"
    require "grep -Eq '(^| )resume=' /proc/cmdline" "kernel command line has no resume= parameter"
    require "grep -Eq '\\bresume\\b' /etc/mkinitcpio.conf" "mkinitcpio has no resume hook"
    require "(( disk_swap_bytes >= memory_bytes ))" "disk-backed swap is smaller than RAM"

    if swapon --noheadings --show=TYPE | grep -qw file; then
        require "grep -Eq '(^| )resume_offset=' /proc/cmdline" "swapfile hibernation requires resume_offset="
    fi
}

show_failures() {
    local mode="$1"

    printf '%s cannot be enabled:\n' "$mode" >&2
    printf '  - %s\n' "${failures[@]}" >&2
    notify-send "${mode^} unavailable" "${failures[*]}" -u critical
}

confirm_test() {
    local mode="$1"
    local answer

    if [[ ! -t 0 ]]; then
        printf 'Run %s --enable %s from a terminal to approve the resume test.\n' "$0" "$mode" >&2
        exit 2
    fi

    read -r -p "Run a real $mode/resume test before enabling it? [y/N] " answer
    [[ "$answer" == "y" || "$answer" == "Y" ]]
}

enable_mode() {
    local mode="$1"

    "check_$mode"
    if (( ${#failures[@]} )); then
        show_failures "$mode"
        exit 1
    fi

    if ! confirm_test "$mode"; then
        printf 'No change made.\n'
        exit 0
    fi

    systemctl "$mode"
    set_state "$mode" enabled
    notify-send "${mode^} enabled" "Resume test completed successfully."
}

run_mode() {
    local mode="$1"

    if ! enabled "$mode"; then
        notify-send "${mode^} disabled" "Run power.sh --enable $mode from a terminal first." -u normal
        exit 1
    fi

    systemctl "$mode"
}

ppd_available() {
    command -v powerprofilesctl >/dev/null 2>&1
}

profile_to_ppd() {
    case "$1" in
        eco)         printf 'power-saver' ;;
        balanced)    printf 'balanced' ;;
        performance) printf 'performance' ;;
        *)           return 1 ;;
    esac
}

ppd_to_profile() {
    case "$1" in
        power-saver) printf 'eco' ;;
        balanced)    printf 'balanced' ;;
        performance) printf 'performance' ;;
        *)           printf '%s' "$1" ;;
    esac
}

profile() {
    if ! ppd_available; then
        printf 'power-profiles-daemon is not installed.\n' >&2
        notify-send "Power profiles unavailable" "Install power-profiles-daemon." -u normal 2>/dev/null || true
        exit 1
    fi

    local action="${1:-status}"
    local target current

    case "$action" in
        eco|balanced|performance)
            target=$(profile_to_ppd "$action")
            powerprofilesctl set "$target"
            notify-send "Power profile" "$action" -u low -t 2000 2>/dev/null || true
            refresh_waybar
            ;;
        status)
            printf '%s\n' "$(ppd_to_profile "$(powerprofilesctl get)")"
            ;;
        cycle)
            current=$(powerprofilesctl get)
            case "$current" in
                power-saver) target=balanced ;;
                balanced)    target=performance ;;
                performance) target=power-saver ;;
                *)           target=balanced ;;
            esac
            powerprofilesctl set "$target"
            notify-send "Power profile" "$(ppd_to_profile "$target")" -u low -t 2000 2>/dev/null || true
            refresh_waybar
            ;;
        *)
            printf 'Usage: %s profile {eco|balanced|performance|status|cycle}\n' "$0" >&2
            exit 2
            ;;
    esac
}

awake_enabled() {
    systemctl --user is-active --quiet "$awake_unit"
}

enable_awake() {
    if awake_enabled; then
        return
    fi

    systemd-run --user --quiet --collect --unit="${awake_unit%.service}" \
        systemd-inhibit --what=idle:sleep --mode=block \
        --who=awake \
        --why="Awake mode enabled" \
        sleep infinity
    refresh_waybar
}

disable_awake() {
    systemctl --user stop "$awake_unit" 2>/dev/null || true
    refresh_waybar
}

awake() {
    case "${1:-}" in
        enable)
            enable_awake
            ;;
        disable)
            disable_awake
            ;;
        toggle)
            if awake_enabled; then
                disable_awake
            else
                enable_awake
            fi
            ;;
        status)
            if awake_enabled; then
                printf 'enabled\n'
            else
                printf 'disabled\n'
            fi
            ;;
        *)
            printf 'Usage: %s awake {enable|disable|toggle|status}\n' "$0" >&2
            exit 2
            ;;
    esac
}

case "${1:-}" in
    1|lock)
        hyprlock
        ;;
    2|logout)
        uwsm stop
        ;;
    3|suspend)
        run_mode suspend
        ;;
    4|hibernate)
        run_mode hibernate
        ;;
    5|reboot)
        systemctl reboot
        ;;
    6|shutdown)
        systemctl poweroff
        ;;
    --enable)
        [[ "${2:-}" == "suspend" || "${2:-}" == "hibernate" ]] || exit 2
        enable_mode "$2"
        ;;
    --disable)
        [[ "${2:-}" == "suspend" || "${2:-}" == "hibernate" ]] || exit 2
        set_state "$2" disabled
        notify-send "${2^} disabled"
        ;;
    --status)
        suspend_state=$(state suspend)
        hibernate_state=$(state hibernate)
        printf 'suspend=%s\nhibernate=%s\n' "${suspend_state:-disabled}" "${hibernate_state:-disabled}"
        ;;
    awake)
        awake "${2:-}"
        ;;
    profile)
        profile "${2:-status}"
        ;;
    *)
        printf 'Usage: %s {lock|logout|suspend|hibernate|reboot|shutdown|--enable MODE|--disable MODE|--status|awake ACTION|profile ACTION}\n' "$0" >&2
        exit 2
        ;;
esac
