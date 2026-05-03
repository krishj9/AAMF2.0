# Enhancement Prompts: Showcasing Agentic AI Behavior

> These prompts are designed to be given sequentially to a coding agent. Each builds on the previous. Start with Phase 0 and validate before moving to Phase 1.
>
> **Context file**: Always include `AGENT_CONTEXT.md` in the agent's context before running any prompt.

---

## UI Rebuild Strategy

**Rebuild the view layer. Keep the logic layer.**

The current `app.ts` contains working, debugged application logic — Angular Signals state, SSE market stream, approval flow, preference reload, portfolio selection. Rebuilding this from scratch means re-solving all the same problems (CORS, Decimal types, hash verification, preference timing). That effort has no upside.

What actually needs replacing is the HTML and SCSS — the layout is a single long page with no information hierarchy, and the recommendation card shows raw data strings instead of visual components.

**Keep untouched:**
- `frontend/src/app/app.ts` — all signals, methods, service calls
- `frontend/src/app/core/api/` — the entire service layer
- `frontend/src/app/preferences/preferences.component.ts` — wizard logic

**Rewrite completely:**
- `frontend/src/app/app.html` — new two-panel dashboard layout
- `frontend/src/app/app.scss` — new design system built on existing color variables
- `frontend/src/app/preferences/preferences.component.html` — updated to match new design
- `frontend/src/app/preferences/preferences.component.scss` — updated to match new design

**Target layout:**
```
┌─────────────────────────────────────────────────────┐
│  Header: title + portfolio selector + preferences   │
├──────────────────────┬──────────────────────────────┤
│  LEFT PANEL          │  RIGHT PANEL                 │
│                      │                              │
│  Market Monitor      │  Live Agent Pipeline         │
│  (drift, signal)     │  (streaming stages)          │
│                      │                              │
│  Portfolio Intake    │  Recommendation Review       │
│  (position values,   │  (verdict, trades,           │
│   targets)           │   allocation charts)         │
│                      │                              │
│                      │  Q&A Chat Panel (Phase 3)    │
└──────────────────────┴──────────────────────────────┘
```

This separates "inputs" (left) from "AI outputs" (right) — a much clearer mental model.

---

## Phase 0 — Two-Panel Dashboard Rebuild

**Goal**: Establish the new layout foundation before adding any new features. All subsequent phases build on top of this structure.

---

### Prompt 0.1 — Rewrite the View Layer

