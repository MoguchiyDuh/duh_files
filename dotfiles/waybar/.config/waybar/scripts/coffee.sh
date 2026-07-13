#!/usr/bin/env bash

set -uo pipefail

power="$HOME/.config/hypr/scripts/power.sh"
awake=disabled
profile=balanced

if [[ -x "$power" ]]; then
    awake=$("$power" awake status 2>/dev/null || printf disabled)
    profile=$("$power" profile status 2>/dev/null || printf balanced)
fi

case "${1:-}" in
    awake)
        if [[ "$awake" == enabled ]]; then
            jq -cn '{text:"󰅶", class:["active"], tooltip:"Idle inhibition  active\n\nManage in AnyRun"}'
        else
            jq -cn '{text:"", class:["hidden"], tooltip:""}'
        fi
        ;;
    profile)
        case "$profile" in
            eco) jq -cn '{text:"󰌪", class:["eco"], tooltip:"Power profile  eco\n\nManage in AnyRun"}' ;;
            performance) jq -cn '{text:"󰓅", class:["performance"], tooltip:"Power profile  performance\n\nManage in AnyRun"}' ;;
            *) jq -cn '{text:"", class:["hidden"], tooltip:""}' ;;
        esac
        ;;
    *)
        printf 'usage: %s <awake|profile>\n' "$0" >&2
        exit 2
        ;;
esac
