# Portfolio Screenshot Checklist — Dragon Pet AI

> Task: TASK-068D
> Depends on: TASK-066D (Demo Script), TASK-067D (README Polish)
> Last Updated: 2026-05-21
> Status: STABLE REFERENCE

---

## Purpose

This document defines the screenshot capture plan for the Dragon Pet AI portfolio. Use it to:

- Capture a consistent set of demo screenshots for GitHub, a portfolio site, or interview slides
- Know exactly what to show and what to avoid in each screenshot
- Follow a reproducible setup so captures can be redone after UI changes
- Attach screenshots to `docs/PORTFOLIO_DEMO_SCRIPT.md` as supporting visuals

---

## Screenshot Naming Convention

```
NN_descriptive_name.png
```

- `NN` — two-digit sequence number (01–09 for required, 10+ for optional)
- `descriptive_name` — lowercase, underscores only
- Always `.png` for lossless quality
- Store in `docs/screenshots/` (create the folder when capturing)

**Example:** `docs/screenshots/01_main_chat_ui.png`

---

## Setup Before Capturing

Run these commands in Windows PowerShell before starting any screenshot session. Both backend and Electron must be running.

```powershell
# Terminal 1 — start backend
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2 — verify backend is healthy
Invoke-RestMethod -Uri http://localhost:8000/health

# Terminal 3 — start Electron desktop
cd apps\desktop
npm start
```

**Before capturing:**
- Use only demo / fake messages in the chat (e.g., "Hello!", "How are you today?")
- Do not enter a real API key anywhere
- Do not use personal file paths in visible terminal output if avoidable
- Set Electron window to a consistent size (e.g., 1024 × 768 or full screen)
- Close DevTools before every screenshot unless the screenshot specifically requires it

---

## Required Screenshots

Capture all 9 of these. They form the core portfolio evidence set.

---

### 01 — Main Chat UI

**Filename:** `docs/screenshots/01_main_chat_ui.png`

**What to show:**
- The Electron window with the chat section visible
- At least one sent message (use demo text: "Hello!" or "Tell me about yourself")
- A visible mock response with `source: mock` shown in the response or status area
- The overall UI layout — header, chat area, input field, Send button

**Setup:** Send a message before capturing. No special configuration needed.

**What NOT to show:** Real API key anywhere on screen. Personal username in window title bar (use a demo account or blur if needed).

---

### 02 — Memory Section

**Filename:** `docs/screenshots/02_memory_section.png`

**What to show:**
- The Memory section of the Electron UI
- At least one created memory entry (use demo content: "User prefers concise responses" or "User is a software engineer")
- The memory list with the entry visible
- Ideally also show the Memory Context Preview output

**Setup:**
```powershell
# Create a demo memory via API (or use the UI)
Invoke-RestMethod -Method POST `
  -Uri http://localhost:8000/memory `
  -ContentType "application/json" `
  -Body '{"content": "User prefers concise responses", "memory_type": "preference", "confidence": 0.9}'
```

**What NOT to show:** Sensitive or personal memory content.

---

### 03 — Audit Logs

**Filename:** `docs/screenshots/03_audit_logs.png`

**What to show:**
- The Audit Logs section of the Electron UI
- At least one audit row with visible columns: `id`, `created_at`, `selected_count`, `total_context_chars`, `feature_flag_enabled`
- The read-only nature of the section (no edit controls)

**Setup:** Audit rows are created when memory-aware chat runs. If no rows exist, you can create one by sending a chat message with `use_memory: true` while `MEMORY_INJECTION_ENABLED=true` is set — or capture the empty-state UI with a note that this shows the audit log container.

**What NOT to show:** Raw memory content (audit rows should not contain it by design, but verify before capturing).

---

### 04 — Provider Settings Overview

**Filename:** `docs/screenshots/04_provider_settings_overview.png`

**What to show:**
- The full Provider Settings section scrolled to show all controls
- Provider selector (set to "anthropic" for the demo)
- Model field (set to a plausible value: "claude-3-haiku-20240307")
- Enable Real Provider toggle (can be shown as off — the safe default)
- Key status display showing "not_configured" or "unavailable" (either is correct)
- Save Key / Clear Key buttons (Save Key should be disabled or show unavailable state)
- Test Connection button (disabled — expected safe state)

