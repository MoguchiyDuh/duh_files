# Waybar

Compact Hyprland status bar with native Waybar modules, small shell adapters,
and three Rust daemons for data that native modules do not expose well.

## Install

Stow the configuration, build the daemons, then populate the optional memory
hardware cache:

```bash
cd ~/duh_files/dotfiles
stow waybar

./waybar/hardwarebar-src/build.sh
./waybar/soundbar-src/build.sh
./waybar/netbar-src/build.sh
./waybar/.config/waybar/scripts/setup-hardware.sh
```

The build scripts install `hardwarebar`, `soundbar`, and `netbar` under
`~/.local/bin`. `hardwarebar-src/build.sh` grants
`cap_dac_read_search=ep` when an unreadable RAPL energy counter exists, which
allows CPU power reporting without running the daemon as root.

`setup-hardware.sh` uses `dmidecode` once and caches the DIMM title at
`$XDG_CACHE_HOME/waybar/memory-title`, falling back to
`~/.cache/waybar/memory-title`. Runtime modules never need root access.

## Architecture

| Component | Update model | Purpose |
| --- | --- | --- |
| `hardwarebar cpu` | 5-second sysfs/procfs sampling | CPU utilization, clocks, temperature, power, topology, process count, and uptime |
| `hardwarebar memory` | 5-second procfs sampling | RAM and swap utilization with cached DIMM identity |
| `hardwarebar gpu` | 5-second sampling | NVIDIA metrics through `nvidia-smi`, AMD metrics through sysfs, hidden when unsupported |
| `soundbar sink` | PulseAudio subscription | Default output volume, mute state, and per-application stream levels |
| `soundbar source` | PulseAudio subscription | Default input volume, mute state, and active-recording detection |
| `netbar` | 5-second sampling | Primary connection, Wi-Fi signal and band, traffic rates, secondary interfaces, VPNs, and proxy state |
| `hyprland/language` | Hyprland IPC | Active keyboard layout without polling or a hardware-specific keyboard name |
| `swaync-client -swb` | SwayNC subscription | Notification count and DND state |
| `custom/cliphist` | `RTMIN+2` | Signal-driven clipboard history count |
| `custom/awake`, `custom/profile` | `RTMIN+1` plus 30-second fallback | Non-default idle-inhibition and power-profile state |
| `custom/weather` | Hourly HTTP request | Compact wttr.in status and monospace report |

`restart-interval` on persistent custom modules is only a crash recovery
mechanism. `soundbar` and SwayNC updates are event-driven rather than polled.

## Integration

The clipboard watcher must pipe both MIME classes through `clipboard.sh` so a
successful store signals Waybar immediately:

```ini
exec-once = wl-paste --type text --watch ~/.config/waybar/scripts/clipboard.sh store
exec-once = wl-paste --type image --watch ~/.config/waybar/scripts/clipboard.sh store
```

Power state changes signal `RTMIN+1`; clipboard changes signal `RTMIN+2`.
`RTMIN+3` is currently free. These are Waybar's relative real-time signal
numbers, matching each custom module's `signal` field.

The language module intentionally uses `"format": "{}"` with `format-en` and
`format-ru`. Waybar 0.15 passes override values as a positional fmt argument,
so `{shortDescription}` fails when overrides are present. That version also
ignores `tooltip-format` for `hyprland/language`.

## Dependencies

Core runtime dependencies are Waybar, Hyprland, SwayNC, PipeWire Pulse or
PulseAudio, NetworkManager, `iproute2`, `jq`, `curl`, `cliphist`, `wl-clipboard`,
and Nerd Fonts. Module actions additionally use AnyRun, `pavucontrol`,
`blueman-manager`, `nm-connection-editor`, LACT, `btop`, `kitty`, and `wlogout`.

Building requires the Rust toolchain and PulseAudio development libraries for
`libpulse-binding`.
