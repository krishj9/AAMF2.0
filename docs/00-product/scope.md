# Scope and Non-Goals

## In scope
- Multi-agent rebalance workflow (research, memory, risk/policy, execution proposal)
- LangGraph stateful orchestration in Lambda
- Bedrock model inference and guardrail enforcement
- AgentCore memory retrieval and memory lifecycle operations
- AgentCore observability and CloudWatch integration
- Approval artifact generation and traceable workflow events
- Environment-isolated deployment (dev, test, staging, main)

## Out of scope
- Autonomous trade execution in production
- Direct frontend calls to specialist agents
- Raw chain-of-thought exposure in UI, logs, traces, or audits

## Assumptions
- Frontend is a web application built with Angular
- DynamoDB remains primary persistence for approval, audit, session, and memory queue data
- All major contracts remain schema-first and versioned
