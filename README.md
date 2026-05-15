# duh_files

A multi-distribution configuration management system and automated environment provisioner for Linux (Arch, Debian, Fedora) and macOS. This project utilizes GNU Stow for symlink management and a custom Python-based installation engine to ensure idempotent system setup.

## Key Features

- **Multi-Distribution Support**: Unified provisioning logic for Arch Linux, Debian/Ubuntu, Fedora, and macOS.
- **Idempotent Execution**: Operations are safe to repeat; existing packages and configurations are detected to prevent redundant actions.
- **Atomic Configuration**: Dotfiles are managed via GNU Stow, allowing for precise, modular symbolic linking.
- **Automated Backup**: Pre-existing configurations are automatically archived to a timestamped directory before deployment to prevent data loss.
- **Dynamic Linking**: Executable scripts are automatically discovered and linked to the user's local binary path.
- **Defensive Integrity Checks**: Comprehensive verification of system state using command availability, filesystem paths, and package manager queries.

## System Architecture

The project is organized into three distinct operational layers:

### 1. Installation Engine (setup_all/)

The core installation logic is implemented in Python and manages package dependencies across supported platforms.

- **Defensive Detection**: Verification of package status is performed through a three-stage process: binary path resolution, filesystem existence checks, and native package manager queries.
- **Platform Abstraction**: An abstract base class defines the required interface for distribution-specific installers.
- **State Management**: All installation tasks include pre-execution checks to prevent redundant operations.

### 2. Configuration Management (dotfiles/)

Configurations are deployed using GNU Stow, which manages symlinks from the repository to the user's home directory.

- **Package Modularity**: Each subdirectory within the `dotfiles` directory represents an atomic configuration unit.
- **Conflict Resolution**: The system detects existing files at target locations and automatically moves them to a backup location.
- **Conditional Deployment**: Platform-specific configurations (e.g., Hyprland) are only deployed on compatible systems.

### 3. Utility Suite (scripts/)

A collection of specialized Python and Shell utilities integrated into the user's environment via `~/.local/bin/duh-*`.

- **yt_manager.py**: Advanced YouTube synchronization tool. Features parallel downloads, local library scanning, and M3U playlist generation.
- **spotify-cli.py**: CLI interface for the Spotify API. Retrieves and formats track metadata from playlists and albums.
- **claude_storage_manager.py**: Interactive maintenance utility for the Claude CLI. Manages session history, cached agents, and storage artifacts.
- **ssh_tool.py**: Unified SSH security and automation suite for Linux (Debian, Arch, Fedora) and macOS; manages server hardening and bidirectional key exchange.
- **fix-grub.sh**: Diagnostic and repair script for GRUB bootloaders, specifically enabling `os-prober` for dual-boot setups.
- **crypt.sh**: OpenSSL wrapper for simplified AES-256 file encryption and decryption operations.

## Package Inventory

The system provisions a comprehensive suite of development and operational tools.

### Core Environment (All Platforms)

- **Development**: base-devel, git, curl, cmake, ninja, clang
- **Terminal**: zsh, oh-my-zsh, powerlevel10k, tmux, stow
- **CLI Utilities**: gh, zoxide, fzf, eza, bat, fd, ripgrep, btop, fastfetch, jq, yq, nnn, direnv
- **System Analysis**: dust, duf, hyperfine
- **Archival**: zip, unzip, p7zip
- **Infrastructure**: docker, redis, postgres
- **Runtimes**: python (uv), nodejs (npm), go, rust (rustup)
- **Built from Source**: neovim, tealdeer, lazygit, lazydocker, lazysql

### Arch Linux Specific

- **Desktop Environment**: Hyprland, Waybar, Rofi-Wayland, SwayNC, Hypridle, Hyprlock
- **Wayland Utilities**: wl-clipboard, cliphist, grim, slurp, hyprshot, hyprpicker, swww, wlogout
- **System Services**: Wireplumber, Playerctl, Brightnessctl, Libnotify
- **Theming**: Wallust, Qt5ct, Kvantum
- **OCR**: Tesseract (Eng/Rus)
- **AUR Helpers**: yay

## Project Structure

```text
~/duh_files/
├── dotfiles/               # Managed configuration units
│   ├── zsh/                # Shell environment
│   ├── nvim/               # Neovim configuration
│   ├── tmux/               # Terminal multiplexer settings
│   ├── hypr/               # Tiling window manager configuration
│   └── wallust/            # Color scheme generation
│
├── scripts/                # Integrated utility scripts
│   ├── yt_manager.py       # YouTube synchronization utility
│   ├── spotify-cli.py      # Spotify metadata interface
│   └── ...
│
└── setup_all/              # Provisioning logic
    ├── main.py             # Execution entry point
    ├── base.py             # Abstract installer definitions
    ├── checker.py          # Dependency verification logic
    └── [distro].py         # Platform-specific implementations
```

