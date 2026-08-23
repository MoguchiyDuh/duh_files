#!/usr/bin/env bash
set -Eeuo pipefail

unit="walker.service"
socket="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/walker/walker.sock"

toggle() {
  if [[ -S $socket ]] && command -v nc >/dev/null 2>&1; then
    printf '' | nc -w 2 -U "$socket" >/dev/null 2>&1 && return 0
  fi
  systemctl --user start "$unit"
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    [[ -S $socket ]] && break
    sleep 0.2
  done
  if [[ -S $socket ]] && command -v nc >/dev/null 2>&1; then
    printf '' | nc -w 2 -U "$socket" >/dev/null 2>&1 && return 0
  fi
  walker
}

case "${1:-}" in
  start) systemctl --user start "$unit" ;;
  stop) systemctl --user stop "$unit" ;;
  restart) systemctl --user restart "$unit" ;;
  toggle) toggle ;;
  status) systemctl --user status "$unit" --no-pager -n 5 || true ;;
  *) printf 'usage: %s {start|stop|restart|toggle|status}\n' "${0##*/}" >&2; exit 2 ;;
esac
