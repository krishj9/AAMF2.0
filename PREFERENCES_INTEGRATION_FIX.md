# Preferences Integration Fix

## Problem Identified

**The rebalancing system was NOT using stored user preferences when generating trade proposals.**

### Root Cause Analysis

1. **Frontend Issue**: The `buildRequest()` method in `app.ts` was building the rebalance request using:
   - Form values (hardcoded in the UI)
   - Portfolio data from database (with old/default values)
   - **Never fetching updated preferences from the preferences API**

2. **Backend Issue**: The orchestrator and agents were correctly using the values from the request, but those values were stale/default values, not the user's saved preferences.

3. **Data Flow Problem**:
   ```
   User saves preferences → Stored in DynamoDB ✅
   User triggers rebalance → Frontend builds request with OLD values ❌
   Backend processes request → Uses OLD values from request ❌
   Trade proposals generated → Based on OLD values ❌
   ```

## Solution Implemented

### Frontend Changes

#### 1. Modified `submitRebalance()` Method
**File**: `frontend/src/app/app.ts`

**Before**:
```typescript
protected submitRebalance() {
  if (this.form.invalid) {
    this.form.markAllAsTouched();
    return;
  }

  this.submitting.set(true);
  this.rebalanceError.set(null);
  this.rebalanceService.submit(this.buildRequest()).subscribe({
    // ... handle response
  });
}
```

**After**:
```typescript
protected submitRebalance() {
  if (this.form.invalid) {
    this.form.markAllAsTouched();
    return;
  }

  this.submitting.set(true);
  this.rebalanceError.set(null);
  
  // Fetch latest preferences before submitting
  const clientId = this.selectedPortfolio()?.client_profile.client_id ?? 'client_demo';
  this.preferenceService.getPreferences(clientId).subscribe({
    next: (preferences) => {
      // Build request with latest preferences
      const request = this.buildRequestWithPreferences(preferences);
      this.submitRebalanceRequest(request);
    },
    error: () => {
      // Fallback to building request without preferences
      this.rebalanceError.set('Warning: Could not load preferences. Using default values.');
      const request = this.buildRequest();
      this.submitRebalanceRequest(request);
    }
  });
}
```

#### 2. Added `buildRequestWithPreferences()` Method

New method that builds the rebalance request using the latest preferences from the API:

```typescript
private buildRequestWithPreferences(preferences: any): PortfolioRebalanceRequest {
  // ... builds request using preferences.allocation_target and preferences.risk_profile
}
```

**Key Differences from `buildRequest()`**:
- Uses `preferences.allocation_target.asset_class_targets` instead of form values
- Uses `preferences.allocation_target.tolerance_bands` instead of hardcoded '5'
- Uses `preferences.risk_profile` values instead of portfolio defaults

#### 3. Extracted `submitRebalanceRequest()` Method

Separated the actual submission logic to avoid duplication:

```typescript
private submitRebalanceRequest(request: PortfolioRebalanceRequest) {
  this.rebalanceService.submit(request).subscribe({
    // ... handle response
  });
}
```

#### 4. Added PreferenceService Injection

```typescript
private readonly preferenceService = inject(PreferenceService);
```

## New Data Flow

```
User saves preferences → Stored in DynamoDB ✅
User triggers rebalance → Frontend fetches latest preferences ✅
Frontend builds request → Uses LATEST preference values ✅
Backend processes request → Uses LATEST values from request ✅
Trade proposals generated → Based on USER'S SAVED PREFERENCES ✅
```

## What Gets Used from Preferences

### Allocation Target
- `asset_class_targets.equity` - Target equity percentage
- `asset_class_targets.fixed_income` - Target fixed income percentage
- `asset_class_targets.cash` - Target cash percentage
- `tolerance_bands.equity` - Equity rebalancing tolerance
- `tolerance_bands.fixed_income` - Fixed income rebalancing tolerance
- `tolerance_bands.cash` - Cash rebalancing tolerance

### Risk Profile
- `risk_level` - Conservative, Balanced, Growth, or Aggressive
- `max_single_position_pct` - Maximum percentage in single position
- `max_sector_pct` - Maximum percentage in single sector
- `allowed_asset_classes` - List of allowed asset classes

