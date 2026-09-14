---
name: k:verify
description: Read-only subagent verifies phase work vs PLAN; writes Verify record into SUMMARY — the completion gate input
argument-hint: "[what to check]"
allowed-tools:
    - Read
    - Glob
    - Grep
    - Bash
    - Write
    - Agent
---

<objective>
Verify work done in the active phase against PLAN.md steps. The inspection subagent is read-only;
the only write is the `**Verify:**` record in SUMMARY.md — which `k:end complete` gates on.
</objective>

<process>

## 1. Read context

`.k/STATE.md` → active phase. Then its PLAN.md (steps, goal) and SUMMARY.md (claims).

## 2. Spawn verify agent

Subagent allowed-tools: Read, Glob, Grep, Bash — no Write, no Edit.

```
Verify the current phase work. Read-only — do not modify anything.

Phase: {phase name}
Goal: {goal from PLAN.md}

Steps to verify:
{steps from PLAN.md, with checked state}

Additional focus (if provided): {$ARGUMENTS}

For each step, actively verify — don't just read SUMMARY as proof:
- Run commands to confirm (curl, docker ps, ssh, systemctl status, ls, cat configs, cargo check, etc.)
- Read files to check contents match expectations
- Treat PLAN.md and SUMMARY.md as claims to verify, not evidence

Output:
- ✓ / ✗ / ⚠ per step with one-line evidence (what command/file confirmed it)
- Verdict: pass | gaps found
- If gaps: specific, actionable findings only — no fluff
```

## 3. Record the verdict

Write into `.k/phases/{active-phase}/SUMMARY.md`, replacing the Verify line:

- Pass → `**Verify:** pass {YYYY-MM-DD}`
- Gaps → `**Verify:** fail {YYYY-MM-DD} — {gap count} gaps` and list the findings under
  **Unresolved**.

This record is the only thing `/k:end complete` accepts.

## 4. Report

Print agent output as-is. If fail: suggest fixes (via sessions or `/k:exec`), then re-verify.

</process>
