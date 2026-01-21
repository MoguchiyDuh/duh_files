import os
import re
import subprocess
from typing import List, Optional, Tuple


class DefensiveChecker:
    """Enhanced checker with explicit path reporting and multi-layered detection."""

    def __init__(self, installer):
        self.installer = installer
        self.distro = installer.log_id

    @staticmethod
    def get_command_path(cmd: str) -> Optional[str]:
        """Get path of command, checking both system PATH and local binaries."""
        # 1. System PATH
        try:
            result = subprocess.run(
                ["which", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                check=True,
                text=True,
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

        # 2. Local Fallbacks (Common for manual/lang-specific installs)
        local_bins = [
            "~/go/bin",
            "~/.cargo/bin",
            "~/.local/bin",
            "/usr/local/go/bin",
        ]
        for bin_dir in local_bins:
            full_path = os.path.join(os.path.expanduser(bin_dir), cmd)
            if os.path.exists(full_path):
                return full_path

        return None

    @staticmethod
    def path_exists(path: str) -> bool:
        """Check if path exists."""
        return os.path.exists(os.path.expanduser(path))

    def check_pacman(self, *pkg_names: str) -> Optional[str]:
        """Check if any package name is installed via pacman."""
        for pkg in pkg_names:
            try:
                result = subprocess.run(
                    ["pacman", "-Q", pkg],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                continue
        return None

    def check_dpkg(self, *pkg_names: str) -> Optional[str]:
        """Check if any package name is installed via dpkg."""
        for pkg in pkg_names:
            try:
                result = subprocess.run(
                    ["dpkg", "-s", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    return f"dpkg: {pkg}"
            except Exception:
                continue
        return None

    def check_brew(self, *pkg_names: str) -> Optional[str]:
        """Check if any package name is installed via brew."""
        for pkg in pkg_names:
            try:
                result = subprocess.run(
                    ["brew", "list", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if result.returncode == 0:
                    return f"brew: {pkg}"
            except Exception:
                continue
        return None

    def enhanced_check(self, name: str, method: str, content) -> Tuple[bool, str]:
        """
        Rewritten detection logic.
        Hierarchy:
        1. Binary check (which)
        2. Plugin/Path check (fs)
        3. Package manager check (query)
        """

        # 1. Binary / Command Check
        cmd_alternatives = {
            "neovim": ["nvim"],
            "ripgrep": ["rg"],
            "fd": ["fd", "fdfind"],
            "bat": ["bat", "batcat"],
            "p7zip": ["7z", "7za", "7zz"],
            "redis": ["redis-server"],
            "postgres": ["postgres", "psql"],
            "docker": ["docker"],
            "rust": ["rustc", "cargo"],
            "node": ["node"],
            "python": ["python3", "python"],
            "tealdeer": ["tldr"],
            "openssh": ["ssh", "sshd"],
            "ninja": ["ninja", "ninja-build"],
            "delta": ["delta"],
            "procs": ["procs"],
        }

        cmds_to_test = cmd_alternatives.get(name.lower(), [name.lower()])
        for cmd in cmds_to_test:
            path = self.get_command_path(cmd)
            if path:
                return True, path.replace(os.path.expanduser("~"), "~")

        # 2. Plugin / Specific Path Check
        path_map = {
            "oh-my-zsh": "~/.oh-my-zsh",
            "powerlevel10k": "~/.oh-my-zsh/custom/themes/powerlevel10k",
            "zsh-autosuggestions": "~/.oh-my-zsh/custom/plugins/zsh-autosuggestions",
            "zsh-syntax-highlighting": "~/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting",
            "zsh-completions": "~/.oh-my-zsh/custom/plugins/zsh-completions",
            "tmux-continuum": "~/.config/tmux/plugins/tmux-continuum",
            "tmux-cpu": "~/.config/tmux/plugins/tmux-cpu",
            "tmux-prefix-highlight": "~/.config/tmux/plugins/tmux-prefix-highlight",
            "tmux-resurrect": "~/.config/tmux/plugins/tmux-resurrect",
            "tmux-plugins": "~/.config/tmux/plugins",
        }

        # Check for generic plugins
        if name.startswith("zsh-") and name not in path_map:
            path_map[name] = f"~/.oh-my-zsh/custom/plugins/{name}"
        elif name.startswith("tmux-") and name not in path_map:
            path_map[name] = f"~/.config/tmux/plugins/{name}"

        if name in path_map:
            if self.path_exists(path_map[name]):
                return True, path_map[name]

        # 3. Font Check
        if method == "font" or name in ("font", "nerd-fonts"):
            font_dirs = [
                "~/.local/share/fonts",
                "~/.fonts",
                "/usr/share/fonts",
                "~/Library/Fonts",
                "/Library/Fonts",
            ]
            font_pattern = re.compile(r"fira.*code", re.IGNORECASE)
            for font_dir in font_dirs:
                expanded = os.path.expanduser(font_dir)
                if os.path.exists(expanded):
                    for root, dirs, files in os.walk(expanded):
                        for f in files:
                            if font_pattern.search(f):
                                return True, os.path.join(font_dir, f).replace(
                                    os.path.expanduser("~"), "~"
                                )

        # 4. Package Manager Fallback (for meta-packages like base-devel)
        pkg_map = {
            "arch": {
                "base-devel": ["base-devel"],
                "openssl": ["openssl"],
                "openssh": ["openssh"],
            },
            "debian": {
                "build-essential": ["build-essential"],
            },
        }

        if self.distro in pkg_map and name in pkg_map[self.distro]:
            pkgs = pkg_map[self.distro][name]
            result = None
            if self.distro == "arch":
                result = self.check_pacman(*pkgs)
            elif self.distro == "debian":
                result = self.check_dpkg(*pkgs)

            if result:
                return True, result

        return False, "NOT FOUND"