**Setup:** No special configuration needed. The default state is the correct safe demo state.

**What NOT to show:** Any real API key in the key input field. Key fragment in the status display (should never appear by design).

---

### 05 — Usage Summary

**Filename:** `docs/screenshots/05_usage_summary.png`

**What to show:**
- The Usage Summary display within the Provider Settings section
- Aggregate fields: total calls, total input tokens, total output tokens, estimated cost
- The safe-fields-only nature of the display (no raw prompt, no key)

**Setup:** Usage data populates after any `/chat` or `/provider/settings/test` call. Send a few demo chat messages first to populate some counts.

```powershell
# Send a few mock chat messages to populate usage data
1..3 | ForEach-Object {
    Invoke-RestMethod -Method POST `
      -Uri http://localhost:8000/chat `
      -ContentType "application/json" `
      -Body '{"message": "Hello!"}'
}
```

**What NOT to show:** Any field that contains prompt text, raw response, or API key.

---

### 06 — Key Storage Unavailable Safe Message

**Filename:** `docs/screenshots/06_key_storage_unavailable_safe_message.png`

**What to show:**
- The safe error message that appears when Save Key is attempted and storage is unavailable (503)
- The message should read something like "Secure key storage is not available. Set your API key as an environment variable: ANTHROPIC_API_KEY=your-key" (or equivalent)
- The key input field cleared / empty after the attempt

**Setup:** Click Save Key with any text in the input field. The `UnavailableProviderKeyStorageBackend` will return 503, and the UI will show the safe message.

**What NOT to show:** Any real API key in the input field before clicking. Use a clearly fake placeholder: `sk-demo-key-placeholder`.

---

### 07 — Test Connection Safe State

**Filename:** `docs/screenshots/07_test_connection_safe_state.png`

**What to show:**
- The Test Connection button in its disabled state
- The helper text or tooltip explaining why it is disabled ("Configure a provider and save your API key to enable Test Connection" or equivalent)
- The key status showing "not_configured" or "unavailable"

**Alternative (if key is configured):**
- The cost acknowledgement `window.confirm()` dialog (if you can screenshot it mid-display)
- Or the test result area showing a safe failure message after a test attempt

**Setup:** Default state after starting the app with no configured key. No special action needed.

**What NOT to show:** A real API key anywhere. A live provider response (no live call should occur).

---

### 08 — pytest 470 Passed

**Filename:** `docs/screenshots/08_pytest_470_passed.png`

**What to show:**
- A terminal running `python -m pytest` from the `backend/` directory
- The final summary line: `470 passed in X.XXs`
- The terminal should show no failures, no errors, no warnings that suggest broken tests

**Setup:**
```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m pytest
```

**Framing tips:**
- Capture the bottom portion of the terminal showing the green summary line
- Include a few lines of dots (`....`) above for context
- The terminal window should be wide enough to show the full summary on one line

**What NOT to show:** Personal username in the prompt, absolute file paths with username (use a neutral terminal theme or crop if needed).

---

### 09 — Docs Overview

**Filename:** `docs/screenshots/09_docs_overview.png`

**What to show:**
- A file explorer view or terminal `ls docs/` or `dir docs\` showing all design documents
- The breadth of documentation: PRD, ARCHITECTURE, ROADMAP, TASKS, LLM design docs, BYOK, PHASE4 summary, PORTFOLIO script, etc.

**Setup (PowerShell):**
```powershell
# Option A: terminal listing
cd dragon-pet-ai
Get-ChildItem docs\ | Select-Object Name | Format-Table -AutoSize

