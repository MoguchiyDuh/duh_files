#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path


class SSHManager:
    def __init__(self, public_key: str, port: int = 10022):
        self.public_key = public_key.strip()
        self.port = port
        self.config_path = "/etc/ssh/sshd_config"
        self.settings = {
            "Port": str(self.port),
            "PasswordAuthentication": "no",
            "PubkeyAuthentication": "yes",
            "ChallengeResponseAuthentication": "no",
            "UsePAM": "no",
            "KbdInteractiveAuthentication": "no",
        }

    def setup_authorized_keys(self) -> None:
        """Ensures the public key is in authorized_keys with correct perms."""
        ssh_dir = Path.home() / ".ssh"
        auth_keys = ssh_dir / "authorized_keys"

        ssh_dir.mkdir(mode=0o700, exist_ok=True)

        # Avoid duplicate entries
        existing_keys = ""
        if auth_keys.exists():
            existing_keys = auth_keys.read_text()

        if self.public_key not in existing_keys:
            with open(auth_keys, "a") as f:
                f.write(f"\n{self.public_key}\n")

        auth_keys.chmod(0o600)

    def update_sshd_config(self) -> None:
        """Modifies /etc/ssh/sshd_config with hardening settings."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"{self.config_path} not found.")

        with open(self.config_path, "r") as f:
            lines = f.readlines()

        new_lines = []
        applied_keys = set()

        for line in lines:
            match = re.match(r"^\s*#?\s*(\w+)\s+", line)
            if match:
                key = match.group(1)
                if key in self.settings:
                    new_lines.append(f"{key} {self.settings[key]}\n")
                    applied_keys.add(key)
                    continue
            new_lines.append(line)

        for key, value in self.settings.items():
            if key not in applied_keys:
                new_lines.append(f"{key} {value}\n")

        with open(self.config_path, "w") as f:
            f.writelines(new_lines)

    def transition_systemd_units(self) -> None:
        """Switches systemd from ssh.socket to ssh.service."""
        cmds = [
            ["systemctl", "stop", "ssh.socket"],
            ["systemctl", "disable", "ssh.socket"],
            ["systemctl", "mask", "ssh.socket"],
            ["systemctl", "unmask", "ssh.service"],
            ["systemctl", "enable", "ssh.service"],
            ["systemctl", "restart", "ssh.service"],
        ]
        for cmd in cmds:
            subprocess.run(cmd, check=False, capture_output=True)

    def run(self) -> None:
        if os.getuid() != 0:
            print("This script requires sudo/root privileges to modify SSH config.")
            sys.exit(1)

        self.setup_authorized_keys()
        self.update_sshd_config()
        self.transition_systemd_units()
        print(f"Setup complete. Port: {self.port}, Auth: Pubkey Only.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sudo ./script.py '<public_key_string>'")
        sys.exit(1)

    manager = SSHManager(sys.argv[1])
    manager.run()
