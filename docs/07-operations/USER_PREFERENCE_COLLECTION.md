# User Preference Collection Strategy

## Overview

Currently, the Asset Management application **does not have a preference collection UI**. Preferences are hardcoded in seed data and stored in the database. This document outlines how the application would collect, store, and use user preferences in a production system.

## Current State

### Existing Data Structures

The application currently stores the following preference-related data:

```python
# Client Profile (Basic Info)
class ClientProfile:
    client_id: str
    household_id: str | None
    display_label: str
    risk_profile_id: str  # References a risk profile
    tax_profile_id: str | None
    synthetic: bool  # Indicates if this is test data

# Risk Profile (Risk Preferences)
class RiskProfile:
    risk_profile_id: str
    risk_level: str  # e.g., "conservative", "balanced", "aggressive"
    max_single_position_pct: Decimal  # Max % in single stock
    max_sector_pct: Decimal  # Max % in single sector
    allowed_asset_classes: list[str]  # e.g., ["equity", "fixed_income", "cash"]

# Allocation Target (Asset Allocation Preferences)
class AllocationTarget:
    target_id: str
    account_id: str
    asset_class_targets: dict[str, Decimal]  # e.g., {"equity": 0.60, "fixed_income": 0.30, "cash": 0.10}
    security_targets: dict[str, Decimal]  # Specific security preferences
    tolerance_bands: dict[str, Decimal]  # Rebalancing thresholds
```

### Seed Data Example

```python
# Demo investor with hardcoded preferences
{
    "client_profile": {
        "client_id": "client_demo",
        "display_label": "Demo Investor",
        "risk_profile_id": "risk_balanced",
        "synthetic": True
    },
    "risk_profile": {
        "risk_profile_id": "risk_balanced",
        "risk_level": "balanced",
        "max_single_position_pct": 85,
        "max_sector_pct": 60,
        "allowed_asset_classes": ["equity", "fixed_income", "cash"]
    },
    "allocation_target": {
        "asset_class_targets": {
            "equity": 0.60,
            "fixed_income": 0.30,
            "cash": 0.10
        },
        "tolerance_bands": {
            "equity": 0.05,
            "fixed_income": 0.05,
            "cash": 0.05
        }
    }
}
```

## Proposed Preference Collection System

### 1. Frontend Preference Collection UI

#### A. Onboarding Wizard (Initial Setup)

**Step 1: Risk Assessment Questionnaire**
```
Question 1: What is your investment time horizon?
- Less than 2 years
- 2-5 years
- 5-10 years
- 10+ years

Question 2: How would you react if your portfolio dropped 20% in value?
- Sell immediately (Very Conservative)
- Sell some positions (Conservative)
- Hold and wait (Moderate)
- Buy more (Aggressive)
- Indifferent (Very Aggressive)

Question 3: What is your primary investment goal?
- Capital preservation
- Income generation
- Balanced growth
- Aggressive growth
- Wealth accumulation

Question 4: Have you invested before?
- No (Beginner)
- Yes, some experience (Intermediate)
- Yes, extensive experience (Advanced)
```

**Output**: Risk Profile
```json
{
  "risk_profile_id": "risk_balanced",
  "risk_level": "balanced",
  "max_single_position_pct": 85,
  "max_sector_pct": 60,
  "allowed_asset_classes": ["equity", "fixed_income", "cash"]
}
```

**Step 2: Asset Allocation Preferences**
```
Question 1: What allocation do you prefer?
- Conservative (30% equity, 60% bonds, 10% cash)
- Moderate (50% equity, 40% bonds, 10% cash)
- Balanced (60% equity, 30% bonds, 10% cash)
- Growth (75% equity, 20% bonds, 5% cash)
- Aggressive (90% equity, 10% bonds, 0% cash)

Question 2: How often should we rebalance?
- Quarterly
- Semi-annually
- Annually
- Only when drift exceeds threshold

Question 3: Rebalancing tolerance (when to rebalance):
- Strict (±2% drift)
- Moderate (±5% drift)
- Relaxed (±10% drift)
```

