# Deployment Updates - Service Orchestration

## Summary

Updated the deployment infrastructure to automatically start all services (Backend, Research Agent A2A, Sentiment Agent MCP) together, with multiple options for different use cases.

## Changes Made

### 1. Updated `backend/scripts/run_backend.sh`
**Before**: Only started the backend API
**After**: Starts all three services in parallel with proper cleanup

**Features:**
- Starts Research Agent A2A on port 8101
- Starts Sentiment Agent MCP on port 8201
- Starts Backend on port 8000
- Automatic virtual environment setup
- Graceful shutdown with Ctrl+C
- Health check display

### 2. New `backend/scripts/run_all_services.sh`
Alternative script for better visibility and control

**Features:**
- Starts each service in a separate process
- Better error handling and logging
- Service-specific virtual environments
- Health check endpoints displayed
- Easier to debug individual services

### 3. New `docker-compose.yml`
Docker Compose configuration for containerized deployment

**Services:**
- Backend (port 8000)
- Research Agent A2A (port 8101)
- Sentiment Agent MCP (port 8201)
- DynamoDB Local (port 55000)

**Features:**
- Automatic dependency management
- Network isolation
- Health checks
- Environment variable configuration
- Easy cleanup

### 4. New Dockerfiles
- `remote-agents/research-agent/Dockerfile`
- `mcp-servers/sentiment/Dockerfile`

**Features:**
- Python 3.11 slim base image
- Dependency installation
- Health checks
- Proper port exposure

### 5. New `STARTUP_GUIDE.md`
Comprehensive guide for starting services

**Covers:**
- Quick start options (Docker, Bash, Manual)
- Service endpoints and health checks
- Configuration and environment variables
- Testing procedures
- Troubleshooting guide
- Logging and monitoring

## Usage

### Option 1: Docker Compose (Recommended for Production)
```bash
docker-compose up
```

### Option 2: Bash Script (Recommended for Development)
```bash
chmod +x backend/scripts/run_all_services.sh
./backend/scripts/run_all_services.sh local
```

### Option 3: Updated run_backend.sh
```bash
chmod +x backend/scripts/run_backend.sh
./backend/scripts/run_backend.sh local
```

### Option 4: Manual (Full Control)
Start each service in a separate terminal as documented in STARTUP_GUIDE.md

## Service Endpoints

| Service | URL | Health Check |
|---------|-----|--------------|
| Backend | http://localhost:8000 | http://localhost:8000/health |
| Research Agent A2A | http://localhost:8101 | http://localhost:8101/health |
| Sentiment Agent MCP | http://localhost:8201 | http://localhost:8201/health |

## Configuration

All services respect environment variables:

```bash
# Backend configuration
export DYNAMODB_MODE=local
export DYNAMODB_ENDPOINT_URL=http://localhost:55000
export RESEARCH_AGENT_URL=http://localhost:8101/a2a/research
export SENTIMENT_MCP_URL=http://localhost:8201/mcp

# Feature flags (all disabled by default)
export FEATURE_MEMORY_AGENT_LLM_ENABLED=false
export FEATURE_RESEARCH_AGENT_LLM_ENABLED=false
export FEATURE_SENTIMENT_AGENT_LLM_ENABLED=false
export FEATURE_REBALANCING_AGENT_LLM_ENABLED=false
export FEATURE_RISK_AGENT_LLM_ENABLED=false
export FEATURE_TRADE_PROPOSAL_AGENT_LLM_ENABLED=false

# LLM configuration
export LLM_BEDROCK_REGION=us-east-1
export LLM_MEMORY_AGENT_MODEL=anthropic.claude-3-haiku-20240307-v1:0
export LLM_RESEARCH_AGENT_MODEL=anthropic.claude-3-5-sonnet-20240620-v1:0
export LLM_SENTIMENT_AGENT_MODEL=anthropic.claude-3-haiku-20240307-v1:0
```

## Benefits

1. **Simplified Startup**: Single command to start all services
2. **Automatic Dependency Management**: Services start in correct order
3. **Graceful Shutdown**: Ctrl+C stops all services cleanly
4. **Multiple Options**: Choose between Docker, Bash, or manual startup
5. **Health Checks**: Verify all services are running
6. **Better Logging**: Clear visibility into service status
7. **Development Friendly**: Easy to debug and modify
8. **Production Ready**: Docker Compose for containerized deployment

## Testing

### Verify All Services Running
```bash
curl http://localhost:8000/health
curl http://localhost:8101/health
curl http://localhost:8201/health
```

### Run Property Tests
```bash
cd backend
pytest tests/property/ -v
```

### Test Research Agent A2A
```bash
curl -X POST http://localhost:8101/a2a/research \
  -H "Content-Type: application/json" \
  -d '{
    "task": "portfolio_research",
    "request_id": "test-123",
    "symbols": ["AAPL", "MSFT"],
    "portfolio_request": {"portfolio_id": "PORT-001"}
  }'
```

### Test Sentiment Agent MCP
```bash
curl -X POST http://localhost:8201/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-123",
    "method": "analyze_symbol_news_sentiment",
    "params": {"symbol": "AAPL"}
  }'
```

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process using port
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

### Virtual Environment Issues
```bash
# Remove and recreate virtual environments
rm -rf remote-agents/research-agent/venv
rm -rf mcp-servers/sentiment/venv
./backend/scripts/run_all_services.sh local
```

### Docker Issues
```bash
# Rebuild and restart
docker-compose build --no-cache
docker-compose up
```

## Files Added/Modified

### New Files
1. `backend/scripts/run_all_services.sh` - Alternative startup script
2. `remote-agents/research-agent/Dockerfile` - Research Agent container
3. `mcp-servers/sentiment/Dockerfile` - Sentiment Agent container
4. `docker-compose.yml` - Docker Compose orchestration
5. `STARTUP_GUIDE.md` - Comprehensive startup documentation
6. `DEPLOYMENT_UPDATES.md` - This file

### Modified Files
1. `backend/scripts/run_backend.sh` - Updated to start all services

## Next Steps

1. **Test Startup**: Run `./backend/scripts/run_all_services.sh local` and verify all services start
2. **Verify Health**: Check all health endpoints
3. **Run Tests**: Execute property tests to verify functionality
4. **Enable LLM**: Set feature flags to enable LLM for specific agents
5. **Deploy**: Use Docker Compose for production deployment

## Documentation

- See `STARTUP_GUIDE.md` for detailed startup instructions
- See `FINAL_SUMMARY.md` for project overview
- See `README_LLM_INTEGRATION.md` for quick start guide
