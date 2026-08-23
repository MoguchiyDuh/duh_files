#!/usr/bin/env bash
set -Eeuo pipefail

refresh_waybar() {
    pkill -RTMIN+1 waybar 2>/dev/null || true
}

awake_active() {
    systemctl --user is-active --quiet awake-inhibit.service
}

awake() {
    case "${1:-status}" in
        enable)
            awake_active || systemd-run --user --quiet --collect --unit=awake-inhibit \
                systemd-inhibit --what=idle:sleep --mode=block --who=awake --why=awake sleep infinity
            refresh_waybar
            ;;
        disable)
            systemctl --user stop awake-inhibit.service 2>/dev/null || true
            refresh_waybar
            ;;
        toggle)
            if awake_active; then awake disable; else awake enable; fi
            ;;
        status)
            if awake_active; then printf 'enabled\n'; else printf 'disabled\n'; fi
            ;;
        *) printf 'usage: %s awake {enable|disable|toggle|status}\n' "${0##*/}" >&2; exit 2 ;;
    esac
}

profile_name() {
    case "$1" in
        power-saver) printf 'eco' ;;
        balanced|performance) printf '%s' "$1" ;;
        eco) printf 'power-saver' ;;
        *) printf '%s' "$1" ;;
    esac
}

profile() {
    command -v powerprofilesctl >/dev/null || exit 1

    case "${1:-status}" in
        eco|balanced|performance)
            powerprofilesctl set "$(profile_name "$1")"
            refresh_waybar
            ;;
        cycle)
            case "$(powerprofilesctl get)" in
                power-saver) powerprofilesctl set balanced ;;
                balanced) powerprofilesctl set performance ;;
                *) powerprofilesctl set power-saver ;;
            esac
            refresh_waybar
            ;;
        status)
            profile_name "$(powerprofilesctl get)"
            printf '\n'
            ;;
        *) printf 'usage: %s profile {eco|balanced|performance|cycle|status}\n' "${0##*/}" >&2; exit 2 ;;
    esac
}

case "${1:-}" in
    lock) loginctl lock-session ;;
    logout) uwsm stop ;;
    suspend) systemctl suspend ;;
    hibernate) systemctl hibernate ;;
    reboot) systemctl reboot ;;
    shutdown) systemctl poweroff ;;
    awake) awake "${2:-status}" ;;
    profile) profile "${2:-status}" ;;
    *) printf 'usage: %s {lock|logout|suspend|hibernate|reboot|shutdown|awake|profile}\n' "${0##*/}" >&2; exit 2 ;;
esac
