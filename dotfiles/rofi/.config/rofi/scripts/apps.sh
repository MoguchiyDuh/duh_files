#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

selected=$(rofi -show drun -theme "$THEME")

if [[ -z "$selected" ]]; then
    "$SCRIPT_DIR/spotlight.sh"
fi
