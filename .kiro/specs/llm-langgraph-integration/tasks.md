# Implementation Plan: LLM-LangGraph Integration

## Overview

This implementation plan transforms the current hardcoded multi-agent portfolio management system into a production-quality LangGraph-based agentic AI solution with AWS Bedrock LLM integration. The plan follows a phased approach starting with foundation infrastructure, then integrating each agent with LLM capabilities, adding multi-protocol support (local, A2A, MCP), and finally implementing comprehensive testing and observability.

## Tasks

- [x] 1. Foundation Infrastructure Setup
  - [x] 1.1 Create Bedrock adapter with retry logic and timeout controls
    - Implement `BedrockModelAdapter` class in `backend/app/adapters/bedrock.py`
    - Add retry logic with exponential backoff for transient errors
    - Implement timeout controls for standard, extended, and streaming requests
    - Add structured error handling for retryable vs non-retryable errors
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x]* 1.2 Write property test for retry exponential backoff
    - **Property 5: Model Adapter Retry Exponential Backoff**
    - **Validates: Requirements 2.3, 11.1**
  
  - [x]* 1.3 Write property test for timeout enforcement
    - **Property 6: Model Adapter Timeout Enforcement**
    - **Validates: Requirements 2.4**
  
  - [x] 1.4 Create prompt template system with versioning
    - Implement `PromptTemplate` class with template_id, version, and validation
    - Create template registry for loading versioned templates
    - Add input validation to prevent prompt injection
    - Implement template rendering with Jinja2 or similar
    - _Requirements: 9.1, 9.2, 9.4, 9.5_
  
  - [x]* 1.5 Write property test for prompt template input validation
    - **Property 11: Prompt Template Input Validation**
    - **Validates: Requirements 9.5**
  
  - [x] 1.6 Create response validator with schema and grounding checks
    - Implement `ResponseValidator` class with Pydantic schema validation
    - Add grounding validation using Bedrock guardrails API
    - Implement confidence threshold checking
    - Add regeneration logic for failed validations
    - _Requirements: 2.8, 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x]* 1.7 Write property test for schema validation correctness
    - **Property 8: Schema Validation Correctness**
    - **Validates: Requirements 2.8, 10.1, 18.5**
  
  - [x]* 1.8 Write property test for evidence grounding validation
    - **Property 9: Evidence Grounding Validation**
    - **Validates: Requirements 3.2, 3.6, 10.1, 10.2**

- [x] 2. LangGraph State Graph Implementation
  - [x] 2.1 Define workflow state schema
    - Create `WorkflowGraphState` TypedDict with all required fields
    - Add correlation metadata, agent outputs, quality indicators
    - Define state transitions and validation rules
    - _Requirements: 1.3, 1.8_
  
  - [x] 2.2 Implement validation and initialization nodes
    - Create `validate_request` node for schema validation
    - Create `initialize_context_and_trace` node for trace setup
    - Create `log_request_audit_event` node for audit emission
    - _Requirements: 1.1, 1.4_
  
  - [x] 2.3 Implement conditional routing logic
    - Create `route_after_validation` for validation failures
    - Create `route_after_risk_policy` for policy-based routing
    - Create `route_after_guardrails` for guardrail blocks
    - _Requirements: 1.2, 1.4, 1.5, 1.6_
  
  - [x]* 2.4 Write property test for state graph conditional routing
    - **Property 1: State Graph Conditional Routing**
    - **Validates: Requirements 1.2, 1.5**
  
  - [x]* 2.5 Write property test for state accumulation invariant
    - **Property 2: State Accumulation Invariant**
    - **Validates: Requirements 1.3, 1.8**
  
  - [x] 2.6 Implement output processing nodes
    - Create `apply_output_guardrails` node
    - Create `assemble_recommendation` node
    - Create `create_approval_artifact` node
    - Create `persist_workflow_artifacts` node
    - Create `return_response` node
    - _Requirements: 1.6, 1.8_
  
  - [x] 2.7 Wire graph with parallel execution support
    - Define all edges between nodes
    - Configure parallel execution for memory and research agents
    - Add conditional edges for policy routing
    - Test graph compilation and execution
    - _Requirements: 1.7_