```
Read AGENT_CONTEXT.md fully before starting.

The current UI is a single long page with no clear information hierarchy. The goal is to rewrite app.html and app.scss with a professional two-panel dashboard layout while keeping all TypeScript logic in app.ts completely intact.

IMPORTANT: Do not modify app.ts, any file in core/api/, or preferences.component.ts. Only rewrite the HTML and SCSS files.

New layout structure for app.html:

1. **App Shell** — full-height layout with a fixed header and scrollable content area.

2. **Header bar** (fixed top):
   - Left: app title "Asset Management" + subtitle "AI-Powered Portfolio Advisor"
   - Center: portfolio selector dropdown (existing `selectPortfolio()` binding)
   - Right: "⚙ Preferences" button (existing `navigateToPreferences()` binding) + backend health indicator dot (green/red based on `backendHealth()`)

3. **Two-column main content** (side by side, equal width, scrollable independently):

   **Left column — "Portfolio & Market"**:
   - Market Monitor card: regime, equity move, rate move, portfolio value from `displayMarketEvent()`
   - Rebalance signal banner: `REBALANCE_NEEDED` in rose/red, `WATCH` in amber, `NO_ACTION` in green
   - Drift breakdown: three mini cards for equity/fixed income/cash showing current %, drift %, tolerance
   - Position Values card: equity value, fixed income value, cash value (readonly inputs, existing form bindings)
   - Target Allocation card: equity %, fixed income %, cash % (editable inputs, existing form bindings)
   - "Simulate Drift" button (existing `simulateDriftAgain()` binding)
   - "Generate Recommendation" submit button (existing `submitRebalance()` binding, shows spinner when `submitting()`)

   **Right column — "AI Recommendation"**:
   - When no recommendation: empty state with icon and "Submit portfolio to generate a recommendation"
   - When `submitting()`: skeleton loading state with animated placeholder cards
   - When recommendation exists: full recommendation review (see below)

4. **Recommendation Review** (right column, when recommendation exists):
   - Summary callout box: blue background for NORMAL, amber for DEGRADED, red for BLOCKED
   - Status bar: workflow state badge + approval status badge + policy verdict badge + trade count
   - Approval action buttons (existing bindings): Approve / Reject / Acknowledge Policy Block
   - Approval message (existing `approvalMessage()`)
   - Agent Pipeline section (always visible, not hidden behind toggle): list of agent stage cards
   - Proposed Trades section: trade table with action/symbol/value
   - Policy Verdict section: verdict badge + rule results checklist

5. **Preferences page** (separate route, rewrite preferences.component.html):
   - Keep the 4-step wizard structure
   - Match the new design system: same header style, same card style, same button style
   - Progress steps should be horizontal at the top, not vertical

Design system rules for app.scss:
- Use the existing SCSS color variables: `$color-bg-primary`, `$color-bg-secondary`, `$color-bg-tertiary`, `$color-border`, `$color-accent`, `$color-success`, `$color-warning`, `$color-danger`, `$color-text-primary`, `$color-text-secondary`
- Cards: `background: $color-bg-secondary`, `border: 1px solid $color-border`, `border-radius: 8px`, `padding: 1.25rem`
- Badges: small pill shapes, colored by status
- Buttons: primary (accent blue fill), secondary (transparent with border), danger (red fill)
- Typography: Inter font, already loaded. Headings 600 weight, body 400 weight
- Two-column layout: CSS Grid `grid-template-columns: 1fr 1fr`, gap 1.5rem, min-width 320px per column
- Responsive: below 1024px, stack columns vertically
- No glow effects, no box shadows heavier than `0 1px 3px rgba(0,0,0,0.3)`

After rewriting, run `npm run build` in the frontend directory to verify it compiles. Fix any template binding errors before proceeding.
```

---

## Phase 1 — Make the Agent Pipeline Visible and Alive

**Status: COMPLETE** — Built as part of Phase 0 view layer rebuild.

**What was built:**
- Two-panel dashboard: left = portfolio/market inputs, right = AI outputs
- Full-width alert strip spanning both columns for REBALANCE_NEEDED / WATCH signals
- Agent Pipeline card always visible on right column (collapsible, starts collapsed when recommendation exists)
- Recommendation Review card leads the right column — decision is always above the fold
- Recommendation card structured in 4 sections: Situation → What Changes → Policy Checks → Decision Bar
- Decision Bar has contextual prompt + full-width Approve/Reject buttons
- Skeleton loading states while agents run
- Context-aware form buttons: balanced portfolio shows only "Simulate Drift", drifting with no recommendation shows "Generate Recommendation", recommendation already showing shows only "Simulate New Drift Scenario"

**Note on streaming (Prompt 1.1):** The pipeline currently shows all stages after workflow completes (not live streaming). True SSE streaming of individual stage updates requires backend changes to the rebalance endpoint. This is deferred — the current UX is significantly better than the original hidden toggle, and streaming can be added in a future phase without breaking anything.

---

### Prompt 1.2 — Rich Recommendation Display with LLM Reasoning

**Status: COMPLETE** — Built as part of Phase 0 view layer rebuild.

**What was built:**
- Policy verdict section with ✓/✗ rule checklist
- Allocation comparison bars (current → target) with color coding
- Trade list with rationale text per trade
- Summary callout styled by workflow state (blue/amber/red)
- Status badge bar (workflow state, approval status, policy verdict, trade count)

---

