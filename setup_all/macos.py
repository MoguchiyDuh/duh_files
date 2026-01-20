import os
import subprocess
from typing import List

from base import DistroInstaller


class MacOSInstaller(DistroInstaller):
    @property
    def log_id(self) -> str:
        return "macos"

    @property
    def PACKAGES(self) -> List:
        return [
            # 1. Foundation
            (
                "brew",
                "binary",
                '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            ),
            ("git", "brew", "git"),
            # 2. Dev (Compilers, Base)
            ("openssl", "brew", "openssl"),
            ("openssh", "brew", "openssh"),
            ("curl", "brew", "curl"),
            ("cmake", "brew", "cmake"),
            ("ninja", "brew", "ninja"),
            ("clang", "brew", "llvm"),
            # Neovim build deps
            ("gettext", "brew", "gettext"),
            ("libtool", "brew", "libtool"),
            ("autoconf", "brew", "autoconf"),
            ("automake", "brew", "automake"),
            ("pkg-config", "brew", "pkg-config"),
            # 3. Terminal and Font
            ("zsh", "brew", "zsh"),
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
            ("tmux", "brew", "tmux"),
            ("stow", "brew", "stow"),
            ("font", "font", "font-fira-code-nerd-font"),
            # 4. Helpers
            ("gh", "brew", "gh"),
            ("zoxide", "brew", "zoxide"),
            ("fzf", "brew", "fzf"),
            ("eza", "brew", "eza"),
            ("bat", "brew", "bat"),
            ("fd", "brew", "fd"),
            ("ripgrep", "brew", "ripgrep"),
            ("rsync", "brew", "rsync"),
            ("btop", "brew", "btop"),
            ("fastfetch", "brew", "fastfetch"),
            ("jq", "brew", "jq"),
            ("yq", "brew", "yq"),
            ("nnn", "brew", "nnn"),
            ("direnv", "brew", "direnv"),
            ("dust", "brew", "dust"),
            ("duf", "brew", "duf"),
            ("hyperfine", "brew", "hyperfine"),
            # Archive tools
            ("zip", "brew", "zip"),
            ("unzip", "brew", "unzip"),
            ("p7zip", "brew", "p7zip"),
            # 5. Tools
            ("docker", "brew", "docker"),
            ("redis", "brew", "redis"),
            ("postgres", "brew", "postgresql"),
            # 6. Langs
            ("python", "brew", "python3"),
            ("node", "brew", "node"),
            ("npm", "brew", "npm"),
            ("go", "brew", "go"),
            (
                "rust",
                "binary",
                "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
            ),
            ("uv", "binary", "curl -LsSf https://astral.sh/uv/install.sh | sh"),
            # 7. AUR-equivalent (Build from source / binary)
            (
                "tealdeer",
                "binary",
                'env PATH="$HOME/.cargo/bin:$PATH" cargo install tealdeer',
            ),
            (
                "lazygit",
                "binary",
                'env PATH="$HOME/go/bin:$PATH" go install github.com/jesseduffield/lazygit@latest',
            ),
            (
                "lazydocker",
                "binary",
                'env PATH="$HOME/go/bin:$PATH" go install github.com/jesseduffield/lazydocker@latest',
            ),
            (
                "lazysql",
                "binary",
                'env PATH="$HOME/go/bin:$PATH" go install github.com/jorgerojas26/lazysql@latest',
            ),
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
        ]

    def check_update(self) -> None:
        self.log("Updating Homebrew...")
        subprocess.run(["brew", "update"], check=True)
        subprocess.run(["brew", "upgrade"], check=True)

    def is_package_installed(self, package: str) -> bool:
        """Check if brew package is installed."""
        try:
            result = subprocess.run(
                ["brew", "list", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except Exception:
            return False

    def install(self, package: str) -> None:
        # Check if already installed
        if self.is_package_installed(package):
            return

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
