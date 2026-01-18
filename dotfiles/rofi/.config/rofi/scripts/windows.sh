#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

# Get list of windows with their workspace, class, and title
windows=$(hyprctl clients -j | jq -r '.[] | "\(.workspace.id):\(.class):\(.title):\(.address)"')

if [[ -z "$windows" ]]; then
    notify-send "No windows" "No windows open" -i dialog-information
    exit 0
fi

# Format for rofi display
formatted=""
while IFS= read -r line; do
    workspace=$(echo "$line" | cut -d':' -f1)
    class=$(echo "$line" | cut -d':' -f2)
    title=$(echo "$line" | cut -d':' -f3)
    address=$(echo "$line" | cut -d':' -f4-)

    # Truncate long titles
    if [[ ${#title} -gt 50 ]]; then
        title="${title:0:47}..."
    fi

    formatted+="[${workspace}] ${class} - ${title}|${address}\n"
done <<< "$windows"

# Show in rofi
selected=$(echo -e "$formatted" | rofi -dmenu -i -p "Windows" -theme "$THEME" -format "s")

if [[ -n "$selected" ]]; then
    # Extract window address
    address=$(echo "$selected" | cut -d'|' -f2)

    # Focus the window
    hyprctl dispatch focuswindow "address:${address}"
fi
