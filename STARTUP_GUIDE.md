# Startup Guide

AI-powered portfolio rebalancing platform with LangGraph orchestration, AWS Bedrock LLMs, A2A and MCP agent protocols, and human-in-the-loop approval workflows.

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker + Docker Compose | Latest | Local backend services |
| Node.js + npm | 18+ | Frontend dev server |
| Python | 3.12+ | Backend (via uv) |
| AWS CLI | Latest | Deployment only |
| Terraform | 1.5+ | Deployment only |

AWS credentials with access to **Bedrock** (Claude models) and **DynamoDB** are required for LLM features and AWS deployment.

---

## Running Locally

### 1. Start Backend Services

```bash
docker compose up --build
```

This starts four containers:

| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | http://localhost:8000 | FastAPI + LangGraph orchestrator |
| Research Agent | http://localhost:8101 | A2A remote research agent |
| Sentiment Agent | http://localhost:8201 | MCP sentiment tool server |
| DynamoDB Local | http://localhost:55000 | Local persistence |

Verify all services are healthy:

```bash
curl http://localhost:8000/health
curl http://localhost:8101/health
curl http://localhost:8201/health
```

### 2. Start Frontend

```bash
cd frontend
npm install
npm start
```

Open **http://localhost:4200**

The dev server proxies `/api/*` to `http://localhost:8000` automatically. No token is required locally — the API token gate is disabled when `API_TOKEN` is not set.

### 3. Stop Services

```bash
docker compose down
```

---

## LLM Features

All LLM features are **enabled by default** in `docker-compose.yml`. They require:
- AWS credentials mounted at `~/.aws` (already configured in docker-compose)
- AWS region set to `us-east-2` (matches your AWS config)
- Bedrock model access for Claude models in your account

### Models Used

| Agent | Model | Notes |
|-------|-------|-------|
| Memory | `us.anthropic.claude-3-5-haiku-20241022-v1:0` | Fast, semantic queries |
| Research | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Market analysis |
| Sentiment | `us.anthropic.claude-3-5-haiku-20241022-v1:0` | Sentiment classification |
| Risk | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Policy decisions |
| Trade Proposal | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` | Trade rationale |

> **Note:** These are cross-region inference profile IDs (prefixed `us.`). Direct model IDs without the `us.` prefix are not supported for on-demand invocation.

### Disabling LLMs

To run without LLM calls (faster, no AWS cost), edit `docker-compose.yml` and set all `FEATURE_*_LLM_ENABLED` to `false`, then restart:

```bash
docker compose down && docker compose up --build
```

---

## Application Walkthrough

### What the app does

1. **Portfolio Monitor** — streams simulated market data showing allocation drift
2. **Auto-generates recommendations** — when drift exceeds 5% threshold, LangGraph runs 7 agents in sequence (Memory → Research → Sentiment → Rebalancing → Risk → Trade Proposal → Approval)
3. **Recommendation Review** — shows AI market intelligence (sentiment, research) before the decision
4. **Human approval** — Approve to apply trades, Reject to dismiss
5. **System Intelligence** — view the full agent workflow trace, memory timeline, and audit trail

### Key interactions

| Action | What happens |
|--------|-------------|
| Page loads | Portfolio starts drifted (67.5% equity vs 60% target) → auto-generates recommendation |
| Approve | Portfolio rebalanced, marked as balanced |
| Reject | Recommendation dismissed, portfolio stays drifted |
| ↺ Simulate Market Drift | Forces drift, generates new recommendation |
| ⚙ Preferences | 4-step wizard to set risk profile and allocation targets |
| ⬡ View Agent Workflow | System Intelligence page — workflow trace, memory, audit trail |

---

## Deploying to AWS

### Prerequisites

1. AWS CLI configured: `aws configure list`
2. Terraform installed: `terraform -version`
3. Docker available (for Lambda packaging)

### One-time setup

```bash
# Copy example tfvars (already done — dev.tfvars exists)
# Edit if needed:
cat infra/terraform/environments/dev/dev.tfvars
```

Current values:
```
aws_region           = "us-east-2"
project_name         = "asset-management"
environment          = "dev"
lambda_runtime       = "python3.13"
frontend_bucket_name = "asset-management-dev-frontend-855603407942"
api_token            = "aIJ3WTclVQs6xIGhm9d-s89aBR0aq3wqB1GE4hM0TNw"
```

> **Security:** `api_token` is the shared secret that gates all API access. Keep `dev.tfvars` out of version control (it's in `.gitignore`).

### Deploy backend

```bash
# 1. Package Lambda functions
./infra/scripts/package_lambda.sh

