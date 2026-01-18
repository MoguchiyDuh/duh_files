# Setup All

Automated, idempotent, multi-distro setup script (Arch, Debian/Ubuntu, Fedora, macOS).

## Features

- **Safe**: Checks status first, shows plan, asks before installing.
- **Idempotent**: Skips already installed packages.
- **Defensive**: Checks package managers, binaries, paths, and versions.
- **Dual-OS**: Auto-switches `.venv-wsl` / `.venv-win` via `.envrc`.

## Usage

```bash
# Interactive (Check → Plan → Approve → Install)
python3 main.py

# Auto-approve
python3 main.py --yes

# Dry-run (Check only)
python3 main.py --dry-run
```

## Included Packages

### Core Development

- **base-devel/build-essential**: Essential compilation tools (make, gcc, etc.).
- **git**: Distributed version control system.
- **curl**: Command line tool for transferring data with URLs.
- **cmake**: Cross-platform build system generator.
- **ninja**: Small build system with a focus on speed.
- **clang**: C language family frontend for LLVM.
- **c++ (gcc)**: GNU Compiler Collection for C++.
- **openssl**: Toolkit for Transport Layer Security (TLS).
- **openssh**: Connectivity tools for remote login with SSH protocol.

### Terminal & Shell

- **zsh**: Improved shell with many features over bash.
- **oh-my-zsh**: Framework for managing your Zsh configuration.
- **powerlevel10k**: Fast, flexible Zsh theme.
- **zsh-autosuggestions**: Fish-like suggestions for Zsh.
- **zsh-syntax-highlighting**: Syntax highlighting for Zsh commands.
- **zsh-completions**: Additional completion definitions for Zsh.
- **starship**: Minimal, blazing-fast, customizable prompt for any shell.
- **tmux**: Terminal multiplexer for managing multiple sessions.
- **stow**: Symlink farm manager (great for dotfiles).
- **font-firacode**: Monospaced font with programming ligatures.
- **direnv**: Unclutter your `.profile` and manage environment variables per project.

### CLI Tools

- **lazygit**: Simple terminal UI for git commands.
- **lazydocker**: The lazier way to manage everything docker.
- **lazysql**: Terminal UI for database management with vim-like controls.
- **zoxide**: A smarter `cd` command that remembers your frequent paths.
- **fzf**: A general-purpose command-line fuzzy finder.
- **bat**: A `cat` clone with syntax highlighting and Git integration.
- **eza**: A modern, maintained replacement for `ls`.
- **ripgrep**: Recursive check for regex patterns in files (`grep` replacement).
- **fd**: A simple, fast and user-friendly alternative to `find`.
- **fastfetch**: Fast, highly customizable system information script.
- **btop**: Resource monitor that shows usage and stats.
- **jq**: Lightweight and flexible command-line JSON processor.
- **nnn**: Tiny, lightning fast, feature-packed file manager.
- **gh**: Official GitHub CLI tool.
- **tealdeer**: Fast implementation of tldr (simplified man pages).
- **neovim**: Hyper-extensible Vim-based text editor.
- **yay**: (Arch only) Yet Another Yogurt - An AUR Helper.

### Languages & Runtimes

- **python**: Interpreted, high-level, general-purpose programming language.
- **uv**: An extremely fast Python package installer and resolver.
- **node**: JavaScript runtime built on Chrome's V8 engine.
- **npm**: Package manager for the Node JavaScript platform.
- **go**: Open source programming language by Google.
- **rust**: Language empowering everyone to build reliable and efficient software.

### Infrastructure & Services

- **docker**: Platform to build, share, and run containerized applications.
- **redis**: In-memory data store used as a database, cache, and message broker.
- **postgres**: Powerful, open source object-relational database system.

## Structure

- `main.py`: Entry point (CLI & Orchestration).
- `checker.py`: Defensive detection logic.
- `base.py`: Abstract installer logic.
- `[distro].py`: Distro-specific implementations.

## Dual-OS Dev

Auto-configured via `direnv` (`.envrc`):

- **WSL**: `.venv-wsl`
- **Windows**: `.venv-win`
