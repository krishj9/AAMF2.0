from datetime import UTC, datetime
from typing import Protocol

from app.contracts.analysis import (
    ApprovalAction,
    ApprovalActionRequest,
    ApprovalArtifact,
    ApprovalTransitionResult,
    AuditEvent,
)
from app.contracts.common import CorrelationMetadata, new_id


class WorkflowStore(Protocol):
    def save_approval(self, artifact: ApprovalArtifact) -> ApprovalArtifact: ...

    def get_approval(self, approval_id: str) -> ApprovalArtifact | None: ...

    def update_approval(
        self, approval_id: str, action: ApprovalActionRequest
    ) -> ApprovalTransitionResult: ...

    def add_audit_event(
        self,
        event_type: str,
        correlation: CorrelationMetadata,
        outcome: str,
        actor_id: str | None = None,
        details: dict[str, str] | None = None,
    ) -> AuditEvent: ...


class InMemoryWorkflowStore:
    def __init__(self) -> None:
        self.approvals: dict[str, ApprovalArtifact] = {}
        self.audit_events: list[AuditEvent] = []

    def save_approval(self, artifact: ApprovalArtifact) -> ApprovalArtifact:
        self.approvals[artifact.approval_id] = artifact
        return artifact

    def get_approval(self, approval_id: str) -> ApprovalArtifact | None:
        return self.approvals.get(approval_id)

    def update_approval(
        self, approval_id: str, action: ApprovalActionRequest
    ) -> ApprovalTransitionResult:
        approval = self.approvals[approval_id]
        previous = approval.approval_status
        if action.expected_recommendation_hash != approval.recommendation_hash:
            event = self.add_audit_event(
                "APPROVAL_ACTION_REJECTED",
                approval.correlation,
                "STALE_APPROVAL_ARTIFACT",
                action.actor_id,
            )
            return ApprovalTransitionResult(
                approval_id=approval_id,
                previous_status=previous,
                next_status=previous,
                accepted=False,
                audit_event_id=event.event_id,
                message="Recommendation hash did not match approval artifact.",
            )

        next_status = {
            ApprovalAction.APPROVE: "APPROVED",
            ApprovalAction.REJECT: "REJECTED",
            ApprovalAction.REQUEST_REVISION: "REVISION_REQUESTED",
        }[action.action]
        approval.approval_status = next_status
        if action.action == ApprovalAction.APPROVE:
            approval.approved_by = action.actor_id
            approval.approved_at = datetime.now(UTC)
        if action.action == ApprovalAction.REJECT:
            approval.rejection_note = action.note
        self.approvals[approval_id] = approval
        event = self.add_audit_event(
            "APPROVAL_ACTION",
            approval.correlation,
            next_status,
            action.actor_id,
            {"approval_id": approval_id, "action": action.action},
        )
        return ApprovalTransitionResult(
            approval_id=approval_id,
            previous_status=previous,
            next_status=next_status,
            accepted=True,
            audit_event_id=event.event_id,
            message="Approval state updated.",
        )

    def add_audit_event(
        self,
        event_type: str,
        correlation: CorrelationMetadata,
        outcome: str,
        actor_id: str | None = None,
        details: dict[str, str] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            event_id=new_id("evt"),
            event_type=event_type,
            correlation=correlation,
            actor_id=actor_id,
            outcome=outcome,
            details=details or {},
            created_at=datetime.now(UTC),
        )
        self.audit_events.append(event)
        return event

