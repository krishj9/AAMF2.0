from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel

from app.contracts import (
    ActorContext,
    ApprovalArtifact,
    AuditEvent,
    CorrelationMetadata,
    ExecutionProposalResponse,
    GraphState,
    OrchestrationResponse,
    PermissionMatrix,
    PortfolioRebalanceRequest,
    RecommendationPackage,
    RiskPolicyResponse,
    SeedManifest,
    StructuredError,
    TradeProposal,
    VersionMetadata,
)
from app.contracts.domain import (
    AccountProfile,
    AllocationTarget,
    ClientProfile,
    PortfolioSnapshot,
    RiskProfile,
)

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "schemas"


MODELS: list[type[BaseModel]] = [
    CorrelationMetadata,
    VersionMetadata,
    ActorContext,
    PermissionMatrix,
    StructuredError,
    ClientProfile,
    AccountProfile,
    PortfolioSnapshot,
    AllocationTarget,
    RiskProfile,
    PortfolioRebalanceRequest,
    GraphState,
    RiskPolicyResponse,
    ExecutionProposalResponse,
    TradeProposal,
    RecommendationPackage,
    ApprovalArtifact,
    AuditEvent,
    OrchestrationResponse,
    SeedManifest,
]


def write_schema(model: type[BaseModel]) -> None:
    schema = model.model_json_schema()
    target = SCHEMA_DIR / f"{model.__name__}.schema.json"
    target.write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n")


def main() -> None:
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        write_schema(model)


if __name__ == "__main__":
    main()
