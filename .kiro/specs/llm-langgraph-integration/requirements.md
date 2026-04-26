# Requirements Document: LLM-LangGraph Integration

## Introduction

This feature transforms the current hardcoded multi-agent portfolio management system into a production-quality LangGraph-based agentic AI solution with AWS Bedrock LLM integration. The current implementation uses sequential function calls with deterministic, rule-based logic and stub adapters. The desired state is a true agentic AI system where LangGraph orchestrates workflow state and conditional routing, while LLMs provide intelligent reasoning, natural language explanations, and contextual analysis for each specialist agent.

## Glossary

- **LangGraph**: A framework for building stateful, multi-agent workflows with explicit graph state, conditional routing, and retry control
- **Bedrock**: AWS managed service providing access to foundation models (Claude, Titan, etc.) through a unified API
- **Agent**: A specialist component that performs a bounded task using LLM reasoning and returns structured results
- **Orchestrator**: The LangGraph-based workflow engine that coordinates agent execution and manages state transitions
- **Model_Adapter**: The interface layer between agents and Bedrock LLM APIs
- **State_Graph**: The LangGraph state machine that defines nodes, edges, and conditional routing logic
- **Agent_Node**: A LangGraph node that wraps an agent's execution logic
- **Guardrails**: AWS Bedrock safety controls that filter harmful content, enforce policies, and validate grounding
- **Evidence**: Source data, references, or context that supports an agent's reasoning or conclusions
- **Prompt_Template**: A structured template that formats agent inputs for LLM consumption
- **Fallback_Behavior**: Local deterministic logic used when LLM services are unavailable
- **Trace_Provider**: The observability backend (Bedrock AgentCore or LangSmith) for workflow tracing
- **Memory_Agent**: Agent that retrieves and synthesizes relevant client context using LLM reasoning
- **Research_Agent**: Agent that synthesizes market research and provides contextual analysis using LLMs
- **Sentiment_Agent**: Agent that analyzes news sentiment and market psychology using LLMs
- **Rebalancing_Agent**: Agent that explains portfolio drift and recommends rebalancing strategies using LLMs
- **Risk_Agent**: Agent that provides natural language policy explanations using LLMs
- **Trade_Proposal_Agent**: Agent that generates detailed trade proposals with LLM-backed rationale
- **Approval_Workflow_Agent**: Agent that manages human approval workflow and decision tracking

## Requirements

### Requirement 1: LangGraph State Graph Implementation

**User Story:** As a platform developer, I want LangGraph to orchestrate the multi-agent workflow with explicit state management, so that execution is predictable, traceable, and supports conditional routing.

#### Acceptance Criteria

1. THE State_Graph SHALL define all agent nodes as explicit LangGraph nodes with typed input and output contracts
2. THE State_Graph SHALL implement conditional edges for policy-based routing (compliant vs non-compliant, blocked vs degraded)
3. THE State_Graph SHALL maintain workflow state including correlation metadata, agent outputs, quality indicators, and final recommendation
4. WHEN validation fails, THE State_Graph SHALL route to audit emission and error response without executing downstream agents
5. WHEN policy verdict is NON_COMPLIANT or UNRESOLVED, THE State_Graph SHALL skip trade proposal generation and mark workflow as BLOCKED
6. WHEN guardrails hard-block output, THE State_Graph SHALL mark workflow as BLOCKED and return GUARDRAIL_VIOLATION
7. THE State_Graph SHALL support parallel execution for independent agents (memory retrieval and research)
8. THE State_Graph SHALL preserve all agent outputs in state for downstream consumption and audit trails

### Requirement 2: Bedrock Model Adapter Implementation

**User Story:** As a platform developer, I want a production-ready Bedrock adapter that replaces stub implementations, so that agents can invoke LLMs for reasoning and explanation.

#### Acceptance Criteria

