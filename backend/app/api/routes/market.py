import asyncio

from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

from app.agents.market_monitoring import MarketMonitoringAgent
from app.agents.market_simulation import MarketSimulationAgent
from app.agents.rebalance_trigger import RebalanceTriggerAgent
from app.contracts.market import MarketStreamEvent

router = APIRouter(prefix="/market", tags=["market"])


@router.get("/stream")
async def stream_market(
    limit: int = Query(default=0, ge=0, le=500),
    interval_ms: int = Query(default=1500, ge=100, le=10000),
) -> StreamingResponse:
    return StreamingResponse(
        _event_stream(limit=limit, interval_ms=interval_ms),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _event_stream(limit: int, interval_ms: int):
    simulation_agent = MarketSimulationAgent()
    monitoring_agent = MarketMonitoringAgent()
    trigger_agent = RebalanceTriggerAgent()
    tick_id = 1

    while limit == 0 or tick_id <= limit:
        tick = simulation_agent.run(tick_id)
        monitoring = monitoring_agent.run(tick)
        rebalance = trigger_agent.run(tick, monitoring)
        event = MarketStreamEvent(tick=tick, monitoring=monitoring, rebalance=rebalance)
        yield f"data: {event.model_dump_json()}\n\n"
        tick_id += 1
        await asyncio.sleep(interval_ms / 1000)
