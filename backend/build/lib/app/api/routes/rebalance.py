from typing import Annotated

from fastapi import APIRouter, Depends

from app.contracts import OrchestrationResponse, PortfolioRebalanceRequest
from app.core.config import Settings, get_settings
from app.persistence.dependencies import get_workflow_store
from app.persistence.memory_store import WorkflowStore
from app.services.orchestrator import Orchestrator

router = APIRouter(prefix="/rebalance", tags=["rebalance"])


def get_orchestrator(store: Annotated[WorkflowStore, Depends(get_workflow_store)]) -> Orchestrator:
    return Orchestrator(store)


@router.post("", response_model=OrchestrationResponse)
async def create_rebalance_request(
    request: PortfolioRebalanceRequest,
    settings: Annotated[Settings, Depends(get_settings)],
    orchestrator: Annotated[Orchestrator, Depends(get_orchestrator)],
) -> OrchestrationResponse:
    request.version = request.version.model_copy(
        update={
            "schema_version": settings.schema_version,
            "policy_version": settings.policy_version,
            "app_version": settings.app_version,
            "environment": settings.environment,
        }
    )
    return await orchestrator.run(request)
