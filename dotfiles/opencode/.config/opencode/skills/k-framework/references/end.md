---
name: k:end
description: Persist session — update STATE Next pointer, write/refresh SUMMARY. Hard gate on phase completion. Quick mode dumps flat note.
argument-hint: "[quick] [\"note\"] | complete"
allowed-tools:
    - Read
    - Write
    - Bash
    - Glob
---

<objective>
Persist session context before /clear or end of work. Files are the only memory — this command is
the handoff contract to the next session.

Modes:

- **Project** (default): update STATE `Next:` + write/refresh active phase SUMMARY.md
- **Quick**: dump flat context note to `.k/quick/`

`complete` argument: marks the active phase complete in STATE — gated, see 2a.3.
Mode auto-detected from `.k/STATE.md` existence unless `quick` is passed.
</objective>

<process>

## 1. Detect mode

First argument `quick` OR `.k/STATE.md` missing → Quick mode. Else Project mode.

## 2a. Project mode

Read `.k/STATE.md` for the active phase dir.

### 2a.1 Update STATE.md

- **Status:** reflect what's done / in progress
- **Progress:** bump only if a phase just completed (via `complete`, below)
- **Next:** the first action of the next session — concrete, imperative, self-contained. A stranger
  agent must be able to act on it without this conversation. If the user's `$ARGUMENTS` note says
  what's next, use it; else derive from SUMMARY.

### 2a.2 Write SUMMARY.md

Create or refresh `.k/phases/{active-phase}/SUMMARY.md`:

```markdown
# Phase {N}: {name} — summary

**Updated:** {YYYY-MM-DD}
**Verify:** {current value — pass / fail {date} / not-run. Never touch here}

## Done

{what was completed this session and before}

## Files touched

{paths}

## Unresolved

{open questions, blocked items — or "none"}

## Next

{first action of next session — mirrors STATE Next}
```

Preserve an existing `**Verify:**` value verbatim. Unresolved items must not silently disappear —
carry them forward until actually resolved.

### 2a.3 Completion gate (hard)

Only when `complete` is passed or the user asks to mark the phase done:

1. Read SUMMARY.md. Check `**Verify:** pass` is present.
2. If not pass → **refuse**. Do not write the completion. Reply:
   "Gate: phase can't complete without a passing verify. Run `/k:verify` first."
3. If pass → set phase row to `complete` in ROADMAP.md, bump STATE Progress, set
   **Active phase: none** (or next pending phase), set **Next:** to starting the next phase.

## 2b. Quick mode

```bash
mkdir -p .k/quick
```

Write `.k/quick/{YYYY-MM-DD-HHMM}.md`:

```markdown
# Quick save — {YYYY-MM-DD HH:MM}

## Context

{what we were doing}

## Done

{what was completed}

## Next

{what's next}

## Notes

{$ARGUMENTS note if provided, else anything worth remembering}
```

## 3. Confirm

One line: what was written, where, and the Next pointer.

</process>
