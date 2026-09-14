---
name: k:todo
description: Manage backlog — add, list, promote to a phase, or drop items
argument-hint: "[add \"item\" | done {n} | drop {n} | promote {n}]"
allowed-tools:
    - Read
    - Write
    - Glob
---

<objective>
Keep `.k/TODO.md` as the single backlog. Items are capture-now / decide-later — promotion to
phases is how they get done.
</objective>

<process>

## 1. Resolve action

- *(no args)* list open items with indices
- **add "item"** — append `- [ ] {item}`
- **done {n}** — remove item {n} (backlog items don't get checked, they leave)
- **drop {n}** — same as done, for items abandoned; note why in one line if non-obvious
- **promote {n}** — turn the item into a phase: suggest `/k:phase "{item}"`, and after phase
  creation remove the item from TODO

## 2. Write

Apply the change to `.k/TODO.md`. Keep the file flat — no sections, no priorities unless the user
asks. A backlog is a collection box, not a system.

## 3. Confirm

One line.

</process>
