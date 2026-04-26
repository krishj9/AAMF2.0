# Startup Guide - LLM-LangGraph Integration

This guide explains how to start all services (Backend, Research Agent A2A, Sentiment Agent MCP) for the LLM-LangGraph integration.

## Quick Start (Recommended)

### Option 1: Docker Compose (Easiest)

```bash
# Start all services with Docker Compose
docker-compose up

# In another terminal, verify services are running
curl http://localhost:8000/health
curl http://localhost:8101/health
curl http://localhost:8201/health
```

**Advantages:**
- All services in isolated containers
- Automatic dependency management
- Easy cleanup with `docker-compose down`

**Requirements:**
- Docker and Docker Compose installed

### Option 2: Bash Script (Development)

```bash
# Make script executable
chmod +x backend/scripts/run_all_services.sh

# Start all services
./backend/scripts/run_all_services.sh local

# Press Ctrl+C to stop all services
```

**Advantages:**
- Direct access to logs
- Easy to modify for development
- No Docker required

**Requirements:**
- Python 3.11+
- uv package manager
- Bash shell

### Option 3: Manual (Full Control)

Start each service in a separate terminal:

**Terminal 1 - Research Agent A2A:**
```bash
cd remote-agents/research-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Sentiment Agent MCP:**
```bash
cd mcp-servers/sentiment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

**Terminal 3 - Backend:**
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Service Endpoints

Once all services are running:

| Service | URL | Purpose |
|---------|-----|---------|
| Backend | http://localhost:8000 | Main API |
| Research Agent A2A | http://localhost:8101 | Market research via A2A protocol |
| Sentiment Agent MCP | http://localhost:8201 | Sentiment analysis via MCP protocol |

## Health Checks

Verify all services are running:

```bash
# Backend health
curl http://localhost:8000/health

# Research Agent health
curl http://localhost:8101/health

# Sentiment Agent health
curl http://localhost:8201/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:00:00Z"
}
```

## Configuration

### Environment Variables

Create `backend/.env` to configure the backend:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# Feature Flags (all disabled by default for safety)
FEATURE_MEMORY_AGENT_LLM_ENABLED=false
FEATURE_RESEARCH_AGENT_LLM_ENABLED=false
FEATURE_SENTIMENT_AGENT_LLM_ENABLED=false
FEATURE_REBALANCING_AGENT_LLM_ENABLED=false
FEATURE_RISK_AGENT_LLM_ENABLED=false
FEATURE_TRADE_PROPOSAL_AGENT_LLM_ENABLED=false

# LLM Configuration
LLM_BEDROCK_REGION=us-east-1
LLM_MEMORY_AGENT_MODEL=anthropic.claude-3-haiku-20240307-v1:0
LLM_RESEARCH_AGENT_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0
LLM_SENTIMENT_AGENT_MODEL=anthropic.claude-3-haiku-20240307-v1:0
LLM_REBALANCING_AGENT_MODEL=anthropic.claude-3-sonnet-20240229-v1:0
LLM_RISK_AGENT_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0
LLM_TRADE_PROPOSAL_AGENT_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0

# Remote Agent URLs
RESEARCH_AGENT_URL=http://localhost:8101/a2a/research
SENTIMENT_MCP_URL=http://localhost:8201/mcp

# Cost Management
COST_DAILY_TOKEN_BUDGET=1000000
COST_ALERT_THRESHOLD_USD=100.0

# Tracing
TRACE_PROVIDER=bedrock_agentcore
```

### Enabling LLM Features

To enable LLM for specific agents, set the corresponding feature flag:

```bash
export FEATURE_MEMORY_AGENT_LLM_ENABLED=true
export FEATURE_RESEARCH_AGENT_LLM_ENABLED=true
export FEATURE_SENTIMENT_AGENT_LLM_ENABLED=true
```

Then restart the backend service.

## Testing

### Run Property Tests

```bash
cd backend
pytest tests/property/ -v
```

### Test Individual Services

**Test Research Agent A2A:**
```bash
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

**Test Sentiment Agent MCP:**
```bash
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

## Troubleshooting

### Port Already in Use

If you get "Address already in use" error:

```bash
# Find process using the port
lsof -i :8000  # Backend
lsof -i :8101  # Research Agent
lsof -i :8201  # Sentiment Agent

# Kill the process
kill -9 <PID>
```

Or use different ports:

```bash
PORT=8001 RESEARCH_AGENT_PORT=8102 SENTIMENT_MCP_PORT=8202 ./backend/scripts/run_all_services.sh local
```

### Virtual Environment Issues

If you get Python version errors:

```bash
# Ensure Python 3.11+ is installed
python3 --version

# Create fresh virtual environments
rm -rf remote-agents/research-agent/venv
rm -rf mcp-servers/sentiment/venv

# Restart services
./backend/scripts/run_all_services.sh local
```

### Import Errors

If you get import errors in remote agents:

```bash
# Ensure backend is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Restart services
./backend/scripts/run_all_services.sh local
```

### Docker Issues

If Docker Compose fails:

```bash
# Rebuild images
docker-compose build --no-cache

# Start services
docker-compose up
```

## Logs

### Docker Compose Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f research-agent
docker-compose logs -f sentiment-mcp
```

### Bash Script Logs

Logs are printed to stdout. To save logs to files:

```bash
./backend/scripts/run_all_services.sh local > services.log 2>&1 &
```

## Stopping Services

### Docker Compose

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Bash Script

```bash
# Press Ctrl+C in the terminal running the script
# Or kill the process
pkill -f "run_all_services.sh"
```

### Manual

```bash
# Kill each service in its terminal
# Press Ctrl+C in each terminal
```

## Next Steps

1. **Enable LLM Features**: Set feature flags to enable LLM for specific agents
2. **Configure AWS Credentials**: Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
3. **Run Tests**: Execute property tests to verify functionality
4. **Monitor Logs**: Watch logs for any errors or warnings
5. **Test Workflows**: Send requests to the backend API

## Additional Resources

- [README_LLM_INTEGRATION.md](README_LLM_INTEGRATION.md) - Quick start guide
- [FINAL_SUMMARY.md](FINAL_SUMMARY.md) - Project overview
- [backend/README.md](backend/README.md) - Backend documentation
- [remote-agents/research-agent/README.md](remote-agents/research-agent/README.md) - Research Agent documentation
- [mcp-servers/sentiment/README.md](mcp-servers/sentiment/README.md) - Sentiment Agent documentation

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review service logs for error messages
3. Verify all dependencies are installed
4. Ensure ports are not in use
5. Check environment variables are set correctly
