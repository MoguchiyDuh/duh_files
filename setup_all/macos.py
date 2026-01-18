import os
import subprocess
from typing import List

from base import DistroInstaller


class MacOSInstaller(DistroInstaller):
    @property
    def log_id(self) -> str:
        return "macos"

    PACKAGES = [
        # 1. Dev
        (
            "brew",
            "binary",
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        ),
        ("openssl", "manager", "openssl"),
        ("ssh", "manager", "openssh"),
        ("git", "manager", "git"),
        ("curl", "manager", "curl"),
        ("cmake", "manager", "cmake"),
        ("ninja", "manager", "ninja"),
        # 2. Terminal
        ("zsh", "manager", "zsh"),
        (
            "oh-my-zsh",
            "binary",
            'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
        ),
        (
            "powerlevel10k",
            "git",
            (
                "https://github.com/romkatv/powerlevel10k.git",
                [
                    "mkdir -p ~/.oh-my-zsh/custom/themes/powerlevel10k",
                    "cp -r * ~/.oh-my-zsh/custom/themes/powerlevel10k",
                ],
            ),
        ),
        (
            "zsh-autosuggestions",
            "git",
            (
                "https://github.com/zsh-users/zsh-autosuggestions",
                [
                    "mkdir -p ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
                    "cp -r * ~/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
                ],
            ),
        ),
        (
            "zsh-syntax-highlighting",
            "git",
            (
                "https://github.com/zsh-users/zsh-syntax-highlighting.git",
                [
                    "mkdir -p ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
                    "cp -r * ~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
                ],
            ),
        ),
        (
            "zsh-completions",
            "git",
            (
                "https://github.com/zsh-users/zsh-completions.git",
                [
                    "mkdir -p ~/.oh-my-zsh/custom/plugins/zsh-completions",
                    "cp -r * ~/.oh-my-zsh/custom/plugins/zsh-completions",
                ],
            ),
        ),
        ("tmux", "manager", "tmux"),
        ("stow", "manager", "stow"),
        ("starship", "binary", "curl -sS https://starship.rs/install.sh | sh -s -- -y"),
        ("font", "font", "font-fira-code-nerd-font"),
        # 3. Helpers
        ("gh", "manager", "gh"),
        ("zoxide", "manager", "zoxide"),
        ("fzf", "manager", "fzf"),
        ("eza", "manager", "eza"),
        ("bat", "manager", "bat"),
        ("fd", "manager", "fd"),
        ("ripgrep", "manager", "ripgrep"),
        ("btop", "manager", "btop"),
        ("fastfetch", "manager", "fastfetch"),
        ("jq", "manager", "jq"),
        ("nnn", "manager", "nnn"),
        ("tree", "manager", "tree"),
        ("direnv", "manager", "direnv"),
        # 4. Tools
        ("docker", "brew", "docker"),
        ("redis", "manager", "redis"),
        ("postgres", "manager", "postgresql"),
        # 5. Langs
        ("python", "manager", "python3"),
        ("node", "manager", "node"),
        ("go", "manager", "go"),
        (
            "rust",
            "binary",
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
        ),
        ("uv", "binary", "curl -LsSf https://astral.sh/uv/install.sh | sh"),
        # 6. Dependent
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
                    "mkdir -p ~/.config/tmux/plugins/tmux-continuum",
                    "cp -r * ~/.config/tmux/plugins/tmux-continuum",
                ],
            ),
        ),
        (
            "tmux-cpu",
            "git",
            (
                "https://github.com/tmux-plugins/tmux-cpu.git",
                [
                    "mkdir -p ~/.config/tmux/plugins/tmux-cpu",
                    "cp -r * ~/.config/tmux/plugins/tmux-cpu",
                ],
            ),
        ),
        (
            "tmux-prefix-highlight",
            "git",
            (
                "https://github.com/tmux-plugins/tmux-prefix-highlight.git",
                [
                    "mkdir -p ~/.config/tmux/plugins/tmux-prefix-highlight",
                    "cp -r * ~/.config/tmux/plugins/tmux-prefix-highlight",
                ],
            ),
        ),
        (
            "tmux-resurrect",
            "git",
            (
                "https://github.com/tmux-plugins/tmux-resurrect.git",
                [
                    "mkdir -p ~/.config/tmux/plugins/tmux-resurrect",
                    "cp -r * ~/.config/tmux/plugins/tmux-resurrect",
                ],
            ),
        ),
    ]

    def check_update(self) -> None:
        self.log("Updating Homebrew...")
        subprocess.run(["brew", "update"], check=True)
        subprocess.run(["brew", "upgrade"], check=True)

    def install(self, package: str) -> None:
        self.log(f"  Installing {package} via brew...")
        subprocess.run(["brew", "install", package], check=True)

    def add_repo(self, repo_info: str) -> None:
        # repo_info for macOS is usually a brew tap
        self.log(f"  Tapping brew repo: {repo_info}")
        subprocess.run(["brew", "tap", repo_info], check=True)

    def install_font(self, font_url: str) -> None:
        # On macOS, fonts can be installed via brew cask or manually
        if font_url.startswith("font-"):
            subprocess.run(["brew", "install", "--cask", font_url], check=True)
        else:
            super().install_font(font_url)

    def brew_install(self, package: str) -> None:
        self.install(package)
