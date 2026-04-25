from datetime import UTC, datetime

from app.contracts.analysis import ApprovalArtifact, AuditEvent
from app.contracts.common import CorrelationMetadata, new_id


class InMemoryWorkflowStore:
    def __init__(self) -> None:
        self.approvals: dict[str, ApprovalArtifact] = {}
        self.audit_events: list[AuditEvent] = []

    def save_approval(self, artifact: ApprovalArtifact) -> ApprovalArtifact:
        self.approvals[artifact.approval_id] = artifact
        return artifact

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


workflow_store = InMemoryWorkflowStore()
