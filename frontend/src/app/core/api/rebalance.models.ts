export interface ActorContext {
  actor_id: string;
  display_name: string;
  role: 'OWNER' | 'TESTER' | 'VIEWER';
  auth_provider: string;
  is_owner: boolean;
}

export interface PortfolioHolding {
  instrument_id: string;
  symbol: string;
  asset_class: string;
  sector?: string;
  quantity: string;
  market_price: string;
  market_value: string;
  as_of: string;
}

export interface PortfolioRebalanceRequest {
  actor: ActorContext;
  client_profile: {
    client_id: string;
    display_label: string;
    risk_profile_id: string;
    synthetic: boolean;
  };
  account_profile: {
    account_id: string;
    client_id: string;
    account_type: string;
    base_currency: string;
    taxable: boolean;
  };
  portfolio_snapshot: {
    snapshot_id: string;
    account_id: string;
    as_of: string;
    holdings: PortfolioHolding[];
    cash: string;
    total_value: string;
  };
  allocation_target: {
    target_id: string;
    account_id: string;
    asset_class_targets: Record<string, string>;
    tolerance_bands: Record<string, string>;
  };
  risk_profile: {
    risk_profile_id: string;
    risk_level: string;
    max_single_position_pct: string;
    max_sector_pct: string;
    allowed_asset_classes: string[];
  };
}

export interface PortfolioRecord {
  client_profile: PortfolioRebalanceRequest['client_profile'];
  account_profile: PortfolioRebalanceRequest['account_profile'];
  portfolio_snapshot: PortfolioRebalanceRequest['portfolio_snapshot'];
  allocation_target: PortfolioRebalanceRequest['allocation_target'];
  risk_profile: PortfolioRebalanceRequest['risk_profile'];
  updated_at: string;
  source: string;
  source_approval_id?: string;
}

export interface OrchestrationResponse {
  workflow_state: 'NORMAL' | 'DEGRADED' | 'LOW_CONFIDENCE' | 'BLOCKED';
  recommendation_package?: {
    summary: string;
    agent_stages: Array<{
      agent_name: string;
      status: string;
      summary: string;
      protocol: string;
      execution_location: string;
    }>;
    current_allocation: Record<string, string>;
    target_allocation: Record<string, string>;
    approval_eligibility: boolean;
    proposal: {
      proposal_status: string;
      trades: Array<{
        trade_id: string;
        symbol: string;
        action: string;
        estimated_value: string;
        rationale: string;
      }>;
    };
    risk_policy: {
      verdict: string;
      rule_results: Array<{
        rule_id: string;
        passed: boolean;
        message: string;
      }>;
    };
  };
  approval_artifact?: {
    approval_id: string;
    approval_status: string;
    recommendation_hash: string;
  };
}

export interface ApprovalTransitionResult {
  approval_id: string;
  previous_status: string;
  next_status: string;
  accepted: boolean;
  audit_event_id: string;
  message: string;
}
