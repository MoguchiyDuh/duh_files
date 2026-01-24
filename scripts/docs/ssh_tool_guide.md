# SSH Tool (`ssh_tool.py`) Guide

A unified utility designed to streamline SSH security and connectivity. It combines server-side hardening for Linux/macOS systems with a distro-agnostic client-side key exchange automator.

---

## Subcommands

### 1. `harden` (Server-Side)

Secures an SSH server by enforcing best-practice security policies. **This command requires root privileges.**

**Usage:** `sudo ssh_tool.py harden [OPTIONS]`

**Features:**

- **Port Customization**: Moves SSH from default port 22 to a custom port (default: 10022) to reduce scanning noise.
- **Auth Lockdown**: Disables `PasswordAuthentication`, `ChallengeResponseAuthentication`, and `PAM`. Enforces `PubkeyAuthentication`.
- **Key Installation**: Automatically adds a provided public key to the `authorized_keys` file of the user running the script (or root).
- **Multi-Distro Support**:
  - **Debian/Ubuntu**: Detects and fixes `ssh.socket` vs `ssh.service` conflicts.
  - **Arch/Fedora**: Identifies `sshd` service correctly.
  - **macOS**: Identifies `com.openssh.sshd` and uses `launchctl`.

**Options:**

- `--port, -p N`: Target SSH port (Default: 10022).
- `--key, -k STRING`: The public key string to authorize.
- `--config FILE`: Path to `sshd_config` (Default: `/etc/ssh/sshd_config`).

---

### 2. `exchange` (Client-Side)

Automates the bidirectional exchange of SSH keys between the local machine and a remote host to enable password-less login in both directions.

**Usage:** `ssh_tool.py exchange <HOST> <USER> [OPTIONS]`

**Workflow:**

1.  **Local Generation**: Checks for `~/.ssh/id_ed25519`. Generates a new key pair if one does not exist.
2.  **Push (Local -> Remote)**: Copies the local public key to the remote host's `authorized_keys`. Requires the remote host to accept password authentication temporarily (or have an existing key).
3.  **Pull (Remote -> Local)**: Connects to the remote host, ensures it has an ED25519 key (generating one if missing), retrieves the public key, and adds it to the local `authorized_keys`.
4.  **Verification**: Tests the connection to confirm password-less access.

**Arguments:**

- `HOST`: Remote hostname or IP address.
- `USER`: Remote username.
- `--port, -p N`: The **current** SSH port of the remote host (Default: 22).
- `--no-test`: Skips the final connection verification step.

