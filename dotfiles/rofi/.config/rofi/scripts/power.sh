#!/bin/bash

case "$1" in
    1|lock)
        sleep 0.5
        hyprlock
        ;;
    2|logout)
        sleep 0.5
        hyprctl dispatch exit
        ;;
    3|suspend)
        sleep 0.5
        systemctl suspend
        ;;
    4|hibernate)
        notify-send "Hibernate disabled" "This machine has no safe resume configuration; use suspend." -u critical
        exit 1
        ;;
    5|reboot)
        sleep 0.5
        systemctl reboot
        ;;
    6|shutdown)
        sleep 0.5
        systemctl poweroff
        ;;
    *)
        echo "Usage: $0 [1-6|lock|logout|suspend|hibernate|reboot|shutdown]"
        echo "1 - lock"
        echo "2 - logout" 
        echo "3 - suspend"
        echo "4 - hibernate disabled"
        echo "5 - reboot"
        echo "6 - shutdown"
        exit 1
        ;;
esac
