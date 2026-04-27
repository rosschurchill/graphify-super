# Map — Feature Context Document

Maps a named feature into a compact context document covering files, dependencies, data flow, and open questions.

## Argument handling

Parse the feature name from the invocation. Examples:
- `/map extract` → feature = `extract`
- `/map hooks` → feature = `hooks`
- `/map install` → feature = `install`

The argument is required. If missing, ask the user which feature to map.

## Steps

1. **Parse the feature name** from the invocation arguments.

2. **Find all files related to the feature** — search by name, directory, and content keywords. Cast wide: include source files, tests, fixtures, and config that touch this feature.

3. **For each file, identify:**
   - What it does
   - What it imports
   - What it exports or exposes

4. **Trace the dependency chain** — both internal (other project files) and external (libraries, APIs).

5. **Map the data flow:** where does data enter this feature, how does it move, where does it go?

6. **Identify any shared state, stores, events, or side effects.**

7. **If `graphify-out/graph.json` exists**, check it for connections the file scan might miss (cross-file call edges, community membership).

8. **Note anything that looks incomplete, ambiguous, or surprising.**

9. **Write the output** to `.claude/context/<feature>.md` (create `.claude/context/` if it doesn't exist). Use this format:

   ```markdown
   # <Feature> Context Map
   _Generated: <today's date> | Source: <project_root>_

   ## Entry Points
   Files / components where this feature starts (routes, page components, main modules).

   ## Key Files
   List of all files that are part of this feature with one-line descriptions.

   ## Dependencies
   ### Internal
   Other parts of the codebase this feature depends on.
   ### External
   Libraries, APIs, services.

   ## Data Flow
   Where data comes from, how it moves through the feature, where it goes.

   ## State & Events
   Any shared state, stores, events, or side effects this feature owns or touches.

   ## Open Questions
   Things that look incomplete, ambiguous, or surprising — flagged for the developer.
   ```

10. **Confirm** to the user: `Context map written to .claude/context/<feature>.md`

## Key Behaviours

- If `graphify-out/graph.json` does not exist, skip graphify queries — the file scan alone is sufficient.
- If a context map already exists for this feature, overwrite it (it's a refresh).
- Return a condensed summary — no raw file dumps.
