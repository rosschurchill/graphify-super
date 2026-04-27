# Arch — Architecture Review

Architecture review of a named feature or module. Identifies over/under-engineering, coupling, and refactoring opportunities. Saves output to `.claude/context/arch-<feature>.md`.

## Argument handling

Parse the feature name from the invocation. Examples:
- `/arch extract` → feature = `extract`
- `/arch hooks` → feature = `hooks`
- `/arch cli` → feature = `cli`

The argument is required. If missing, ask the user which feature to review.

## Steps

1. **Parse the feature name** from the arguments.

2. **Find the relevant files** — search by name and content keyword to identify all files in scope.

3. **Assess the architecture** of the feature area:
   - Is this area appropriately complex for what it does, or is it over/under-engineered?
   - Are there coupling or cohesion problems?
   - Are abstractions at the right level — not too early, not too late?
   - What would a new contributor find confusing or surprising?
   - What are the top 1–3 refactoring moves that would most improve maintainability?

   Context: graphify-super is a Python CLI/library where each pipeline stage is a single function in its own module communicating via plain dicts — no shared state, no side effects outside `graphify-out/`.

4. **Write the output** to `.claude/context/arch-<feature>.md` (create `.claude/context/` if it doesn't exist). Use this format:

   ```markdown
   # <Feature> Architecture Review
   _Generated: <today's date> | Source: <project_root>_

   ## Complexity Assessment
   Over-engineered / Under-engineered / Appropriate — with rationale.

   ## Coupling & Cohesion
   What depends on what, and whether that's healthy.

   ## Abstraction Quality
   Where abstractions help vs. where they obscure.

   ## Surprise Points
   What would confuse a new contributor.

   ## Top Refactoring Moves
   1. ...
   2. ...
   3. ...

   ## Verdict
   One paragraph: is this area healthy or does it need attention before it grows further?
   ```

5. **Confirm** to the user: `Architecture review written to .claude/context/arch-<feature>.md`

## Key Behaviours

- Overwrite any existing arch review for the same feature (it's a refresh).
- Pair with `/map <feature>` to get structural context before reviewing the architecture.
- Focus on structural health, not style.
