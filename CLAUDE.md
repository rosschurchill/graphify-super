# graphify-super — Claude Code Instructions

## What this project is

A fork/superset of [graphify](https://github.com/The-Pocket-World/graphify) — a Claude Code skill + Python library that converts any codebase into a knowledge graph (AST extraction → community clustering → HTML viz + wiki + audit report).

This repo tracks upstream and adds fixes and features ahead of upstream merges.

- **Branch:** `v4` (main working branch)
- **Current version:** v0.5.0
- **Python package:** `graphify/` — the library and CLI entry point

## Architecture

See `ARCHITECTURE.md` for the full pipeline. Quick reference:

```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

Each stage is a single function in its own module. They communicate via plain dicts and NetworkX graphs — no shared state, no side effects outside `graphify-out/`.

Key files:
| File | Role |
|---|---|
| `graphify/__main__.py` | CLI entry point — all subcommands and install handlers |
| `graphify/extract.py` | Language extractors — AST parsing → nodes/edges |
| `graphify/detect.py` | File collection — extension filtering, ignore rules |
| `graphify/build.py` | Graph construction from extraction output |
| `graphify/hooks.py` | Git hook install/uninstall logic |
| `graphify/wiki.py` | Wiki article generation from graph |
| `graphify/watch.py` | File watcher for `--watch` mode |
| `graphify/export.py` | Graph export (JSON, HTML, SVG, Obsidian) |

## Graphify knowledge graph

This repo has its own graph at `graphify-out/`. Before answering architecture or codebase questions:
1. Read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure
2. If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files
3. After modifying code files, run `graphify update .` to keep the graph current (AST-only, no API cost)

## Adding a new language extractor

1. Add `extract_<lang>(path: Path) -> dict` in `extract.py` following the existing pattern
2. Register suffix in `extract()` dispatch and `collect_files()`
3. Add suffix to `CODE_EXTENSIONS` in `detect.py` and `_WATCHED_EXTENSIONS` in `watch.py`
4. Add tree-sitter package to `pyproject.toml` dependencies
5. Add fixture to `tests/fixtures/` and tests to `tests/test_languages.py`

## Testing

```bash
pytest tests/ -q                    # full suite
pytest tests/test_wiki.py -q        # single module
```

All tests are pure unit tests — no network calls, no filesystem side effects outside `tmp_path`.

## Development conventions

- **One commit per fix** — each bug is independently revertable
- **Explicit `git add <file>`** — never `git add -A` or `git add .` (untracked planning files must stay out of commits: `BACKLOG.md`, `HANDOVER.md`, `UPGRADE_PLAN.md`, `GEMINI.md`, `.cursor/`, `.gemini/`)
- **Verify before fixing** — confirm the bug exists in current code before changing anything; the backlog was written from PR descriptions and may be stale
- **Run the affected test file** after each fix before committing

## Pre-built context maps

Read these before touching the relevant module — saves re-exploration:

| Map | Covers |
|---|---|
| `.claude/context/extract.md` | `extract.py` — AST extraction, language dispatch, cross-file resolution, node/edge schema |
| `.claude/context/hooks.md` | `hooks.py` — git hook install/uninstall, marker system, `_rebuild_code()` flow |
| `.claude/context/wiki.md` | `wiki.py` — wiki article generation, orphan bug, community/god-node flow |
| `.claude/context/install.md` | `__main__.py` — all install handlers, platform configs, skill file variants, hook registration |

## Current work

Active backlog is in `BACKLOG.md`. The **Session Progress** section at the top of that file shows:
- What's already been completed
- The next item to pick up
- Any session-specific notes

**Start there** — read the Session Progress section of `BACKLOG.md`, then pick up the "Next Up" item.

## Skills

Project skills live in `.claude/skills/`. Install them on any host with:

```bash
graphify skills install
```

This copies each skill to `~/.claude/skills/` so Claude Code picks them up. Run after cloning on a new machine.

| Command | What it does |
|---|---|
| `/fix` | Pick up next BACKLOG item → verify → fix → test → commit |
| `/lang <name>` | Scaffold a new language extractor (fixture, extract fn, detect/watch, tests) |
| `/graph [path]` | Run `graphify update` and report graph changes |
| `/test [module]` | Run pytest, surface failures with file:line pointers |
| `/review [base]` | Review current branch vs main, produce PR summary |
| `/map <feature>` | Map feature files, deps, and data flow → `.claude/context/<feature>.md` |
| `/map-sec <feature>` | Security audit of a feature → `.claude/context/security-<feature>.md` |
| `/arch <feature>` | Architecture review → `.claude/context/arch-<feature>.md` |
| `/perf <feature>` | Performance audit → `.claude/context/perf-<feature>.md` |

# fix
- **fix** (`.claude/skills/fix/SKILL.md`) - pick up next BACKLOG item, verify, fix, test, commit. Trigger: `/fix`
When the user types `/fix`, invoke the Skill tool with `skill: "fix"` before doing anything else.
# lang
- **lang** (`.claude/skills/lang/SKILL.md`) - scaffold a new language extractor. Trigger: `/lang`
When the user types `/lang`, invoke the Skill tool with `skill: "lang"` before doing anything else.
# graph
- **graph** (`.claude/skills/graph/SKILL.md`) - run graphify update and report changes. Trigger: `/graph`
When the user types `/graph`, invoke the Skill tool with `skill: "graph"` before doing anything else.
# test
- **test** (`.claude/skills/test/SKILL.md`) - run pytest, surface failures with file:line pointers. Trigger: `/test`
When the user types `/test`, invoke the Skill tool with `skill: "test"` before doing anything else.
# review
- **review** (`.claude/skills/review/SKILL.md`) - review current branch vs main, produce PR summary. Trigger: `/review`
When the user types `/review`, invoke the Skill tool with `skill: "review"` before doing anything else.
# map
- **map** (`.claude/skills/map/SKILL.md`) - map a feature's files, dependencies, and data flow into a compact context document. Trigger: `/map`
When the user types `/map`, invoke the Skill tool with `skill: "map"` before doing anything else.
# map-sec
- **map-sec** (`.claude/skills/map-sec/SKILL.md`) - security audit of a feature. Trigger: `/map-sec`
When the user types `/map-sec`, invoke the Skill tool with `skill: "map-sec"` before doing anything else.
# arch
- **arch** (`.claude/skills/arch/SKILL.md`) - architecture review of a feature or module. Trigger: `/arch`
When the user types `/arch`, invoke the Skill tool with `skill: "arch"` before doing anything else.
# perf
- **perf** (`.claude/skills/perf/SKILL.md`) - performance audit of a feature or module. Trigger: `/perf`
When the user types `/perf`, invoke the Skill tool with `skill: "perf"` before doing anything else.

## Security

All external input passes through `graphify/security.py`:
- URLs → `validate_url()` (http/https only)
- Graph file paths → `validate_graph_path()` (must resolve inside `graphify-out/`)
- Node labels → `sanitize_label()` (strips control chars, HTML-escapes)

See `SECURITY.md` for the full threat model.
