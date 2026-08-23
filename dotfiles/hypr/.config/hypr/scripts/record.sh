#!/usr/bin/env bash
set -Eeuo pipefail

pidfile="${XDG_RUNTIME_DIR:-/tmp}/recording.pid"
outdir="$HOME/Videos/Screenshots"
mkdir -p "$outdir"

notify() {
  notify-send "$1" "$2" -t 3000 2>/dev/null || true
}

stop() {
  local pid comm
  pid=$(cat "$pidfile" 2>/dev/null || true)
  if [[ -n $pid ]]; then
    comm=$(ps -o comm= -p "$pid" 2>/dev/null || true)
    if [[ $comm == gpu-screen-rec* ]]; then
      kill -INT "$pid" 2>/dev/null || true
      wait "$pid" 2>/dev/null || true
      notify "Recording stopped" "Saved to $outdir"
    fi
  fi
  rm -f "$pidfile"
  exit 0
}

if [[ -f $pidfile ]]; then
  stop
fi

outfile="$outdir/recording_$(date +%Y%m%d_%H%M%S).mp4"
monitor=$(hyprctl -j monitors | jq -r '(map(select(.focused)) + .)[0].name')

gpu-screen-recorder -w "$monitor" -f 60 -k h264 -o "$outfile" &
pid=$!
sleep 0.3

if ! kill -0 "$pid" 2>/dev/null; then
  notify "Recording failed" "gpu-screen-recorder could not start"
  exit 1
fi

echo "$pid" > "$pidfile"
notify "Recording started" "Output: $outfile"
