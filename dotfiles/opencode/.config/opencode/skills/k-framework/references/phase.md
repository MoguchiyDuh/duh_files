---
name: k:phase
description: Define a phase — resolve unknowns, write CONTEXT.md + PLAN.md, update STATE and ROADMAP. --edit amends active phase plan.
argument-hint: "\"phase name\" | --edit"
allowed-tools:
    - Read
    - Write
    - Bash
    - Glob
    - Grep
---

<objective>
Create a phase directory with CONTEXT.md and PLAN.md. The plan must be executable by a fresh agent
(`k-executor`) with zero session history — anything it would need lives in CONTEXT.md or PLAN.md.

`--edit` amends the active phase's PLAN.md instead.
</objective>

<process>

## 0. Edit mode (--edit)

Read `.k/STATE.md` → active phase → its PLAN.md. Print the steps, ask what should change. Apply.
Don't touch Goal/Tools/Risks unless told. Confirm: "Plan updated — {N} steps." Stop.

## 1. Resolve phase number

```bash
ls .k/phases/ 2>/dev/null | grep -E '^[0-9]+' | sort | tail -1
```

Next = last + 1, or 01. Zero-pad 2 digits. Slugify name: "Caddy HTTPS" → `01-caddy-https`.

## 2. Gather plan context

Ask only what you can't infer from PROJECT.md, ROADMAP.md, DECISIONS.md, FACTS.md, CODEMAP.md —
read those first. One round usually enough.

- Goal of the phase (if not clear from name)
- Steps — rough list, high level ok
- Tools/access/external deps (ssh, API keys, containers)
- Risks / constraints

**Resolve unknowns before planning:** if the phase hinges on an undecided choice (tool,
architecture, approach with real tradeoffs), interview the user until the choice is made — one
question at a time, options with recommendations. Record the outcome via `k:note decision`, then
plan. Never plan around an unknown.

## 3. Scaffold

```bash
mkdir -p .k/phases/{NN-slug}
```

**`.k/phases/{NN-slug}/CONTEXT.md`** — decisions pinned at plan time. The executor's ground truth:

```markdown
# Context — Phase {N}: {name}

{every decision, constraint, and fact the executor must not re-derive or violate.
Include: chosen approach + why, what NOT to do, relevant DECISIONS/FACTS entries verbatim,
environment specifics (hosts, ports, paths, credentials *locations* — never secrets).}
```

**`.k/phases/{NN-slug}/PLAN.md`**

```markdown
# Phase {N}: {Name}

## Goal

{goal}

## Steps

- [ ] {step 1 — concrete, independently checkable}
- [ ] {step 2}

## Tools & access

{ssh aliases, containers, API keys needed — or "none"}

## Risks

{what could go wrong — or "none"}
```

## 4. Update STATE.md and ROADMAP.md

STATE: **Active phase:** `{NN-slug}`, **Status:** in progress, **Next:** execute step 1 (or "plan
ready — start executing").

ROADMAP: matching row → `in progress`, append row if absent.

## 5. Done

Print phase dir, step list. Ready to execute — suggest `/k:exec` for heavy implementation.

</process>
