---
name: k:done
description: Check off PLAN steps and update STATE progress
argument-hint: "[step numbers] | all"
allowed-tools:
    - Read
    - Write
    - Glob
---

<objective>
Mark steps complete in the active phase's PLAN.md and keep STATE Progress honest.
</objective>

<process>

## 1. Resolve steps

Read `.k/STATE.md` → active phase → PLAN.md.

$ARGUMENTS: step numbers (`2`, `1-3`) or `all`. If omitted, ask which steps — but verify first:
before checking a step, confirm it's actually done (file exists, command output, user confirmation).
Never check off on faith.

## 2. Update PLAN.md

`- [ ]` → `- [x]` for the resolved steps. Don't touch anything else.

## 3. Update STATE.md

**Next:** next unchecked step ("execute step {N}: {text}"), or "all steps done — run /k:verify".

## 4. Nudge

If all steps are now checked and SUMMARY Verify is not `pass`: one line — "All steps done. Run
`/k:verify`, then `/k:end complete`."

</process>
