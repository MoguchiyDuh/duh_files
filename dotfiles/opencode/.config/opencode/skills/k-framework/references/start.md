---
name: k:start
description: Session-start briefing — STATE Next pointer first, then core files. Read-only.
argument-hint: ""
allowed-tools:
    - Read
    - Glob
    - Grep
    - Bash
---

<objective>
Orient at session start. Read project files and output a concise briefing — what this project is,
where we are, what's next. No writing, no unprompted work.
</objective>

<process>

## 1. Read STATE first

Read `.k/STATE.md`. The `Next:` line is the anchor — the session resumes exactly there.

## 2. Read core files

All that exist:

- `.k/PROJECT.md`
- `.k/ROADMAP.md`
- `.k/DECISIONS.md`
- `.k/FACTS.md`
- `.k/TODO.md`

Find active phase from STATE, then read:

- `.k/phases/{active-phase}/CONTEXT.md`
- `.k/phases/{active-phase}/PLAN.md`
- `.k/phases/{active-phase}/SUMMARY.md`

Read more (RESEARCH, CODEMAP) only if the task clearly calls for it.

## 3. Output briefing

Concise:

```
**{project name}** — {one line vision}

Progress: {N}/{M} phases | Active: {phase name} | Verify: {state from SUMMARY}

Next: {the Next pointer from STATE}

Context: {2-3 bullets — where we are, what's unresolved from SUMMARY}
Decisions worth remembering: {only ones affecting current phase}
Backlog: {open TODO items, or omit if empty}
```

If STATE has no `Next:` line, derive it from SUMMARY and propose writing it in.

## 4. Stay ready

Wait for instruction. Do not start working, do not suggest tasks unprompted.

</process>
