---
name: test
description: >
  Use when the user asks to run pytest, check the test suite, isolate a failing
  module or keyword, or invokes `/test` or `$test` — runs the appropriate pytest
  command in quiet mode and reports pass counts or actionable failures with
  file:line pointers and likely source locations.
allowed-tools: [Read, Bash, Glob, Grep]
argument-hint: "[module or keyword]"
---

## Overview
Use this skill to run the relevant pytest scope and convert the results into a compact report with concrete failure pointers.

## When to Use
- The user says `$test` or `/test`.
- The user asks to run the whole test suite.
- The user asks to run tests for a module, feature, or keyword.
- The user wants failing assertions summarized without changing code.

## Steps
1. Determine the test scope from the argument:
   - No argument: `pytest tests/ -q`
   - Module name such as `wiki`: `pytest tests/test_<module>.py -q`
   - Keyword or test name: `pytest tests/ -q -k "<keyword>"`
2. Run the chosen pytest command and capture the output.
3. If all tests pass, report the number of passing tests and the runtime.
4. If tests fail, report each failure with:
   - `test_file.py:line_number`
   - The failing test name
   - The key assertion or actual-versus-expected detail from pytest output
   - The source file most likely responsible based on the traceback
5. If the run fails during collection, report import or setup errors first because they block the rest of the file.
6. Do not edit code as part of this skill unless the test run is being performed inside a larger `$fix` workflow that already requires a fix.

## Usage
```text
$test
$test wiki
$test extract_python
```

## Key Behaviours
- Always use `-q` to keep the output compact.
- If `pytest` is not installed, report that directly and suggest installing it.
- This skill is read-only in normal use and should not silently fix failures.
