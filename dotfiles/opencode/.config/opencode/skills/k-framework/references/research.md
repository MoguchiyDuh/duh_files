---
name: k:research
description: Research a topic into RESEARCH/{topic}.md with mandatory sources, plus INDEX entry
argument-hint: "\"topic\" [extra focus]"
allowed-tools:
    - Read
    - Write
    - WebSearch
    - WebFetch
    - Glob
    - Grep
---

<objective>
Research a topic and persist it decision-oriented, so no future session researches it again.
Sources are mandatory — a claim without a source cannot be asserted.
</objective>

<process>

## 1. Dedup check

Read `.k/RESEARCH/INDEX.md` (if exists) and `.k/FACTS.md`. If the topic (or a near match) was
already researched: say so, show the INDEX takeaway, ask whether to extend that file or research a
genuinely new angle. Never silently redo work.

## 2. Research

WebSearch/WebFetch the topic + $ARGUMENTS focus. Prefer primary sources (official docs, changelogs,
GitHub issues) over blog spam. Cross-check version-sensitive claims (does this apply to *our*
stack version from PROJECT.md?).

## 3. Write

`.k/RESEARCH/{topic-slug}.md`:

```markdown
# {Topic}

**Researched:** {YYYY-MM-DD} | **Stack context:** {relevant versions from PROJECT.md}

## Verdict

{the answer in 2-3 lines — what to do and why. If no clear verdict: what was learned and what
remains open}

## Findings

{dense bullets. every claim carries its source inline}

## Sources

{full URLs, verbatim — not abbreviated}
```

## 4. INDEX entry

Append to `.k/RESEARCH/INDEX.md`:

```markdown
| {topic} | {one-line takeaway} | {YYYY-MM-DD} | {file} |
```

## 5. Surface facts

If research produced durable truths (ports, versions, limits), offer `k:note fact` for each —
research files are for depth, FACTS.md is for retrieval.

</process>
