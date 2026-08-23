#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

result=$(rofi -show calc -theme "$THEME" -no-show-match -no-sort)

if [[ -z "$result" ]]; then
    "$SCRIPT_DIR/spotlight.sh"
    exit 0
elif [[ -n "$result" ]]; then
    answer=$(echo "$result" | awk '{print $NF}')
    
    echo "$answer" | cliphist store
    notify-send "Calculator" "Result copied: $answer"
fi

