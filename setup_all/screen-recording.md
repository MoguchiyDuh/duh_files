# Screen Recording

Hyprland uses `gpu-screen-recorder` for full-screen recording on Nvidia.

- `Shift+Print`: start/stop recording
- Output: `~/Videos/Screenshots/recording_YYYYMMDD_HHMMSS.mp4`
- Video: 60 FPS H.264 through NVENC
- Target monitor: auto-detected (focused monitor); override by editing
  `record.sh`

The toggle script is stowed at `~/.config/hypr/scripts/record.sh`. It detects
the target monitor at runtime via `hyprctl`; inspect available names with:

```bash
hyprctl monitors
```

VLC needs `vlc-plugin-ffmpeg` to decode the H.264 recordings. It is included
in the official package inventory.

This configuration records video only. Add an audio input to `record.sh` if
desktop or microphone audio is needed.
