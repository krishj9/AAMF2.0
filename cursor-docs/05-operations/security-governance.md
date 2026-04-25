# Security and Safety Controls

## Lightweight role model (personal project)
Minimum roles:
- Owner
- Tester
- Viewer

## Authorization controls
- Approvals and overrides require the `Owner` role.
- Memory correction/invalidation requires explicit permission.
- Deployment changes require owner confirmation.

## Data protection
- Minimize PII in prompts, responses, logs, and dashboards.
- Apply sensitive-data controls via guardrails and service-side policies.
- Separate user-facing identifiers from internal storage identifiers where possible.

## Audit policy
- Record all request, analysis, approval, policy, memory, and release events.
- Enforce immutable-style append semantics for critical policy records.
- Maintain retention and export paths for safety and controls investigations.
