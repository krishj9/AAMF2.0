"""LangGraph workflow nodes."""

import logging
from datetime import datetime

from app.contracts.analysis import PolicyVerdictStatus
from app.contracts.common import WorkflowState
from app.services.langgraph_state import (
    WorkflowGraphState,
    add_agent_stage,
    add_audit_event_id,
    add_blocker,
    add_degraded_reason,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Validation and Initialization Nodes
# ============================================================================


async def validate_request(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Validate request schema and business rules.

    Args:
        state: Current workflow state

    Returns:
        Updated state with validation results
    """
    logger.info(f"Validating request {state['request_id']}")

    request = state["request"]

    # Basic validation (schema validation happens at API layer)
    errors = []

    # Validate allocation targets sum to 100%
    if hasattr(request, "allocation_target"):
        total = sum(request.allocation_target.asset_class_targets.values())
        if abs(total - 1.0) > 0.01:  # Allow 1% tolerance
            errors.append(f"Allocation targets sum to {total:.2%}, expected 100%")

    # Validate holdings have positive quantities
    if hasattr(request, "portfolio_snapshot"):
        for holding in request.portfolio_snapshot.holdings:
            if holding.quantity <= 0:
                errors.append(f"Invalid quantity for {holding.symbol}: {holding.quantity}")

    if errors:
        state["validation_error"] = {"errors": errors, "timestamp": datetime.now().isoformat()}
        state["workflow_state"] = WorkflowState.BLOCKED
        add_blocker(state, "Request validation failed")

    return state


async def initialize_context_and_trace(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Initialize tracing context and correlation metadata.

    Args:
        state: Current workflow state

    Returns:
        Updated state with trace context
    """
    logger.info(f"Initializing trace context for {state['request_id']}")

    # Initialize trace provider (placeholder - actual implementation would use real provider)
    trace_provider = state.get("trace_provider", "bedrock_agentcore")

    # Generate trace URL (placeholder)
    if trace_provider == "bedrock_agentcore":
        state["provider_trace_url"] = (
            f"https://console.aws.amazon.com/cloudwatch/home?"
            f"region=us-east-1#logsV2:logs-insights?queryDetail=~(source~'{state['trace_id']})"
        )
    elif trace_provider == "langsmith":
        state["provider_trace_url"] = (
            f"https://smith.langchain.com/o/org/projects/p/project/r/{state['trace_id']}"
        )

    logger.info(f"Trace URL: {state.get('provider_trace_url')}")

    return state


async def log_request_audit_event(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Log request received audit event.

    Args:
        state: Current workflow state

    Returns:
        Updated state with audit event ID
    """
    logger.info(f"Logging audit event for {state['request_id']}")

    # Generate audit event ID
    event_id = f"audit-{state['request_id']}-request-received"

    # Log audit event (placeholder - actual implementation would write to DynamoDB)
    audit_event = {
        "event_id": event_id,
        "event_type": "REQUEST_RECEIVED",
        "request_id": state["request_id"],
        "session_id": state["session_id"],
        "trace_id": state["trace_id"],
        "actor_id": state["user_role_context"]["actor_id"],
        "timestamp": datetime.now().isoformat(),
        "outcome": "ACCEPTED" if not state.get("validation_error") else "REJECTED",
    }

    logger.info(f"Audit event: {audit_event}")

    add_audit_event_id(state, event_id)

    return state


# ============================================================================
# Output Processing Nodes
# ============================================================================


async def apply_output_guardrails(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Apply Bedrock guardrails to recommendation output.

    Args:
        state: Current workflow state

    Returns:
        Updated state with guardrail results
    """
    logger.info(f"Applying guardrails for {state['request_id']}")

    # Placeholder - actual implementation would call Bedrock guardrails API
    guardrail_result = {
        "action": "NONE",  # NONE, BLOCKED
        "assessments": [],
        "timestamp": datetime.now().isoformat(),
    }

    # Check if recommendation contains sensitive content (simplified)
    recommendation = state.get("recommendation_package")
    if recommendation:
        summary = recommendation.summary.lower()
        # Simple keyword check (actual implementation would use Bedrock guardrails)
        sensitive_keywords = ["password", "ssn", "credit card"]
        if any(keyword in summary for keyword in sensitive_keywords):
            guardrail_result["action"] = "BLOCKED"
            guardrail_result["assessments"].append(
                {"type": "SENSITIVE_INFORMATION", "action": "BLOCKED"}
            )

    state["guardrail_result"] = guardrail_result

    return state


async def assemble_recommendation(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Assemble final recommendation package from agent outputs.

    Args:
        state: Current workflow state

    Returns:
        Updated state with recommendation package
    """
    logger.info(f"Assembling recommendation for {state['request_id']}")

    from app.contracts.analysis import RecommendationPackage

    # Get agent outputs
    rebalancing = state.get("rebalancing_output", {})
    risk_policy = state.get("risk_policy_output")
    trade_proposal = state.get("trade_proposal_output", {})

    # Determine workflow state
    workflow_state = state.get("workflow_state", WorkflowState.NORMAL)
    if state.get("blockers"):
        workflow_state = WorkflowState.BLOCKED
    elif state.get("degraded_reasons"):
        workflow_state = WorkflowState.DEGRADED

    # Determine approval eligibility
    proposal_status = trade_proposal.get("proposal_status", "UNKNOWN")
    approval_eligibility = proposal_status in {"READY_FOR_REVIEW", "NO_ACTION_NEEDED"}

    if workflow_state == WorkflowState.BLOCKED:
        approval_eligibility = False

    # Create recommendation package
    recommendation = RecommendationPackage(
        summary=_generate_summary(state),
        agent_stages=state.get("agent_stages", []),
        current_allocation=rebalancing.get("current_allocation", {}),
        target_allocation=rebalancing.get("target_allocation", {}),
        proposed_allocation=trade_proposal.get("estimated_impact", rebalancing.get("current_allocation", {})),
        risk_policy=risk_policy,
        proposal=trade_proposal,
        workflow_state=workflow_state,
        approval_eligibility=approval_eligibility,
        evidence=risk_policy.evidence if risk_policy else [],
    )

    state["recommendation_package"] = recommendation
    state["workflow_state"] = workflow_state

    return state


async def create_approval_artifact(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Create approval artifact for human review.

    Args:
        state: Current workflow state

    Returns:
        Updated state with approval artifact
    """
    logger.info(f"Creating approval artifact for {state['request_id']}")

    from app.contracts.domain import ApprovalArtifact

    recommendation = state.get("recommendation_package")

    # Create approval artifact
    approval = ApprovalArtifact(
        approval_id=f"approval-{state['request_id']}",
        request_id=state["request_id"],
        session_id=state["session_id"],
        created_at=datetime.now(),
        approval_status="PENDING",
        recommendation=recommendation,
    )

    state["approval_artifact"] = approval

    return state


async def persist_workflow_artifacts(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Persist workflow artifacts to storage.

    Args:
        state: Current workflow state

    Returns:
        Updated state
    """
    logger.info(f"Persisting artifacts for {state['request_id']}")

    # Placeholder - actual implementation would write to DynamoDB
    artifacts = {
        "request_id": state["request_id"],
        "recommendation": state.get("recommendation_package"),
        "approval": state.get("approval_artifact"),
        "timestamp": datetime.now().isoformat(),
    }

    logger.info(f"Persisted artifacts: {list(artifacts.keys())}")

    return state


async def emit_workflow_audit_event(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Emit final workflow audit event.

    Args:
        state: Current workflow state

    Returns:
        Updated state with audit event ID
    """
    logger.info(f"Emitting workflow audit event for {state['request_id']}")

    # Generate audit event ID
    event_id = f"audit-{state['request_id']}-workflow-completed"

    # Log audit event
    audit_event = {
        "event_id": event_id,
        "event_type": "WORKFLOW_COMPLETED",
        "request_id": state["request_id"],
        "session_id": state["session_id"],
        "trace_id": state["trace_id"],
        "workflow_state": state.get("workflow_state", WorkflowState.NORMAL).value,
        "timestamp": datetime.now().isoformat(),
        "outcome": "SUCCESS" if not state.get("error") else "FAILED",
    }

    logger.info(f"Audit event: {audit_event}")

    add_audit_event_id(state, event_id)

    return state


async def return_response(state: WorkflowGraphState) -> WorkflowGraphState:
    """
    Prepare final response.

    Args:
        state: Current workflow state

    Returns:
        Updated state (terminal node)
    """
    logger.info(f"Returning response for {state['request_id']}")

    # State is ready for response serialization
    return state


# ============================================================================
# Helper Functions
# ============================================================================


def _generate_summary(state: WorkflowGraphState) -> str:
    """Generate summary based on workflow state."""
    if state.get("blockers"):
        return f"Recommendation is blocked: {', '.join(state['blockers'])}"

    trade_proposal = state.get("trade_proposal_output", {})
    proposal_status = trade_proposal.get("proposal_status", "UNKNOWN")

    if proposal_status == "BLOCKED":
        return "Recommendation is blocked by deterministic policy checks."
    elif proposal_status == "NO_ACTION_NEEDED":
        return "Portfolio is already within configured allocation tolerances."
    elif state.get("degraded_reasons"):
        return f"Recommendation generated with degraded quality: {', '.join(state['degraded_reasons'])}"
    else:
        return "Portfolio has drift outside tolerance and is ready for manual review."
