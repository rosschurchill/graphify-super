# Review — Branch Quality Review

Reviews the current branch against main and produces a PR-ready summary with quality and security notes.

## Argument handling

Parse the optional base branch from the invocation. Examples:
- `/review` → compare against `main` (or `v4` if that's the default)
- `/review v4` → compare against `v4`
- `/review origin/main` → compare against `origin/main`

If no argument is given, detect the base branch from `git remote show origin` or default to `main`.

## Steps

1. **Determine the base branch** — use the argument if given, otherwise detect from `git remote show origin` or default to `main`.

2. **Gather the diff**:
   ```bash
   git log <base>..HEAD --oneline
   git diff <base>...HEAD
   ```

3. **Review the diff** against these criteria:
   - Does each commit do one thing? Are any commits too large or mixed?
   - Are there any obvious bugs, regressions, or missing edge cases?
   - Any security concerns (input validation, path traversal, injection)?
   - Is the code consistent with the surrounding style?
   - Are tests present and meaningful for the changes?

4. **Produce a review report** in this format:

   ## Summary
   One paragraph describing what this branch does and why.

   ## Commits
   Brief verdict on each commit (good / needs splitting / needs message fix).

   ## Issues
   ### Blockers
   ### Warnings
   ### Nits

   ## PR Description (ready to paste)
   A complete PR body — summary, test plan, checklist.

   ## Verdict
   GO / NO-GO with one-sentence rationale.

## Key Behaviours

- If the branch is up to date with main (no commits), say so and stop.
- If the diff is very large (>500 lines), note that before reviewing — large diffs get less precise review.
- Focus on correctness, security, and test coverage — not style for its own sake.
