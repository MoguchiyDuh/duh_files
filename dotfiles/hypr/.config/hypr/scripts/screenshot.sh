case "$1" in
    fullscreen)
        hyprshot -m output
        ;;
    area)
        hyprshot -m region --clipboard-only
        ;;
    window)
        hyprshot -m window --clipboard-only
        ;;
    active)
        hyprshot -m window -m active --clipboard-only
        ;;
    *)
        echo "Usage: $0 {fullscreen|area|window|active}"
        exit 1
        ;;
esac