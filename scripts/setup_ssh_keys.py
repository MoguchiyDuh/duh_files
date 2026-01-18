"""SSH key setup automation for bidirectional key exchange."""

import subprocess
import sys
from pathlib import Path


class SSHKeyManager:
    """Manages SSH key generation and distribution."""

    def __init__(self, remote_host: str, remote_user: str, port: int = 22):
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.port = port
        self.ssh_dir = Path.home() / ".ssh"
        self.key_path = self.ssh_dir / "id_ed25519"
        self.pub_key_path = self.ssh_dir / "id_ed25519.pub"

    def ensure_ssh_dir(self) -> None:
        """Ensure .ssh directory exists with correct permissions."""
        self.ssh_dir.mkdir(mode=0o700, exist_ok=True)

    def generate_key_if_missing(self) -> bool:
        """Generate SSH key pair if it doesn't exist."""
        if self.key_path.exists():
            print(f"Key already exists: {self.key_path}")
            return False

        print(f"Generating ED25519 key pair at {self.key_path}...")
        subprocess.run(
            ["ssh-keygen", "-t", "ed25519", "-f", str(self.key_path), "-N", ""],
            check=True,
        )
        return True

    def copy_key_to_remote(self) -> None:
        """Copy public key to remote machine."""
        if not self.pub_key_path.exists():
            raise FileNotFoundError(f"Public key not found: {self.pub_key_path}")

        pub_key = self.pub_key_path.read_text().strip()
        remote = f"{self.remote_user}@{self.remote_host}"

        print(f"Copying key to {remote}...")

        # Create .ssh directory and append key to authorized_keys on remote
        cmd = (
            f"mkdir -p ~/.ssh && chmod 700 ~/.ssh && "
            f"echo '{pub_key}' >> ~/.ssh/authorized_keys && "
            f"chmod 600 ~/.ssh/authorized_keys"
        )

        subprocess.run(["ssh", "-p", str(self.port), remote, cmd], check=True)

    def fetch_remote_key(self) -> None:
        """Fetch public key from remote and add to local authorized_keys."""
        remote = f"{self.remote_user}@{self.remote_host}"

        print(f"Fetching public key from {remote}...")

        # Ensure remote has a key
        subprocess.run(
            [
                "ssh",
                "-p",
                str(self.port),
                remote,
                "test -f ~/.ssh/id_ed25519.pub || ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ''",
            ],
            check=True,
        )

        # Fetch remote public key
        result = subprocess.run(
            ["ssh", "-p", str(self.port), remote, "cat ~/.ssh/id_ed25519.pub"],
            capture_output=True,
            text=True,
            check=True,
        )

        remote_pub_key = result.stdout.strip()

        # Add to local authorized_keys
        auth_keys_path = self.ssh_dir / "authorized_keys"

        if auth_keys_path.exists():
            existing = auth_keys_path.read_text()
            if remote_pub_key in existing:
                print("Remote key already in authorized_keys")
                return

        with auth_keys_path.open("a") as f:
            f.write(f"\n{remote_pub_key}\n")

        auth_keys_path.chmod(0o600)
        print("Remote key added to authorized_keys")

    def setup_bidirectional(self) -> None:
        """Setup SSH keys in both directions."""
        self.ensure_ssh_dir()
        self.generate_key_if_missing()

        print("\n=== Setting up local -> remote ===")
        self.copy_key_to_remote()

        print("\n=== Setting up remote -> local ===")
        self.fetch_remote_key()

        print("\n✓ Bidirectional SSH key setup complete")

    def test_connection(self) -> bool:
        """Test SSH connection."""
        remote = f"{self.remote_user}@{self.remote_host}"
        print(f"\nTesting connection to {remote}...")

        try:
            subprocess.run(
                [
                    "ssh",
                    "-p",
                    str(self.port),
                    "-o",
                    "BatchMode=yes",
                    remote,
                    "echo 'Connection successful'",
                ],
                check=True,
                timeout=5,
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False


def main():
    """Main entry point."""
    REMOTE_HOST = input("remote host ip: ")
    REMOTE_USER = input("remote host username: ")
    REMOTE_PORT = input("remote port (default 22): ").strip() or "22"

    manager = SSHKeyManager(REMOTE_HOST, REMOTE_USER, int(REMOTE_PORT))

    try:
        manager.setup_bidirectional()

        if manager.test_connection():
            print("✓ SSH connection test passed")
            sys.exit(0)
        else:
            print("✗ SSH connection test failed")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
