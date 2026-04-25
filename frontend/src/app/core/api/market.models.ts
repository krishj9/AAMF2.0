export interface MarketStreamEvent {
  tick: {
    tick_id: number;
    as_of: string;
    regime: string;
    equity_index: string;
    equity_change_pct: string;
    interest_rate_pct: string;
    rate_change_bps: string;
    bond_price_index: string;
    bond_change_pct: string;
    cash_yield_pct: string;
  };
  monitoring: {
    portfolio_value: string;
    current_allocation: Record<string, string>;
    drift: Record<string, string>;
    max_abs_drift_pct: string;
  };
  rebalance: {
    signal: 'NO_ACTION' | 'WATCH' | 'REBALANCE_NEEDED' | 'BLOCKED_BY_POLICY';
    reason: string;
    threshold_pct: string;
  };
}