## Operation

### Automated Provisioning

To initiate a full system setup:

```bash
cd ~/duh_files/setup_all
python3 main.py --yes
```

### Manual Configuration Deployment

To deploy specific configurations independently:

```bash
cd ~/duh_files/dotfiles
stow -v <package_name>
```

## Technical Notes

- **Configuration Scope**: Arch-specific configurations (hypr, waybar, kitty, rofi) are restricted to Arch Linux environments.
- **Backup Location**: Conflict resolution artifacts are stored in `.backups/` and are excluded from version control.
- **Script Constraints**: Only files with `.py` or `.sh` extensions in the `scripts/` directory are processed for linking.
- **Stow Behavior**: The system uses the `--adopt` strategy implicitly during manual conflict resolution scenarios described in the legacy documentation, though the automated installer handles backups explicitly.

---

## Neovim Configuration

Modern config rebuilt from scratch (May 2026). Located at `dotfiles/nvim/.config/nvim/`, symlinked to `~/.config/nvim`.

### Structure

```text
nvim/
├── init.lua                  # loads core.options, core.keymaps, core.lazy
└── lua/
    ├── core/
    │   ├── options.lua       # vim settings
    │   ├── keymaps.lua       # all keymaps
    │   └── lazy.lua          # lazy.nvim bootstrap, auto-loads lua/plugins/
    └── plugins/
        ├── ui.lua            # colorschemes, snacks, lualine, bufferline, which-key
        ├── editor.lua        # oil, treesitter, gitsigns, lazygit, flash, surround, autopairs, render-markdown
        ├── lsp.lua           # mason, lspconfig, blink.cmp
        └── format.lua        # conform, nvim-lint
```

### Plugin Stack

| Category | Plugin | Notes |
|---|---|---|
| Plugin manager | lazy.nvim | auto-loads all files in `lua/plugins/` |
| UI suite | snacks.nvim | dashboard, picker, notifier, indent, scratch, words |
| Colorscheme | kanagawa (default) | hot-switch via `<leader>ct`; also: tokyonight, catppuccin, onedark, rose-pine |
| Statusline | lualine | |
| Bufferline | bufferline.nvim | ordinal numbers, LSP diagnostics |
| File manager | oil.nvim | edit filesystem as buffer, `<C-n>` |
| Syntax | nvim-treesitter | nvim 0.12+: highlight/indent via built-in vim.treesitter |
| Git hunks | gitsigns.nvim | |
| Git UI | lazygit.nvim | `<leader>gg` |
| Jump nav | flash.nvim | `<leader>j` / `<leader>J` |
| Surround | nvim-surround | |
| Autopairs | nvim-autopairs | |
| Completion | blink.cmp | Rust-based, replaces nvim-cmp |
| LSP installer | mason + mason-lspconfig | |
| Formatter | conform.nvim | format on save |
| Linter | nvim-lint | lint on save/read/insert-leave |
| Markdown | render-markdown.nvim | |
| Which-key | which-key.nvim | |

### LSP Servers

| Server | Language |
|---|---|
| lua_ls | Lua |
| basedpyright | Python (uv/.venv auto-detect) |
| rust_analyzer | Rust (via rustup, not mason) |
| clangd | C/C++ |
| ts_ls | JS/TS |
| html | HTML |
| cssls | CSS |
| taplo | TOML |
| yamlls | YAML |

### Formatters / Linters

| Tool | Language | Via |
|---|---|---|
| stylua | Lua | mason |
| ruff | Python (format + lint) | mason |
| rustfmt | Rust | rustup |
| clang-format | C/C++ | mason |
| prettier | JS/TS/JSON/MD/YAML | mason |
| taplo | TOML | mason |
| eslint | JS/TS | mason |
| yamllint | YAML | mason |
| shfmt | Shell | brew |

### Key Keymaps

| Key | Action |
|---|---|
| `<leader>ff` | Find files |
| `<leader>fg` | Live grep |
| `<leader>fb` | Buffers |
| `<leader>fr` | Recent files |
| `<C-n>` | File explorer (oil) |
| `<leader>gg` | LazyGit |
| `<leader>ct` | Switch colorscheme |
| `<leader>cb` | Toggle transparency |
| `<leader>j` | Flash jump |
| `<leader>F` | Format buffer |
| `<S-h>` / `<S-l>` | Prev/next buffer |
| `<leader>bd` | Close buffer |

### Notes

- Theme + transparency state persisted to `~/.local/share/nvim/theme_state.json`
- `rust_analyzer` and `rustfmt` managed by rustup, not mason
- `shfmt` installed via `brew install shfmt`
- Backup of old config at `dotfiles/nvim/.config/nvim_backup_<timestamp>`

---

Updated: 2026-05-15
