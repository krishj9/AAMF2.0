"""LangGraph workflow graph definition."""

import logging
from typing import Optional

from langgraph.graph import StateGraph, END

from app.contracts.workflow import OrchestrationResponse, PortfolioRebalanceRequest
from app.services.langgraph_nodes import (
    apply_output_guardrails,
    assemble_recommendation,
    create_approval_artifact,
    emit_workflow_audit_event,
    initialize_context_and_trace,
    log_request_audit_event,
    persist_workflow_artifacts,
    return_response,
    validate_request,
)
from app.services.langgraph_routing import (
    route_after_guardrails,
    route_after_risk_policy,
    route_after_validation,
)
from app.services.langgraph_state import WorkflowGraphState, create_initial_state

logger = logging.getLogger(__name__)


# ============================================================================
# Graph Builder
# ============================================================================


def build_workflow_graph() -> StateGraph:
    """
    Build LangGraph workflow with all nodes and edges.

    Returns:
        Compiled StateGraph ready for execution
    """
    # Create graph
    graph = StateGraph(WorkflowGraphState)

    # ========================================================================
    # Add Nodes
    # ========================================================================

    # Validation and initialization
    graph.add_node("validate_request", validate_request)
    graph.add_node("initialize_context_and_trace", initialize_context_and_trace)
    graph.add_node("log_request_audit_event", log_request_audit_event)

    # Agent execution nodes (placeholders - will be implemented in later phases)
    graph.add_node("hydrate_memory", hydrate_memory_node)
    graph.add_node("run_research", _placeholder_research_node)
    graph.add_node("run_sentiment_analysis", _placeholder_sentiment_node)
    graph.add_node("run_portfolio_rebalancing", _placeholder_rebalancing_node)
    graph.add_node("run_risk_policy", _placeholder_risk_node)
    graph.add_node("generate_execution_proposal", _placeholder_trade_proposal_node)

    # Output processing
    graph.add_node("assemble_recommendation", assemble_recommendation)
    graph.add_node("apply_output_guardrails", apply_output_guardrails)
    graph.add_node("create_approval_artifact", create_approval_artifact)
    graph.add_node("persist_workflow_artifacts", persist_workflow_artifacts)
    graph.add_node("emit_workflow_audit_event", emit_workflow_audit_event)
    graph.add_node("return_response", return_response)

    # ========================================================================
    # Set Entry Point
    # ========================================================================
    graph.set_entry_point("validate_request")

    # ========================================================================
    # Add Edges
    # ========================================================================

    # Validation flow with conditional routing
    graph.add_conditional_edges(
        "validate_request",
        route_after_validation,
        {
            "emit_workflow_audit_event": "emit_workflow_audit_event",
            "initialize_context_and_trace": "initialize_context_and_trace",
        },
    )

    # Initialization flow
    graph.add_edge("initialize_context_and_trace", "log_request_audit_event")

    # Parallel fan-out: memory and research can run in parallel
    graph.add_edge("log_request_audit_event", "hydrate_memory")
    graph.add_edge("log_request_audit_event", "run_research")

    # Both must complete before sentiment
    graph.add_edge("hydrate_memory", "run_sentiment_analysis")
    graph.add_edge("run_research", "run_sentiment_analysis")

    # Sequential agent execution
    graph.add_edge("run_sentiment_analysis", "run_portfolio_rebalancing")
    graph.add_edge("run_portfolio_rebalancing", "run_risk_policy")

    # Conditional routing after risk policy
    graph.add_conditional_edges(
        "run_risk_policy",
        route_after_risk_policy,
        {
            "generate_execution_proposal": "generate_execution_proposal",
            "assemble_recommendation": "assemble_recommendation",
        },
    )

    # Trade proposal to recommendation assembly
    graph.add_edge("generate_execution_proposal", "assemble_recommendation")

    # Recommendation assembly to guardrails
    graph.add_edge("assemble_recommendation", "apply_output_guardrails")

    # Conditional routing after guardrails
    graph.add_conditional_edges(
        "apply_output_guardrails",
        route_after_guardrails,
        {
            "create_approval_artifact": "create_approval_artifact",
            "emit_workflow_audit_event": "emit_workflow_audit_event",
        },
    )

    # Approval artifact to persistence
    graph.add_edge("create_approval_artifact", "persist_workflow_artifacts")

    # Persistence to audit
    graph.add_edge("persist_workflow_artifacts", "emit_workflow_audit_event")

    # Audit to response
    graph.add_edge("emit_workflow_audit_event", "return_response")

    # Response is terminal
    graph.add_edge("return_response", END)

    # ========================================================================
    # Compile Graph
    # ========================================================================
    return graph.compile()


