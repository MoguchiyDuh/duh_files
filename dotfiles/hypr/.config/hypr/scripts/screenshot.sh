case "$1" in
    fullscreen)
        hyprshot -m output
        ;;
    area)
        hyprshot -m region --clipboard
        ;;
    *)
        echo "Invalid argument: $1"
        exit 1
        ;;
esac