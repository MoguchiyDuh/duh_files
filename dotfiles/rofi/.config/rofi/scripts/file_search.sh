#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

search_files() {
    local query="$1"
    
    if [[ -z "$query" ]]; then
        find "$HOME" -type f -not -path "*/.*" -printf "%T@ %p\n" 2>/dev/null | \
        sort -rn | head -20 | cut -d' ' -f2- | \
        while read -r file; do
            echo "󰈙 $(basename "$file")|$file"
        done
    else
        find "$HOME" -type f -not -path "*/.*" -iname "*$query*" 2>/dev/null | \
        head -50 | \
        while read -r file; do
            case "${file##*.}" in
                pdf) icon="󰈦" ;;
                txt|md) icon="󰈙" ;;
                jpg|jpeg|png|gif) icon="󰈟" ;;
                mp3|wav|flac) icon="󰈣" ;;
                mp4|avi|mkv) icon="󰈫" ;;
                zip|tar|gz) icon="󰈦" ;;
                *) icon="󰈙" ;;
            esac
            echo "$icon $(basename "$file")|$file"
        done
    fi
}

while true; do
    query=$(echo "" | rofi -dmenu -p "Files" -theme "$THEME" -filter "$query")
    
    if [[ -z "$query" && -z "$previous_query" ]]; then
        "$SCRIPT_DIR/spotlight.sh"
        exit 0
    fi
    
    if [[ "$query" != "$previous_query" ]]; then
        results=$(search_files "$query")
        previous_query="$query"
    fi
    
    if [[ -n "$results" ]]; then
        selected=$(echo "$results" | rofi -dmenu -p "Files: $query" -theme "$THEME" -format "s")
        
        if [[ -n "$selected" ]]; then
            file_path=$(echo "$results" | sed -n "${selected}p" | cut -d'|' -f2)
            
            if [[ -f "$file_path" ]]; then
                xdg-open "$file_path" 2>/dev/null &
                exit 0
            fi
        else
            "$SCRIPT_DIR/spotlight.sh"
            exit 0
        fi
    else
        echo "No files found" | rofi -dmenu -p "Files: $query" -theme "$THEME"
        query=""
    fi
done
