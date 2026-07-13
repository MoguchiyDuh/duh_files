#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DESTINATION = Path.home() / ".local" / "bin"
HARDWARE_SETUP = Path.home() / ".config" / "waybar" / "scripts" / "setup-hardware.sh"


def workspace_binaries() -> tuple[Path, list[str]]:
    result = subprocess.run(
        ["cargo", "metadata", "--format-version", "1", "--locked", "--no-deps"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(result.stdout)
    binaries = sorted(
        target["name"]
        for package in metadata["packages"]
        for target in package["targets"]
        if "bin" in target["kind"]
    )
    if not binaries:
        raise RuntimeError("workspace contains no binary targets")
    return Path(metadata["target_directory"]) / "release", binaries


def deploy(source_dir: Path, binary: str) -> None:
    source = source_dir / binary
    if not source.is_file():
        raise FileNotFoundError(f"Cargo did not produce {source}")

    destination = DESTINATION / binary
    temporary = DESTINATION / f".{binary}.tmp"
    shutil.copyfile(source, temporary)
    temporary.chmod(
        stat.S_IRUSR
        | stat.S_IWUSR
        | stat.S_IXUSR
        | stat.S_IRGRP
        | stat.S_IXGRP
        | stat.S_IROTH
        | stat.S_IXOTH
    )
    os.replace(temporary, destination)
    print(f"deployed {destination}")


def main() -> int:
    try:
        source_dir, binaries = workspace_binaries()
        subprocess.run(
            ["cargo", "build", "--release", "--workspace", "--locked"],
            cwd=ROOT,
            check=True,
        )
        DESTINATION.mkdir(parents=True, exist_ok=True)
        for binary in binaries:
            deploy(source_dir, binary)
    except (OSError, RuntimeError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"build failed: {error}", file=sys.stderr)
        return 1

    print("\nOptional hardware metadata and CPU power reporting require:")
    print(f"  {HARDWARE_SETUP}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
