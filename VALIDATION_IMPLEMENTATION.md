# Allocation Validation Implementation

## Summary
Implemented validation in the preferences screen to prevent users from setting target allocations that violate risk profile concentration limits.

## Changes Made

### 1. Updated Allocation Presets
**File**: `frontend/src/app/preferences/preferences.component.ts`

Changed the "Aggressive" preset from violating concentration limits:
- **Before**: Equity 90%, Fixed Income 10%, Cash 0%
- **After**: Equity 85%, Fixed Income 10%, Cash 5%

This ensures all presets stay within the default 85% max concentration limit.

### 2. Added Validation Logic

#### Concentration Warning
```typescript
protected readonly concentrationWarning = computed(() => {
  const riskValues = this.riskForm.getRawValue();
  const allocationValues = this.allocationForm.getRawValue();
  const maxConcentration = riskValues.maxSinglePositionPct;
  
  const warnings: string[] = [];
  
  if (allocationValues.equityTarget > maxConcentration) {
    warnings.push(`Equity target (${allocationValues.equityTarget}%) exceeds max concentration limit (${maxConcentration}%)`);
  }
  // Similar checks for fixed income and cash
  
  return warnings;
});
```

#### Cash Warning
```typescript
protected readonly cashWarning = computed(() => {
  const allocationValues = this.allocationForm.getRawValue();
  if (allocationValues.cashTarget === 0) {
    return 'Warning: 0% cash allocation provides no liquidity buffer for rebalancing operations. Consider maintaining at least 5% cash.';
  }
  return null;
});
```

#### Validation Check
```typescript
protected readonly hasValidationErrors = computed(() => {
  return !this.allocationValid() || this.concentrationWarning().length > 0;
});
```

### 3. Updated Navigation Logic

Modified `nextStep()` to block progression when validation errors exist:
```typescript
if (this.hasValidationErrors()) {
  this.allocationForm.markAllAsTouched();
  console.error('Allocation has validation errors:', {
    allocationValid: this.allocationValid(),
    concentrationWarnings: this.concentrationWarning()
  });
  return;
}
```

### 4. Added UI Warning Displays

**File**: `frontend/src/app/preferences/preferences.component.html`

Added two warning sections in the allocation step:

#### Concentration Errors (Blocking)
```html
@if (concentrationWarning().length > 0) {
  <div class="validation-errors">
    <div class="error-icon">⚠️</div>
    <div class="error-content">
      <strong>Concentration Limit Violations:</strong>
      <ul>
        @for (warning of concentrationWarning(); track warning) {
          <li>{{ warning }}</li>
        }
      </ul>
      <p class="error-hint">Reduce allocation percentages to stay within the max single position limit set in your risk profile.</p>
    </div>
  </div>
}
```

#### Cash Warning (Informational)
```html
@if (cashWarning()) {
  <div class="validation-warning">
    <div class="warning-icon">ℹ️</div>
    <div class="warning-content">
      {{ cashWarning() }}
    </div>
  </div>
}
```

### 5. Added Styling

**File**: `frontend/src/app/preferences/preferences.component.scss`

Added styles for validation messages:
- `.validation-errors` - Red border, danger background for blocking errors
- `.validation-warning` - Orange border, warning background for informational warnings

## Business Logic

### Why Recommendations Get Blocked

The system blocks recommendations when:

1. **Concentration Violation**: Any single asset class exceeds `max_single_position_pct` from the risk profile
   - Default limit: 85%
   - Evaluated in: `backend/app/services/policy.py`
   - Verdict: `NON_COMPLIANT`

2. **Missing Risk Profile**: No risk profile provided
   - Verdict: `UNRESOLVED`

3. **Guardrail Violations**: Bedrock Guardrails detect sensitive content (rare)
   - Verdict: `BLOCKED`

### Validation Flow

1. User selects risk level on screen 1 → Sets `max_single_position_pct` (e.g., 85%)
2. User moves to allocation screen 2 → Auto-populates safe allocation
3. User modifies allocation → Real-time validation checks concentration limits
4. If any asset class > max concentration → Shows error, blocks progression
5. If cash = 0% → Shows warning (informational only, doesn't block)
6. User can only proceed when allocations are valid

## Testing

### Test Scenario 1: Concentration Violation
1. Set risk profile with max concentration 85%
2. Try to set equity target to 90%
3. **Expected**: Red error message appears, "Next" button blocked
4. **Message**: "Equity target (90%) exceeds max concentration limit (85%)"

### Test Scenario 2: Zero Cash Warning
1. Set allocation to 85/15/0
2. **Expected**: Orange warning appears, but can still proceed
3. **Message**: "Warning: 0% cash allocation provides no liquidity buffer..."

### Test Scenario 3: Valid Allocation
1. Set allocation to 85/10/5
2. **Expected**: No errors, can proceed to next step
3. **Result**: Preferences save successfully, no blocking on rebalance

## Benefits

1. **Prevents Policy Blocks**: Users can't create allocations that will be blocked by policy
2. **Clear Feedback**: Users understand why certain allocations are invalid
3. **Guided Experience**: Auto-population from risk level ensures safe defaults
4. **Flexibility**: Warnings (like 0% cash) inform but don't block
5. **Consistency**: Frontend validation matches backend policy rules

## Next Steps

If you want to enhance this further:
1. Add validation for sector concentration limits
2. Show visual indicators (red/green) on input fields
3. Add a "Why?" tooltip explaining concentration risk
4. Allow advanced users to override warnings with confirmation
5. Display the specific policy rule being violated in the main app when blocked
