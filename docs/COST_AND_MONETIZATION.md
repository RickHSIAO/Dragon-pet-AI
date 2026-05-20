# Cost Control and Monetization Design

Status: TASK-044 DONE. TASK-046 Usage Meter Design in progress. This document does not enable live provider calls.

## Usage Meter Requirement (TASK-046)

A usage meter is required before broad live provider usage. The following rules apply:

- Exact cost estimation should be conservative and clearly labeled as approximate.
- Token estimates are the primary metric. Currency cost estimates are optional and require a maintained pricing table.
- Provider dashboard remains the authoritative billing source of truth.
- Usage meter must be implemented (TASK-050) before BYOK settings ship to users (TASK-051).
- See `docs/USAGE_METER_DESIGN.md` for full design including what to track, privacy boundaries, storage options, and UI requirements.

## Why Cost Matters

Always-on cloud LLM use can become expensive because a desktop pet may stay open for long sessions, invite frequent casual interaction, and eventually include memory context or other features that increase token volume.

Entertainment-only usage may not justify sustained API cost. If the product is only a novelty companion, every cloud call becomes a recurring expense without a clear path to recover it.

Product positioning should include utility or monetization before always-on LLM use. The project can remain valuable as a portfolio/demo or personal companion, but a cloud-backed product needs a cost model before live usage becomes normal.

## Cost Drivers

- request frequency
- input tokens
- output tokens
- memory context
- conversation history
- model choice
- tools
- retries
- autonomous loops
- TTS if added later

## Cost Control Strategy

- LLM off by default
- `LLM_CHAT_ENABLED=false` by default
- `LLM_PROVIDER_ENABLED=false` by default
- no retries
- no tools
- no autonomous loops
- max_tokens cap
- memory context cap
- no full history by default
- manual live smoke only
- usage meter later
- daily quota later
- BYOK option
- local/mock mode default

## Product Positioning Options

| Option | Fit | Cost profile | Notes |
|---|---|---|---|
| Portfolio/demo | Strong short-term fit | Low | Shows architecture, safety, memory, and adapter design without paying for continuous LLM use. |
| Personal local companion | Strong MVP fit | Low to user-controlled | Local/mock by default; user can opt into cloud with their own key. |
| BYOK desktop app | Best first product direction | User-controlled | User owns provider account and cost; app focuses on UX, memory safety, and configuration. |
| Subscription SaaS | Risky before usage data | Operator pays cloud cost | Needs usage caps, billing, abuse controls, and support. |
| Credit-based model | Possible after metering | Bounded | Requires accurate usage tracking and payment flow. |
| Hybrid local/cloud model | Good long-term direction | Variable | Local/default mode for casual interactions; cloud for high-value turns. |

## Recommended Direction

- Short term: portfolio/demo + personal use.
- MVP product direction: BYOK first.
- Cloud-hosted subscription only after real usage data.
- Do not offer unlimited free cloud LLM.

Rationale: BYOK keeps the project useful while avoiding uncapped operator cost. It also matches the current safety design: API keys stay backend-local, real provider flags default off, and manual live smoke requires explicit opt-in.

TASK-045 expands this into the BYOK product and settings safety model. BYOK is the recommended MVP path. A usage meter should come before broad live provider usage, and provider settings plus secure key handling must be designed before implementation.

## Live Smoke Go/No-Go Criteria

Go only if:

- user has API key
- user accepts possible cost
- exactly one minimal request
- memory disabled first
- no tools
- no retries
- logs monitored
- env vars cleared after test

No-go if:

- no API key
- cost concern not accepted
- unclear provider pricing
- implementation might send repeated calls
- logs could expose key
- source behavior not clear

## Not Recommended

- unlimited free cloud LLM
- always-on autonomous agent
- Opus as default model
- long conversation history by default
- automatic retries
- background polling with LLM
- hidden live calls

## Suggested Next Tasks

- TASK-045 - BYOK Product and Settings Design
- TASK-046 - Usage Meter Design
- defer live smoke until explicit user cost confirmation
- later: provider settings UI design
- later: local model exploration
