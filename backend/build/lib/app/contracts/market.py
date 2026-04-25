from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from app.contracts.common import ContractModel


class MarketRegime(StrEnum):
    CALM = "CALM"
    NORMAL = "NORMAL"
    STRESSED = "STRESSED"


class RebalanceSignal(StrEnum):
    NO_ACTION = "NO_ACTION"
    WATCH = "WATCH"
    REBALANCE_NEEDED = "REBALANCE_NEEDED"
    BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"


class MarketTick(ContractModel):
    tick_id: int
    as_of: datetime
    regime: MarketRegime
    equity_index: Decimal
    equity_change_pct: Decimal
    interest_rate_pct: Decimal
    rate_change_bps: Decimal
    bond_price_index: Decimal
    bond_change_pct: Decimal
    cash_yield_pct: Decimal


class MarketMonitoringSnapshot(ContractModel):
    portfolio_value: Decimal
    current_allocation: dict[str, Decimal]
    drift: dict[str, Decimal]
    max_abs_drift_pct: Decimal


class RebalanceTriggerResult(ContractModel):
    signal: RebalanceSignal
    reason: str
    threshold_pct: Decimal


class MarketStreamEvent(ContractModel):
    tick: MarketTick
    monitoring: MarketMonitoringSnapshot
    rebalance: RebalanceTriggerResult
