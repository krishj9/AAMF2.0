# AWS Deployment Model: Lambda + LangGraph + Bedrock/AgentCore

## Runtime architecture
- Angular web frontend -> API Gateway HTTP API -> Lambda-backed FastAPI services
- Backend Lambda handles portfolio APIs, rebalance orchestration, approvals, and market monitoring
- Remote Research Agent Lambda exposes the A2A research endpoint
- Sentiment MCP Lambda exposes the JSON-RPC MCP tool endpoint
- Bedrock runtime invoked from graph nodes for model tasks when live model adapters are enabled
- AgentCore services used for memory and observability when enabled
- DynamoDB used for durable workflow and portfolio persistence

## Environment model
- `dev`
- `test`
- `staging`
- `main`

Each environment has isolated config, IAM, data boundaries, and deployment artifacts.

## Deployment units
- Backend Lambda package
- Remote Research Agent Lambda package
- Sentiment MCP Lambda package
- Angular S3 static website artifact upload
- Shared node adapter libraries
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
- `MARKET_STREAM_MAX_EVENTS` should be set in AWS so Lambda market streams are bounded

## Infrastructure as Code
- Use Terraform for AWS resources.
- Keep reusable modules under `infra/terraform/modules/`.
- Keep environment-specific inputs under `infra/terraform/environments/<environment>/`.
- Do not commit `.tfstate`, `.terraform/`, or real `.tfvars` files.
- Commit example variable files as `*.tfvars.example`.
- Run `terraform plan` before every `terraform apply`.

## DynamoDB runtime selection
- Local development uses DynamoDB Local at `http://localhost:55000`.
- AWS deployment uses hosted DynamoDB by leaving the endpoint unset.
- Keep table names configurable through environment variables.
- The application repository layer must not branch business logic between local and AWS modes.

## Lambda packaging
- Build packages before Terraform plan/apply with `./infra/scripts/package_lambda.sh`.
- Packages are written under `infra/build/` and are not committed.
- Each FastAPI service has a Mangum handler for API Gateway events.
- The packaging script uses an AWS SAM Python 3.13 Docker image when Docker is available so native wheels match Lambda.
- If native dependencies grow, switch from zip artifacts to container-image Lambdas using ECR.

## Frontend hosting
- The dev environment provisions an S3 static website bucket.
- Angular reads `app-config.js` at runtime for `apiBaseUrl`.
- For AWS, overwrite `app-config.js` in the built artifact with the API Gateway URL before uploading to S3.

## Promotion checklist (minimum)
- All required eval suites pass thresholds
- No unresolved critical policy/safety findings
- Observability dashboards and alarms verified
- Rollback path tested and documented
