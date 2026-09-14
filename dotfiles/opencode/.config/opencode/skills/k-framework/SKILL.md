---
name: k-framework
description: Use for project management, phased development, state tracking, and research across many sessions. Trigger when the user mentions "k commands", "project state", "/k:init", "/k:phase", or "/k:exec".
---

# K-Framework Skill (v2)

Multi-session project continuity. All state lives in files, never in chat. A fresh session must be
able to resume a week-old project in under a minute without re-asking anything settled.

## File structure

All state lives in `.k/` of the workspace. `.k/` is git-ignored (agent-owned, never committed).

```
.k/
  STATE.md                   status, active phase, progress, Next: pointer
  PROJECT.md                 vision / result / stack / constraints
  ROADMAP.md                 phase table
  DECISIONS.md               settled by the human. append-only, with rationale
  FACTS.md                   learned truths. every entry needs a source
  TODO.md                    backlog
  CODEMAP.md                 codebase/infra map (optional)
  RESEARCH/INDEX.md          topic → file, one-line takeaway, date
  RESEARCH/{topic}.md        decision-oriented research, sources mandatory
  phases/{NN-slug}/          CONTEXT.md, PLAN.md, SUMMARY.md
  quick/{date}.md            k:end quick-mode dumps (non-project)
```

Legacy `.k-framework/` dirs are never touched.

## Operational rules

1. **Files are the only memory.** If it matters and isn't in `.k/`, it doesn't exist. Surface
   relevant DECISIONS/FACTS before acting; never re-litigate a settled decision — extend it with a
   new dated entry instead.
2. **Trust levels.** DECISIONS = human authority, don't override. FACTS = source required; an
   assertion without a source is a guess — treat it as one.
3. **Next pointer.** `STATE.md` `Next:` is the first action of the next session. Keep it concrete
   enough that a stranger agent can act on it. Update it whenever work state changes.
4. **Completion gate (hard).** A phase may only be marked complete in `STATE.md` when its
   `SUMMARY.md` contains `**Verify:** pass`. `k:end` refuses otherwise. No exceptions.
5. **Fresh-context execution.** Heavy implementation goes through `k:exec` (the `k-executor`
   subagent): it reads only CONTEXT.md + PLAN.md, writes code, never writes `.k/`, and reports back.
   The main session updates state.
6. **Conciseness.** Operator-reference format everywhere — dense, no fluff, no ceremony.

## Commands

Invocation: `/k:{name}`. Each maps to a workflow file in `${OPENCODE_SKILL_DIR}/references/`:

| Command    | File        | Purpose                                                                         |
| ---------- | ----------- | ------------------------------------------------------------------------------- |
| k:init     | init.md     | Scaffold `.k/`, interview, gitignore entry, optional research/codemap           |
| k:start    | start.md    | Session-start briefing; read STATE `Next:` first                                |
| k:end      | end.md      | Persist session: STATE + SUMMARY, hard completion gate; quick mode              |
| k:phase    | phase.md    | Define phase → CONTEXT.md + PLAN.md; resolve unknowns first; --edit amends |
| k:exec     | exec.md     | Run phase steps in `k-executor` subagent, fresh context                         |
| k:done     | done.md     | Check off PLAN steps, update STATE progress                                     |
| k:status   | status.md   | Progress snapshot                                                               |
| k:note     | note.md     | Append to DECISIONS.md or FACTS.md                                              |
| k:todo     | todo.md     | Backlog management                                                              |
| k:debug    | debug.md    | Systematic read-only-first investigation                                        |
| k:research | research.md | Per-topic research, sources mandatory, INDEX entry                              |
| k:verify   | verify.md   | Read-only verification vs PLAN; writes Verify record to SUMMARY                 |
| k:codemap  | codemap.md  | Map codebase/infra into CODEMAP.md                                              |

## Skill variables

- References: `${OPENCODE_SKILL_DIR}/references/`
- Executor agent: `k-executor` (defined in `~/.config/opencode/agent/k-executor.md`)
