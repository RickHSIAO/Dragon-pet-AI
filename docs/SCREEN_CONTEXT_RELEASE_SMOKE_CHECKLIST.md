# Screen Context v0.4 Release Smoke Checklist

## Purpose

This checklist covers the full Screen Context v0.4 feature set (TASK-174 through TASK-179).
Use it to verify that every capture mode, OCR analysis path, chat handoff, OCR ask hint,
and privacy boundary is working correctly before declaring a Screen Context release complete.

Automated tests (pytest + renderer-chat-smoke) must pass before running this checklist.

---

## Automated Pre-checks (run first)

```powershell
# Backend OCR tests
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
.\.venv\Scripts\Activate.ps1
python -m pytest tests/test_ocr_routes.py -q
# Expected: 34 passed

# Desktop smoke (covers all capture + OCR + chat scope checks)
cd F:\RickHSIAO\Python\dragon-pet-ai
node apps/desktop/scripts/renderer-chat-smoke.js
# Expected: renderer chat smoke: PASS
```

---

## Pre-flight: Backend + OCR Status

```powershell
# Start backend
cd F:\RickHSIAO\Python\dragon-pet-ai\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

- [ ] **P1** `GET http://localhost:8000/health` → `{"status": "ok"}`
- [ ] **P2** `GET http://localhost:8000/ocr/status` → valid JSON, no Python traceback, no `pytesseract` or `PIL` in response
- [ ] **P3** OCR status fields present: `tesseract_available`, `chi_tra_available`, `eng_available`, `selected_lang`, `fallback_reason`
- [ ] **P4** `tesseract_available: true`
- [ ] **P5** `chi_tra_available: true` → `selected_lang: "eng+chi_tra"`, `fallback_reason: null` *(preferred)*
  — OR — `chi_tra_available: false`, `eng_available: true` → `selected_lang: "eng"`, `fallback_reason: "chi_tra-language-data-missing"` *(acceptable fallback)*
- [ ] **P6** Electron app opens without errors; Full App UI loads

---

## Section A — Capture Modes

### A1. Display Picker Capture (TASK-174)

- [ ] **A1-1** Click "擷取螢幕" → semi-transparent picker overlay appears on each connected monitor (one overlay per display)
- [ ] **A1-2** Click primary monitor → overlay(s) close → status shows "截圖完成。尚未儲存，可供後續分析使用。"; "分析這張" button enabled
- [ ] **A1-3** *(dual-monitor only)* Click secondary monitor → only secondary display content captured (confirm with unique test text on each screen)
- [ ] **A1-4** Press **Esc** in picker → "已取消擷取螢幕。"; "分析這張" button remains disabled

### A2. Region Drag-to-Select Capture (TASK-175)

- [ ] **A2-1** After display picker, canvas region overlay appears full-screen on the selected display
- [ ] **A2-2** Drag a rectangle → release mouse → overlay closes; status shows success; "分析這張" enabled
- [ ] **A2-3** OCR result shows only content from the dragged region, not the full display (place unique test text `REGION_SMOKE_TEST` in the region and verify it appears in "螢幕摘要")
- [ ] **A2-4** Drag area smaller than 16 × 16 logical px → "選取範圍太小，請重新拖曳較大區域。"; button stays disabled
- [ ] **A2-5** Press **Esc** on region overlay → "已取消選取區域。"; button stays disabled

### A3. Window Picker Capture (TASK-176)

- [ ] **A3-1** Click "擷取視窗" → dark opaque window picker opens; list of open window names visible
- [ ] **A3-2** Click a window name (e.g., Notepad with `WINDOW_SMOKE_TEST`) → picker closes → status shows success; "分析這張" enabled
- [ ] **A3-3** Click "分析這張" → OCR result contains `WINDOW_SMOKE_TEST`; other windows' content absent
- [ ] **A3-4** Repeat with a second window (e.g., browser) → OCR result shows only that window's content; capture isolation confirmed
- [ ] **A3-5** Press **Esc** in window picker → "已取消選取視窗。"; button stays disabled

---

## Section B — OCR Analysis (TASK-172A + TASK-177)

- [ ] **B1** After any successful capture, "分析這張" button is enabled
- [ ] **B2** Click "分析這張" → confirmation dialog appears (must mention passwords/API keys/private messages)
- [ ] **B3** Click **Cancel** in confirmation → analysis NOT triggered; no `/chat` POST; button re-enabled
- [ ] **B4** Click **OK** in confirmation → "正在分析…" status appears; "分析這張" disabled during analysis
- [ ] **B5** Analysis completes → "螢幕摘要" panel appears with extracted text
- [ ] **B6** OCR output is bounded (≤ 800 chars visible); no raw base64 string visible
- [ ] **B7** No Python traceback, no `pytesseract`, no `PIL`, no JSON dump visible in any UI element
- [ ] **B8** *(chi_tra)* Traditional Chinese text on screen is extracted correctly when `selected_lang: "eng+chi_tra"`
- [ ] **B9** *(eng fallback)* If `chi_tra_available: false` — OCR runs in `eng`-only mode with no crash and no traceback

