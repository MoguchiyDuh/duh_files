# duh_files

Personal dotfiles, scripts, and minimal rebuild state.

This repo is not a full system image and no longer contains an automated distro provisioner. The intended model is: install a clean OS, install packages from inventories, run GNU Stow, then let a human or AI agent handle machine-specific quirks.

## Structure

```text
duh_files/
├── dotfiles/     # stow packages for user configs
├── scripts/      # personal utility scripts
└── setup_all/    # minimal rebuild instructions and inventories
```

## Dotfiles

Configs are organized as GNU Stow packages under `dotfiles/`.

Common packages:

```text
zsh
kitty
hypr
waybar
wallust
wlogout
zed
qt5
fastfetch
nvim
```

Deploy from the repo root like this:

```bash
cd ~/duh_files/dotfiles
stow zsh kitty hypr waybar tmux wallust wlogout zed gtk qt5 fastfetch nvim
```

Preview first when unsure:

```bash
stow -n -v <package>
```

## Minimal Rebuild

`setup_all/` stores a small rebuild snapshot:

- `README.md`: rebuild instructions for an AI agent or experienced human
- `pkg-pacman.txt`: installable aggregate of selected official Arch packages
- `pkg-aur.txt`: installable aggregate of selected AUR/foreign packages
- `packages/`: package groups by role, plus documented dependency/debug drops
- `pkg-flatpak.txt`: Flatpak apps
- `systemd-enabled.txt`: enabled system services reference
- `systemd-user-enabled.txt`: enabled user services reference
- `language-tools/`: global npm/cargo/uv/pipx/rustup/go tool inventories
- `etc-restore-candidates.txt`: `/etc` files worth reviewing/recreating
- `machine.txt`: source-machine metadata

Basic rebuild flow:

```bash
sudo pacman -S --needed git base-devel stow
git clone <repo-url> ~/duh_files
cd ~/duh_files
sudo pacman -Syu
sudo pacman -S --needed - < setup_all/pkg-pacman.txt
```

Then install AUR packages after review:

```bash
paru -S --needed - < setup_all/pkg-aur.txt
```

Then stow selected config packages:

```bash
cd ~/duh_files/dotfiles
stow <packages>
```

Use `setup_all/README.md` for the full checklist.

## Secrets

No real secrets belong in this repo.

Keep these outside git, encrypted with `age`, `gpg`, `borg`, or `restic`:

- SSH keys
- GPG/age keys
- real proxy/VPN configs
- password manager exports
- API tokens
- `.env` files
- browser profiles if needed

Sanitized templates are allowed. Real credentials are not.

## What This Repo Is For

- Fast Arch rebuilds
- Portable terminal/editor/Hyprland setup
- Package inventory tracking
- Config templates
- Personal scripts

## What This Repo Is Not For

- Full disk backups
- Browser/session/cache backups
- Docker volumes
- media files
- language build artifacts
- secrets

Use encrypted backup tooling for private state and large data.
