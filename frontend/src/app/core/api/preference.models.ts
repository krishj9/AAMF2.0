export interface PreferenceProfile {
  client_id: string;
  client_profile: {
    client_id: string;
    display_label: string;
    risk_profile_id: string;
    tax_profile_id?: string;
  };
  risk_profile: {
    risk_profile_id: string;
    risk_level: string;
    max_single_position_pct: string;
    max_sector_pct: string;
    allowed_asset_classes: string[];
  } | null;
  allocation_target: {
    target_id: string;
    account_id: string;
    asset_class_targets: Record<string, string>;
    tolerance_bands: Record<string, string>;
  };
  constraints: Record<string, any>;
  updated_at: string;
}

export interface PreferenceUpdateRequest {
  risk_profile?: {
    risk_profile_id?: string;
    risk_level: string;
    max_single_position_pct: string;
    max_sector_pct: string;
    allowed_asset_classes: string[];
  };
  allocation_target?: {
    asset_class_targets: Record<string, string>;
    tolerance_bands: Record<string, string>;
  };
  constraints?: Record<string, any>;
}

export interface PreferenceHistoryItem {
  version: number;
  timestamp: string;
  changes: Record<string, { old: any; new: any }>;
  reason: string;
}
