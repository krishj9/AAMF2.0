# LangGraph Orchestration on Lambda

## Why LangGraph here
LangGraph provides explicit graph state, predictable transitions, retry control, and flexible branching. This gives strong control over financial workflows while keeping Bedrock as the managed AI control plane.

## Graph design

### Nodes
- `validate_request`
- `initialize_context_and_trace`
- `log_request_audit_event`
- `hydrate_memory`
- `run_research`
- `run_sentiment_analysis`
- `run_portfolio_rebalancing`
- `run_risk_policy`
- `generate_execution_proposal`
- `apply_output_guardrails`
- `assemble_recommendation`
- `create_approval_artifact`
- `persist_workflow_artifacts`
- `enqueue_memory_consolidation_candidates`
- `emit_workflow_audit_event`
- `return_response`

### Cross-cutting orchestration service
- `trace_provider_adapter` (not a graph node): unified interface used by all nodes for trace/span emission.
- Supported providers: `bedrock_agentcore` and `langsmith`.
- Provider selection SHALL be environment-configurable and hot-swappable through config/deployment variables.

### Conditional edges
- If validation fails -> `emit_workflow_audit_event` -> `return_response` with structured error
- If policy is `NON_COMPLIANT` or `UNRESOLVED` -> skip execution proposal, mark `BLOCKED`
- If guardrails hard-block output -> mark `BLOCKED`, return `GUARDRAIL_VIOLATION`
- If non-critical sources fail -> continue with `DEGRADED` when policy permits

## Requirement coverage map
- **R1/R2 (entrypoint + validation):** `validate_request`, `initialize_context_and_trace`, `log_request_audit_event`
- **R3 (research):** `run_research`
- **Sentiment analysis:** `run_sentiment_analysis`
- **Portfolio rebalancing:** `run_portfolio_rebalancing`
- **R4 (memory retrieval):** `hydrate_memory`
- **R5 (memory lifecycle):** `enqueue_memory_consolidation_candidates` (writeback pipeline trigger)
- **R6 (risk/policy):** `run_risk_policy`
- **R7 (execution proposal):** `generate_execution_proposal` with policy gate
- **R8 (approval workflow):** `create_approval_artifact`, `persist_workflow_artifacts`
- **R9 (no autonomous execution):** enforced by graph boundary (no execution node in orchestration path)
- **R10 (guardrails):** `apply_output_guardrails`
- **R11 (observability + audit):** `initialize_context_and_trace`, `log_request_audit_event`, `emit_workflow_audit_event`
- **R13 (seeding readiness):** graph consumes seeded domain data but does not own seeding jobs
- **R14 (schema versioning):** `validate_request` + schema metadata carried through state and response

## State object (minimum)
- Correlation: `request_id`, `session_id`, `trace_id`
- Versioning: `schema_version`, `agent_version_set`, `policy_version`, `environment`
- Tracing: `trace_provider`, optional `provider_trace_url`
- Inputs: normalized request + user role context
- Node outputs: memory, research, sentiment, rebalancing, policy, proposal, approval, guardrail_result
- Quality: confidence map, degraded reasons, blockers
- Final: recommendation package + approval artifact reference + audit event ids

## Lambda runtime model
- One Lambda handler per orchestration invocation
- Configurable timeout budget and node-level retry policy
- Idempotency key based on request/session tuple
- Structured error contract for all failures
- Per-node telemetry and audit correlation fields are mandatory, even in error paths
- Tracing provider SHALL be selected via config (for example `TRACE_PROVIDER=bedrock_agentcore|langsmith`) without codepath forks in node business logic

## Integration pattern
- LangGraph nodes call Bedrock models for synthesis/explanations
- Guardrails run on recommendation-bearing input/output paths via dedicated node
- Memory retrieval/write intents use AgentCore APIs
- Traces are emitted via `trace_provider_adapter` per node and correlated to audit events
- Metrics/logs continue to be emitted to CloudWatch regardless of tracing provider

## Reference execution path
1. `validate_request`
2. `initialize_context_and_trace`
3. `log_request_audit_event`
4. Parallel fan-out: `hydrate_memory` + `run_research`
5. `run_sentiment_analysis`
6. `run_portfolio_rebalancing`
7. `run_risk_policy`
8. Conditional: `generate_execution_proposal` only if policy allows
9. `assemble_recommendation`
10. `apply_output_guardrails`
11. `create_approval_artifact`
12. `persist_workflow_artifacts`
13. `enqueue_memory_consolidation_candidates`
14. `emit_workflow_audit_event`
15. `return_response`

## Agent implementation rule
Each graph node should be backed by a concrete agent class with a typed input/output contract. Service functions may support agents, but the orchestration path should expose explicit agent boundaries so traces, audit events, tests, and UI stage progress can identify which agent produced each result.
