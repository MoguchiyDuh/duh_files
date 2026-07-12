#!/usr/bin/env bash

set -euo pipefail

pidfile="${XDG_RUNTIME_DIR:-/tmp}/recording.pid"
outdir="${HOME}/Videos/Screenshots"
monitor="HDMI-A-1"
mkdir -p "$outdir"

stop() {
    local pid
    pid=$(cat "$pidfile" 2>/dev/null || true)
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        kill -INT "$pid" 2>/dev/null || true
        wait "$pid" 2>/dev/null || true
        notify-send "Recording stopped" "Saved to $outdir" -t 3000
    fi
    rm -f "$pidfile"
    exit 0
}

if [[ -f "$pidfile" ]]; then
    stop
fi

outfile="$outdir/recording_$(date +%Y%m%d_%H%M%S).mp4"

gpu-screen-recorder -w "$monitor" -f 60 -k h264 -o "$outfile" &
pid=$!
sleep 0.2

if ! kill -0 "$pid" 2>/dev/null; then
    notify-send "Recording failed" "GPU Screen Recorder could not start" -t 3000
    exit 1
fi

echo "$pid" > "$pidfile"
notify-send "Recording started" "Output: $outfile" -t 3000
