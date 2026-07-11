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
- `machine.txt`: source-machine metadata
- `power-management.md`: suspend fix and hibernation safeguard notes
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
stow zsh kitty hypr waybar rofi tmux wallust wlogout zed gtk qt5 fastfetch nvim clash-verge
```

Only stow directories that make sense on the target machine.

Clash Verge profiles are not stowed or installed automatically. Review and import `setup_all/clash-verge-v2rayn-profile.txt` manually, replacing its placeholder connection values with private values from an encrypted source.

12. Review `/etc` candidates:

```bash
while read -r file; do test -e "$file" && echo "$file"; done < ~/duh_files/setup_all/etc-restore-candidates.txt
```

Restore these manually from backups or recreate them. Do not copy them blindly across machines.

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
