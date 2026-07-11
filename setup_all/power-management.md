# Power Management

Machine-specific state for this Arch/Hyprland desktop.

## Suspend

Suspend uses S3/deep sleep and is known-good on this machine.

Required services:

```bash
sudo systemctl enable nvidia-suspend.service nvidia-resume.service
sudo systemctl enable disable-acpi-wakeup-gpp0.service
```

`disable-acpi-wakeup-gpp0.service` disables `GPP0` from `/proc/acpi/wakeup` at boot. On this board `GPP0` maps to `0000:00:01.1`, the PCIe bridge to the NVMe SSD, and caused immediate wake after successful S3 suspend.

Keep keyboard USB wake enabled. The keyboard was tested and was not the root cause.

## Hibernate Safeguard

Hibernate is intentionally disabled on this machine.

Current blockers:

- no valid kernel `resume=` parameter
- no mkinitcpio `resume` hook
- disk swap is too small for 31 GiB RAM
- zram swap cannot be used for hibernation resume

Install the systemd sleep drop-in:

```bash
sudo install -Dm0644 setup_all/systemd/sleep.conf.d/disable-hibernation.conf /etc/systemd/sleep.conf.d/disable-hibernation.conf
```

The rofi power script also refuses `hibernate` so UI-triggered hibernation fails safely.

Re-enable hibernation only after creating a real disk swap target large enough for RAM, adding correct `resume=` kernel parameters, adding the mkinitcpio `resume` hook, and validating resume from disk.
