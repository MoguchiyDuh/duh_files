#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

selected=$(cliphist list | rofi -dmenu -p "Clipboard" -theme "$THEME" \
    -kb-delete-entry "" \
    -kb-custom-1 "shift+Delete" \
    -kb-custom-2 "alt+Delete" \
    -kb-accept-entry "Return")

exit_code=$?

case $exit_code in
    0)
        if [[ -n "$selected" ]]; then
            echo "$selected" | cliphist decode | wl-copy
        fi
        ;;
    10)
        if [[ -n "$selected" ]]; then
            echo "$selected" | cliphist delete
            exec "$0"
        fi
        ;;
    11)
        cliphist wipe
        "$SCRIPT_DIR/spotlight.sh"
        ;;
    *)
        "$SCRIPT_DIR/spotlight.sh"
        ;;
esac
