# Research Agent A2A Server

Agent-to-Agent (A2A) server for market research with AWS Bedrock LLM integration.

## Features

- A2A protocol implementation for remote agent communication
- LLM-enhanced market context synthesis
- Evidence-based insights with citations
- Graceful fallback to deterministic behavior
- Feature flag support for LLM enable/disable

## Installation

```bash
cd remote-agents/research-agent
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
# Feature Flags
export FEATURE_RESEARCH_AGENT_LLM_ENABLED=true

# LLM Configuration
export LLM_BEDROCK_REGION=us-east-1
export LLM_RESEARCH_AGENT_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0

# AWS Credentials
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Running the Server

```bash
python main.py
```

The server will start on `http://0.0.0.0:8101`.

## API Endpoints

### POST /a2a/research

A2A endpoint for market research.

**Request:**
```json
{
  "task": "portfolio_research",
  "request_id": "req-123",
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "portfolio_request": {
    "portfolio_id": "PORT-001",
    "portfolio_snapshot": {...},
    "allocation_target": {...}
  }
}
```

**Response:**
```json
{
  "request_id": "req-123",
  "summary": "Market context synthesized",
  "payload": {
    "market_summary": "...",
    "key_trends": [...],
    "sector_insights": [...],
    "risk_factors": [...],
    "opportunities": [...],
    "confidence": 0.85
  },
  "timestamp": "2024-01-15T10:00:00Z",
  "agent_name": "Research Agent",
  "protocol": "A2A",
  "execution_location": "remote"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "Research Agent",
  "protocol": "A2A",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

## Testing

Test the server with curl:

```bash
# Health check
curl http://localhost:8101/health

# Research request
curl -X POST http://localhost:8101/a2a/research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "portfolio_research",
    "request_id": "test-123",
    "symbols": ["AAPL", "MSFT"],
    "portfolio_request": {
      "portfolio_id": "PORT-001"
    }
  }'
```

## Architecture

The Research Agent A2A server:

1. Receives A2A requests from the main orchestrator
2. Loads prompt templates for market context synthesis
3. Invokes AWS Bedrock LLM for market analysis
4. Validates LLM responses against schema
5. Returns A2A response envelope with market context

If LLM is disabled or fails, the agent falls back to deterministic behavior.

## Deployment

For production deployment:

1. Deploy as a separate service (ECS, Lambda, etc.)
2. Configure environment variables
3. Set up IAM roles for Bedrock access
4. Configure networking for A2A communication
5. Set up monitoring and logging

## Notes

- LLM integration is disabled by default via feature flags
- All LLM outputs are validated against schemas
- Evidence grounding is required for all insights
- Confidence thresholds ensure quality
- Graceful fallback on LLM failure
