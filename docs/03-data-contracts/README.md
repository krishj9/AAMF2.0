# Data Contracts

This folder defines the schema-first contract surface for the personal portfolio multi-agent platform.

## Contract principles
- Every API, node, persistence, seed, and eval payload uses an explicit `schema_version`.
- External-facing contracts stay provider-agnostic even when the implementation uses Bedrock, AgentCore, DynamoDB, or CloudWatch.
- All recommendation-bearing outputs carry evidence, provenance, confidence, and workflow-state metadata.
- Hidden reasoning and raw chain-of-thought are never valid contract fields.
- Synthetic personal-project data must be clearly labeled and separated from any real financial data.

## Contract groups
- `shared` - metadata, identity, evidence, errors, status, and versioning primitives.
- `domain` - portfolio, account, instrument, allocation, objective, risk, and policy reference objects.
- `workflow` - orchestration request/response, node outputs, recommendation package, and approval artifacts.
- `memory` - memory records, memory candidates, conflicts, consolidation tasks, and lifecycle events.
- `persistence` - DynamoDB item shapes for approvals, audits, sessions, and memory queues.
- `seeding` - seed manifest, seed batch, dataset snapshot, and fixture records.
- `evals` - golden scenarios, eval cases, eval runs, and quality results.

## Files
- `data-contract-catalog.md` - detailed list of contracts, required fields, producers, consumers, and first-build priority.
- `seed-manifest.example.json` - example seed manifest referenced by the data seeding strategy.
