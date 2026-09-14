---
name: grill-me
description: Interview the user relentlessly about a plan, decision, or architecture until full shared understanding — one question at a time, each with a recommended answer. Trigger on intent "grill me", "poke holes in this", "stress test this", "help me decide", "which should I use", "is this a good approach", or whenever the user is choosing between real options.
---

# Grill Me

A decision stress-tester. The most common failure mode is charging ahead on wrong assumptions —
this prevents it by forcing shared understanding *before* commitment. Works on any concrete
decision space: architecture, tool choices, refactors, designs. Useless on vagueness — if the user
hasn't sketched a plan at all, open by asking for the 30-second version.

## Protocol

1. **One question at a time.** Never batch. Wait for the answer before the next question.
2. **Every question carries options.** 2–5 concrete options, **recommended answer first with a
   one-line why**. The user reacts instead of inventing from scratch.
3. **Walk the decision tree.** Resolve dependencies between decisions one by one, deepest
   dependency first. Skip nothing load-bearing; skip ruthlessly anything already settled.
4. **Self-serve what you can.** If a question is answerable from the codebase, docs, or files —
   read and answer it yourself, move on. Only ask what genuinely needs the human.
5. **No vague escapes.** "Flexible", "we'll see", "both" are not answers. Force a concrete choice
   or record it explicitly as an open risk.
6. **Expect fatigue, respect it.** 15–25 questions is normal for a real decision. If the user is
   losing energy, offer to compress the remaining branches into your best-guess recommendations
   they can veto in one pass.

## Termination

End the session with a summary, always:

- **Decision:** {what was decided, stated plainly}
- **Risks:** {what could bite, ranked}
- **Untested assumptions:** {what we're taking on faith}
- **Next steps:** {concrete first moves}

## Output

Chat only — this tool stores nothing itself.

If the user works in a k-framework project (`.k/DECISIONS.md` exists), offer to record the
conclusion with `/k:note decision`. Otherwise done.
