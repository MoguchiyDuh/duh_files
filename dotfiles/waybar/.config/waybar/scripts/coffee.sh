#!/usr/bin/env bash
# Waybar "coffee" status module.
#   icon/class reflect awake (idle-inhibit) state + current power profile.
#   LMB toggles awake, RMB cycles profile (handlers live in the module config,
#   which re-signals this script).
#
# Output: waybar JSON {text, tooltip, class}. Tooltip shows current states only.

set -uo pipefail

power="$HOME/.config/rofi/scripts/power.sh"

awake="disabled"
[[ -x "$power" ]] && awake=$("$power" awake status 2>/dev/null || echo disabled)

profile="unknown"
[[ -x "$power" ]] && profile=$("$power" profile status 2>/dev/null || echo unknown)

if [[ "$awake" == "enabled" ]]; then
    icon="󰅶"                      # coffee (mug full): staying awake
    state_class="awake"
    awake_line="Awake: on"
else
    icon="󰅷"                      # coffee-off: normal idle behavior
    state_class="normal"
    awake_line="Awake: off"
fi

case "$profile" in
    eco)         prof_icon="󰌪"; prof_line="Profile: eco" ;;
    balanced)    prof_icon="󰾅"; prof_line="Profile: balanced" ;;
    performance) prof_icon="󰓅"; prof_line="Profile: performance" ;;
    *)           prof_icon="";  prof_line="Profile: $profile" ;;
esac

printf '{"text":"%s %s","tooltip":"%s\\n%s","class":["%s","profile-%s"]}\n' \
    "$icon" "$prof_icon" "$awake_line" "$prof_line" "$state_class" "$profile"