- [ ] 3. Checkpoint - Ensure foundation tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Memory Agent LLM Integration
  - [x] 4.1 Create Memory Agent prompt templates
    - Create semantic query generation template
    - Create memory synthesis template
    - Create conflict detection template
    - Add few-shot examples and grounding instructions
    - _Requirements: 8.1, 8.2, 8.3, 9.1, 9.2, 9.3_
  
  - [x] 4.2 Implement LLM-enhanced Memory Agent
    - Create `MemoryAgentLLM` class extending `LLMEnhancedAgent`
    - Implement `generate_semantic_query` method
    - Implement `synthesize_memory_items` method
    - Implement `detect_conflicts` method
    - Add fallback to keyword-based retrieval
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [ ]* 4.3 Write property test for fallback activation on LLM failure
    - **Property 10: Fallback Activation on LLM Failure**
    - **Validates: Requirements 3.7, 11.2, 11.4, 11.5**
  
  - [ ]* 4.4 Write unit tests for Memory Agent
    - Test semantic query generation with mocked LLM
    - Test memory synthesis with various memory items
    - Test conflict detection edge cases
    - Test fallback behavior when LLM unavailable

- [x] 5. Research Agent A2A Integration
  - [x] 5.1 Create Research Agent prompt templates
    - Create market context synthesis template
    - Create evidence citation template
    - Add few-shot examples with confidence levels
    - _Requirements: 3.1, 3.2, 3.4, 9.1, 9.2, 9.3_
  
  - [x] 5.2 Implement remote Research Agent A2A server
    - Create FastAPI endpoint for A2A protocol in `remote-agents/research-agent/`
    - Implement `ResearchAgentLLM` with market context synthesis
    - Add A2A request/response envelope handling
    - Deploy as separate service
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8_
  
  - [x] 5.3 Implement Research Agent A2A client
    - Create `ResearchAgentA2AClient` in orchestrator
    - Implement HTTP POST with JSON envelope
    - Add timeout and error handling
    - Implement fallback to local deterministic behavior
    - _Requirements: 3.7, 11.1, 11.2_
  
  - [ ]* 5.4 Write integration tests for Research Agent A2A
    - Test A2A protocol communication
    - Test timeout handling
    - Test fallback on remote failure
    - Test evidence citation validation

- [x] 6. Sentiment Agent MCP Integration
  - [x] 6.1 Create Sentiment Agent prompt templates
    - Create sentiment analysis template
    - Create theme identification template
    - Add confidence level instructions
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 9.1, 9.2, 9.3_
  
  - [x] 6.2 Implement Sentiment Agent MCP server
    - Create MCP server in `mcp-servers/sentiment/`
    - Implement `analyze_symbol_news_sentiment` tool
    - Add JSON-RPC 2.0 request/response handling
    - Implement `SentimentAgentLLM` with news analysis
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [x] 6.3 Implement Sentiment Agent MCP client
    - Create `SentimentAgentMCPClient` in orchestrator
    - Implement JSON-RPC tool invocation
    - Add timeout and error handling
    - Implement fallback to neutral sentiment
    - _Requirements: 4.7, 11.1, 11.2_
  
  - [ ]* 6.4 Write integration tests for Sentiment Agent MCP
    - Test MCP JSON-RPC protocol
    - Test tool invocation and response parsing
    - Test fallback on MCP server failure
    - Test sentiment validation

- [ ] 7. Checkpoint - Ensure agent integration tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Rebalancing Agent LLM Integration
  - [ ] 8.1 Create Rebalancing Agent prompt templates
    - Create drift explanation template
    - Create rebalancing strategy recommendation template
    - Add evidence citation for drift metrics
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 9.1, 9.2, 9.3_
  
  - [ ] 8.2 Implement LLM-enhanced Rebalancing Agent
    - Create `RebalancingAgentLLM` class
    - Implement `explain_drift` method with LLM reasoning
    - Implement `recommend_strategy` method
    - Add validation against deterministic drift calculations
    - Implement fallback to template explanations
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8_
  
  - [ ]* 8.3 Write unit tests for Rebalancing Agent
    - Test drift explanation generation
    - Test strategy recommendation validation
    - Test fallback behavior
    - Test validation against deterministic calculations