**Output**: Allocation Target
```json
{
  "asset_class_targets": {
    "equity": 0.60,
    "fixed_income": 0.30,
    "cash": 0.10
  },
  "tolerance_bands": {
    "equity": 0.05,
    "fixed_income": 0.05,
    "cash": 0.05
  }
}
```

**Step 3: Investment Constraints**
```
Question 1: Do you have any restricted securities?
- Yes (list them)
- No

Question 2: Tax considerations:
- Tax-loss harvesting enabled
- Minimize short-term gains
- No special tax strategy

Question 3: ESG preferences:
- No ESG requirements
- ESG-focused
- Exclude certain sectors (specify)

Question 4: Dividend preferences:
- No preference
- Prefer dividend-paying stocks
- Avoid dividends
```

**Output**: Constraints
```json
{
  "constraints": {
    "restricted_securities": [],
    "tax_strategy": "tax_loss_harvesting",
    "esg_preference": "esg_focused",
    "dividend_preference": "prefer_dividends",
    "excluded_sectors": []
  }
}
```

#### B. Preference Management Dashboard

**View Current Preferences**
```
┌─────────────────────────────────────────┐
│ Your Investment Preferences             │
├─────────────────────────────────────────┤
│ Risk Level: Balanced                    │
│ Time Horizon: 10+ years                 │
│ Experience: Intermediate                │
│                                         │
│ Target Allocation:                      │
│ ├─ Equity: 60% (±5%)                   │
│ ├─ Fixed Income: 30% (±5%)             │
│ └─ Cash: 10% (±5%)                     │
│                                         │
│ Constraints:                            │
│ ├─ Tax Strategy: Tax-loss harvesting   │
│ ├─ ESG: ESG-focused                    │
│ └─ Dividends: Prefer dividend stocks   │
│                                         │
│ [Edit Preferences] [View History]      │
└─────────────────────────────────────────┘
```

**Edit Preferences**
- Allow users to update any preference
- Show impact of changes (e.g., "This will increase equity exposure by 15%")
- Require confirmation for significant changes
- Track preference change history

### 2. Backend API Endpoints for Preference Collection

#### Create/Update Preferences

```python
# POST /api/preferences
# Create new preference profile
{
    "client_id": "client_123",
    "risk_profile": {
        "risk_level": "balanced",
        "max_single_position_pct": 85,
        "max_sector_pct": 60,
        "allowed_asset_classes": ["equity", "fixed_income", "cash"]
    },
    "allocation_target": {
        "asset_class_targets": {
            "equity": 0.60,
            "fixed_income": 0.30,
            "cash": 0.10
        },
        "tolerance_bands": {
            "equity": 0.05,
            "fixed_income": 0.05,
            "cash": 0.05
        }
    },
    "constraints": {
        "tax_strategy": "tax_loss_harvesting",
        "esg_preference": "esg_focused",
        "dividend_preference": "prefer_dividends"
    }
}

# PUT /api/preferences/{client_id}
# Update existing preferences
{
    "allocation_target": {
        "asset_class_targets": {
            "equity": 0.70,  # Changed from 0.60
            "fixed_income": 0.20,  # Changed from 0.30
            "cash": 0.10
        }
    }
}

# GET /api/preferences/{client_id}
# Retrieve current preferences
Response:
{
    "client_id": "client_123",
    "risk_profile": {...},
    "allocation_target": {...},
    "constraints": {...},
    "created_at": "2024-01-15T10:00:00Z",
    "updated_at": "2024-04-26T15:30:00Z"
}

# GET /api/preferences/{client_id}/history
# Retrieve preference change history
Response:
[
    {
        "version": 1,
        "timestamp": "2024-01-15T10:00:00Z",
        "changes": {
            "allocation_target.asset_class_targets.equity": {
                "old": 0.50,
                "new": 0.60
            }
        },
        "reason": "Initial setup"
    },
    {
        "version": 2,
        "timestamp": "2024-04-26T15:30:00Z",
        "changes": {
            "allocation_target.asset_class_targets.equity": {
                "old": 0.60,
                "new": 0.70
            }
        },
        "reason": "Increased risk tolerance"
    }
]
```

