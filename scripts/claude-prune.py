#!/usr/bin/env python3
"""Interactive Claude storage manager."""

import curses
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Set, Tuple

CLAUDE_DIR = Path.home() / ".claude"

CLEAR_TARGETS: List[Tuple[str, Path]] = [
    ("history",      CLAUDE_DIR / "history.jsonl"),
    ("todos",        CLAUDE_DIR / "todos"),
    ("plans",        CLAUDE_DIR / "plans"),
    ("session-env",  CLAUDE_DIR / "session-env"),
    ("file-history", CLAUDE_DIR / "file-history"),
    ("debug",        CLAUDE_DIR / "debug"),
    ("statsig",      CLAUDE_DIR / "statsig"),
]


# ── helpers ───────────────────────────────────────────────────────────────────

def get_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    try:
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    except Exception:
        return 0


def fmt_size(size: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def fmt_time(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "unknown"


def delete_paths(paths: List[Path]) -> int:
    deleted = 0
    for p in paths:
        try:
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p)
            deleted += 1
        except Exception:
            pass
    return deleted


def clear_path(path: Path):
    """Truncate a file or wipe+recreate a directory."""
    if path.is_file():
        path.unlink()
        path.touch()
    elif path.is_dir():
        shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


# ── data fetchers ─────────────────────────────────────────────────────────────

def get_projects() -> List[Path]:
    d = CLAUDE_DIR / "projects"
    if not d.exists():
        return []
    return sorted(
        [p for p in d.iterdir() if p.is_dir() and not p.name.startswith(".")],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )


def get_sessions(project: Path) -> List[Path]:
    return sorted(
        [f for f in project.iterdir()
         if f.suffix == ".jsonl" and not f.stem.startswith("agent-")],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )


def get_agents(project: Path) -> List[Path]:
    return sorted(
        [f for f in project.iterdir()
         if f.suffix == ".jsonl" and f.stem.startswith("agent-")],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )


def get_snapshots() -> List[Path]:
    d = CLAUDE_DIR / "shell-snapshots"
    if not d.exists():
        return []
    return sorted(
        [f for f in d.iterdir() if f.name.startswith("snapshot-")],
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )


def get_session_name(path: Path) -> str:
    """Return the last custom-title set via /rename, or empty string."""
    last = ""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("type") == "custom-title":
                        last = entry.get("customTitle", "")
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return last


def get_first_message(path: Path) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("type") == "user" and not entry.get("isMeta"):
                        text = entry.get("message", {}).get("content", "").strip()
                        if not text or text.startswith("/") or text.startswith("<"):
                            continue
                        if "Caveat:" in text or "DO NOT respond" in text:
                            continue
                        return text[:70] + "…" if len(text) > 70 else text
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return "[No message]"


def is_empty_session(path: Path) -> bool:
    if path.stat().st_size == 0:
        return True
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if entry.get("type") == "user" and not entry.get("isMeta"):
                        content = entry.get("message", {}).get("content", "").strip()
                        if (content
                                and not content.startswith("/")
                                and not content.startswith("<")
                                and "Caveat:" not in content
                                and "DO NOT respond" not in content):
                            return False
                except Exception:
                    pass
    except Exception:
        pass
    return True


# ── colors ────────────────────────────────────────────────────────────────────
# All pairs use -1 background so terminal transparency passes through.
# -1 foreground = terminal default fg (works on both dark and light themes).

def init_colors():
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,  -1)  # cursor
    curses.init_pair(2, curses.COLOR_YELLOW,-1)  # selected
    curses.init_pair(3, -1,                 -1)  # title  (default fg, bold)
    curses.init_pair(4, -1,                 -1)  # dim    (default fg, A_DIM)
    curses.init_pair(5, curses.COLOR_RED,   -1)  # danger


def C_CURSOR()   : return curses.color_pair(1) | curses.A_BOLD
def C_SELECTED() : return curses.color_pair(2)
def C_TITLE()    : return curses.color_pair(3) | curses.A_BOLD
def C_DIM()      : return curses.color_pair(4) | curses.A_DIM
def C_DANGER()   : return curses.color_pair(5) | curses.A_BOLD
def C_NORMAL()   : return curses.A_NORMAL


# ── TUI primitives ────────────────────────────────────────────────────────────

def draw_title(stdscr, title: str):
    _, w = stdscr.getmaxyx()
    try:
        stdscr.attron(C_TITLE())
        stdscr.addstr(0, 0, f"  {title}"[:w - 1])
        stdscr.attroff(C_TITLE())
    except curses.error:
        pass


