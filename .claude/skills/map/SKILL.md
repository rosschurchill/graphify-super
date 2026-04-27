# /map Skill

Maps a named feature into a compact context document by delegating all exploration to an Explore subagent.

## Trigger

`/map <feature>`

## Steps

1. **Parse the feature name** from the invocation arguments (e.g. `/map dashboard` → feature = `dashboard`).
2. **Determine the project root** — use the primary working directory of the current session.
3. **Spawn an Explore subagent** with the prompt template below, substituting `<feature>` and `<project_root>`.
4. **Take the subagent's returned markdown** as-is.
5. **Write it** to `<project_root>/.claude/context/<feature>.md` (create `.claude/context/` if it doesn't exist).
6. **Confirm** to the user: `Context map written to .claude/context/<feature>.md`

## Subagent prompt template

Pass this verbatim to an Explore subagent (subagent_type: "Explore"), substituting the placeholders:

```
You are mapping the "<feature>" feature in the codebase at <project_root>.

Your job is to explore this feature thoroughly and return a single compact markdown document. Do NOT return raw file contents. Return only the condensed summary.

Steps:
1. Find all files related to "<feature>" (search by name, directory, and content keywords).
2. For each file, identify: what it does, what it imports, what it exports/exposes.
3. Trace the dependency chain — both internal (other project files) and external (libraries, APIs).
4. Map the data flow: where does data enter this feature, how does it move, where does it go?
5. Identify any shared state, stores, events, or side effects.
6. If <project_root>/graphify-out/graph.json exists, run graphify queries for "<feature>" to surface connections the file scan might miss.
7. Note anything that looks incomplete, ambiguous, or surprising.

Return ONLY the completed context map in this exact format:

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

## Behaviour notes

- If `graphify-out/graph.json` does not exist, the subagent skips graphify queries — the file scan alone is sufficient.
- If `.claude/context/` does not exist, create it before writing.
- If a context map already exists for this feature, overwrite it (it's a refresh).
- This skill works on any project, not just graphify-super.
- The subagent burns its own context doing all exploration. The main session only ever receives the condensed output.