## Phase 2 — Wire Up the Placeholder Agents with Real LLM Calls

**Goal**: The research, sentiment, and rebalancing agents currently return static placeholder data. Replace them with real LLM-powered implementations that produce visible, meaningful output in the UI.

---

### Prompt 2.1 — Real Trade Proposal Generation

```
Read AGENT_CONTEXT.md fully before starting.

The `generate_execution_proposal` node in `backend/app/services/langgraph_graph.py` currently returns a stub with no real trades. Implement real trade proposal generation.

Backend changes:

1. In `backend/app/agents/trade_execution.py`, implement the `run()` method to:
   a. Calculate required trades from drift: for each asset class outside tolerance, compute the dollar amount to buy or sell to reach the target allocation.
   b. Formula: trade_value = (target_pct - current_pct) / 100 * total_portfolio_value. Positive = BUY, negative = SELL.
   c. Only generate trades for asset classes where abs(drift_pct) > tolerance_pct.
   d. Create a `TradeProposal` for each trade with: trade_id (new_id("trade")), symbol (use the asset class name uppercased), action (BUY/SELL), estimated_value (Decimal), rationale (explain why this trade is needed based on drift).
   e. If LLM is enabled (FEATURE_TRADE_PROPOSAL_AGENT_LLM_ENABLED), call Bedrock to enhance the rationale with a more detailed explanation referencing the specific drift amounts, risk profile, and market context from the state.
   f. Return an `ExecutionProposalResponse` with proposal_status="READY_FOR_REVIEW", the trades list, and estimated_impact showing the post-trade allocation.

2. Wire the agent into `_placeholder_trade_proposal_node` in `langgraph_graph.py` — replace the stub with a real call to `TradeExecutionAgent.run()`.

3. The `estimated_impact` dict should show what the allocation will look like after trades execute.

Frontend changes:
1. The trades table already exists. Ensure it shows the new trade data correctly.
2. Add a "Post-Trade Allocation Preview" section below the trades table showing the `proposed_allocation` as a simple percentage breakdown, with an arrow (→) showing current → proposed for each asset class.

All financial calculations must use Python `Decimal`, not `float`. Follow the existing agent pattern: deterministic calculation first, LLM enhancement second, fallback on failure.
```

---

### Prompt 2.2 — Research Agent with Real Bedrock Calls

```
Read AGENT_CONTEXT.md fully before starting.

The `run_research` node returns a static placeholder. The Research Agent at `remote-agents/research-agent/` exists as a service but is not wired to real LLM calls.

Implement real research agent behavior:

Backend changes (remote-agents/research-agent/):

1. In the research agent's main handler, implement a `research_portfolio` function that:
   a. Takes the portfolio symbols and allocation context from the A2A request envelope.
   b. Calls Bedrock (claude-3-5-sonnet) with a prompt asking for: current market regime assessment, key risks for the given asset allocation, and 2-3 actionable insights relevant to rebalancing.
   c. The prompt should include: the asset classes in the portfolio, current allocation percentages, and the rebalance signal (REBALANCE_NEEDED/WATCH/NO_ACTION).
   d. Parse the LLM response into: `market_context` (string summary), `key_insights` (list of strings), `regime` (BULL/BEAR/NEUTRAL/VOLATILE), `confidence` (0-1 float).
   e. Respect FEATURE_RESEARCH_AGENT_LLM_ENABLED — if false, return a structured placeholder with regime=NEUTRAL.

2. In `backend/app/agents/research.py`, update the `run()` method to pass the portfolio context (asset classes, current allocation, rebalance signal) in the A2A request envelope.

3. In `backend/app/services/langgraph_graph.py`, update `_placeholder_research_node` to call the real `ResearchAgent.run()` and store the structured output in `state["research_output"]`.

Frontend changes:
1. Add a "Market Research" section to the recommendation review card that displays:
   - Market regime badge (BULL=green, BEAR=red, NEUTRAL=gray, VOLATILE=amber)
   - Key insights as a bulleted list
   - Research confidence score
   - A note showing "via A2A Research Agent" to make the distributed architecture visible

This makes the A2A protocol visible to the user — they can see that a remote agent contributed to the recommendation.
```