1. THE Model_Adapter SHALL invoke AWS Bedrock APIs using boto3 with proper authentication and error handling
2. THE Model_Adapter SHALL support multiple foundation models (Claude, Titan) through configuration
3. THE Model_Adapter SHALL implement retry logic with exponential backoff for transient failures
4. THE Model_Adapter SHALL implement timeout controls to prevent indefinite blocking
5. WHEN Bedrock API calls fail, THE Model_Adapter SHALL return structured errors with failure reason and context
6. THE Model_Adapter SHALL log all LLM invocations with request metadata, model identifier, token usage, and latency
7. THE Model_Adapter SHALL support streaming responses for long-running LLM generations
8. THE Model_Adapter SHALL validate LLM responses against expected schema before returning to agents

### Requirement 3: Research Agent LLM Integration

**User Story:** As a personal investor, I want the Research Agent to use LLMs to synthesize market research and provide contextual analysis, so that recommendations reflect intelligent interpretation of market conditions.

#### Acceptance Criteria

1. THE Research_Agent SHALL use LLMs to generate market context summaries from retrieved market data
2. THE Research_Agent SHALL include evidence references for all material claims in LLM-generated summaries
3. THE Research_Agent SHALL distinguish retrieved facts from LLM-derived interpretation in output metadata
4. THE Research_Agent SHALL use prompt templates that instruct LLMs to provide confidence levels and cite sources
5. WHEN market data is incomplete, THE Research_Agent SHALL use LLMs to identify gaps and recommend degraded handling
6. THE Research_Agent SHALL validate LLM outputs for grounding against provided evidence before returning results
7. WHEN LLM services are unavailable, THE Research_Agent SHALL fall back to local deterministic behavior
8. THE Research_Agent SHALL emit trace spans for LLM invocations with prompt hash, model identifier, and token usage

### Requirement 4: Sentiment Analysis Agent LLM Integration

**User Story:** As a personal investor, I want the Sentiment Agent to use LLMs to analyze news sentiment and market psychology, so that recommendations account for qualitative market factors.

#### Acceptance Criteria

1. THE Sentiment_Agent SHALL use LLMs to analyze news articles and generate sentiment scores with natural language explanations
2. THE Sentiment_Agent SHALL provide confidence levels for sentiment classifications (positive, negative, neutral)
3. THE Sentiment_Agent SHALL identify key themes and psychological factors from news content using LLM reasoning
4. THE Sentiment_Agent SHALL cite specific news sources and quotes as evidence for sentiment conclusions
5. WHEN news data is unavailable, THE Sentiment_Agent SHALL use LLMs to explain the limitation and recommend neutral sentiment
6. THE Sentiment_Agent SHALL validate LLM sentiment outputs against configured sentiment ranges before returning results
7. WHEN LLM services are unavailable, THE Sentiment_Agent SHALL fall back to neutral sentiment with local explanation
8. THE Sentiment_Agent SHALL emit trace spans for LLM invocations with sentiment classification metadata

### Requirement 5: Portfolio Rebalancing Agent LLM Integration

**User Story:** As a personal investor, I want the Rebalancing Agent to use LLMs to explain portfolio drift and recommend rebalancing strategies, so that I understand the rationale behind recommendations.

#### Acceptance Criteria

1. THE Rebalancing_Agent SHALL use LLMs to generate natural language explanations of allocation drift
2. THE Rebalancing_Agent SHALL use LLMs to recommend rebalancing strategies based on drift magnitude, risk profile, and market context
3. THE Rebalancing_Agent SHALL provide confidence levels for rebalancing recommendations
4. THE Rebalancing_Agent SHALL cite specific drift metrics and policy thresholds as evidence for recommendations
5. WHEN drift is within tolerance, THE Rebalancing_Agent SHALL use LLMs to explain why no action is needed
6. THE Rebalancing_Agent SHALL validate LLM recommendations against deterministic drift calculations before returning results
7. WHEN LLM services are unavailable, THE Rebalancing_Agent SHALL fall back to deterministic drift calculation with template explanations
8. THE Rebalancing_Agent SHALL emit trace spans for LLM invocations with drift analysis metadata

### Requirement 6: Risk and Compliance Agent LLM Integration

**User Story:** As a personal investor, I want the Risk Agent to use LLMs to provide natural language policy explanations, so that I understand why recommendations are compliant or blocked.

