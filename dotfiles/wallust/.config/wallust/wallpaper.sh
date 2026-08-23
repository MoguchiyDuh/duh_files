#!/usr/bin/env bash
set -Eeuo pipefail

usage() {
    printf 'usage: %s <image|video>\n' "${0##*/}" >&2
    exit 1
}

[[ $# -eq 1 ]] || usage
wallpaper=$(readlink -f -- "$1")
[[ -f $wallpaper ]] || usage

cache="$HOME/.cache"
mkdir -p "$cache/wallust"

pkill -u "$(id -u)" -x mpvpaper 2>/dev/null || true

case $wallpaper in
*.mp4 | *.avi | *.mov | *.mkv | *.webm | *.gif)
    monitor=$(hyprctl -j monitors | jq -r '(map(select(.focused)) + .)[0].name')
    setsid mpvpaper -o "no-audio loop-file panscan=1.0" "$monitor" "$wallpaper" >/dev/null 2>&1 &
    ln -sfn "$wallpaper" "$cache/current_wallpaper.png"
    frame=$(mktemp --suffix=.jpg)
    if ffmpeg -y -ss 3 -i "$wallpaper" -vframes 1 -q:v 2 "$frame" </dev/null >/dev/null 2>&1; then
        wallust run "$frame"
    else
        wallust run "$wallpaper"
    fi
    rm -f "$frame"
    ;;
*.jpg | *.jpeg | *.png | *.webp)
    awww img "$wallpaper" -t center 2>/dev/null || true
    ln -sfn "$wallpaper" "$cache/current_wallpaper.png"
    wallust run "$wallpaper"
    ;;
*)
    usage
    ;;
esac