---

### Prompt 2.3 — Sentiment Agent with Real MCP Calls

```
Read AGENT_CONTEXT.md fully before starting.

The `run_sentiment_analysis` node returns NEUTRAL placeholder. The Sentiment MCP server at `mcp-servers/sentiment/` exists but is not wired to real LLM calls.

Implement real sentiment analysis:

Backend changes (mcp-servers/sentiment/):

1. Implement the `analyze_symbol_news_sentiment` MCP tool to:
   a. Accept a symbol (asset class name like "equity", "fixed_income", "cash") and optional context.
   b. Call Bedrock (claude-3-haiku) with a prompt asking for sentiment assessment for that asset class given current market conditions.
   c. Return: `sentiment` (POSITIVE/NEGATIVE/NEUTRAL/MIXED), `score` (-1.0 to 1.0), `summary` (1-2 sentence explanation), `confidence` (0-1).
   d. Respect FEATURE_SENTIMENT_AGENT_LLM_ENABLED — if false, return NEUTRAL with score 0.0.

2. In `backend/app/agents/sentiment.py`, update `run()` to call the MCP tool for each asset class in the portfolio and aggregate results.

3. In `backend/app/services/langgraph_graph.py`, update `_placeholder_sentiment_node` to call the real `SentimentAgent.run()`.

Frontend changes:
1. Add a "Market Sentiment" row to the allocation comparison section showing a sentiment indicator per asset class:
   - Small colored dot: green (POSITIVE), red (NEGATIVE), gray (NEUTRAL), amber (MIXED)
   - Sentiment score as a mini bar (-1 to +1)
   - Tooltip on hover showing the sentiment summary text
2. Add a note "via MCP Sentiment Server" to make the MCP protocol visible.

This makes both the A2A and MCP protocols tangible to the user — they can see which parts of the recommendation came from which remote service.
```

---

## Phase 3 — Conversational Reasoning Panel

**Goal**: Add a conversational interface where the user can ask the AI to explain its recommendation, challenge a trade, or ask "what if" questions. This is the most visible showcase of agentic behavior.

---

### Prompt 3.1 — Recommendation Q&A Chat Panel

```
Read AGENT_CONTEXT.md fully before starting.

Add a conversational Q&A panel to the recommendation review card. After a recommendation is generated, the user should be able to ask natural language questions about it and get LLM-powered answers grounded in the actual recommendation data.

Backend changes:

1. Add a new route `POST /api/recommendations/{approval_id}/explain` in a new file `backend/app/api/routes/explain.py`.
2. The request body: `{ "question": string, "actor_id": string }`.
3. The handler should:
   a. Load the approval artifact from the store.
   b. Build a context string from the recommendation: summary, trades, policy verdict, drift items, agent stages, risk profile.
   c. Call Bedrock (claude-3-5-sonnet) with a system prompt establishing it as a portfolio advisor explaining this specific recommendation, and the user's question.
   d. Stream the response back as SSE with type "token" events and a final "done" event.
   e. The LLM must be instructed to only answer based on the provided recommendation context — no hallucinated market data.
4. Register the router in `backend/app/main.py`.

Frontend changes:

1. Add a new `ExplainPanelComponent` (inline in app or as a separate component) that appears below the recommendation review card when a recommendation exists.
2. The panel has:
   - A text input with placeholder "Ask about this recommendation..."
   - Suggested questions as clickable chips: "Why is equity being sold?", "What happens if I reject this?", "Explain the policy check", "What's the risk if I don't rebalance?"
   - A chat-style message thread showing user questions and AI responses
   - Streaming token display (characters appear as they stream in, like a typewriter effect)
   - A "Grounded in this recommendation" badge to make clear the AI is not making things up
3. The panel should be disabled (with a message "Generate a recommendation first") when no recommendation exists.
4. Use Angular Signals: `chatMessages = signal<{role: 'user'|'assistant', content: string}[]>([])`.
5. Streaming: use EventSource or fetch with ReadableStream to consume the SSE token stream.

Style: The chat panel should feel like a professional financial advisor chat, not a consumer chatbot. Use the existing dark theme. Assistant messages should have a subtle left border in the accent blue color.
```