#### Acceptance Criteria

1. THE Risk_Agent SHALL use LLMs to generate natural language explanations of policy verdicts (COMPLIANT, NON_COMPLIANT, UNRESOLVED)
2. THE Risk_Agent SHALL use LLMs to explain specific policy violations with references to violated rules
3. THE Risk_Agent SHALL provide confidence levels for policy interpretations when rules are ambiguous
4. THE Risk_Agent SHALL cite specific policy rules, drift metrics, and risk indicators as evidence for verdicts
5. WHEN policy verdict is NON_COMPLIANT, THE Risk_Agent SHALL use LLMs to recommend corrective actions
6. THE Risk_Agent SHALL validate LLM explanations against deterministic policy evaluation results before returning
7. WHEN LLM services are unavailable, THE Risk_Agent SHALL fall back to deterministic policy evaluation with template explanations
8. THE Risk_Agent SHALL emit trace spans for LLM invocations with policy verdict metadata

### Requirement 7: Trade Execution Proposal Agent LLM Integration

**User Story:** As a personal investor, I want the Trade Proposal Agent to use LLMs to generate detailed trade proposals with rationale, so that I can make informed approval decisions.

#### Acceptance Criteria

1. THE Trade_Proposal_Agent SHALL use LLMs to generate structured trade proposals with natural language rationale
2. THE Trade_Proposal_Agent SHALL use LLMs to explain estimated impact on allocations, costs, and tax considerations
3. THE Trade_Proposal_Agent SHALL provide confidence levels for trade recommendations
4. THE Trade_Proposal_Agent SHALL cite policy verdicts, drift metrics, and market context as evidence for proposals
5. WHEN policy blocks proposal generation, THE Trade_Proposal_Agent SHALL use LLMs to explain why no proposal is possible
6. THE Trade_Proposal_Agent SHALL validate LLM proposals against policy gates and allocation constraints before returning
7. WHEN LLM services are unavailable, THE Trade_Proposal_Agent SHALL fall back to template-based proposal generation
8. THE Trade_Proposal_Agent SHALL emit trace spans for LLM invocations with proposal generation metadata

### Requirement 8: Memory and Personalization Agent LLM Integration

**User Story:** As a personal investor, I want the Memory Agent to use LLMs to retrieve and synthesize relevant client context, so that recommendations are personalized and consistent with my history.

#### Acceptance Criteria

1. THE Memory_Agent SHALL use LLMs to generate semantic queries for memory retrieval based on current request context
2. THE Memory_Agent SHALL use LLMs to synthesize retrieved memory items into coherent client context summaries
3. THE Memory_Agent SHALL identify conflicts between retrieved memory and current request using LLM reasoning
4. THE Memory_Agent SHALL provide confidence levels for memory relevance and conflict detection
5. WHEN memory retrieval returns no results, THE Memory_Agent SHALL use LLMs to explain the absence and recommend fallback behavior
6. THE Memory_Agent SHALL validate LLM memory summaries against retrieved memory items for accuracy before returning
7. WHEN LLM services are unavailable, THE Memory_Agent SHALL fall back to keyword-based memory retrieval with template summaries
8. THE Memory_Agent SHALL emit trace spans for LLM invocations with memory retrieval and synthesis metadata

### Requirement 9: Prompt Engineering and Template Management

**User Story:** As a platform developer, I want structured prompt templates for each agent, so that LLM interactions are consistent, maintainable, and produce reliable outputs.

#### Acceptance Criteria

1. THE System SHALL define prompt templates for each agent with clear instructions, input formatting, and output expectations
2. THE System SHALL include few-shot examples in prompt templates to guide LLM behavior
3. THE System SHALL use prompt templates that instruct LLMs to provide confidence levels, evidence citations, and structured outputs
4. THE System SHALL version prompt templates and track which version was used for each LLM invocation
5. THE System SHALL validate prompt template inputs before LLM invocation to prevent injection attacks
6. THE System SHALL support prompt template overrides through configuration for testing and experimentation
7. THE System SHALL log prompt template identifiers and versions in trace spans for debugging
8. THE System SHALL maintain prompt template documentation with usage guidelines and expected outputs

