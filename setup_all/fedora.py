import os
import subprocess
from typing import List

from base import DistroInstaller


class FedoraInstaller(DistroInstaller):
    @property
    def log_id(self) -> str:
        return "fedora"

    PACKAGES = [
        # 1. Dev
        ("build-tools", "manager", "@development-tools"),
        ("openssl", "manager", "openssl-devel"),
        ("ssh", "manager", "openssh-clients"),
        ("git", "manager", "git"),
        ("curl", "manager", "curl"),
        ("cmake", "manager", "cmake"),
        ("c++", "manager", "gcc-c++"),
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
        (
            "font",
            "font",
            "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip",
        ),
        # 3. Helpers
        ("gh", "manager", "gh"),
        ("zoxide", "manager", "zoxide"),
        ("fzf", "manager", "fzf"),
        ("eza", "manager", "eza"),
        ("bat", "manager", "bat"),
        ("fd", "manager", "fd-find"),
        ("ripgrep", "manager", "ripgrep"),
        ("btop", "manager", "btop"),
        ("fastfetch", "manager", "fastfetch"),
        ("jq", "manager", "jq"),
        ("nnn", "manager", "nnn"),
        ("direnv", "manager", "direnv"),
        # 4. Tools
        (
            "docker",
            "binary",
            "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh",
        ),
        ("mod-docker", "binary", "sudo usermod -aG docker $USER"),
        ("redis", "manager", "redis"),
        ("postgres", "manager", "postgresql-server"),
        # 5. Langs
        ("python", "manager", "python3"),
        ("node", "manager", "nodejs"),
        ("npm", "manager", "npm"),
        ("go", "manager", "golang"),
        (
            "rust",
            "binary",
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
        ),
        ("uv", "binary", "curl -LsSf https://astral.sh/uv/install.sh | sh"),
        # 6. Dependent
        ("tealdeer", "binary", ". ~/.cargo/env && cargo install tealdeer"),
        (
            "lazydocker",
            "binary",
            "go install github.com/jesseduffield/lazydocker@latest",
        ),
        (
            "lazygit",
            "binary",
            "go install github.com/jesseduffield/lazygit@latest",
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
        self.log("Checking for system updates...")
        subprocess.run(
            ["sudo", "dnf", "check-update"], check=False
        )  # dnf returns 100 if updates are available
        self.log("Upgrading system...")
        subprocess.run(["sudo", "dnf", "upgrade", "-y"], check=True)

    def install(self, package: str) -> None:
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
