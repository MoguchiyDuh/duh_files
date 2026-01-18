#!/usr/bin/env python
"""Interactive Claude storage manager."""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class ClaudeStorageManager:
    """Manages Claude storage directories and data."""

    def __init__(self):
        """Initialize storage manager."""
        self.claude_dir = Path.home() / ".claude"
        self.project_dir = self._find_project_dir()

        # Directory constants
        self.DIRS = {
            "history": self.claude_dir / "history.jsonl",
            "shell-snapshots": self.claude_dir / "shell-snapshots",
            "todos": self.claude_dir / "todos",
            "plans": self.claude_dir / "plans",
            "session-env": self.claude_dir / "session-env",
            "file-history": self.claude_dir / "file-history",
            "debug": self.claude_dir / "debug",
            "statsig": self.claude_dir / "statsig",
        }

    @staticmethod
    def clear_screen():
        """Clear the terminal screen."""
        os.system("clear")

    def _find_project_dir(self) -> Optional[Path]:
        """Find the current project directory."""
        projects_dir = self.claude_dir / "projects"
        if not projects_dir.exists():
            return None

        # Get the first (or only) project
        projects = [
            d
            for d in projects_dir.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]
        return projects[0] if projects else None

    def _get_size(self, path: Path) -> int:
        """Get file/directory size in bytes."""
        if path.is_file():
            return path.stat().st_size
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())

    def _format_size(self, size: int) -> str:
        """Format size to human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def show_system_info(self):
        """Display Claude storage system information."""
        print("\n" + "=" * 60)
        print("  Claude Storage Info")
        print("=" * 60 + "\n")

        for name, path in self.DIRS.items():
            if not path.exists():
                print(f"✗ {name:20s} | Not found")
                continue

            size = self._get_size(path)
            if path.is_file():
                count_str = "1 file"
            else:
                count = sum(1 for _ in path.iterdir())
                count_str = f"{count} items"

            print(f"✓ {name:20s} | {count_str:12s} | {self._format_size(size):>10s}")

        if self.project_dir:
            sessions = self._get_sessions()
            agents = self._get_agents()
            sessions_size = sum(self._get_size(s[1]) for s in sessions)
            agents_size = sum(self._get_size(a[1]) for a in agents)

            print(f"\n{'Project: ' + self.project_dir.name}")
            print(
                f"  Sessions: {len(sessions):4d} | {self._format_size(sessions_size):>10s}"
            )
            print(
                f"  Agents:   {len(agents):4d} | {self._format_size(agents_size):>10s}"
            )

        print()

    def _get_sessions(self) -> List[Tuple[str, Path]]:
        """Get list of session files."""
        if not self.project_dir:
            return []

        sessions = []
        for f in self.project_dir.iterdir():
            if f.is_file() and f.suffix == ".jsonl" and not f.stem.startswith("agent-"):
                sessions.append((f.stem, f))

        return sorted(sessions, key=lambda x: x[1].stat().st_mtime, reverse=True)

    def _get_agents(self) -> List[Tuple[str, Path]]:
        """Get list of agent files."""
        if not self.project_dir:
            return []

        agents = []
        for f in self.project_dir.iterdir():
            if f.is_file() and f.suffix == ".jsonl" and f.stem.startswith("agent-"):
                agents.append((f.stem, f))

        return sorted(agents, key=lambda x: x[1].stat().st_mtime, reverse=True)

    def _get_snapshots(self) -> List[Tuple[str, Path]]:
        """Get list of snapshots."""
        snap_dir = self.claude_dir / "shell-snapshots"
        if not snap_dir.exists():
            return []

        snapshots = []
        for f in snap_dir.iterdir():
            if f.is_file() and f.name.startswith("snapshot-"):
                snapshots.append((f.name, f))

        return sorted(snapshots, key=lambda x: x[1].stat().st_mtime, reverse=True)

    def _get_first_message(self, session_path: Path) -> str:
        """Extract first user message from session file."""
        try:
            with open(session_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("type") == "user" and not entry.get("isMeta"):
                            msg = entry.get("message", {})
                            text = msg.get("content", "").strip()

                            # Skip empty, slash commands, and system messages
                            if not text or text.startswith("/") or text.startswith("<"):
                                continue

                            # Skip caveat messages
                            if "Caveat:" in text or "DO NOT respond" in text:
                                continue

                            # Truncate to 80 chars
                            return text[:80] + "..." if len(text) > 80 else text
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return "[No message]"

    def _find_empty_sessions(self) -> List[Tuple[str, Path]]:
        """Find empty sessions (0 bytes or no user messages)."""
        if not self.project_dir:
            return []

        empty = []
        for f in self.project_dir.iterdir():
            if f.is_file() and f.suffix == ".jsonl" and not f.stem.startswith("agent-"):
                size = f.stat().st_size

                # 0 bytes = definitely empty
                if size == 0:
                    empty.append((f.stem, f))
                    continue

                # Check if session has actual user messages (not just commands)
                has_msg = False
                try:
                    with open(f, "r", encoding="utf-8") as file:
                        for line in file:
                            try:
                                entry = json.loads(line.strip())
                                if entry.get("type") == "user" and not entry.get(
                                    "isMeta"
                                ):
                                    msg = entry.get("message", {})
                                    content = msg.get("content", "").strip()

                                    # Skip commands and system messages
                                    if (
                                        not content
                                        or content.startswith("/")
                                        or content.startswith("<")
                                    ):
                                        continue

                                    # Skip caveat messages
                                    if (
                                        "Caveat:" in content
                                        or "DO NOT respond" in content
                                    ):
                                        continue

                                    has_msg = True
                                    break
                            except:
                                pass
                except:
                    pass

                if not has_msg:
                    empty.append((f.stem, f))

        return empty

    def _display_items(
        self,
        items: List[Tuple[str, Path]],
        show_date: bool = True,
        show_message: bool = False,
    ):
        """Display numbered list of items."""
        for i, (name, path) in enumerate(items, 1):
            size = self._format_size(self._get_size(path))
            if show_date:
                mtime = path.stat().st_mtime
                date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                print(f"  {i:3d}. {size:>10s} | {date} | {name}")
                if show_message:
                    msg = self._get_first_message(path)
                    print(f"       {msg}")
            else:
                print(f"  {i:3d}. {name:45s} | {size:>10s}")

    def _delete_items(self, items: List[Path]) -> int:
        """Delete list of files/directories."""
        deleted = 0
        for path in items:
            try:
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                deleted += 1
            except Exception as e:
                print(f"Error deleting {path.name}: {e}")
        return deleted

    def _handle_deletion(
        self,
        items: List[Tuple[str, Path]],
        selected_indices: List[int],
        item_type: str,
    ) -> List[Tuple[str, Path]]:
        """Handle deletion of selected items and refresh list."""
        selected = [items[i - 1] for i in selected_indices]
        print(f"\nSelected {len(selected)} {item_type}.")

        if confirm(f"Delete these {len(selected)} {item_type}?"):
            paths = [p for _, p in selected]
            deleted = self._delete_items(paths)
            print(f"Deleted {deleted}/{len(selected)} {item_type}.")
            self.clear_screen()

        return self._refresh_items(item_type)

    def _refresh_items(self, item_type: str) -> List[Tuple[str, Path]]:
        """Refresh item list based on type."""
        if item_type == "sessions":
            return self._get_sessions()
        elif item_type == "agents":
            return self._get_agents()
        elif item_type == "snapshots":
            return self._get_snapshots()
        return []

    def manage_sessions(self):
        """Manage sessions interactively."""
        sessions = self._get_sessions()

        if not sessions:
            print("\nNo sessions found.")
            return

        while True:
            print("\n" + "=" * 80)
            print("  Sessions")
            print("=" * 80 + "\n")
            self._display_items(sessions, show_message=True)
            print(f"\n  Total: {len(sessions)} sessions")

            print("\nOptions:")
            print("  [number]     Delete specific session")
            print("  [range]      Delete range (e.g., 1-5)")
            print("  [list]       Delete multiple (e.g., 1,3,5)")
            print("  empty        Delete empty sessions")
            print("  all          Delete all")
            print("  back         Return")

            choice = input("\n> ").strip().lower()

            if choice == "back":
                self.clear_screen()
                break
            elif choice == "empty":
                empty = self._find_empty_sessions()
                if not empty:
                    print("\nNo empty sessions found.")
                else:
                    print(f"\nFound {len(empty)} empty sessions:")
                    for name, path in empty:
                        size = self._get_size(path)
                        print(f"  - {name} ({size} bytes)")

                    if confirm(f"\nDelete {len(empty)} empty sessions?"):
                        paths = [p for _, p in empty]
                        deleted = self._delete_items(paths)
                        print(f"Deleted {deleted}/{len(empty)} empty sessions.")
                        sessions = self._get_sessions()
                        self.clear_screen()
                        if not sessions:
                            break
            elif choice == "all":
                if confirm(f"Delete ALL {len(sessions)} sessions?"):
                    paths = [p for _, p in sessions]
                    deleted = self._delete_items(paths)
                    print(f"Deleted {deleted}/{len(sessions)} sessions.")
                    sessions = self._get_sessions()
                    self.clear_screen()
                    if not sessions:
                        break
            else:
                indices = parse_selection(choice, len(sessions))
                if indices:
                    sessions = self._handle_deletion(sessions, indices, "sessions")
                    if not sessions:
                        break

    def manage_agents(self):
        """Manage agents interactively."""
        agents = self._get_agents()

        if not agents:
            print("\nNo agents found.")
            return

        while True:
            print("\n" + "=" * 80)
            print("  Agents")
            print("=" * 80 + "\n")
            self._display_items(agents)
            print(f"\n  Total: {len(agents)} agents")

            print("\nOptions:")
            print("  [number]     Delete specific agent")
            print("  [range]      Delete range (e.g., 1-5)")
            print("  [list]       Delete multiple (e.g., 1,3,5)")
            print("  all          Delete all")
            print("  back         Return")

            choice = input("\n> ").strip().lower()

            if choice == "back":
                self.clear_screen()
                break
            elif choice == "all":
                if confirm(f"Delete ALL {len(agents)} agents?"):
                    paths = [p for _, p in agents]
                    deleted = self._delete_items(paths)
                    print(f"Deleted {deleted}/{len(agents)} agents.")
                    agents = self._get_agents()
                    self.clear_screen()
                    if not agents:
                        break
            else:
                indices = parse_selection(choice, len(agents))
                if indices:
                    agents = self._handle_deletion(agents, indices, "agents")
                    if not agents:
                        break

    def manage_snapshots(self):
        """Manage snapshots interactively."""
        snapshots = self._get_snapshots()

        if not snapshots:
            print("\nNo snapshots found.")
            return

        while True:
            print("\n" + "=" * 80)
            print("  Shell Snapshots")
            print("=" * 80 + "\n")
            self._display_items(snapshots)
            print(f"\n  Total: {len(snapshots)} snapshots")

            print("\nOptions:")
            print("  [number]     Delete specific snapshot")
            print("  [range]      Delete range (e.g., 1-5)")
            print("  [list]       Delete multiple (e.g., 1,3,5)")
            print("  all          Delete all")
            print("  back         Return")

            choice = input("\n> ").strip().lower()

            if choice == "back":
                self.clear_screen()
                break
            elif choice == "all":
                if confirm(f"Delete ALL {len(snapshots)} snapshots?"):
                    paths = [p for _, p in snapshots]
                    deleted = self._delete_items(paths)
                    print(f"Deleted {deleted}/{len(snapshots)} snapshots.")
                    snapshots = self._get_snapshots()
                    self.clear_screen()
                    if not snapshots:
                        break
            else:
                indices = parse_selection(choice, len(snapshots))
                if indices:
                    snapshots = self._handle_deletion(snapshots, indices, "snapshots")
                    if not snapshots:
                        break

    def clear_directory(self, dir_name: str, path: Path) -> bool:
        """Clear a directory or file."""
        if not path.exists():
            print(f"\n{dir_name} does not exist.")
            return False

        try:
            if path.is_file():
                path.unlink()
                path.touch()
            else:
                shutil.rmtree(path)
                path.mkdir(parents=True, exist_ok=True)
            print(f"\nCleared: {dir_name}")
            return True
        except Exception as e:
            print(f"\nError clearing {dir_name}: {e}")
            return False


def parse_selection(selection: str, max_items: int) -> Optional[List[int]]:
    """Parse selection string into list of indices."""
    try:
        indices = set()

        if "-" in selection:
            parts = selection.split("-")
            if len(parts) == 2:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                indices.update(range(start, end + 1))
        elif "," in selection:
            for part in selection.split(","):
                indices.add(int(part.strip()))
        else:
            indices.add(int(selection))

        indices = [i for i in indices if 1 <= i <= max_items]
        return sorted(indices) if indices else None

    except ValueError:
        print("Dame. Invalid format.")
        return None


def confirm(prompt: str) -> bool:
    """Get user confirmation."""
    response = input(f"{prompt} [y/N]: ").strip().lower()
    return response in ("y", "yes")


def print_menu():
    """Display main menu."""
    print("\n" + "=" * 60)
    print("  Claude Storage Manager")
    print("=" * 60)
    print("\n[Info]")
    print("  1. System info")
    print("\n[Manage]")
    print("  2. Manage sessions")
    print("  3. Manage agents")
    print("  4. Manage snapshots")
    print("\n[Clear]")
    print("  5. Clear history")
    print("  6. Clear todos")
    print("  7. Clear plans")
    print("  8. Clear session-env")
    print("  9. Clear file-history")
    print(" 10. Clear debug")
    print(" 11. Clear cache (statsig)")
    print("\n  0. Exit")
    print()


def main():
    """Main interactive loop."""
    manager = ClaudeStorageManager()

    while True:
        print_menu()
        choice = input("> ").strip()

        if choice == "0":
            print("\nBB")
            break

        elif choice == "1":
            manager.clear_screen()
            manager.show_system_info()

        elif choice == "2":
            manager.clear_screen()
            if not manager.project_dir:
                print("\nNo project directory found.")
            else:
                manager.manage_sessions()

        elif choice == "3":
            manager.clear_screen()
            if not manager.project_dir:
                print("\nNo project directory found.")
            else:
                manager.manage_agents()

        elif choice == "4":
            manager.clear_screen()
            manager.manage_snapshots()

        elif choice in ["5", "6", "7", "8", "9", "10", "11"]:
            dir_map = {
                "5": ("history", "history"),
                "6": ("todos", "todos"),
                "7": ("plans", "plans"),
                "8": ("session-env", "session-env"),
                "9": ("file-history", "file-history"),
                "10": ("debug", "debug"),
                "11": ("cache (statsig)", "statsig"),
            }
            display_name, dir_key = dir_map[choice]
            if confirm(f"Clear {display_name}?"):
                manager.clear_directory(display_name, manager.DIRS[dir_key])
                manager.clear_screen()

        else:
            print("\nDame. Invalid option.")


if __name__ == "__main__":
    main()
