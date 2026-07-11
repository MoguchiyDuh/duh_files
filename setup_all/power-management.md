# Power Management

Machine-specific state for this Arch/Hyprland desktop (Ryzen 7 5700X, RTX 3060 Ti,
`nvidia-open-dkms`, Wayland).

## NVIDIA suspend/resume

Suspend uses S3/deep sleep and is known-good on this machine.

Two pieces are required for a *correct* resume, not just a working-looking one:

1. Systemd services (VRAM save/restore hooks):

   ```bash
   sudo systemctl enable nvidia-suspend.service nvidia-resume.service
   sudo systemctl enable disable-acpi-wakeup-gpp0.service
   ```

2. Driver options in `/etc/modprobe.d/nvidia-power-management.conf`
   (mirrored in `setup_all/etc/modprobe.d/`):

   ```
   options nvidia NVreg_PreserveVideoMemoryAllocations=1 NVreg_TemporaryFilePath=/var/tmp
   options nvidia_drm modeset=1 fbdev=1
   ```

   - `NVreg_PreserveVideoMemoryAllocations=1` saves *all* VRAM on suspend and
     restores it on resume. Without it the nvidia-suspend/resume services are
     effectively useless: resume under GPU load risks a black screen or
     corrupted framebuffers. This is the fix for the previously-latent bug where
     suspend only "worked" because the GPU was idle at test time.
   - `NVreg_TemporaryFilePath=/var/tmp` puts the VRAM dump on disk (ext4) instead
     of the default `/tmp`, which is tmpfs (RAM). Recommended by the Arch Wiki
     and the NVIDIA README.
   - `nvidia_drm modeset=1 fbdev=1` set explicitly. `fbdev=1` is mandatory for
     Wayland on kernel >= 6.11; do not rely on the driver default.

   No initramfs regeneration is needed: these options are not in the
   `mkinitcpio.conf` `MODULES=` array, so they load at normal module init.
   Changes take effect on the next reboot.

`disable-acpi-wakeup-gpp0.service` disables `GPP0` from `/proc/acpi/wakeup` at
boot. On this board `GPP0` maps to `0000:00:01.1`, the PCIe bridge to the NVMe
SSD, and caused immediate wake after successful S3 suspend. Keep keyboard USB
wake enabled; the keyboard was tested and was not the root cause.

## Idle escalation (hypridle)

`~/.config/hypr/hypridle.conf` implements a progressive, macOS/Windows-style
"balanced, plugged-in" escalation. Each visible stage restores itself on
activity, and the screen is locked *before* the display turns off so waking
never reveals the unlocked desktop.

| Stage        | Timeout   | Action                                           |
| ------------ | --------- | ------------------------------------------------ |
| notify       | 8 min     | warning toast                                    |
| dim          | 9 min 50s | `idle-dim.sh dim` (hardware backlight/DDC + LEDs) |
| lock         | 10 min    | `loginctl lock-session`                          |
| display off  | 10 min    | `hyprctl dispatch dpms off` (1s after lock)      |
| suspend      | 30 min    | `power.sh suspend` (honours awake mode + gating) |

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
pauses the whole idle escalation. Intended to be wired to a coffee-cup toggle in
the top bar later.

## Hibernate safeguard

Hibernate is intentionally disabled on this machine and is **not** meant to work
here. Blockers (all still true):

- no valid kernel `resume=` parameter
- no mkinitcpio `resume` hook
- disk swap is too small for 31 GiB RAM (2 GiB swapfile only)
- zram swap cannot be used for hibernation resume

Enforced in two places:

```bash
sudo install -Dm0644 setup_all/etc/systemd/sleep.conf.d/disable-hibernation.conf \
    /etc/systemd/sleep.conf.d/disable-hibernation.conf
```

and `power.sh`, whose `check_hibernate` refuses UI-triggered hibernation so it
fails safely.

Note: `NVreg_PreserveVideoMemoryAllocations=1` is known to break
resume-from-*hibernate* on some setups. Since only S3 suspend is used here, `=1`
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
