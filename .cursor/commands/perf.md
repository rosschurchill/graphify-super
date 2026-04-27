# Perf — Performance Audit

Performance audit of a named feature or module. Finds bottlenecks, algorithmic issues, and resource leaks. Saves output to `.claude/context/perf-<feature>.md`.

## Argument handling

Parse the feature name from the invocation. Examples:
- `/perf extract` → feature = `extract`
- `/perf build` → feature = `build`
- `/perf export` → feature = `export`

The argument is required. If missing, ask the user which feature to audit.

## Steps

1. **Parse the feature name** from the arguments.

2. **Find the relevant files** — search by name and content keyword.

3. **Audit performance** of the feature area:
   - Algorithmic complexity — any O(n²) or worse loops over large data sets?
   - Memory usage — are large structures held longer than needed?
   - I/O patterns — are files read multiple times, or read all at once when streaming would suffice?
   - LLM API efficiency — are calls batched? Is caching used where possible?
   - Startup cost — any expensive imports or initialisation on cold start?
   - Concrete bottlenecks — where would time be spent on a 10k-file repo?

   Context: graphify-super processes codebases of varying sizes (small hobby projects to large monorepos). Key concerns are startup time, memory usage on large repos, and LLM API call efficiency.

4. **Write the output** to `.claude/context/perf-<feature>.md` (create `.claude/context/` if it doesn't exist). Use this format:

   ```markdown
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

5. **Confirm** to the user: `Performance audit written to .claude/context/perf-<feature>.md`

## Key Behaviours

- Overwrite any existing perf audit for the same feature.
- Pair with `/map <feature>` first to get the structural picture before auditing.
- Focus on concrete bottlenecks with file:line references, not hypothetical issues.
