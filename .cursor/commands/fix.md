# Fix — Next Backlog Item

Picks up the next open item from BACKLOG.md, verifies the bug exists, fixes it following project conventions, runs the affected tests, and commits.

## Argument handling

Parse the argument from the invocation. Examples:
- `/fix` → pick the next open BACKLOG.md item
- `/fix <item-id>` → target the item matching that ID or keyword
- `/fix wiki bug` → search for "wiki bug" in BACKLOG.md items

If no argument is given, default to the next uncompleted item in the Session Progress section.

## Steps

1. **Read BACKLOG.md** — find the Session Progress section. Identify the next uncompleted item (or the item matching the argument if one was given).

2. **State the target** — tell the user which item you're picking up before doing any code work.

3. **Verify the bug exists** — read the relevant source file(s) and confirm the described problem is present in current code. If the bug is already fixed, say so and stop. Do not fix something that isn't broken.

4. **Read the relevant context map** (if one exists in `.claude/context/`) before touching code.

5. **Fix** — make the minimal change required. Follow project conventions:
   - One commit per fix — each bug must be independently revertable
   - No refactoring beyond the scope of the fix
   - No comments unless the WHY is non-obvious

6. **Run the affected test file**:
   ```bash
   pytest tests/<affected_test_file>.py -q
   ```
   If tests fail, fix the failure before committing. Do not commit broken tests.

7. **Commit** — stage only the changed source files explicitly (`git add <file>`) — never `git add -A` or `git add .`. Never include: `BACKLOG.md`, `HANDOVER.md`, `UPGRADE_PLAN.md`, `GEMINI.md`, `.cursor/`, `.gemini/`.

8. **Update BACKLOG.md Session Progress** — mark the item complete and set the next item.

## Graphify-specific conventions

- After fixing an extractor (`extract.py`, `detect.py`, `watch.py`): run `pytest tests/test_languages.py -q`
- After fixing hooks (`hooks.py`): run `pytest tests/test_hooks.py -q`
- After fixing wiki (`wiki.py`): run `pytest tests/test_wiki.py -q`
- After fixing the CLI (`__main__.py`): run `pytest tests/ -q` (full suite)
- When in doubt: run `pytest tests/ -q`

## Key Behaviours

- Always verify first — the backlog was written from PR descriptions and may be stale.
- If multiple files need changes for one logical fix, that is still one commit.
- If the fix reveals a deeper problem that can't be addressed in one commit, stop, describe the blocker, and ask the user how to proceed.
