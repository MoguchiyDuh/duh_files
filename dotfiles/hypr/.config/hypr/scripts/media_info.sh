#!/bin/bash

player_status=$(playerctl status 2>/dev/null)

if [ "$player_status" = "Playing" ] || [ "$player_status" = "Paused" ]; then
    artist=$(playerctl metadata artist)
    title=$(playerctl metadata title)
    album=$(playerctl metadata album)
    
    # Get position and duration in minutes:seconds
    position=$(playerctl position | awk '{printf "%d:%02d", $1/60, $1%60}')
    duration=$(playerctl metadata mpris:length | awk '{printf "%d:%02d", $1/1000000/60, $1/1000000%60}')
    
    if [ "$player_status" = "Playing" ]; then
        status_icon="▶"
    else
        status_icon="⏸"
    fi
    
    echo "$status_icon $artist - $title"
    echo "Position: $position / $duration"
else
    echo ""
fi