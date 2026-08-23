# Power Management

Machine-specific state for this Arch/Hyprland desktop (Ryzen 7 5700X, RTX 3060 Ti,
`nvidia-open-dkms`, Wayland).

## NVIDIA suspend/resume

Suspend uses S3/deep sleep and is known-good on this machine.

Three pieces are required for a _correct_ resume, not just a working-looking one:

1. VRAM preservation (driver options). As of nvidia-open 610 the right options
   are already active on this machine — verify with
   `grep -E 'Preserve|Temporary|SuspendNotifiers' /proc/driver/nvidia/params`:

   - `PreserveVideoMemoryAllocations: 1` comes from
     `/usr/lib/modprobe.d/gsr-nvidia.conf`, shipped by the
     gpu-screen-recorder NVIDIA package. It saves _all_ VRAM on suspend and
     restores it on resume; without it, resume under GPU load risks a black
     screen or corrupted framebuffers.
   - `TemporaryFilePath: "/var/tmp"` (VRAM dump on ext4, not tmpfs) and
     `UseKernelSuspendNotifiers: 1` (kernel-driven VRAM save/restore, so the
     old `nvidia-suspend.service`/`nvidia-resume.service` pair is not needed)
     are driver defaults in this version.
   - `modeset=1 fbdev=1` for `nvidia_drm` are default-on here; `fbdev=1` is
     mandatory for Wayland on kernel >= 6.11.

   The old `/etc/modprobe.d/nvidia-power-management.conf` is gone; do not
   recreate it — it would only duplicate the shipped options.

2. Wake-source udev rules (see next section).

3. Session freeze on suspend (see below).

`enable nvidia-suspend.service`/`nvidia-resume.service` are no longer part of
this setup: kernel suspend notifiers replaced them.

## Wake sources (udev rules)

Phantom wake after S3 was caused by `GPP0` (`0000:00:01.1`, the PCIe bridge to
the NVMe SSD) firing spurious PME events — a known Gigabyte B550 quirk. Fixed
persistently with a udev rule instead of the old
`disable-acpi-wakeup-gpp0.service`:

- `/etc/udev/rules.d/90-nvme-bridge-gpp0-nowake.rules`:
  `ACTION=="add", SUBSYSTEM=="pci", KERNELS=="0000:00:01.1", ATTR{power/wakeup}="disabled"`
- `/etc/udev/rules.d/90-logitech-g502-wake.rules`: keeps the G502 mouse
  wake-enabled (wakeup on its USB port is explicitly `enabled`)

Keyboard (G512) wake stays at the kernel default (`enabled`); it was tested and
was not the wake source. Verify with `cat /proc/acpi/wakeup | grep GPP0`
(must show `*disabled`).

Both rules are mirrored in `setup_all/etc/udev/rules.d/`.

## Session freeze on suspend

nvidia-utils ships
`/usr/lib/systemd/system/systemd-suspend.service.d/10-nvidia-no-freeze-session.conf`
setting `SYSTEMD_SLEEP_FREEZE_USER_SESSIONS=false`. With sessions unfrozen,
wayland clients resume concurrently with the GPU driver restore and race it —
on this machine hyprlock lost a pending DMABUF resource, never repainted, and
showed a translucent frozen lockscreen (desktop blended through) until a hard
reset.

