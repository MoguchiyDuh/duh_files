---
name: k:status
description: Progress snapshot — read-only
argument-hint: ""
allowed-tools:
    - Read
    - Glob
---

<objective>
One-screen snapshot of where the project is. No writes.
</objective>

<process>

Read `.k/STATE.md`, `.k/ROADMAP.md`, active phase PLAN.md + SUMMARY.md.

Output:

```
{project} — {status} | {N}/{M} phases

Active: {phase name}
Steps:  {checked}/{total} (mini progress from PLAN.md checkboxes)
Verify: {from SUMMARY}

Next: {STATE Next line}

Unresolved: {from SUMMARY, or "-"}
```

No suggestions, no follow-up questions. Just the snapshot.

</process>
