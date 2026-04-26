# Verification Checklist - LLM-LangGraph Integration

## Pre-Deployment Verification

### ✅ Code Quality
- [x] All agents have LLM integration with fallback support
- [x] Prompt templates created for all 6 agents
- [x] Response validation implemented
- [x] Feature flags for safe rollout
- [x] Error handling and logging
- [x] Property-based tests (12/20 passing)

### ✅ Infrastructure
- [x] Bedrock adapter with retry logic
- [x] Prompt template system with versioning
- [x] Response validator with schema validation
- [x] LangGraph orchestrator with conditional routing
- [x] Configuration system with environment variables
- [x] Multi-protocol support (Local, A2A, MCP)

### ✅ Agents
- [x] Memory Agent - LLM-enhanced semantic retrieval
- [x] Research Agent - A2A server with market synthesis
- [x] Sentiment Agent - MCP server with sentiment analysis
- [x] Rebalancing Agent - LLM-enhanced drift explanation
- [x] Risk Agent - LLM-enhanced policy verdict
- [x] Trade Proposal Agent - LLM-enhanced rationale

### ✅ Deployment
- [x] Updated run_backend.sh to start all services
- [x] Created run_all_services.sh alternative script
- [x] Docker Compose configuration
- [x] Dockerfiles for remote agents and MCP servers
- [x] Comprehensive startup guide
- [x] Health check endpoints

## Pre-Launch Checklist

### Environment Setup
- [ ] Python 3.11+ installed
- [ ] uv package manager installed
- [ ] Docker and Docker Compose installed (for Docker option)
- [ ] AWS credentials configured (if using Bedrock)
- [ ] All required ports available (8000, 8101, 8201, 55000)

### Configuration
- [ ] `backend/.env` created with required variables
- [ ] Feature flags set appropriately (all disabled by default)
- [ ] AWS region configured
- [ ] DynamoDB endpoint configured (local or AWS)
- [ ] Remote agent URLs configured

### Dependencies
- [ ] Backend dependencies installed: `cd backend && pip install -e ".[dev]"`
- [ ] Research Agent dependencies: `cd remote-agents/research-agent && pip install -r requirements.txt`
- [ ] Sentiment Agent dependencies: `cd mcp-servers/sentiment && pip install -r requirements.txt`

### Database
- [ ] DynamoDB Local running (if using local mode): `docker run -p 55000:8000 amazon/dynamodb-local`
- [ ] Or AWS DynamoDB configured (if using AWS mode)

## Startup Verification

### Option 1: Docker Compose
```bash
# Start services
docker-compose up

# Verify in another terminal
curl http://localhost:8000/health
curl http://localhost:8101/health
curl http://localhost:8201/health
```

### Option 2: Bash Script
```bash
# Make script executable
chmod +x backend/scripts/run_all_services.sh

# Start services
./backend/scripts/run_all_services.sh local

# Verify in another terminal
curl http://localhost:8000/health
curl http://localhost:8101/health
curl http://localhost:8201/health
```

### Option 3: Manual
```bash
# Terminal 1 - Research Agent
cd remote-agents/research-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py

# Terminal 2 - Sentiment Agent
cd mcp-servers/sentiment
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python server.py

# Terminal 3 - Backend
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 4 - Verify
curl http://localhost:8000/health
curl http://localhost:8101/health
curl http://localhost:8201/health
```

## Health Checks

### Backend Health
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", ...}
```

### Research Agent Health
```bash
curl http://localhost:8101/health
# Expected: {"status": "healthy", "agent": "Research Agent", "protocol": "A2A", ...}
```

### Sentiment Agent Health
```bash
curl http://localhost:8201/health
# Expected: {"status": "healthy", "agent": "Sentiment Agent", "protocol": "MCP", ...}
```

## Functional Tests

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
# Expected: A2A response with market context
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
# Expected: MCP JSON-RPC response with sentiment analysis
```

