# Map-Sec — Feature Security Audit

Maps the security posture of a named feature — tracing exploit chains, trust boundaries, and vulnerability clusters — and writes a compact security context document.

## Argument handling

Parse the feature name from the invocation. Examples:
- `/map-sec install` → feature = `install`
- `/map-sec extract` → feature = `extract`
- `/map-sec hooks` → feature = `hooks`

The argument is required. If missing, ask the user which feature to audit.

## Steps

1. **Parse the feature name** from the invocation arguments.

2. **Find all files related to the feature** — search by name, directory, and content keywords.

3. **Think like an attacker.** Assess:
   - All entry points where untrusted input enters this feature (attack surface)
   - Data flows from those entry points — look for injection vectors, missing validation, unsafe deserialization, trust boundary violations
   - Vulnerability chains: how do small issues (e.g. missing auth check + info leak) combine into critical exploits?
   - Hardcoded secrets, insecure defaults, overly permissive configs, sensitive data exposure, OWASP Top 10 patterns
   - Authentication and authorisation: who can reach what, and can that be bypassed?
   - Anything that looks commented-out, incomplete, or like a known dangerous pattern
   - Compliance concerns (GDPR data handling, PII exposure, audit logging gaps) if visible

4. **Write the output** to `.claude/context/security-<feature>.md` (create `.claude/context/` if it doesn't exist). Use this format:

   ```markdown
   # <Feature> Security Map
   _Generated: <today's date> | Source: <project_root>_

   ## Attack Surface
   All entry points where untrusted input enters this feature.

   ## Vulnerabilities
   ### Critical
   ### High
   ### Medium / Low

   ## Exploit Chains
   How individual issues combine into higher-severity attack paths.

   ## Trust Boundaries
   Where the feature crosses privilege levels, auth zones, or external systems.

   ## Sensitive Data Flows
   PII, credentials, tokens, or other sensitive data — where they enter, move, and exit.

   ## Compliance Gaps
   GDPR, audit logging, data retention, or other compliance concerns visible in the code.

   ## Recommended Fixes
   Prioritised list of mitigations. Most critical first.

   ## Open Questions
   Things that need developer clarification before a full assessment is possible.
   ```

5. **Confirm** to the user: `Security map written to .claude/context/security-<feature>.md`

## Key Behaviours

- Return condensed findings — no raw file dumps.
- If a security map already exists for this feature, overwrite it (it's a refresh).
- Output files are prefixed `security-` to distinguish them from structural `/map` outputs.
- Pair with `/map <feature>` to get both structural and security context for the same feature.
