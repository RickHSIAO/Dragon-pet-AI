# Usage Meter Design

> dragon-pet-ai
> Phase: 4 — LLM Adapter Integration
> Status: DESIGN (TASK-046)
> Last Updated: 2026-05-19
> Owner: TASK-046

---

## 1. Purpose

The usage meter gives BYOK users visibility into how much they are sending to their LLM provider and approximately what it may cost.

Key principles:

- BYOK users own their API key and are responsible for their provider billing. The app should make usage visible before encouraging real provider use.
- Exact billing is determined by the provider dashboard. App estimates are informational only and must be clearly labeled as approximate.
- Usage visibility should exist before any user-facing provider settings UI is shipped. A user who enables live provider calls should be able to see what they are spending immediately.
- The usage meter is not a billing system, a payment integration, or a quota enforcement system in Phase 4. It is a transparency tool.

---

## 2. What to Track

The following fields should be recorded per chat turn when a real provider is active. Fields marked `(future)` are lower-priority and may be added after core tracking is in place.

| Field | Type | Description |
|---|---|---|
| `request_count` | int | Cumulative count of provider requests made (session and daily) |
| `provider` | str | Provider name: `mock`, `anthropic`, `openai` |
| `model` | str \| None | Model identifier if available: `claude-opus-4-6`, `gpt-4o`, etc. |
| `source` | str | Response source: `mock`, `llm_mock`, `llm_real`, `llm_real_error` |
| `estimated_input_tokens` | int \| None | Best estimate of input token count before or after the call |
| `estimated_output_tokens` | int \| None | Best estimate of output token count from the response |
| `estimated_total_tokens` | int \| None | Sum of input + output estimates |
| `provider_reported_usage` | dict \| None | Raw usage block from provider if returned (internal only — not exposed to frontend as-is) |
| `estimated_cost_usd` | float \| None | Approximate cost in USD based on configured pricing table. Null if pricing not configured. |
| `timestamp` | datetime | UTC timestamp of the request |
| `memory_used` | bool | Whether approved memory context was injected in this turn |
| `memory_count` | int | Number of memory entries injected (0 if memory not used) |
| `fallback_used` | bool | Whether real provider failed and mock fallback was used |
| `error_category` | str \| None | Error category if provider failed: `provider_timeout`, `rate_limit`, `provider_auth_error`, `provider_unavailable`, `invalid_response`, `provider_error` |

---

## 3. What Must Not Be Tracked

The following are **strictly forbidden** from any usage record, log line, or export:

| Forbidden Field | Reason |
|---|---|
| API key value | Core security boundary — never stored anywhere |
| Raw prompt text | Contains user message + system prompt + memory context — sensitive |
| Raw user message content | User PII risk |
| Raw approved memory context | Contains user-defined personal facts |
| Raw provider response body | May contain sensitive generated content |
| Full conversation history | Bulk PII risk |
| System / developer prompt text | Internal behavioral rules, not user-visible |
| Any sensitive user input | Catch-all for anything not explicitly listed above |

Usage records must contain only aggregate metadata and safe diagnostic identifiers. They must be safe to retain locally without requiring user data consent review.

---

## 4. Token Estimation Rules

Token counts from provider vs. local estimation differ by provider and model.

**Preference order:**

1. **Provider-reported usage** — if the provider returns a usage block (e.g. `input_tokens`, `output_tokens` from Anthropic), use those values directly. These are the most accurate.
2. **Local rough estimation** — if provider-reported usage is not available or the call failed, use a rough character-based heuristic (e.g. 1 token ≈ 4 characters for English). This is an approximation.

**Rules:**

- All token counts presented to the user must be labeled as **estimates** unless sourced from provider-reported usage AND the label says "provider-reported."
- Chinese, Japanese, Korean, and other CJK text tokenizes differently from English (often 1–2 chars per token vs. 4 chars per token). Do not apply English-only estimation to multilingual messages.
- Token estimation is not required to match the provider invoice. It is a guidance tool only.
- Never present local token estimates as exact billing figures.

---

## 5. Cost Estimation Rules

Cost estimation requires a pricing table mapping `(provider, model)` → `(cost_per_input_token, cost_per_output_token)`.

**Rules:**

- Pricing tables change over time. The app must not embed a hardcoded pricing table as if it were permanent.
- MVP may choose to show estimated tokens only, without a currency cost, if no pricing table is configured or maintained.
- When pricing is configured: show cost as **approximate** with a disclaimer. Example: `~$0.003 (estimate — check provider dashboard)`.
- Never guarantee that in-app estimates match provider invoices.
- Provider dashboard remains the authoritative billing source of truth.
- If pricing table is stale (last updated more than 90 days ago), the cost estimate should be labeled as potentially outdated.

**Recommended MVP approach:** Show estimated tokens first. Add optional cost estimate only if a pricing table is actively maintained. Default to tokens-only display to avoid misleading cost figures.

---

## 6. UI Requirements

The following elements should appear in a future Usage Meter UI. Implementation is deferred to TASK-050.

### 6.1 Core Display Fields

| Display Element | Source | Notes |
|---|---|---|
| Today's request count | daily aggregate | Mock-only requests may be excluded or shown separately |
| Session request count | in-memory counter | Resets on app restart |
| Estimated tokens today | daily aggregate | Labeled as estimate |
| Estimated tokens this session | in-memory counter | Labeled as estimate |
| Current provider | resolved provider name | `mock`, `anthropic`, `openai` |
| Current model | resolved model | If available |
| Last response source | most recent `source` value | `mock`, `llm_mock`, `llm_real`, `llm_real_error` |
| Fallback count today | daily aggregate | How many turns used mock fallback |
| Memory-aware request count | daily aggregate | Turns where memory injection was used |

