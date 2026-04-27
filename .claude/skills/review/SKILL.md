# /review Skill

Reviews the current branch against main and produces a PR-ready summary with quality and security notes.

## Trigger

`/review`

Optionally: `/review <base-branch>` to compare against a branch other than main/v4.

## Steps

1. **Determine the base branch** — use the argument if given, otherwise detect from `git remote show origin` or default to `main`.

2. **Gather the diff**:
   ```bash
   git log <base>..HEAD --oneline
   git diff <base>...HEAD
   ```

3. **Spawn a Lead Developer subagent** (`subagent_type: "The Lead Developer"`) with this prompt (substituting the actual diff):

   ```
   Review the following branch diff for production readiness. The project is graphify-super — a Python CLI/library that converts codebases into knowledge graphs via AST extraction.

   Commits:
   <git log output>

   Diff:
   <git diff output>

   Assess:
   1. Does each commit do one thing? Are any commits too large or mixed?
   2. Are there any obvious bugs, regressions, or missing edge cases?
   3. Any security concerns (input validation, path traversal, injection)?
   4. Is the code consistent with the surrounding style?
   5. Are tests present and meaningful for the changes?

   Return a PR summary in this format:

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
   ```

4. **Present the subagent's output** to the user as-is.

## Behaviour notes

- The subagent sees the full diff; the main session only receives the summary.
- If the branch is up to date with main (no commits), say so and stop.
- If the diff is very large (>500 lines), note that to the user before spawning — large diffs get less precise review.
