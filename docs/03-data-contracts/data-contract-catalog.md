# Data Contract Catalog

This catalog is the source of truth for the first personal-project implementation. Contract names use API-friendly PascalCase, while field names use snake_case.

## Contract detail standard
Each implemented contract should have a source-controlled JSON Schema and matching Pydantic model. The catalog below lists the required contract inventory; implementation should expand each item with:
- Field types, required/optional markers, enum values, defaults, and nullable rules.
- Validation rules such as allocation totals, identifier formats, timestamp format, value ranges, and max list sizes.
- Example valid and invalid payloads.
- Compatibility notes for additive, breaking, deprecated, and migrated fields.
- Producer and consumer ownership so changes have a clear blast radius.

## Naming compatibility notes
- `RiskPolicyResponse` is the personal-project name for the enterprise-style `RiskComplianceResponse`. Use one canonical code model and provide an alias only if older fixtures still reference `RiskComplianceResponse`.
- `ExecutionProposalResponse` is the personal-project name for `ExecutionResponse`.
- `PolicyVerdict` is the personal-project name for `ComplianceVerdict`; allowed values remain `COMPLIANT`, `NON_COMPLIANT`, and `UNRESOLVED` unless the codebase intentionally introduces new values.

## Shared primitives

### `CorrelationMetadata`
Purpose: Tie requests, logs, traces, audits, and UI displays together.
Fields: `request_id`, `session_id`, `trace_id`, `idempotency_key`, `created_at`.
Used by: every request, node response, audit event, and persisted workflow item.
Priority: Phase 1.

### `VersionMetadata`
Purpose: Make schemas, policies, prompts, and agent/runtime versions explicit.
Fields: `schema_version`, `policy_version`, `agent_version_set`, `app_version`, `environment`.
Used by: orchestration state, API responses, audit events, eval runs.
Priority: Phase 1.

### `ActorContext`
Purpose: Identify the current local user and role.
Fields: `actor_id`, `display_name`, `role`, `auth_provider`, `is_owner`.
Validation: `role` must be one of `OWNER`, `TESTER`, or `VIEWER`.
Used by: request intake, approval actions, audit events, memory correction.
Priority: Phase 1.

### `EvidenceReference`
Purpose: Link recommendation claims to data, calculations, or source documents.
Fields: `evidence_id`, `source_type`, `source_name`, `source_uri`, `retrieved_at`, `freshness_seconds`, `summary`.
Used by: research, risk/policy, proposal, recommendation package.
Priority: Phase 1.

### `A2AAgentRequest`
Purpose: Envelope a supervisor-to-remote-agent task.
Fields: `task`, `request_id`, `symbols`, `portfolio_request`.
Used by: supervisor backend, remote research agent.
Priority: Phase 5.

### `A2AAgentResponse`
Purpose: Return remote agent output with protocol and payload metadata.
Fields: `agent`, `protocol`, `request_id`, `summary`, `payload`.
Used by: remote research agent, supervisor backend, UI trace display.
Priority: Phase 5.

### `McpJsonRpcRequest`
Purpose: Represent MCP-style JSON-RPC tool list and tool call requests.
Fields: `jsonrpc`, `id`, `method`, `params`.
Used by: sentiment MCP server, supervisor backend, remote research agent.
Priority: Phase 5.

### `AgentStageResult`
Purpose: Report per-agent progress and outcomes for the UI and audit trail.
Fields: `agent_name`, `status`, `summary`, `protocol`, `execution_location`, `evidence`.
Validation: `status` values are `PENDING`, `RUNNING`, `COMPLETED`, `DEGRADED`, `BLOCKED`, `FAILED`.
Used by: orchestrator, frontend workflow timeline, audit events.
Priority: Phase 3.

### `ProvenanceMetadata`
Purpose: Describe how a value was produced.
Fields: `source_stage`, `producer_node`, `model_id`, `input_refs`, `transformation`, `generated_at`.
Used by: all model-assisted and derived outputs.
Priority: Phase 1.

### `ConfidenceMetadata`
Purpose: Make uncertainty visible and machine-readable.
Fields: `score`, `label`, `drivers`, `missing_inputs`, `stale_inputs`.
Used by: node responses, recommendation package, eval results.
Priority: Phase 1.

### `StructuredError`
Purpose: Standardize validation, runtime, guardrail, and policy failures.
Fields: `code`, `message`, `severity`, `retryable`, `source`, `correlation`, `details`.
Used by: API layer, LangGraph nodes, frontend error panels.
Priority: Phase 1.

