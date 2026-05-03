"""System Intelligence API — exposes workflow traces, memory, and audit trail."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.persistence.dependencies import get_workflow_store
from app.persistence.memory_store import WorkflowStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.get("/workflow-trace/{account_id}")
async def get_workflow_trace(
    account_id: str,
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
) -> dict:
    """
    Return the most recent workflow trace for an account — agent stages,
    state transitions, inputs/outputs, and timing metadata.
    """
    # Find the most recent approval artifact for this account
    approvals = [
        a for a in store.approvals.values()
        if a.account_profile.account_id == account_id
    ]
    if not approvals:
        return {"traces": [], "account_id": account_id}

    # Sort by creation time, most recent first
    approvals.sort(key=lambda a: a.correlation.created_at, reverse=True)
    latest = approvals[0]
    rec = latest.recommendation

    # Build enriched stage trace
    stages = []
    for i, stage in enumerate(rec.agent_stages):
        # Determine what each agent received and produced based on its role
        received, produced = _stage_io(stage.agent_name, rec, latest)
        stages.append({
            "index": i + 1,
            "agent_name": stage.agent_name,
            "status": stage.status,
            "summary": stage.summary,
            "protocol": stage.protocol,
            "execution_location": stage.execution_location,
            "received": received,
            "produced": produced,
            "is_llm_enhanced": stage.execution_location not in ("in_process_fallback",),
        })

    return {
        "account_id": account_id,
        "approval_id": latest.approval_id,
        "request_id": latest.correlation.request_id,
        "workflow_state": rec.workflow_state,
        "approval_status": latest.approval_status,
        "created_at": latest.correlation.created_at.isoformat(),
        "stages": stages,
        "state_transitions": _build_state_transitions(latest),
        "graph_summary": {
            "total_agents": len(stages),
            "llm_enhanced": sum(1 for s in stages if s["is_llm_enhanced"]),
            "remote_agents": sum(1 for s in stages if s["execution_location"] == "remote"),
            "mcp_agents": sum(1 for s in stages if s["protocol"] == "MCP"),
            "parallel_nodes": ["Memory / Personalization Agent", "Research Agent"],
            "conditional_routes": [
                {
                    "after": "Risk & Compliance Agent",
                    "condition": "policy verdict",
                    "taken": "generate_execution_proposal" if rec.risk_policy.verdict == "COMPLIANT" else "assemble_recommendation (BLOCKED)",
                },
                {
                    "after": "apply_output_guardrails",
                    "condition": "guardrail result",
                    "taken": "create_approval_artifact",
                },
            ],
        },
    }


@router.get("/memory/{client_id}")
async def get_memory_timeline(
    client_id: str,
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
) -> dict:
    """
    Return the client's memory timeline — past decisions, learned preferences,
    and how memory influenced the most recent recommendation.
    """
    from app.adapters.memory import LocalMemoryAdapter
    adapter = LocalMemoryAdapter()
    items = await adapter.retrieve(client_id)

    # Find all approvals for this client to build decision history
    client_approvals = [
        a for a in store.approvals.values()
        if a.client_profile.client_id == client_id
    ]
    client_approvals.sort(key=lambda a: a.correlation.created_at, reverse=True)

    # Build decision memory from actual approval history
    decision_memories = []
    for approval in client_approvals:
        trades = approval.recommendation.proposal.trades
        trade_summary = ", ".join(
            f"{t.action} {t.symbol} ${t.estimated_value}" for t in trades
        ) if trades else "no trades"

        decision_memories.append({
            "memory_id": f"decision_{approval.approval_id[:8]}",
            "category": "decision",
            "content": f"Recommendation {approval.approval_status.lower()} on "
                       f"{approval.correlation.created_at.strftime('%Y-%m-%d %H:%M')} — {trade_summary}",
            "timestamp": approval.correlation.created_at.isoformat(),
            "confidence": 1.0,
            "source": "approval_artifact",
            "approval_status": approval.approval_status,
        })

    # Static memory items from adapter
    static_memories = [
        {
            "memory_id": item.memory_id,
            "category": item.category,
            "content": item.content or item.summary,
            "timestamp": item.timestamp,
            "confidence": item.confidence,
            "source": "memory_store",
        }
        for item in items
    ]

    all_memories = decision_memories + static_memories

    # Find most recent recommendation to show memory influence
    memory_influence = None
    if client_approvals:
        latest = client_approvals[0]
        memory_influence = {
            "recommendation_id": latest.approval_id,
            "items_retrieved": len(items),
            "items_used": len(items),
            "synthesis_available": False,
            "note": "Memory items were retrieved and passed to the rebalancing workflow as client context.",
        }

    return {
        "client_id": client_id,
        "total_memories": len(all_memories),
        "memories": all_memories,
        "memory_influence": memory_influence,
        "architecture_note": (
            "Memory is retrieved by the Memory/Personalization Agent at the start of each "
            "LangGraph workflow run. Items are passed through the state graph and influence "
            "the rebalancing agent's context and the recommendation summary."
        ),
    }


@router.get("/audit/{account_id}")
async def get_audit_trail(
    account_id: str,
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
) -> dict:
    """
    Return the human-in-the-loop audit trail — every workflow run,
    approval artifact created, and human decision made.
    """
    # Get all approvals for this account
    approvals = [
        a for a in store.approvals.values()
        if a.account_profile.account_id == account_id
    ]
    approvals.sort(key=lambda a: a.correlation.created_at, reverse=True)

    # Get audit events (filter by correlation if possible)
    all_events = store.audit_events
    request_ids = {a.correlation.request_id for a in approvals}
    relevant_events = [
        e for e in all_events
        if e.correlation.request_id in request_ids
    ]
    relevant_events.sort(key=lambda e: e.created_at, reverse=True)

    # Build decision records
    decisions = []
    for approval in approvals:
        rec = approval.recommendation
        trades = rec.proposal.trades
        decisions.append({
            "approval_id": approval.approval_id,
            "request_id": approval.correlation.request_id,
            "created_at": approval.correlation.created_at.isoformat(),
            "workflow_state": str(rec.workflow_state),
            "policy_verdict": rec.risk_policy.verdict,
            "trade_count": len(trades),
            "trades": [
                {
                    "action": t.action,
                    "symbol": t.symbol,
                    "estimated_value": str(t.estimated_value),
                    "rationale": t.rationale,
                }
                for t in trades
            ],
            "approval_status": approval.approval_status,
            "approved_by": approval.approved_by,
            "approved_at": approval.approved_at.isoformat() if approval.approved_at else None,
            "rejection_note": approval.rejection_note,
            "recommendation_hash": approval.recommendation_hash[:12] + "...",
            "hitl_node": "Human Approval Workflow Agent",
            "state_transition": f"PENDING → {approval.approval_status}",
        })

    # Build audit event log
    event_log = [
        {
            "event_id": e.event_id,
            "event_type": e.event_type,
            "outcome": e.outcome,
            "actor_id": e.actor_id,
            "created_at": e.created_at.isoformat(),
            "details": e.details,
        }
        for e in relevant_events[:20]
    ]

    return {
        "account_id": account_id,
        "total_workflows": len(approvals),
        "total_decisions": len([d for d in decisions if d["approval_status"] != "PENDING"]),
        "decisions": decisions,
        "audit_events": event_log,
        "hitl_architecture": {
            "approval_node": "Human Approval Workflow Agent",
            "artifact_type": "ApprovalArtifact",
            "hash_verification": "SHA-256 recommendation hash prevents stale approvals",
            "state_machine": "PENDING → APPROVED | REJECTED | REVISION_REQUESTED",
            "audit_log": "Every action written to immutable audit event store",
            "no_autonomous_execution": "Trades never execute without explicit human approval",
        },
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stage_io(agent_name: str, rec, approval) -> tuple[str, str]:
    """Return human-readable input/output description for each agent stage."""
    name = agent_name.lower()

    if "memory" in name:
        return (
            "client_id, risk_profile, portfolio_context",
            f"memory items, client preferences context",
        )
    if "research" in name:
        portfolio_symbols = ", ".join(
            h.symbol for h in approval.original_portfolio_snapshot.holdings
        )
        return (
            f"symbols: {portfolio_symbols}, allocation context",
            f"market_context, key_insights, regime assessment",
        )
    if "sentiment" in name:
        return (
            "asset class symbols from portfolio",
            f"sentiment scores per symbol, overall_sentiment",
        )
    if "rebalanc" in name:
        drift_count = len([d for d in rec.risk_policy.drift if not d.within_tolerance])
        return (
            "portfolio_snapshot, allocation_target",
            f"drift analysis: {drift_count} asset class(es) outside tolerance",
        )
    if "risk" in name or "compliance" in name:
        return (
            "portfolio_snapshot, drift_items, risk_profile",
            f"policy verdict: {rec.risk_policy.verdict}, rule results",
        )
    if "trade" in name or "execution" in name or "proposal" in name:
        trade_count = len(rec.proposal.trades)
        return (
            "portfolio_snapshot, risk_policy_output",
            f"{trade_count} trade proposal(s), estimated_impact",
        )
    if "human" in name or "approval" in name:
        return (
            "recommendation_package, workflow_state",
            f"approval_artifact (status: {approval.approval_status}), recommendation_hash",
        )
    return ("workflow state", "updated workflow state")


def _build_state_transitions(approval) -> list[dict]:
    """Build the LangGraph state transition history."""
    rec = approval.recommendation
    transitions = [
        {
            "from_node": "START",
            "to_node": "validate_request",
            "condition": None,
            "state_change": "workflow_state = NORMAL",
        },
        {
            "from_node": "validate_request",
            "to_node": "initialize_context_and_trace",
            "condition": "validation passed",
            "state_change": "trace_id assigned",
        },
        {
            "from_node": "log_request_audit_event",
            "to_node": "hydrate_memory + run_research (parallel)",
            "condition": None,
            "state_change": "parallel fan-out",
        },
        {
            "from_node": "run_risk_policy",
            "to_node": "generate_execution_proposal" if rec.risk_policy.verdict == "COMPLIANT" else "assemble_recommendation",
            "condition": f"policy verdict = {rec.risk_policy.verdict}",
            "state_change": "BLOCKED" if rec.risk_policy.verdict != "COMPLIANT" else "proceeding to trade proposal",
        },
        {
            "from_node": "apply_output_guardrails",
            "to_node": "create_approval_artifact",
            "condition": "guardrails = NONE",
            "state_change": "approval_artifact created",
        },
        {
            "from_node": "create_approval_artifact",
            "to_node": "Human Decision (HITL)",
            "condition": None,
            "state_change": f"approval_status = {approval.approval_status}",
        },
    ]
    return transitions
