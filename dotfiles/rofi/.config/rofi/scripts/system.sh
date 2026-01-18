#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="$HOME/.config/rofi/conf/main.rasi"

options=(
    "󰌾 Lock"
    "󰗽 Logout"
    "󰒲 Suspend"
    "󰜛 Hibernate"
    "󰜉 Reboot"
    "󰐥 Shutdown"
)

selected=$(printf '%s\n' "${options[@]}" | rofi -dmenu -i -p "System" -theme "$THEME")

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
    *"Hibernate")
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
    *)
        "$SCRIPT_DIR/spotlight.sh"
        ;;
esac
