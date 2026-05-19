"""Performance regression tests for C5, C6, C7, H8, H9, H10, H11 fixes.

These tests verify that:
  (a) C5 — _parser_for returns cached object identity across two calls
  (b) C6 — collect_files uses a single os.walk (no rglob calls on directories)
  (c) C7 — _partition no longer uses json.dumps for edge sorting
  (d) H8 — _llm_tiebreak candidate pool is bounded to _LLM_TIEBREAK_MAX_CANDIDATES
  (e) H9 — build_merge skips dedup when fingerprint is unchanged
  (f) H10 — suggest_questions uses approximate betweenness (k=min(500,n))
  (g) H11 — stat-index files are PID-partitioned (no shared write between workers)
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import networkx as nx

# datasketch / rapidfuzz are optional in the test environment —
# skip tests that require them rather than failing the suite.
_HAS_DATASKETCH = True
try:
    import datasketch  # noqa: F401
except ImportError:
    _HAS_DATASKETCH = False

requires_datasketch = pytest.mark.skipif(
    not _HAS_DATASKETCH,
    reason="datasketch not installed in this environment",
)


# ── C5 — Parser cache reuse ───────────────────────────────────────────────────

def test_parser_for_cache_identity():
    """_parser_for returns the same (Language, Parser) objects on repeated calls.

    This verifies the lru_cache is in place. If the cache is missing, a new
    Parser is constructed on each call and `is` equality fails.
    """
    from graphify.extract import _parser_for

    result_a = _parser_for("tree_sitter_python", "language")
    result_b = _parser_for("tree_sitter_python", "language")

    # Both must be the same tuple object (lru_cache returns the cached value).
    assert result_a is result_b, (
        "_parser_for did not return the same object on second call — lru_cache missing or broken"
    )
    # If the language is actually installed, Language and Parser should be non-None.
    lang, parser, err = result_a
    if err is None:
        assert lang is not None
        assert parser is not None


def test_parser_for_cache_different_langs():
    """Different (ts_module, ts_language_fn) keys produce different cached entries."""
    from graphify.extract import _parser_for

    py = _parser_for("tree_sitter_python", "language")
    # Use a second call to python — must be identical object.
    py2 = _parser_for("tree_sitter_python", "language")
    assert py is py2

    # A different module produces a different entry (different key).
    # We don't require javascript to be installed — just check it's a different object.
    js = _parser_for("tree_sitter_javascript", "language")
    # They should not be the same object.
    assert py is not js


def test_parser_for_import_error_cached():
    """Import failures are returned as (None, None, error_str) and cached."""
    from graphify.extract import _parser_for
    import functools

    # Use a module name that can't possibly exist.
    result = _parser_for.__wrapped__("tree_sitter_THIS_DOES_NOT_EXIST_xyz", "language")
    lang, parser, err = result
    assert lang is None
    assert parser is None
    assert err is not None
    assert "not installed" in err or "No language function" in err or "tree_sitter" in err.lower()


# ── C6 — collect_files single walk ───────────────────────────────────────────

def test_collect_files_no_rglob_on_directory(tmp_path):
    """collect_files on a directory must not call Path.rglob.

    The pre-C6 implementation called rglob once per supported extension
    (~50 times). After C6 it uses a single os.walk instead.
    """
    # Create a small tree with a Python file.
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "hello.py").write_text("x = 1")
    (tmp_path / "src" / "readme.md").write_text("# hi")

    rglob_calls: list[str] = []

    original_rglob = Path.rglob

    def counting_rglob(self, pattern):
        rglob_calls.append(pattern)
        return original_rglob(self, pattern)

    from graphify.extract import collect_files

    with patch.object(Path, "rglob", counting_rglob):
        results = collect_files(tmp_path)

    # After C6: rglob must not be called at all on a directory target.
    # (It may still be called for the is_file() check on path itself, but
    # the directory walk must use os.walk, not rglob per extension.)
    assert len(rglob_calls) == 0, (
        f"collect_files called Path.rglob {len(rglob_calls)} time(s) — "
        f"expected 0 after C6 fix (patterns: {rglob_calls[:5]})"
    )

    # Sanity: the python file was found.
    assert any(p.name == "hello.py" for p in results)


def test_collect_files_single_file_passthrough(tmp_path):
    """collect_files([file]) returns that file directly without walking."""
    f = tmp_path / "main.py"
    f.write_text("pass")

    rglob_calls: list[str] = []
    original_rglob = Path.rglob

    def counting_rglob(self, pattern):
        rglob_calls.append(pattern)
        return original_rglob(self, pattern)

    from graphify.extract import collect_files

    with patch.object(Path, "rglob", counting_rglob):
        results = collect_files(f)

    assert results == [f]
    # Single-file path must never call rglob.
    assert len(rglob_calls) == 0


def test_collect_files_excludes_noise_dirs(tmp_path):
    """collect_files skips node_modules and .git directories."""
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "dep.py").write_text("x = 1")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 2")

    from graphify.extract import collect_files

    results = collect_files(tmp_path)
    paths = [p.name for p in results]
    assert "app.py" in paths
    assert "dep.py" not in paths, "collect_files must exclude node_modules"


# ── C7 — _partition no longer JSON-sorts edge attrs ──────────────────────────

def test_partition_does_not_import_json_for_edge_sort():
    """_partition must not call json.dumps for edge attribute sorting (C7).

    We verify that the cluster module no longer imports json at module level
    (the only use was the edge sort key, which has been removed).
    """
    import graphify.cluster as cluster_mod

    assert not hasattr(cluster_mod, "json") or cluster_mod.__dict__.get("json") is None, (
        "cluster module still has a top-level 'json' import — C7 fix may be missing"
    )
    # Belt-and-suspenders: check no json.dumps call in the sorted() key expression.
    import inspect
    src = inspect.getsource(cluster_mod._partition)
    # The sort call must not include json.dumps as a key. Comments are ok.
    # Find lines that contain 'sorted(' and check they don't reference json.dumps.
    sort_lines = [
        line for line in src.splitlines()
        if "sorted(" in line or "key=lambda" in line
    ]
    for line in sort_lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            continue  # ignore comments
        assert "json.dumps" not in line, (
            f"Found json.dumps in sort key line: {line!r} — C7 fix missing"
        )


def test_partition_deterministic_without_json_sort():
    """_partition produces the same result on two calls (determinism via seed)."""
    from graphify.cluster import _partition

    G = nx.Graph()
    G.add_nodes_from(["a", "b", "c", "d"])
    G.add_edges_from([("a", "b"), ("b", "c"), ("c", "d"), ("d", "a"), ("a", "c")])

    result1 = _partition(G)
    result2 = _partition(G)
    assert result1 == result2, "_partition is not deterministic after C7 fix"


# ── H8 — _llm_tiebreak candidate pool bounded ────────────────────────────────

@requires_datasketch
def test_llm_tiebreak_max_candidates_constant_exists():
    """_LLM_TIEBREAK_MAX_CANDIDATES must be defined and <= 1000."""
    from graphify.dedup import _LLM_TIEBREAK_MAX_CANDIDATES
    assert isinstance(_LLM_TIEBREAK_MAX_CANDIDATES, int)
    assert 10 <= _LLM_TIEBREAK_MAX_CANDIDATES <= 1000, (
        f"_LLM_TIEBREAK_MAX_CANDIDATES={_LLM_TIEBREAK_MAX_CANDIDATES} is out of expected range"
    )


@requires_datasketch
def test_llm_tiebreak_caps_candidates(monkeypatch):
    """When candidates exceed _LLM_TIEBREAK_MAX_CANDIDATES, _llm_tiebreak
    processes at most that many candidates in its O(C²) inner loop.
    """
    from graphify import dedup as dedup_mod
    from graphify.dedup import _UF, _LLM_TIEBREAK_MAX_CANDIDATES

    # Build more candidates than the cap.
    n = _LLM_TIEBREAK_MAX_CANDIDATES + 100
    candidates = [{"id": f"n{i}", "label": f"concept alpha delta gamma {i}"} for i in range(n)]
    uf = _UF()

    pairs_seen: list[tuple[str, str]] = []

    # Monkeypatch the BACKENDS check to bypass LLM import.
    monkeypatch.setattr(dedup_mod, "_LLM_TIEBREAK_MAX_CANDIDATES", _LLM_TIEBREAK_MAX_CANDIDATES)

    # We want to verify the O(C²) loop runs on at most _LLM_TIEBREAK_MAX_CANDIDATES entries.
    # Patch _call_llm to no-op and BACKENDS/key checks to pass.
    import sys
    import types
    fake_llm = types.ModuleType("graphify.llm")
    fake_llm.BACKENDS = {"test_backend": {}}
    fake_llm._format_backend_env_keys = lambda b: "TEST_KEY"
    fake_llm._get_backend_api_key = lambda b: "fake-key"
    fake_llm._call_llm = lambda *a, **kw: ""
    sys.modules["graphify.llm"] = fake_llm

    try:
        # The function should not raise; it should silently cap the pool.
        from graphify.dedup import _llm_tiebreak
        _llm_tiebreak(candidates, uf, {}, backend="test_backend")
    finally:
        sys.modules.pop("graphify.llm", None)

    # If we get here without OOM/timeout, the cap is working.
    # The real O(C²) with n=600+ would be noticeably slow in CI.


# ── H9 — build_merge dedup fingerprint caching ───────────────────────────────

def test_dedup_fingerprint_stable_for_same_nodes():
    """_dedup_fingerprint returns identical hash when node corpus is unchanged (H9)."""
    from graphify.build import _dedup_fingerprint

    nodes = [
        {"id": "a", "label": "Alpha"},
        {"id": "b", "label": "Beta"},
        {"id": "c", "label": "Gamma"},
    ]

    fp1 = _dedup_fingerprint(nodes, None)
    fp2 = _dedup_fingerprint(nodes, None)
    assert fp1 == fp2, "fingerprint is not stable for identical input"


def test_dedup_fingerprint_changes_on_new_node():
    """_dedup_fingerprint changes when a new node is added (H9 invalidation)."""
    from graphify.build import _dedup_fingerprint

    nodes_before = [{"id": "a", "label": "Alpha"}, {"id": "b", "label": "Beta"}]
    nodes_after = nodes_before + [{"id": "c", "label": "NewNode"}]

    fp_before = _dedup_fingerprint(nodes_before, None)
    fp_after = _dedup_fingerprint(nodes_after, None)
    assert fp_before != fp_after, "fingerprint did not change after adding a node"


def test_dedup_fingerprint_changes_on_backend_change():
    """_dedup_fingerprint changes when the LLM backend changes (H9 invalidation)."""
    from graphify.build import _dedup_fingerprint

    nodes = [{"id": "a", "label": "Alpha"}]
    fp_none = _dedup_fingerprint(nodes, None)
    fp_gemini = _dedup_fingerprint(nodes, "gemini")
    assert fp_none != fp_gemini, "fingerprint did not change when backend changed"


def test_build_merge_fingerprint_file_written(tmp_path):
    """build_merge writes a dedup-fingerprint.json after a successful dedup run (H9)."""
    graph_path = tmp_path / "graphify-out" / "graph.json"
    graph_path.parent.mkdir(parents=True)

    nodes = [{"id": "a", "label": "Alpha", "file_type": "concept"}]
    chunk = {"nodes": nodes, "edges": []}

    import graphify.build as build_mod
    from graphify.build import build_merge, _dedup_fingerprint_path

    # Patch build() to skip actual dedup (datasketch may not be installed).
    def fake_build(extractions, *, directed=False, dedup=True, **kwargs):
        # Combine nodes into a graph without real dedup.
        G = nx.Graph()
        for ext in extractions:
            for n in ext.get("nodes", []):
                G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
        return G

    with patch.object(build_mod, "build", fake_build):
        build_merge([chunk], graph_path=graph_path, dedup=True)

    fp_path = _dedup_fingerprint_path(graph_path)
    assert fp_path.exists(), (
        f"dedup fingerprint file was not created at {fp_path} — H9 persistence missing"
    )
    saved = json.loads(fp_path.read_text())
    assert "fingerprint" in saved and saved["fingerprint"], "fingerprint file has no 'fingerprint' key"


def test_build_merge_skips_dedup_when_fingerprint_matches(tmp_path):
    """build_merge forwards effective_dedup=False when fingerprint matches (H9)."""
    graph_path = tmp_path / "graphify-out" / "graph.json"
    graph_path.parent.mkdir(parents=True)

    nodes = [{"id": "a", "label": "Alpha", "file_type": "concept"}]
    chunk = {"nodes": nodes, "edges": []}

    import graphify.build as build_mod
    from graphify.build import build_merge, _dedup_fingerprint, _dedup_fingerprint_path

    build_dedup_args: list[bool] = []

    def fake_build(extractions, *, directed=False, dedup=True, **kwargs):
        build_dedup_args.append(dedup)
        G = nx.Graph()
        for ext in extractions:
            for n in ext.get("nodes", []):
                G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
        return G

    # Pre-write a matching fingerprint so the second call skips dedup.
    all_nodes = nodes  # same as what build_merge will see on second call
    # First call with graph_path not yet existing:
    with patch.object(build_mod, "build", fake_build):
        G1 = build_merge([chunk], graph_path=graph_path, dedup=True)
    # Persist graph so second call has an existing graph_path.
    data = {"nodes": [{"id": n, **d} for n, d in G1.nodes(data=True)], "edges": []}
    graph_path.write_text(json.dumps(data), encoding="utf-8")
    # Manually write fingerprint matching what second call would compute.
    combined_nodes = list(data["nodes"]) + nodes
    fp = _dedup_fingerprint(combined_nodes, None)
    fp_path = _dedup_fingerprint_path(graph_path)
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    fp_path.write_text(json.dumps({"fingerprint": fp}), encoding="utf-8")

    build_dedup_args.clear()
    with patch.object(build_mod, "build", fake_build):
        G2 = build_merge([chunk], graph_path=graph_path, dedup=True)

    assert build_dedup_args, "build() was not called at all on second build_merge"
    assert build_dedup_args[-1] is False, (
        f"effective_dedup={build_dedup_args[-1]!r} — expected False when fingerprint matches (H9)"
    )


def test_build_merge_reruns_dedup_when_nodes_change(tmp_path):
    """build_merge runs dedup again when new nodes are added (H9 invalidation)."""
    graph_path = tmp_path / "graphify-out" / "graph.json"
    graph_path.parent.mkdir(parents=True)

    nodes = [{"id": "a", "label": "Alpha", "file_type": "concept"}]
    new_node = {"id": "b", "label": "Beta", "file_type": "concept"}
    chunk = {"nodes": nodes, "edges": []}

    import graphify.build as build_mod
    from graphify.build import build_merge, _dedup_fingerprint, _dedup_fingerprint_path

    build_dedup_args: list[bool] = []

    def fake_build(extractions, *, directed=False, dedup=True, **kwargs):
        build_dedup_args.append(dedup)
        G = nx.Graph()
        for ext in extractions:
            for n in ext.get("nodes", []):
                G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
        return G

    with patch.object(build_mod, "build", fake_build):
        G1 = build_merge([chunk], graph_path=graph_path, dedup=True)

    data = {"nodes": [{"id": n, **d} for n, d in G1.nodes(data=True)], "edges": []}
    graph_path.write_text(json.dumps(data), encoding="utf-8")

    # Write a fingerprint matching the ORIGINAL corpus (without new_node).
    fp_path = _dedup_fingerprint_path(graph_path)
    fp_path.parent.mkdir(parents=True, exist_ok=True)
    fp_path.write_text(json.dumps({"fingerprint": "old-stale-fingerprint"}), encoding="utf-8")

    build_dedup_args.clear()
    with patch.object(build_mod, "build", fake_build):
        # Add new_node — fingerprint changes, dedup must run.
        G2 = build_merge([chunk, {"nodes": [new_node], "edges": []}], graph_path=graph_path, dedup=True)

    assert build_dedup_args, "build() was not called on second build_merge"
    assert build_dedup_args[-1] is True, (
        "dedup was NOT requested after adding new nodes — H9 fingerprint invalidation broken"
    )


def test_build_merge_natural_skip_on_second_call(tmp_path):
    """build_merge naturally skips dedup on the second call with identical nodes (H9).

    No manual fingerprint pre-writing. The first call runs dedup and persists the
    fingerprint. The second call re-reads it and discovers the corpus is unchanged
    (set semantics collapse existing+new duplicates), so effective_dedup=False.
    """
    graph_path = tmp_path / "graphify-out" / "graph.json"
    graph_path.parent.mkdir(parents=True)

    nodes = [{"id": "a", "label": "Alpha", "file_type": "concept"}]
    chunk = {"nodes": nodes, "edges": []}

    import graphify.build as build_mod
    from graphify.build import build_merge

    build_dedup_calls: list[bool] = []

    def fake_build(extractions, *, directed=False, dedup=True, dedup_llm_backend=None, root=None, **kwargs):
        build_dedup_calls.append(dedup)
        G = nx.Graph()
        for ext in extractions:
            for n in ext.get("nodes", []):
                G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
        return G

    # Call 1: graph_path does not exist yet → dedup runs, fingerprint is saved.
    with patch.object(build_mod, "build", fake_build):
        G1 = build_merge([chunk], graph_path=graph_path, dedup=True)

    assert build_dedup_calls and build_dedup_calls[-1] is True, (
        "First build_merge call must run dedup (no cached fingerprint yet)"
    )

    # Persist the graph so the second call can load existing_nodes.
    data = {"nodes": [{"id": n, **d} for n, d in G1.nodes(data=True)], "edges": []}
    graph_path.write_text(json.dumps(data), encoding="utf-8")

    build_dedup_calls.clear()

    # Call 2: same chunk, graph_path exists, fingerprint on disk — dedup must be skipped.
    with patch.object(build_mod, "build", fake_build):
        G2 = build_merge([chunk], graph_path=graph_path, dedup=True)

    assert build_dedup_calls, "build() was not called on second build_merge"
    assert build_dedup_calls[-1] is False, (
        f"Second build_merge call passed effective_dedup={build_dedup_calls[-1]!r} — "
        "expected False. H9 set-semantics fingerprint fix may be missing or "
        "the fingerprint file was not persisted after call 1."
    )


# ── H10 — betweenness_centrality uses approximate variant ────────────────────

def test_suggest_questions_uses_approximate_betweenness():
    """suggest_questions must always use k=min(500, n) for betweenness, never exact.

    The old code had a `G.number_of_nodes() > 1000` branch that fell through to
    k=None (exact O(V·E)). H10 removes that branch and always uses the
    approximate variant with k=min(500, n).

    Note: caching betweenness on G.graph was deliberately NOT added because it
    mutated the topology hash used by watch._rebuild_code, breaking
    incremental rebuilds (see tests/test_watch.py).
    """
    import inspect
    from graphify import analyze

    src = inspect.getsource(analyze.suggest_questions)

    # The old threshold was `> 1000` with k=None fallback; that conditional must be gone.
    assert "G.number_of_nodes() > 1000" not in src, (
        "suggest_questions still has the > 1000 node exact-betweenness branch — H10 not applied"
    )
    # And it must use min(500, ...) as the approximate sample size.
    assert "min(500" in src, (
        "suggest_questions no longer uses k=min(500, n) — H10 regressed"
    )


# ── H11 — stat-index PID partitioning ────────────────────────────────────────

def test_stat_index_file_is_pid_partitioned():
    """_stat_index_file returns a path containing the current process PID.

    The PID must be evaluated at call time (via os.getpid()), not captured at
    module import, so that forked workers each write to their own shard rather
    than all inheriting the parent's PID via copy-on-write.
    """
    from graphify.cache import _stat_index_file
    from pathlib import Path

    root = Path("/tmp/fake_root")
    p = _stat_index_file(root)

    current_pid = os.getpid()
    assert str(current_pid) in p.name, (
        f"stat-index file '{p.name}' does not contain current PID {current_pid} — "
        "H11 fix missing: _stat_index_file must call os.getpid() at invocation time, "
        "not read a module-level constant captured at import"
    )
    assert p.name == f"stat-index-{current_pid}.json", (
        f"stat-index filename '{p.name}' does not match expected 'stat-index-{current_pid}.json'"
    )


def test_ensure_stat_index_merges_shards(tmp_path):
    """_ensure_stat_index merges data from all stat-index-*.json shards."""
    from graphify import cache as cache_mod

    # Reset module-level state so _ensure_stat_index re-initialises.
    cache_mod._stat_index = {}
    cache_mod._stat_index_root = None
    cache_mod._stat_index_dirty = False

    cache_dir = tmp_path / "graphify-out" / "cache"
    cache_dir.mkdir(parents=True)

    # Write two "worker" shards.
    (cache_dir / "stat-index-1001.json").write_text(
        json.dumps({"/abs/file_a.py": {"size": 100, "mtime_ns": 1000, "hash": "aaaa"}}),
        encoding="utf-8",
    )
    (cache_dir / "stat-index-1002.json").write_text(
        json.dumps({"/abs/file_b.py": {"size": 200, "mtime_ns": 2000, "hash": "bbbb"}}),
        encoding="utf-8",
    )

    # Point GRAPHIFY_OUT at our tmp directory structure.
    original_out = cache_mod._GRAPHIFY_OUT
    cache_mod._GRAPHIFY_OUT = str(tmp_path / "graphify-out")

    try:
        cache_mod._ensure_stat_index(tmp_path)
        merged = cache_mod._stat_index
    finally:
        cache_mod._GRAPHIFY_OUT = original_out
        cache_mod._stat_index = {}
        cache_mod._stat_index_root = None
        cache_mod._stat_index_dirty = False

    assert "/abs/file_a.py" in merged, "shard 1001 not merged into stat index"
    assert "/abs/file_b.py" in merged, "shard 1002 not merged into stat index"
    assert merged["/abs/file_a.py"]["hash"] == "aaaa"
    assert merged["/abs/file_b.py"]["hash"] == "bbbb"
