#!/usr/bin/env bash

set -euo pipefail

direction=${1:-next}
[[ "$direction" == "next" || "$direction" == "prev" ]] || exit 2

keyboard=$(hyprctl devices -j | jq -r '.keyboards as $keyboards | (($keyboards | map(select(.main == true)) | .[0].name) // $keyboards[0].name // empty)')
[[ -n "$keyboard" ]] || exit 1

hyprctl switchxkblayout "$keyboard" "$direction" >/dev/null
