---
name: review
description: >
  Use when the user asks for a branch review, PR summary, readiness check, or
  invokes `/review` or `$review` with an optional base branch — compares the
  current branch against the base, inspects commits and diff quality, and
  returns a concise review with blockers, warnings, and a PR-ready summary.
allowed-tools: [Read, Bash, Glob, Grep]
argument-hint: "[base-branch]"
---

## Overview
Use this skill to review the current branch against a base branch, summarize the change set, and surface quality, regression, and security concerns in PR-ready form.

## When to Use
- The user says `$review` or `/review`.
- The user asks for a code review of the current branch.
- The user asks for a PR summary or production-readiness check.
- The user asks what changed versus `main` or another base branch.

## Steps
1. Determine the base branch from the argument. If none was provided, infer it from the repo defaults and fall back to `main` when needed.
2. Gather the change set:
   ```bash
   git log <base>..HEAD --oneline
   git diff <base>...HEAD
   ```
3. If there are no commits or no diff against the base branch, report that and stop.
4. Review the commit list and diff for:
   - Whether each commit does one thing
   - Likely bugs, regressions, or missing edge cases
   - Security concerns such as unsafe input handling or trust-boundary mistakes
   - Consistency with surrounding code style and architecture
   - Test coverage and whether the tests are meaningful for the changes
5. Return the result in this structure:
   - `## Summary`
   - `## Commits`
   - `## Issues`
   - `## PR Description`
   - `## Verdict`
6. If the diff is unusually large, note that review confidence is lower and focus on the highest-risk areas first.

## Usage
```text
$review
$review main
$review release/v4
```

## Key Behaviours
- This skill reports findings; it does not edit code.
- Prefer concrete findings over broad narrative and tie concerns back to files or commits when possible.
- If the branch is empty relative to the base, say so explicitly instead of producing a forced summary.
