#!/usr/bin/env bash

set -euo pipefail

case "${1:-}" in
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
        printf 'Usage: %s {fullscreen|area|window|active}\n' "$0" >&2
        exit 1
        ;;
esac