### 3. Memory Storage for Preferences

The Memory Agent would store preferences as memory items:

```python
# Memory items stored in DynamoDB
[
    {
        "memory_id": "mem_client_123_risk_profile",
        "client_id": "client_123",
        "memory_type": "PREFERENCE",
        "category": "risk_profile",
        "timestamp": "2024-01-15T10:00:00Z",
        "content": "Client prefers balanced risk profile with max 85% single position",
        "relevance_score": 0.95,
        "confidence": 0.98
    },
    {
        "memory_id": "mem_client_123_allocation",
        "client_id": "client_123",
        "memory_type": "PREFERENCE",
        "category": "allocation_target",
        "timestamp": "2024-01-15T10:00:00Z",
        "content": "Target allocation: 60% equity, 30% fixed income, 10% cash",
        "relevance_score": 0.95,
        "confidence": 0.98
    },
    {
        "memory_id": "mem_client_123_tax_strategy",
        "client_id": "client_123",
        "memory_type": "PREFERENCE",
        "category": "constraint",
        "timestamp": "2024-01-15T10:00:00Z",
        "content": "Client prefers tax-loss harvesting strategy",
        "relevance_score": 0.90,
        "confidence": 0.95
    },
    {
        "memory_id": "mem_client_123_esg",
        "client_id": "client_123",
        "memory_type": "PREFERENCE",
        "category": "constraint",
        "timestamp": "2024-01-15T10:00:00Z",
        "content": "Client prefers ESG-focused investments",
        "relevance_score": 0.85,
        "confidence": 0.92
    }
]
```

### 4. Preference Collection Flow in LangGraph

When a user updates preferences, the workflow would:

```
1. User submits preference update via UI
   ↓
2. Backend validates preferences
   ├─ Check allocation targets sum to 100%
   ├─ Validate risk profile constraints
   └─ Verify constraints are compatible
   ↓
3. Store preferences in database
   ├─ Update ClientProfile
   ├─ Update RiskProfile
   ├─ Update AllocationTarget
   └─ Update Constraints
   ↓
4. Store as memory items
   ├─ Create PREFERENCE memory items
   ├─ Set high relevance scores
   └─ Store in DynamoDB
   ↓
5. Trigger preference update event
   ├─ Log audit event
   ├─ Notify user of confirmation
   └─ Update UI
   ↓
6. Next rebalance uses new preferences
   ├─ hydrate_memory retrieves updated preferences
   ├─ LLM synthesizes preference context
   └─ Recommendations reflect new preferences
```

### 5. Preference-Driven Recommendation Personalization

Once preferences are collected, the Memory Agent uses them to personalize recommendations:

**Example: User Updates Dividend Preference**

```
User Action: Changes dividend preference from "no preference" to "prefer dividends"

Memory Update:
{
    "memory_id": "mem_client_123_dividend_update",
    "timestamp": "2024-04-26T15:30:00Z",
    "content": "Client updated dividend preference to prefer dividend-paying stocks",
    "relevance_score": 0.98
}

Next Rebalance:
1. hydrate_memory retrieves preferences
2. LLM synthesizes: "Client prefers dividend-paying stocks for income generation"
3. Rebalancing Agent considers dividend yield in recommendations
4. Recommendation: "Increase allocation to dividend aristocrats (e.g., JNJ, PG, KO)"
5. User sees personalized recommendation aligned with their preference
```

### 6. Preference Collection Triggers

Preferences can be collected at multiple points:

**1. Initial Onboarding**
- New user creates account
- Completes risk assessment questionnaire
- Sets initial allocation preferences
- Specifies constraints

**2. Periodic Review**
- Annual preference review (e.g., "Has your risk tolerance changed?")
- Life event triggers (marriage, retirement, inheritance)
- Market condition changes (e.g., "Market volatility increased, adjust risk?")

**3. Explicit Update**
- User manually updates preferences via dashboard
- User responds to recommendation feedback
- User adjusts constraints based on new goals

