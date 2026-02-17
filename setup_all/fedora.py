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
            (
                "zoxide",
                "github",
                ("ajeetdsouza/zoxide", "zoxide*x86_64-unknown-linux-musl.tar.gz"),
            ),
            ("fzf", "github", ("junegunn/fzf", "fzf*linux_amd64.tar.gz")),
            ("eza", "manager", "eza"),
            (
                "bat",
                "github",
                ("sharkdp/bat", "bat*x86_64-unknown-linux-musl.tar.gz"),
            ),
            ("fd", "github", ("sharkdp/fd", "fd*x86_64-unknown-linux-musl.tar.gz")),
            (
                "ripgrep",
                "github",
                ("BurntSushi/ripgrep", "ripgrep*x86_64-unknown-linux-musl.tar.gz"),
            ),
            ("rsync", "manager", "rsync"),
            (
                "btop",
                "github",
                ("aristocratos/btop", "btop*x86_64*linux-musl.tbz"),
            ),
            (
                "fastfetch",
                "github",
                ("fastfetch-cli/fastfetch", "fastfetch*linux-amd64.tar.gz"),
            ),
            ("jq", "manager", "jq"),
            ("yq", "github", ("mikefarah/yq", "yq_linux_amd64.tar.gz")),
            ("nnn", "manager", "nnn"),
            ("direnv", "github", ("direnv/direnv", "direnv.linux-amd64")),
            (
                "delta",
                "github",
                ("dandavison/delta", "delta*x86_64-unknown-linux-musl.tar.gz"),
            ),
            ("dust", "cargo", "du-dust"),
            ("duf", "go", "github.com/muesli/duf@latest"),
            (
                "hyperfine",
                "github",
                ("sharkdp/hyperfine", "hyperfine*x86_64-unknown-linux-musl.tar.gz"),
            ),
            # Archive tools
            ("zip", "manager", "zip"),
            ("unzip", "manager", "unzip"),
            ("p7zip", "manager", "p7zip p7zip-plugins"),
            # 5. Tools
            (
                "docker",
                "binary",
                "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && rm get-docker.sh && sudo usermod -aG docker $(whoami)",
            ),
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
            ("tealdeer", "cargo", "tealdeer"),
            (
                "lazygit",
                "github",
                ("jesseduffield/lazygit", "lazygit_*.linux_x86_64.tar.gz"),
            ),
            (
                "lazydocker",
                "github",
                ("jesseduffield/lazydocker", "lazydocker_*.Linux_x86_64.tar.gz"),
            ),
            (
                "lazysql",
                "github",
                ("jorgerojas26/lazysql", "lazysql_Linux_x86_64.tar.gz"),
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
            if self.force:
                self.log(f"  Force-reinstalling {package} via dnf...")
                subprocess.run(["sudo", "dnf", "reinstall", "-y", package], check=True)
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
