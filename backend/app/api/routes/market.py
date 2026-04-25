import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.agents.market_monitoring import MarketMonitoringAgent
from app.agents.market_simulation import MarketSimulationAgent
from app.agents.rebalance_trigger import RebalanceTriggerAgent
from app.contracts.market import MarketStreamEvent
from app.persistence.dependencies import get_workflow_store
from app.persistence.memory_store import WorkflowStore

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/stream")
async def stream_market(
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
    limit: int = Query(default=0, ge=0, le=500),
    interval_ms: int = Query(default=1500, ge=100, le=10000),
    account_id: str | None = Query(default=None),
) -> StreamingResponse:
    portfolio = _portfolio_for_stream(store, account_id)
    return StreamingResponse(
        _event_stream(
            limit=limit,
            interval_ms=interval_ms,
            account_id=portfolio.account_profile.account_id,
            store=store,
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _event_stream(limit: int, interval_ms: int, account_id: str, store: WorkflowStore):
    simulation_agent = MarketSimulationAgent()
    monitoring_agent = MarketMonitoringAgent()
    trigger_agent = RebalanceTriggerAgent()
    tick_id = 1

    while limit == 0 or tick_id <= limit:
        portfolio = store.get_portfolio(account_id)
        if portfolio is None:
            break
        tick = simulation_agent.run(tick_id)
        monitoring = monitoring_agent.run(tick, portfolio.portfolio_snapshot)
        rebalance = trigger_agent.run(tick, monitoring)
        event = MarketStreamEvent(tick=tick, monitoring=monitoring, rebalance=rebalance)
        yield f"data: {event.model_dump_json()}\n\n"
        tick_id += 1
        await asyncio.sleep(interval_ms / 1000)


def _portfolio_for_stream(store: WorkflowStore, account_id: str | None):
    if account_id:
        portfolio = store.get_portfolio(account_id)
        if portfolio is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return portfolio
    portfolios = store.list_portfolios()
    if not portfolios:
        raise HTTPException(status_code=404, detail="No portfolios are stored")
    return portfolios[0]