### `WorkflowState`
Purpose: Normalize final and intermediate workflow status.
Values: `NORMAL`, `DEGRADED`, `LOW_CONFIDENCE`, `BLOCKED`.
Used by: orchestration state, UI controls, approval eligibility.
Priority: Phase 1.

### `PermissionMatrix`
Purpose: Keep personal-project authorization explicit without enterprise RBAC complexity.
Fields: `role`, `can_submit_request`, `can_approve`, `can_override`, `can_correct_memory`, `can_view_audit`, `can_deploy`.
Validation: only `OWNER` can approve, override, correct memory, view restricted audit data, or deploy.
Used by: API authorization, frontend enablement, tests.
Priority: Phase 1.

## Domain contracts

### `ClientProfile`
Purpose: Represent the synthetic or personal investor profile used for recommendations.
Fields: `client_id`, `household_id`, `display_label`, `risk_profile_id`, `tax_profile_id`, `synthetic`.
Producer: seed loader or profile editor.
Consumers: memory node, request builder, audit summaries.
Priority: Phase 1.

### `AccountProfile`
Purpose: Represent an investment account.
Fields: `account_id`, `client_id`, `account_type`, `base_currency`, `custodian_label`, `taxable`.
Producer: seed loader or profile editor.
Consumers: request validator, proposal generator.
Priority: Phase 1.

### `InstrumentReference`
Purpose: Normalize holdings and market-data lookup.
Fields: `instrument_id`, `symbol`, `name`, `asset_class`, `sector`, `currency`, `data_source`.
Producer: seed loader and market reference refresh.
Consumers: research node, allocation engine, risk/policy node.
Priority: Phase 1.

### `PortfolioHolding`
Purpose: Represent one position in an account.
Fields: `instrument_id`, `symbol`, `quantity`, `market_price`, `market_value`, `cost_basis`, `as_of`.
Producer: request intake or seeded portfolio snapshot.
Consumers: request validator, research, risk/policy, execution proposal.
Priority: Phase 1.

### `PortfolioSnapshot`
Purpose: Represent current account state at a point in time.
Fields: `snapshot_id`, `account_id`, `as_of`, `holdings`, `cash`, `total_value`, `allocation`.
Producer: request intake or portfolio importer.
Consumers: orchestration request, drift calculation, UI allocation views.
Priority: Phase 1.

### `PortfolioRecord`
Purpose: Persist each client's portfolio and related decision inputs.
Fields: `client_profile`, `account_profile`, `portfolio_snapshot`, `allocation_target`, `risk_profile`, `updated_at`, `source`, `source_approval_id`.
Producer: seed loader, rebalance request intake, approval workflow.
Consumers: portfolio API, market drift simulation, rebalance intake UI.
Priority: Phase 2.

### `AllocationTarget`
Purpose: Describe desired allocation constraints.
Fields: `target_id`, `account_id`, `asset_class_targets`, `security_targets`, `tolerance_bands`.
Producer: user input or seed data.
Consumers: risk/policy node, execution proposal node.
Priority: Phase 1.

### `RiskProfile`
Purpose: Describe risk preference and suitability constraints.
Fields: `risk_profile_id`, `risk_level`, `max_single_position_pct`, `max_sector_pct`, `allowed_asset_classes`.
Producer: seed data or profile editor.
Consumers: risk/policy node, recommendation package.
Priority: Phase 1.

### `PolicyRule`
Purpose: Encode deterministic personal safety rules.
Fields: `rule_id`, `name`, `description`, `severity`, `condition`, `failure_state`, `enabled`.
Producer: local policy configuration.
Consumers: risk/policy node, eval suite.
Priority: Phase 2.

### `MarketDataSnapshot`
Purpose: Represent retrieved price and market context.
Fields: `instrument_id`, `symbol`, `price`, `currency`, `as_of`, `source`, `freshness_seconds`.
Producer: research node.
Consumers: proposal generator, evidence summary, UI.
Priority: Phase 2.

## Workflow contracts

### `PortfolioRebalanceRequest`
Purpose: Main frontend-to-orchestrator input.
Fields: `correlation`, `version`, `actor`, `client_profile`, `account_profile`, `portfolio_snapshot`, `allocation_target`, `constraints`, `requested_action_context`.
Producer: Angular frontend.
Consumers: API validation and LangGraph state.
Priority: Phase 1.

### `GraphState`
Purpose: Internal LangGraph state passed between nodes.
Fields: `correlation`, `version`, `actor`, `request`, `research`, `memory`, `risk_policy`, `proposal`, `guardrail_result`, `quality`, `errors`.
Producer: orchestration runtime.
Consumers: all graph nodes.
Priority: Phase 1.

