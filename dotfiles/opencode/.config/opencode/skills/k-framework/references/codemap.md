---
name: k:codemap
description: Map codebase/infrastructure into CODEMAP.md — persistent orientation for future sessions
argument-hint: "[scope, e.g. network | docker | src/]"
allowed-tools:
    - Read
    - Write
    - Bash
    - Glob
    - Grep
    - Agent
---

<objective>
Produce or refresh `.k/CODEMAP.md` — what exists, where it lives, how it connects. Read-only
exploration; the map is the artifact.
</objective>

<process>

## 1. Scope

$ARGUMENTS narrows the sweep (e.g. just docker, just src/). No args = full map. If CODEMAP.md
exists, read it first — refresh sections that changed, don't regenerate from zero.

## 2. Explore (read-only)

Spawn read-only agent (Read, Bash, Glob, Grep — no Write/Edit) or explore directly:

- What's running: `docker ps`, `systemctl`, listening ports
- Where things live: configs, source, data volumes, dotfiles
- How it connects: networks, reverse proxies, env vars, secrets *locations* (never values)
- Gotchas: non-obvious behavior, fragile spots, "don't touch X"

## 3. Write

`.k/CODEMAP.md`:

```markdown
# Codemap

**Updated:** {YYYY-MM-DD}

## Running

{services/containers/processes: name, port, purpose}

## Layout

{paths → what they are}

## Connections

{who talks to whom, through what}

## Gotchas

{the stuff that bites}
```

Dense tables/bullets over prose. This file is skimmed at session start — optimize for that.

## 4. Cross-link

Offer `k:note fact` for durable standalone truths (ports, paths) so they're retrievable without
opening the map.

</process>
