# Claude Storage Manager (`claude_storage_manager.py`) Guide

A Terminal User Interface (TUI) for managing the local data footprint of the Claude CLI. It provides tools for auditing usage and cleaning up session artifacts.

---

## Interactive Menu

The script launches an interactive menu loop.

**Usage:** `python3 claude_storage_manager.py`

### 1. System Info

Displays a dashboard of disk usage across all Claude storage directories (`~/.claude/`):

- **History**: Size of the user command history.
- **Shell Snapshots**: Space consumed by filesystem state snapshots.
- **Cache**: Statsig and debug cache size.
- **Sessions**: Total count and size of chat session logs.
- **Agents**: Total count and size of sub-agent session logs.

### 2. Manage Sessions

Opens a submenu to inspect and delete chat sessions.

- **List View**: Shows sessions ordered by date, including size and a preview of the first user message.
- **Deletion Commands**:
  - `[number]`: Delete a specific session by its index.
  - `[range]`: Delete a range (e.g., `1-5`).
  - `[list]`: Delete multiple specific indices (e.g., `1,3,5`).
  - `empty`: Automatically scans for and deletes sessions with 0 bytes or no meaningful user interaction.
  - `all`: **Destructive.** Deletes every recorded session.

### 3. Manage Agents

Similar to "Manage Sessions", but focuses on sub-agent logs (`agent-*.jsonl`). These are often generated during complex multi-step tasks.

### 4. Manage Snapshots

Allows deletion of shell snapshots. These can accumulate quickly if the CLI is used for extensive file operations.

### 5-11. Quick Clear Operations

Direct commands to wipe specific data categories without navigating lists:

- **5. Clear History**: Wipes `history.jsonl` (user prompt history).
- **6. Clear Todos**: Wipes the `todos/` directory.
- **7. Clear Plans**: Wipes the `plans/` directory.
- **8. Clear Session Env**: Cleans up saved session environment variables.
- **9. Clear File History**: Wipes file modification logs.
- **10. Clear Debug**: Removes debug log files.
- **11. Clear Cache**: Wipes the Statsig cache.

