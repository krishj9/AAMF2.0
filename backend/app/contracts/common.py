from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ActorRole(StrEnum):
    OWNER = "OWNER"
    TESTER = "TESTER"
    VIEWER = "VIEWER"


class WorkflowState(StrEnum):
    NORMAL = "NORMAL"
    DEGRADED = "DEGRADED"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    BLOCKED = "BLOCKED"


class ErrorSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CorrelationMetadata(ContractModel):
    request_id: str = Field(default_factory=lambda: new_id("req"))
    session_id: str = Field(default_factory=lambda: new_id("ses"))
    trace_id: str = Field(default_factory=lambda: new_id("trc"))
    idempotency_key: str | None = None
    created_at: datetime = Field(default_factory=utc_now)


class VersionMetadata(ContractModel):
    schema_version: str = "1.0.0"
    policy_version: str = "1.0.0"
    agent_version_set: str = "local-dev"
    app_version: str = "0.1.0"
    environment: str = "dev"


class ActorContext(ContractModel):
    actor_id: str
    display_name: str
    role: ActorRole = ActorRole.OWNER
    auth_provider: str = "local"
    is_owner: bool = True


class PermissionMatrix(ContractModel):
    role: ActorRole
    can_submit_request: bool = True
    can_approve: bool = False
    can_override: bool = False
    can_correct_memory: bool = False
    can_view_audit: bool = False
    can_deploy: bool = False

    @computed_field
    @property
    def owner_only_permissions_valid(self) -> bool:
        if self.role == ActorRole.OWNER:
            return True
        return not any(
            [
                self.can_approve,
                self.can_override,
                self.can_correct_memory,
                self.can_view_audit,
                self.can_deploy,
            ]
        )


class StructuredError(ContractModel):
    code: str
    message: str
    severity: ErrorSeverity = ErrorSeverity.ERROR
    retryable: bool = False
    source: str
    correlation: CorrelationMetadata | None = None
    details: dict[str, Any] = Field(default_factory=dict)
