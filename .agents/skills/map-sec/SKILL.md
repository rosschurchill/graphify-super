---
name: map-sec
description: >
  Use when the user asks for a security map, attack-surface review, exploit-path
  analysis, or invokes `/map-sec` or `$map-sec` with a feature name — traces
  untrusted inputs, trust boundaries, vulnerability chains, and sensitive data
  flows, then writes a security context document to
  `.claude/context/security-<feature>.md`.
allowed-tools: [Read, Edit, Write, Bash, Glob, Grep]
argument-hint: "<feature>"
---

## Overview
Use this skill to map the security posture of a feature into a compact document that highlights attack surface, exploit chains, trust boundaries, and prioritized mitigations.

## When to Use
- The user says `$map-sec` or `/map-sec`.
- The user asks for a security audit of a feature or subsystem.
- The user asks about attack surface, exploit chains, trust boundaries, or sensitive data paths.
- The user wants a written security context file for later work.

## Steps
1. Parse the feature name from the invocation.
2. Determine the project root from the current working directory.
3. Find all files related to the feature by name, path, and content keyword search.
4. Identify every entry point where untrusted input can reach the feature.
5. Trace those inputs through validation, transformation, storage, and output paths.
6. Look for injection vectors, missing validation, unsafe deserialization, authorization gaps, insecure defaults, sensitive data exposure, and other common OWASP-style issues.
7. Assess how smaller issues combine into higher-severity exploit chains.
8. Identify trust boundaries, privilege transitions, and external system crossings.
9. Note compliance concerns that are visible in code, including PII handling, audit logging gaps, or data retention issues.
10. Write the result to `.claude/context/security-<feature>.md`, creating `.claude/context/` if needed, using this structure:
    - `# <Feature> Security Map`
    - `## Attack Surface`
    - `## Vulnerabilities`
    - `## Exploit Chains`
    - `## Trust Boundaries`
    - `## Sensitive Data Flows`
    - `## Compliance Gaps`
    - `## Recommended Fixes`
    - `## Open Questions`
11. Confirm the output path to the user after writing.

## Usage
```text
$map-sec auth
$map-sec install
$map-sec billing
```

## Key Behaviours
- Overwrite any existing security map for the same feature; treat the skill as a refresh.
- If delegation is available and explicitly permitted, the analysis can be delegated, but the final artifact must still be written locally.
- Pairing this with `$map <feature>` is useful when both structural and security context are needed.
