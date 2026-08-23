#!/usr/bin/env bash
set -Eeuo pipefail

unit="elephant.service"
socket="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/elephant/elephant.sock"

case "${1:-}" in
  start) systemctl --user start "$unit" ;;
  stop) systemctl --user stop "$unit" ;;
  restart) systemctl --user restart "$unit" ;;
  status)
    systemctl --user status "$unit" --no-pager -n 5 || true
    if [[ -S $socket ]]; then
      printf 'socket: %s\n' "$socket"
    else
      printf 'socket missing: %s\n' "$socket"
    fi
    ;;
  *) printf 'usage: %s {start|stop|restart|status}\n' "${0##*/}" >&2; exit 2 ;;
esac
