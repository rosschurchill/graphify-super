# /graph Skill

Rebuilds the graphify knowledge graph for the current project and reports what changed.

## Trigger

`/graph`

Optionally: `/graph <path>` to target a specific directory (default: `.`)

## Steps

1. **Determine the target path** — use the argument if given, otherwise `.` (project root).

2. **Check if a graph already exists** at `graphify-out/graph.json`. Note the node/edge count before the update.

3. **Run the update**:
   ```bash
   graphify update <path>
   ```
   This re-extracts code files and updates the graph without any LLM calls.

4. **Read `graphify-out/GRAPH_REPORT.md`** after the update completes.

5. **Report the diff** — compare before/after:
   - Node count change (added / removed)
   - Edge count change
   - Any new god nodes or community shifts noted in the report
   - Files that were re-extracted

6. **Remind the user** of any god nodes flagged in the report, since those are architectural hot spots.

## Behaviour notes

- If `graphify` is not on PATH, suggest `pip install -e .` from the project root.
- If `graphify-out/graph.json` doesn't exist yet, this is a first-time build — skip the before-count step and just report the final state.
- This skill never makes LLM API calls — it's always safe to run.
- After large refactors, pair this with `/map <feature>` to get fresh context for the changed area.
