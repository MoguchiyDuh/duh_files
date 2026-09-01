# Minimal Rebuild Instructions

This directory is intentionally not a full installer. It is a compact state snapshot for an AI agent or experienced human to rebuild the machine with judgment.

Do not blindly overwrite machine-specific files. Inspect first, adapt paths, and preserve secrets.

## Goal

Recreate the working environment from:

- package inventories
- stowed dotfiles
- selected system config candidates
- manually restored encrypted secrets

## Files

- `pkg-pacman.txt`: installable aggregate of selected official Arch packages
- `pkg-aur.txt`: installable aggregate of selected AUR/foreign packages
- `packages/`: structured package inventories by role
- `packages/dropped-explicit-deps.txt`: packages intentionally omitted from aggregates because they are generic dependency libraries/debug packages
- `language-tools/`: global npm/cargo/uv/pipx/rustup/go tool inventories
- `pkg-flatpak.txt`: Flatpak application IDs
- `systemd-enabled.txt`: enabled system services
- `systemd-user-enabled.txt`: enabled user services
- `etc-restore-candidates.txt`: system config files worth inspecting/restoring
- `etc/`: verbatim mirror of the tracked `/etc` files listed in `etc-restore-candidates.txt`. Layout mirrors real paths (`etc/sysctl.d/99-zram.conf` -> `/etc/sysctl.d/99-zram.conf`). Machine-specific files (`etc/fstab`, `etc/hostname`) are stored for reference only and MUST be adapted, never copied blindly (they contain this machine's disk UUIDs / hostname).
- `machine.txt`: source-machine metadata
- `power-management.md`: suspend fix and hibernation safeguard notes
- `screen-recording.md`: Nvidia recording keybind, output, and VLC decoder notes
- `clash-verge-v2rayn-profile.txt`: sanitized manual Clash Verge profile template

## Rebuild Flow

1. Install Arch normally.
2. Create the user and add needed groups such as `wheel`, `docker`, `video`, `input` as appropriate.
3. Enable sudo for the user.
4. Install base tooling:

```bash
sudo pacman -S --needed git base-devel stow
```

5. Clone this repo:

```bash
git clone <repo-url> ~/duh_files
cd ~/duh_files
```

6. Review structured package groups:

```bash
find setup_all/packages -maxdepth 3 -type f -print
```

7. Install official packages:

```bash
sudo pacman -Syu
sudo pacman -S --needed - < setup_all/pkg-pacman.txt
```

The aggregate is generated from `setup_all/packages/official/*.txt` and intentionally excludes packages listed in `setup_all/packages/dropped-explicit-deps.txt`.

8. Install an AUR helper manually, then install AUR packages after reviewing the list:

```bash
paru -S --needed - < setup_all/pkg-aur.txt
```

9. Restore language/tool-manager globals after runtimes are installed:

```bash
cat setup_all/language-tools/README.md
```

Install only tools that still make sense.

10. Install Flatpak apps if Flatpak is used:

```bash
while read -r app; do flatpak install -y flathub "$app"; done < setup_all/pkg-flatpak.txt
```

11. Stow dotfiles from `~/duh_files/dotfiles`:

```bash
cd ~/duh_files/dotfiles
stow zsh kitty ghostty hypr waybar tmux matugen swaync walker elephant systemd starship fastfetch gtk qt5 nvim
```

Only stow directories that make sense on the target machine.

Clash Verge profiles are not stowed or installed automatically. Review and import `setup_all/clash-verge-v2rayn-profile.txt` manually, replacing its placeholder connection values with private values from an encrypted source.

12. Review `/etc` candidates:

Most tracked files have a verbatim copy under `setup_all/etc/`. Diff the stored
copy against the live system before deciding to restore:

```bash
cd ~/duh_files/setup_all
while read -r file; do
    src="etc/${file#/etc/}"
    [ -f "$src" ] || { echo "NOT STORED: $file"; continue; }
    diff -q "$src" "$file" >/dev/null 2>&1 && echo "OK (same): $file" || echo "REVIEW: $file"
done < etc-restore-candidates.txt
```

Safe to copy verbatim on a fresh install: `zram-generator.conf` (16 GiB zstd
zram0), both `sysctl.d/*`, `modules-load.d/*`, `mkinitcpio.conf`,
`default/grub`, `locale.conf`, `locale.gen`, `vconsole.conf`, `hosts`,
`pacman.conf`, `sleep.conf.d/disable-hibernation.conf`,
`systemd/system/systemd-suspend.service.d/override.conf`, and both
`udev/rules.d/90-*.rules` (wake-source fixes; see `power-management.md`).

Must be ADAPTED, never copied blindly: `fstab` (disk UUIDs) and `hostname`.
After copying `mkinitcpio.conf` or `default/grub`, regenerate: `mkinitcpio -P`
and `grub-mkconfig -o /boot/grub/grub.cfg`.

13. Re-enable services selectively:

```bash
sudo systemctl enable --now docker.service
sudo systemctl enable --now fstrim.timer
sudo systemctl enable --now systemd-oomd.service
systemctl --user enable --now pipewire.service pipewire-pulse.service wireplumber.service
```

Use `systemd-enabled.txt` and `systemd-user-enabled.txt` as references, not commands to execute blindly.

Power-management state is machine-specific. Read `setup_all/power-management.md` before enabling suspend/hibernate behavior.

14. Restore secrets from encrypted backup only:

- SSH keys
- GPG/age keys
- real proxy/VPN configs
- password manager exports
- `.env` files

Never commit secrets to this repo.

15. Validate:

```bash
systemctl --failed
systemctl --user --failed
stow -n <package>
```

## Notes

- Prefer recreating caches and build artifacts instead of backing them up.
- Browser profiles, Docker volumes, media, models, and project dependencies are not part of this minimal system snapshot.
- For real private backups, use encrypted `borg`, `restic`, `age`, or `gpg` outside this repo.
