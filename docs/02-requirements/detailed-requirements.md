# Detailed Requirements: LangGraph Multi-Agent Portfolio Platform

## Introduction
This document restores the detailed requirements style from the original spec while aligning the architecture to:
- LangGraph orchestration running on AWS Lambda
- Angular frontend
- Bedrock and AgentCore services for guardrails, memory, evals, and observability

---

## Requirement 1: Orchestration Entrypoint and Workflow Control
**User Story:** As a personal investor, I want a single orchestration entrypoint that coordinates specialist agents, so that recommendations are consistent and traceable.

### Acceptance Criteria
1. The Angular frontend SHALL invoke only the orchestration API path.
2. The orchestration API SHALL invoke LangGraph on AWS Lambda as the workflow engine.
3. Direct calls from frontend to specialist agent endpoints SHALL be rejected with `INVALID_ENTRYPOINT`.
4. Orchestrator responses SHALL include `request_id`, `session_id`, `trace_id`, `schema_version`, `policy_version`, and `environment`.
5. The orchestrator SHALL run only required nodes for each request path.
6. Node-specific business logic SHALL remain in specialist nodes and not be duplicated in API handlers.
7. Blocking node failures SHALL produce a blocked response and SHALL NOT return approval-ready output.
8. All workflow responses SHALL conform to a versioned `OrchestrationResponse` schema.

---

## Requirement 2: Request Intake and Validation
**User Story:** As a solo operator, I want strict request validation before orchestration starts, so that invalid or contradictory requests do not enter the workflow.

### Acceptance Criteria
1. The system SHALL validate all `PortfolioRebalanceRequest` payloads against schema.
2. Required fields SHALL include client/account context, current holdings/allocation, objectives, risk profile, and constraints.
3. Allocation math SHALL be validated against configured tolerances.
4. Contradictory constraints SHALL return `INVALID_CONSTRAINTS`.
5. Unsupported schema versions SHALL return `UNSUPPORTED_SCHEMA_VERSION`.
6. Valid requests SHALL be assigned `request_id`, linked to `session_id`, and traced with `trace_id`.
7. Request metadata SHALL be logged to audit storage before node execution begins.
8. Validation failures SHALL use `StructuredError` and SHALL NOT leak raw internal exceptions.

---

## Requirement 3: Research Node (Market Data and Context)
**User Story:** As a personal investor, I want current market context and evidence-backed summaries, so that recommendations reflect present conditions.

### Acceptance Criteria
1. The research node SHALL retrieve market data from approved sources.
2. The node SHALL generate market context summaries through Bedrock models.
3. Outputs SHALL include freshness metadata for each material data source.
4. Each material analytic output SHALL include confidence and evidence references.
5. The node SHALL distinguish retrieved facts from model-derived interpretation.
6. Missing non-critical inputs SHALL produce degraded flags with reason metadata.
7. Unsupported claims or ungrounded outputs SHALL be blocked or flagged by policy.
8. The node SHALL return schema-valid `ResearchResponse`.

---

## Requirement 4: Memory and Personalization Node
**User Story:** As a personal investor, I want recommendations to account for long-term client context, so that outputs are personalized and consistent with prior decisions.

### Acceptance Criteria
1. The memory node SHALL retrieve relevant long-term memory through AgentCore memory interfaces.
2. Retrieval SHALL support semantic relevance and category-aware filtering.
3. Returned memory items SHALL include recency, confidence, category, and memory version metadata.
4. Conflicts between retrieved memory and current request SHALL be explicitly flagged.
5. The node SHALL NOT expose raw memory backend payloads.
6. Memory retrieval outages SHALL produce degraded or blocked outcomes per policy.
7. All memory reads SHALL be audit-logged with request and trace correlation.
8. The node SHALL return schema-valid `MemoryPersonalizationResponse`.

---

## Requirement 5: Memory Lifecycle, Consolidation, and Correction
**User Story:** As a project maintainer, I want a controlled memory lifecycle, so that long-term personalization remains accurate and correctable.

### Acceptance Criteria
1. The platform SHALL support memory candidate extraction from completed workflows.
2. Consolidation SHALL distinguish new candidates from established records.
3. Low-confidence or policy-disallowed candidates SHALL NOT become authoritative memory.
4. Consolidation outcomes SHALL include accepted, merged, rejected, and failed statuses.
5. Authorized users SHALL be able to correct or invalidate memory records.
6. Memory writes, updates, invalidations, and deletions SHALL be audit-logged.
7. Memory processing metrics SHALL be emitted for extraction and consolidation success/failure.
8. Memory lifecycle operations SHALL preserve provenance metadata.

---

## Requirement 6: Risk and Compliance Node
**User Story:** As a safety reviewer, I want deterministic risk and mandate evaluation before proposals are generated, so that recommendations satisfy policy controls.

### Acceptance Criteria
1. The node SHALL compute drift between current and target allocations.
2. The node SHALL compute configured risk indicators (for example concentration and exposure).
3. Mandates and suitability constraints SHALL be evaluated deterministically.
4. A `ComplianceVerdict` SHALL be returned as `COMPLIANT`, `NON_COMPLIANT`, or `UNRESOLVED`.
5. Critical rule violations SHALL force `NON_COMPLIANT`.
6. Missing critical inputs SHALL force `UNRESOLVED`.
7. Deterministic outcomes SHALL be separated from model-assisted narrative.
8. The node SHALL return schema-valid `RiskComplianceResponse` with evidence and confidence.

---

## Requirement 7: Execution Proposal Node
**User Story:** As a personal investor, I want structured trade proposals generated only when policy gates are satisfied, so that I can review actionable recommendations safely.

