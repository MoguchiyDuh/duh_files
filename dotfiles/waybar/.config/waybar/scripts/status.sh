#!/usr/bin/env bash

set -euo pipefail

power=$HOME/.config/hypr/scripts/power.sh

pill_gpu() {
    local row util used total temp tooltip class
    row=$(nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu --format=csv,noheader,nounits 2>/dev/null || true)
    if [[ -z "$row" ]]; then
        jq -cn '{text:"", class:"hidden", tooltip:""}'
        return
    fi
    IFS=',' read -r util used total temp <<<"$row"
    class=normal
    ((temp >= 80)) && class=hot
    tooltip=$(printf '<b>GPU</b>  %s%%  ·  %s°C\nVRAM  %s / %s MiB' "$util" "$temp" "$used" "$total")
    jq -cn --arg text "󰢮 ${util}%" --arg class "$class" --arg tooltip "$tooltip" \
        '{text:$text, class:$class, tooltip:$tooltip}'
}

pill_weather() {
    local compact report tooltip
    compact=$(curl --fail --silent --max-time 10 'https://wttr.in/?format=%c%t' 2>/dev/null || printf '?')
    if [[ "$compact" == "?" ]]; then
        report='weather unavailable'
    else
        report=$(curl --fail --silent --max-time 10 'https://wttr.in/?0T' 2>/dev/null || printf 'weather unavailable')
    fi
    tooltip=$(printf '<tt>%s</tt>' "$report")
    jq -cn --arg text "$compact" --arg tooltip "$tooltip" '{text:$text, tooltip:$tooltip}'
}

pill_clipboard() {
    local count tooltip
    count=$(timeout 3 elephant query "clipboard;;200;false" 2>/dev/null | grep -c '^item:' || true)
    tooltip=$(printf '<b>Clipboard history</b>\n%s entries' "$count")
    jq -cn --arg text "󰅍" --arg tooltip "$tooltip" '{text:$text, tooltip:$tooltip}'
}

pill_awake() {
    local state
    state=$("$power" awake status 2>/dev/null || printf disabled)
    if [[ "$state" == enabled ]]; then
        jq -cn '{text:"󰅶", class:"active", tooltip:"Idle inhibition  active"}'
    else
        jq -cn '{text:"", class:"hidden", tooltip:""}'
    fi
}

pill_profile() {
    local state
    state=$("$power" profile status 2>/dev/null || printf balanced)
    case "$state" in
    eco) jq -cn '{text:"󰌪", class:"eco", tooltip:"Power profile  eco"}' ;;
    performance) jq -cn '{text:"󰓅", class:"performance", tooltip:"Power profile  performance"}' ;;
    *) jq -cn '{text:"", class:"hidden", tooltip:""}' ;;
    esac
}

case "${1:-}" in
gpu) pill_gpu ;;
weather) pill_weather ;;
clipboard) pill_clipboard ;;
awake) pill_awake ;;
profile) pill_profile ;;
*)
    printf 'usage: %s <gpu|weather|clipboard|awake|profile>\n' "$0" >&2
    exit 2
    ;;
esac
