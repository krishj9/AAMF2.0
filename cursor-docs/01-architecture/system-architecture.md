# System Architecture

## High-level flow
1. Angular frontend submits `PortfolioRebalanceRequest` to API layer.
2. API invokes a Lambda entrypoint that runs LangGraph.
3. LangGraph orchestrates explicit specialist agents:
   - Memory/Personalization Agent
   - Research Agent
   - Sentiment Analysis Agent
   - Portfolio Rebalancing Agent
   - Risk & Compliance Agent
   - Trade Execution Proposal Agent
   - Human Approval Workflow Agent
4. Node outputs are merged into a recommendation package.
5. Workflow state is set (`NORMAL`, `DEGRADED`, `LOW_CONFIDENCE`, `BLOCKED`).
6. Approval artifact is persisted and returned for human decisioning.

## Core components
- **Angular frontend**: request intake, recommendation review, approval controls
- **API layer**: authentication, request validation, Lambda invocation, Python FastAPI
- **Lambda + LangGraph runtime**: orchestration, state transitions, routing/fallback logic
- **Supervisor Agent**: coordinates all specialist agents and assembles final user-facing responses
- **Specialist agents**: independent bounded agents for memory, research, sentiment, rebalancing, risk/compliance, trade proposal, and human approval workflow
- **Bedrock runtime**: model inference endpoints
- **Bedrock Guardrails**: safety, policy, sensitive data, grounding checks
- **AgentCore Memory**: long-term memory retrieval and managed memory lifecycle features
- **Tracing provider adapter**: pluggable tracing backend (`bedrock_agentcore` or `langsmith`)
- **CloudWatch**: metrics/logs/dashboards/alarms for platform operations (independent of tracing provider)
- **DynamoDB**: approval artifacts, audit events, session state, memory consolidation queue

## Local vs AWS persistence
- Local development uses DynamoDB Local through the same repository interfaces used in AWS.
- Default local endpoint: `http://localhost:55000`.
- AWS deployments omit the local endpoint and use hosted DynamoDB tables with the same logical table names.
- The application selects local or AWS DynamoDB through environment settings, not code forks.

## Trust boundaries
- Frontend may only call the orchestration entrypoint.
- Specialist agents are private internal components.
- Memory writes and corrections require role-based authorization.
- Approval decisions require signed-in owner identity and are fully audited.

## Guiding architecture rules
- Keep deterministic checks separate from model-assisted explanation.
- Keep contracts provider-agnostic at API boundaries.
- Preserve correlation metadata end-to-end: request/session/trace/version/policy/environment.
- Keep tracing provider behind an abstraction so backend switching does not require workflow logic changes.
