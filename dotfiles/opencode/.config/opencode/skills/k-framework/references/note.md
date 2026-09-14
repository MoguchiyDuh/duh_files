---
name: k:note
description: Append to DECISIONS.md or FACTS.md
argument-hint: "[decision|fact] \"text\""
allowed-tools:
    - Read
    - Write
---

<objective>
Persist a decision or a learned fact. Append-only — history is never rewritten.
</objective>

<process>

## 1. Resolve type

From $ARGUMENTS if given. Else infer:

- **decision** — a choice was made, by/with the human, between real options ("we use sqlite over
  postgres because single-file backups")
- **fact** — a discovered truth about the world/codebase ("navidrome listens on :4533") 

If genuinely ambiguous, ask. Guesses are recorded nowhere — an unverified claim is not a fact.

## 2. Append

**DECISIONS.md:**

```markdown
## {YYYY-MM-DD} — {short title}

{decision}
Why: {rationale — the why is the payload; a decision without why gets re-litigated}
{Supersedes: {date} — {old title}, if replacing an earlier decision}
```

**FACTS.md:**

```markdown
## {YYYY-MM-DD} — {short title}

{fact}
Source: {where this was learned — command output, doc URL, file path. "unverified" only if truly
uncheckable, and say why}
```

## 3. Confirm

One line: which file, what title.

</process>
