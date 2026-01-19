import os
import subprocess
from typing import List

from base import DistroInstaller


class ArchInstaller(DistroInstaller):
    @property
    def log_id(self) -> str:
        return "arch"

    PACKAGES = [
        # 1. Dev (Compilers, Base)
        ("base-devel", "manager", "base-devel"),
        ("openssl", "manager", "openssl"),
        ("openssh", "manager", "openssh"),
        ("git", "manager", "git"),
        ("curl", "manager", "curl"),
        ("cmake", "manager", "cmake"),
        ("ninja", "manager", "ninja"),
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
        ("gh", "manager", "github-cli"),
        ("zoxide", "manager", "zoxide"),
        ("fzf", "manager", "fzf"),
        ("eza", "manager", "eza"),
        ("bat", "manager", "bat"),
        ("fd", "manager", "fd"),
        ("ripgrep", "manager", "ripgrep"),
        ("rsync", "manager", "rsync"),
        ("btop", "manager", "btop"),
        ("fastfetch", "manager", "fastfetch"),
        ("jq", "manager", "jq"),
        ("yq", "manager", "yq"),
        ("nnn", "manager", "nnn"),
        ("direnv", "manager", "direnv"),
        ("dust", "manager", "dust"),
        ("duf", "manager", "duf"),
        ("hyperfine", "manager", "hyperfine"),
        # Archive tools
        ("zip", "manager", "zip"),
        ("unzip", "manager", "unzip"),
        ("p7zip", "manager", "p7zip"),
        # 4. Tools
        (
            "docker",
            "binary",
            "curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && rm get-docker.sh",
        ),
        ("docker-group", "binary", "sudo usermod -aG docker $(whoami)"),
        ("redis", "manager", "redis"),
        ("postgres", "manager", "postgresql"),
        # 5. Langs
        ("python", "manager", "python"),
        ("node", "manager", "nodejs"),
        ("npm", "manager", "npm"),
        ("go", "manager", "go"),
        (
            "rust",
            "binary",
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
        ),
        ("uv", "binary", "curl -LsSf https://astral.sh/uv/install.sh | sh"),
        # 6. Dependent / Late Bound
        ("tealdeer", "binary", ". ~/.cargo/env && cargo install tealdeer"),
        ("yay", "aur", "yay"),
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
        # 7. Arch-specific (Hyprland ecosystem)
        ("hyprland", "manager", "hyprland"),
        ("waybar", "manager", "waybar"),
        ("kitty", "manager", "kitty"),
        ("rofi-wayland", "manager", "rofi-wayland"),
        ("swaync", "manager", "swaync"),
        ("hypridle", "manager", "hypridle"),
        ("hyprlock", "manager", "hyprlock"),
        ("wallust", "manager", "wallust"),
        # Wayland core tools
        ("wl-clipboard", "manager", "wl-clipboard"),
        ("cliphist", "manager", "cliphist"),
        ("grim", "manager", "grim"),
        ("slurp", "manager", "slurp"),
        ("hyprshot", "aur", "hyprshot"),
        ("hyprpicker", "manager", "hyprpicker"),
        ("swww", "manager", "swww"),
        ("wlogout", "manager", "wlogout"),
        # OCR & Translation
        ("tesseract", "manager", "tesseract"),
        ("tesseract-data-eng", "manager", "tesseract-data-eng"),
        ("tesseract-data-rus", "manager", "tesseract-data-rus"),
        # Audio/Media/System
        ("wireplumber", "manager", "wireplumber"),
        ("playerctl", "manager", "playerctl"),
        ("brightnessctl", "manager", "brightnessctl"),
        ("libnotify", "manager", "libnotify"),
        # Qt/GTK theming
        ("qt5ct", "manager", "qt5ct"),
        ("kvantum", "manager", "kvantum"),
        # Apps
        ("nautilus", "manager", "nautilus"),
        ("flatpak", "manager", "flatpak"),
    ]

    def check_update(self) -> None:
        self.log("Updating system packages...")
        subprocess.run(["sudo", "pacman", "-Syu", "--noconfirm"], check=True)

    def is_package_installed(self, package: str) -> bool:
        """Check if pacman package is installed."""
        try:
            result = subprocess.run(
                ["pacman", "-Q", package],
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

        self.log(f"  Installing {package} via pacman...")
        subprocess.run(
            ["sudo", "pacman", "-S", "--noconfirm", "--needed", package], check=True
        )

    def add_repo(self, repo_info: str) -> None:
        # repo_info could be a line for /etc/pacman.conf
        self.log(f"  Adding repo: {repo_info}")
        with open("/etc/pacman.conf", "a") as f:
            f.write(f"\n{repo_info}\n")
        subprocess.run(["sudo", "pacman", "-Sy"], check=True)

    def yay_install(self, package: str) -> None:
        try:
            subprocess.run(["yay", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("yay not found. Installing yay manually...")
            # Manual installation steps provided by user
            self.build_from_source(
                "https://aur.archlinux.org/yay.git", ["makepkg -si --noconfirm"]
            )

        if package != "yay":
            self.log(f"  Installing {package} via yay...")
            subprocess.run(["yay", "-S", "--noconfirm", package], check=True)
