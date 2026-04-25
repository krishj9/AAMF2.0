# Comprehensive Implementation Guide

This guide turns the product, architecture, requirements, and data contracts into a practical build sequence for a personal project. The goal is to get a useful end-to-end system working early, then deepen reliability, policy controls, memory, and deployment.

## Build strategy
- Build contract-first: schemas and Pydantic models come before services and UI.
- Keep the first version advisory-only: no brokerage or trade execution integration.
- Use synthetic data until the workflow, tests, and evidence model are stable.
- Treat deterministic policy checks as code, not LLM judgment.
- Add managed Bedrock/AgentCore pieces behind adapters so local tests can run without live AWS calls.

## Phase 0: Project baseline

### Objective
Create a runnable local foundation with clear package boundaries, developer commands, and configuration.

### Deliverables
- Monorepo or coordinated app structure for backend, frontend, infrastructure, docs, and seed data.
- Local environment files for development settings.
- Python backend skeleton with FastAPI, Pydantic, pytest, and lint/format tooling.
- Angular frontend skeleton with routing and a basic shell layout.
- Shared naming conventions for schema versions, policy versions, request IDs, and trace IDs.

### Acceptance criteria
- Backend health endpoint runs locally.
- Frontend loads locally and can call a mock health/status endpoint.
- Tests can be run from a single documented command.
- No real financial credentials or personal PII are required for local development.

## Phase 1: Contracts and validation

### Objective
Define the stable contract surface before implementing orchestration logic.

### Deliverables
- Pydantic models for Phase 1 contracts from `03-data-contracts/data-contract-catalog.md`.
- JSON Schema exports for API and fixture validation.
- Source-controlled schema artifacts for every implemented contract.
- A schema generation/check command that keeps Pydantic models and JSON Schema files synchronized.
- Validation for required fields, allocation totals, schema versions, and unsupported versions.
- Shared `StructuredError` response mapper.
- Contract tests for serialization, validation errors, and schema compatibility.

### Key contracts
- `CorrelationMetadata`
- `VersionMetadata`
- `ActorContext`
- `StructuredError`
- `WorkflowState`
- `PortfolioRebalanceRequest`
- `GraphState`
- `OrchestrationResponse`
- `SeedManifest`

### Acceptance criteria
- Invalid requests fail before orchestration starts.
- All responses include correlation and version metadata.
- JSON Schema files are committed, versioned, and regenerated deterministically.
- CI or local checks fail when model definitions and schema artifacts drift.
- Contract tests pass without live AWS dependencies.
- Example seed manifest validates successfully.

## Phase 2: Synthetic data and domain engine

### Objective
Make the system useful with deterministic seed data and local calculations before adding LLM behavior.

### Deliverables
- Synthetic seed files for client profiles, accounts, instruments, holdings, allocation targets, and policy rules.
- Idempotent seed loader for local/dev data.
- Portfolio math utilities for market value, allocation, drift, and tolerance-band checks.
- Deterministic policy rule evaluator.
- Golden scenario fixtures for normal, degraded, low-confidence, and blocked outcomes.

### Key contracts
- `ClientProfile`
- `AccountProfile`
- `InstrumentReference`
- `PortfolioHolding`
- `PortfolioSnapshot`
- `AllocationTarget`
- `RiskProfile`
- `PolicyRule`
- `GoldenScenario`

### Acceptance criteria
- A seeded portfolio can be loaded and validated locally.
- Drift and policy verdicts are deterministic and test-covered.
- Golden scenarios can be executed without Bedrock.
- Synthetic records are clearly labeled.

## Phase 3: LangGraph orchestration

### Objective
Implement the workflow skeleton and state transitions with stubbed node adapters.

### Deliverables
- Lambda-compatible orchestration handler.
- LangGraph state machine with nodes from `01-architecture/langgraph-orchestration.md`.
- Explicit agent classes for supervisor, memory, research, sentiment analysis, portfolio rebalancing, risk/compliance, trade execution proposal, and human approval workflow.
- Stubbed research, sentiment, memory, risk/policy, execution proposal, guardrail, and persistence adapters.
- Conditional routing for validation failures, blocked states, degraded states, and guardrail violations.
- Idempotency handling based on request/session tuple.

### Key contracts
- `GraphState`
- `ResearchResponse`
- `MemoryPersonalizationResponse`
- `RiskPolicyResponse`
- `ExecutionProposalResponse`
- `GuardrailResult`
- `RecommendationPackage`

### Acceptance criteria
- A valid request traverses the full graph and returns a recommendation package.
- The response includes agent-stage outputs suitable for UI progress and audit review.
- A blocked policy result skips proposal generation.
- Every node emits a structured outcome with correlation metadata.
- Unit tests cover normal, degraded, and blocked graph paths.

## Phase 4: Persistence, audit, and approvals

### Objective
Persist the review package and make manual approval explicit.

### Deliverables
- DynamoDB table definitions or local DynamoDB equivalents for approval artifacts, audit events, sessions, and memory queue tasks.
- DynamoDB Local support for local development using endpoint `http://localhost:55000`.
- AWS DynamoDB support using the same repository code with hosted endpoints selected by environment config.
- Repository/adaptor layer for persistence operations.
- Append-only audit event writer.
- Approval artifact creation and status transitions.
- Approval, rejection, and revision endpoints.
- Recommendation hash or version check to invalidate stale approval artifacts.

