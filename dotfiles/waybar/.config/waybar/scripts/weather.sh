#!/usr/bin/env bash

set -euo pipefail

compact=$(curl --fail --silent --max-time 10 'https://wttr.in/?format=%c%t')
report=$(curl --fail --silent --max-time 10 'https://wttr.in/?0T')

tooltip=$(printf '<tt>%s</tt>\n\nLMB  Open wttr.in' "$report")

jq -cn --arg text "$compact" --arg tooltip "$tooltip" '{text:$text, tooltip:$tooltip}'
