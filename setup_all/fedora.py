import os
import subprocess
from typing import List

from base import DistroInstaller


class FedoraInstaller(DistroInstaller):
    @property
    def log_id(self) -> str:
        return "fedora"

    @property
    def PACKAGES(self) -> List:
        return [
            # 1. Foundation
            ("build-tools", "manager", "@development-tools"),
            ("git", "manager", "git"),
            # 2. Dev (Compilers, Base)
            ("openssl", "manager", "openssl-devel"),
            ("openssh", "manager", "openssh-clients"),
            ("curl", "manager", "curl"),
            ("cmake", "manager", "cmake"),
            ("ninja", "manager", "ninja-build"),
            ("clang", "manager", "clang"),
            # Neovim build deps
            ("gettext", "manager", "gettext"),
            ("libtool", "manager", "libtool"),
            ("autoconf", "manager", "autoconf"),
            ("automake", "manager", "automake"),
            ("pkg-config", "manager", "pkg-config"),
            # 3. Terminal and Font
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
            # 4. Helpers
            ("gh", "manager", "gh"),
            ("zoxide", "manager", "zoxide"),
            ("fzf", "manager", "fzf"),
            ("eza", "manager", "eza"),
            ("bat", "manager", "bat"),
            ("fd", "manager", "fd-find"),
            ("ripgrep", "manager", "ripgrep"),
            ("rsync", "manager", "rsync"),
            ("btop", "manager", "btop"),
            ("fastfetch", "manager", "fastfetch"),
            ("jq", "manager", "jq"),
            ("yq", "manager", "yq"),
            ("nnn", "manager", "nnn"),
            ("direnv", "manager", "direnv"),
            ("dust", "binary", 'PATH="$HOME/.cargo/bin:$PATH" cargo install du-dust'),
            (
                "duf",
                "binary",
                'PATH="$HOME/go/bin:$PATH" go install github.com/muesli/duf@latest',
            ),
            ("hyperfine", "manager", "hyperfine"),
            # Archive tools
            ("zip", "manager", "zip"),
            ("unzip", "manager", "unzip"),
            ("p7zip", "manager", "p7zip p7zip-plugins"),
            # 5. Tools
            (
                "docker",
                "binary",
                "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && rm get-docker.sh",
            ),
            ("docker-group", "binary", "sudo usermod -aG docker $(whoami)"),
            ("redis", "manager", "redis"),
            ("postgres", "manager", "postgresql-server"),
            # 6. Langs
            ("python", "manager", "python3"),
            ("node", "manager", "nodejs"),
            ("npm", "manager", "npm"),
            ("go", "manager", "golang"),
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
                'PATH="$HOME/.cargo/bin:$PATH" cargo install tealdeer',
            ),
            (
                "lazygit",
                "binary",
                'PATH="$HOME/go/bin:$PATH" go install github.com/jesseduffield/lazygit@latest',
            ),
            (
                "lazydocker",
                "binary",
                'PATH="$HOME/go/bin:$PATH" go install github.com/jesseduffield/lazydocker@latest',
            ),
            (
                "lazysql",
                "binary",
                'PATH="$HOME/go/bin:$PATH" go install github.com/jorgerojas26/lazysql@latest',
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
        self.log("Checking for system updates...")
        subprocess.run(
            ["sudo", "dnf", "check-update"], check=False
        )  # dnf returns 100 if updates are available
        self.log("Upgrading system...")
        subprocess.run(["sudo", "dnf", "upgrade", "-y"], check=True)

    def is_package_installed(self, package: str) -> bool:
        """Check if dnf package is installed."""
        try:
            result = subprocess.run(
                ["rpm", "-q", package],
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

        self.log(f"  Installing {package} via dnf...")
        subprocess.run(["sudo", "dnf", "install", "-y", package], check=True)

    def add_repo(self, repo_info: str) -> None:
        # repo_info for Fedora is usually a .repo URL or a dnf config-manager command
        self.log(f"  Adding repo: {repo_info}")
        if repo_info.endswith(".repo"):
            subprocess.run(
                ["sudo", "dnf", "config-manager", "--add-repo", repo_info], check=True
            )
        else:
            subprocess.run(
                ["sudo", "dnf", "copr", "enable", "-y", repo_info], check=True
            )
