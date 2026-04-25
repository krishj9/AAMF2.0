from decimal import ROUND_HALF_UP, Decimal

from app.contracts.domain import PortfolioSnapshot
from app.contracts.market import MarketMonitoringSnapshot, MarketTick


class MarketMonitoringAgent:
    name = "Market Monitoring Agent"

    def run(self, tick: MarketTick, snapshot: PortfolioSnapshot) -> MarketMonitoringSnapshot:
        base_values = self._base_values(snapshot)
        equity_value = base_values["equity"] * (
            Decimal("1") + tick.equity_change_pct / Decimal("100")
        )
        fixed_income_value = base_values["fixed_income"] * (
            Decimal("1") + tick.bond_change_pct / Decimal("100")
        )
        cash_value = base_values["cash"] * (Decimal("1") + tick.cash_yield_pct / Decimal("10000"))
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

    def _base_values(self, snapshot: PortfolioSnapshot) -> dict[str, Decimal]:
        values = {"equity": Decimal("0"), "fixed_income": Decimal("0"), "cash": snapshot.cash}
        for holding in snapshot.holdings:
            if holding.asset_class in values:
                values[holding.asset_class] += holding.market_value
        return values
