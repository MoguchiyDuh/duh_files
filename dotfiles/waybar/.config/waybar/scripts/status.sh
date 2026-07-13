#!/usr/bin/env bash

set -euo pipefail

case "${1:-}" in
    clipboard)
        count=$(cliphist list 2>/dev/null | wc -l)
        tooltip=$(printf '<b>Clipboard history</b>\n%s entries\n\nLMB  Open\nMMB  Wipe\nRMB  Wipe' "$count")
        jq -cn --arg tooltip "$tooltip" '{text:"", tooltip:$tooltip}'
        ;;
    *)
        printf 'usage: %s <clipboard>\n' "$0" >&2
        exit 2
        ;;
esac