Fixed by re-enabling the systemd default:
`/etc/systemd/system/systemd-suspend.service.d/override.conf` sets
`SYSTEMD_SLEEP_FREEZE_USER_SESSIONS=true` (drop-in filename sorts after
nvidia's, so it wins). Sessions now freeze before sleep and thaw after the
driver is fully restored. Mirrored in `setup_all/etc/systemd/system/`.

## Idle escalation (hypridle)

`~/.config/hypr/hypridle.conf` implements a progressive, macOS/Windows-style
"balanced, plugged-in" escalation. Each visible stage restores itself on
activity, and the screen is locked _before_ the display turns off so waking
never reveals the unlocked desktop.

| Stage       | Timeout   | Action                                            |
| ----------- | --------- | ------------------------------------------------- |
| notify      | 8 min     | warning toast                                     |
| dim         | 9 min 50s | `idle-dim.sh dim` (hardware backlight/DDC + LEDs) |
| lock        | 10 min    | `loginctl lock-session`                           |
| display off | 10 min    | dpms off via Lua dispatch (1s after lock)         |
| suspend     | 30 min    | `power.sh suspend` (honours awake mode + gating)  |

hypridle itself runs as the systemd user unit `hypridle.service`. Display power
is toggled with `hyprctl repl 'hl.dispatch(hl.dsp.dpms("off"))'` (and `"on"`
for `after_sleep_cmd`/`on-resume`): since Hyprland 0.56 configs are Lua and the
old string form `hyprctl dispatch dpms on` fails to parse two-word dispatcher
args. `dpms` is exposed as `hl.dsp.dpms("on"|"off"|"toggle")`.

Timings mirror the Windows "Balanced, plugged-in" plan: display off at 10 min,
sleep at 30 min, with a short dim ~10 s before the display goes dark.

**Dimming is hardware-only** (`idle-dim.sh`), by design, so it actually reduces
power draw:

1. sysfs backlight (`/sys/class/backlight/*`) via `brightnessctl` — laptop panels
2. DDC/CI via `ddcutil` — external monitors that support it (**active on this
   machine**: LG ULTRAWIDE on `/dev/i2c-1`, VCP 2.1)

If neither exists, display dimming is **skipped**. Software gamma dimming
(`wl-gammarelay-rs`) was deliberately removed: it only darkens pixel values, the
backlight stays at full, so it saves no power. The dim level is power-source
aware (~5% on battery, ~30% on AC). Keyboard/NIC LEDs are also dimmed as a
cosmetic idle cue.

### DDC/CI setup

```bash
sudo pacman -S ddcutil i2c-tools
echo i2c-dev | sudo tee /etc/modules-load.d/i2c-dev.conf   # load the module at boot
sudo modprobe i2c-dev                                       # load it now
ddcutil detect                                              # verify the monitor responds
```

No `i2c` group membership is needed: the shipped udev rule
(`/usr/lib/udev/rules.d/60-ddcutil-i2c.rules`) tags `i2c-dev` devices with
`uaccess`, granting the active session user an ACL on `/dev/i2c-*`.

`idle-dim.sh` detects the I2C bus once via `ddcutil detect` (~400 ms) and caches
it in `$XDG_RUNTIME_DIR/idle-dim/ddc-bus`; subsequent brightness reads/writes use
`ddcutil --bus N` (~175 ms) and only re-detect if the cached bus stops
responding. `ddcutil detect` over NVIDIA can be flaky/slow, hence the cache.

The `sleep 1` before `dpms off` guards the DPMS-vs-lock race that can otherwise
freeze Hyprland.

## Awake mode (PowerToys-Awake / caffeinate equivalent)

`power.sh awake {enable|disable|toggle|status}` runs a transient user unit
`awake-inhibit.service` holding `systemd-inhibit --what=idle:sleep --mode=block`.
Because hypridle has `ignore_systemd_inhibit = false`, an active inhibitor
pauses the whole idle escalation. Wired to the waybar coffee pill
(`status.sh awake`, click toggles, RTMIN+1 signal refresh).

## Hibernate safeguard

Hibernate is intentionally disabled on this machine and is **not** meant to work
here. Blockers (all still true):

- no valid kernel `resume=` parameter
- no mkinitcpio `resume` hook
- the only swap is 16 GiB zram (`zram-generator`, compressed in RAM), which
  cannot back hibernation; no disk swap exists

Enforced in two places:

```bash
sudo install -Dm0644 setup_all/etc/systemd/sleep.conf.d/disable-hibernation.conf \
    /etc/systemd/sleep.conf.d/disable-hibernation.conf
```

and `power.sh`, whose `check_hibernate` refuses UI-triggered hibernation so it
fails safely.

Note: `NVreg_PreserveVideoMemoryAllocations=1` is known to break
resume-from-_hibernate_ on some setups. Since only S3 suspend is used here, `=1`
is safe. Revisit this if hibernation is ever enabled.

Re-enable hibernation only after creating a real disk swap target >= RAM, adding
correct `resume=`/`resume_offset=` kernel parameters, adding the mkinitcpio
`resume` hook, and validating resume from disk.

## Power profiles (eco/balanced/performance)

The Windows power-mode slider / macOS Low Power Mode equivalent, via
**`power-profiles-daemon`** (official `extra/`):

```bash
sudo pacman -S power-profiles-daemon
sudo systemctl enable --now power-profiles-daemon.service
```

Driven through `power.sh`:

```
power.sh profile eco          # -> power-saver  (EPP: power)
power.sh profile balanced     # -> balanced     (EPP: balance_performance)
power.sh profile performance  # -> performance  (EPP: performance)
power.sh profile status
power.sh profile cycle        # eco -> balanced -> performance -> eco
```

ppd drives `amd-pstate-epp` directly (this CPU uses the `amd-pstate-epp` scaling
driver); the EPP mapping above is verified live. It works on desktops with no
battery — `eco` still lowers EPP, clocks, heat and fan noise.

Notes / pitfalls:

- ppd does **not** auto-switch on AC/battery; it holds the last set profile. An
  optional udev-triggered auto-switch could be added later.
- Do not run more than one ppd-compatible daemon: `power-profiles-daemon`,
  `tuned-ppd`, and `tlp-pd` conflict. `tuned` + `tuned-ppd` is a heavier
  alternative only if per-profile disk/network/sysctl tuning is wanted.
- ppd does not touch the NVIDIA dGPU. `nvidia-smi -pl` is not worth wiring in for
  a desktop 3060 Ti.
- Kernel >= 6.15 has an `amd_dynamic_epp` auto AC/DC EPP feature; leave it
  disabled (default) so it does not race ppd.
