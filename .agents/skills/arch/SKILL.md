---
name: arch
description: >
  Use when the user asks for an architecture review, coupling analysis,
  refactoring guidance, or invokes `/arch` or `$arch` with a feature name —
  inspects the relevant files, judges complexity and abstraction quality, and
  writes an architecture review to `.claude/context/arch-<feature>.md`.
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]
argument-hint: "<feature>"
---

## Overview
Use this skill to review the architecture of a feature or module, focusing on complexity, coupling, cohesion, abstraction quality, and the most valuable refactoring moves.

## When to Use
- The user says `$arch` or `/arch`.
- The user asks whether an area is over-engineered or under-engineered.
- The user asks for coupling, cohesion, or abstraction review.
- The user wants a written architecture review for a named feature.

## Steps
1. Parse the feature name from the invocation.
2. Identify relevant files by searching file names and content keywords tied to the feature.
3. Read enough of those files to understand the public entry points, key dependencies, and implementation shape.
4. Assess:
   - Whether the area is appropriately complex for what it does
   - Coupling and cohesion quality
   - Whether abstractions are helping or obscuring the code
   - What would surprise or confuse a new contributor
   - The top refactoring moves that would improve maintainability
5. Write the result to `.claude/context/arch-<feature>.md`, creating `.claude/context/` if needed, using this structure:
   - `# <Feature> Architecture Review`
   - `## Complexity Assessment`
   - `## Coupling & Cohesion`
   - `## Abstraction Quality`
   - `## Surprise Points`
   - `## Top Refactoring Moves`
   - `## Verdict`
6. Confirm the output path to the user after writing.

## Usage
```text
$arch extract
$arch hooks
$arch cli
```

## Key Behaviours
- Overwrite an existing review for the same feature; the output is a refresh.
- If a structural map does not already exist, it can still be produced from direct file inspection.
- If delegation is available and explicitly permitted, exploration can be offloaded, but the required artifact is still `.claude/context/arch-<feature>.md`.
