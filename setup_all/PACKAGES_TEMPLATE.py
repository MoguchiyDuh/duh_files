"""
Standardized package list template for all distros.

This file serves as the canonical reference. All distro-specific files
should match this structure with only package names differing.
"""

STANDARD_PACKAGES = [
    # 1. Dev (Compilers, Base)
    ("base-devel", "manager", "<distro-specific>"),
    ("openssl", "manager", "<distro-specific>"),
    ("openssh", "manager", "<distro-specific>"),
    ("git", "manager", "git"),
    ("curl", "manager", "curl"),
    ("cmake", "manager", "cmake"),
    ("ninja", "manager", "<distro-specific>"),
    ("clang", "manager", "clang"),
    # 2. Terminal and Font
    ("zsh", "manager", "zsh"),
    (
        "oh-my-zsh",
        "binary",
        'RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
    ),
    (
        "powerlevel10k",
        "git",
        (
            "https://github.com/romkatv/powerlevel10k.git",
            [
                "rm -rf ~/.oh-my-zsh/custom/themes/powerlevel10k",
                "mkdir -p ~/.oh-my-zsh/custom/themes/powerlevel10k",
                "cp -r . ~/.oh-my-zsh/custom/themes/powerlevel10k",
            ],
        ),
    ),
    (
        "zsh-autosuggestions",
        "git",
        (
            "https://github.com/zsh-users/zsh-autosuggestions",
            [
                "rm -rf ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
                "mkdir -p ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
                "cp -r . ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
            ],
        ),
    ),
    (
        "zsh-syntax-highlighting",
        "git",
        (
            "https://github.com/zsh-users/zsh-syntax-highlighting.git",
            [
                "rm -rf ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
                "mkdir -p ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
                "cp -r . ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
            ],
        ),
    ),
    (
        "zsh-completions",
        "git",
        (
            "https://github.com/zsh-users/zsh-completions.git",
            [
                "rm -rf ~/.oh-my-zsh/custom/plugins/zsh-completions",
                "mkdir -p ~/.oh-my-zsh/custom/plugins/zsh-completions",
                "cp -r . ~/.oh-my-zsh/custom/plugins/zsh-completions",
            ],
        ),
    ),
    ("tmux", "manager", "tmux"),
    ("stow", "manager", "stow"),
    (
        "font",
        "font",
        "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip",
    ),
    # 3. Helpers
    ("gh", "manager", "<distro-specific>"),
    ("zoxide", "manager", "<distro-specific>"),
    ("fzf", "manager", "fzf"),
    ("eza", "manager", "<distro-specific>"),
    ("bat", "manager", "bat"),
    ("fd", "manager", "<distro-specific>"),
    ("ripgrep", "manager", "ripgrep"),
    ("rsync", "manager", "rsync"),
    ("btop", "manager", "btop"),
    ("fastfetch", "manager", "fastfetch"),
    ("jq", "manager", "jq"),
    ("nnn", "manager", "nnn"),
    ("direnv", "manager", "direnv"),
    # 4. Tools
    (
        "docker",
        "binary",
        "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && rm get-docker.sh",
    ),
    ("docker-group", "binary", "sudo usermod -aG docker $(whoami)"),
    ("redis", "manager", "<distro-specific>"),
    ("postgres", "manager", "<distro-specific>"),
    # 5. Langs
    ("python", "manager", "python3"),
    ("node", "manager", "<distro-specific>"),
    ("npm", "manager", "npm"),
    ("go", "manager", "<distro-specific>"),
    (
        "rust",
        "binary",
        "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
    ),
    ("uv", "binary", "curl -LsSf https://astral.sh/uv/install.sh | sh"),
    # 6. Dependent / Late Bound
    ("tealdeer", "binary", ". ~/.cargo/env && cargo install tealdeer"),
    ("lazygit", "binary", "go install github.com/jesseduffield/lazygit@latest"),
    (
        "lazydocker",
        "binary",
        "go install github.com/jesseduffield/lazydocker@latest",
    ),
    ("lazysql", "binary", "go install github.com/jorgerojas26/lazysql@latest"),
    (
        "neovim",
        "git",
        (
            "https://github.com/neovim/neovim.git",
            [
                "git checkout stable",
                "make CMAKE_BUILD_TYPE=RelWithDebInfo",
                "sudo make install",
            ],
        ),
    ),
    (
        "tmux-continuum",
        "git",
        (
            "https://github.com/tmux-plugins/tmux-continuum.git",
            [
                "rm -rf ~/.config/tmux/plugins/tmux-continuum",
                "mkdir -p ~/.config/tmux/plugins/tmux-continuum",
                "cp -r . ~/.config/tmux/plugins/tmux-continuum",
            ],
        ),
    ),
    (
        "tmux-cpu",
        "git",
        (
            "https://github.com/tmux-plugins/tmux-cpu.git",
            [
                "rm -rf ~/.config/tmux/plugins/tmux-cpu",
                "mkdir -p ~/.config/tmux/plugins/tmux-cpu",
                "cp -r . ~/.config/tmux/plugins/tmux-cpu",
            ],
        ),
    ),
    (
        "tmux-prefix-highlight",
        "git",
        (
            "https://github.com/tmux-plugins/tmux-prefix-highlight.git",
            [
                "rm -rf ~/.config/tmux/plugins/tmux-prefix-highlight",
                "mkdir -p ~/.config/tmux/plugins/tmux-prefix-highlight",
                "cp -r . ~/.config/tmux/plugins/tmux-prefix-highlight",
            ],
        ),
    ),
    (
        "tmux-resurrect",
        "git",
        (
            "https://github.com/tmux-plugins/tmux-resurrect.git",
            [
                "rm -rf ~/.config/tmux/plugins/tmux-resurrect",
                "mkdir -p ~/.config/tmux/plugins/tmux-resurrect",
                "cp -r . ~/.config/tmux/plugins/tmux-resurrect",
            ],
        ),
    ),
    # 7. Hyprland / GUI (conditional, distro-specific)
    ("rofi-wayland", "manager", "<distro-specific>"),
    ("rofi-calc", "manager", "<distro-specific>"),
    ("rofi-emoji", "manager", "<distro-specific>"),
    ("swayimg", "manager", "<distro-specific>"),
]
