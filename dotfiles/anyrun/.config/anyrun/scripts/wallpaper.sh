#!/usr/bin/env bash
# Wallpaper picker for anyrun. Lists images from the wallpaper dir via the
# stdin plugin, then applies the choice through wallust (which recolors the
# whole theme, anyrun included).
set -euo pipefail

wallpaper_dir="$HOME/Pictures/Wallpapers"
wallust_apply="$HOME/.config/wallust/wallpaper.sh"

[ -d "$wallpaper_dir" ] || { notify-send "Wallpaper" "Dir not found: $wallpaper_dir" -i dialog-error; exit 1; }

# Collect candidate files (basename shown, full path resolved on select).
mapfile -t files < <(
    find "$wallpaper_dir" -type f \
        \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.webp' \
           -o -iname '*.gif' -o -iname '*.mp4' -o -iname '*.mkv' -o -iname '*.webm' -o -iname '*.mov' \) \
        | sort
)
[ "${#files[@]}" -gt 0 ] || { notify-send "Wallpaper" "No wallpapers found" -i dialog-error; exit 0; }

# Present basenames; anyrun stdin plugin echoes the selected line to stdout.
selected="$(
    for f in "${files[@]}"; do basename "$f"; done \
        | anyrun --plugins libstdin.so --show-results-immediately true 2>/dev/null
)"
[ -n "$selected" ] || exit 0

# Resolve back to the full path.
path=""
for f in "${files[@]}"; do
    [ "$(basename "$f")" = "$selected" ] && { path="$f"; break; }
done
[ -n "$path" ] || { notify-send "Wallpaper" "Not found: $selected" -i dialog-error; exit 1; }

[ -x "$wallust_apply" ] || { notify-send "Wallpaper" "wallust apply script missing" -i dialog-error; exit 1; }
"$wallust_apply" "$path"