- [ ] 9. Risk Agent LLM Integration
  - [ ] 9.1 Create Risk Agent prompt templates
    - Create policy verdict explanation template
    - Create corrective action recommendation template
    - Add policy rule citation instructions
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 9.1, 9.2, 9.3_
  
  - [ ] 9.2 Implement LLM-enhanced Risk Agent
    - Create `RiskAgentLLM` class
    - Implement `explain_policy_verdict` method
    - Implement `recommend_corrective_actions` method
    - Add validation against deterministic policy evaluation
    - Implement fallback to template explanations
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  
  - [ ]* 9.3 Write unit tests for Risk Agent
    - Test policy verdict explanations
    - Test corrective action recommendations
    - Test validation against deterministic verdicts
    - Test fallback behavior

- [ ] 10. Trade Proposal Agent LLM Integration
  - [ ] 10.1 Create Trade Proposal Agent prompt templates
    - Create proposal rationale template
    - Create estimated impact explanation template
    - Add evidence citation for policy verdicts and drift
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 9.1, 9.2, 9.3_
  
  - [ ] 10.2 Implement LLM-enhanced Trade Proposal Agent
    - Create `TradeProposalAgentLLM` class
    - Implement `generate_proposal_rationale` method
    - Implement `explain_estimated_impact` method
    - Add validation for allocation math consistency
    - Implement fallback to template-based proposals
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_
  
  - [ ]* 10.3 Write unit tests for Trade Proposal Agent
    - Test proposal rationale generation
    - Test estimated impact validation
    - Test allocation math consistency checks
    - Test fallback behavior

- [ ] 11. Checkpoint - Ensure all agent LLM integrations pass tests
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Observability and Tracing Implementation
  - [ ] 12.1 Create trace provider abstraction
    - Implement `TraceProvider` protocol interface
    - Create `BedrockAgentCoreTraceProvider` implementation
    - Create `LangSmithTraceProvider` implementation
    - Add trace URL generation for both providers
    - _Requirements: 12.1, 12.2, 12.5_
  
  - [ ] 12.2 Implement LLM invocation tracing
    - Add trace span emission for every LLM invocation
    - Include model_id, prompt_hash, token usage in spans
    - Add correlation with workflow trace_id
    - Implement sampling for prompt/response logging
    - _Requirements: 12.1, 12.2, 12.3, 12.6, 12.7_
  
  - [ ]* 12.3 Write property test for comprehensive logging invariant
    - **Property 15: Comprehensive Logging Invariant**
    - **Validates: Requirements 2.6, 3.8, 9.7, 10.6, 11.3, 18.7**
  
  - [ ] 12.4 Implement CloudWatch metrics emission
    - Add metrics for LLM invocations, latency, errors
    - Add metrics for token usage and cost estimates
    - Add metrics for validation pass/fail rates
    - Add metrics for fallback activations
    - _Requirements: 12.4, 14.2, 14.3, 14.7_
  
  - [ ]* 12.5 Write property test for metrics emission completeness
    - **Property 16: Metrics Emission Completeness**
    - **Validates: Requirements 10.8, 11.7, 18.8**
  
  - [ ] 12.6 Create CloudWatch dashboards and alarms
    - Create LLM Operations Dashboard
    - Create Agent Performance Dashboard
    - Configure alarms for error rate, latency, cost, fallback rate
    - _Requirements: 12.8_

- [x] 13. Configuration and Feature Flags
  - [x] 13.1 Create configuration models
    - Implement `LLMIntegrationConfig` with all settings
    - Implement `AgentLLMConfig` for per-agent configuration
    - Implement `FeatureFlags` for agent enable/disable
    - Implement `CostManagementConfig` for budget controls
    - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 14.1, 14.4, 14.5_
  
  - [x] 13.2 Implement configuration validation
    - Add startup validation for all config parameters
    - Validate model IDs against supported models
    - Validate temperature, max_tokens ranges
    - Validate trace provider configuration
    - Fail fast with clear error messages
    - _Requirements: 13.6_
  
  - [x] 13.3 Create local development mode with mocks
    - Implement `MockBedrockAdapter` for local testing
    - Add mock response configuration
    - Support running without AWS credentials
    - _Requirements: 13.7_
  
  - [ ]* 13.4 Write unit tests for configuration validation
    - Test validation of invalid model IDs
    - Test validation of out-of-range parameters
    - Test validation of missing required config
    - Test local development mode

