---
name: k:debug
description: Systematic investigation and fixing — read-only investigation first
argument-hint: "[symptom]"
allowed-tools:
    - Read
    - Write
    - Bash
    - Glob
    - Grep
    - Agent
---

<objective>
Find root cause before touching anything. Investigation is read-only; fixes come after the
diagnosis is confirmed.
</objective>

<process>

## 1. Frame

From $ARGUMENTS: what's broken, since when, what changed recently (check phase SUMMARY.md and
STATE.md history — regressions usually trace to recent work).

## 2. Investigate (read-only first)

Spawn read-only agent (Read, Glob, Grep, Bash — no Write/Edit) or investigate directly:

- Reproduce: run the failing thing, capture exact error
- Narrow: bisect the surface — config, logs, versions, environment
- Consult `.k/FACTS.md` and CODEMAP.md — known behavior, ports, paths
- Root cause, not proximate cause: the error message is a symptom

## 3. Diagnose

State the diagnosis in one paragraph: cause → mechanism → why it produces this symptom. If the fix
is non-obvious or has options, present them with options and a recommendation before touching
anything.

## 4. Fix

Minimal, targeted change. No drive-by refactors. If the fix contradicts a DECISIONS.md entry —
stop and surface the conflict; decisions don't get silently overridden.

## 5. Persist

Offer: `k:note fact` for the discovered truth (root cause, the non-obvious mechanism), and update
phase SUMMARY Unresolved/Done if this was tracked work.

</process>
