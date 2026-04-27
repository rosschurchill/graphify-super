---
name: perf
description: >
  Use when the user asks for a performance audit, bottleneck analysis, scaling
  review, or invokes `/perf` or `$perf` with a feature name — examines
  complexity, memory use, I/O, startup cost, and API efficiency, then writes a
  performance audit to `.claude/context/perf-<feature>.md`.
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]
argument-hint: "<feature>"
---

## Overview
Use this skill to audit the performance characteristics of a feature or module and capture the main bottlenecks, scaling risks, and high-impact optimizations in a reusable report.

## When to Use
- The user says `$perf` or `/perf`.
- The user asks for a performance review or bottleneck analysis.
- The user asks how an area will behave on larger repositories or workloads.
- The user wants a written performance audit for later implementation work.

## Steps
1. Parse the feature name from the invocation.
2. Identify the relevant files by searching file names and content keywords.
3. Read enough of those files to understand the hot paths and major data structures.
4. Assess:
   - Algorithmic complexity and any likely `O(n^2)` or worse behavior
   - Memory usage and whether large structures are retained too long
   - I/O patterns such as repeated reads or all-at-once loading
   - LLM or API efficiency where relevant, including batching and caching
   - Startup cost from heavy imports or expensive initialization
   - The most likely bottlenecks on large inputs
5. Write the result to `.claude/context/perf-<feature>.md`, creating `.claude/context/` if needed, using this structure:
   - `# <Feature> Performance Audit`
   - `## Complexity Profile`
   - `## Memory Hotspots`
   - `## I/O Patterns`
   - `## LLM Efficiency`
   - `## Bottlenecks`
   - `## Recommended Fixes`
   - `## Verdict`
6. Confirm the output path to the user after writing.

## Usage
```text
$perf extract
$perf build
$perf export
```

## Key Behaviours
- Overwrite any existing perf audit for the same feature; treat this as a refresh.
- If delegation is available and explicitly permitted, analysis can be delegated, but the final audit still must be written locally.
- If an area has no LLM or external API work, state that explicitly instead of forcing that section.
