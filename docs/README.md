# Cursor-Friendly Docs: Portfolio Multi-Agent Platform

This folder contains a fresh, Cursor-friendly documentation set generated from your existing `specs` and `steering` intent, with one key architecture change:

- Orchestration runtime is **LangGraph** running in **AWS Lambda**
- **Amazon Bedrock + AgentCore** remain the managed control plane for:
  - Guardrails
  - Memory
  - Evals
  - Observability

## Why this structure

The layout is optimized for agent-assisted development in Cursor:

- Small, focused files by concern
- Explicit boundaries between product, architecture, requirements, contracts, and operations
- Clear execution roadmap from idea to deploy

## Folder map

- `00-product/` - product intent and boundaries
- `01-architecture/` - system design and orchestration decisions
- `02-requirements/` - functional and non-functional requirements
- `03-data-contracts/` - core object contracts and metadata standards
- `04-implementation/` - phased build plan and task backlog
- `05-operations/` - safety and controls, security, observability, and eval operations
- `06-deployment/` - AWS Lambda deployment and environment model
- `99-steering/` - Cursor steering guidance for ongoing generation

## Reading order

1. `00-product/product.md`
2. `01-architecture/system-architecture.md`
3. `01-architecture/langgraph-orchestration.md`
4. `02-requirements/detailed-requirements.md`
5. `02-requirements/non-functional-requirements.md`
6. `03-data-contracts/README.md`
7. `03-data-contracts/data-contract-catalog.md`
8. `04-implementation/implementation-guide.md`
9. `04-implementation/workstreams.md`
10. `05-operations/data-seeding-strategy.md`
11. `06-deployment/aws-lambda-bedrock-agentcore.md`