### Key contracts
- `ApprovalArtifact`
- `AuditEvent`
- `SessionState`
- `ApprovalArtifactItem`
- `AuditEventItem`
- `MemoryConsolidationTask`

### Acceptance criteria
- Recommendation output creates a persisted approval artifact.
- Approval is disabled for `BLOCKED` workflows.
- Rejection requires a note.
- Audit events are written for request intake, node outcomes, recommendation assembly, and approval actions.
- Conditional writes prevent double approval or stale updates.

## Phase 5: Bedrock, guardrails, and research integration

### Objective
Replace stubs with controlled model and market-data integrations.

### Deliverables
- Bedrock model invocation adapter.
- Prompt templates for research summaries, rationale summaries, and user-facing explanations.
- Public/delayed market-data adapter for prices and basic market context.
- Bedrock guardrail wrapper for recommendation-bearing inputs and outputs.
- Evidence and provenance generation for retrieved and model-assisted content.
- Fallback behavior for missing, stale, or unavailable market data.

### Key contracts
- `MarketDataSnapshot`
- `EvidenceReference`
- `ProvenanceMetadata`
- `ConfidenceMetadata`
- `GuardrailResult`

### Acceptance criteria
- Model outputs are schema-validated before entering graph state.
- Unsupported or ungrounded claims are blocked or flagged.
- The UI receives summaries, not hidden reasoning.
- Research outages produce `DEGRADED` or `BLOCKED` outcomes according to policy.

## Phase 6: Memory and personalization

### Objective
Add long-term context while keeping memory correction and provenance visible.

### Deliverables
- AgentCore Memory adapter behind a local-testable interface.
- Memory retrieval by semantic relevance and category.
- Memory conflict detection against current request context.
- Memory candidate extraction after completed workflows.
- Memory consolidation queue processing.
- Owner-only memory correction and invalidation path.

### Key contracts
- `MemoryRecord`
- `MemoryCandidate`
- `MemoryConflict`
- `MemoryConsolidationTask`
- `MemoryPersonalizationResponse`

### Acceptance criteria
- Retrieved memory appears as a structured summary with recency and confidence.
- Conflicting memory lowers confidence or blocks where configured.
- Memory writes preserve source request and approval artifact provenance.
- Memory correction actions are audited.

## Phase 7: Angular workflow UI

### Objective
Build a complete intake-to-review experience for the personal project.

### Deliverables
- Request intake form for account, holdings, target allocation, objectives, risk profile, and constraints.
- Workflow status view for graph stages.
- Allocation comparison view for current, target, and proposed allocations.
- Recommendation review page with rationale, evidence, policy verdict, confidence, and memory summary.
- Approval controls for approve, reject, and request revision.
- Metadata panel for request ID, trace ID, schema version, policy version, and workflow state.

### Acceptance criteria
- The frontend only calls the orchestrator API.
- Blocked workflows visibly disable approval.
- Recommendation evidence is easy to inspect.
- Errors and degraded states are displayed with actionable messages.

## Phase 8: Observability and evals

### Objective
Make quality, regressions, and runtime behavior visible enough for ongoing iteration.

### Deliverables
- Trace provider adapter for AgentCore Observability or LangSmith.
- CloudWatch-compatible metrics/logging adapter.
- Contract eval suite.
- Golden scenario eval suite.
- Safety/adversarial tests for policy bypass, hallucinated facts, and unsupported claims.
- Operational tests for timeouts, retries, and degraded mode.
- Eval result storage for local comparison over time.

### Key contracts
- `EvalRun`
- `GoldenScenario`
- `StructuredError`
- `AuditEvent`

### Acceptance criteria
- Contract tests pass before implementation changes are considered complete.
- Golden scenarios verify expected workflow state and policy verdicts.
- Safety tests catch known bypass attempts.
- Traces and audit events can be correlated by request ID and trace ID.

## Phase 9: Personal AWS deployment

### Objective
Deploy the advisory system with enough isolation and cost control for a home project.

### Deliverables
- AWS Lambda package for the orchestrator.
- API Gateway or authenticated service API.
- DynamoDB tables with TTL and on-demand billing.
- IAM roles scoped to the app’s required Bedrock, DynamoDB, CloudWatch, and AgentCore operations.
- Angular deployment target.
- Environment configuration for `dev`, `test`, `staging`, and `main`.
- Terraform modules and environment variable files for repeatable AWS deployment.
- Cost guardrails, logging retention, and rollback notes.

### Acceptance criteria
- `dev` deployment can run a seeded synthetic scenario.
- `main` remains advisory-only and does not execute trades.
- IAM access is least-privilege for the personal app.
- Terraform plan is reviewed before apply for each environment.
- Rollback and redeploy steps are documented.
- CloudWatch logs and metrics are available for failed requests.

## Suggested milestone order
1. Local contract tests and synthetic request validation.
2. Deterministic drift and policy verdicts.
3. Stubbed LangGraph end-to-end response.
4. Persisted approval artifact and audit trail.
5. Angular intake and recommendation review.
6. Bedrock-backed research and summaries.
7. Guardrails and eval gates.
8. Memory retrieval and consolidation.
9. AWS deployment with cost controls.

## Done definition for MVP
- A synthetic portfolio rebalance request can be submitted from the Angular UI.
- LangGraph runs research, memory, risk/policy, proposal, guardrail, and assembly stages.
- The system returns a recommendation package with evidence, confidence, provenance, and workflow state.
- Manual approval/rejection is persisted and audited.
- No autonomous trading path exists.
- Contract, golden scenario, and basic safety evals pass.