# ============================================================================
# Placeholder Agent Nodes (to be replaced in later phases)
# ============================================================================


async def hydrate_memory_node(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Execute Memory Agent to retrieve and synthesize client context.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with memory output
    """
    logger.info(f"Executing Memory Agent for {state['request_id']}")

    from app.adapters.bedrock import BedrockModelAdapter
    from app.adapters.prompts import PromptTemplateLoader
    from app.adapters.validation import ResponseValidator
    from app.agents.memory import MemoryPersonalizationAgent
    from app.core.config import get_feature_flags
    from app.services.langgraph_state import add_agent_stage

    try:
        # Initialize Memory Agent with LLM support if enabled
        feature_flags = get_feature_flags()
        
        if feature_flags.memory_agent_llm_enabled:
            bedrock_adapter = BedrockModelAdapter()
            prompt_loader = PromptTemplateLoader()
            validator = ResponseValidator()
            
            agent = MemoryPersonalizationAgent(
                bedrock_adapter=bedrock_adapter,
                prompt_loader=prompt_loader,
                validator=validator,
            )
        else:
            agent = MemoryPersonalizationAgent()

        # Execute agent
        stage_result, payload = await agent.run(state["request"])

        # Store output in state
        state["memory_output"] = payload

        # Add stage result
        add_agent_stage(state, stage_result)

        logger.info(f"Memory Agent completed for {state['request_id']}")

    except Exception as e:
        logger.error(f"Memory Agent failed: {e}", exc_info=True)

        from app.agents.base import failed_stage

        # Add failed stage
        stage = failed_stage("Memory Agent", f"Memory retrieval failed: {str(e)}")
        add_agent_stage(state, stage)

        # Store empty output
        state["memory_output"] = {"items": [], "conflicts": []}

    return state


async def _placeholder_research_node(state: WorkflowGraphState) -> WorkflowGraphState:
    """Placeholder for research agent node."""
    logger.info(f"[PLACEHOLDER] Research agent for {state['request_id']}")

    from app.agents.base import completed_stage
    from app.services.langgraph_state import add_agent_stage

    # Placeholder output
    state["research_output"] = {
        "market_context": "Placeholder market context",
        "key_insights": [],
    }

    # Add stage result
    stage = completed_stage(
        "Research Agent", "Placeholder: Research not yet implemented"
    )
    add_agent_stage(state, stage)

    return state


async def _placeholder_sentiment_node(state: WorkflowGraphState) -> WorkflowGraphState:
    """Placeholder for sentiment agent node."""
    logger.info(f"[PLACEHOLDER] Sentiment agent for {state['request_id']}")

    from app.agents.base import completed_stage
    from app.services.langgraph_state import add_agent_stage

    # Placeholder output
    state["sentiment_output"] = {
        "overall_sentiment": "NEUTRAL",
        "symbol_sentiments": [],
    }

    # Add stage result
    stage = completed_stage(
        "Sentiment Agent", "Placeholder: Sentiment analysis not yet implemented"
    )
    add_agent_stage(state, stage)

    return state


async def _placeholder_rebalancing_node(
    state: WorkflowGraphState,
) -> WorkflowGraphState:
    """Placeholder for rebalancing agent node."""
    logger.info(f"[PLACEHOLDER] Rebalancing agent for {state['request_id']}")

    from app.agents.base import completed_stage
    from app.services.langgraph_state import add_agent_stage
    from app.services.portfolio import calculate_asset_allocation, calculate_drift

    request = state["request"]

    # Use existing deterministic logic
    current_allocation = calculate_asset_allocation(request.portfolio_snapshot)
    drift = calculate_drift(request.portfolio_snapshot, request.allocation_target)

    state["rebalancing_output"] = {
        "current_allocation": current_allocation,
        "target_allocation": request.allocation_target.asset_class_targets,
        "drift": drift,
    }

    # Add stage result
    out_of_tolerance = [item for item in drift if not item.within_tolerance]
    stage = completed_stage(
        "Portfolio Rebalancing Agent",
        f"Calculated allocation drift with {len(out_of_tolerance)} target(s) outside tolerance.",
    )
    add_agent_stage(state, stage)

    return state


async def _placeholder_risk_node(state: WorkflowGraphState) -> WorkflowGraphState:
    """Placeholder for risk agent node."""
    logger.info(f"[PLACEHOLDER] Risk agent for {state['request_id']}")

    from app.agents.base import completed_stage
    from app.services.langgraph_state import add_agent_stage
    from app.services.policy import evaluate_policy

    request = state["request"]
    drift = state.get("rebalancing_output", {}).get("drift", [])

    # Use existing deterministic logic
    result = evaluate_policy(request.portfolio_snapshot, drift, request.risk_profile)

    state["risk_policy_output"] = result

    # Add stage result
    stage = completed_stage("Risk & Compliance Agent", f"Policy verdict: {result.verdict}.")
    add_agent_stage(state, stage)

    return state


async def _placeholder_trade_proposal_node(
    state: WorkflowGraphState,
) -> WorkflowGraphState:
    """Placeholder for trade proposal agent node."""
    logger.info(f"[PLACEHOLDER] Trade proposal agent for {state['request_id']}")

    from app.agents.base import completed_stage
    from app.services.langgraph_state import add_agent_stage

    risk_policy = state.get("risk_policy_output")

    # Simple placeholder logic
    if risk_policy and risk_policy.verdict.value == "COMPLIANT":
        proposal_status = "READY_FOR_REVIEW"
        summary = "Trade proposal generated and ready for review."
    else:
        proposal_status = "BLOCKED"
        summary = "Trade proposal blocked by policy."

    state["trade_proposal_output"] = {
        "proposal_status": proposal_status,
        "estimated_impact": state.get("rebalancing_output", {}).get("current_allocation", {}),
    }

    # Add stage result
    stage = completed_stage("Trade Execution Proposal Agent", summary)
    add_agent_stage(state, stage)

    return state


# ============================================================================
# Orchestrator Class
# ============================================================================


class LangGraphOrchestrator:
    """LangGraph-based orchestrator for portfolio rebalancing workflow."""

    def __init__(self):
        """Initialize orchestrator with compiled graph."""
        self.graph = build_workflow_graph()
        logger.info("LangGraph orchestrator initialized")

    async def run(self, request: PortfolioRebalanceRequest) -> OrchestrationResponse:
        """
        Execute workflow for portfolio rebalance request.

        Args:
            request: Portfolio rebalance request

        Returns:
            Orchestration response with recommendation and approval artifact
        """
        logger.info(f"Starting workflow for request {request.correlation.request_id}")

        # Create initial state
        initial_state = create_initial_state(request)

        # Execute graph
        final_state = await self.graph.ainvoke(initial_state)

        # Build response
        response = OrchestrationResponse(
            correlation=request.correlation,
            version=request.version,
            workflow_state=final_state.get("workflow_state"),
            recommendation_package=final_state.get("recommendation_package"),
            approval_artifact=final_state.get("approval_artifact"),
        )

        logger.info(
            f"Workflow completed for {request.correlation.request_id} "
            f"with state {response.workflow_state}"
        )

        return response
