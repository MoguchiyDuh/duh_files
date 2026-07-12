#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

# Menu options with icons
options=(
    "󰀻 Applications"
    "󰖯 Windows"
    "󰃬 Calculator"
    "󰊿 Translate"
    "󰖟 Web Search"
    "󰅌 Clipboard"
    " Emoji"
    "󰐥 Power Management"
    "󰖩 Wi-Fi"
    "󰂯 Bluetooth" 
    "󰻌 Process Management"
    "󰸉 Wallpaper"
    "󰏘 Color Picker"
    "󰖟 OCR"
)

# Show main menu
selected=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "Spotlight" -theme "$THEME")

# Handle selection
case "$selected" in
    *"Applications")
        "$SCRIPT_DIR/apps.sh"
        ;;
    *"Windows")
        "$SCRIPT_DIR/windows.sh"
        ;;
    *"Calculator")
        "$SCRIPT_DIR/calc.sh"
        ;;
    *"Translate")
        "$SCRIPT_DIR/translate.sh"
        ;;
    *"Web Search")
        "$SCRIPT_DIR/web_search.sh"
        ;;
    *"Clipboard")
        "$SCRIPT_DIR/clipboard.sh"
        ;;
    *"Emoji")
        "$SCRIPT_DIR/emoji.sh"
        ;;
    *"Power Management")
        "$SCRIPT_DIR/system.sh"
        ;;
    *"Wi-Fi")
        nm-connection-editor
        ;;
    *"Bluetooth")
        blueman-manager
        ;;
    *"Process Management")
        kitty btop
        ;;
    *"Wallpaper")
        "$SCRIPT_DIR/wallpaper.sh"
        ;;
    *"Color Picker")
        "$SCRIPT_DIR/color_picker.sh"
        ;;
    *"OCR")
        "$SCRIPT_DIR/ocr.sh"
        ;;
    *)
        exit 0
        ;;
esac