**4. Implicit Learning** (Future Enhancement)
- Track which recommendations user approves/rejects
- Infer preference changes from approval patterns
- Suggest preference updates based on behavior

## Implementation Roadmap

### Phase 1: Basic Preference Collection (Current)
- ✅ Data structures defined (ClientProfile, RiskProfile, AllocationTarget)
- ✅ Seed data with hardcoded preferences
- ⏳ API endpoints for preference CRUD
- ⏳ Frontend preference management UI

### Phase 2: Memory Integration
- ⏳ Store preferences as memory items
- ⏳ Retrieve preferences in hydrate_memory node
- ⏳ LLM synthesis of preference context
- ⏳ Preference-driven personalization

### Phase 3: Advanced Collection
- ⏳ Risk assessment questionnaire UI
- ⏳ Preference change history tracking
- ⏳ Preference validation and conflict detection
- ⏳ Preference impact analysis

### Phase 4: Intelligent Learning
- ⏳ Track user approval/rejection of recommendations
- ⏳ Infer preference changes from behavior
- ⏳ Suggest preference updates
- ⏳ A/B test different preference sets

## Data Storage Architecture

### DynamoDB Tables

**1. ClientPreferences Table**
```
PK: client_id
SK: preference_type (RISK_PROFILE, ALLOCATION_TARGET, CONSTRAINTS)
Attributes:
  - client_id
  - preference_type
  - preference_data (JSON)
  - version
  - created_at
  - updated_at
  - created_by
  - updated_by
```

**2. PreferenceHistory Table**
```
PK: client_id
SK: timestamp#version
Attributes:
  - client_id
  - version
  - timestamp
  - changes (JSON diff)
  - reason
  - created_by
```

**3. MemoryItems Table** (Existing)
```
PK: client_id
SK: memory_id
Attributes:
  - memory_id
  - client_id
  - memory_type (PREFERENCE, DECISION, CONSTRAINT, etc.)
  - category
  - content
  - timestamp
  - relevance_score
  - confidence
```

## Security and Privacy Considerations

### 1. Access Control
- Users can only view/edit their own preferences
- Advisors can view client preferences with explicit consent
- Audit trail tracks all preference changes

### 2. Data Validation
- Validate all preference inputs
- Check for conflicting constraints
- Verify allocation targets sum to 100%

### 3. Audit Logging
- Log all preference changes
- Track who made changes and when
- Store change reasons for compliance

### 4. Encryption
- Encrypt sensitive preference data at rest
- Use HTTPS for preference API endpoints
- Encrypt preference data in transit

## Example: Complete Preference Collection Flow

### User Journey

```
1. New User Signup
   ↓
2. Onboarding Wizard
   ├─ Risk Assessment (5 questions)
   ├─ Allocation Preferences (3 questions)
   └─ Constraints (4 questions)
   ↓
3. Preferences Stored
   ├─ ClientProfile created
   ├─ RiskProfile created
   ├─ AllocationTarget created
   ├─ Constraints stored
   └─ Memory items created
   ↓
4. First Rebalance Request
   ├─ hydrate_memory retrieves preferences
   ├─ LLM synthesizes: "New investor, balanced risk, prefers dividends"
   ├─ Recommendations generated with preferences
   └─ User sees personalized recommendation
   ↓
5. User Approves Recommendation
   ├─ Approval stored
   ├─ Preference confidence increases
   └─ Memory updated
   ↓
6. Annual Review
   ├─ System suggests preference review
   ├─ User updates risk tolerance
   ├─ New preferences stored
   └─ Next rebalance uses updated preferences
```

## Conclusion

The Asset Management application has the data structures in place to collect and use user preferences. The next steps are:

1. **Build Frontend UI** for preference collection and management
2. **Implement API Endpoints** for preference CRUD operations
3. **Integrate with Memory Agent** to retrieve and synthesize preferences
4. **Add Preference Validation** to ensure consistency
5. **Track Preference History** for audit and learning

Once these are implemented, the system will be able to provide truly personalized recommendations based on each user's unique preferences, risk tolerance, and constraints.