### `ResearchResponse`
Purpose: Output from market/context research.
Fields: `correlation`, `market_data`, `market_summary`, `evidence`, `provenance`, `confidence`, `degraded_reasons`.
Producer: research node.
Consumers: risk/policy node, recommendation assembly.
Priority: Phase 2.

### `MemoryPersonalizationResponse`
Purpose: Output from memory retrieval and conflict detection.
Fields: `correlation`, `memory_items`, `conflicts`, `applied_preferences`, `confidence`, `degraded_reasons`.
Producer: memory node.
Consumers: risk/policy node, recommendation assembly, memory queue.
Priority: Phase 2.

### `RiskPolicyResponse`
Purpose: Deterministic risk and personal policy verdict.
Fields: `correlation`, `drift_analysis`, `risk_findings`, `rule_results`, `verdict`, `evidence`, `confidence`.
Producer: risk/policy node.
Consumers: execution proposal node, UI, approval artifact.
Priority: Phase 2.

### `ExecutionProposalResponse`
Purpose: Proposed trades or blocked/degraded proposal result.
Fields: `correlation`, `proposal_status`, `trades`, `estimated_impact`, `estimated_cost`, `tax_notes`, `evidence`, `confidence`.
Producer: execution proposal node.
Consumers: recommendation assembly, approval artifact.
Priority: Phase 3.

### `TradeProposal`
Purpose: One proposed buy/sell/hold action.
Fields: `trade_id`, `instrument_id`, `symbol`, `action`, `quantity`, `estimated_price`, `estimated_value`, `rationale`, `evidence_refs`.
Producer: execution proposal node.
Consumers: frontend, approval artifact.
Priority: Phase 3.

### `GuardrailResult`
Purpose: Structured result of safety and grounding checks.
Fields: `guardrail_id`, `policy_version`, `status`, `violations`, `blocked`, `checked_at`.
Producer: guardrail adapter.
Consumers: orchestration response, audit event, UI.
Priority: Phase 3.

### `RecommendationPackage`
Purpose: Final user-facing recommendation.
Fields: `correlation`, `summary`, `current_allocation`, `target_allocation`, `proposed_allocation`, `risk_policy`, `trades`, `evidence`, `quality`, `approval_eligibility`.
Producer: `assemble_recommendation`.
Consumers: frontend, approval artifact persistence.
Priority: Phase 3.

### `ApprovalArtifact`
Purpose: Immutable-ish review package for manual approval.
Fields: `approval_id`, `correlation`, `recommendation_hash`, `recommendation`, `approval_status`, `approved_by`, `approved_at`, `rejection_note`, `override_note`.
Producer: `create_approval_artifact`.
Consumers: frontend, audit log, persistence layer.
Priority: Phase 3.

### `ApprovalActionRequest`
Purpose: Capture a manual approval, rejection, or revision command.
Fields: `approval_id`, `action`, `actor`, `note`, `override_reason`, `expected_recommendation_hash`, `submitted_at`.
Validation: `action` must be `APPROVE`, `REJECT`, or `REQUEST_REVISION`; `REJECT` and `REQUEST_REVISION` require `note`; override actions require owner role and `override_reason`.
Producer: Angular frontend.
Consumers: approval API, audit event writer.
Priority: Phase 3.

### `ApprovalTransitionResult`
Purpose: Return the result of an approval state transition.
Fields: `approval_id`, `previous_status`, `next_status`, `accepted`, `structured_error`, `audit_event_id`, `updated_at`.
Validation: stale recommendation hashes must fail with `STALE_APPROVAL_ARTIFACT`.
Producer: approval API.
Consumers: Angular frontend, audit log.
Priority: Phase 3.

### `OrchestrationResponse`
Purpose: Main API response to the Angular frontend.
Fields: `correlation`, `version`, `workflow_state`, `recommendation_package`, `approval_artifact`, `structured_error`, `provider_trace_url`.
Producer: orchestrator API.
Consumers: Angular frontend.
Priority: Phase 1.

## Memory contracts

### `MemoryRecord`
Purpose: Long-term personalization item.
Fields: `memory_id`, `client_id`, `category`, `content`, `confidence`, `source_request_id`, `created_at`, `updated_at`, `expires_at`.
Priority: Phase 2.

### `MemoryCandidate`
Purpose: Proposed memory extracted from workflow output.
Fields: `candidate_id`, `client_id`, `category`, `content`, `source_artifact_id`, `confidence`, `proposed_action`.
Priority: Phase 3.

