# duh_files

Multi-distro dotfiles manager and auto-installer using GNU Stow.

## Structure

```
~/duh_files/
├── dotfiles/          # Stow packages (symlinked to ~)
│   ├── zsh/           # .zshrc, .p10k.zsh
│   ├── nvim/          # .config/nvim/
│   ├── tmux/          # .config/tmux/
│   ├── fastfetch/     # .config/fastfetch/
│   └── [Arch only]:
│       ├── hypr/      # .config/hypr/
│       ├── waybar/    # .config/waybar/
│       ├── kitty/     # .config/kitty/
│       └── rofi/      # .config/rofi/
│
├── scripts/           # Custom scripts (linked to ~/.local/bin/duh-*)
│   ├── ytdl.py
│   ├── spotify-cli.py
│   ├── claude_storage_manager.py
│   └── ...
│
└── setup_all/         # Auto-installer for all distros
    ├── main.py        # Entry point
    ├── arch.py        # Arch Linux packages
    ├── debian.py      # Debian/Ubuntu packages
    ├── fedora.py      # Fedora packages
    └── macos.py       # macOS packages
```

## Quick Start

### Install packages and setup dotfiles
```bash
cd ~/duh_files/setup_all
python3 main.py          # Check → Install → Stow → Link scripts
python3 main.py --dry-run  # Check only
python3 main.py -y       # Auto-approve
```

### Manually stow dotfiles
```bash
cd ~/duh_files/dotfiles
stow zsh nvim tmux fastfetch  # Common
stow hypr waybar kitty rofi   # Arch only
```

### Manually link scripts
```bash
ln -sf ~/duh_files/scripts/ytdl.py ~/.local/bin/duh-ytdl
ln -sf ~/duh_files/scripts/spotify-cli.py ~/.local/bin/duh-spotify-cli
# etc...
```

## Features

- **Multi-distro support**: Arch, Debian/Ubuntu, Fedora, macOS
- **Idempotent**: Safe to run multiple times, skips installed packages
- **GNU Stow**: Dotfiles are symlinked (easy to update via git)
- **Auto-backup**: Conflicting files backed up to `.backups/<timestamp>/`
- **Script linking**: All scripts auto-linked to `~/.local/bin/duh-*`
- **Defensive checking**: Multi-layered package detection (command, path, version)

## Packages Installed

### Core (all distros)
- **Dev**: base-devel, git, curl, cmake, ninja, clang
- **Terminal**: zsh, oh-my-zsh, powerlevel10k, tmux, stow
- **CLI tools**: gh, zoxide, fzf, eza, bat, fd, ripgrep, btop, fastfetch, jq, yq, nnn, direnv
- **Modern utils**: dust, duf, hyperfine
- **Archives**: zip, unzip, p7zip
- **Tools**: docker, redis, postgres
- **Languages**: python, node, npm, go, rust (rustup), uv
- **Late-bound**: tealdeer, lazygit, lazydocker, lazysql, neovim (from source)

### Arch Linux only
- **Hyprland ecosystem**: hyprland, waybar, kitty, rofi-wayland, swaync, hypridle, hyprlock, wallust
- **Wayland tools**: wl-clipboard, cliphist, grim, slurp, hyprshot, hyprpicker, swww, wlogout
- **OCR**: tesseract + eng/rus language data
- **System**: wireplumber, playerctl, brightnessctl, libnotify
- **Theming**: qt5ct, kvantum
- **Apps**: nautilus, flatpak
- **AUR**: yay, hyprshot

## Notes

- Arch configs (hypr/waybar/kitty/rofi) only stowed on Arch Linux
- Backups stored in `.backups/` (gitignored)
- Scripts must be `.py` or `.sh` to be linked
- Stow uses `--adopt` fallback for conflict resolution

---

**Updated**: 2026-01-18
