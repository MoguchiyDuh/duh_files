#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

# Language selection
languages=(
    "🇬🇧 English (eng)"
    "🇷🇺 Russian (rus)"
    "🇬🇧🇷🇺 Both (eng+rus)"
)

selected_lang=$(printf '%s\n' "${languages[@]}" | rofi -dmenu -i -p "OCR Language" -theme "$THEME")

if [[ -z "$selected_lang" ]]; then
    exit 0
fi

# Parse language code
case "$selected_lang" in
    *"English"*)
        lang="eng"
        ;;
    *"Russian"*)
        lang="rus"
        ;;
    *"Both"*)
        lang="eng+rus"
        ;;
    *)
        exit 0
        ;;
esac

# Take screenshot of selected area
temp_img="/tmp/ocr_screenshot.png"
grim -g "$(slurp)" "$temp_img"

if [[ ! -f "$temp_img" ]]; then
    notify-send "OCR" "Screenshot cancelled" -i dialog-error
    exit 1
fi

# Perform OCR
text=$(tesseract "$temp_img" - -l "$lang" 2>/dev/null)

if [[ -n "$text" ]]; then
    echo "$text" | wl-copy
    notify-send "OCR Complete" "Text copied to clipboard:\n\n${text:0:100}..." -i edit-copy
else
    notify-send "OCR Failed" "No text detected" -i dialog-error
fi

# Cleanup
rm -f "$temp_img"
