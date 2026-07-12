# Screen Recording

Hyprland uses `gpu-screen-recorder` for full-screen recording on Nvidia.

- `Shift+Print`: start/stop recording
- Output: `~/Videos/Screenshots/recording_YYYYMMDD_HHMMSS.mp4`
- Video: 60 FPS H.264 through NVENC
- Target monitor: `HDMI-A-1`

The toggle script is stowed at `~/.config/hypr/scripts/record.sh`. Update its
`monitor` value if the output name changes; inspect available names with:

```bash
hyprctl monitors
```

VLC needs `vlc-plugin-ffmpeg` to decode the H.264 recordings. It is included
in the official package inventory.

This configuration records video only. Add an audio input to `record.sh` if
desktop or microphone audio is needed.
