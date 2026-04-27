# Cursor Command Requirements

This document defines how graphify project commands in `.cursor/commands/` should be written for the Cursor IDE.

## How Cursor loads commands

Cursor scans `.cursor/commands/` at startup and registers every `.md` file as a slash command. When the user types `/fix`, Cursor injects the **entire file content** as context for that chat turn. There is no two-phase loading — the full file is always passed.

**Consequence:** unlike Codex skills, there is no separate "trigger" field. Cursor uses the filename as the command name. Everything in the file is immediately visible to the agent, so you can be specific and detailed without worrying about boot-time token cost.

## File naming

```
.cursor/commands/
├── fix.md           → /fix
├── lang.md          → /lang
├── graph.md         → /graph
├── map-sec.md       → /map-sec
└── ...
```

- Lowercase, hyphens allowed, no spaces
- `.md` extension only
- Filename (minus `.md`) is the exact slash command

## Format

Plain markdown. **No YAML frontmatter.** No special metadata fields.

```markdown
# Command Title

One-line summary of what this command does.

## Objective

Detailed description of the task, including what inputs to expect and what
the output should be.

## Steps

1. Step one — concrete, imperative, references actual file paths
2. Step two
3. ...

## Argument handling

Explain how to parse arguments from the invocation message (e.g. `/fix 512`
→ the `512` is the backlog item ID).

## Key Behaviours

Edge cases, fallback logic, things the agent should not do.
```

Sections are flexible — use what the command needs. Keep total length under ~400 lines.

## Writing good commands

Since the full file is injected, the first `#` heading and opening paragraph carry the most weight — they anchor the agent's understanding before it reads the steps.

Rules:
- **Lead with the job**, not the mechanics — "Fix the next backlog item" not "Read BACKLOG.md and find..."
- **Reference file paths concretely** — agents perform better with explicit paths than vague descriptions
- **Document argument parsing explicitly** — Cursor has no argument schema; the agent extracts arguments from the raw invocation message
- **Keep steps imperative** — "Read X", "Run Y", "Write Z" rather than "You should read X"
- **No Claude Code-isms** — do not reference the Skill tool, `skill:` invocations, or Claude Code hooks; this is plain Cursor chat
- **Cross-reference rules** — if a project rule in `.cursor/rules/` is relevant, mention it by path

## Argument handling pattern

Cursor passes the full invocation message to the agent. The command file should tell the agent how to extract arguments:

```markdown
## Argument handling

Parse the argument from the invocation. Examples:
- `/fix`          → pick the next open BACKLOG.md item
- `/fix 512`      → target item 512
- `/fix wiki bug` → search for "wiki bug" in BACKLOG.md items

If no argument is given, use the default behaviour described in Step 1.
```

## Our commands

| Command | Invocation | Scope | Output |
|---|---|---|---|
| `fix` | `/fix [item-id]` | Write+commit | Minimal bug fix committed to git |
| `lang` | `/lang <language>` | Write+commit | New language extractor scaffolded and tested |
| `graph` | `/graph [path]` | Run+report | `graphify update` run, diff reported |
| `test` | `/test [module]` | Run+report | pytest run, failures surfaced with file:line |
| `review` | `/review [base]` | Read+report | PR summary vs base branch |
| `map` | `/map <feature>` | Read+write | `.claude/context/<feature>.md` written |
| `map-sec` | `/map-sec <feature>` | Read+write | `.claude/context/security-<feature>.md` written |
| `arch` | `/arch <feature>` | Read+report | Architecture review report |
| `perf` | `/perf <feature>` | Read+report | Performance audit report |

## Install

Commands are installed into `.cursor/commands/` by running:

```bash
graphify skills install --platform cursor
```

The install copies each `.claude/skills/<name>/SKILL.md` to `.cursor/commands/<name>.md`. After editing commands in `.cursor/commands/`, commit them so they are available in the repo for all contributors.

## Cursor invocation

Users invoke commands by typing `/` in Cursor chat:

```
/fix
/fix 512
/lang swift
/map extract
/map-sec install
```

Cursor shows all available commands in the autocomplete menu when the user types `/`.
