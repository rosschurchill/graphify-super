---
name: graph
description: >
  Use when the user asks to rebuild the project graph, refresh graphify output,
  inspect graph changes, or invokes `/graph` or `$graph` with an optional path —
  runs `graphify update`, reads the generated report, and summarizes node and
  edge count changes, architectural hot spots, and graph refresh results.
allowed-tools: [Read, Bash, Glob, Grep]
argument-hint: "[path]"
---

## Overview
Use this skill to refresh the graphify knowledge graph for the current project or a specific subpath and report what changed after the update.

## When to Use
- The user says `$graph` or `/graph`.
- The user asks to rebuild or refresh the graphify graph.
- The user asks for graph diff reporting after code changes.
- The user asks to run `graphify update` on a project or subdirectory.

## Steps
1. Determine the target path from the argument; default to `.`.
2. Check whether a prior graph exists at `graphify-out/graph.json` and record the current node and edge counts if present.
3. Run the update:
   ```bash
   graphify update <path>
   ```
4. Read `graphify-out/GRAPH_REPORT.md` after the update finishes.
5. Compare the graph before and after the run and report:
   - Node count changes
   - Edge count changes
   - Newly flagged or persistent god nodes
   - Community or structural shifts called out in the report
   - Files or areas re-extracted if the report shows them
6. Remind the user about any god nodes or other architectural hot spots noted in the report.

## Usage
```text
$graph
$graph .
$graph graphify
```

## Key Behaviours
- If `graphify-out/graph.json` does not exist yet, treat the run as a first build and report the final counts only.
- If `graphify` is not on `PATH`, suggest installing the project in editable mode so the command is available.
- This skill is run-and-report only; it does not edit application code.