- [ ] 14. Parser and Serializer Implementation
  - [ ] 14.1 Create LLM output parser
    - Implement JSON/YAML parsing with Pydantic validation
    - Add descriptive error messages with line numbers
    - Implement retry logic for parsing failures
    - _Requirements: 18.1, 18.2, 18.6, 18.7_
  
  - [ ]* 14.2 Write property test for parser round-trip identity
    - **Property 17: Parser Round-Trip Identity**
    - **Validates: Requirements 18.3, 18.4**
  
  - [ ]* 14.3 Write property test for parser error descriptiveness
    - **Property 18: Parser Error Descriptiveness**
    - **Validates: Requirements 18.2**
  
  - [ ]* 14.4 Write unit tests for parser
    - Test parsing valid JSON/YAML
    - Test parsing invalid inputs with error messages
    - Test retry logic on parsing failures
    - Test round-trip for all agent output models

- [ ] 15. Security and Data Privacy Implementation
  - [ ] 15.1 Implement input sanitization
    - Create `InputSanitizer` class
    - Add detection for prompt injection patterns
    - Add input validation for template rendering
    - _Requirements: 17.1, 17.2_
  
  - [ ] 15.2 Implement PII redaction
    - Create `PIIRedactor` class
    - Add patterns for SSN, account numbers, emails, phones
    - Apply redaction to all logs and traces
    - _Requirements: 17.3, 17.6_
  
  - [ ] 15.3 Configure IAM policies for Bedrock access
    - Create IAM policy for InvokeModel permissions
    - Restrict to specific model ARNs
    - Add guardrail permissions
    - _Requirements: 17.4_
  
  - [ ]* 15.4 Write unit tests for security features
    - Test prompt injection detection
    - Test PII redaction patterns
    - Test input sanitization edge cases

- [ ] 16. Checkpoint - Ensure observability and security tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Cost Management Implementation
  - [ ] 17.1 Implement token budget manager
    - Create `TokenBudgetManager` class
    - Add daily budget tracking and reset logic
    - Implement budget checking before invocations
    - Emit metrics for budget usage
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.8_
  
  - [ ] 17.2 Implement response caching
    - Create `ResponseCache` class with TTL
    - Generate cache keys from request parameters
    - Add cache hit/miss metrics
    - _Requirements: 14.7_
  
  - [ ]* 17.3 Write unit tests for cost management
    - Test budget tracking and reset
    - Test budget enforcement
    - Test response caching with TTL
    - Test cache key generation

- [ ] 18. Migration and Feature Flag Integration
  - [ ] 18.1 Implement side-by-side comparison logic
    - Create comparison wrapper for agents
    - Run both hardcoded and LLM implementations
    - Log differences for validation
    - _Requirements: 16.3, 16.4, 16.7_
  
  - [ ] 18.2 Wire feature flags into orchestrator
    - Update orchestrator to check feature flags
    - Route to LLM or hardcoded implementation per flag
    - Add fallback on LLM failure
    - _Requirements: 16.1, 16.5_
  
  - [ ] 18.3 Create migration validation tests
    - Test feature flag enable/disable
    - Test side-by-side comparison logging
    - Test rollback to hardcoded implementation
    - _Requirements: 16.5, 16.7_

- [ ] 19. Integration Testing Suite
  - [ ]* 19.1 Write integration test for end-to-end workflow
    - Test complete workflow from request to response
    - Verify all agents execute in correct order
    - Verify state accumulation across agents
    - Verify conditional routing based on policy verdicts
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_
  
  - [ ]* 19.2 Write integration test for Bedrock adapter
    - Test real Bedrock API invocations (with mocks)
    - Test retry logic with transient errors
    - Test timeout enforcement
    - Test structured error responses
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ]* 19.3 Write integration test for guardrails
    - Test guardrail invocation for recommendations
    - Test guardrail blocking behavior
    - Test workflow routing on guardrail blocks
    - _Requirements: 1.6, 10.3_
  
  - [ ]* 19.4 Write integration test for A2A protocol
    - Test Research Agent A2A communication
    - Test timeout and error handling
    - Test fallback on remote failure
    - _Requirements: 3.7, 11.1, 11.2_
  
  - [ ]* 19.5 Write integration test for MCP protocol
    - Test Sentiment Agent MCP communication
    - Test JSON-RPC tool invocation
    - Test fallback on MCP failure
    - _Requirements: 4.7, 11.1, 11.2_

