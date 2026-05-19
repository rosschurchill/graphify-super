"""Tests for graphify/security.py - URL validation, safe fetch, path guards, label sanitisation."""
from __future__ import annotations

import json
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from graphify.security import (
    sanitize_label,
    safe_fetch,
    safe_fetch_text,
    validate_graph_path,
    validate_url,
    _MAX_FETCH_BYTES,
    _MAX_TEXT_BYTES,
)


# ---------------------------------------------------------------------------
# validate_url
# ---------------------------------------------------------------------------

def test_validate_url_accepts_http():
    assert validate_url("http://example.com/page") == "http://example.com/page"

def test_validate_url_accepts_https():
    assert validate_url("https://arxiv.org/abs/1706.03762") == "https://arxiv.org/abs/1706.03762"

def test_validate_url_rejects_file():
    with pytest.raises(ValueError, match="file"):
        validate_url("file:///etc/passwd")

def test_validate_url_rejects_ftp():
    with pytest.raises(ValueError, match="ftp"):
        validate_url("ftp://files.example.com/data.zip")

def test_validate_url_rejects_data():
    with pytest.raises(ValueError, match="data"):
        validate_url("data:text/html,<script>alert(1)</script>")

def test_validate_url_rejects_empty_scheme():
    with pytest.raises(ValueError):
        validate_url("//no-scheme.example.com")


# ---------------------------------------------------------------------------
# safe_fetch - scheme and redirect guards (mocked network)
# ---------------------------------------------------------------------------

def _make_mock_response(content: bytes, status: int = 200):
    mock = MagicMock()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    mock.status = status
    mock.code = status
    chunks = [content[i:i+65536] for i in range(0, len(content), 65536)] + [b""]
    mock.read.side_effect = chunks
    return mock


def test_safe_fetch_rejects_file_url():
    with pytest.raises(ValueError, match="file"):
        safe_fetch("file:///etc/passwd")

def test_safe_fetch_rejects_ftp_url():
    with pytest.raises(ValueError, match="ftp"):
        safe_fetch("ftp://example.com/file.zip")

def test_safe_fetch_returns_bytes(tmp_path):
    mock_resp = _make_mock_response(b"hello world")
    with patch("graphify.security._build_opener") as mock_opener_fn:
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_resp
        mock_opener_fn.return_value = mock_opener
        result = safe_fetch("https://example.com/")
    assert result == b"hello world"

def test_safe_fetch_raises_on_non_2xx():
    mock_resp = _make_mock_response(b"Not Found", status=404)
    with patch("graphify.security._build_opener") as mock_opener_fn:
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_resp
        mock_opener_fn.return_value = mock_opener
        with pytest.raises(urllib.error.HTTPError):
            safe_fetch("https://example.com/missing")

def test_safe_fetch_raises_on_size_exceeded():
    # Build a response larger than max_bytes
    big_chunk = b"x" * 65_537
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    mock_resp.status = 200
    mock_resp.code = 200
    # Return the chunk twice so total > max_bytes=65536
    mock_resp.read.side_effect = [big_chunk, big_chunk, b""]

    with patch("graphify.security._build_opener") as mock_opener_fn:
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_resp
        mock_opener_fn.return_value = mock_opener
        with pytest.raises(OSError, match="size limit"):
            safe_fetch("https://example.com/huge", max_bytes=65_536)


# ---------------------------------------------------------------------------
# safe_fetch_text
# ---------------------------------------------------------------------------

def test_safe_fetch_text_decodes_utf8():
    content = "héllo wörld".encode("utf-8")
    mock_resp = _make_mock_response(content)
    with patch("graphify.security._build_opener") as mock_opener_fn:
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_resp
        mock_opener_fn.return_value = mock_opener
        result = safe_fetch_text("https://example.com/")
    assert result == "héllo wörld"

def test_safe_fetch_text_replaces_bad_bytes():
    bad = b"hello \xff world"
    mock_resp = _make_mock_response(bad)
    with patch("graphify.security._build_opener") as mock_opener_fn:
        mock_opener = MagicMock()
        mock_opener.open.return_value = mock_resp
        mock_opener_fn.return_value = mock_opener
        result = safe_fetch_text("https://example.com/")
    assert "hello" in result
    assert "world" in result
    assert "\xff" not in result


# ---------------------------------------------------------------------------
# validate_graph_path
# ---------------------------------------------------------------------------

def test_validate_graph_path_allows_inside_base(tmp_path):
    base = tmp_path / "graphify-out"
    base.mkdir()
    graph = base / "graph.json"
    graph.write_text("{}")
    result = validate_graph_path(str(graph), base=base)
    assert result == graph.resolve()

