from __future__ import annotations

import json
import os
import shlex
import subprocess
from pathlib import Path

from fastmcp import FastMCP


mcp = FastMCP("rclone-gdrive")

REMOTE = os.environ.get("RCLONE_REMOTE", "gdrive")


def remote_path(path: str = "") -> str:
    path = path.strip().lstrip("/")
    if not path:
        return f"{REMOTE}:"
    if path.startswith(f"{REMOTE}:"):
        return path
    return f"{REMOTE}:{path}"


def remote_option_path(option: str, path: str = "") -> str:
    target = remote_path(path)
    suffix = target[len(f"{REMOTE}:"):]
    # Ensure a leading slash so the option-path is well-formed (e.g. gdrive,opt:/dir)
    if suffix and not suffix.startswith("/"):
        suffix = f"/{suffix}"
    return f"{REMOTE},{option}:{suffix}"


def run_rclone(*args: str) -> str:
    result = subprocess.run(
        ["rclone", *args],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        stdout = result.stdout.decode("utf-8", errors="replace").strip()
        message = stderr or stdout or "rclone failed"
        raise RuntimeError(message)
    return result.stdout.decode("utf-8", errors="replace").strip()


def format_ls_entry(entry: dict, long: bool) -> str:
    name = entry["Path"] + ("/" if entry.get("IsDir") else "")
    if not long:
        return name
    size = entry.get("Size", 0)
    # ModTime is ISO-8601 with ms: "2026-05-05T16:14:29.887Z" → "2026-05-05 16:14:29"
    modtime = entry.get("ModTime", "")[:19].replace("T", " ")
    kind = "d" if entry.get("IsDir") else "-"
    return f"{kind} {size:>12} {modtime} {name}"


@mcp.tool()
def ls(path: str = "", args: str = "") -> str:
    """List Google Drive entries with simple Unix-like args such as -l or -R."""
    flags = set(shlex.split(args))
    command = ["lsjson", remote_path(path)]
    if "-R" in flags:
        command.insert(1, "--recursive")
    items = json.loads(run_rclone(*command) or "[]")
    long = "-l" in flags
    return "\n".join(format_ls_entry(item, long) for item in items)


@mcp.tool()
def read(path: str, max_bytes: int = 20000) -> str:
    """Read a readable file from Google Drive."""
    return run_rclone("cat", "--head", str(max_bytes), remote_path(path))


@mcp.tool()
def download(path: str, local_path: str) -> str:
    """Download a Google Drive file to a local path."""
    target = Path(local_path).expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    run_rclone("copyto", remote_path(path), str(target))
    return str(target)


@mcp.tool()
def upload(local_path: str, path: str) -> str:
    """Upload a local file to a Google Drive path."""
    source = Path(local_path).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(str(source))
    run_rclone("copyto", str(source), remote_path(path))
    return remote_path(path)


@mcp.tool()
def rm(path: str) -> str:
    """Move a file or directory to Google Drive trash."""
    target = remote_path(path)
    try:
        run_rclone("deletefile", target)
    except RuntimeError:
        # deletefile only works on files; fall back to delete for directories.
        # delete (unlike purge) respects --drive-use-trash (default true).
        run_rclone("delete", target)
    return target


@mcp.tool()
def trash_list(path: str = "") -> str:
    """List trashed files and directories in Google Drive."""
    return run_rclone("lsf", remote_option_path("trashed_only", path))


@mcp.tool()
def untrash(path: str) -> str:
    """Restore a trashed file or directory in Google Drive.

    Restores all trashed items inside the parent directory of the given path.
    If path points to the root (no parent), untrash is run against the root.
    """
    target = remote_path(path)
    # rclone backend untrash operates on a directory and restores all trashed
    # children within it — it cannot target a single file by path.
    parent = Path(path.strip().lstrip("/")).parent.as_posix()
    parent_remote = remote_path("" if parent in ("", ".") else parent)
    run_rclone("backend", "untrash", parent_remote)
    return target


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
