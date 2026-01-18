import os
import subprocess
from typing import List

from base import DistroInstaller


class DebianInstaller(DistroInstaller):
    @property
    def log_id(self) -> str:
        return "debian"

    def check_update(self) -> None:
        self.log("Updating apt cache and upgrading system...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "upgrade", "-y"], check=True)

    def is_package_installed(self, package: str) -> bool:
        """Check if apt package is installed."""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return result.returncode == 0
        except Exception:
            return False

    def install(self, package: str) -> None:
        # Check if already installed
        if self.is_package_installed(package):
            self.log(f"  ↳ Skipping {package} (apt: already installed)")
            return

        self.log(f"  Installing {package} via apt...")
        subprocess.run(["sudo", "apt", "install", "-y", package], check=True)

    PACKAGES = [
        # 1. Dev
        ("build-essential", "manager", "build-essential"),
        ("ssl", "manager", "libssl-dev"),
        ("ssh", "manager", "openssh-client"),
        ("git", "manager", "git"),
        ("curl", "manager", "curl"),
        ("wget", "manager", "wget"),
        ("cmake", "manager", "cmake"),
        ("ninja", "manager", "ninja-build"),
        ("c++", "manager", "g++"),
        ("software-properties-common", "manager", "software-properties-common"),
        # Neovim build deps
        ("gettext", "manager", "gettext"),
        ("libtool", "manager", "libtool"),
        ("libtool-bin", "manager", "libtool-bin"),
        ("autoconf", "manager", "autoconf"),
        ("automake", "manager", "automake"),
        ("unzip", "manager", "unzip"),
        ("pkg-config", "manager", "pkg-config"),
        # 2. Terminal / Font
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
                    "cp -r . ~/.oh-my-zsh/custom/plugins/zsh-completions",
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
        (
            "zoxide",
            "binary",
            "curl -sS https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash",
        ),
        ("fzf", "manager", "fzf"),
        (
            "eza-repo",
            "binary",
            'sudo mkdir -p /etc/apt/keyrings && wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg && echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list && sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list && sudo apt update',
        ),
        ("eza", "manager", "eza"),
        ("bat", "manager", "bat"),  # installs batcat
        (
            "bat-alias",
            "binary",
            "mkdir -p ~/.local/bin && ln -sf /usr/bin/batcat ~/.local/bin/bat",
        ),
        ("fd", "manager", "fd-find"),
        ("ripgrep", "manager", "ripgrep"),
        ("btop", "manager", "btop"),
        ("fastfetch-repo", "repo", "ppa:zhangsongcui3371/fastfetch"),
        ("fastfetch", "manager", "fastfetch"),
        ("jq", "manager", "jq"),
        ("nnn", "manager", "nnn"),
        ("tree", "manager", "tree"),
        ("direnv", "manager", "direnv"),
        # 4. Tools
        (
            "docker",
            "binary",
            "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && rm get-docker.sh",
        ),
        ("mod-docker", "binary", "sudo usermod -aG docker $(whoami)"),
        ("redis", "manager", "redis-server"),
        ("postgres", "manager", "postgresql"),
        # 5. Langs
        ("python", "manager", "python3"),
        ("node", "manager", "nodejs"),
        ("npm", "manager", "npm"),
        ("go", "manager", "golang-go"),
        (
            "rust",
            "binary",
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
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

    def add_repo(self, repo_info: str) -> None:
        # repo_info for Debian is usually a PPA or a source line
        self.log(f"  Adding repo: {repo_info}")
        if repo_info.startswith("ppa:"):
            subprocess.run(["sudo", "add-apt-repository", "-y", repo_info], check=True)
        else:
            with open("/etc/apt/sources.list.d/custom.list", "a") as f:
                f.write(f"\n{repo_info}\n")
        subprocess.run(["sudo", "apt", "update"], check=True)
