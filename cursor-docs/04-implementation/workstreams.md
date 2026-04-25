# Implementation Workstreams

## WS-1 Platform foundation
- Define schemas and Pydantic models.
- Implement contract validation and compatibility tests.
- Build shared correlation and error middleware.

## WS-2 LangGraph orchestration runtime
- Build Lambda handler and LangGraph state machine.
- Implement node contracts and conditional routing.
- Add idempotency and retry policy handling.

## WS-3 Specialist agent nodes
- Research node with market retrieval + grounded summary.
- Memory node with AgentCore retrieval + conflict signaling.
- Risk/policy node with deterministic rule engine + summary layer.
- Execution proposal node with strict gating by policy status.

## WS-4 Bedrock/AgentCore control plane
- Bedrock model invocation adapters.
- Guardrail enforcement wrappers.
- AgentCore memory integration.
- AgentCore observability instrumentation and trace propagation.

## WS-5 Workflow persistence and approvals
- Approval artifact lifecycle and state transition controls.
- Full audit event coverage.
- Session and memory queue persistence with TTL.

## WS-6 Frontend integration
- Orchestrator-only API integration.
- Stage-by-stage workflow status rendering.
- Approval controls with policy-aware enablement.
- Angular application architecture, routing, and state management patterns.

## WS-7 Evals and release gates
- Contract, scenario, safety, policy, regression, and operational evals.
- Promotion gates tied to critical pass thresholds.