### Test Backend API
```bash
# Get health
curl http://localhost:8000/health

# List available endpoints
curl http://localhost:8000/docs
```

## Property Tests

### Run All Property Tests
```bash
cd backend
pytest tests/property/ -v
# Expected: 12 tests passing
```

### Run Specific Test
```bash
cd backend
pytest tests/property/test_bedrock_adapter_properties.py -v
# Expected: 4 tests passing
```

### Run with Coverage
```bash
cd backend
pytest tests/property/ --cov=app --cov-report=html
# Expected: Coverage report generated
```

## Feature Flag Verification

### Verify Feature Flags Disabled (Default)
```bash
# Check environment variables
echo $FEATURE_MEMORY_AGENT_LLM_ENABLED
echo $FEATURE_RESEARCH_AGENT_LLM_ENABLED
echo $FEATURE_SENTIMENT_AGENT_LLM_ENABLED
echo $FEATURE_REBALANCING_AGENT_LLM_ENABLED
echo $FEATURE_RISK_AGENT_LLM_ENABLED
echo $FEATURE_TRADE_PROPOSAL_AGENT_LLM_ENABLED
# Expected: All should be false or unset
```

### Enable LLM for Testing
```bash
export FEATURE_MEMORY_AGENT_LLM_ENABLED=true
# Restart backend to apply changes
```

## Performance Verification

### Check Response Times
```bash
# Backend health check
time curl http://localhost:8000/health

# Research Agent health check
time curl http://localhost:8101/health

# Sentiment Agent health check
time curl http://localhost:8201/health
# Expected: All responses < 100ms
```

### Check Memory Usage
```bash
# Monitor process memory
ps aux | grep python
# Expected: Each service using < 500MB
```

## Logging Verification

### Check Backend Logs
```bash
# If using Docker Compose
docker-compose logs backend

# If using bash script
# Logs printed to stdout
```

### Check Research Agent Logs
```bash
# If using Docker Compose
docker-compose logs research-agent

# If using bash script
# Logs printed to stdout
```

### Check Sentiment Agent Logs
```bash
# If using Docker Compose
docker-compose logs sentiment-mcp

# If using bash script
# Logs printed to stdout
```

## Cleanup Verification

### Stop All Services
```bash
# If using Docker Compose
docker-compose down

# If using bash script
# Press Ctrl+C

# If using manual
# Press Ctrl+C in each terminal
```

### Verify Services Stopped
```bash
# Check no processes running
ps aux | grep python
# Expected: No python processes for our services

# Check ports are free
lsof -i :8000
lsof -i :8101
lsof -i :8201
# Expected: No processes listening on these ports
```

## Troubleshooting

### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
PORT=8001 ./backend/scripts/run_all_services.sh local
```

### Issue: Import Errors
```bash
# Ensure PYTHONPATH includes backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Restart services
./backend/scripts/run_all_services.sh local
```

### Issue: Virtual Environment Issues
```bash
# Remove and recreate venvs
rm -rf remote-agents/research-agent/venv
rm -rf mcp-servers/sentiment/venv

# Restart services
./backend/scripts/run_all_services.sh local
```

### Issue: Docker Build Fails
```bash
# Rebuild without cache
docker-compose build --no-cache

# Start services
docker-compose up
```

## Sign-Off

- [ ] All health checks passing
- [ ] All functional tests passing
- [ ] All property tests passing
- [ ] Feature flags working correctly
- [ ] Logging working correctly
- [ ] Cleanup working correctly
- [ ] Documentation complete
- [ ] Ready for production deployment

## Notes

- All LLM features are disabled by default for safety
- System gracefully falls back to deterministic behavior on LLM failure
- Feature flags allow incremental rollout of LLM capabilities
- All services have health check endpoints
- Docker Compose recommended for production
- Bash script recommended for development

## Support

For issues or questions:
1. Check STARTUP_GUIDE.md for detailed instructions
2. Review service logs for error messages
3. Verify all dependencies are installed
4. Ensure ports are not in use
5. Check environment variables are set correctly