### Acceptance Criteria
1. The node SHALL generate structured trade proposals from upstream outputs.
2. The node SHALL NOT return approval-ready proposals if verdict is `NON_COMPLIANT` or `UNRESOLVED`.
3. Proposals SHALL include estimated impact on allocations.
4. Proposals SHALL include estimated cost and available tax considerations.
5. Output SHALL include evidence, provenance, and confidence metadata.
6. Insufficient data SHALL return degraded or structured error outcomes per policy.
7. The node SHALL never execute trades.
8. The node SHALL return schema-valid `ExecutionResponse`.

---

## Requirement 8: Human Approval Workflow
**User Story:** As a personal investor, I want explicit approve/reject/revise controls, so that I remain accountable for recommendation progression.

### Acceptance Criteria
1. A recommendation result SHALL produce an `ApprovalArtifact` for review.
2. The artifact SHALL include correlation metadata and version metadata.
3. The workflow SHALL support `APPROVE`, `REJECT`, and `REQUEST_REVISION`.
4. Rejection SHALL require a `rejection_note`.
5. Overrides (if policy allows) SHALL require an `override_note`.
6. Approval SHALL be disabled for blocked workflow states.
7. Material recommendation changes SHALL invalidate stale approval artifacts.
8. Approval actions SHALL be audit-logged with user identity and role.

---

## Requirement 9: No Autonomous Execution Without Approval
**User Story:** As a policy stakeholder, I want assurance that personal execution cannot occur without explicit authorized approval.

### Acceptance Criteria
1. Downstream execution handoff SHALL require a valid approved artifact.
2. Missing approval SHALL return `APPROVAL_REQUIRED`.
3. Execution handoff payload SHALL match the approved artifact content.
4. Mismatched payloads SHALL be rejected and audited.
5. No hidden bypass path SHALL allow approval control circumvention.
6. Production approval SHALL require signed-in owner identity.
7. Advisory-only mode SHALL be supported where execution handoff is disabled.
8. All execution attempts and outcomes SHALL be audit-logged.

---

## Requirement 10: Guardrails and Responsible AI Controls
**User Story:** As a safety reviewer, I want policy and safety controls enforced on recommendation-bearing paths, so that harmful or ungrounded outputs are contained.

### Acceptance Criteria
1. Bedrock guardrails SHALL be applied to applicable recommendation-bearing input/output paths.
2. Denied topics and policy-restricted guidance SHALL be blocked.
3. Harmful content and sensitive-information filters SHALL be configured where applicable.
4. Grounding checks SHALL be applied for evidence-dependent outputs.
5. Guardrail violations SHALL return `GUARDRAIL_VIOLATION` when hard-blocked.
6. Guardrail outcomes SHALL include policy version and trace correlation metadata.
7. Non-overridable violation classes SHALL be defined by safety and controls policy.
8. Guardrail events SHALL be audit-logged.

---

## Requirement 11: Observability and Audit Correlation
**User Story:** As a solo operator, I want request-level traces and complete audit trails, so that I can monitor, debug, and operate the platform.

### Acceptance Criteria
1. Every rebalance request SHALL create a correlated trace.
2. LangGraph node execution SHALL emit per-node telemetry.
3. Traces SHALL correlate with audit events through shared identifiers.
4. CloudWatch SHALL capture logs, metrics, and alarms for personal monitoring.
5. Core metrics SHALL include latency, errors, blocked/degraded rates, and memory lifecycle health.
6. Audit logs SHALL capture requests, node outcomes, approvals, memory operations, and policy events.
7. Observability and audit outputs SHALL avoid raw chain-of-thought.
8. Access to restricted audit data SHALL be role-controlled.

---

## Requirement 12: Angular Frontend Workflow
**User Story:** As a personal investor, I want an Angular UI that supports complete intake-to-approval workflows, so that I can operate efficiently and safely.

### Acceptance Criteria
1. The Angular frontend SHALL submit requests only to the orchestrator API.
2. The frontend SHALL display stage-by-stage workflow status.
3. The frontend SHALL display current, target, and proposed allocations distinctly.
4. The frontend SHALL display rationale, evidence summaries, memory summaries, and policy verdicts.
5. The frontend SHALL display trace and policy metadata for safety and controls context.
6. The frontend SHALL provide approve/reject/revision controls with policy-based enablement.
7. The frontend SHALL disable approval actions for blocked states.
8. The frontend SHALL not expose internal-only reasoning artifacts.

---

## Requirement 13: Data Seeding and External Data Strategy
**User Story:** As a project maintainer, I want deterministic seeding plus controlled external data onboarding, so that environments are reproducible and personal decisions are trustworthy.

### Acceptance Criteria
1. The platform SHALL support synthetic seed data for non-personal environments.
2. Seed batches SHALL be validated against the seed manifest contract before import.
3. Seed imports SHALL be idempotent and environment-scoped.
4. Policy-critical reference domains SHALL transition to trusted real sources before personal release.
5. Synthetic and real data namespaces SHALL remain separated.
6. Seed and refresh operations SHALL be audit-logged.
7. Seed datasets SHALL include provenance and version metadata.
8. Rollback to prior approved dataset snapshots SHALL be supported.

---

## Requirement 14: Schema Versioning and Compatibility
**User Story:** As a project maintainer, I want controlled schema evolution, so that services and UIs can evolve safely without breaking workflows.

### Acceptance Criteria
1. All machine-consumable contracts SHALL include explicit schema version fields.
2. Inputs and outputs SHALL be validated against expected versions.
3. Non-breaking changes SHALL preserve backward compatibility.
4. Breaking changes SHALL use explicit new versions with migration guidance.
5. Unsupported versions SHALL fail with structured errors.
6. Schema changelog documentation SHALL be maintained.
7. API DTOs SHALL remain provider-agnostic across version upgrades.
8. Release gates SHALL include contract test validation for active versions.
