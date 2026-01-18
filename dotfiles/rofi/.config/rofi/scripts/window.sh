#!/bin/bash

THEME="$HOME/.config/rofi/conf/main.rasi"

selected=$(rofi -show window -theme "$THEME")

if [[ -z "$selected" ]]; then
    "$SCRIPT_DIR/spotlight.sh"
fi
