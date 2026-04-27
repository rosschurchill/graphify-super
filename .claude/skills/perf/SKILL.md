# /perf Skill

Performance audit of a named feature or module via The Auditor subagent. Finds bottlenecks, algorithmic issues, and resource leaks. Saves output to `.claude/context/perf-<feature>.md`.

## Trigger

`/perf <feature>`

Examples: `/perf extract`, `/perf build`, `/perf export`

## Steps

1. **Parse the feature name** from the arguments.

2. **Find the relevant files** — search by name and content keyword.

3. **Spawn an Auditor subagent** (`subagent_type: "The Auditor"`) with this prompt (substituting placeholders):

   ```
   You are auditing the performance of the "<feature>" area in the codebase at <project_root>.

   The project is graphify-super — a Python CLI/library. The pipeline processes codebases of varying sizes (small hobby projects to large monorepos). Key concerns: startup time, memory usage on large repos, and LLM API call efficiency.

   Relevant files: <file list>

   Assess:
   1. Algorithmic complexity — any O(n²) or worse loops over large data sets?
   2. Memory usage — are large structures held longer than needed?
   3. I/O patterns — are files read multiple times, or read all at once when streaming would suffice?
   4. LLM API efficiency — are calls batched? Is caching used where possible?
   5. Startup cost — any expensive imports or initialisation on cold start?
   6. Concrete bottlenecks — where would time be spent on a 10k-file repo?

   Return ONLY this format:

   # <Feature> Performance Audit
   _Generated: <today's date> | Source: <project_root>_

   ## Complexity Profile
   Big-O analysis of the main operations in this area.

   ## Memory Hotspots
   Where large allocations happen and whether they can be reduced.

   ## I/O Patterns
   File reads, writes, and whether they are efficient.

   ## LLM Efficiency
   API call count, batching, and caching opportunities (if applicable).

   ## Bottlenecks
   Top 3 places where time is spent on large inputs, with line references.

   ## Recommended Fixes
   Prioritised list. Include estimated impact (high/medium/low) for each.

   ## Verdict
   Is performance a concern at current scale? At 10× scale?
   ```

4. **Write the output** to `<project_root>/.claude/context/perf-<feature>.md`.

5. **Confirm** to the user: `Performance audit written to .claude/context/perf-<feature>.md`

## Behaviour notes

- The Auditor subagent burns its own context. The main session only receives the condensed audit.
- If `.claude/context/` does not exist, create it before writing.
- Overwrite any existing perf audit for the same feature.
- Pair with `/map <feature>` first to get the structural picture before auditing.
