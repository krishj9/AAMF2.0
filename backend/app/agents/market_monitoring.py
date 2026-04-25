from decimal import ROUND_HALF_UP, Decimal

from app.contracts.market import MarketMonitoringSnapshot, MarketTick


class MarketMonitoringAgent:
    name = "Market Monitoring Agent"

    def run(self, tick: MarketTick) -> MarketMonitoringSnapshot:
        equity_value = Decimal("7000") * (Decimal("1") + tick.equity_change_pct / Decimal("100"))
        fixed_income_value = Decimal("2000") * (
            Decimal("1") + tick.bond_change_pct / Decimal("100")
        )
        cash_value = Decimal("1000") * (Decimal("1") + tick.cash_yield_pct / Decimal("10000"))
        portfolio_value = equity_value + fixed_income_value + cash_value

        current_allocation = {
            "equity": self._pct(equity_value, portfolio_value),
            "fixed_income": self._pct(fixed_income_value, portfolio_value),
            "cash": self._pct(cash_value, portfolio_value),
        }
        target = {"equity": Decimal("60"), "fixed_income": Decimal("30"), "cash": Decimal("10")}
        drift = {key: self._quantize(current_allocation[key] - target[key]) for key in target}
        max_abs_drift = max(abs(value) for value in drift.values())

        return MarketMonitoringSnapshot(
            portfolio_value=portfolio_value.quantize(Decimal("0.01")),
            current_allocation=current_allocation,
            drift=drift,
            max_abs_drift_pct=max_abs_drift,
        )

    def _pct(self, value: Decimal, total: Decimal) -> Decimal:
        return self._quantize((value / total) * Decimal("100"))

    def _quantize(self, value: Decimal) -> Decimal:
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
