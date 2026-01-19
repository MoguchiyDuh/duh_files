#!/bin/bash

wallpaper="$1"

pkill -f "mpvpaper" || true
sleep 0.1

case "$wallpaper" in
    *.mp4 | *.avi | *.mov | *.mkv | *.webm | *.gif )
        
        MONITOR=$(hyprctl monitors | grep -oP 'Monitor \K[^ ]+' | head -n1)
        
        mpvpaper -o "no-audio loop-file panscan=1.0" "$MONITOR" "$wallpaper" &
        
        ln -sf "$wallpaper" ~/.cache/current_wallpaper.png
        
        TEMP_FRAME="/tmp/video_wall_frame.jpg"
        ffmpeg -y -ss "00:00:03" -i "$wallpaper" -vframes 1 -q:v 2 "$TEMP_FRAME" 2>/dev/null
        
        if [[ -f "$TEMP_FRAME" ]]; then
            sleep 0.6
            wallust run "$TEMP_FRAME"
            rm -f "$TEMP_FRAME"
        fi
        ;;
    
    *.jpg | *.jpeg | *.png | *.webp )
        swww img "$wallpaper" -t center
        ln -sf "$wallpaper" ~/.cache/current_wallpaper.png
        sleep 0.6
        wallust run "$wallpaper"
        ;;
    
    *)
        echo "Error: Unsupported file format: $wallpaper" >&2
        echo "Supported formats: jpg, jpeg, png, webp, mp4, avi, mov, mkv, webm, gif" >&2
        exit 1
        ;;
esac

# Restart Hyprland gui
hyprctl reload

# Restart Waybar
killall waybar && waybar &
