from datetime import UTC, datetime
from decimal import Decimal

from app.contracts.market import MarketRegime, MarketTick


class MarketSimulationAgent:
    name = "Market Simulation Agent"

    def run(self, tick_id: int) -> MarketTick:
        regime = self._regime(tick_id)
        equity_change = self._equity_change(tick_id, regime)
        rate_change_bps = self._rate_change_bps(tick_id, regime)
        bond_change = self._bond_change(rate_change_bps)

        return MarketTick(
            tick_id=tick_id,
            as_of=datetime.now(UTC),
            regime=regime,
            equity_index=(Decimal("100") * (Decimal("1") + equity_change / Decimal("100"))),
            equity_change_pct=equity_change,
            interest_rate_pct=Decimal("4.25") + rate_change_bps / Decimal("100"),
            rate_change_bps=rate_change_bps,
            bond_price_index=(Decimal("100") * (Decimal("1") + bond_change / Decimal("100"))),
            bond_change_pct=bond_change,
            cash_yield_pct=Decimal("4.00"),
        )

    def _regime(self, tick_id: int) -> MarketRegime:
        if tick_id % 17 == 0:
            return MarketRegime.STRESSED
        if tick_id % 5 == 0:
            return MarketRegime.CALM
        return MarketRegime.NORMAL

    def _equity_change(self, tick_id: int, regime: MarketRegime) -> Decimal:
        cycle = Decimal(str((tick_id % 9) - 4))
        multiplier = {
            MarketRegime.CALM: Decimal("0.35"),
            MarketRegime.NORMAL: Decimal("0.80"),
            MarketRegime.STRESSED: Decimal("-1.75"),
        }[regime]
        return (cycle * multiplier).quantize(Decimal("0.01"))

    def _rate_change_bps(self, tick_id: int, regime: MarketRegime) -> Decimal:
        if regime == MarketRegime.STRESSED:
            return Decimal("18")
        return Decimal(str((tick_id % 7) - 3)) * Decimal("2")

    def _bond_change(self, rate_change_bps: Decimal) -> Decimal:
        return (rate_change_bps * Decimal("-0.08")).quantize(Decimal("0.01"))
