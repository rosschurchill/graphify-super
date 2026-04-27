---
name: fix
description: >
  Use when the user asks to pick up the next backlog item, continue from
  BACKLOG.md, fix a reported bug, or invokes `/fix` or `$fix` with an item id or
  keyword — reads BACKLOG.md, verifies the bug still exists in current code,
  applies a minimal targeted fix, runs the affected tests, updates backlog
  progress, and commits one fix per commit with a clear message.
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]
argument-hint: "[item-id or keyword]"
---

## Overview
Use this skill to take the next actionable bug from `BACKLOG.md`, confirm it is still real, fix it with the smallest safe change, validate it with the relevant tests, and leave a clean single-purpose commit.

## When to Use
- The user says `$fix` or `/fix`.
- The user asks to pick up the next backlog item.
- The user asks to continue from `BACKLOG.md`.
- The user asks for a targeted bug fix tied to a backlog item, ID, or keyword.

## Steps
1. Read `BACKLOG.md` and find the Session Progress section. If an argument was provided, locate the matching item by ID or keyword; otherwise pick the next incomplete item.
2. State which backlog item you are taking before editing code.
3. Verify the bug exists in current code by reading the relevant files and, when possible, reproducing it from tests or behavior. If it is already fixed or the backlog entry is stale, report that and stop.
4. Read any relevant context map in `.claude/context/` before changing code.
5. Apply the minimal fix needed. Keep the scope tight, avoid unrelated refactors, and add comments only when the reason for the change would otherwise be unclear.
6. Run the affected tests and fix any failures before proceeding.
   ```bash
   pytest tests/<affected_test_file>.py -q
   ```
7. Use graphify-specific test scope when it fits the touched area:
   - Extractor changes in `extract.py`, `detect.py`, or `watch.py`: `pytest tests/test_languages.py -q`
   - Hook changes in `hooks.py`: `pytest tests/test_hooks.py -q`
   - Wiki changes in `wiki.py`: `pytest tests/test_wiki.py -q`
   - CLI changes in `__main__.py`: `pytest tests/ -q`
   - If unsure: `pytest tests/ -q`
8. Stage only the files required for this fix with explicit `git add <file>` commands. Never use `git add -A` or `git add .`, and never include `BACKLOG.md`, `HANDOVER.md`, `UPGRADE_PLAN.md`, `GEMINI.md`, `.cursor/`, or `.gemini/` in the commit.
9. Commit exactly one logical fix with a clear message.
10. Update `BACKLOG.md` Session Progress to mark the item complete and point to the next item.

## Usage
```text
$fix
$fix 512
$fix wiki export regression
```

## Key Behaviours
- Always verify the bug first; backlog entries may be stale.
- Multiple file edits are acceptable if they are required for one logical fix.
- If the fix opens a larger problem that cannot be handled as one clean commit, stop and report the blocker instead of widening scope.
