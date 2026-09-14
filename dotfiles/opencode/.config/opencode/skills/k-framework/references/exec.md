---
name: k:exec
description: Execute phase steps in the k-executor subagent — fresh context, fresh model. Main session stays clean.
argument-hint: "[step numbers or range, e.g. 1-3] | all"
allowed-tools:
    - Read
    - Write
    - Bash
    - Glob
    - Grep
    - Agent
---

<objective>
Run implementation through the `k-executor` subagent. The executor gets a fresh context and only the
files it needs; it never sees this session. The main session keeps state ownership.
</objective>

<process>

## 1. Resolve scope

Read `.k/STATE.md` → active phase. Read its PLAN.md and CONTEXT.md.

Determine which steps to run from $ARGUMENTS (`all`, single `2`, range `1-3`). Default: the next
unchecked step. If CONTEXT.md is missing, stop — run `/k:phase --edit` material first; an executor
without context guesses, and guesses are how slop happens.

## 2. Spawn executor

Spawn the `k-executor` subagent (Task tool, subagent_type `k-executor`). Prompt:

```
Execute a planned task. You are a fresh executor — everything you need is in these files. If
something is genuinely missing or contradictory, STOP and report back instead of guessing.

Read first:
- .k/phases/{NN-slug}/CONTEXT.md   (decisions and constraints — do not violate, do not re-derive)
- .k/phases/{NN-slug}/PLAN.md      (goal, steps, risks)

Your task: execute step(s) {N}: {step text verbatim}

Rules:
- Implement exactly the scoped steps. No drive-by refactors, no scope creep.
- Do not modify anything under .k/ — state belongs to the orchestrator.
- Verify your own work where cheap (build, lint, run the thing) before reporting.
- Treat FACTS in CONTEXT.md as ground truth; if reality contradicts them, stop and report.

Report back:
- Steps completed: {N} — one line each on what was done
- Files changed: {paths}
- Verification: {what you ran, results}
- Deviations from plan: {any, with reason}
- Blocked/unresolved: {anything the orchestrator must handle}
```

## 3. On return

1. Sanity-check the report — spot-check one claimed file change yourself.
2. Check off completed steps in PLAN.md (same as k:done).
3. Relay deviations/blocked items to the user.
4. Suggest next: `/k:exec` for remaining steps, `/k:verify` when phase looks done.

Never let the executor's "done" flip STATE to complete — completion only through `/k:end complete`
with a passing verify.

</process>
