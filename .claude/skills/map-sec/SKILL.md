# /map-sec Skill

Maps the security posture of a named feature or area by delegating all analysis to a Sentinel subagent. The Sentinel thinks like an attacker — tracing exploit chains, trust boundaries, and vulnerability clusters — and returns a compact security context document.

## Trigger

`/map-sec <feature>`

## Steps

1. **Parse the feature name** from the invocation arguments (e.g. `/map-sec auth` → feature = `auth`).
2. **Determine the project root** — use the primary working directory of the current session.
3. **Spawn a Sentinel subagent** (`subagent_type: "The Sentinel"`) with the prompt template below, substituting `<feature>` and `<project_root>`.
4. **Take the subagent's returned markdown** as-is.
5. **Write it** to `<project_root>/.claude/context/security-<feature>.md` (create `.claude/context/` if it doesn't exist).
6. **Confirm** to the user: `Security map written to .claude/context/security-<feature>.md`

## Subagent prompt template

Pass this verbatim to a Sentinel subagent (`subagent_type: "The Sentinel"`), substituting the placeholders:

```
You are performing a security audit of the "<feature>" feature in the codebase at <project_root>.

Think like an attacker. Your job is to find how small issues chain into critical exploits, map the attack surface, and surface anything that looks dangerous or incomplete. Return a single compact security context document — no raw file dumps, only condensed findings.

Steps:
1. Find all files related to "<feature>" (search by name, directory, and content keywords).
2. Identify the attack surface: all entry points where untrusted input enters this feature.
3. Trace data flows from those entry points — look for injection vectors, missing validation, unsafe deserialization, and trust boundary violations.
4. Hunt for vulnerability chains: how do small issues (e.g. missing auth check + info leak) combine into critical exploits?
5. Check for: hardcoded secrets, insecure defaults, overly permissive configs, sensitive data exposure, OWASP Top 10 patterns.
6. Assess authentication and authorisation: who can reach what, and can that be bypassed?
7. Flag anything that looks incomplete, commented-out, or like a known dangerous pattern.
8. Note compliance concerns (GDPR data handling, PII exposure, audit logging gaps) if visible.

Return ONLY the completed security map in this exact format:

# <Feature> Security Map
_Generated: <today's date> | Source: <project_root> | Analyst: Sentinel_

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

## Behaviour notes

- The Sentinel subagent burns its own context. The main session only receives the condensed security document.
- If `.claude/context/` does not exist, create it before writing.
- If a security map already exists for this feature, overwrite it (it's a refresh).
- Output files are prefixed `security-` to distinguish them from structural `/map` outputs.
- This skill works on any project.
- Pair with `/map <feature>` to get both structural and security context for the same feature.
