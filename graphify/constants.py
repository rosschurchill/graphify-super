# Zero-dependency constants shared across graphify modules.
# This module must NOT import from any other graphify module — it sits at the
# bottom of the dependency stack so that detect.py, analyze.py, watch.py, and
# llm.py can all import from here without creating circular dependencies.

# ---------------------------------------------------------------------------
# File extension sets
# ---------------------------------------------------------------------------

CODE_EXTENSIONS: frozenset[str] = frozenset({
    '.py', '.ts', '.js', '.jsx', '.tsx', '.mjs', '.ejs', '.go', '.rs',
    '.java', '.groovy', '.gradle', '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp',
    '.rb', '.swift', '.kt', '.kts', '.cs', '.scala', '.php', '.lua', '.luau',
    '.toc', '.zig', '.ps1', '.ex', '.exs', '.m', '.mm', '.jl', '.vue',
    '.svelte', '.astro', '.dart', '.v', '.sv', '.sql', '.r', '.f', '.F',
    '.f90', '.F90', '.f95', '.F95', '.f03', '.F03', '.f08', '.F08',
    '.pas', '.pp', '.dpr', '.dpk', '.lpr', '.inc', '.dfm', '.lfm', '.lpk',
    '.sh', '.bash', '.json',
})

DOC_EXTENSIONS: frozenset[str] = frozenset({
    '.md', '.mdx', '.qmd', '.txt', '.rst', '.html', '.yaml', '.yml',
})

PAPER_EXTENSIONS: frozenset[str] = frozenset({'.pdf'})

IMAGE_EXTENSIONS: frozenset[str] = frozenset({
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg',
})

# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

# Coarse fallback used only when `tiktoken` is not installed.
# 1 token ≈ 4 chars is the standard heuristic for English/code on BPE tokenizers.
CHARS_PER_TOKEN: int = 4

# ---------------------------------------------------------------------------
# I/O utilities (no graphify imports allowed here)
# ---------------------------------------------------------------------------

import json as _json
from pathlib import Path as _Path
from typing import TypeVar as _TypeVar

_T = _TypeVar("_T")


def load_json_with_fallback(path: _Path, default: _T) -> _T:
    """Load JSON from *path*, returning *default* on any error (missing file,
    invalid JSON, permission error, etc.).

    Used by lightweight manifest loaders in global_graph.py and detect.py to
    avoid duplicating the try/except-around-json.loads pattern.
    """
    if path.exists():
        try:
            return _json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return default
