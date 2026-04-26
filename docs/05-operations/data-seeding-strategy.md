# Data Seeding Strategy

## Goal
Define how the platform is bootstrapped with reliable data before and during runtime, using a staged approach from synthetic datasets to governed external sources.

## Position
The system should not rely entirely on online, request-time data.  
It should use a hybrid model:
- Pre-seeded baseline data for consistency, policy, and latency
- Live data for freshness-sensitive signals

## What can be synthetic first
- Client profiles and household structures
- Account holdings and allocation histories
- Investment objectives, risk tolerances, and mandate constraints
- Approval/rejection/revision workflows
- Audit event histories and operator activity
- Memory candidates and personalization histories
- Golden test scenarios for blocked/degraded/low-confidence outcomes

## What should become real before production
- Instrument/security master reference (identifiers, classifications, lot rules)
- Trading calendars and market session metadata
- Corporate actions and split/dividend adjustments
- Compliance policy source data and controlled rule catalogs
- Production-grade benchmark/reference datasets used in decisioning

## Live data at runtime
- Latest prices and intraday market snapshots
- Breaking news and sentiment refreshes
- On-demand model inference responses from Bedrock

## Seeding phases

### Phase 1: Build with synthetic-only
- Generate complete synthetic datasets for all core entities.
- Validate end-to-end orchestration, approvals, memory lifecycle, and audit coverage.
- Use deterministic generators so test runs are reproducible.

### Phase 2: Hybrid hardening
- Keep synthetic client/workflow data.
- Introduce delayed/public real market and reference feeds.
- Benchmark quality, latency, and failure handling with mixed datasets.

### Phase 3: Production-readiness
- Replace policy-critical/reference domains with governed real sources.
- Retain synthetic datasets only for testing, simulation, and chaos exercises.
- Enforce versioned data snapshots for repeatable evals and audits.

## Recommended seed domains (minimum)
- `client_master`
- `account_master`
- `portfolio_positions_history`
- `mandate_constraints_catalog`
- `risk_policy_catalog`
- `instrument_reference`
- `approval_artifact_samples`
- `audit_event_samples`
- `memory_seed_records`

## Quality gates for seeded data
- Schema-valid records at ingest time
- Referential integrity across client/account/instrument identifiers
- Coverage thresholds for all major scenario classes
- No sensitive real PII in synthetic environments
- Version tag and provenance metadata on every seeded batch

## Operational pattern
- Store seed artifacts as versioned files in a controlled data folder or bucket.
- Run idempotent seeding jobs per environment.
- Log all seed and refresh runs as traceable events.
- Support rollback to a known-good dataset version.
- Validate every batch against `03-data-contracts/seed-manifest.example.json` before import.

## Guardrails for synthetic data
- Clearly label synthetic records and prevent cross-contamination into personal datasets.
- Do not train memory corrections in personal from synthetic user identities.
- Keep synthetic and real data namespaces separated in memory and persistence layers.

## Success criteria
- New environments can be provisioned with complete baseline data in one automated run.
- Core workflows pass contract, scenario, and policy tests using seeded datasets.
- Hybrid mode demonstrates stable behavior under missing or stale live inputs.
