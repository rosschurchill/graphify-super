## graphify

This project has a graphify knowledge graph at graphify-out/.

Rules:
- Before answering architecture or codebase questions, read graphify-out/GRAPH_REPORT.md for god nodes and community structure
- If graphify-out/wiki/index.md exists, navigate it instead of reading raw files
- After modifying code files in this session, run `graphify update .` to keep the graph current (AST-only, no API cost)

## Skills

Project workflow skills are in `.agents/skills/` (installed by `graphify skills install --platform codex`).

| Skill | What it does |
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

Each skill file lives at `.agents/skills/<name>/SKILL.md` and contains the full step-by-step instructions.
