# graphify-super — Claude Code Instructions

## What this project is

A fork/superset of [graphify](https://github.com/safishamsi/graphify) — a Claude Code skill + Python library that converts any codebase (plus docs, PDFs, images, videos) into a knowledge graph (AST + semantic extraction → community clustering → HTML viz + wiki + audit report).

This repo tracks upstream and adds fixes/features ahead of upstream merges.

- **Local branch:** `v4` (tracks upstream `v8`)
- **Current version:** v0.8.13
- **Python package:** `graphify/` — the library and CLI entry point

## Architecture

See `ARCHITECTURE.md` for the full pipeline. Quick reference:

```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

Each stage is a single function in its own module. They communicate via plain dicts and NetworkX graphs — no shared state, no side effects outside `graphify-out/`.

Key modules (27 total under `graphify/`):

| File | Role |
|---|---|
| `graphify/__main__.py` | CLI entry point — all subcommands and install handlers |
| `graphify/extract.py` | Language extractors — AST parsing → nodes/edges (~6640 lines, god-module) |
| `graphify/detect.py` | File collection — extension filtering, ignore rules, manifest helpers |
| `graphify/build.py` | Graph construction; merge + incremental dedup |
| `graphify/cluster.py` | Leiden / Louvain community detection |
| `graphify/analyze.py` | God nodes, surprising connections, suggested questions |
| `graphify/report.py` | GRAPH_REPORT.md generation |
| `graphify/export.py` | Graph export (JSON, HTML, SVG, Obsidian) |
| `graphify/hooks.py` | Git hook install/uninstall logic |
| `graphify/wiki.py` | Wiki article generation from graph |
| `graphify/watch.py` | File watcher for `--watch` mode + `_rebuild_code()` |
| `graphify/ingest.py` | URL fetcher (web, oEmbed, etc.) |
| `graphify/cache.py` | AST + semantic cache |
| `graphify/dedup.py` | Entity deduplication (MinHash/LSH + Jaro-Winkler) |
| `graphify/llm.py` | Direct LLM backends (Claude, Gemini, OpenAI, Kimi) |
| `graphify/prs.py` | `graphify prs` graph-aware PR dashboard |
| `graphify/global_graph.py` | Cross-repo `~/.graphify/` aggregate |
| `graphify/google_workspace.py` | `.gdoc/.gsheet/.gslides` shortcut export |
| `graphify/transcribe.py` | Video/audio → text via faster-whisper |
| `graphify/tree_html.py` | D3 collapsible-tree HTML view |
| `graphify/callflow_html.py` | Mermaid architecture / call-flow HTML |
| `graphify/serve.py` | MCP stdio server |
| `graphify/benchmark.py` | Corpus-vs-subgraph token benchmark |
| `graphify/security.py` | URL / path / label validation helpers |
| `graphify/validate.py` | Extraction schema validation |
| `graphify/manifest.py` | Thin shim re-exporting from `detect.py` |
| `graphify/__init__.py` | Lazy-import map for public surface |

## Graphify knowledge graph

This repo has its own graph at `graphify-out/`. Before answering architecture or codebase questions:
1. Read `graphify-out/GRAPH_REPORT.md` for god nodes and community structure
2. If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files
3. After modifying code files, run `graphify update .` to keep the graph current (AST-only, no API cost)

## Adding a new language extractor

1. Add `extract_<lang>(path: Path) -> dict` in `extract.py` following the existing pattern (or add a `LanguageConfig` and let `_extract_generic` handle it).
2. Register the suffix in the `_DISPATCH` table in `extract.py` and the `_get_extractor` registry (extract.py:6217).
3. Add the suffix to `CODE_EXTENSIONS` in `detect.py` and `_WATCHED_EXTENSIONS` in `watch.py`.
4. Add the tree-sitter package to `pyproject.toml` dependencies.
5. Add a fixture to `tests/fixtures/` and tests to `tests/test_languages.py`.

`dedup.py` and `manifest.py` are language-agnostic — no per-language entries needed there.

## Testing

```bash
pytest tests/ -q                    # full suite
pytest tests/test_wiki.py -q        # single module
```

All tests are pure unit tests — no network calls, no filesystem side effects outside `tmp_path`.

## Development conventions

- **One commit per fix** — each bug is independently revertable
- **Explicit `git add <file>`** — never `git add -A` or `git add .` (untracked planning files must stay out of commits: `BACKLOG.md`, `HANDOVER.md`, `UPGRADE_PLAN.md`, `GEMINI.md`, `.cursor/`, `.gemini/`)
- **Verify before fixing** — confirm the bug exists in current code before changing anything; backlog entries written from PR descriptions may be stale
- **Run the affected test file** after each fix before committing

## Pre-built context maps

Read these before touching the relevant module — saves re-exploration:

| Map | Covers |
|---|---|
| `.claude/context/extract.md` | `extract.py` — AST extraction, language dispatch, cross-file resolution, node/edge schema |
| `.claude/context/hooks.md` | `hooks.py` — git hook install/uninstall, marker system, `_rebuild_code()` flow |
| `.claude/context/wiki.md` | `wiki.py` — wiki article generation, communities/god-node flow |
| `.claude/context/install.md` | `__main__.py` — all install handlers, platform configs, skill file variants, hook registration |

## Current work

Active backlog is in `BACKLOG.md`. The **Session Progress** section at the top of that file shows:
- What's already been completed
- The next item to pick up
- Any session-specific notes

**Start there** — read the Session Progress section of `BACKLOG.md`, then pick up the "Next Up" item.

For the upgrade-related issues currently in flight, see `ISSUES.md` and `.reviews/`.

## Skills installation

Skills are installed via the upstream CLI (the old local `graphify skills install --platform cursor|codex` subcommand is gone):

```bash
graphify install                       # Claude Code (Linux/Mac) → ~/.claude/skills/graphify/
graphify install --platform windows    # Claude Code (Windows)
graphify cursor install                # Cursor → .cursor/rules/graphify.mdc
graphify install --platform codex      # Codex → .agents/skills/graphify/
graphify install --platform gemini     # Gemini CLI
graphify install --platform opencode   # OpenCode
graphify kiro install                  # Kiro
graphify antigravity install           # Google Antigravity
graphify vscode install                # VS Code Copilot Chat
graphify install --platform <P>        # aider | copilot | claw | droid | trae | trae-cn | hermes | kimi | pi
```

See README.md "Pick your platform" table for the full list. The project-local `.claude/skills/<name>/SKILL.md` workflow files are still consumed automatically by Claude Code.

### Available skills (project-local)

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

## Security

All external input passes through `graphify/security.py`:
- URLs → `validate_url()` (http/https only, blocks private/loopback/metadata IPs; redirect targets revalidated)
- Graph file paths → `validate_graph_path()` (must resolve inside `graphify-out/`)
- Node labels → `sanitize_label()` (strips control chars, HTML-escapes, caps at 256 chars)

See `SECURITY.md` for the full threat model. Note: several `.json` loaders and HTML/Markdown writers do not yet route through these helpers — see `ISSUES.md` C2/C3/C4.