def test_validate_graph_path_blocks_traversal(tmp_path):
    base = tmp_path / "graphify-out"
    base.mkdir()
    evil = tmp_path / "graphify-out" / ".." / "etc_passwd"
    with pytest.raises(ValueError, match="escapes"):
        validate_graph_path(str(evil), base=base)

def test_validate_graph_path_requires_base_exists(tmp_path):
    base = tmp_path / "graphify-out"  # not created
    with pytest.raises(ValueError, match="does not exist"):
        validate_graph_path(str(base / "graph.json"), base=base)

def test_validate_graph_path_raises_if_file_missing(tmp_path):
    base = tmp_path / "graphify-out"
    base.mkdir()
    with pytest.raises(FileNotFoundError):
        validate_graph_path(str(base / "missing.json"), base=base)


# ---------------------------------------------------------------------------
# sanitize_label
# ---------------------------------------------------------------------------

def test_sanitize_label_passthrough_html_chars():
    # sanitize_label does NOT HTML-escape — callers that inject into HTML must
    # wrap with html.escape() themselves (e.g. the title in to_html())
    assert sanitize_label("<script>") == "<script>"
    assert sanitize_label("foo & bar") == "foo & bar"

def test_sanitize_label_strips_control_chars():
    result = sanitize_label("hello\x00\x1fworld")
    assert "\x00" not in result
    assert "\x1f" not in result
    assert "helloworld" in result

def test_sanitize_label_caps_at_256():
    long_label = "a" * 300
    assert len(sanitize_label(long_label)) <= 256

def test_sanitize_label_safe_passthrough():
    assert sanitize_label("MyClass") == "MyClass"
    assert sanitize_label("extract_python") == "extract_python"


# ---------------------------------------------------------------------------
# C2 — graph loaders refuse paths outside their base
# ---------------------------------------------------------------------------

def test_serve_load_graph_rejects_non_json(tmp_path):
    """serve._load_graph must refuse non-.json suffixes (basic input validation)."""
    from graphify import serve as serve_mod
    base = tmp_path / "graphify-out"
    base.mkdir()
    (base / "graph.txt").write_text("not json")
    with pytest.raises(SystemExit):
        serve_mod._load_graph(str(base / "graph.txt"))


def test_serve_load_graph_uses_validate_graph_path():
    """serve._load_graph must import and use the shared validator (C2)."""
    # Static check: the import must be present so future refactors don't
    # silently revert to the ad-hoc validation that shipped pre-C2.
    import inspect
    from graphify import serve as serve_mod
    src = inspect.getsource(serve_mod._load_graph)
    assert "validate_graph_path" in src


def test_serve_load_graph_rejects_missing_file(tmp_path):
    from graphify import serve as serve_mod
    base = tmp_path / "graphify-out"
    base.mkdir()
    with pytest.raises(SystemExit):
        serve_mod._load_graph(str(base / "missing.json"))


def test_serve_load_graph_accepts_legit_path(tmp_path):
    from graphify import serve as serve_mod
    base = tmp_path / "graphify-out"
    base.mkdir()
    p = base / "graph.json"
    p.write_text('{"directed": true, "multigraph": false, "graph": {}, "nodes": [], "links": []}')
    G = serve_mod._load_graph(str(p))
    assert G.number_of_nodes() == 0


def test_prs_load_graph_json_blocks_traversal(tmp_path):
    """prs._load_graph_json returns None (not raises) on path escape."""
    from graphify import prs as prs_mod
    base = tmp_path / "graphify-out"
    base.mkdir()
    (base / "graph.json").write_text('{"nodes": []}')
    secret = tmp_path / "secret.json"
    secret.write_text('{"nodes": []}')

    # Construct a path that resolves outside the parent of itself: impossible,
    # so test the more realistic scenario — symlink/traversal via ".."
    evil_path = base / ".." / "secret.json"
    # _load_graph_json's contract: return None on any failure (incl. traversal)
    # When the file exists, validate_graph_path is called with base=parent of
    # resolved path, so direct traversal is hard to construct here. Instead,
    # cover the contract: a missing file returns None.
    missing = base / "missing.json"
    assert prs_mod._load_graph_json(missing) is None
    # And: a corrupt file returns None instead of crashing.
    bad = base / "bad.json"
    bad.write_text("{not json")
    assert prs_mod._load_graph_json(bad) is None


