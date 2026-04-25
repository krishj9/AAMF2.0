from decimal import ROUND_HALF_UP, Decimal

from app.contracts.analysis import DriftItem
from app.contracts.domain import AllocationTarget, PortfolioSnapshot

PCT_QUANT = Decimal("0.01")


def quantize_pct(value: Decimal) -> Decimal:
    return value.quantize(PCT_QUANT, rounding=ROUND_HALF_UP)


def calculate_asset_allocation(snapshot: PortfolioSnapshot) -> dict[str, Decimal]:
    allocation: dict[str, Decimal] = {}
    if snapshot.total_value <= 0:
        return allocation

    for holding in snapshot.holdings:
        key = holding.asset_class or "unknown"
        allocation[key] = allocation.get(key, Decimal("0")) + holding.market_value

    if snapshot.cash > 0:
        allocation["cash"] = allocation.get("cash", Decimal("0")) + snapshot.cash

    return {
        key: quantize_pct((market_value / snapshot.total_value) * Decimal("100"))
        for key, market_value in allocation.items()
    }


def calculate_drift(snapshot: PortfolioSnapshot, target: AllocationTarget) -> list[DriftItem]:
    current = calculate_asset_allocation(snapshot)
    all_keys = set(current) | set(target.asset_class_targets)
    drift: list[DriftItem] = []

    for key in sorted(all_keys):
        current_pct = current.get(key, Decimal("0"))
        target_pct = target.asset_class_targets.get(key, Decimal("0"))
        tolerance = target.tolerance_bands.get(key, Decimal("5"))
        drift_pct = quantize_pct(current_pct - target_pct)
        drift.append(
            DriftItem(
                key=key,
                current_pct=current_pct,
                target_pct=target_pct,
                drift_pct=drift_pct,
                tolerance_pct=tolerance,
                within_tolerance=abs(drift_pct) <= tolerance,
            )
        )

    return drift
