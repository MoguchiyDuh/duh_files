#!/usr/bin/env bash
# Runtime dispatcher for anyrun action entries.
# Picks whatever tool is actually installed so the same config works across
# machines (laptop/desktop, NVIDIA/AMD/Intel). Assumes Arch + Hyprland.
set -euo pipefail

have() { command -v "$1" >/dev/null 2>&1; }

# Run the first available command from a list of "cmd args" strings.
first_of() {
    local entry bin
    for entry in "$@"; do
        bin=${entry%% *}
        if have "$bin"; then
            # shellcheck disable=SC2086
            exec $entry
        fi
    done
    notify-send "anyrun" "No handler found for: ${FUNCNAME[1]:-action}" -i dialog-error
    exit 1
}

case "${1:-}" in
    wifi)
        first_of \
            "nm-connection-editor" \
            "iwgtk" \
            "kitty -e nmtui" \
            "alacritty -e nmtui" \
            "foot -e nmtui"
        ;;

    bluetooth)
        first_of \
            "blueman-manager" \
            "overskride" \
            "kitty -e bluetuith" \
            "alacritty -e bluetuith" \
            "foot -e bluetuith"
        ;;

    audio)
        first_of \
            "pavucontrol" \
            "pavucontrol-qt" \
            "kitty -e wiremix" \
            "kitty -e pulsemixer"
        ;;

    display)
        # GPU-agnostic monitor arrangement first, vendor control panels last.
        first_of \
            "nwg-displays" \
            "wdisplays" \
            "kitty -e wlr-randr" \
            "nvidia-settings" \
            "kitty -e ddcutil detect"
        ;;

    color-picker)
        if have hyprpicker; then
            color=$(hyprpicker -a -f hex 2>/dev/null || true)
            [ -n "${color:-}" ] && notify-send "Color copied" "$color" -i color-picker -t 2000
        elif have wl-color-picker; then
            wl-color-picker
        else
            notify-send "Color picker" "Install hyprpicker" -i dialog-error
        fi
        ;;

    record)
        # Prefer the repo's toggle script; otherwise fall back generically.
        rec="$HOME/.config/hypr/scripts/record.sh"
        if [ -x "$rec" ]; then
            exec "$rec"
        elif have wf-recorder; then
            pidfile="${XDG_RUNTIME_DIR:-/tmp}/wf-recorder.pid"
            if [ -f "$pidfile" ] && kill -0 "$(cat "$pidfile")" 2>/dev/null; then
                kill -INT "$(cat "$pidfile")"; rm -f "$pidfile"
                notify-send "Recording stopped" -t 1500
            else
                out="$HOME/Videos/rec_$(date +%Y%m%d_%H%M%S).mp4"
                mkdir -p "$HOME/Videos"
                wf-recorder -f "$out" & echo $! > "$pidfile"
                notify-send "Recording started" "$out" -t 1500
            fi
        else
            notify-send "Screen record" "Install wf-recorder or gpu-screen-recorder" -i dialog-error
        fi
        ;;

    *)
        printf 'Unknown dispatch target: %s\n' "${1:-}" >&2
        exit 2
        ;;
esac