---

## Section C — Chat Handoff (TASK-172B)

- [ ] **C0** After OCR summary exists, OCR ask hint appears below "螢幕摘要" panel (was hidden before); hint text mentions 文字摘要 and does NOT mention dataUrl or image *(TASK-179)*
- [ ] **C1** After OCR summary exists, "問克莉絲蒂娜這個畫面" button appears (was hidden before)
- [ ] **C2** Click "問克莉絲蒂娜這個畫面" → privacy confirmation dialog appears
- [ ] **C3** Click **Cancel** → no `/chat` POST sent; button remains visible
- [ ] **C4** Click **OK** → one `/chat` POST sent; body contains OCR summary text only
- [ ] **C5** The `/chat` POST body does NOT contain: `dataUrl`, `data:image`, base64 string, image bytes
- [ ] **C6** Christina's reply appears in chat area; Pet expression updates; TTS follows normal rules
- [ ] **C7** "螢幕摘要" panel remains visible after handoff (not cleared by send)

---

## Section D — Clear Screenshot

- [ ] **D1** "清除截圖" button visible after any successful capture
- [ ] **D2** Click "清除截圖" → "分析這張" disabled; "螢幕摘要" panel hidden; OCR ask hint hidden; "問克莉絲蒂娜這個畫面" hidden; "清除截圖" hidden
- [ ] **D3** All capture-dependent UI resets to pre-capture state
- [ ] **D4** After clear, clicking "擷取螢幕" or "擷取視窗" starts a fresh capture with no leftover state

---

## Section E — Privacy & Safety Boundaries

These items verify that the feature does NOT do anything it shouldn't.

- [ ] **E1** App launch: no screenshot taken automatically (no "截圖完成" status on load)
- [ ] **E2** App running idle: no background screenshot polling; no repeated status updates; no capture without user click
- [ ] **E3** Successful capture alone: OCR NOT auto-triggered; "螢幕摘要" panel NOT shown; must click "分析這張"
- [ ] **E4** Successful OCR alone: `/chat` NOT auto-called; must click "問克莉絲蒂娜這個畫面"
- [ ] **E5** "問克莉絲蒂娜這個畫面" sends ONLY the OCR text summary — not the screenshot image, not a dataUrl, not base64 bytes
- [ ] **E6** No screenshot or image data written to disk at any point during capture, OCR, or chat handoff
- [ ] **E7** No cloud OCR or cloud vision API called; all OCR is local Tesseract only
- [ ] **E8** Pet bubble does NOT show screenshot content, OCR summary, or autonomous commentary about the screen

---

## Section F — Regression: Full App Features

These items confirm that Screen Context changes do not break pre-existing functionality.

- [ ] **F1** Full App chat: type a message → Enter → `/chat` POST sent → reply appears in chat area
- [ ] **F2** Pet direct input: type in Pet window input → Christina replies in Pet bubble
- [ ] **F3** Voice/STT: microphone input → transcript appears in Full App input bar *(skip if no mic)*
- [ ] **F4** TTS: Christina's reply is spoken after chat *(if TTS enabled)*
- [ ] **F5** Quiet Mode: TTS suppressed when quiet mode is active
- [ ] **F6** Pet window: Show Pet / Hide Pet works; Pet bubble state is preserved after hide/show
- [ ] **F7** Memory toggle: "Use approved memories" checkbox still routes correctly to `/chat`
- [ ] **F8** Provider Settings: save/reload settings without crash

---

## Sign-off Record

Fill this in when all items pass:

| Field | Value |
|---|---|
| Date | |
| Branch / commit | |
| OS / Electron version | |
| `selected_lang` at sign-off | |
| `chi_tra_available` at sign-off | |
| Automated tests | `pytest test_ocr_routes.py` 34 PASS / `renderer-chat-smoke` PASS |
| All checklist items | PASS / FAIL |
| Signed off by | |

---

## Known Limitations (not blocking release)

- OCR output can contain UI noise (window chrome, icons) — expected Tesseract limitation on full-desktop screenshots.
- Window picker list order is OS-dependent; does not match visual Z-order.
- Minimized windows may return an empty capture thumbnail.
- chi_tra fallback to eng degrades Traditional Chinese text extraction quality.
- Visual/multimodal analysis (describing image content beyond text) is deferred to TASK-180 (backlog).

---

## Related Docs

- [TASKS.md](TASKS.md) — task-by-task implementation record for TASK-171A through TASK-181
- [ROADMAP.md](ROADMAP.md) — Screen Context milestone history
- [OLLAMA_RUNTIME_SMOKE_CHECKLIST.md](OLLAMA_RUNTIME_SMOKE_CHECKLIST.md) — Ollama provider smoke (separate from screen context)