---

### Prompt 3.2 — "What If" Scenario Simulator

```
Read AGENT_CONTEXT.md fully before starting.

Add a "What If" scenario panel that lets the user adjust allocation targets or risk parameters and instantly see how the recommendation would change — without submitting a full new rebalance request.

Backend changes:

1. Add `POST /api/recommendations/{approval_id}/simulate` in `backend/app/api/routes/explain.py`.
2. Request body: `{ "scenario": { "equity_target": number, "fixed_income_target": number, "cash_target": number, "max_single_position_pct": number } }`.
3. The handler should:
   a. Load the original approval artifact.
   b. Re-run only the deterministic parts: recalculate drift with the new targets, re-evaluate policy with the new risk profile.
   c. Call Bedrock (claude-3-haiku) to generate a brief "scenario impact" explanation: what changes, what risks emerge or resolve.
   d. Return: `{ "drift_changes": [...], "policy_verdict": "...", "would_be_blocked": bool, "scenario_summary": string }`.
   e. This should be fast (< 3 seconds) — no full LangGraph run.

Frontend changes:

1. Add a "What If Simulator" collapsible section below the Q&A panel.
2. The panel has sliders for: Equity target %, Fixed Income target %, Cash target %, Max concentration %.
3. Sliders are initialized to the current recommendation's values.
4. As the user moves a slider, debounce 500ms then call the simulate endpoint.
5. Show the result inline:
   - Updated drift bars (same visual as the main allocation comparison)
   - Policy verdict badge (changes color in real time)
   - A "Would be blocked" warning if the scenario violates policy
   - The scenario_summary text from the LLM
6. A "Use these values" button that pre-fills the preferences wizard with the scenario values.

This makes the AI feel interactive and exploratory — users can understand the recommendation by probing it.
```

---

## Phase 4 — Memory and Personalization Visibility

**Goal**: Make the Memory Agent's contribution visible. Currently users have no idea that the system remembers past decisions and uses them to personalize recommendations.

---

### Prompt 4.1 — Client Memory Timeline

```
Read AGENT_CONTEXT.md fully before starting.

The Memory Agent retrieves client context but its output is invisible in the UI. Make memory visible.

Backend changes:

1. In `backend/app/agents/memory.py`, ensure the `run()` method returns structured memory items in `memory_output`:
   ```python
   {
     "items": [{ "content": str, "category": str, "recency": str, "confidence": float }],
     "synthesis": str,  # LLM-generated summary of client context
     "conflicts": [{ "description": str }]
   }
   ```
2. If LLM is enabled, use Bedrock to synthesize the memory items into a 2-3 sentence client context summary.
3. Pass the synthesis into the recommendation package's `summary` field as a prefix: "Based on your history: {synthesis}. {original_summary}".

Frontend changes:

1. Add a "Client Context" section to the recommendation review card, visible only when `memory_output` has items.
2. Show:
   - The synthesis paragraph in a styled callout box with a "🧠 From your history" label
   - Memory items as a compact timeline: category badge + content + recency
   - Any conflicts flagged with an amber warning icon
3. Add a "Memory contributed to this recommendation" indicator in the agent pipeline stage for the Memory Agent.

4. In the preferences page, add a new "Memory" tab (5th step or separate page) that shows:
   - A list of remembered preferences and past decisions
   - Each item with a "Forget this" button (calls a new DELETE /api/memory/{client_id}/{item_id} endpoint)
   - A "Clear all memory" button

Backend for memory management:
1. Add `GET /api/memory/{client_id}` — returns list of memory items from the store.
2. Add `DELETE /api/memory/{client_id}/{item_id}` — removes a specific memory item.
3. After each approved recommendation, automatically write a memory item: "Client approved rebalance on {date}: sold {X}% equity, bought {Y}% fixed income."
4. After each rejected recommendation, write: "Client rejected rebalance on {date}. Reason: {rejection_note}."

This closes the loop — users see that the AI learns from their decisions.
```

