# Test — Run Test Suite

Runs the test suite and surfaces failures with actionable file:line pointers.

## Argument handling

Parse the optional scope from the invocation. Examples:
- `/test` → run full suite: `pytest tests/ -q`
- `/test wiki` → run single module: `pytest tests/test_wiki.py -q`
- `/test extract_python` → run by keyword: `pytest tests/ -q -k "extract_python"`

If no argument is given, run the full suite.

## Steps

1. **Determine scope** from the argument:
   - No argument → `pytest tests/ -q`
   - Module name (e.g. `wiki`) → `pytest tests/test_<module>.py -q`
   - Keyword → `pytest tests/ -q -k "<keyword>"`

2. **Run the tests** and capture output.

3. **If all tests pass** — report the count and duration. Done.

4. **If tests fail** — for each failure, report:
   - `test_file.py:line_number` — the failing assertion
   - The test name
   - The actual vs expected values (from pytest output)
   - Which source file is most likely responsible (based on the traceback)

5. **Do not fix failures automatically** — report them clearly so the user can decide what to fix. Exception: if the user invokes `/test` as part of a `/fix` workflow, fix the failure before reporting.

## Key Behaviours

- Always use `-q` (quiet) mode to keep output compact.
- If pytest is not installed, suggest `pip install pytest`.
- If there are import errors at collection time, report those first — they block all tests in that file.
- This command is read-only — it never edits code.