# Option B: file explorer
# Open File Explorer at the docs/ folder and screenshot
```

**What NOT to show:** File system paths containing personal usernames (crop or blur if needed).

---

## Optional Screenshots

Capture these if available or if the feature state allows.

| # | Filename | When to capture |
|---|---|---|
| 10 | `10_test_connection_cost_ack_dialog.png` | If key is configured and Test Connection is enabled — shows the `window.confirm()` cost disclosure dialog |
| 11 | `11_test_connection_result_safe_message.png` | After a test connection attempt — shows the safe result display (status, safe_message, error_category) |
| 12 | `12_memory_context_preview.png` | Shows the formatted memory context text in the preview panel |
| 13 | `13_audit_logs_row_detail.png` | Close-up of a single audit row with all safe metadata columns visible |
| 14 | `14_provider_settings_real_provider_enabled.png` | Provider Settings with real_provider_enabled=true (still disabled at runtime — shows the toggle state) |
| 15 | `15_chat_with_memory_toggle.png` | Chat area with the "Use approved memories" checkbox visible |

---

## What Must NOT Appear in Screenshots

These are absolute rules. Review every screenshot before saving.

| Prohibited content | Why |
|---|---|
| Real API key (any `sk-...` or equivalent starting value) | Security — key must never be visible |
| Key fragment in status display | By design, status shows only safe values; if fragment appears, this is a bug |
| Raw provider response body | Never returned by the backend by design |
| Personal system username in file paths | Privacy — crop or blur system-level paths |
| Real personal memory content | Use only demo content ("User prefers concise responses", etc.) |
| Test Connection showing a live provider response | No live call should occur; if it does, do not publish the screenshot |
| Error messages containing API key text | Should never occur, but verify before publishing |
| Browser network tab with API key in request | Do not screenshot DevTools network panel with any auth headers visible |

---

## Recommended Capture Order

Follow this order for a smooth single session:

1. Start backend and Electron (see Setup commands above)
2. Send 2–3 demo chat messages → captures baseline usage data
3. **Screenshot 01** — Main chat UI with a visible response
4. Create a demo memory entry
5. **Screenshot 02** — Memory section with entry visible
6. (If audit row exists) **Screenshot 03** — Audit Logs
7. Open Provider Settings, set provider to "anthropic", set a plausible model name
8. **Screenshot 04** — Provider Settings overview
9. **Screenshot 05** — Usage Summary (scroll to it)
10. Click Save Key with a fake placeholder key → observe safe error message
11. **Screenshot 06** — Key storage unavailable safe message
12. **Screenshot 07** — Test Connection disabled state
13. Open a new terminal, run `python -m pytest`
14. **Screenshot 08** — pytest 470 passed
15. Open File Explorer or terminal, navigate to `docs/`
16. **Screenshot 09** — Docs overview

Total estimated time: 10–15 minutes for a complete session.

---

## README and Portfolio Usage

Once captured, use the screenshots as follows:

**GitHub README** — embed the most impactful screenshots inline:
```markdown
![Main Chat UI](docs/screenshots/01_main_chat_ui.png)
![Provider Settings](docs/screenshots/04_provider_settings_overview.png)
![pytest 470 passed](docs/screenshots/08_pytest_470_passed.png)
```

**Portfolio site / slide deck** — use screenshots 01, 04, 07, and 08 as the core visual set. They show: the running app, the safety-first provider settings, the disabled-by-default Test Connection, and the test coverage.

**Interview** — share your screen and walk through the app live using `docs/PORTFOLIO_DEMO_SCRIPT.md`. Use the screenshots as backup if screen sharing is unavailable.

**Demo video** — follow the Recommended Capture Order above as a recording script. Narrate with the 2-minute demo script from `docs/PORTFOLIO_DEMO_SCRIPT.md`.

---

## Future Capture Notes

These screenshots are not yet capturable and should be added when the corresponding features are enabled:

| Future screenshot | Blocker |
|---|---|
| Test Connection cost ack dialog (live) | Requires OS keychain backend to be wired so `key_status: configured` |
| Test Connection result — success | Requires live provider call (needs explicit user cost confirmation) |
| Save Key success state | Requires OS keychain backend implementation |
| Real LLM response in chat | Requires `LLM_CHAT_ENABLED=true` + real key + explicit user cost confirmation |

---

## Reference

| Document | Purpose |
|---|---|
| [docs/PORTFOLIO_DEMO_SCRIPT.md](PORTFOLIO_DEMO_SCRIPT.md) | Full demo script: 2-minute walk-through, interview talking points, what not to claim |
| [docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md](PHASE4_PROVIDER_SETTINGS_SUMMARY.md) | Phase 4 stabilization summary |
| [docs/PROVIDER_TEST_CONNECTION_DESIGN.md](PROVIDER_TEST_CONNECTION_DESIGN.md) | Test Connection safety design and hardening test results |
