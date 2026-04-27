# /test Skill

Runs the test suite and surfaces failures with actionable file:line pointers.

## Trigger

`/test`

Optionally:
- `/test <module>` — run a single test file (e.g. `/test wiki` → `pytest tests/test_wiki.py -q`)
- `/test <keyword>` — run tests matching a keyword (e.g. `/test extract_python`)

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

## Behaviour notes

- Always use `-q` (quiet) mode to keep output compact.
- If pytest is not installed, suggest `pip install pytest`.
- If there are import errors at collection time, report those first — they block all tests in that file.
- This skill is read-only — it never edits code.
