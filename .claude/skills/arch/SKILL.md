# /arch Skill

Architecture review of a named feature or module via The Architect subagent. Identifies over/under-engineering, coupling, and refactoring opportunities. Saves output to `.claude/context/arch-<feature>.md`.

## Trigger

`/arch <feature>`

Examples: `/arch extract`, `/arch hooks`, `/arch cli`

## Steps

1. **Parse the feature name** from the arguments.

2. **Find the relevant files** — search by name and content keyword to identify all files in scope.

3. **Spawn an Architect subagent** (`subagent_type: "The Architect"`) with this prompt (substituting placeholders):

   ```
   You are reviewing the architecture of the "<feature>" area in the codebase at <project_root>.

   The project is graphify-super — a Python CLI/library that converts codebases into knowledge graphs via tree-sitter AST extraction, NetworkX graph building, community clustering, LLM analysis, and HTML/JSON export. Each pipeline stage is a single function in its own module communicating via plain dicts.

   Relevant files: <file list>

   Assess:
   1. Is this area appropriately complex for what it does, or is it over/under-engineered?
   2. Are there coupling or cohesion problems?
   3. Are abstractions at the right level — not too early, not too late?
   4. What would a new contributor find confusing or surprising?
   5. What are the top 1-3 refactoring moves that would most improve maintainability?

   Return ONLY this format:

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

4. **Write the output** to `<project_root>/.claude/context/arch-<feature>.md`.

5. **Confirm** to the user: `Architecture review written to .claude/context/arch-<feature>.md`

## Behaviour notes

- The Architect subagent burns its own context. The main session only receives the condensed review.
- If `.claude/context/` does not exist, create it before writing.
- Overwrite any existing arch review for the same feature (it's a refresh).
- Pair with `/map <feature>` to get structural context before the architecture review.
