# GRUB Fixer (`fix-grub.sh`) Guide

A specialized bash script for repairing dual-boot configurations on Arch Linux systems where Windows or other OS entries have disappeared from the GRUB menu.

**Scope:** This script is designed for `pacman`-based systems (Arch Linux, Manjaro, EndeavourOS).

---

## Workflow

**Usage:** `sudo ./fix-grub.sh`

The script performs the following automated steps:

1.  **Privilege Check**: Verifies it is running as root.
2.  **Backup**: Creates a timestamped backup of the existing `/etc/default/grub` configuration file (e.g., `grub.backup.20240124_...`).
3.  **OS Prober Activation**:
    - Checks `/etc/default/grub` for `GRUB_DISABLE_OS_PROBER`.
    - If set to `true`, it changes it to `false`.
    - If commented out, it uncomments and sets it to `false`.
    - If missing, it appends the line `GRUB_DISABLE_OS_PROBER=false`.
4.  **Detection Scan**: Runs the `os-prober` utility to identify other operating systems on connected drives.
5.  **Configuration Regeneration**: Executes `grub-mkconfig -o /boot/grub/grub.cfg` to apply changes and update the boot menu.

## Requirements

- **Root Access**: Must be run with `sudo`.
- **Dependencies**: The `os-prober` package must be installed. The script will warn if it is missing.

