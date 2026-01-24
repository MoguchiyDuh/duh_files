#!/usr/bin/env python3
"""
Unified SSH Tool
Combines server hardening and bidirectional key exchange features.

This tool provides:
- SSH server hardening (Multi-distro support: Debian/Ubuntu, Arch, Fedora, macOS)
- Bidirectional SSH key exchange automation
"""

import argparse
import logging
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SSHToolError(Exception):
    """Base exception for SSH tool errors."""

    pass


class PermissionError(SSHToolError):
    """Raised when insufficient permissions are detected."""

    pass


class ConfigurationError(SSHToolError):
    """Raised when configuration is invalid."""

    pass


class ServerHardener:
    """
    Hardens SSH server configuration on Linux and macOS systems.

    Features:
    - Sets custom port
    - Disables password authentication
    - Enforces public key authentication
    - Fixes systemd socket/service issues (Debian/Ubuntu)
    - Distro-aware service management

    Args:
        public_key: SSH public key to add to authorized_keys
        port: SSH port number (default: 10022)
        config_path: Path to sshd_config (default: /etc/ssh/sshd_config)
    """

    DEFAULT_PORT = 10022
    DEFAULT_CONFIG_PATH = "/etc/ssh/sshd_config"

    def __init__(
        self,
        public_key: str,
        port: int = DEFAULT_PORT,
        config_path: str = DEFAULT_CONFIG_PATH,
    ):
        self.public_key = public_key.strip()
        self.port = self._validate_port(port)
        self.config_path = config_path
        self.settings = {
            "Port": str(self.port),
            "PasswordAuthentication": "no",
            "PubkeyAuthentication": "yes",
            "ChallengeResponseAuthentication": "no",
            "UsePAM": "no",
            "KbdInteractiveAuthentication": "no",
        }
        self.os_type, self.distro_id = self._detect_platform()
        self.service_name = self._get_service_name()
        logger.info(
            "Detected platform: %s (%s). Service name: %s",
            self.os_type,
            self.distro_id,
            self.service_name,
        )

    @staticmethod
    def _validate_port(port: int) -> int:
        """Validate SSH port number."""
        if not 1 <= port <= 65535:
            raise ConfigurationError(f"Port must be between 1-65535, got {port}")
        if port < 1024:
            logger.warning(
                "Using privileged port %d. Ensure you have appropriate permissions.",
                port,
            )
        return port

    def _detect_platform(self):
        """Detect OS and distribution."""
        system = platform.system().lower()
        distro_id = "unknown"

        if system == "linux":
            try:
                # Try to read /etc/os-release
                if os.path.exists("/etc/os-release"):
                    with open("/etc/os-release") as f:
                        for line in f:
                            if line.startswith("ID="):
                                distro_id = line.split("=")[1].strip().strip('"')
                                break
            except Exception:
                pass
        elif system == "darwin":
            distro_id = "macos"

        return system, distro_id

    def _get_service_name(self) -> str:
        """Determine SSH service name based on distro."""
        if self.os_type == "darwin":
            return "com.openssh.sshd"

        # Linux mappings
        if self.distro_id in ["ubuntu", "debian", "kali", "pop", "linuxmint"]:
            return "ssh"
        elif self.distro_id in [
            "fedora",
            "centos",
            "rhel",
            "almalinux",
            "rocky",
            "arch",
            "manjaro",
            "endeavouros",
        ]:
            return "sshd"

        return "sshd"  # Default fallback

    def ensure_authorized_keys(self) -> None:
        """
        Ensures the public key is in authorized_keys with correct permissions.
        """
        ssh_dir = Path.home() / ".ssh"
        auth_keys = ssh_dir / "authorized_keys"

        try:
            ssh_dir.mkdir(mode=0o700, exist_ok=True)
            logger.debug("SSH directory ensured: %s", ssh_dir)

            existing_keys = ""
            if auth_keys.exists():
                existing_keys = auth_keys.read_text()

            if self.public_key and self.public_key not in existing_keys:
                logger.info("Adding provided public key to %s", auth_keys)
                with open(auth_keys, "a") as f:
                    f.write(f"\n{self.public_key}\n")
            elif not self.public_key:
                logger.warning(
                    "No public key provided. Skipping authorized_keys update."
                )
            else:
                logger.info("Public key already exists in authorized_keys")

            if auth_keys.exists():
                auth_keys.chmod(0o600)
                logger.debug("Set permissions 0600 on %s", auth_keys)

        except (OSError, IOError) as e:
            raise SSHToolError(f"Failed to update authorized_keys: {e}") from e

    def update_sshd_config(self) -> None:
        """
        Modifies /etc/ssh/sshd_config with hardening settings.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"{self.config_path} not found.")

        try:
            logger.info("Updating %s...", self.config_path)

            # Backup original config
            backup_path = f"{self.config_path}.backup"
            if not os.path.exists(backup_path):
                import shutil

                shutil.copy2(self.config_path, backup_path)
                logger.info("Created backup: %s", backup_path)

            with open(self.config_path, "r") as f:
                lines = f.readlines()

            new_lines = []
            applied_keys = set()

            # Update existing keys
            for line in lines:
                match = re.match(r"^\s*#?\s*(\w+)\s+", line)
                if match:
                    key = match.group(1)
                    if key in self.settings:
                        new_lines.append(f"{key} {self.settings[key]}\n")
                        applied_keys.add(key)
                        logger.debug(
                            "Updated setting: %s = %s", key, self.settings[key]
                        )
                        continue
                new_lines.append(line)

            # Append missing keys
            for key, value in self.settings.items():
                if key not in applied_keys:
                    new_lines.append(f"{key} {value}\n")
                    logger.debug("Added setting: %s = %s", key, value)

            with open(self.config_path, "w") as f:
                f.writelines(new_lines)

            logger.info("SSH configuration updated successfully")

        except (OSError, IOError) as e:
            raise SSHToolError(f"Failed to update SSH config: {e}") from e

    def fix_systemd_socket_issue(self) -> None:
        """
        Switches systemd from ssh.socket to ssh.service.
        Only runs on Debian-based systems where this is a known issue.
        """
        if self.distro_id not in ["debian", "ubuntu", "kali", "pop", "linuxmint"]:
            return

        logger.info("Checking for Debian ssh.socket issue...")

        # Check if ssh.socket is active
        try:
            subprocess.run(
                ["systemctl", "is-active", "--quiet", "ssh.socket"], check=True
            )
            logger.info("ssh.socket detected. Transitioning to ssh.service...")
        except subprocess.CalledProcessError:
            logger.debug("ssh.socket not active. Skipping.")
            return

        cmds = [
            (["systemctl", "stop", "ssh.socket"], "Stopping ssh.socket"),
            (["systemctl", "disable", "ssh.socket"], "Disabling ssh.socket"),
            (["systemctl", "mask", "ssh.socket"], "Masking ssh.socket"),
            (["systemctl", "unmask", "ssh.service"], "Unmasking ssh.service"),
            (["systemctl", "enable", "ssh.service"], "Enabling ssh.service"),
        ]

        for cmd, description in cmds:
            try:
                subprocess.run(
                    cmd, check=True, capture_output=True, text=True, timeout=10
                )
                logger.debug(description)
            except Exception as e:
                logger.warning("Failed to run %s: %s", " ".join(cmd), e)

    def restart_service(self) -> None:
        """Restart the SSH service using the appropriate init system."""
        logger.info("Restarting %s...", self.service_name)

        try:
            if self.os_type == "linux":
                subprocess.run(
                    ["systemctl", "restart", self.service_name],
                    check=True,
                    timeout=15,
                )
            elif self.os_type == "darwin":
                # macOS: try to unload/load
                plist_path = "/System/Library/LaunchDaemons/ssh.plist"
                if os.path.exists(plist_path):
                    subprocess.run(["launchctl", "unload", plist_path], check=False)
                    subprocess.run(["launchctl", "load", "-w", plist_path], check=True)
                else:
                    logger.warning(
                        "Could not find ssh.plist to restart service on macOS."
                    )
                    print(
                        "Please restart Remote Login manually: System Preferences -> Sharing"
                    )

            logger.info("Service restarted successfully")
        except subprocess.CalledProcessError as e:
            raise SSHToolError(f"Failed to restart service: {e}") from e

    def run(self) -> None:
        """Execute server hardening process."""
        if os.getuid() != 0:
            raise PermissionError(
                "Server hardening requires sudo/root privileges. "
                "Run with: sudo python3 ssh_tool.py harden ..."
            )

        try:
            self.ensure_authorized_keys()
            self.update_sshd_config()
            self.fix_systemd_socket_issue()
            self.restart_service()

            logger.info("Hardening complete. Port: %d, Auth: Pubkey Only.", self.port)
            print(f"\n✓ SSH server hardened successfully on port {self.port}")
            print(f"  - Platform: {self.distro_id}")
            print(f"  - Service: {self.service_name}")
            print(f"  - Password authentication: disabled")
            print(f"  - Public key authentication: enabled")
            print(f"  - Config backup: {self.config_path}.backup")

        except SSHToolError:
            raise
        except Exception as e:
            raise SSHToolError(f"Unexpected error during hardening: {e}") from e


class KeyExchanger:
    """
    Manages bidirectional SSH key exchange.

    Features:
    - Generates local ED25519 key if missing
    - Copies local key to remote host
    - Fetches remote key to local host

    Args:
        remote_host: Remote hostname or IP address
        remote_user: Username on remote host
        port: SSH port number (default: 22)
    """

    DEFAULT_PORT = 22
    DEFAULT_KEY_TYPE = "ed25519"

    def __init__(self, remote_host: str, remote_user: str, port: int = DEFAULT_PORT):
        self.remote_host = remote_host.strip()
        self.remote_user = remote_user.strip()
        self.port = self._validate_port(port)
        self.ssh_dir = Path.home() / ".ssh"
        self.key_path = self.ssh_dir / f"id_{self.DEFAULT_KEY_TYPE}"
        self.pub_key_path = self.ssh_dir / f"id_{self.DEFAULT_KEY_TYPE}.pub"

    @staticmethod
    def _validate_port(port: int) -> int:
        """Validate SSH port number."""
        if not 1 <= port <= 65535:
            raise ConfigurationError(f"Port must be between 1-65535, got {port}")
        return port

    def ensure_ssh_dir(self) -> None:
        """Ensure .ssh directory exists with correct permissions."""
        try:
            self.ssh_dir.mkdir(mode=0o700, exist_ok=True)
            logger.debug("SSH directory ensured: %s", self.ssh_dir)
        except OSError as e:
            raise SSHToolError(f"Failed to create SSH directory: {e}") from e

    def generate_local_key(self) -> bool:
        """Generate SSH key pair if it doesn't exist."""
        if self.key_path.exists():
            logger.info("Local key already exists: %s", self.key_path)
            return False

        try:
            logger.info(
                "Generating %s key pair at %s...",
                self.DEFAULT_KEY_TYPE.upper(),
                self.key_path,
            )
            subprocess.run(
                [
                    "ssh-keygen",
                    "-t",
                    self.DEFAULT_KEY_TYPE,
                    "-f",
                    str(self.key_path),
                    "-N",
                    "",
                    "-C",
                    f"{os.getenv('USER', 'user')}@{os.uname().nodename}",
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            logger.info("Key pair generated successfully")
            return True
        except subprocess.CalledProcessError as e:
            raise SSHToolError(f"Failed to generate SSH key: {e.stderr}") from e
        except subprocess.TimeoutExpired as e:
            raise SSHToolError("SSH key generation timed out") from e

    def send_local_key(self) -> None:
        """Copy public key to remote machine."""
        if not self.pub_key_path.exists():
            raise FileNotFoundError(f"Public key not found: {self.pub_key_path}")

        try:
            pub_key = self.pub_key_path.read_text().strip()
            remote = f"{self.remote_user}@{self.remote_host}"

            logger.info("Copying local key to %s...", remote)

            # Use a list to avoid shell injection issues
            ssh_cmd = [
                "ssh",
                "-p",
                str(self.port),
                "-o",
                "StrictHostKeyChecking=ask",
                remote,
                (
                    "mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
                    f"grep -qxF '{pub_key}' ~/.ssh/authorized_keys 2>/dev/null || "
                    f"echo '{pub_key}' >> ~/.ssh/authorized_keys && "
                    "chmod 600 ~/.ssh/authorized_keys"
                ),
            ]

            subprocess.run(ssh_cmd, check=True, timeout=30)
            logger.info("Local key successfully copied to remote")

        except subprocess.CalledProcessError as e:
            raise SSHToolError(
                f"Failed to copy key to remote: {e}\n"
                "Ensure you can connect to the remote host with password authentication."
            ) from e
        except subprocess.TimeoutExpired as e:
            raise SSHToolError("Key transfer timed out") from e
        except (OSError, IOError) as e:
            raise SSHToolError(f"Failed to read local public key: {e}") from e

    def fetch_remote_key(self) -> None:
        """Fetch public key from remote and add to local authorized_keys."""
        remote = f"{self.remote_user}@{self.remote_host}"

        try:
            logger.info("Fetching public key from %s...", remote)

            # Ensure remote has a key. If not, generate one.
            subprocess.run(
                [
                    "ssh",
                    "-p",
                    str(self.port),
                    remote,
                    f"test -f ~/.ssh/id_{self.DEFAULT_KEY_TYPE}.pub || "
                    f"ssh-keygen -t {self.DEFAULT_KEY_TYPE} -f ~/.ssh/id_{self.DEFAULT_KEY_TYPE} -N '' "
                    f"-C '{self.remote_user}@{self.remote_host}'",
                ],
                check=True,
                timeout=30,
            )

            # Fetch remote public key content
            result = subprocess.run(
                [
                    "ssh",
                    "-p",
                    str(self.port),
                    remote,
                    f"cat ~/.ssh/id_{self.DEFAULT_KEY_TYPE}.pub",
                ],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            remote_pub_key = result.stdout.strip()
            if not remote_pub_key:
                raise SSHToolError(
                    "Could not retrieve remote public key (empty response)"
                )

            # Add to local authorized_keys
            auth_keys_path = self.ssh_dir / "authorized_keys"

            existing = ""
            if auth_keys_path.exists():
                existing = auth_keys_path.read_text()

            if remote_pub_key in existing:
                logger.info("Remote key already in local authorized_keys")
                return

            with auth_keys_path.open("a") as f:
                f.write(f"\n{remote_pub_key}\n")

            auth_keys_path.chmod(0o600)
            logger.info("Remote key added to local authorized_keys")

        except subprocess.CalledProcessError as e:
            raise SSHToolError(f"Failed to fetch remote key: {e}") from e
        except subprocess.TimeoutExpired as e:
            raise SSHToolError("Remote key fetch timed out") from e
        except (OSError, IOError) as e:
            raise SSHToolError(f"Failed to update local authorized_keys: {e}") from e

    def run_exchange(self) -> None:
        """Setup SSH keys in both directions."""
        try:
            self.ensure_ssh_dir()
            self.generate_local_key()

            print("\n=== Phase 1: Local → Remote ===")
            self.send_local_key()

            print("\n=== Phase 2: Remote → Local ===")
            self.fetch_remote_key()

            print("\n✓ Bidirectional SSH key setup complete")

        except SSHToolError:
            raise
        except Exception as e:
            raise SSHToolError(f"Unexpected error during key exchange: {e}") from e

    def test_connection(self) -> bool:
        """Test SSH connection using key-based authentication."""
        remote = f"{self.remote_user}@{self.remote_host}"
        logger.info("Testing connection to %s...", remote)

        try:
            subprocess.run(
                [
                    "ssh",
                    "-p",
                    str(self.port),
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=5",
                    remote,
                    "echo 'Connection successful'",
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            logger.info("Connection test passed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Connection test failed: %s", e.stderr if e.stderr else str(e))
            return False
        except subprocess.TimeoutExpired:
            logger.error("Connection test timed out")
            return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Unified SSH Tool: Server Hardening & Key Exchange",
        epilog="Examples:\n"
        "  %(prog)s harden --key 'ssh-ed25519 AAAA...'\n"
        "  %(prog)s exchange user@example.com --port 2222\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True, help="Action to perform"
    )

    # Subcommand: harden
    parser_harden = subparsers.add_parser(
        "harden",
        help="Harden SSH server (requires root)",
        description="Harden SSH server configuration on Linux/macOS systems",
    )
    parser_harden.add_argument(
        "--port",
        "-p",
        type=int,
        default=ServerHardener.DEFAULT_PORT,
        help=f"New SSH port (default: {ServerHardener.DEFAULT_PORT})",
    )
    parser_harden.add_argument(
        "--key", "-k", type=str, default="", help="Public key to add to authorized_keys"
    )
    parser_harden.add_argument(
        "--config",
        type=str,
        default=ServerHardener.DEFAULT_CONFIG_PATH,
        help=f"Path to sshd_config (default: {ServerHardener.DEFAULT_CONFIG_PATH})",
    )

    # Subcommand: exchange
    parser_exchange = subparsers.add_parser(
        "exchange",
        help="Bidirectional key exchange with a remote host",
        description="Setup bidirectional SSH key authentication with a remote host",
    )
    parser_exchange.add_argument("host", help="Remote host IP or hostname")
    parser_exchange.add_argument("user", help="Remote username")
    parser_exchange.add_argument(
        "--port",
        "-p",
        type=int,
        default=KeyExchanger.DEFAULT_PORT,
        help=f"Remote SSH port (default: {KeyExchanger.DEFAULT_PORT})",
    )
    parser_exchange.add_argument(
        "--no-test", action="store_true", help="Skip connection test after setup"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.command == "harden":
            hardener = ServerHardener(args.key, args.port, args.config)
            hardener.run()
            return 0

        elif args.command == "exchange":
            exchanger = KeyExchanger(args.host, args.user, args.port)
            exchanger.run_exchange()

            if not args.no_test:
                if exchanger.test_connection():
                    print("✓ SSH connection verified")
                    return 0
                else:
                    print("✗ SSH connection test failed")
                    print(
                        "  This might be normal if the remote server has been hardened."
                    )
                    print(
                        f"  Try connecting manually: ssh -p {args.port} {args.user}@{args.host}"
                    )
                    return 1
            return 0

    except PermissionError as e:
        logger.error("Permission error: %s", e)
        return 1
    except ConfigurationError as e:
        logger.error("Configuration error: %s", e)
        return 1
    except SSHToolError as e:
        logger.error("SSH tool error: %s", e)
        return 1
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