def draw_statusbar(stdscr, hint: str, flash: str = ""):
    h, w = stdscr.getmaxyx()
    # flash on left (normal), hint on right (dim)
    left  = f" {flash}  " if flash else ""
    right = hint
    bar   = (left + right)[:w - 1]
    try:
        if flash:
            stdscr.attron(C_NORMAL())
            stdscr.addstr(h - 1, 0, f" {flash}  "[:w - 1])
            stdscr.attroff(C_NORMAL())
            offset = min(len(f" {flash}  "), w - 1)
        else:
            offset = 0
        stdscr.attron(C_DIM())
        stdscr.addstr(h - 1, offset, right[:w - 1 - offset])
        stdscr.attroff(C_DIM())
    except curses.error:
        pass


def confirm_dialog(stdscr, msg: str) -> bool:
    h, w = stdscr.getmaxyx()
    text = f"  {msg} [y/N]  "
    y = h // 2
    x = max(0, (w - len(text)) // 2)
    try:
        stdscr.attron(C_DANGER())
        stdscr.addstr(y, x, text[:w - 1])
        stdscr.attroff(C_DANGER())
    except curses.error:
        pass
    stdscr.refresh()
    ch = stdscr.getch()
    return ch in (ord("y"), ord("Y"))


# ── ListScreen ────────────────────────────────────────────────────────────────

HINT_NAV   = "j/k:move  spc:sel  a:all  d:del  h:back"
HINT_ENTER = "j/k:move  spc:sel  a:all  d:del  l:open  h:back"
HINT_EMPTY = "j/k:move  spc:sel  a:all  d:del  e:empty  h:back"


class ListScreen:
    """
    Generic interactive list with cached row labels.

    items       — list of Path objects
    row_fn      — called once per item to build the display label (disk I/O goes here)
    can_enter   — l/enter returns the highlighted Path
    empty_pred  — optional predicate: Path -> bool, used by 'e' to select empty items
    """

    def __init__(
        self,
        stdscr,
        title: str,
        items: List[Path],
        row_fn: Callable[[Path], str],
        hint: str = HINT_NAV,
        can_enter: bool = False,
        empty_pred: Optional[Callable[[Path], bool]] = None,
    ):
        self.stdscr    = stdscr
        self.title     = title
        self.row_fn    = row_fn
        self.hint      = hint
        self.can_enter = can_enter
        self.empty_pred = empty_pred
        self.cursor    = 0
        self.selected: Set[int] = set()
        self.offset    = 0
        self.flash     = ""

        self.items: List[Path] = []
        self._labels: List[str] = []
        self._set_items(items)

    def _set_items(self, items: List[Path]):
        self.items   = list(items)
        self._labels = [self.row_fn(p) for p in self.items]  # compute once

    def _lh(self) -> int:
        h, _ = self.stdscr.getmaxyx()
        return max(1, h - 3)

    def _clamp(self):
        n = len(self.items)
        self.cursor = max(0, min(self.cursor, n - 1)) if n else 0
        lh = self._lh()
        if self.cursor < self.offset:
            self.offset = self.cursor
        elif self.cursor >= self.offset + lh:
            self.offset = self.cursor - lh + 1

    def draw(self):
        self.stdscr.erase()
        _, w = self.stdscr.getmaxyx()
        self._clamp()

        draw_title(self.stdscr, self.title)

        lh = self._lh()
        for i, label in enumerate(self._labels[self.offset:self.offset + lh]):
            idx = i + self.offset
            sel = "*" if idx in self.selected else " "
            cur = ">" if idx == self.cursor else " "
            line = f" {cur}[{sel}] {label}"[:w - 1]
            row  = i + 1

            attrs = C_CURSOR() if idx == self.cursor else (C_SELECTED() if idx in self.selected else C_NORMAL())
            try:
                self.stdscr.attron(attrs)
                self.stdscr.addstr(row, 0, line)
                self.stdscr.attroff(attrs)
            except curses.error:
                pass

        # scrollbar pip
        n = len(self.items)
        if n > lh:
            pip = 1 + int(self.offset / max(1, n - lh) * (lh - 1))
            try:
                self.stdscr.attron(C_DIM())
                self.stdscr.addstr(pip, w - 1, "│")
                self.stdscr.attroff(C_DIM())
            except curses.error:
                pass

        count = f"{len(self.selected)} sel / {n} total"
        draw_statusbar(self.stdscr, self.hint, f"{count}  {self.flash}".strip())
        self.stdscr.refresh()

    def _delete(self):
        targets = sorted(self.selected) if self.selected else ([self.cursor] if self.items else [])
        if not targets:
            return
        if confirm_dialog(self.stdscr, f"Delete {len(targets)} item(s)?"):
            paths   = [self.items[i] for i in targets if i < len(self.items)]
            deleted = delete_paths(paths)
            self.flash = f"Deleted {deleted}/{len(targets)}."
            for i in sorted(targets, reverse=True):
                if i < len(self.items):
                    del self.items[i]
                    del self._labels[i]
            self.selected.clear()
            self.cursor = min(self.cursor, max(0, len(self.items) - 1))
        else:
            self.flash = ""

    def _select_empty(self):
        if not self.empty_pred:
            return
        self.selected = {i for i, p in enumerate(self.items) if self.empty_pred(p)}
        self.flash = f"{len(self.selected)} empty selected."

    def run(self) -> Optional[Path]:
        """Returns None on back, or the chosen Path if can_enter."""
        curses.curs_set(0)
        while True:
            self.draw()
            if not self.items:
                return None

            ch = self.stdscr.getch()

            if ch == curses.KEY_RESIZE:
                curses.resizeterm(*self.stdscr.getmaxyx())
                continue

            if ch in (ord("q"), ord("b"), ord("h"), 27, curses.KEY_LEFT):
                return None

            elif ch in (ord("j"), curses.KEY_DOWN):
                self.cursor += 1
                self.flash = ""

            elif ch in (ord("k"), curses.KEY_UP):
                self.cursor -= 1
                self.flash = ""

            elif ch == curses.KEY_NPAGE:
                self.cursor += self._lh()

            elif ch == curses.KEY_PPAGE:
                self.cursor -= self._lh()

            elif ch == ord("g"):
                self.cursor = 0

            elif ch == ord("G"):
                self.cursor = len(self.items) - 1

            elif ch == ord(" "):
                if self.cursor in self.selected:
                    self.selected.discard(self.cursor)
                else:
                    self.selected.add(self.cursor)
                self.cursor = min(self.cursor + 1, len(self.items) - 1)
                self.flash = ""

            elif ch == ord("a"):
                if len(self.selected) == len(self.items):
                    self.selected.clear()
                else:
                    self.selected = set(range(len(self.items)))
                self.flash = ""

            elif ch in (ord("d"), curses.KEY_DC):
                self._delete()
                if not self.items:
                    return None

            elif ch == ord("e") and self.empty_pred:
                self._select_empty()

            elif ch in (curses.KEY_ENTER, ord("\n"), ord("\r"), ord("l"), curses.KEY_RIGHT):
                if self.can_enter and self.items:
                    return self.items[self.cursor]


# ── screen functions ──────────────────────────────────────────────────────────

def sessions_screen(stdscr, project: Path):
    def row(f: Path) -> str:
        name = get_session_name(f)
        label = f"[{name}] {get_first_message(f)}" if name else get_first_message(f)
        return f"{fmt_size(get_size(f)):>8}  {fmt_time(f)}  {label}"

    ListScreen(
        stdscr,
        title=f"Sessions — {project.name}",
        items=get_sessions(project),
        row_fn=row,
        hint=HINT_EMPTY,
        empty_pred=is_empty_session,
    ).run()


def agents_screen(stdscr, project: Path):
    def row(f: Path) -> str:
        return f"{fmt_size(get_size(f)):>8}  {fmt_time(f)}  {f.stem}"

    ListScreen(
        stdscr,
        title=f"Agents — {project.name}",
        items=get_agents(project),
        row_fn=row,
    ).run()


def projects_screen(stdscr):
    def row(p: Path) -> str:
        sessions = get_sessions(p)
        agents   = get_agents(p)
        total    = sum(get_size(f) for f in sessions + agents)
        return f"{fmt_size(total):>8}  {fmt_time(p)}  {p.name}  ({len(sessions)}s {len(agents)}a)"

    ls = ListScreen(
        stdscr,
        title="Projects",
        items=get_projects(),
        row_fn=row,
        hint=HINT_ENTER,
        can_enter=True,
    )
    while True:
        chosen = ls.run()
        if chosen is None:
            return
        sessions_screen(stdscr, chosen)
        # refresh after returning from sessions (sizes may have changed)
        prev_name = chosen.name
        ls._set_items(get_projects())
        names = [p.name for p in ls.items]
        ls.cursor = names.index(prev_name) if prev_name in names else min(ls.cursor, len(ls.items) - 1)
        ls.selected.clear()


def agents_project_screen(stdscr):
    def row(p: Path) -> str:
        agents = get_agents(p)
        total  = sum(get_size(f) for f in agents)
        return f"{fmt_size(total):>8}  {fmt_time(p)}  {p.name}  ({len(agents)} agents)"

    ls = ListScreen(
        stdscr,
        title="Projects — agents",
        items=get_projects(),
        row_fn=row,
        hint=HINT_ENTER,
        can_enter=True,
    )
    while True:
        chosen = ls.run()
        if chosen is None:
            return
        agents_screen(stdscr, chosen)
        prev_name = chosen.name
        ls._set_items(get_projects())
        names = [p.name for p in ls.items]
        ls.cursor = names.index(prev_name) if prev_name in names else min(ls.cursor, len(ls.items) - 1)
        ls.selected.clear()


def snapshots_screen(stdscr):
    def row(f: Path) -> str:
        return f"{fmt_size(get_size(f)):>8}  {fmt_time(f)}  {f.name}"

    ListScreen(
        stdscr,
        title="Shell Snapshots",
        items=get_snapshots(),
        row_fn=row,
    ).run()


def clear_screen_ui(stdscr, name: str, path: Path):
    stdscr.erase()
    draw_title(stdscr, f"Clear — {name}")
    stdscr.refresh()

    if not path.exists():
        msg = f"{name} does not exist."
    elif confirm_dialog(stdscr, f"Clear {name}?"):
        try:
            clear_path(path)
            msg = f"Cleared {name}."
        except Exception as e:
            msg = f"Error: {e}"
    else:
        return

    stdscr.erase()
    draw_title(stdscr, f"Clear — {name}")
    try:
        stdscr.addstr(2, 2, msg)
        stdscr.attron(C_DIM())
        stdscr.addstr(4, 2, "press any key…")
        stdscr.attroff(C_DIM())
    except curses.error:
        pass
    stdscr.refresh()
    stdscr.getch()


# ── main menu ─────────────────────────────────────────────────────────────────

MENU: List[Tuple[str, object]] = [
    ("Manage projects",  "projects"),
    ("Manage agents",    "agents"),
    ("Manage snapshots", "snapshots"),
    ("─" * 24,           None),
    *[(f"Clear {name}", ("clear", path)) for name, path in CLEAR_TARGETS],
]

_SEPARATORS = {i for i, (label, _) in enumerate(MENU) if str(label).startswith("─")}


def _next(cursor: int, direction: int) -> int:
    c = cursor + direction
    while 0 <= c < len(MENU) and c in _SEPARATORS:
        c += direction
    return max(0, min(c, len(MENU) - 1))


def menu_screen(stdscr):
    cursor = 0
    curses.curs_set(0)

    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        draw_title(stdscr, "Claude Storage Manager")

        for i, (label, _) in enumerate(MENU):
            row = i + 2
            if row >= h - 1:
                break
            if i in _SEPARATORS:
                try:
                    stdscr.attron(C_DIM())
                    stdscr.addstr(row, 4, str(label)[:w - 5])
                    stdscr.attroff(C_DIM())
                except curses.error:
                    pass
            elif i == cursor:
                try:
                    stdscr.attron(C_CURSOR())
                    stdscr.addstr(row, 2, f"> {label}"[:w - 3])
                    stdscr.attroff(C_CURSOR())
                except curses.error:
                    pass
            else:
                try:
                    stdscr.addstr(row, 4, str(label)[:w - 5])
                except curses.error:
                    pass

        draw_statusbar(stdscr, "j/k:move  l/enter:open  q:quit")
        stdscr.refresh()

        ch = stdscr.getch()

        if ch == curses.KEY_RESIZE:
            curses.resizeterm(*stdscr.getmaxyx())
            continue

        if ch in (ord("q"), ord("Q"), 27):
            return

        elif ch in (ord("j"), curses.KEY_DOWN):
            cursor = _next(cursor, 1)

        elif ch in (ord("k"), curses.KEY_UP):
            cursor = _next(cursor, -1)

        elif ch in (curses.KEY_ENTER, ord("\n"), ord("\r"), ord("l"), curses.KEY_RIGHT):
            _, action = MENU[cursor]
            if action is None:
                continue
            elif action == "projects":
                projects_screen(stdscr)
            elif action == "agents":
                agents_project_screen(stdscr)
            elif action == "snapshots":
                snapshots_screen(stdscr)
            elif isinstance(action, tuple) and action[0] == "clear":
                clear_screen_ui(stdscr, action[1].name, action[1])


# ── entry ─────────────────────────────────────────────────────────────────────

def _run(stdscr):
    init_colors()
    menu_screen(stdscr)


def main():
    curses.wrapper(_run)


if __name__ == "__main__":
    main()