### Requirement 10: LLM Response Validation and Grounding

**User Story:** As a safety reviewer, I want LLM outputs validated for grounding and accuracy, so that ungrounded or hallucinated content does not reach users.

#### Acceptance Criteria

1. THE System SHALL validate LLM outputs against provided evidence before accepting results
2. THE System SHALL reject LLM outputs that make unsupported claims without evidence citations
3. THE System SHALL use Bedrock guardrails to check grounding for recommendation-bearing outputs
4. THE System SHALL flag LLM outputs with low confidence scores for human review
5. WHEN LLM outputs fail grounding checks, THE System SHALL request regeneration with stricter grounding instructions
6. THE System SHALL log all grounding validation results with pass/fail status and violation details
7. THE System SHALL support configurable grounding thresholds per agent based on risk tolerance
8. THE System SHALL emit metrics for grounding validation pass rates and failure reasons

### Requirement 11: Fallback Behavior and Resilience

**User Story:** As a platform operator, I want graceful fallback behavior when LLM services are unavailable, so that the system remains operational during outages.

#### Acceptance Criteria

1. WHEN Bedrock API calls fail with transient errors, THE System SHALL retry with exponential backoff up to configured limits
2. WHEN Bedrock API calls fail with permanent errors, THE System SHALL fall back to local deterministic behavior
3. THE System SHALL log all fallback activations with failure reason and fallback mode used
4. THE System SHALL mark workflow state as DEGRADED when fallback behavior is used
5. THE System SHALL include fallback mode indicators in agent stage results for transparency
6. THE System SHALL support configuration of fallback behavior per agent (fail-fast vs graceful degradation)
7. THE System SHALL emit metrics for fallback activation rates and reasons
8. THE System SHALL test fallback behavior in automated test suites to ensure correctness

### Requirement 12: Observability and Tracing for LLM Invocations

**User Story:** As a platform operator, I want detailed tracing for all LLM invocations, so that I can monitor performance, debug issues, and optimize costs.

#### Acceptance Criteria

1. THE System SHALL emit trace spans for every LLM invocation with model identifier, prompt hash, and token usage
2. THE System SHALL correlate LLM trace spans with agent execution spans and workflow trace identifiers
3. THE System SHALL log LLM invocation latency, token counts (input and output), and cost estimates
4. THE System SHALL emit metrics for LLM invocation success rates, error rates, and latency percentiles
5. THE System SHALL support trace provider abstraction so LangSmith and Bedrock AgentCore can be used interchangeably
6. THE System SHALL include LLM response metadata (confidence, grounding status, validation results) in trace spans
7. THE System SHALL support sampling of LLM prompts and responses for debugging without logging all content
8. THE System SHALL emit alarms when LLM error rates or latency exceed configured thresholds

### Requirement 13: Configuration and Environment Management

**User Story:** As a platform operator, I want environment-based configuration for LLM integration, so that I can control model selection, timeouts, and fallback behavior per environment.

#### Acceptance Criteria

1. THE System SHALL support configuration of Bedrock model identifiers per agent through environment variables
2. THE System SHALL support configuration of LLM timeout values per agent through environment variables
3. THE System SHALL support configuration of retry limits and backoff parameters through environment variables
4. THE System SHALL support configuration of fallback behavior (enabled/disabled) per agent through environment variables
5. THE System SHALL support configuration of prompt template versions through environment variables
6. THE System SHALL validate all configuration values at startup and fail fast with clear error messages for invalid configs
7. THE System SHALL support local development mode with mock LLM responses for testing without AWS credentials
8. THE System SHALL document all configuration parameters with default values and usage guidelines

### Requirement 14: Cost Management and Token Optimization

**User Story:** As a platform operator, I want to monitor and optimize LLM token usage, so that I can control costs while maintaining quality.

#### Acceptance Criteria

