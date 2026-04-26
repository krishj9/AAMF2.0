# Observability and Evals

## Observability strategy
- Use a tracing-provider abstraction with selectable backend:
  - `bedrock_agentcore` for Bedrock/AgentCore tracing
  - `langsmith` for LangSmith tracing
- Use CloudWatch for metrics, logs, dashboards, and alarms in all modes.
- Correlate traces with audit events for incident analysis.

## Tracing provider switching rules
- Configure provider via environment/config (for example `TRACE_PROVIDER`).
- Keep trace emission calls provider-agnostic through a single adapter interface.
- Preserve canonical correlation IDs (`request_id`, `session_id`, `trace_id`) across providers.
- Capture provider-specific trace link as optional metadata (`provider_trace_url`) for operator workflows.
- Require parity checks to ensure both providers emit equivalent core spans for critical workflow stages.

## Must-have metrics
- End-to-end orchestration latency
- Node-level latency and error rates
- Blocked/degraded/low-confidence rates
- Guardrail violation rates
- Approval turnaround and override rates
- Memory retrieval and consolidation success/failure rates

## Eval suites
- Contract tests for all schemas and handoffs
- Golden scenarios for representative rebalance cases
- Safety/adversarial tests for policy bypass and hallucination risk
- Compliance tests for mandate and suitability rules
- Operational tests for timeouts, retries, and degraded mode behavior

## Release gates
- Critical contract tests: 100% pass required
- Critical safety/policy: zero unresolved critical failures
- Promotion requires documented version set and rollback plan
