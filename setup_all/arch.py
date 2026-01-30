import subprocess
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from base import PackageDef

from base import DistroInstaller


class ArchInstaller(DistroInstaller):
    def __init__(self, hyprland: bool = False) -> None:
        super().__init__()
        self.hyprland = hyprland

    @property
    def log_id(self) -> str:
        return "arch"

    @property
    def PACKAGES(self) -> List["PackageDef"]:
        PACKAGES_CORE = [
            # 0. Foundation (yay and its deps)
            ("base-devel", "manager", "base-devel"),
            ("git", "manager", "git"),
            (
                "yay",
                "binary",
                "git clone --depth 1 https://aur.archlinux.org/yay.git /tmp/yay && cd /tmp/yay && makepkg -si --noconfirm && rm -rf /tmp/yay",
            ),
            # 1. Dev (Compilers, Base)
            ("openssl", "aur", "openssl"),
            ("openssh", "aur", "openssh"),
            ("curl", "aur", "curl"),
            ("cmake", "aur", "cmake"),
            ("ninja", "aur", "ninja"),
            ("clang", "aur", "clang"),
            # 2. Terminal and Font
            ("zsh", "aur", "zsh"),
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
            ("tmux", "aur", "tmux"),
            ("stow", "aur", "stow"),
            ("ttf-firacode-nerd", "aur", "ttf-firacode-nerd"),
            # 3. Helpers
            ("gh", "aur", "github-cli"),
            ("zoxide", "aur", "zoxide"),
            ("fzf", "aur", "fzf"),
            ("eza", "aur", "eza"),
            ("bat", "aur", "bat"),
            ("fd", "aur", "fd"),
            ("ripgrep", "aur", "ripgrep"),
            ("rsync", "aur", "rsync"),
            ("btop", "aur", "btop"),
            ("fastfetch", "aur", "fastfetch"),
            ("jq", "aur", "jq"),
            ("yq", "aur", "yq"),
            ("nnn", "aur", "nnn"),
            ("direnv", "aur", "direnv"),
            ("delta", "aur", "git-delta"),
            ("procs", "aur", "procs"),
            ("dust", "aur", "dust"),
            ("duf", "aur", "duf"),
            ("hyperfine", "aur", "hyperfine"),
            # Archive tools
            ("zip", "aur", "zip"),
            ("unzip", "aur", "unzip"),
            ("p7zip", "aur", "p7zip"),
            # Filesystem support
            ("ntfs-3g", "aur", "ntfs-3g"),
            # 4. Tools
            ("docker", "aur", "docker"),
            ("docker-group", "binary", "sudo usermod -aG docker $(whoami)"),
            ("redis", "aur", "redis"),
            ("postgres", "aur", "postgresql"),
            # 5. Langs
            ("python", "aur", "python"),
            ("node", "aur", "nodejs"),
            ("npm", "aur", "npm"),
            ("go", "aur", "go"),
            ("rust", "aur", "rustup"),
            ("uv", "aur", "uv"),
            ("tealdeer", "aur", "tealdeer"),
            ("lazygit", "aur", "lazygit"),
            ("lazydocker", "aur", "lazydocker"),
            ("lazysql", "aur", "lazysql-bin"),
            ("neovim", "aur", "neovim-git"),
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

        PACKAGES_HYPRLAND = [
            # 7. Arch-specific (Hyprland ecosystem)
            ("hyprland", "aur", "hyprland-git"),
            ("waybar", "aur", "waybar-hyprland-git"),
            ("kitty", "aur", "kitty"),
            ("rofi-wayland", "aur", "rofi-wayland"),
            ("swaync", "aur", "swaync"),
            ("hypridle", "aur", "hypridle"),
            ("hyprlock", "aur", "hyprlock"),
            ("wallust", "aur", "wallust"),
            ("imagemagick", "aur", "imagemagick"),
            # Wayland core tools
            ("wl-clipboard", "aur", "wl-clipboard"),
            ("cliphist", "aur", "cliphist"),
            ("grim", "aur", "grim"),
            ("slurp", "aur", "slurp"),
            ("hyprshot", "aur", "hyprshot"),
            ("hyprpicker", "aur", "hyprpicker"),
            ("swww", "aur", "swww"),
            ("wlogout", "aur", "wlogout"),
            # OCR & Translation
            ("tesseract", "aur", "tesseract"),
            ("tesseract-data-eng", "aur", "tesseract-data-eng"),
            ("tesseract-data-rus", "aur", "tesseract-data-rus"),
            # Audio/Media/System
            ("pipewire", "aur", "pipewire"),
            ("pipewire-pulse", "aur", "pipewire-pulse"),
            ("wireplumber", "aur", "wireplumber"),
            ("pavucontrol", "aur", "pavucontrol"),
            ("playerctl", "aur", "playerctl"),
            ("brightnessctl", "aur", "brightnessctl"),
            ("libnotify", "aur", "libnotify"),
            # Bluetooth
            ("bluez", "aur", "bluez"),
            ("bluez-utils", "aur", "bluez-utils"),
            ("blueman", "aur", "blueman"),
            ("bluetooth-enable", "binary", "sudo systemctl enable --now bluetooth"),
            # Network/WiFi
            ("networkmanager", "aur", "networkmanager"),
            ("network-manager-applet", "aur", "network-manager-applet"),
            ("nm-enable", "binary", "sudo systemctl enable --now NetworkManager"),
            # Qt/GTK theming
            ("qt5ct", "aur", "qt5ct"),
            ("kvantum", "aur", "kvantum"),
            # Apps
            ("nautilus", "aur", "nautilus"),
            ("flatpak", "aur", "flatpak"),
            # NVIDIA drivers (DKMS for better compatibility)
            ("nvidia-dkms", "aur", "nvidia-dkms"),
            ("nvidia-utils", "aur", "nvidia-utils"),
            ("nvidia-settings", "aur", "nvidia-settings"),
            ("lib32-nvidia-utils", "aur", "lib32-nvidia-utils"),
            # Fonts (comprehensive coverage)
            ("ttf-firacode-nerd", "aur", "ttf-firacode-nerd"),
            ("noto-fonts", "aur", "noto-fonts"),
            ("noto-fonts-cjk", "aur", "noto-fonts-cjk"),
            ("noto-fonts-emoji", "aur", "noto-fonts-emoji"),
            ("noto-fonts-extra", "aur", "noto-fonts-extra"),
        ]

        return PACKAGES_CORE + PACKAGES_HYPRLAND if self.hyprland else PACKAGES_CORE

    def check_update(self) -> None:
        """Update system packages."""
        self.log("Updating system packages...")
        subprocess.run(
            ["sudo", "pacman", "-Syu", "--noconfirm"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def is_package_installed(self, package: str) -> bool:
        """Check if a pacman package is installed."""
        result = subprocess.run(
            ["pacman", "-Q", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0

    def install(self, package: str) -> None:
        """Install a package via pacman."""
        self.log(f"  Installing {package} via pacman...")
        install_args = ["sudo", "pacman", "-S", "--noconfirm", package]
        if not self.force:
            install_args.insert(3, "--needed")
        subprocess.run(
            install_args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def add_repo(self, repo_info: str) -> None:
        """Add a repository to pacman.conf."""
        self.log(f"  Adding repo: {repo_info}")
        try:
            with open("/etc/pacman.conf", "a") as f:
                f.write(f"\n{repo_info}\n")
            subprocess.run(
                ["sudo", "pacman", "-Sy"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except PermissionError:
            self.log("  Error: Need sudo privileges to modify pacman.conf")
            raise

    def yay_install(self, package: str) -> None:
        """Install a package via yay (AUR helper)."""
        if package == "yay":
            return

        self.log(f"  Installing {package} via yay...")
        install_args = ["yay", "-S", "--noconfirm", package]
        if self.force:
            install_args.append(
                "--force"
            )  # yay specific force if needed, but usually just omitting --needed works
        subprocess.run(
            install_args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
