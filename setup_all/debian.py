import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, List, Tuple

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
            # 2. Development Tools
            ("openssl", "manager", "libssl-dev"),
            ("openssh", "manager", "ssh"),
            ("curl", "manager", "curl"),
            ("wget", "manager", "wget"),
            ("cmake", "manager", "cmake"),
            ("ninja", "manager", "ninja-build"),
            ("clang", "manager", "clang"),
            ("gettext", "manager", "gettext"),
            ("libtool", "manager", "libtool-bin"),
            ("autoconf", "manager", "autoconf"),
            ("automake", "manager", "automake"),
            ("pkg-config", "manager", "pkg-config"),
            # 3. Shell & Terminal
            ("zsh", "manager", "zsh"),
            ("oh-my-zsh", "script", self._install_ohmyzsh),
            ("powerlevel10k", "script", self._install_p10k),
            (
                "zsh-autosuggestions",
                "script",
                self._install_zsh_plugin("zsh-autosuggestions"),
            ),
            (
                "zsh-syntax-highlighting",
                "script",
                self._install_zsh_plugin("zsh-syntax-highlighting"),
            ),
            ("zsh-completions", "script", self._install_zsh_plugin("zsh-completions")),
            ("tmux", "manager", "tmux"),
            ("tmux-plugins", "script", self._install_tmux_plugins),
            ("stow", "manager", "stow"),
            # 4. Fonts
            ("nerd-fonts", "script", self._install_nerd_fonts),
            # 5. Modern CLI Tools
            ("gh", "manager", "gh"),  # GitHub CLI has official apt repo
            (
                "zoxide",
                "github",
                ("ajeetdsouza/zoxide", "zoxide-*-x86_64-unknown-linux-musl.tar.gz"),
            ),
            ("fzf", "github", ("junegunn/fzf", "fzf-*-linux_amd64.tar.gz")),
            ("eza", "script", self._install_eza),
            (
                "bat",
                "github",
                ("sharkdp/bat", "bat-v*-x86_64-unknown-linux-musl.tar.gz"),
            ),
            ("bat-alias", "script", self._create_bat_alias),
            ("fd", "github", ("sharkdp/fd", "fd-v*-x86_64-unknown-linux-musl.tar.gz")),
            (
                "ripgrep",
                "github",
                ("BurntSushi/ripgrep", "ripgrep-*-x86_64-unknown-linux-musl.tar.gz"),
            ),
            ("rsync", "manager", "rsync"),
            (
                "btop",
                "github",
                ("aristocratos/btop", "btop-x86_64-unknown-linux-musl.tbz"),
            ),
            (
                "fastfetch",
                "github",
                ("fastfetch-cli/fastfetch", "fastfetch-linux-amd64.tar.gz"),
            ),
            ("jq", "manager", "jq"),
            ("yq", "github", ("mikefarah/yq", "yq_linux_amd64.tar.gz")),
            ("nnn", "manager", "nnn"),
            ("direnv", "github", ("direnv/direnv", "direnv.linux-amd64")),
            (
                "hyperfine",
                "github",
                ("sharkdp/hyperfine", "hyperfine-v*-x86_64-unknown-linux-musl.tar.gz"),
            ),
            (
                "delta",
                "github",
                ("dandavison/delta", "delta-*-x86_64-unknown-linux-musl.tar.gz"),
            ),
            # Archive tools
            ("zip", "manager", "zip"),
            ("unzip", "manager", "unzip"),
            ("p7zip", "manager", "p7zip-full"),
            # 6. Container & Database
            ("docker", "script", self._install_docker),
            ("redis", "manager", "redis-server"),
            ("postgres", "manager", "postgresql postgresql-contrib"),
            # 7. Programming Languages
            ("python3", "manager", "python3 python3-pip python3-venv"),
            ("python-symlink", "script", self._create_python_symlink),
            ("nodejs", "script", self._install_nodejs),
            ("go", "script", self._install_go),
            ("rust", "script", self._install_rust),
            ("uv", "script", self._install_uv),
            # 8. Advanced Tools (built with language package managers)
            ("tealdeer", "cargo", "tealdeer"),
            ("dust", "cargo", "du-dust"),
            (
                "lazygit",
                "github",
                ("jesseduffield/lazygit", "lazygit_*_linux_x86_64.tar.gz"),
            ),
            (
                "lazydocker",
                "github",
                ("jesseduffield/lazydocker", "lazydocker_*_Linux_x86_64.tar.gz"),
            ),
            (
                "lazysql",
                "github",
                ("jorgerojas26/lazysql", "lazysql_Linux_x86_64.tar.gz"),
            ),
            ("duf", "go", "github.com/muesli/duf@latest"),
            # 9. Neovim (pre-built binary)
            ("neovim", "script", self._install_neovim_binary),
        ]

    def check_update(self) -> None:
        """Update package cache and upgrade system."""
        self.log("Updating apt cache and upgrading system...")
        self._run_silent(["sudo", "apt", "update"])
        self._run_silent(["sudo", "apt", "upgrade", "-y"])

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
        """Install via apt."""
        # Handle multiple packages
        packages = package.split()
        all_installed = all(self.is_package_installed(pkg) for pkg in packages)

        if all_installed:
            return

        self.log(f"  Installing {package} via apt...")
        install_args = ["sudo", "apt", "install", "-y"]
        if self.force:
            install_args.append("--reinstall")
        self._run_silent(install_args + packages)
        self._run_silent(["sudo", "apt", "update"])

    def add_repo(self, repo_info: str) -> None:
        """Add repository (PPA or custom source)."""
        self.log(f"  Adding repo: {repo_info}")
        if repo_info.startswith("ppa:"):
            self._run_silent(["sudo", "add-apt-repository", "-y", repo_info])
        else:
            sources_file = Path("/etc/apt/sources.list.d/custom.list")
            with open(sources_file, "a") as f:
                f.write(f"\n{repo_info}\n")
        self._run_silent(["sudo", "apt", "update"])

    # Helper methods
    def _run_silent(self, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run command with optional verbosity."""
        stdout = None if self.verbose else subprocess.DEVNULL
        stderr = None if self.verbose else subprocess.DEVNULL
        return subprocess.run(cmd, check=True, stdout=stdout, stderr=stderr)

    # Installation methods for specific tools
    def _install_ohmyzsh(self) -> None:
        """Install Oh My Zsh."""
        oh_my_zsh_dir = Path.home() / ".oh-my-zsh"
        if oh_my_zsh_dir.exists():
            return

        self.log("  Installing Oh My Zsh...")
        subprocess.run(
            'RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL if not self.verbose else None,
            stderr=subprocess.DEVNULL if not self.verbose else None,
        )

    def _install_p10k(self) -> None:
        """Install Powerlevel10k theme."""
        p10k_dir = Path.home() / ".oh-my-zsh" / "custom" / "themes" / "powerlevel10k"
        if p10k_dir.exists():
            return

        self.log("  Installing Powerlevel10k...")
        p10k_dir.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            [
                "git",
                "clone",
                "--depth=1",
                "https://github.com/romkatv/powerlevel10k.git",
                str(p10k_dir),
            ],
            check=True,
            stdout=subprocess.DEVNULL if not self.verbose else None,
            stderr=subprocess.DEVNULL if not self.verbose else None,
        )

    def _install_zsh_plugin(self, plugin_name: str) -> Callable:
        """Return a function that installs a zsh plugin."""

        def install() -> None:
            plugin_dir = Path.home() / ".oh-my-zsh" / "custom" / "plugins" / plugin_name
            if plugin_dir.exists():
                return

            self.log(f"  Installing {plugin_name}...")
            plugin_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    f"https://github.com/zsh-users/{plugin_name}.git",
                    str(plugin_dir),
                ],
                check=True,
                stdout=subprocess.DEVNULL if not self.verbose else None,
                stderr=subprocess.DEVNULL if not self.verbose else None,
            )

        return install

    def _install_tmux_plugins(self) -> None:
        """Install common tmux plugins."""
        plugins = [
            "tmux-continuum",
            "tmux-cpu",
            "tmux-prefix-highlight",
            "tmux-resurrect",
        ]

        for plugin in plugins:
            plugin_dir = Path.home() / ".config" / "tmux" / "plugins" / plugin
            if plugin_dir.exists():
                continue

            self.log(f"  Installing {plugin}...")
            plugin_dir.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    f"https://github.com/tmux-plugins/{plugin}.git",
                    str(plugin_dir),
                ],
                check=True,
                stdout=subprocess.DEVNULL if not self.verbose else None,
                stderr=subprocess.DEVNULL if not self.verbose else None,
            )

    def _install_nerd_fonts(self) -> None:
        """Install FiraCode Nerd Font."""
        font_dir = Path.home() / ".local" / "share" / "fonts"
        font_dir.mkdir(parents=True, exist_ok=True)

        if (font_dir / "FiraCodeNerdFont-Regular.ttf").exists():
            return

        self.log("  Installing Nerd Fonts...")
        temp_dir = Path(tempfile.mkdtemp())
        font_zip = temp_dir / "FiraCode.zip"

        subprocess.run(
            [
                "curl",
                "-sL",
                "-o",
                str(font_zip),
                "https://github.com/ryanoasis/nerd-fonts/releases/latest/download/FiraCode.zip",
            ],
            check=True,
        )
        subprocess.run(["unzip", "-q", str(font_zip), "-d", str(font_dir)], check=True)
        subprocess.run(
            ["fc-cache", "-fv"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        shutil.rmtree(temp_dir)

    def _create_bat_alias(self) -> None:
        """Create bat symlink/alias (Debian installs it as batcat)."""
        local_bin = Path.home() / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)

        bat_link = local_bin / "bat"
        if bat_link.exists():
            return

        # If installed via apt, it's called batcat
        if shutil.which("batcat"):
            self.log("  Creating bat alias for batcat...")
            bat_link.symlink_to("/usr/bin/batcat")
        # If installed via GitHub release, it should already be named bat
        elif (local_bin / "batcat").exists():
            self.log("  Creating bat alias...")
            bat_link.symlink_to(local_bin / "batcat")

    def _create_python_symlink(self) -> None:
        """Create python -> python3 symlink in ~/.local/bin."""
        local_bin = Path.home() / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)

        python_link = local_bin / "python"
        if python_link.exists() or shutil.which("python"):
            return

        python3_path = shutil.which("python3")
        if python3_path:
            self.log("  Creating python -> python3 symlink...")
            python_link.symlink_to(python3_path)

    def _install_eza(self) -> None:
        """Install eza from official apt repository."""
        keyring_path = Path("/etc/apt/keyrings/gierens.gpg")
        if not keyring_path.exists():
            self.log("  Setting up eza repository...")
            subprocess.run(["sudo", "mkdir", "-p", "/etc/apt/keyrings"], check=True)
            subprocess.run(
                "wget -qO- https://raw.githubusercontent.com/eza-community/eza/main/deb.asc | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg",
                shell=True,
                check=True,
            )
            subprocess.run(
                'echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" | sudo tee /etc/apt/sources.list.d/gierens.list',
                shell=True,
                check=True,
            )
            subprocess.run(
                ["sudo", "chmod", "644", "/etc/apt/keyrings/gierens.gpg"], check=True
            )
            self._run_silent(["sudo", "apt", "update"])

        self.install("eza")

    def _install_docker(self) -> None:
        """Install Docker from official repository."""
        if shutil.which("docker"):
            return

        self.log("  Installing Docker...")
        temp_script = Path(tempfile.mktemp(suffix=".sh"))
        subprocess.run(
            ["curl", "-fsSL", "https://get.docker.com", "-o", str(temp_script)],
            check=True,
        )
        subprocess.run(["sudo", "sh", str(temp_script)], check=True)
        temp_script.unlink()

        # Add user to docker group
        username = os.getenv("USER")
        subprocess.run(["sudo", "usermod", "-aG", "docker", username], check=True)  # type: ignore

    def _install_nodejs(self) -> None:
        """Install Node.js LTS via NodeSource."""
        if shutil.which("node"):
            return

        self.log("  Installing Node.js LTS...")
        subprocess.run(
            "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL if not self.verbose else None,
        )
        self.install("nodejs")

    def _install_go(self) -> None:
        """Install latest Go release."""
        if shutil.which("go"):
            return

        self.log("  Installing Go...")
        # Get latest version
        result = subprocess.run(
            ["curl", "-sL", "https://go.dev/VERSION?m=text"],
            capture_output=True,
            text=True,
            check=True,
        )
        version = result.stdout.strip().split("\n")[0]  # e.g., "go1.21.5"

        archive = f"{version}.linux-amd64.tar.gz"
        url = f"https://go.dev/dl/{archive}"

        temp_dir = Path(tempfile.mkdtemp())
        archive_path = temp_dir / archive

        subprocess.run(["curl", "-sL", "-o", str(archive_path), url], check=True)
        subprocess.run(["sudo", "rm", "-rf", "/usr/local/go"], check=True)
        subprocess.run(
            ["sudo", "tar", "-C", "/usr/local", "-xzf", str(archive_path)], check=True
        )

        shutil.rmtree(temp_dir)

    def _install_rust(self) -> None:
        """Install Rust via rustup."""
        if shutil.which("rustc"):
            return

        self.log("  Installing Rust...")
        subprocess.run(
            "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL if not self.verbose else None,
        )

    def _install_uv(self) -> None:
        """Install uv (Python package manager)."""
        if shutil.which("uv"):
            return

        self.log("  Installing uv...")
        subprocess.run(
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL if not self.verbose else None,
        )

    def _install_neovim_binary(self) -> None:
        """Install Neovim from pre-built binary."""
        if shutil.which("nvim"):
            return

        self.log("  Installing Neovim from pre-built binary...")
        temp_dir = Path(tempfile.mkdtemp())

        # Download latest release
        download_url = "https://github.com/neovim/neovim/releases/latest/download/nvim-linux-x86_64.tar.gz"
        archive_path = temp_dir / "nvim.tar.gz"

        subprocess.run(
            ["curl", "-sL", "-o", str(archive_path), download_url],
            check=True,
        )

        # Extract
        extract_dir = temp_dir / "nvim-extracted"
        extract_dir.mkdir()
        subprocess.run(
            ["tar", "xzf", str(archive_path), "-C", str(extract_dir)],
            check=True,
        )

        # Copy to ~/.local
        local_dir = Path.home() / ".local"
        nvim_dir = extract_dir / "nvim-linux-x86_64"

        if nvim_dir.exists():
            # Copy bin, lib, share directories
            for subdir in ["bin", "lib", "share"]:
                src = nvim_dir / subdir
                dst = local_dir / subdir
                if src.exists():
                    dst.mkdir(parents=True, exist_ok=True)
                    subprocess.run(
                        ["cp", "-r", f"{src}/.", str(dst)],
                        check=True,
                    )

        shutil.rmtree(temp_dir)
