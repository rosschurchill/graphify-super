# Codex Skill Requirements

This document defines how graphify project skills in `.agents/skills/` should be written for the OpenAI Codex CLI.

## How Codex loads skills

Codex uses a **two-phase loading strategy**:

1. **Boot phase** — Codex scans all installed skills and loads only `name` + `description` from each SKILL.md into the system prompt (capped at ~8,000 chars total). This is what drives automatic skill selection.
2. **Execution phase** — when a skill is selected (via `$skill-name` or automatic trigger), the full SKILL.md body is injected as context for that session.

**Consequence:** the `description` field is the primary trigger mechanism. If the description doesn't match how a user phrases a request, the skill won't fire automatically. Put all "when to use" signal in the description — not in the body.

## Frontmatter schema

```yaml
---
name: fix                          # required — lowercase-hyphenated, matches folder name
description: >                     # required — one-sentence trigger + purpose, max 1024 chars
  Use when the user asks to pick up the next backlog item, fix a bug, or
  continue work from BACKLOG.md — verifies the bug exists, applies a minimal
  fix, runs the affected tests, and commits with a clear message.
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]  # optional — whitelist tools
argument-hint: "[item-id or keyword]"                 # optional — shown as parameter hint
---
```

### Required fields

| Field | Notes |
|---|---|
| `name` | Must match the directory name exactly. Lowercase, hyphens only. |
| `description` | The trigger. Front-load the "when to use" signal. Include the command name (`/fix`, `$fix`) and the key action words a user would type. Max 1024 chars. |

### Recommended optional fields

| Field | Notes |
|---|---|
| `allowed-tools` | Scope permissions to what the skill actually needs. Common set: `[Read, Edit, Write, Bash, Glob, Grep]`. Read-only skills: `[Read, Bash, Glob, Grep]`. |
| `argument-hint` | Short placeholder shown in the skill picker UI (e.g. `"<language-name>"`). |

## Body structure

```markdown
## Overview
One paragraph: what the skill does and why it exists.

## When to Use
Bullet list of concrete trigger conditions — the phrases or situations that should invoke this skill.

## Steps
Numbered, imperative steps. Each step should be actionable. Reference file paths concretely.

## Usage
Short examples of invocation.

## Key Behaviours
Edge cases, fallback logic, things that would surprise a reader.
```

Sections are optional but keep this order when present. Keep the total body under 500 lines.

## Writing the description

The description is the **only thing Codex reads at boot time**. Write it as if answering: "when should I pick this skill?"

Good:
```
Use when the user asks to pick up the next backlog item, fix a reported bug,
continue from BACKLOG.md, or asks '/fix' — reads BACKLOG.md, verifies the
bug exists in current code, applies a minimal targeted fix, runs affected
tests, and commits one fix per commit.
```

Bad (too vague, won't trigger):
```
Fixes bugs in the codebase.
```

Rules:
- Include the slash/dollar command name (`/fix`, `$fix`) so manual invocations match
- Include the key action verbs a user would type when asking for this
- Mention the output/deliverable (e.g. "commits with a clear message", "writes to `.claude/context/`")
- Keep it under 200 words

## Tool allowlists

Scope each skill to what it actually needs:

| Skill type | Suggested `allowed-tools` |
|---|---|
| Read-only analysis (`/map`, `/arch`, `/perf`, `/map-sec`) | `[Read, Bash, Glob, Grep]` |
| Write-and-commit (`/fix`, `/lang`) | `[Read, Edit, Write, Bash, Glob, Grep]` |
| Run-and-report (`/graph`, `/test`, `/review`) | `[Read, Bash, Glob, Grep]` |

## Our skills

The 9 project skills and their intended scope:

| Skill | Command | Scope | Output |
|---|---|---|---|
| `fix` | `$fix [item-id]` | Write+commit | Minimal bug fix committed to git |
| `lang` | `$lang <language>` | Write+commit | New language extractor scaffolded and tested |
| `graph` | `$graph [path]` | Run+report | `graphify update` run, diff reported |
| `test` | `$test [module]` | Run+report | pytest run, failures surfaced with file:line |
| `review` | `$review [base]` | Read+report | PR summary vs base branch |
| `map` | `$map <feature>` | Read+write | `.claude/context/<feature>.md` written |
| `map-sec` | `$map-sec <feature>` | Read+write | `.claude/context/security-<feature>.md` written |
| `arch` | `$arch <feature>` | Read+report | Architecture review report |
| `perf` | `$perf <feature>` | Read+report | Performance audit report |

## Install

Skills are installed into `.agents/skills/` by running:

```bash
graphify skills install --platform codex
```

The install command reads each `.claude/skills/<name>/SKILL.md`, adds the correct Codex frontmatter, and writes to `.agents/skills/<name>/SKILL.md`. After editing skills in `.agents/skills/`, commit both the source (`.claude/skills/`) and the generated output (`.agents/skills/`) so both are available in the repo.

## Codex invocation

Users invoke skills in Codex with `$` prefix:

```
$fix
$fix 512
$lang swift
$map extract
$map-sec install
```

Codex also auto-selects skills based on `description` matching — a user typing "pick up the next bug" should trigger `$fix` automatically if the description is written well.
