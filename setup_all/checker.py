import os
import re
import subprocess
from typing import Optional, Tuple


class DefensiveChecker:
    """Enhanced checker with multiple detection layers."""

    def __init__(self, installer):
        self.installer = installer
        self.distro = installer.log_id

    @staticmethod
    def get_command_path(cmd: str) -> Optional[str]:
        """Get path of command if it exists."""
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
            return None

    @staticmethod
    def command_exists(cmd: str) -> bool:
        """Check if command exists in PATH."""
        return DefensiveChecker.get_command_path(cmd) is not None

    @staticmethod
    def path_exists(path: str) -> bool:
        """Check if path exists."""
        return os.path.exists(os.path.expanduser(path))

    def get_version(self, cmd: str) -> Optional[str]:
        """Get version string from command."""
        try:
            result = subprocess.run(
                [cmd, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2,
            )
            output = (result.stdout or result.stderr).split("\n")[0].strip()
            return output[:60] if output else None
        except Exception:
            return None

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
                    ["dpkg", "-l", pkg],
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
        """Enhanced multi-layered check with detailed reason."""
        reasons = []

        # Package-specific enhanced checks
        if self.distro == "arch":
            # Enhanced Arch package checks
            pkg_map = {
                "base-devel": ["base-devel"],
                "build-essential": ["base-devel"],
                "openssl": ["openssl"],
                "ssl": ["openssl"],
                "openssh": ["openssh"],
                "ssh": ["openssh"],
                "postgres": ["postgresql", "postgresql-libs"],
                "redis": ["redis"],
                "node": ["nodejs"],
                "c++": ["gcc"],
                "clang": ["clang"],
                "ninja": ["ninja"],
                "cmake": ["cmake"],
                "stow": ["stow"],
                "direnv": ["direnv"],
            }

            if name in pkg_map:
                result = self.check_pacman(*pkg_map[name])
                if result:
                    reasons.append(f"pacman: {result}")

        # Check via standard should_skip
        if self.installer.should_skip(name, method, content):
            # Try to resolve path anyway for better boolean reason if simple skip
            path = self.get_command_path(name)
            if path:
                reasons.append(f"found at {path}")
            elif not reasons:
                reasons.append("detected by should_skip()")
            return True, " | ".join(reasons)

        # Additional command checks with alternatives
        cmd_alternatives = {
            "openssl": ["openssl"],
            "ssh": ["ssh"],
            "postgres": ["psql", "postgres"],
            "redis": ["redis-server", "redis-cli"],
            "node": ["node"],
            "npm": ["npm"],
            "c++": ["g++", "clang++"],
            "clang": ["clang", "clang++"],
            "ninja": ["ninja"],
            "cmake": ["cmake"],
            "yay": ["yay"],
            "stow": ["stow"],
            "direnv": ["direnv"],
            "starship": ["starship"],
            "tealdeer": ["tldr"],
            "lazygit": ["lazygit"],
            "lazydocker": ["lazydocker"],
            "neovim": ["nvim"],
            "docker": ["docker"],
            "rust": ["cargo", "rustc"],
            "go": ["go"],
            "python": ["python3", "python"],
            "tmux": ["tmux"],
            "zoxide": ["zoxide"],
            "fzf": ["fzf"],
            "eza": ["eza"],
            "bat": ["bat", "batcat"],
            "fastfetch": ["fastfetch"],
            "uv": ["uv"],
            "rg": ["rg", "ripgrep"],
            "ripgrep": ["rg", "ripgrep"],
            "fd": ["fd", "fdfind"],
        }

        if name in cmd_alternatives:
            for cmd in cmd_alternatives[name]:
                path = self.get_command_path(cmd)
                if path:
                    version = self.get_version(cmd)
                    if version:
                        reasons.append(f"cmd:{cmd} ({version}) -> {path}")
                    else:
                        reasons.append(f"cmd:{cmd} -> {path}")
                    return True, " | ".join(reasons)

        # Path-based checks
        path_checks = {
            "openssl": ["/usr/bin/openssl", "/usr/lib/libssl.so"],
            "ssh": ["/usr/bin/ssh", "~/.ssh"],
            "postgres": ["/usr/bin/psql", "/usr/lib/postgresql"],
            "redis": ["/usr/bin/redis-server"],
            "oh-my-zsh": ["~/.oh-my-zsh"],
        }

        if name in path_checks:
            for path in path_checks[name]:
                if self.path_exists(path):
                    reasons.append(f"path:{path}")
                    return True, " | ".join(reasons)

        # Font check (search multiple directories)
        if method == "font" or name == "font":
            import platform

            font_dirs = (
                ["~/.local/share/fonts", "~/.fonts", "/usr/share/fonts"]
                if platform.system().lower() != "darwin"
                else ["~/Library/Fonts", "/Library/Fonts"]
            )

            # Flexible regex for Fira Code
            font_pattern = re.compile(r"fira.*code", re.IGNORECASE)

            for font_dir in font_dirs:
                expanded = os.path.expanduser(font_dir)
                if os.path.exists(expanded):
                    for root, dirs, files in os.walk(expanded):
                        # Search for matching file
                        for f in files:
                            if font_pattern.search(f):
                                reasons.append(f"found '{f}' in {font_dir}")
                                return True, " | ".join(reasons)

        # Not found
        return False, "NOT FOUND"
