#!/bin/bash

readonly WALLPAPER_DIR="$HOME/Pictures/Wallpapers"
readonly CACHE_DIR="$HOME/.cache/wallpapers"
readonly ROFI_COMMAND="rofi -dmenu -show-icons -theme $HOME/.config/rofi/conf/wallpaper.rasi"
readonly WALLUST_SCRIPT="$HOME/.config/wallust/wallpaper.sh"

set -euo pipefail

mkdir -p "$CACHE_DIR"

if [[ ! -d "$WALLPAPER_DIR" ]]; then
    echo "Error: Wallpaper directory not found: $WALLPAPER_DIR" >&2
    exit 1
fi

process_thumbnail() {
    local file="$1"
    local filename=$(basename "$file")
    local cache_file="${CACHE_DIR}/${filename}.jpg"
    
    if [[ -f "$cache_file" && "$file" -ot "$cache_file" ]]; then
        return 0
    fi
    
    case "${filename##*.}" in
        gif|mp4|mkv|webm|mov)
            ffmpeg -loglevel error -y -ss "00:00:01" -i "$file" \
                   -vframes 1 -q:v 3 -vf "scale=500:500:force_original_aspect_ratio=decrease:flags=lanczos" \
                   "$cache_file" || return 1
            ;;
        jpg|jpeg|png|webp)
            magick "$file" -resize "500x500^" -gravity center -extent "500x500" \
                   -quality 90 "$cache_file" || return 1
            ;;
        *)
            return 1
            ;;
    esac
    
    echo "Created thumbnail: $cache_file" >&2
}

export -f process_thumbnail
export CACHE_DIR

echo "Generating thumbnails..." >&2
find "$WALLPAPER_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \
    -o -iname "*.webp" -o -iname "*.gif" -o -iname "*.mp4" -o -iname "*.mkv" \
    -o -iname "*.webm" -o -iname "*.mov" \) -print0 | \
    xargs -0 -P 4 -I {} bash -c 'process_thumbnail "{}"' _

echo "Loading wallpaper selector..." >&2
selected_wallpaper=$(find "$WALLPAPER_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" \
    -o -iname "*.png" -o -iname "*.webp" -o -iname "*.gif" -o -iname "*.mp4" \
    -o -iname "*.mkv" -o -iname "*.webm" -o -iname "*.mov" \) -print0 | \
    xargs -0 -I {} basename "{}" | \
    while IFS= read -r filename; do
        cache_file="${CACHE_DIR}/${filename}.jpg"
        if [[ -f "$cache_file" ]]; then
            printf '%s\000icon\037%s\n' "$filename" "$cache_file"
        else
            printf '%s\n' "$filename"
        fi
    done | $ROFI_COMMAND)

if [[ -z "$selected_wallpaper" ]]; then
    echo "No wallpaper selected." >&2
    exit 0
fi

wallpaper_path="${WALLPAPER_DIR}/${selected_wallpaper}"

if [[ ! -f "$wallpaper_path" ]]; then
    echo "Error: Wallpaper not found: $wallpaper_path" >&2
    exit 1
fi

echo "Selected wallpaper: $wallpaper_path" >&2

if [[ ! -x "$WALLUST_SCRIPT" ]]; then
    echo "Error: Wallust script not found or not executable: $WALLUST_SCRIPT" >&2
    exit 1
fi

"$WALLUST_SCRIPT" "$wallpaper_path"
