#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

current_profile=$("$SCRIPT_DIR/power.sh" profile status 2>/dev/null || echo "unknown")

options=(
    "󰌾 Lock"
    "󰗽 Logout"
    "󰒲 Suspend"
    "󰜛 Hibernate"
    "󰜉 Reboot"
    "󰐥 Shutdown"
    ""
    "󰌪 Profile: Eco"
    "󰾅 Profile: Balanced"
    "󰓅 Profile: Performance"
)

selected=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "System ($current_profile)" -theme "$THEME")

case "$selected" in
    *"Lock")
        "$SCRIPT_DIR/power.sh" lock
        ;;
    *"Logout")
        confirm=$(echo -e "Yes\nNo" | rofi -dmenu -p "Logout?" -theme "$THEME")
        if [[ "$confirm" == "Yes" ]]; then
            "$SCRIPT_DIR/power.sh" logout
        else
            "$SCRIPT_DIR/spotlight.sh"
        fi
        ;;
    *"Suspend")
        "$SCRIPT_DIR/power.sh" suspend
        ;;
    *"Hibernate"*)
        "$SCRIPT_DIR/power.sh" hibernate
        ;;
    *"Reboot")
        confirm=$(echo -e "Yes\nNo" | rofi -dmenu -p "Reboot?" -theme "$THEME")
        if [[ "$confirm" == "Yes" ]]; then
            "$SCRIPT_DIR/power.sh" reboot
        else
            "$SCRIPT_DIR/spotlight.sh"
        fi
        ;;
    *"Shutdown")
        confirm=$(echo -e "Yes\nNo" | rofi -dmenu -p "Shutdown?" -theme "$THEME")
        if [[ "$confirm" == "Yes" ]]; then
            "$SCRIPT_DIR/power.sh" shutdown
        else
            "$SCRIPT_DIR/spotlight.sh"
        fi
        ;;
    *"Profile: Eco")
        "$SCRIPT_DIR/power.sh" profile eco
        "$SCRIPT_DIR/spotlight.sh"
        ;;
    *"Profile: Balanced")
        "$SCRIPT_DIR/power.sh" profile balanced
        "$SCRIPT_DIR/spotlight.sh"
        ;;
    *"Profile: Performance")
        "$SCRIPT_DIR/power.sh" profile performance
        "$SCRIPT_DIR/spotlight.sh"
        ;;
    "")
        "$SCRIPT_DIR/spotlight.sh"
        ;;
    *)
        "$SCRIPT_DIR/spotlight.sh"
        ;;
esac
