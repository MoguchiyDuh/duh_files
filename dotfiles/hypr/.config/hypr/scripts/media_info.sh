#!/usr/bin/env bash
set -uo pipefail

player_status=$(playerctl status 2>/dev/null) || player_status=""

case $player_status in
  Playing | Paused)
    artist=$(playerctl metadata artist 2>/dev/null) || artist=""
    title=$(playerctl metadata title 2>/dev/null) || title=""
    position=$(playerctl position 2>/dev/null | awk '{printf "%d:%02d", $1/60, $1%60}') || position=""
    duration=$(playerctl metadata mpris:length 2>/dev/null | awk '{printf "%d:%02d", $1/1000000/60, $1/1000000%60}') || duration=""
    if [[ $player_status == Playing ]]; then
      status_icon="▶"
    else
      status_icon="⏸"
    fi
    printf '%s %s - %s\n' "$status_icon" "$artist" "$title"
    printf 'Position: %s / %s\n' "$position" "$duration"
    ;;
  *)
    printf '\n'
    ;;
esac