# 2. Deploy infrastructure
cd infra/terraform/environments/dev
terraform init
terraform apply -var-file=dev.tfvars
```

### Deploy frontend

```bash
./infra/scripts/publish_frontend.sh \
  "https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com" \
  "asset-management-dev-frontend-855603407942" \
  "aIJ3WTclVQs6xIGhm9d-s89aBR0aq3wqB1GE4hM0TNw"
```

### Live URLs

| Resource | URL |
|----------|-----|
| Frontend | http://asset-management-dev-frontend-855603407942.s3-website.us-east-2.amazonaws.com |
| API | https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com |

### Verify deployment

```bash
# Health check (no token needed)
curl https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/health

# API check (token required)
curl -H "x-api-token: aIJ3WTclVQs6xIGhm9d-s89aBR0aq3wqB1GE4hM0TNw" \
  https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/api/portfolios
```

---

## Security

### API Token Gate

All `/api/*` routes require the `x-api-token` header. The frontend sends it automatically via an Angular HTTP interceptor. The token is baked into `app-config.js` at deploy time.

- Without token → `401 Unauthorized`
- With wrong token → `401 Unauthorized`
- `/health` → always open (no token needed)

### Rate Limiting

API Gateway stage throttling:
- **Burst**: 20 concurrent requests
- **Rate**: 10 requests/second sustained

Requests exceeding limits receive `429 Too Many Requests`.

### Local development

The token gate is **disabled locally** — `API_TOKEN` is not set in `docker-compose.yml`, so the middleware skips validation. No token is needed when running `npm start` against `localhost:8000`.

---

## AWS Infrastructure

All resources are in `us-east-1` (Lambda, API Gateway, DynamoDB) except the S3 frontend bucket which is in `us-east-2`.

| Resource | Name |
|----------|------|
| Backend Lambda | `asset-management-dev-backend` |
| Research Agent Lambda | `asset-management-dev-research-agent` |
| Sentiment MCP Lambda | `asset-management-dev-sentiment-mcp` |
| API Gateway | `asset-management-dev-api` |
| DynamoDB tables | `asset-management-dev-{approvals,portfolios,preferences,...}` |
| S3 bucket | `asset-management-dev-frontend-855603407942` |

### Monitor logs

```bash
# Backend logs (live)
aws logs tail /aws/lambda/asset-management-dev-backend --follow --region us-east-1

# Check for errors
aws logs tail /aws/lambda/asset-management-dev-backend --region us-east-1 | grep -i error
```

### Teardown

```bash
cd infra/terraform/environments/dev
terraform destroy -var-file=dev.tfvars
```

---

## Troubleshooting

### Frontend can't reach backend (ECONNREFUSED)

Docker containers aren't running. Start them:
```bash
docker compose up --build
```

### LLM calls failing (ResourceNotFoundException)

The model ID is deprecated. Check `backend/app/core/config.py` — all models must use the `us.` prefix (cross-region inference profiles).

### LLM calls failing (ValidationException: on-demand throughput not supported)

Same issue — use `us.anthropic.*` model IDs, not `anthropic.*` directly.

### Preferences not saving (400 error)

All financial values must be `Decimal` on the backend. The preferences route converts strings to `Decimal` — if you see 400, check that the request body has numeric strings, not floats.

### CORS errors on AWS

Both API Gateway CORS config and FastAPI middleware must allow the same methods. Current config allows: `GET, POST, PUT, DELETE, OPTIONS`.

### Docker build fails

Force a clean rebuild:
```bash
docker compose build --no-cache
docker compose up
```

### Port already in use

```bash
lsof -i :8000   # find what's using port 8000
kill -9 <PID>
```

---

## Project Structure

```
/
├── frontend/          # Angular 19 SPA (npm start → localhost:4200)
├── backend/           # FastAPI + LangGraph (port 8000)
├── remote-agents/     # A2A Research Agent (port 8101)
├── mcp-servers/       # MCP Sentiment Server (port 8201)
├── infra/
│   ├── scripts/       # package_lambda.sh, publish_frontend.sh
│   └── terraform/     # AWS infrastructure as code
├── docker-compose.yml # Local dev: all 4 services
└── AGENT_CONTEXT.md   # Full technical context for AI coding agents
```

For deep technical context (architecture, data contracts, agent implementations, known issues), see **[AGENT_CONTEXT.md](AGENT_CONTEXT.md)**.
