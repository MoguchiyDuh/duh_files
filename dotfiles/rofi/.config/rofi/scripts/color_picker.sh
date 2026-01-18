#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

# Close rofi if open
pkill rofi
sleep 0.3

# Pick color with hyprpicker
color=$(hyprpicker -a -f hex)

if [[ -n "$color" ]]; then
    # Show notification
    notify-send "Color Picked" "$color copied to clipboard" -i color-picker

    # Options for what to do with the color
    options=(
        "📋 Copied: $color"
        "🎨 RGB"
        "🖌️ HSL"
        "🔢 Decimal"
    )

    selected=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "Color: $color" -theme "$THEME")

    case "$selected" in
        *"RGB"*)
            # Convert hex to RGB
            rgb=$(printf "%d %d %d" 0x${color:1:2} 0x${color:3:2} 0x${color:5:2})
            echo "rgb($rgb)" | tr ' ' ',' | wl-copy
            notify-send "RGB" "rgb($rgb) copied" -i color-picker
            ;;
        *"HSL"*)
            notify-send "HSL" "Feature not implemented yet" -i color-picker
            ;;
        *"Decimal"*)
            decimal=$((16#${color:1}))
            echo "$decimal" | wl-copy
            notify-send "Decimal" "$decimal copied" -i color-picker
            ;;
    esac
fi