### `MemoryConflict`
Purpose: Explicit mismatch between retrieved memory and current request.
Fields: `conflict_id`, `memory_id`, `request_field`, `memory_value`, `request_value`, `severity`.
Priority: Phase 2.

### `MemoryConsolidationTask`
Purpose: Queue item for async memory consolidation.
Fields: `task_id`, `client_id`, `candidate_ids`, `status`, `attempt_count`, `last_error`, `created_at`, `processed_at`.
Priority: Phase 4.

## Persistence contracts

### `AuditEvent`
Purpose: Append-only record of meaningful system and user actions.
Fields: `event_id`, `event_type`, `correlation`, `actor`, `node`, `outcome`, `details`, `created_at`.
Priority: Phase 1.

### `TraceSpanEvent`
Purpose: Provider-neutral trace/span event emitted by graph nodes.
Fields: `span_id`, `parent_span_id`, `trace_id`, `node_name`, `status`, `started_at`, `ended_at`, `duration_ms`, `provider_trace_url`.
Priority: Phase 3.

### `MetricEvent`
Purpose: Provider-neutral metric emitted for local logs or CloudWatch.
Fields: `metric_name`, `value`, `unit`, `dimensions`, `timestamp`, `correlation`.
Priority: Phase 3.

### `SessionState`
Purpose: Short-lived session and workflow continuity record.
Fields: `session_id`, `actor`, `active_request_id`, `workflow_state`, `last_activity_at`, `ttl`.
Priority: Phase 2.

### `ApprovalArtifactItem`
Purpose: DynamoDB item shape for approvals.
Fields: `approval_id`, `request_id`, `trace_id`, `approval_status`, `recommendation_hash`, `artifact_json`, `ttl`.
Priority: Phase 3.

### `AuditEventItem`
Purpose: DynamoDB item shape for audit events and query indexes.
Fields: `event_id`, `request_id`, `trace_id`, `event_type`, `timestamp`, `event_json`, `ttl`.
Priority: Phase 2.

## Seeding and eval contracts

### `SeedManifest`
Purpose: Describe a versioned seed batch.
Fields: `manifest_version`, `dataset_id`, `dataset_version`, `environment`, `synthetic`, `domains`, `created_at`, `created_by`, `idempotency_key`, `manifest_checksum_sha256`, `provenance`, `rollback_from_dataset_version`.
Validation: checksum placeholders are valid only in documentation examples, not in executable seed manifests.
Priority: Phase 1.

### `SeedDomainBatch`
Purpose: One domain in a seed manifest.
Fields: `domain`, `schema_version`, `record_count`, `file`, `checksum_sha256`, `load_order`.
Priority: Phase 1.

### `GoldenScenario`
Purpose: Repeatable end-to-end test case.
Fields: `scenario_id`, `title`, `request_fixture`, `expected_workflow_state`, `expected_verdict`, `assertions`.
Priority: Phase 4.

### `EvalRun`
Purpose: Record one evaluation run.
Fields: `eval_run_id`, `version`, `suite`, `started_at`, `completed_at`, `summary`, `case_results`.
Priority: Phase 4.

### `EvalCaseResult`
Purpose: Record the result of one eval case.
Fields: `case_id`, `scenario_id`, `status`, `expected`, `actual`, `assertion_failures`, `trace_id`.
Priority: Phase 4.

### `ReleaseGateResult`
Purpose: Record whether a version set is ready to move from local/dev to a higher environment.
Fields: `gate_id`, `environment`, `version`, `contract_passed`, `golden_passed`, `safety_passed`, `critical_failures`, `approved_by`, `decided_at`.
Priority: Phase 5.

## First-build contract order
1. `CorrelationMetadata`, `VersionMetadata`, `ActorContext`, `StructuredError`, `WorkflowState`.
2. `ClientProfile`, `AccountProfile`, `InstrumentReference`, `PortfolioHolding`, `PortfolioSnapshot`, `AllocationTarget`, `RiskProfile`.
3. `PortfolioRebalanceRequest`, `GraphState`, `OrchestrationResponse`.
4. `ResearchResponse`, `MemoryPersonalizationResponse`, `RiskPolicyResponse`.
5. `ExecutionProposalResponse`, `TradeProposal`, `RecommendationPackage`, `ApprovalArtifact`, `ApprovalActionRequest`, `ApprovalTransitionResult`.
6. `AuditEvent`, `SessionState`, `ApprovalArtifactItem`, `AuditEventItem`, `TraceSpanEvent`, `MetricEvent`.
7. `SeedManifest`, `SeedDomainBatch`, `GoldenScenario`, `EvalRun`, `EvalCaseResult`, `ReleaseGateResult`.
