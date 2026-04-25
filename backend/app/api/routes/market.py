import asyncio
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.agents.market_monitoring import MarketMonitoringAgent
from app.agents.market_simulation import MarketSimulationAgent
from app.agents.rebalance_trigger import RebalanceTriggerAgent
from app.contracts.market import MarketStreamEvent
from app.core.config import Settings, get_settings
from app.persistence.dependencies import get_workflow_store
from app.persistence.memory_store import WorkflowStore

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/stream")
async def stream_market(
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
    settings: Annotated[Settings, Depends(get_settings)],
    limit: int = Query(default=0, ge=0, le=500),
    interval_ms: int = Query(default=1500, ge=100, le=10000),
    account_id: str | None = Query(default=None),
) -> StreamingResponse:
    portfolio = _portfolio_for_stream(store, account_id)
    effective_limit = limit
    if effective_limit == 0 and settings.market_stream_max_events > 0:
        effective_limit = settings.market_stream_max_events
    return StreamingResponse(
        _event_stream(
            limit=effective_limit,
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


@router.get("/tick", response_model=MarketStreamEvent)
def get_market_tick(
    store: Annotated[WorkflowStore, Depends(get_workflow_store)],
    interval_ms: int = Query(default=1500, ge=100, le=10000),
    account_id: str | None = Query(default=None),
) -> MarketStreamEvent:
    portfolio = _portfolio_for_stream(store, account_id)
    # Use elapsed time buckets so polling requests advance deterministically.
    tick_id = max(1, int(time.time() * 1000 / interval_ms))
    return _build_event(tick_id=tick_id, account_id=portfolio.account_profile.account_id, store=store)


def _build_event(tick_id: int, account_id: str, store: WorkflowStore) -> MarketStreamEvent:
    simulation_agent = MarketSimulationAgent()
    monitoring_agent = MarketMonitoringAgent()
    trigger_agent = RebalanceTriggerAgent()
    portfolio = store.get_portfolio(account_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    tick = simulation_agent.run(tick_id)
    monitoring = monitoring_agent.run(tick, portfolio.portfolio_snapshot)
    rebalance = trigger_agent.run(tick, monitoring)
    return MarketStreamEvent(tick=tick, monitoring=monitoring, rebalance=rebalance)


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
