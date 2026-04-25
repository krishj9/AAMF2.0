from decimal import Decimal

from app.contracts.market import (
    MarketMonitoringSnapshot,
    MarketRegime,
    MarketTick,
    RebalanceSignal,
    RebalanceTriggerResult,
)


class RebalanceTriggerAgent:
    name = "Rebalance Trigger Agent"

    def run(self, tick: MarketTick, monitoring: MarketMonitoringSnapshot) -> RebalanceTriggerResult:
        threshold = Decimal("5.00")
        watch_threshold = Decimal("3.00")

        if tick.regime == MarketRegime.STRESSED and monitoring.max_abs_drift_pct >= watch_threshold:
            return RebalanceTriggerResult(
                signal=RebalanceSignal.REBALANCE_NEEDED,
                reason="Stressed market regime with material allocation drift.",
                threshold_pct=threshold,
            )

        if monitoring.max_abs_drift_pct >= threshold:
            return RebalanceTriggerResult(
                signal=RebalanceSignal.REBALANCE_NEEDED,
                reason="Allocation drift exceeded the configured rebalance threshold.",
                threshold_pct=threshold,
            )

        if monitoring.max_abs_drift_pct >= watch_threshold:
            return RebalanceTriggerResult(
                signal=RebalanceSignal.WATCH,
                reason="Allocation drift is approaching the rebalance threshold.",
                threshold_pct=threshold,
            )

        return RebalanceTriggerResult(
            signal=RebalanceSignal.NO_ACTION,
            reason="Allocation drift is within monitoring tolerance.",
            threshold_pct=threshold,
        )