---

## Phase 5 — Audit Trail and Explainability Dashboard

**Goal**: Add a dedicated audit and explainability view that shows the full decision trail for compliance and trust.

---

### Prompt 5.1 — Decision Audit Dashboard

```
Read AGENT_CONTEXT.md fully before starting.

Add a new "Decision History" page that shows the full audit trail of all rebalance decisions, approvals, and rejections.

Backend changes:

1. Add `GET /api/audit/{client_id}` in a new `backend/app/api/routes/audit.py`.
2. Returns the last 20 audit events for the client, sorted by timestamp descending.
3. Each event includes: event_type, outcome, actor_id, timestamp, details dict.
4. Add `GET /api/audit/{client_id}/decisions` that returns a higher-level view: each completed workflow with its recommendation summary, policy verdict, approval decision, and the trades that were applied (if approved).

Frontend changes:

1. Add a new Angular route `/history` with a `HistoryComponent`.
2. Add a "Decision History" link in the main page header.
3. The history page shows:
   - A timeline of decisions (most recent first)
   - Each decision card shows: date, recommendation summary, policy verdict badge, approval decision badge (APPROVED/REJECTED), trades applied (if approved)
   - Clicking a decision expands it to show the full agent pipeline that ran, the drift at the time, and the LLM reasoning
   - A "Replay" button that pre-fills the intake form with the same portfolio values (for comparison)
4. Add a simple chart (use a CSS-only bar chart, no external charting library) showing portfolio allocation over time based on approved decisions.

This gives users confidence that the system is traceable and auditable — a key requirement for any financial AI system.
```

---

## Delivery Notes for the Agent

### Before starting any phase:
1. Read `AGENT_CONTEXT.md` completely
2. Read the specific files mentioned in the prompt
3. Run `docker compose up` to verify local environment works
4. Run `cd backend && uv run pytest tests/ -v` to confirm tests pass before making changes

### The view-layer rule
Phases 0 and 1.2 touch HTML and SCSS only. **Never modify `app.ts`, `core/api/`, or `preferences.component.ts`** during these phases. All TypeScript logic is working and correct — only the templates and styles change.

### After completing each prompt:
1. Build the frontend: `cd frontend && npm run build`
2. Run backend tests: `cd backend && uv run pytest tests/ -v`
3. Test locally with `docker compose up`
4. Deploy: `./infra/scripts/package_lambda.sh && cd infra/terraform/environments/dev && terraform apply -auto-approve -var-file=dev.tfvars && ./infra/scripts/publish_frontend.sh "https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com" "asset-management-dev-frontend-855603407942"`

### Coding rules (from AGENT_CONTEXT.md):
- Python: use `Decimal` for all financial values, `async def` everywhere, extend `ContractModel` for new Pydantic models
- TypeScript: use Angular Signals (`signal()`, `computed()`), `inject()` for DI, no RxJS BehaviorSubject
- All new API routes must be registered in `backend/app/main.py`
- CORS is already configured for all methods — no changes needed
- Feature flags for any new LLM feature: add to `FeatureFlags` in `backend/app/core/config.py` with `default=False`

### Recommended order:
Phase 0.1 → 1.1 → 1.2 → 2.1 → 2.2 → 2.3 → 3.1 → 3.2 → 4.1 → 5.1

Phase 0.1 must come first — it establishes the layout that all subsequent phases build into. Phase 1.1 adds streaming on top of that layout. Each phase after that is independent enough to skip if not needed.
