# Build Tasks (Cursor-Friendly Backlog)

## Phase 1: Contracts and scaffolding
- [ ] Define JSON schema files and model classes for all core contracts.
- [ ] Implement schema version validator and migration policy doc.
- [ ] Implement structured error library and response mapper.

## Phase 2: Lambda + LangGraph
- [ ] Create orchestration Lambda package and handler entrypoint.
- [ ] Implement graph state model and typed node I/O.
- [ ] Implement conditional edges for blocked/degraded routing.
- [ ] Add retry policies and timeout budgets.

## Phase 3: Node integrations
- [ ] Implement research node adapters (data retrieval + synthesis).
- [ ] Implement memory node adapters (AgentCore retrieval/write intents).
- [ ] Implement risk/policy deterministic rules and verdict builder.
- [ ] Implement execution proposal node with hard policy guard.

## Phase 4: Governance controls
- [ ] Add guardrail wrapper and violation response handling.
- [ ] Add audit event emitter for every critical action.
- [ ] Add approval artifact persistence and transition checks.

## Phase 5: Observability and evals
- [ ] Instrument graph/node traces and metrics.
- [ ] Build contract + golden scenario eval suites.
- [ ] Build safety/adversarial and policy eval suites.
- [ ] Define release gate thresholds and enforcement checks.

## Phase 6: Deployment
- [ ] Create infra templates/scripts for Lambda, DynamoDB, IAM, and alarms.
- [ ] Create Angular frontend deployment pipeline and environment configuration strategy.
- [ ] Define environment promotion flow and rollback playbook.
- [ ] Validate personal readiness checklist.
