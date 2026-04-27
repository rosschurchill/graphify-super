---
name: lang
description: >
  Use when the user asks to add a new language extractor, scaffold parser
  support, or invokes `/lang` or `$lang` with a language name — researches the
  tree-sitter package, adds the dependency, scaffolds fixture and extractor
  support, registers detect/watch extensions, adds targeted tests, and leaves
  the new language extractor ready for review.
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]
argument-hint: "<language-name>"
---

## Overview
Use this skill to scaffold a complete new language extractor for graphify, including parser dependency, fixture, extractor registration, extension detection, and focused tests.

## When to Use
- The user says `$lang` or `/lang`.
- The user asks to add support for a new language.
- The user asks to scaffold a new extractor, parser integration, or language fixture.

## Steps
1. Parse the language name from the invocation, for example `$lang swift`.
2. Determine the likely `tree-sitter-<language>` package and import path. If the package is uncertain or missing, note that explicitly and continue with the safest scaffold you can.
3. Read a similar extractor in `graphify/extract.py` to use as the implementation model, preferably one with both classes and functions.
4. Add the `tree-sitter-<language>` dependency to `pyproject.toml`.
5. Create a fixture at `tests/fixtures/sample.<ext>` containing at least one import, one brief comment, one class definition when the language supports classes, and at least two function or method definitions.
6. Add `extract_<language>(path: Path) -> dict` to `graphify/extract.py`.
7. Register the extractor in the dispatch map in `graphify/extract.py` and add the new suffix to the file collection logic.
8. Register the extension in `graphify/detect.py` under `CODE_EXTENSIONS`.
9. Register the extension in `graphify/watch.py` under `_WATCHED_EXTENSIONS`.
10. Add focused tests to `tests/test_languages.py`:
    1. `test_extract_<language>_nodes`
    2. `test_extract_<language>_has_class` when the language supports classes
    3. `test_extract_<language>_has_function`
11. Keep the node and edge schema aligned with existing extractors:
    ```python
    {
        "nodes": [
            {"id": "<relative_path>::<Name>", "label": "<Name>", "type": "class|function|method|import", "file": "<relative_path>", "line": <int>}
        ],
        "edges": [
            {"source": "<id>", "target": "<id>", "relation": "contains|imports|calls"}
        ]
    }
    ```
12. Run the targeted tests and fix any failures before reporting completion.
    ```bash
    pytest tests/test_languages.py -q -k "<language>"
    ```
13. Report what was created: fixture path, extractor function name, registered extensions, and test names.

## Usage
```text
$lang swift
$lang kotlin
$lang haskell
```

## Key Behaviours
- If no tree-sitter package exists yet, scaffold the extractor with a clear `TODO` marking the missing dependency.
- Do not commit automatically unless the user explicitly asks for a commit.
- If the language has unusual structure, adapt fixture and tests accordingly and explain the deviation.
