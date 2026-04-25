from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.contracts.domain import PortfolioRecord
from app.persistence.dependencies import get_workflow_store
from app.persistence.memory_store import WorkflowStore

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("", response_model=list[PortfolioRecord])
async def list_portfolios(
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
) -> list[PortfolioRecord]:
    return store.list_portfolios()


@router.get("/{account_id}", response_model=PortfolioRecord)
async def get_portfolio(
    account_id: str,
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
) -> PortfolioRecord:
    portfolio = store.get_portfolio(account_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio
