"""
Base installer class with defensive checks for idempotent installations.

Features:
- Multi-layered package detection (command existence, path checks, version checks)
- Skips already-installed packages to make script re-runnable
- APT package check via dpkg
- Binary installation checks via 'which' and path existence
- Git repo checks via directory existence
- Font installation checks via file existence
"""

import os
import platform
import subprocess
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union

PackageDef = Tuple[str, str, Union[str, List[str], Tuple[str, List[str]]]]


class Colors:
    """ANSI color codes for prettier output."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class DistroInstaller(ABC):
    @property
    @abstractmethod
    def PACKAGES(self) -> List[PackageDef]:
        pass

    def __init__(self) -> None:
        self.verbose: bool = False

    @staticmethod
    def command_exists(cmd: str) -> bool:
        """Check if a command exists in PATH."""
        try:
            subprocess.run(
                ["which", cmd],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def path_exists(path: str) -> bool:
        """Check if a path exists."""
        expanded = os.path.expanduser(path)
        return os.path.exists(expanded)

    def package_installed(self, *pkg_names: str) -> bool:
        """Check if package is installed via package manager (distro-agnostic)."""
        # Delegate to subclass implementation
        if hasattr(self, "is_package_installed"):
            for pkg in pkg_names:
                if self.is_package_installed(pkg):  # type: ignore
                    return True
        return False

    def log(self, message: str) -> None:
        """Standardized logger with colors."""
        tag = f"{Colors.CYAN}[{self.log_id.upper()}]{Colors.RESET}"
        if "Skipping" in message:
            print(f"{tag} {Colors.YELLOW}{message}{Colors.RESET}")
        elif "Failed" in message or "Fail" in message or "✗" in message:
            print(f"{tag} {Colors.RED}{message}{Colors.RESET}")
        elif "Installed" in message or "✓" in message:
            print(f"{tag} {Colors.GREEN}{message}{Colors.RESET}")
        elif "Building" in message or "Cloning" in message:
            print(f"{tag} {Colors.BLUE}{message}{Colors.RESET}")
        else:
            print(f"{tag} {message}")

    def should_skip(
        self, name: str, method: str, content: Union[str, List, Tuple]
    ) -> bool:
        """Determine if installation should be skipped."""
        # Check common command names
        cmd_map = {
            "git": "git",
            "curl": "curl",
            "wget": "wget",
            "docker": "docker",
            "zsh": "zsh",
            "tmux": "tmux",
            "nvim": "nvim",
            "neovim": "nvim",
            "go": "go",
            "python": "python3",
            "rust": "rustc",
            "cargo": "cargo",
            "gh": "gh",
            "fzf": "fzf",
            "bat": "bat",
            "eza": "eza",
            "btop": "btop",
            "jq": "jq",
            "ripgrep": "rg",
            "fd": "fd",
            "zoxide": "zoxide",
            "lazygit": "lazygit",
            "lazydocker": "lazydocker",
            "starship": "starship",
            "direnv": "direnv",
            "fastfetch": "fastfetch",
            "nnn": "nnn",
            "stow": "stow",
            "cmake": "cmake",
            "ninja": "ninja",
            "tealdeer": "tldr",
            "uv": "uv",
            "node": "node",
            "npm": "npm",
            "yay": "yay",
            "redis": "redis-server",
            "rsync": "rsync",
            "dust": "dust",
            "duf": "duf",
            "hyperfine": "hyperfine",
            "jq": "jq",
            "yq": "yq",
            "p7zip": "7z",
        }

        # Package name variations across distros (for package manager checks)
        pkg_map = {
            "base-devel": ["base-devel", "build-essential", "@development-tools"],
            "build-essential": [
                "base-devel",
                "build-essential",
                "gcc",
                "@development-tools",
            ],
            "openssl": ["openssl", "libssl-dev", "openssl-devel"],
            "ssl": ["openssl", "libssl-dev", "openssl-devel"],
            "ssh": ["openssh", "openssh-client", "openssh-clients"],
            "openssh": ["openssh", "openssh-client", "openssh-clients"],
            "postgres": ["postgresql", "postgresql-libs", "postgresql-server"],
            "redis": ["redis", "redis-server"],
            "node": ["nodejs", "node"],
            "c++": ["gcc", "g++", "clang"],
            "clang": ["clang", "clang++"],
            "ninja": ["ninja", "ninja-build"],
            "cmake": ["cmake"],
            "stow": ["stow"],
            "direnv": ["direnv"],
        }

        # Check if command exists
        if name.lower() in cmd_map:
            if self.command_exists(cmd_map[name.lower()]):
                self.log(f"  ↳ Skipping {name} (already installed)")
                return True
        else:
            # Fallback: check if the name itself is a valid command
            if self.command_exists(name.lower()):
                self.log(f"  ↳ Skipping {name} (found command: {name})")
                return True

        # Check package manager for packages that may not have obvious commands
        if name in pkg_map:
            if self.package_installed(*pkg_map[name]):
                self.log(f"  ↳ Skipping {name} (package manager: already installed)")
                return True

        # Special checks for binary installations
        if method == "binary":
            # oh-my-zsh (check by name since content varies)
            if "oh-my-zsh" in name or "ohmyzsh" in str(content).lower():
                if self.path_exists("~/.oh-my-zsh"):
                    self.log(f"  ↳ Skipping {name} (already installed)")
                    return True
            # Docker group modification
            elif "usermod" in str(content) and "docker" in str(content):
                try:
                    result = subprocess.run(
                        ["groups"],
                        capture_output=True,
                        text=True,
                    )
                    if "docker" in result.stdout:
                        self.log(f"  ↳ Skipping {name} (already in docker group)")
                        return True
                except Exception:
                    pass
            # bat alias
            elif "bat-alias" in name:
                if self.path_exists("~/.local/bin/bat"):
                    self.log(f"  ↳ Skipping {name} (already created)")
                    return True
            # Rust installation
            elif "rustup" in str(content):
                if self.command_exists("rustc") and self.path_exists("~/.cargo"):
                    self.log(f"  ↳ Skipping {name} (already installed)")
                    return True
            # UV installation
            elif "astral.sh/uv" in str(content):
                if self.command_exists("uv"):
                    self.log(f"  ↳ Skipping {name} (already installed)")
                    return True

        # Check specific paths for git installations
        if method == "git":
            if name == "oh-my-zsh":
                if self.path_exists("~/.oh-my-zsh"):
                    self.log(f"  ↳ Skipping {name} (already installed)")
                    return True
            elif name == "powerlevel10k":
                if self.path_exists("~/.oh-my-zsh/custom/themes/powerlevel10k"):
                    self.log(f"  ↳ Skipping {name} (already installed)")
                    return True
            elif "zsh-" in name:
                plugin_name = name
                if self.path_exists(f"~/.oh-my-zsh/custom/plugins/{plugin_name}"):
                    self.log(f"  ↳ Skipping {name} (already installed)")
                    return True
            elif name == "neovim":
                # Only skip if nvim exists AND was built from source
                if self.command_exists("nvim"):
                    try:
                        result = subprocess.run(
                            ["nvim", "--version"],
                            capture_output=True,
                            text=True,
                        )
                        # Check if it's a recent version (likely built from source)
                        if "NVIM v0" in result.stdout:
                            self.log(f"  ↳ Skipping {name} (already installed)")
                            return True
                    except Exception:
                        pass
            elif "tmux-" in name:
                plugin_name = name
                if self.path_exists(f"~/.config/tmux/plugins/{plugin_name}"):
                    self.log(f"  ↳ Skipping {name} (already installed)")
                    return True

        # Check font installation
        if method == "font":
            # Check multiple font directories
            font_dirs = []
            if platform.system().lower() == "darwin":
                font_dirs = ["~/Library/Fonts", "/Library/Fonts"]
            else:
                font_dirs = [
                    "~/.local/share/fonts",
                    "~/.fonts",
                    "/usr/share/fonts",
                    "/usr/local/share/fonts",
                ]

            for font_dir in font_dirs:
                expanded_dir = os.path.expanduser(font_dir)
                if os.path.exists(expanded_dir):
                    # Check if any FiraCode files exist (case-insensitive)
                    for root, dirs, files in os.walk(expanded_dir):
                        if any("firacode" in f.lower() for f in files):
                            self.log(f"  ↳ Skipping {name} (font found in {font_dir})")
                            return True

        return False

    def install_all(self) -> None:
        for name, method, content in self.PACKAGES:
            self.log(f"Processing {name} ({method})...")

            # Special handling for shell and env reloading
            if name == "zsh":
                # Ensure zsh is default shell if installed
                if self.command_exists("zsh"):
                    current_shell = os.environ.get("SHELL", "")
                    if "zsh" not in current_shell:
                        self.log("  Switching default shell to zsh...")
                        try:
                            zsh_path = (
                                subprocess.check_output(["which", "zsh"])
                                .decode()
                                .strip()
                            )
                            subprocess.run(["chsh", "-s", zsh_path], check=False)
                        except Exception:
                            self.log(
                                "  ⚠ Failed to switch shell automatically. Please run: chsh -s $(which zsh)"
                            )

            # Reload environment paths dynamically (for go, cargo, etc.)
            home = os.path.expanduser("~")
            new_paths = [
                os.path.join(home, "go/bin"),
                os.path.join(home, ".cargo/bin"),
                os.path.join(home, ".local/bin"),
            ]
            for path in new_paths:
                if path not in os.environ["PATH"] and os.path.exists(path):
                    os.environ["PATH"] = f"{path}:{os.environ['PATH']}"

            # Skip if already installed
            if self.should_skip(name, method, content):
                continue

            try:
                if method == "manager":
                    self.install(str(content))
                elif method == "aur":
                    self.yay_install(str(content))
                elif method == "brew":
                    self.brew_install(str(content))
                elif method == "repo":
                    self.add_repo(str(content))
                elif method == "binary":
                    stdout = None if self.verbose else subprocess.DEVNULL
                    stderr = None if self.verbose else subprocess.DEVNULL
                    subprocess.run(
                        str(content),
                        shell=True,
                        check=True,
                        stdout=stdout,
                        stderr=stderr,
                    )
                elif method == "git":
                    if isinstance(content, (list, tuple)):
                        self.build_from_source(content[0], content[1])  # type: ignore
                elif method == "font":
                    self.install_font(str(content))
                self.log(f"  ✓ Installed {name}")
            except Exception as e:
                self.log(f"  ✗ Failed to install {name}: {e}")

        # Restore configurations after installation
        self.restore_configs()
        self.link_scripts()

    def restore_configs(self) -> None:
        """Use GNU Stow to symlink dotfiles from repo to home."""
        self.log("Stowing dotfiles...")

        home = os.path.expanduser("~")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dotfiles_dir = os.path.join(os.path.dirname(script_dir), "dotfiles")

        if not os.path.exists(dotfiles_dir):
            self.log(f"  ⚠ Dotfiles directory not found: {dotfiles_dir}")
            return

        # Create backup dir if needed
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(script_dir), f".backups/{timestamp}")

        # Stow packages (each subdirectory in dotfiles/)
        packages = ["zsh", "nvim", "tmux", "fastfetch"]

        # Add arch-specific packages if on Arch
        if self.log_id == "arch":
            packages.extend(
                ["hypr", "waybar", "kitty", "rofi", "gtk", "qt5", "wallust"]
            )

        for pkg in packages:
            pkg_path = os.path.join(dotfiles_dir, pkg)
            if not os.path.exists(pkg_path):
                continue

            self.log(f"  Checking {pkg} for conflicts...")

            # Try stow first to detect conflicts
            result = subprocess.run(
                ["stow", "--simulate", "--restow", "--target", home, pkg],
                cwd=dotfiles_dir,
                capture_output=True,
                text=True,
            )

            # If conflicts detected, backup existing files
            if result.returncode != 0 and "existing target" in result.stderr:
                self.log(f"    Found conflicts, backing up existing files...")
                os.makedirs(backup_dir, exist_ok=True)

                # Extract conflicting file paths from stow error output
                for line in result.stderr.split("\n"):
                    if "existing target" in line:
                        # Parse: "* existing target is ... (.zshrc)"
                        parts = line.split("(")
                        if len(parts) > 1:
                            conflict_file = parts[-1].rstrip(")")
                            conflict_path = os.path.join(home, conflict_file)

                            if os.path.exists(conflict_path) and not os.path.islink(
                                conflict_path
                            ):
                                backup_path = os.path.join(backup_dir, conflict_file)
                                os.makedirs(os.path.dirname(backup_path), exist_ok=True)

                                # Move to backup
                                subprocess.run(
                                    ["mv", conflict_path, backup_path], check=True
                                )
                                self.log(f"    Backed up {conflict_file}")

            # Now stow (should succeed after backup)
            try:
                subprocess.run(
                    ["stow", "--restow", "--target", home, pkg],
                    cwd=dotfiles_dir,
                    check=True,
                    capture_output=True,
                )
                self.log(f"  ✓ Stowed {pkg}")
            except subprocess.CalledProcessError as e:
                self.log(f"  ⚠ Failed to stow {pkg}: {e.stderr.decode()}")

        if os.path.exists(backup_dir):
            self.log(f"  Backups saved to: {backup_dir}")

    def link_scripts(self) -> None:
        """Symlink scripts from repo to ~/.local/bin."""
        self.log("Linking scripts to ~/.local/bin...")

        home = os.path.expanduser("~")
        bin_dir = os.path.join(home, ".local/bin")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(os.path.dirname(script_dir), "scripts")

        if not os.path.exists(scripts_dir):
            self.log(f"  ⚠ Scripts directory not found: {scripts_dir}")
            return

        # Ensure ~/.local/bin exists
        os.makedirs(bin_dir, exist_ok=True)

        # Find all executable scripts
        for script_file in os.listdir(scripts_dir):
            script_path = os.path.join(scripts_dir, script_file)

            # Skip non-files and non-executables
            if not os.path.isfile(script_path):
                continue
            if not (script_file.endswith(".py") or script_file.endswith(".sh")):
                continue

            # Create symlink name (duh-<name> without extension)
            script_name = os.path.splitext(script_file)[0]
            if not script_name.startswith("duh-"):
                link_name = f"duh-{script_name}"
            else:
                link_name = script_name

            link_path = os.path.join(bin_dir, link_name)

            try:
                # Remove existing symlink/file
                if os.path.lexists(link_path):
                    os.remove(link_path)

                # Create symlink
                os.symlink(script_path, link_path)
                self.log(f"  ✓ Linked {script_file} -> {link_name}")
            except Exception as e:
                self.log(f"  ⚠ Failed to link {script_file}: {e}")

    @property
    @abstractmethod
    def log_id(self) -> str:
        pass

    @abstractmethod
    def check_update(self) -> None:
        pass

    @abstractmethod
    def install(self, package: str) -> None:
        pass

    def build_from_source(self, repo_url: str, build_commands: List[str]) -> None:
        """Clone and build a package from source."""
        pkg_name = repo_url.split("/")[-1].replace(".git", "")
        clone_path = f"/tmp/{pkg_name}"

        self.log(f"  Building {pkg_name} from source...")

        # Remove if exists, start fresh
        if os.path.exists(clone_path):
            self.log(f"    Cleaning up existing directory {clone_path}")
            subprocess.run(["rm", "-rf", clone_path], check=True)

        self.log(f"    Cloning {repo_url}...")
        stdout = None if self.verbose else subprocess.DEVNULL
        stderr = None if self.verbose else subprocess.DEVNULL
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, clone_path],
            check=True,
            stdout=stdout,
            stderr=stderr,
        )

        for cmd in build_commands:
            self.log(f"    Running: {cmd}")
            subprocess.run(
                cmd,
                shell=True,
                cwd=clone_path,
                check=True,
                stdout=stdout,
                stderr=stderr,
            )

    @abstractmethod
    def add_repo(self, repo_info: str) -> None:
        pass

    def install_font(self, font_url: str) -> None:
        system = platform.system().lower()
        if system == "darwin":
            target_dir = os.path.expanduser("~/Library/Fonts")
        else:
            target_dir = os.path.expanduser("~/.local/share/fonts")

        self.log(f"  Installing font to {target_dir}...")

        os.makedirs(target_dir, exist_ok=True)
        font_file = os.path.basename(font_url)
        temp_path = f"/tmp/{font_file}"

        # Download font
        stdout = None if self.verbose else subprocess.DEVNULL
        stderr = None if self.verbose else subprocess.DEVNULL
        wget_args = ["wget", font_url, "-O", temp_path]
        if not self.verbose:
            wget_args.insert(1, "-q")
        subprocess.run(wget_args, check=True, stdout=stdout, stderr=stderr)

        # Unzip if it's a zip file
        if font_file.endswith(".zip"):
            unzip_args = ["unzip", "-o", temp_path, "-d", target_dir]
            if not self.verbose:
                unzip_args.insert(1, "-q")
            subprocess.run(unzip_args, check=True, stdout=stdout, stderr=stderr)
            subprocess.run(["rm", temp_path], check=True, stdout=stdout, stderr=stderr)
        else:
            subprocess.run(
                ["mv", temp_path, target_dir], check=True, stdout=stdout, stderr=stderr
            )

        # Refresh font cache
        if system != "darwin":
            fc_args = ["fc-cache", "-fv"] if self.verbose else ["fc-cache", "-f"]
            subprocess.run(fc_args, check=True, stdout=stdout, stderr=stderr)

    def brew_install(self, package: str) -> None:
        pass

    def yay_install(self, package: str) -> None:
        pass
