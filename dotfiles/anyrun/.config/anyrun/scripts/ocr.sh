#!/usr/bin/env bash
# Screen-region OCR (eng+rus) -> clipboard. No launcher menu; fixed languages.
set -euo pipefail

lang="eng+rus"
tmp="$(mktemp --suffix=.png)"
trap 'rm -f "$tmp"' EXIT

grim -g "$(slurp)" "$tmp" || { notify-send "OCR" "Cancelled" -i dialog-error; exit 0; }

text="$(tesseract "$tmp" - -l "$lang" 2>/dev/null)"

if [ -n "$text" ]; then
    printf '%s' "$text" | wl-copy
    notify-send "OCR complete" "${text:0:120}" -i edit-copy
else
    notify-send "OCR failed" "No text detected" -i dialog-error
fi