- [ ] 20. Property-Based Testing Suite
  - [ ]* 20.1 Write property test for validation failure short-circuit
    - **Property 3: Validation Failure Short-Circuit**
    - **Validates: Requirements 1.4**
  
  - [ ]* 20.2 Write property test for guardrail block enforcement
    - **Property 4: Guardrail Block Enforcement**
    - **Validates: Requirements 1.6**
  
  - [ ]* 20.3 Write property test for structured error response
    - **Property 7: Structured Error Response**
    - **Validates: Requirements 2.5**
  
  - [ ]* 20.4 Write property test for template version tracking
    - **Property 12: Template Version Tracking**
    - **Validates: Requirements 9.4, 9.7**
  
  - [ ]* 20.5 Write property test for confidence threshold flagging
    - **Property 13: Confidence Threshold Flagging**
    - **Validates: Requirements 10.4**
  
  - [ ]* 20.6 Write property test for grounding failure regeneration
    - **Property 14: Grounding Failure Regeneration**
    - **Validates: Requirements 10.5**
  
  - [ ]* 20.7 Write property test for parsing failure retry
    - **Property 19: Parsing Failure Retry**
    - **Validates: Requirements 18.6**
  
  - [ ]* 20.8 Write property test for multi-model support
    - **Property 20: Multi-Model Support**
    - **Validates: Requirements 2.2**

- [ ] 21. Checkpoint - Ensure all tests pass and coverage meets requirements
  - Ensure all tests pass, ask the user if questions arise.
  - Verify test coverage is above 80% for all LLM integration code
  - Verify all 20 correctness properties have corresponding tests

- [ ] 22. Documentation and Deployment Preparation
  - [ ] 22.1 Create prompt template documentation
    - Document all prompt templates with usage guidelines
    - Document expected outputs and few-shot examples
    - Document versioning strategy
    - _Requirements: 9.8_
  
  - [ ] 22.2 Create configuration documentation
    - Document all environment variables with defaults
    - Document feature flag usage
    - Document model selection rationale
    - _Requirements: 13.8_
  
  - [ ] 22.3 Create migration runbook
    - Document phased rollout plan
    - Document rollback procedures
    - Document monitoring and validation steps
    - _Requirements: 16.6, 16.8_
  
  - [ ] 22.4 Update deployment scripts
    - Add environment variable configuration
    - Add IAM policy deployment
    - Add CloudWatch dashboard deployment
    - Add alarm configuration

- [ ] 23. Final Integration and Validation
  - [ ] 23.1 Deploy to development environment
    - Deploy with all feature flags disabled
    - Verify baseline functionality
    - Enable Memory Agent LLM flag and validate
    - Enable Research Agent LLM flag and validate
    - Enable Sentiment Agent LLM flag and validate
    - Enable Rebalancing Agent LLM flag and validate
    - Enable Risk Agent LLM flag and validate
    - Enable Trade Proposal Agent LLM flag and validate
    - _Requirements: 16.1, 16.2, 16.6_
  
  - [ ] 23.2 Run side-by-side comparison validation
    - Compare LLM outputs with hardcoded outputs
    - Log differences and validate quality
    - Verify LLM outputs meet or exceed hardcoded quality
    - _Requirements: 16.3, 16.4, 16.7_
  
  - [ ] 23.3 Validate observability and monitoring
    - Verify trace spans are emitted correctly
    - Verify metrics are published to CloudWatch
    - Verify dashboards display correct data
    - Verify alarms trigger appropriately
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.8_
  
  - [ ] 23.4 Validate cost management
    - Verify token usage tracking
    - Verify budget enforcement
    - Verify cost estimates are accurate
    - Verify response caching reduces costs
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.7_

- [ ] 24. Final checkpoint - Production readiness validation
  - Ensure all tests pass, ask the user if questions arise.
  - Verify all acceptance criteria are met
  - Verify all correctness properties are validated
  - Verify documentation is complete
  - Verify deployment runbook is tested

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at major milestones
- Property tests validate universal correctness properties from the design
- Unit tests validate specific examples and edge cases
- Integration tests validate interactions with external services
- The implementation uses Python as specified in the design document
- Multi-protocol support (local, A2A, MCP) allows flexible agent deployment
- Feature flags enable phased migration with independent agent validation
- Comprehensive observability ensures production monitoring and debugging
- Cost management prevents runaway LLM expenses
- Security features protect sensitive data and prevent prompt injection
