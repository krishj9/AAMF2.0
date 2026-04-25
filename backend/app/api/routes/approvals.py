from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.contracts import ApprovalActionRequest, ApprovalTransitionResult
from app.persistence.dependencies import get_workflow_store
from app.persistence.memory_store import WorkflowStore

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/{approval_id}/actions", response_model=ApprovalTransitionResult)
async def apply_approval_action(
    approval_id: str,
    action: ApprovalActionRequest,
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
) -> ApprovalTransitionResult:
    approval = store.get_approval(approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval artifact not found")

    if approval.recommendation.workflow_state == "BLOCKED":
        raise HTTPException(status_code=409, detail="Blocked recommendations cannot be approved")

    if action.action in {"REJECT", "REQUEST_REVISION"} and not action.note:
        raise HTTPException(status_code=422, detail="A note is required for this approval action")

    return store.update_approval(approval_id, action)
