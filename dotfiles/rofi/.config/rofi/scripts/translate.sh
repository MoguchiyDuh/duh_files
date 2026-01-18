#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

# Get selected text from primary clipboard (active selection on screen)
selected=$(wl-paste --primary 2>/dev/null)

# If no active selection, show rofi prompt
if [ -z "$selected" ]; then
    selected=$(echo "" | rofi -dmenu -p "Translate:" -theme $THEME)
fi

# Clear primary selection
wl-copy --primary ""

# Open reverso if we have text
if [ -n "$selected" ]; then
    xdg-open "https://www.reverso.net/text-translation#&text=${selected// /%20}"
fi
