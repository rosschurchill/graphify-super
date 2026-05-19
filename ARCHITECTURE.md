# Architecture

graphify is a Claude Code skill backed by a Python library. The skill orchestrates the library; the library can be used standalone.

## Pipeline

```
detect()  →  extract()  →  build_graph()  →  cluster()  →  analyze()  →  report()  →  export()
```

Each stage is a single function in its own module. They communicate through plain Python dicts and NetworkX graphs - no shared state, no side effects outside `graphify-out/`.

## Module responsibilities

| Module | Function | Input → Output |
|--------|----------|----------------|
| `detect.py` | `collect_files(root)` | directory → `[Path]` filtered list |
| `extract.py` | `extract(path)` | file path → `{nodes, edges}` dict |
| `build.py` | `build_graph(extractions)` | list of extraction dicts → `nx.Graph` |
| `cluster.py` | `cluster(G)` | graph → graph with `community` attr on each node |
| `analyze.py` | `analyze(G)` | graph → analysis dict (god nodes, surprises, questions) |
| `report.py` | `render_report(G, analysis)` | graph + analysis → GRAPH_REPORT.md string |
| `export.py` | `export(G, out_dir, ...)` | graph → Obsidian vault, graph.json, graph.html, graph.svg |
| `callflow_html.py` | `write_callflow_html(...)` | graphify-out files → Mermaid architecture/call-flow HTML |
| `ingest.py` | `ingest(url, ...)` | URL → file saved to corpus dir |
| `cache.py` | `check_semantic_cache / save_semantic_cache` | files → (cached, uncached) split |
| `security.py` | validation helpers | URL / path / label → validated or raises |
| `validate.py` | `validate_extraction(data)` | extraction dict → raises on schema errors |
| `serve.py` | `start_server(graph_path)` | graph file path → MCP stdio server |
| `watch.py` | `watch(root, flag_path)` | directory → writes flag file on change |
| `benchmark.py` | `run_benchmark(graph_path)` | graph file → corpus vs subgraph token comparison |
| `dedup.py` | `deduplicate_entities(nodes, edges, ...)` | nodes+edges → merged nodes+edges (exact norm → entropy gate → MinHash/LSH blocking → Jaro-Winkler → union-find) |
| `manifest.py` | `save_manifest / load_manifest / detect_incremental` | thin re-export shim around the same helpers in `detect.py` (kept for backwards-compatible imports) |
| `llm.py` | `_call_llm(prompt, backend, ...)` / direct extractors | prompt + backend choice → semantic extraction dict; supports Claude, Gemini, OpenAI, Kimi |
| `prs.py` | `graphify prs` CLI entry | open PRs (via `gh`) → terminal dashboard with CI/review state, worktree mapping, graph-impact, optional Opus triage |
| `global_graph.py` | `update_global / load_global` | per-repo `graph.json` → aggregated graph under `~/.graphify/` (cross-repo view) |
| `google_workspace.py` | `export_shortcuts(paths)` | `.gdoc/.gsheet/.gslides` shortcut files → Markdown sidecars via the `gws` CLI |
| `transcribe.py` | `transcribe(path)` | video/audio file (mp4/mov/mp3/wav/...) → text transcript via `faster-whisper` |
| `tree_html.py` | `write_tree_html(graph_path, out)` | graph file → self-contained D3 v7 collapsible-tree HTML view (printable module overview) |

## Extraction output schema

Every extractor returns:

```json
{
  "nodes": [
    {"id": "unique_string", "label": "human name", "source_file": "path", "source_location": "L42"}
  ],
  "edges": [
    {"source": "id_a", "target": "id_b", "relation": "calls|imports|uses|...", "confidence": "EXTRACTED|INFERRED|AMBIGUOUS"}
  ]
}
```

`validate.py` enforces this schema before `build_graph()` consumes it.

## Confidence labels

| Label | Meaning |
|-------|---------|
| `EXTRACTED` | Relationship is explicitly stated in the source (e.g., an import statement, a direct call) |
| `INFERRED` | Relationship is a reasonable deduction (e.g., call-graph second pass, co-occurrence in context) |
| `AMBIGUOUS` | Relationship is uncertain; flagged for human review in GRAPH_REPORT.md |

## Adding a new language extractor

1. Add a `extract_<lang>(path: Path) -> dict` function in `extract.py` following the existing pattern (tree-sitter parse → walk nodes → collect `nodes` and `edges` → call-graph second pass for INFERRED `calls` edges). For simple languages, add only a `LanguageConfig` and let `_extract_generic` handle the walk.
2. Register the file suffix in the `_DISPATCH` table (`extract.py`) and the `_get_extractor` registry.
3. Add the suffix to `CODE_EXTENSIONS` in `detect.py` and `_WATCHED_EXTENSIONS` in `watch.py`.
4. Add the tree-sitter package to `pyproject.toml` dependencies.
5. Add a fixture file to `tests/fixtures/` and tests to `tests/test_languages.py`.

`dedup.py` (entity deduplication) and `manifest.py` (re-export shim around `detect.py`) are language-agnostic and need **no** per-language entries. The incremental-update path (`detect_incremental` → `build_merge`) inherits the new extension automatically via `CODE_EXTENSIONS`.

## Security

All external input passes through `graphify/security.py` before use:

- URLs → `validate_url()` (http/https only) + `_NoFileRedirectHandler` (blocks file:// redirects)
- Fetched content → `safe_fetch()` / `safe_fetch_text()` (size cap, timeout)
- Graph file paths → `validate_graph_path()` (must resolve inside `graphify-out/`)
- Node labels → `sanitize_label()` (strips control chars, caps 256 chars, HTML-escapes)

See `SECURITY.md` for the full threat model.

## Testing

One test file per module under `tests/`. Run with:

```bash
pytest tests/ -q
```

All tests are pure unit tests - no network calls, no file system side effects outside `tmp_path`.