### 6.2 Optional Fields (lower priority)

- Estimated cost today (only if pricing table is maintained)
- Estimated cost this session
- Rolling 7-day token total
- Per-model breakdown

### 6.3 Placement

Placement decided in TASK-047 Provider Settings UI Design:

- **Primary placement**: A compact usage summary section embedded in the Provider Settings panel (Section 2.6 of `docs/PROVIDER_SETTINGS_UI_DESIGN.md`). This is the canonical home for the usage meter in Phase 4.
- **Secondary placement** (optional, lower priority): A collapsed or minimal status indicator near the chat input toggle bar for quick session visibility.

The usage meter must not interrupt the chat flow. It should be visible but not prominent.

Standing disclaimer visible wherever usage meter appears:
```
Usage estimates are approximate. Check your provider dashboard for exact billing.
```

Provider dashboard remains the authoritative billing source of truth. The in-app usage meter is a transparency tool only — it must never be presented as a substitute for the provider's own billing interface.

---

## 7. Warning UX

The following warning messages should appear in the UI when relevant. All warnings must be non-alarming and informational.

### 7.1 Standing Disclaimer (always visible when real provider is active)

```
Usage estimates are approximate. Check your provider dashboard for exact billing.
```

### 7.2 Memory Usage Notice

```
Memory-aware chat may increase input tokens per turn.
```

Shown when `memory_used=true` is detected in recent turns.

### 7.3 Long Reply Notice

```
Longer replies increase output tokens.
```

Shown optionally, low priority.

### 7.4 Always-On Cost Risk Warning

```
Leaving the app open with a real provider active may increase usage continuously.
Mock mode has no API cost.
```

Shown at session start when `LLM_PROVIDER_ENABLED=true` and `LLM_CHAT_ENABLED=true`.

### 7.5 High Usage Alert (future)

A configurable daily token threshold (e.g. 100,000 tokens) that triggers a soft warning:

```
You have used approximately {N} tokens today. Check your provider dashboard.
```

This is a soft advisory — the app does not block requests based on it in Phase 4.

---

## 8. Privacy and Logging Boundaries

| Boundary | Rule |
|---|---|
| No API key in usage records | Usage rows must never store `LLM_API_KEY` or any key fragment |
| No raw user message | Usage rows must never store the user's message text |
| No memory content | Usage rows must never store approved memory context text |
| No raw provider response | Usage rows must never store provider response body |
| No prompt text | Usage rows must never store full prompt or system prompt |
| Aggregate-only logs | Backend logs may record provider name, model, error category, token counts, fallback flag — nothing sensitive |
| Export safety | If a usage export feature is added later, it must exclude all forbidden fields and must not expose API keys or raw prompts |
| Retention | Usage data should be deletable by the user without affecting memory or conversation data |

---

## 9. Storage Design Options

| Option | Pros | Cons | Verdict |
|---|---|---|---|
| In-memory session counters only | Zero persistence risk, zero DB schema change | Lost on restart, no day-over-day view | Good for session view only |
| Local SQLite usage table | Persistent, queryable, day-over-day possible | Requires schema addition, migration | Recommended for Phase 4 |
| Daily rollup table only | Compact, low storage | Loses per-turn granularity | Good for long-term retention |
| External analytics service | Rich dashboards | Sends data offsite, privacy concern | Deferred — not in MVP |

**Recommended MVP approach:**

- Phase 1 (TASK-050 initial): In-memory session counters only. No new DB table. No migration risk.
- Phase 2 (TASK-050 follow-up or later): Optional local SQLite daily rollup table. Stores only safe aggregate fields. User can delete this table independently.
- Raw per-turn usage rows are not stored by default in Phase 4.

**Storage rules:**
- Do not store raw content in any usage row.
- Keep usage data deletable independently from conversation history.
- Do not send usage data to any external service in Phase 4.

---

## 10. Interaction with BYOK

BYOK does not reduce the need for usage visibility — it increases it.

- The user owns the API key and the billing. They bear cost risk directly.
- The app must warn and estimate before and during real provider use, even if the user has configured their own key.
- Usage meter should be visible in the settings UI that TASK-047 designs and TASK-050 implements.
- The usage meter must be ready before TASK-051 (BYOK Settings Implementation) ships to users, because BYOK without cost visibility creates a poor user experience.

Key dependency: **Usage meter must be designed (TASK-046) and implemented (TASK-050) before BYOK settings become user-accessible (TASK-051).**

---

## 11. Future Implementation Sequence

| Task | Name | Type |
|---|---|---|
| TASK-047 | Provider Settings UI Design | Design-only |
| TASK-048 | Backend Provider Settings API Design | Design-only |
| TASK-049 | Secure Key Storage Design | Design-only |
| TASK-050 | Usage Meter Implementation | Implementation |
| TASK-051 | BYOK Settings Implementation | Implementation |
| TASK-052 | BYOK Runtime Smoke Check | Validation |

---

## 12. Non-Goals for Phase 4

| Feature | Reason |
|---|---|
| Exact billing guarantee | Provider invoice is authoritative — app estimates are informational only |
| Payment / billing integration | No payment system in Phase 4 |
| Hosted subscription billing | Deferred until real usage data and pricing model exist |
| Provider dashboard replacement | App shows estimates; dashboard shows actuals |
| Automatic cost charging | Never — the app never charges users |
| External billing API calls | No external billing or analytics API calls |
| Per-user multi-tenant accounting | Not in MVP scope |
| Quota enforcement blocking | App warns but does not block requests based on estimated cost in Phase 4 |
