#!/usr/bin/env bash

set -Eeuo pipefail

power_script="$HOME/.config/walker/scripts/power.sh"
hypr_scripts="$HOME/.config/hypr/scripts"
wallpaper_root="$HOME/Pictures/Wallpapers"

fail() {
    printf '%s\n' "$1" >&2
    notify-send "Walker utility" "$1" -u critical 2>/dev/null || true
    exit 1
}

need() {
    command -v "$1" >/dev/null 2>&1 || fail "$1 is not installed"
}

stdin_value() {
    local value=""
    IFS= read -r value || [[ -n "$value" ]] || return 1
    printf '%s' "$value"
}

walker_menu() {
    local prompt="$1" selection
    shift
    sleep 0.15
    selection=$(printf '%s\n' "$@" | walker --dmenu --placeholder "$prompt") || return 1
    [[ -n "$selection" && "$selection" != "CNCLD" ]] || return 1
    printf '%s' "$selection"
}

confirm() {
    local label="$1" choice
    choice=$(walker_menu "Confirm $label" "Confirm $label" "Cancel") || return 1
    [[ "$choice" == "Confirm $label" ]]
}

ocr() {
    local language="$1" geometry
    need slurp
    need grim
    need tesseract
    need wl-copy
    geometry=$(slurp) || return 0
    [[ -n "$geometry" ]] || return 0
    grim -g "$geometry" - | tesseract stdin stdout -l "$language" 2>/dev/null | wl-copy
    notify-send "OCR" "Recognized text copied" -u low 2>/dev/null || true
}

validate_wallpaper() {
    local candidate="$1" root resolved
    root=$(realpath -- "$wallpaper_root") || fail "Wallpaper directory is unavailable"
    resolved=$(realpath -- "$candidate") || fail "Wallpaper does not exist"
    [[ -f "$resolved" && "$resolved" == "$root/"* ]] || fail "Invalid wallpaper path"
    case "$resolved" in
        *.jpg|*.jpeg|*.png|*.webp|*.gif|*.mp4|*.avi|*.mov|*.mkv|*.webm) ;;
        *) fail "Unsupported wallpaper format" ;;
    esac
    printf '%s' "$resolved"
}

thumbnail() {
    local source cache_dir hash thumb temporary lower
    need sha256sum
    source=$(validate_wallpaper "$1")
    cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/walker/wallpaper-thumbnails"
    mkdir -p "$cache_dir"
    hash=$(printf '%s' "$source" | sha256sum)
    hash=${hash%% *}
    thumb="$cache_dir/$hash.jpg"

    if [[ ! -f "$thumb" || "$source" -nt "$thumb" ]]; then
        temporary=$(mktemp "$cache_dir/.$hash.XXXXXX.jpg")
        lower=${source,,}
        if [[ "$lower" == *.gif || "$lower" == *.mp4 || "$lower" == *.avi || "$lower" == *.mov || "$lower" == *.mkv || "$lower" == *.webm ]]; then
            need ffmpeg
            if ! ffmpeg -loglevel error -y -ss 1 -i "$source" -frames:v 1 \
                -vf 'scale=320:180:force_original_aspect_ratio=increase,crop=320:180' "$temporary"; then
                if ! ffmpeg -loglevel error -y -i "$source" -frames:v 1 \
                    -vf 'scale=320:180:force_original_aspect_ratio=increase,crop=320:180' "$temporary"; then
                    rm -f "$temporary"
                    fail "Could not create video thumbnail"
                fi
            fi
        else
            need magick
            if ! magick "$source" -auto-orient -thumbnail '320x180^' -gravity center -extent 320x180 "$temporary"; then
                rm -f "$temporary"
                fail "Could not create image thumbnail"
            fi
        fi
        mv -f "$temporary" "$thumb"
    fi
    printf '%s\n' "$thumb"
}

action=${1:-}
if [[ -z "$action" ]]; then
    action=$(stdin_value) || fail "Missing action"
fi

case "$action" in
    power.lock)
        bash "$power_script" lock
        ;;
    power.logout|power.suspend|power.hibernate|power.reboot|power.shutdown)
        power_action=${action#power.}
        confirm "$power_action" || exit 0
        bash "$power_script" "$power_action"
        ;;
    profile.eco|profile.balanced|profile.performance)
        bash "$power_script" profile "${action#profile.}"
        ;;
    theme.*)
        fail "Theme switching not supported"
        ;;
    awake.toggle)
        bash "$power_script" awake toggle
        ;;
    animation.*)
        animation=${action#animation.}
        printf '%s\n' "$animation" > "${XDG_CACHE_HOME:-$HOME/.cache}/current-animation"
        hyprctl reload >/dev/null 2>&1 || true
        notify-send "Animations" "$animation applied" -u low -t 2000 2>/dev/null || true
        ;;
    ocr.eng)
        ocr eng
        ;;
    screenshot.fullscreen|screenshot.active|screenshot.area)
        bash "$hypr_scripts/screenshot.sh" "${action#screenshot.}"
        ;;
    record.toggle)
        bash "$hypr_scripts/record.sh"
        ;;
    ocr.rus)
        ocr rus
        ;;
    ocr.eng-rus)
        ocr eng+rus
        ;;
    color.pick)
        need hyprpicker
        need wl-copy
        color=$(hyprpicker) || exit 0
        [[ -n "$color" ]] || exit 0
        printf '%s' "$color" | wl-copy
        notify-send "Color" "$color copied" -u low 2>/dev/null || true
        ;;
    provider.translate)
        (sleep 0.15; walker --provider translate --placeholder "Translate to English" >/dev/null 2>&1) &
        ;;
    wallpaper)
        wallpaper=$(stdin_value) || fail "Missing wallpaper"
        wallpaper=$(validate_wallpaper "$wallpaper")
        ln -sfn "$wallpaper" "${XDG_CACHE_HOME:-$HOME/.cache}/current_wallpaper.png"
        awww img "$wallpaper" --resize crop -t fade --transition-step 90 2>/dev/null || true
        matugen image --prefer saturation "$wallpaper" 2>/dev/null || true
        notify-send "Wallpaper" "Applied" -u low -t 2000 2>/dev/null || true
        ;;
    thumbnail)
        (($# == 2)) || fail "Invalid thumbnail request"
        thumbnail "$2"
        ;;
    *)
        fail "Unknown action"
        ;;
esac