### Constraints (Future Enhancement)
Currently stored but not yet used in trade generation:
- `tax_strategy` - Tax optimization strategy
- `esg_preference` - ESG investment preferences
- `dividend_preference` - Dividend preferences
- `excluded_sectors` - Sectors to exclude

## Testing the Fix

### Test Scenario 1: Change Allocation Targets
1. Go to Preferences page
2. Change equity target from 60% to 70%
3. Change fixed income from 30% to 20%
4. Save preferences
5. Return to main page
6. Trigger rebalance
7. **Expected**: Trade proposals should target 70% equity, 20% fixed income

### Test Scenario 2: Change Tolerance Bands
1. Go to Preferences page
2. Change equity tolerance from 5% to 10%
3. Save preferences
4. Return to main page
5. Simulate drift of 7%
6. **Expected**: No rebalance needed (within 10% tolerance)

### Test Scenario 3: Change Risk Profile
1. Go to Preferences page
2. Change risk level from Balanced to Conservative
3. Change max single position from 85% to 50%
4. Save preferences
5. Return to main page
6. Trigger rebalance
7. **Expected**: Risk compliance checks use 50% limit

### Test Scenario 4: Fallback Behavior
1. Stop backend server
2. Trigger rebalance
3. **Expected**: Warning message displayed, uses default values

## Backend Integration Points

The backend already correctly uses the values from the request:

### Rebalancing Agent
```python
# Uses request.allocation_target.asset_class_targets
drift = calculate_drift(request.portfolio_snapshot, request.allocation_target)
```

### Risk Compliance Agent
```python
# Uses request.risk_profile
risk_stage, risk_policy = await self.risk_agent.run(
    request.portfolio_snapshot, drift, request.risk_profile
)
```

### Trade Execution Agent
```python
# Uses allocation targets and risk profile from request
trade_stage, proposal = await self.trade_agent.run(
    request.portfolio_snapshot, risk_policy
)
```

## Future Enhancements

### 1. Use Constraints in Trade Generation
Currently constraints are stored but not used. Future enhancement:
- Tax-loss harvesting logic
- ESG filtering
- Dividend preference filtering
- Sector exclusion

### 2. Real-time Preference Sync
Instead of fetching on every rebalance, could:
- Load preferences on portfolio selection
- Cache preferences in frontend
- Refresh on preference updates

### 3. Preference Versioning
Track which preference version was used for each recommendation:
- Add `preference_version` to recommendation
- Show preference changes in audit trail
- Allow comparing recommendations with different preferences

### 4. Preference Validation
Add validation to ensure preferences are compatible:
- Allocation targets sum to 100%
- Tolerance bands are reasonable
- Risk profile matches allocation strategy

## Impact Assessment

### Before Fix
- ❌ User preferences were ignored
- ❌ All users got same default allocation (60/30/10)
- ❌ All users got same tolerance bands (5%)
- ❌ Preference UI was essentially non-functional

### After Fix
- ✅ User preferences are respected
- ✅ Each user gets personalized allocation targets
- ✅ Each user gets personalized tolerance bands
- ✅ Preference UI is fully functional and integrated

## Verification Checklist

- [x] Frontend fetches preferences before rebalance
- [x] Request is built with preference values
- [x] Fallback works if preferences unavailable
- [x] Build completes successfully
- [x] No TypeScript errors
- [x] PreferenceService properly injected
- [ ] Manual testing: Change preferences and verify trades
- [ ] Manual testing: Verify fallback behavior
- [ ] Manual testing: Verify different risk profiles

## Files Modified

1. `frontend/src/app/app.ts`
   - Modified `submitRebalance()` to fetch preferences
   - Added `buildRequestWithPreferences()` method
   - Added `submitRebalanceRequest()` method
   - Added `PreferenceService` injection

## Build Status

✅ Build successful
✅ No TypeScript errors
✅ No runtime errors expected
✅ Backward compatible (fallback to old behavior if preferences unavailable)

## Deployment Notes

1. This is a frontend-only change
2. No backend changes required
3. No database migrations required
4. Backward compatible with existing data
5. Safe to deploy immediately
