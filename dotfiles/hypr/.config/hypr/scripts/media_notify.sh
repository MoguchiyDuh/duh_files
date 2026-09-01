#!/usr/bin/env bash
set -uo pipefail

action="${1:-}"

case "$action" in
    play-pause) playerctl play-pause ;;
    next)       playerctl next ;;
    previous)   playerctl previous ;;
    stop)       playerctl stop ;;
    *)
        printf 'Usage: %s {play-pause|next|previous|stop}\n' "$0" >&2
        exit 1
        ;;
esac

status=$(playerctl status 2>/dev/null) || exit 0
[[ "$status" == "Stopped" || -z "$status" ]] && exit 0

if [[ "$action" == "next" || "$action" == "previous" ]]; then
    old_id=$(playerctl metadata mpris:trackid 2>/dev/null)
    deadline=$(( $(date +%s%3N) + 1500 ))
    while [[ $(date +%s%3N) -lt $deadline ]]; do
        new_id=$(playerctl metadata mpris:trackid 2>/dev/null)
        [[ "$new_id" != "$old_id" && -n "$new_id" ]] && break
        sleep 0.05
    done
fi

title=$(playerctl metadata xesam:title 2>/dev/null)
artist=$(playerctl metadata xesam:artist 2>/dev/null)
art_url=$(playerctl metadata mpris:artUrl 2>/dev/null)
position=$(playerctl position 2>/dev/null | awk '{printf "%d:%02d", $1/60, $1%60}')
length=$(playerctl metadata mpris:length 2>/dev/null | awk '{printf "%d:%02d", $1/1000000/60, $1/1000000%60}')

[[ "$status" == "Playing" ]] && status_icon="▶" || status_icon="⏸"

art_path=""
if [[ "$art_url" == file://* ]]; then
    art_path="${art_url#file://}"
elif [[ "$art_url" == https://* || "$art_url" == http://* ]]; then
    art_path="/tmp/media-notify-art.jpg"
    curl -sL --max-time 3 "$art_url" -o "$art_path" || art_path=""
fi

body="${artist}"
[[ -n "$position" && -n "$length" ]] && body="${body}  ${position} / ${length}"

notify_args=(
    --app-name "Media"
    --urgency low
    --expire-time 3000
    --hint string:x-dunst-stack-tag:media-osd
    --hint string:x-canonical-private-synchronous:media-osd
    "${status_icon} ${title}"
    "${body}"
)
[[ -n "$art_path" ]] && notify_args+=(--icon "$art_path")

notify-send "${notify_args[@]}"
