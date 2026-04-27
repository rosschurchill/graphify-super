# Lang — Scaffold a New Language Extractor

Scaffolds a complete new language extractor for graphify: fixture file, extract function, detect/watch registration, pyproject.toml dependency, and tests.

## Argument handling

Parse the language name from the invocation. Examples:
- `/lang swift` → language = `swift`
- `/lang kotlin` → language = `kotlin`
- `/lang haskell` → language = `haskell`

The argument is required. If missing, ask the user which language to scaffold.

## Steps

1. **Parse the language name** from the arguments (e.g. `/lang swift` → language = `swift`).

2. **Research the tree-sitter package** — check PyPI for `tree-sitter-<language>` and confirm the package name and import path. If uncertain, note it and proceed with the most likely name.

3. **Find an existing extractor to use as a model** — read a similar language extractor in `graphify/extract.py` (prefer one with classes + functions, e.g. Python or TypeScript).

4. **Add the tree-sitter dependency** to `pyproject.toml`:
   ```
   "tree-sitter-<language>",
   ```

5. **Create a fixture file** at `tests/fixtures/sample.<ext>` with:
   - At least one class definition
   - At least two function/method definitions
   - At least one import statement
   - A brief comment

6. **Add the extractor function** to `graphify/extract.py`:
   - Function name: `extract_<language>(path: Path) -> dict`
   - Register in the `extract()` dispatch dict (suffix → function)
   - Register in `collect_files()` suffix list
   - Follow the existing node/edge schema exactly

7. **Register the extension** in:
   - `graphify/detect.py` → `CODE_EXTENSIONS` set
   - `graphify/watch.py` → `_WATCHED_EXTENSIONS` set

8. **Add tests** to `tests/test_languages.py`:
   - `test_extract_<language>_nodes` — assert at least one node is returned
   - `test_extract_<language>_has_class` — assert a class node is present
   - `test_extract_<language>_has_function` — assert a function node is present

9. **Run the new tests**:
   ```bash
   pytest tests/test_languages.py -q -k "<language>"
   ```
   Fix any failures before reporting done.

10. **Report** what was created: fixture path, function name, file extensions registered, test names.

## Node/edge schema (must match exactly)

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

## Key Behaviours

- If the tree-sitter package doesn't exist yet, say so and scaffold a stub extractor with a clear `# TODO` comment noting the missing package.
- Do not commit — leave that to the user after review.
- If the language has unusual scoping (e.g. no classes), adapt the fixture and tests accordingly and explain why.
