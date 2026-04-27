---
name: map
description: >
  Use when the user asks to map a feature, trace related files and data flow,
  build implementation context, or invokes `/map` or `$map` with a feature name
  — finds the feature's entry points, dependencies, state, and data flow, then
  writes a compact context document to `.claude/context/<feature>.md`.
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]
argument-hint: "<feature>"
---

## Overview
Use this skill to build a compact context map for a named feature so later work can start from a focused file and dependency overview instead of re-exploring the codebase.

## When to Use
- The user says `$map` or `/map`.
- The user asks to map a feature, flow, module, or subsystem.
- The user wants a context document for future implementation or review work.
- The user asks which files, dependencies, and entry points belong to a feature.

## Steps
1. Parse the feature name from the invocation.
2. Determine the project root from the current working directory.
3. Find files related to the feature by searching file names, directories, and content keywords.
4. For each relevant file, identify what it does, what it imports, and what it exposes.
5. Trace the internal and external dependency chain for the feature.
6. Map the feature's data flow: where data enters, how it moves through the implementation, and where it exits.
7. Identify shared state, events, side effects, stores, or background work touched by the feature.
8. If `graphify-out/graph.json` exists, use graphify output to surface connections the raw file scan might miss.
9. Note anything incomplete, ambiguous, or surprising.
10. Write the final document to `.claude/context/<feature>.md`, creating `.claude/context/` if needed, using this structure:
    - `# <Feature> Context Map`
    - `## Entry Points`
    - `## Key Files`
    - `## Dependencies`
    - `## Data Flow`
    - `## State & Events`
    - `## Open Questions`
11. Confirm the output path to the user after writing.

## Usage
```text
$map dashboard
$map extract
$map auth
```

## Key Behaviours
- Overwrite an existing map for the same feature; this skill refreshes context rather than merging reports.
- If delegation is available and explicitly permitted, exploration can be offloaded, but the final artifact still must be written to `.claude/context/<feature>.md`.
- If no graph output exists yet, rely on file and text search alone.
