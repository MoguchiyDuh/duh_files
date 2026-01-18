#!/bin/bash

FAV_FILE="${HOME}/.cliphist_favorites"
MENU="rofi -dmenu -p "📋" -theme ~/.config/rofi/conf/clipboard.rasi"

show_history() {
    selected=$(cliphist list | $MENU)
    if [ -n "$selected" ]; then
        cliphist decode <<< "$selected" | wl-copy
        notify-send "Copied to clipboard."
    fi
}

wipe_history() {
    cliphist wipe
    notify-send "Clipboard history wiped."
}

show_favorites() {
    if [[ ! -s "$FAV_FILE" ]]; then
        notify-send "No favorites found."
        exit 0
    fi

    mapfile -t favorites < "$FAV_FILE"
    decoded_lines=()

    for fav in "${favorites[@]}"; do
        single_line=$(echo "$fav" | base64 --decode | tr '\n' ' ')
        decoded_lines+=("$single_line")
    done

    selected=$(printf "%s\n" "${decoded_lines[@]}" | $MENU -p "Favorites")
    if [ -n "$selected" ]; then
        index=$(printf "%s\n" "${decoded_lines[@]}" | grep -nxF "$selected" | cut -d: -f1)
        [[ -n "$index" ]] && echo "${favorites[$((index - 1))]}" | base64 --decode | wl-copy
        notify-send "Copied favorite to clipboard."
    fi
}

case "$1" in
    show)
        show_history
        ;;
    wipe)
        wipe_history
        ;;
    fav)
        show_favorites
        ;;
    *)
        echo "Usage: $0 {show|wipe|fav}"
        exit 1
        ;;
esac
