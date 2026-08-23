#!/usr/bin/env bash

set -euo pipefail

kind=${1:?sink|source}
action=${2:?up|down}
step=5
limit=100

if [[ "$kind" == sink ]]; then
    cur=$(pactl get-sink-volume @DEFAULT_SINK@ 2>/dev/null | grep -oP '\d+(?=%)' | head -1 || printf 100)
else
    cur=$(pactl get-source-volume @DEFAULT_SOURCE@ 2>/dev/null | grep -oP '\d+(?=%)' | head -1 || printf 100)
fi

((cur > limit)) && cur=$limit
case "$action" in
up)
    ((cur += step))
    ((cur > limit)) && cur=$limit
    ;;
down)
    ((cur -= step))
    ((cur < 0)) && cur=0
    ;;
*) exit 2 ;;
esac

if [[ "$kind" == sink ]]; then
    pactl set-sink-volume @DEFAULT_SINK@ "${cur}%"
else
    pactl set-source-volume @DEFAULT_SOURCE@ "${cur}%"
fi
