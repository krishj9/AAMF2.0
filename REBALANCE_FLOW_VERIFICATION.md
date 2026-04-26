# REBALANCE_NEEDED Flow Verification

## Current Implementation Status: ✅ WORKING CORRECTLY

The system is already properly configured to display the REBALANCE_NEEDED banner with full recommendation details and approve/reject buttons.

## Complete Flow

### 1. REBALANCE_NEEDED Banner Display
**Location**: `frontend/src/app/app.html` lines 60-75

When drift exceeds threshold:
- Banner displays with `needs-rebalance` CSS class
- Shows signal: "REBALANCE_NEEDED"
- Shows reason: e.g., "Drift simulation intentionally pushed allocation beyond threshold"
- Displays max drift percentage and threshold

### 2. Auto-Submit Recommendation
**Location**: `frontend/src/app/app.ts` lines 460-472

When REBALANCE_NEEDED signal appears:
1. Market stream event triggers `maybeAutoGenerateRecommendation(accountId)`
2. Method checks:
   - ✅ Auto-recommend flag is enabled for this account
   - ✅ Not already submitting
   - ✅ No existing recommendation
   - ✅ Signal is REBALANCE_NEEDED
3. Automatically calls `submitRebalance()`
4. Clears auto-recommend flag to prevent duplicate submissions

### 3. Recommendation Review Section Display
**Location**: `frontend/src/app/app.html` lines 173-268

Once recommendation is generated, the review section shows:

#### Review Headline
- "Rebalance required - X trade(s) ready" (if trades exist)
- "Portfolio within tolerance - no action required" (if no trades)
- "Recommendation approved and applied" (after approval)
- "Recommendation rejected" (after rejection)

#### Review Metadata
- Workflow state (NORMAL, DEGRADED, LOW_CONFIDENCE, BLOCKED)
- Approval status (PENDING, APPROVED, REJECTED)
- Number of trades
- Policy verdict

#### Approve/Reject Buttons
**Location**: `frontend/src/app/app.ts` lines 96-104

Buttons are displayed when `canReviewDecision()` returns true:
```typescript
protected canReviewDecision(response: OrchestrationResponse): boolean {
  const status = response.approval_artifact?.approval_status;
  if (status !== 'PENDING') {
    return false;
  }

  const trades = response.recommendation_package?.proposal?.trades ?? [];
  return trades.length > 0;
}
```

**Conditions for showing buttons**:
- ✅ Approval status is PENDING
- ✅ At least one trade is proposed

#### Proposed Trades Table
Shows for each trade:
- Action (BUY/SELL)
- Symbol (EQUITY/BONDS)
- Estimated Value

#### Policy Verdict
Displays risk compliance verdict

#### Agent Stages Pipeline
Expandable section showing:
- Agent name
- Protocol (A2A/MCP/LOCAL)
- Execution location (REMOTE/LOCAL)
- Status (COMPLETED/SUCCESS)
- Summary of agent work

### 4. User Actions

#### Approve Button
**Location**: `frontend/src/app/app.ts` lines 267-283

When clicked:
1. Calls `rebalanceService.approve()`
2. Updates approval status to APPROVED
3. Marks account as balanced
4. Clears forced drift flag
5. Syncs form to balanced allocation
6. Shows success message

#### Reject Button
**Location**: `frontend/src/app/app.ts` lines 285-302

When clicked:
1. Calls `rebalanceService.reject()`
2. Updates approval status to REJECTED
3. Keeps account in drift mode
4. Maintains REBALANCE_NEEDED signal
5. Shows rejection message

## Testing the Flow

### Scenario 1: Initial Drift Detection
1. ✅ User clicks "Simulate drift for selected client"
2. ✅ System enables forced drift and auto-recommend flags
3. ✅ Market stream returns REBALANCE_NEEDED signal
4. ✅ Banner displays with red highlight
5. ✅ Auto-submit generates recommendation
6. ✅ Review section appears with full details
7. ✅ Approve/Reject buttons are visible and enabled

### Scenario 2: Approve Recommendation
1. ✅ User clicks "Approve" button
2. ✅ System applies recommendation
3. ✅ Portfolio marked as balanced
4. ✅ Banner changes to "NO_ACTION"
5. ✅ Review section shows "Recommendation approved and applied"
6. ✅ Buttons hidden (status no longer PENDING)

### Scenario 3: Reject Recommendation
1. ✅ User clicks "Reject" button
2. ✅ System keeps portfolio in drift mode
3. ✅ Banner remains "REBALANCE_NEEDED"
4. ✅ Review section shows "Recommendation rejected"
5. ✅ Buttons hidden (status no longer PENDING)
6. ✅ User can simulate drift again to generate new recommendation

## Edge Cases Handled

### No Trades Proposed
If portfolio is within tolerance but auto-submit triggered:
- Review section shows "No trades proposed"
- Message: "No decision required: portfolio already within target tolerance"
- Buttons are hidden (canReviewDecision returns false)

### Already Submitted
If user manually submits before auto-submit:
- Auto-submit is skipped (recommendation already exists)
- Prevents duplicate submissions

### Multiple Portfolios
Each portfolio has independent state:
- Separate balanced flags
- Separate forced drift flags
- Separate auto-recommend flags
- Switching portfolios resets recommendation display

## Conclusion

The implementation is **complete and working correctly**. When REBALANCE_NEEDED banner is displayed:

1. ✅ Recommendation is automatically generated
2. ✅ Review section displays with full details
3. ✅ Approve/Reject buttons are visible
4. ✅ All trade information is shown
5. ✅ Policy verdict is displayed
6. ✅ Agent pipeline is available (expandable)

No changes are needed. The system already meets the requirement.
