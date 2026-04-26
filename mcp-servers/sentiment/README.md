# Sentiment Agent MCP Server

Model Context Protocol (MCP) server for sentiment analysis with AWS Bedrock LLM integration.

## Features

- MCP JSON-RPC 2.0 protocol implementation
- LLM-enhanced sentiment analysis
- Theme identification and categorization
- Graceful fallback to neutral sentiment
- Feature flag support for LLM enable/disable

## Installation

```bash
cd mcp-servers/sentiment
pip install -r requirements.txt
```

## Configuration

Set environment variables:

```bash
# Feature Flags
export FEATURE_SENTIMENT_AGENT_LLM_ENABLED=true

# LLM Configuration
export LLM_BEDROCK_REGION=us-east-1
export LLM_SENTIMENT_AGENT_MODEL=anthropic.claude-3-haiku-20240307-v1:0

# AWS Credentials
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

## Running the Server

```bash
python server.py
```

The server will start on `http://0.0.0.0:8201`.

## API Endpoints

### POST /mcp

MCP JSON-RPC 2.0 endpoint for tool invocation.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "method": "analyze_symbol_news_sentiment",
  "params": {
    "symbol": "AAPL",
    "news_items": [
      {
        "headline": "Apple announces record sales",
        "source": "Reuters",
        "published_date": "2024-01-15",
        "summary": "Strong Q4 results",
        "sentiment_indicators": "positive, strong"
      }
    ],
    "social_posts": [
      {
        "platform": "Twitter",
        "content": "Love the new iPhone!",
        "engagement": 1500,
        "date": "2024-01-15"
      }
    ]
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "result": {
    "symbol": "AAPL",
    "overall_sentiment": "POSITIVE",
    "sentiment_score": 0.75,
    "themes": [
      {
        "theme": "Product success",
        "sentiment": "POSITIVE",
        "mentions": 2
      }
    ],
    "confidence": 0.85,
    "sources_analyzed": 2
  }
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "agent": "Sentiment Agent",
  "protocol": "MCP",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

### GET /tools

List available MCP tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "analyze_symbol_news_sentiment",
      "description": "Analyze sentiment for a symbol from news and social media",
      "parameters": {
        "symbol": {"type": "string", "required": true},
        "news_items": {"type": "array", "required": false},
        "social_posts": {"type": "array", "required": false}
      }
    }
  ]
}
```

## Testing

Test the server with curl:

```bash
# Health check
curl http://localhost:8201/health

# List tools
curl http://localhost:8201/tools

# Sentiment analysis
curl -X POST http://localhost:8201/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-123",
    "method": "analyze_symbol_news_sentiment",
    "params": {
      "symbol": "AAPL"
    }
  }'
```

## Architecture

The Sentiment Agent MCP server:

1. Receives MCP JSON-RPC 2.0 requests
2. Loads prompt templates for sentiment analysis
3. Invokes AWS Bedrock LLM for sentiment classification
4. Validates LLM responses against schema
5. Returns MCP JSON-RPC 2.0 response with sentiment analysis

If LLM is disabled or fails, the agent falls back to neutral sentiment.

## MCP Protocol

The server implements the Model Context Protocol (MCP) JSON-RPC 2.0 specification:

- **Method**: Tool name (e.g., "analyze_symbol_news_sentiment")
- **Params**: Tool parameters as JSON object
- **Result**: Tool output as JSON object
- **Error**: Error object with code, message, and optional data

Error codes:
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

## Deployment

For production deployment:

1. Deploy as a separate service (ECS, Lambda, etc.)
2. Configure environment variables
3. Set up IAM roles for Bedrock access
4. Configure networking for MCP communication
5. Set up monitoring and logging

## Notes

- LLM integration is disabled by default via feature flags
- All LLM outputs are validated against schemas
- Confidence thresholds ensure quality
- Graceful fallback to neutral sentiment on LLM failure
- MCP protocol allows flexible tool invocation
