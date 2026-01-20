import os
import subprocess
from typing import List

from base import DistroInstaller


class DebianInstaller(DistroInstaller):
    @property
    def log_id(self) -> str:
        return "debian"

    @property
    def PACKAGES(self) -> List:
        return [
            # 1. Foundation
            ("build-essential", "manager", "build-essential"),
            ("git", "manager", "git"),
            # 2. Dev (Compilers, Base)
            ("openssl", "manager", "libssl-dev"),
            ("openssh", "manager", "openssh-client"),
            ("curl", "manager", "curl"),
            ("cmake", "manager", "cmake"),
            ("ninja", "manager", "ninja-build"),
            ("clang", "manager", "clang"),
            ("gettext", "manager", "gettext"),
            ("libtool", "manager", "libtool-bin"),
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
            ("bat", "manager", "bat"),
            (
                "bat-alias",
                "binary",
                "mkdir -p ~/.local/bin && ln -sf /usr/bin/batcat ~/.local/bin/bat",
            ),
            ("fd", "manager", "fd-find"),
            ("ripgrep", "manager", "ripgrep"),
            ("rsync", "manager", "rsync"),
            ("btop", "manager", "btop"),
            ("fastfetch-repo", "repo", "ppa:zhangsongcui3371/fastfetch"),
            ("fastfetch", "manager", "fastfetch"),
            ("jq", "manager", "jq"),
            ("yq", "manager", "yq"),
            ("nnn", "manager", "nnn"),
            ("direnv", "manager", "direnv"),
            ("hyperfine", "manager", "hyperfine"),
            # Archive tools
            ("zip", "manager", "zip"),
            ("unzip", "manager", "unzip"),
            ("p7zip", "manager", "p7zip-full"),
            # 5. Tools
            (
                "docker",
                "binary",
                "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && rm get-docker.sh",
            ),
            ("docker-group", "binary", "sudo usermod -aG docker $(whoami)"),
            ("redis", "manager", "redis-server"),
            ("postgres", "manager", "postgresql"),
            # 6. Langs
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
                "duf",
                "binary",
                'env PATH="$HOME/go/bin:$PATH" go install github.com/muesli/duf@latest',
            ),
            (
                "dust",
                "binary",
                'env PATH="$HOME/.cargo/bin:$PATH" cargo install du-dust',
            ),
            (
                "neovim",
                "git",
                (
                    "https://github.com/neovim/neovim.git",
                    [
                        "git checkout stable || true",
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
        self.log("Updating apt cache and upgrading system...")
        stdout = None if self.verbose else subprocess.DEVNULL
        stderr = None if self.verbose else subprocess.DEVNULL
        apt_args = ["sudo", "apt", "update"]
        if not self.verbose:
            apt_args.insert(2, "-qq")
        subprocess.run(apt_args, check=True, stdout=stdout, stderr=stderr)

        upgrade_args = ["sudo", "apt", "upgrade", "-y"]
        if not self.verbose:
            upgrade_args.insert(2, "-qq")
        subprocess.run(upgrade_args, check=True, stdout=stdout, stderr=stderr)

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
            return

        self.log(f"  Installing {package} via apt...")
        stdout = None if self.verbose else subprocess.DEVNULL
        stderr = None if self.verbose else subprocess.DEVNULL
        install_args = ["sudo", "apt", "install", "-y", package]
        if not self.verbose:
            install_args.insert(2, "-qq")
        subprocess.run(install_args, check=True, stdout=stdout, stderr=stderr)

    def add_repo(self, repo_info: str) -> None:
        # repo_info for Debian is usually a PPA or a source line
        self.log(f"  Adding repo: {repo_info}")
        stdout = None if self.verbose else subprocess.DEVNULL
        stderr = None if self.verbose else subprocess.DEVNULL
        if repo_info.startswith("ppa:"):
            subprocess.run(
                ["sudo", "add-apt-repository", "-y", repo_info],
                check=True,
                stdout=stdout,
                stderr=stderr,
            )
        else:
            with open("/etc/apt/sources.list.d/custom.list", "a") as f:
                f.write(f"\n{repo_info}\n")
        apt_args = ["sudo", "apt", "update"]
        if not self.verbose:
            apt_args.insert(2, "-qq")
        subprocess.run(apt_args, check=True, stdout=stdout, stderr=stderr)
