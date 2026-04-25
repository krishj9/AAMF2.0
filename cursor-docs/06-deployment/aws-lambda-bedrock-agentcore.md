# AWS Deployment Model: Lambda + LangGraph + Bedrock/AgentCore

## Runtime architecture
- Angular web frontend -> API Gateway or authenticated service API -> Lambda orchestrator
- Lambda runs LangGraph for orchestration and state transitions
- Bedrock runtime invoked from graph nodes for model tasks
- AgentCore services used for memory and observability
- DynamoDB used for durable workflow persistence

## Environment model
- `dev`
- `test`
- `staging`
- `main`

Each environment has isolated config, IAM, data boundaries, and deployment artifacts.

## Deployment units
- Orchestrator Lambda package
- Node adapter libraries
- Shared schema package
- Angular frontend application build artifacts
- Terraform configuration for DynamoDB/IAM/alarms/logging

## Configuration baseline
- Schema version set
- Policy version set
- Model and guardrail configuration
- Tracing provider configuration (`TRACE_PROVIDER=bedrock_agentcore|langsmith`)
- Timeout/retry budgets
- Environment and correlation metadata defaults

## Infrastructure as Code
- Use Terraform for AWS resources.
- Keep reusable modules under `infra/terraform/modules/`.
- Keep environment-specific inputs under `infra/terraform/environments/<environment>/`.
- Do not commit `.tfstate`, `.terraform/`, or real `.tfvars` files.
- Commit example variable files as `*.tfvars.example`.
- Run `terraform plan` before every `terraform apply`.

## Promotion checklist (minimum)
- All required eval suites pass thresholds
- No unresolved critical policy/safety findings
- Observability dashboards and alarms verified
- Rollback path tested and documented
