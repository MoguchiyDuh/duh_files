#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

query=$(echo "" | rofi -dmenu -p "Web Search" -theme "$THEME")

if [[ -z "$query" ]]; then
    "$SCRIPT_DIR/spotlight.sh"
    exit 0
fi

engines=(
    "󰇥 DuckDuckGo: $query"
    " Google: $query"
    " YouTube: $query"
    " Pinterest: $query"
    "Yandex: $query"
)

selected_engine=$(printf '%s\n' "${engines[@]}" | rofi -dmenu -i -p "Search" -theme "$THEME")

if [[ -z "$selected_engine" ]]; then
    "$SCRIPT_DIR/spotlight.sh"
    exit 0
fi

encoded_query=$(echo "$query" | jq -sRr @uri)

case "$selected_engine" in
    *"Google:"*)
        url="https://www.google.com/search?q=$encoded_query"
        ;;
    *"DuckDuckGo:"*)
        url="https://duckduckgo.com/?q=$encoded_query"
        ;;
    *"YouTube:"*)
        url="https://www.youtube.com/results?search_query=$encoded_query"
        ;;
    *"Pinterest:"*)
        url="https://www.pinterest.com/search/pins/?q=$encoded_query"
        ;;
    *"Yandex:"*)
        url="https://yandex.ru/search?text=$encoded_query"
        ;;
    *)
        "$SCRIPT_DIR/spotlight.sh"
        exit 0
        ;;
esac

xdg-open "$url" 2>/dev/null &