1. THE System SHALL log token usage (input and output) for every LLM invocation
2. THE System SHALL emit metrics for total token usage per agent, per workflow, and per time period
3. THE System SHALL estimate costs based on token usage and model pricing
4. THE System SHALL support configurable token limits per LLM invocation to prevent runaway costs
5. WHEN token limits are exceeded, THE System SHALL truncate inputs or fail gracefully with clear error messages
6. THE System SHALL optimize prompt templates to minimize token usage while maintaining output quality
7. THE System SHALL support caching of LLM responses for identical inputs to reduce redundant invocations
8. THE System SHALL emit alarms when token usage or estimated costs exceed configured budgets

### Requirement 15: Testing and Validation Framework

**User Story:** As a platform developer, I want comprehensive testing for LLM-integrated agents, so that I can validate correctness and prevent regressions.

#### Acceptance Criteria

1. THE System SHALL include unit tests for each agent with mocked LLM responses
2. THE System SHALL include integration tests that invoke real Bedrock APIs in test environments
3. THE System SHALL include tests for fallback behavior when LLM services are unavailable
4. THE System SHALL include tests for LLM response validation and grounding checks
5. THE System SHALL include tests for prompt template rendering and input validation
6. THE System SHALL include tests for error handling and retry logic in Model_Adapter
7. THE System SHALL include tests for LangGraph state transitions and conditional routing
8. THE System SHALL maintain test coverage above 80% for all LLM integration code

### Requirement 16: Migration Strategy and Backward Compatibility

**User Story:** As a platform operator, I want a phased migration from hardcoded logic to LLM integration, so that I can validate each agent independently without breaking existing functionality.

#### Acceptance Criteria

1. THE System SHALL support feature flags to enable/disable LLM integration per agent
2. THE System SHALL preserve existing API contracts and response schemas during migration
3. THE System SHALL support side-by-side execution of old and new agent implementations for comparison
4. THE System SHALL log differences between hardcoded and LLM-generated outputs for validation
5. THE System SHALL support rollback to hardcoded implementations if LLM integration causes issues
6. THE System SHALL migrate agents in priority order (Research, Sentiment, Rebalancing, Risk, Trade Proposal, Memory)
7. THE System SHALL validate that LLM-integrated agents produce equivalent or better outputs than hardcoded versions
8. THE System SHALL document migration status and validation results for each agent

### Requirement 17: Security and Data Privacy

**User Story:** As a security reviewer, I want LLM integration to protect sensitive data and prevent prompt injection attacks, so that client information remains secure.

#### Acceptance Criteria

1. THE System SHALL sanitize all user inputs before including them in LLM prompts
2. THE System SHALL validate prompt templates to prevent injection of malicious instructions
3. THE System SHALL redact sensitive information (account numbers, SSNs, credentials) from LLM prompts and logs
4. THE System SHALL use AWS IAM roles and policies to control access to Bedrock APIs
5. THE System SHALL encrypt LLM prompts and responses in transit using TLS
6. THE System SHALL not log full LLM prompts or responses containing sensitive data
7. THE System SHALL audit all LLM invocations with correlation identifiers for security review
8. THE System SHALL comply with data retention policies for LLM interaction logs

### Requirement 18: Parser and Serializer Requirements for LLM Outputs

**User Story:** As a platform developer, I want robust parsing of LLM-generated structured outputs, so that agent results are reliable and type-safe.

#### Acceptance Criteria

1. WHEN an LLM generates structured output (JSON, YAML), THE Parser SHALL parse it into typed domain objects
2. WHEN parsing fails, THE Parser SHALL return descriptive errors with line numbers and context
3. THE Pretty_Printer SHALL format typed domain objects back into LLM-consumable structured formats
4. FOR ALL valid typed domain objects, parsing then printing then parsing SHALL produce equivalent objects (round-trip property)
5. THE System SHALL validate parsed LLM outputs against Pydantic schemas before accepting results
6. THE System SHALL retry LLM invocations with corrected prompts when parsing fails
7. THE System SHALL log parsing failures with LLM response content for debugging
8. THE System SHALL emit metrics for LLM output parsing success rates and failure reasons