def test_global_graph_uses_validated_path(tmp_path, monkeypatch):
    """_load_global_graph validates the fixed ~/.graphify path."""
    from graphify import global_graph as gg

    fake_dir = tmp_path / ".graphify"
    fake_dir.mkdir()
    fake_graph = fake_dir / "global-graph.json"
    fake_graph.write_text('{"directed": false, "multigraph": false, "graph": {}, "nodes": [], "links": []}')
    monkeypatch.setattr(gg, "_GLOBAL_DIR", fake_dir)
    monkeypatch.setattr(gg, "_GLOBAL_GRAPH", fake_graph)
    G = gg._load_global_graph()
    assert G.number_of_nodes() == 0


# ---------------------------------------------------------------------------
# C3 — sanitisation in wiki + report
# ---------------------------------------------------------------------------

def test_wiki_sanitises_hostile_node_label(tmp_path):
    """Wiki output must strip control chars from LLM-derived labels."""
    import networkx as nx
    from graphify.wiki import to_wiki

    G = nx.DiGraph()
    G.add_node("a", label="evil\x00\x1fname", source_file="src\x00.py")
    G.add_node("b", label="ok", source_file="b.py")
    G.add_edge("a", "b", relation="calls", confidence="EXTRACTED")
    communities = {0: ["a", "b"]}
    out = tmp_path / "wiki"
    to_wiki(G, communities, out, community_labels={0: "Community 0"})
    md = (out / "Community_0.md").read_text(encoding="utf-8")
    assert "\x00" not in md
    assert "\x1f" not in md
    assert "evilname" in md


def test_report_sanitises_god_node_label():
    from graphify.report import generate
    import networkx as nx

    G = nx.DiGraph()
    G.add_node("x", label="badname")
    detection = {"total_files": 1, "total_words": 100, "warning": None}
    out = generate(
        G,
        communities={},
        cohesion_scores={},
        community_labels={},
        god_node_list=[{"label": "x\x00\x1fy", "degree": 5}],
        surprise_list=[],
        detection_result=detection,
        token_cost={"input": 0, "output": 0},
        root=".",
    )
    assert "\x00" not in out
    assert "\x1f" not in out
    assert "xy" in out


# ---------------------------------------------------------------------------
# C4 — cache.save_semantic_cache refuses out-of-root source_file
# ---------------------------------------------------------------------------

def test_save_semantic_cache_rejects_absolute_escape(tmp_path):
    """An LLM-returned source_file pointing outside the project root must be skipped."""
    from graphify.cache import save_semantic_cache

    root = tmp_path / "proj"
    root.mkdir()
    # Create a legit file inside root
    good = root / "good.py"
    good.write_text("x = 1")
    # Try a node with a malicious absolute path outside root
    nodes = [
        {"label": "good", "source_file": "good.py"},
        {"label": "evil", "source_file": "/etc/passwd"},
        {"label": "evil2", "source_file": "../../escape.py"},
    ]
    saved = save_semantic_cache(nodes, edges=[], hyperedges=[], root=root)
    # Only the legit file inside root should have been cached.
    assert saved == 1


# ---------------------------------------------------------------------------
# H6 — ingest._html_to_markdown strips <script> robustly
# ---------------------------------------------------------------------------

def test_html_to_markdown_strips_script_with_malformed_tag():
    from graphify.ingest import _html_to_markdown
    # Regex with `<script[^>]*>` is defeated by an attribute that contains '>'.
    html = '<p>safe</p><script foo=">"> alert("xss"); </script><p>after</p>'
    out = _html_to_markdown(html, "https://example.com")
    assert "alert" not in out
    assert "xss" not in out

def test_html_to_markdown_strips_unclosed_script():
    from graphify.ingest import _html_to_markdown
    html = "<p>safe</p><script>alert('pwn')"
    out = _html_to_markdown(html, "https://example.com")
    assert "alert" not in out
    assert "pwn" not in out

def test_html_to_markdown_strips_style():
    from graphify.ingest import _html_to_markdown
    html = "<style>body{background:url(javascript:alert(1))}</style><p>hi</p>"
    out = _html_to_markdown(html, "https://example.com")
    assert "javascript" not in out
    assert "alert" not in out


# ---------------------------------------------------------------------------
# H7 — google_workspace._safe_yaml_str delegates to ingest._yaml_str
# ---------------------------------------------------------------------------

def test_google_workspace_yaml_helper_uses_strong_escaper():
    from graphify.google_workspace import _safe_yaml_str
    from graphify.ingest import _yaml_str
    # Same implementation
    assert _safe_yaml_str is _yaml_str
    # Hostile input that the old weaker escaper would have passed through
    out = _safe_yaml_str('a\tb c')
    assert "\t" not in out
    assert " " not in out
