#!/usr/bin/env bash
# Waybar "coffee" status module — Android-statusbar style.
#   Shows an icon ONLY when state is non-default:
#     - awake (idle-inhibit) is on, and/or
#     - power profile is eco or performance (balanced = default, hidden).
#   When balanced AND awake-off, emits empty text so waybar hides the module.
#
#   LMB toggles awake, RMB cycles profile (handlers in the module config,
#   which re-signal this script).
#
# Output: waybar JSON {text, tooltip, class}.

set -uo pipefail

power="$HOME/.config/hypr/scripts/power.sh"

awake="disabled"
[[ -x "$power" ]] && awake=$("$power" awake status 2>/dev/null || echo disabled)

profile="balanced"
[[ -x "$power" ]] && profile=$("$power" profile status 2>/dev/null || echo balanced)

parts=()
classes=()

# Awake indicator (only when on).
if [[ "$awake" == "enabled" ]]; then
    parts+=("󰅶")                 # full mug: staying awake
    classes+=("awake")
    awake_line="Awake: on"
else
    awake_line="Awake: off"
fi

# Profile indicator (only when non-default).
case "$profile" in
    eco)         parts+=("󰌪"); classes+=("profile-eco");         prof_line="Profile: eco" ;;
    performance) parts+=("󰓅"); classes+=("profile-performance"); prof_line="Profile: performance" ;;
    balanced)    prof_line="Profile: balanced" ;;
    *)           prof_line="Profile: $profile" ;;
esac

# Nothing to show -> empty text hides the module (Android topbar behavior).
if [[ ${#parts[@]} -eq 0 ]]; then
    printf '{"text":"","tooltip":"","class":[]}\n'
    exit 0
fi

text="${parts[*]}"
class_json=$(printf '"%s",' "${classes[@]}"); class_json="[${class_json%,}]"

printf '{"text":"%s","tooltip":"%s\\n%s","class":%s}\n' \
    "$text" "$awake_line" "$prof_line" "$class_json"
