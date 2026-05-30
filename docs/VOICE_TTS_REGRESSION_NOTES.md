# Voice / TTS Regression Baseline — dragon-pet-ai

> Created: TASK-191 (2026-05-31)
> Scope: Pet Window voice input (STT), TTS playback, Quiet Mode, voice settings, mutual exclusion.

This document records the Voice/TTS baseline established in TASK-191. No bugs were found.
All 101 automated voice/STT/TTS tests pass across three test suites.

---

## Automated Test Coverage Summary

| Suite | Voice/STT/TTS Tests | Total Tests | Status |
|---|---|---|---|
| `pet-renderer-smoke.js` | 80 checks | 226 checks | PASS |
| `pet-window-smoke.js` | 7 checks | 45 checks | PASS |
| `python -m pytest tests/test_stt_routes.py` | 14 tests | 14 tests | PASS |
| **Total** | **101** | — | **ALL PASS** |

### pet-renderer-smoke.js Voice/STT/TTS Coverage

| Area | Test count | Task |
|---|---|---|
| Mic button HTML/CSS/state | 9 | TASK-167A |
| Recording state machine (data-recording) | 5 | TASK-167A |
| Mutual exclusion (recording ↔ text input, recording ↔ CT) | 3 | TASK-167A |
| getUserMedia + MediaRecorder presence | 2 | TASK-167A |
| Scope safety (no direct Ollama, no screen capture in voice) | 2 | TASK-167A |
| Transcribing state machine (data-transcribing) | 5 | TASK-167B |
| Transcribing HTML/CSS | 3 | TASK-167B |
| Mutual exclusion (transcribing ↔ recording CSS) | 1 | TASK-167B |
| STT IPC bridge + error message cleanliness | 3 | TASK-167B |
| STT stop-to-transcribe handoff | 2 | TASK-167B |
| Voice→chat constants and guards | 5 | TASK-167C |
| handlePetVoiceChatSend wiring and error handling | 5 | TASK-167C |
| Scope/safety checks | 3 | TASK-167C |
| TTS HTML/CSS/constants | 5 | TASK-168B |
| TTS guards (recording/transcribing block TTS) | 3 | TASK-168B |
| TTS speech behaviour (truncate, cancel, empty, state attr) | 5 | TASK-168B |
| TTS wiring (voice chat + direct send) | 4 | TASK-168B |
| TTS settings constants/functions | 2 | TASK-169 |
| TTS settings HTML/CSS | 2 | TASK-169 |
| Voice selector (getVoices, voiceschanged) | 2 | TASK-169 |
| Clamp logic + defaults + localStorage | 4 | TASK-169 |
| Rate/pitch/volume applied to SpeechSynthesisUtterance | 1 | TASK-169 |
| Reset TTS controls | 2 | TASK-169 |
| Scope safety check | 1 | TASK-169 |

### pet-window-smoke.js Voice/STT Coverage

| Test | Purpose |
|---|---|
| `testVoiceRecordingFunctionsExportedFromRenderer` | pet-renderer exports recording functions |
| `testNoNewIpcChannelsForMic` | mic capture uses no new IPC (getUserMedia only) |
| `testMicPermissionHandlerInMain` | main.js has session.setPermissionRequestHandler for media |
| `testSttIpcBridgeExposedInPreload` | pet-preload exposes `transcribeAudio` on correct channel |
| `testSttIpcHandlerInMain` | main.js handles `stt:transcribe` channel |
| `testSttHandlerNoPersistenceInMain` | STT handler writes no files, no disk audio |
| `testSttTranscribeAudioBlobFunctionsInRenderer` | pet-renderer has `transcribeAudioBlob` function |

### backend/tests/test_stt_routes.py Coverage

| Test | Purpose |
|---|---|
| `test_stt_service_empty_bytes_returns_empty_status` | Empty audio → `{status: "empty"}` |
| `test_stt_service_returns_dict_with_required_keys` | Response always has `transcript` + `status` |
| `test_stt_service_unavailable_when_no_whisper` | faster-whisper not installed → `{status: "unavailable"}` |
| `test_stt_service_model_load_failure_returns_unavailable` | Whisper load failure → safe fallback |
| `test_stt_service_model_transcribe_error_returns_error_status` | Whisper error → `{status: "error"}` |
| `test_stt_service_empty_transcript_returns_empty_status` | Whisper returns "" → `{status: "empty"}` |
| `test_stt_service_ok_transcript` | Whisper returns text → `{transcript: "...", status: "ok"}` |
| `test_stt_transcribe_endpoint_exists` | `POST /stt/transcribe` endpoint exists |
| `test_stt_transcribe_returns_json_with_transcript_and_status` | Endpoint returns correct schema |
| `test_stt_transcribe_empty_audio_returns_empty_or_unavailable` | Empty upload handled safely |
| `test_stt_transcribe_no_audio_field_returns_422` | Missing field → 422 validation error |
| `test_stt_transcribe_oversized_audio_returns_413` | Audio > 10 MB → 413 |
| `test_stt_transcribe_no_chat_forwarding` | STT endpoint never calls `/chat` |
| `test_stt_service_no_audio_persistence` | No audio written to disk |

---

## State Machine Reference

### Recording State

| Attribute | Element | Set when |
|---|---|---|
| `data-recording="true"` | `#pet-mode-root` | `openPetVoiceRecording()` succeeded |
| `data-recording="false"` / absent | — | recording stopped, cancelled, or not started |
| `#pet-recording-indicator` hidden | — | `data-recording` absent or false |

### Transcribing State

| Attribute | Element | Set when |
|---|---|---|
| `data-transcribing="true"` | `#pet-mode-root` | `setTranscribingState(active=true)` |
| `data-transcribing="false"` / absent | — | STT complete, error, or not started |
| `#pet-transcribing-indicator` hidden | — | `data-transcribing` absent or false |

### Speaking State

| Attribute | Element | Set when |
|---|---|---|
| `data-speaking="true"` | `#pet-mode-root` | `speakPetReply()` starts utterance |
| `data-speaking="false"` / absent | — | `stopPetSpeech()` called or utterance ended |

### Mutual Exclusion Matrix (CSS + JS guards)

| A active | B guarded | How |
|---|---|---|
| Recording | Text input | CSS: `[data-recording="true"] .pet-direct-input-panel { display:none }` |
| Recording | TTS (speaking indicator) | CSS: `[data-recording="true"] .pet-speaking-indicator { display:none }` |
| Recording | New recording | JS: `openPetVoiceRecording()` calls `stopPetVoiceRecording()` if already recording |
| Transcribing | New recording | JS: `openPetVoiceRecording()` returns early if `isTranscribingActive()` |
| Transcribing | TTS (speaking indicator) | CSS: `[data-transcribing="true"] .pet-speaking-indicator { display:none }` |
| Transcribing | Text input | CSS: `[data-transcribing="true"] .pet-direct-input-panel { display:none }` |
| Recording | TTS speak call | JS: `speakPetReply()` returns early if `isPetRecordingActive()` |
| Transcribing | TTS speak call | JS: `speakPetReply()` returns early if `isTranscribingActive()` |
| Recording starts | Previous TTS | JS: `openPetVoiceRecording()` calls `stopPetSpeech()` first |
| CT-ON | Recording | JS: `setClickThrough(true)` cancels active recording |
| Text input opens | Recording | JS: `openPetDirectInput()` calls `cancelPetVoiceRecording()` |
| Recording starts | Text input | JS: `openPetVoiceRecording()` calls `closePetDirectInput()` |

---

## Error Message Taxonomy

All error messages are clean Chinese strings — no raw exceptions, no tracebacks, no internal field names.

| Error | Chinese message | Trigger |
|---|---|---|
| Mic permission denied | 麥克風權限被拒絕。請在系統設定中開啟麥克風權限。 | `getUserMedia` NotAllowedError |
| No mic found | 找不到麥克風裝置。請確認麥克風已連接。 | `getUserMedia` NotFoundError |
| MediaRecorder unsupported | 此環境不支援語音錄音。 | `typeof MediaRecorder === "undefined"` or start() fails |
| STT unavailable | 語音辨識目前不可用。 | Backend `status: "unavailable"` (faster-whisper not installed) |
| STT timeout | 語音辨識超時，請再試一次。 | IPC call exceeds 30-second PET_STT_TIMEOUT_MS |
| STT offline | 後端離線，無法辨識語音。 | Backend `status: "offline"` |
| STT error | 語音辨識出錯，請再試一次。 | Backend `status: "error"` |
| Empty audio | 沒有偵測到語音，請再試一次。 | Backend returns empty transcript |
| Transcript too long | 語音太長，請縮短後再試。 | Transcript > 2000 chars |

---

## TTS Settings Reference

| Control | ID | Storage key | Range | Default |
|---|---|---|---|---|
| Voice selector | `#pet-tts-voice-select` | `pet_tts_voice` | Browser SpeechSynthesis voices | `""` (browser default) |
| Rate | `#pet-tts-rate` | `pet_tts_rate` | 0.7 – 1.3, step 0.05 | 1.0 |
| Pitch | `#pet-tts-pitch` | `pet_tts_pitch` | 0.8 – 1.3, step 0.05 | 1.0 |
| Volume | `#pet-tts-volume` | `pet_tts_volume` | 0.0 – 1.0, step 0.05 | 1.0 |
| Reset button | `#pet-tts-reset` | — | — | — |

**Persistence:** All settings saved to `localStorage` on change; loaded on Pet Window init via `loadTtsSettings()`.

**TTS-only for final states:** `speakPetReply()` only fires for `"speaking"` and `"long_reply"` bubble states. Error and timeout states never trigger TTS.

---

## Quiet Mode × TTS / Voice Interaction

| Scenario | Quiet Mode = ON | Quiet Mode = OFF |
|---|---|---|
| Idle rotation | Suppressed | Normal |
| Pet bubble | Collapses to "collapsed" if idle | Shows idle_default |
| Hint text | Hidden (CSS) | Visible |
| Voice recording | Not suppressed — user-initiated | Normal |
| TTS playback | Not suppressed — fires on any final reply | Normal |
| TTS for thinking/error | Blocked by `speakPetReply` state guard | Blocked (same guard) |

---

## Manual Smoke Checklist

> Created: TASK-191 (2026-05-31). Expanded to executable 14-item form: TASK-192 (2026-05-31).
> For use when running Pet Window in development. `npm start` with backend live.
> Prerequisites: backend running (`uvicorn`), `npm start`, Pet Window open (click "Show Pet").

---

### 1. Pet Window Mic Button 可見性

**Precondition:** Pet Window open at any scale (S / M / L).

- [ ] Mic button (🎤) visible in Pet nav bar at S scale (300×400)
- [ ] Mic button visible at M scale (340×470)
- [ ] Mic button visible at L scale (380×540)
- [ ] Mic button not hidden by any CSS at the three scales

**Pass:** Button present and not hidden at all three scales.

---

### 2. 點 Mic 後 Recording Indicator 是否出現

**Precondition:** Mic permission granted at OS level. Pet Window open.

- [ ] Click mic button → `data-recording="true"` set on `#pet-mode-root`
- [ ] Pulsing red recording indicator (`#pet-recording-indicator`) becomes visible
- [ ] Text input panel (`.pet-direct-input-panel`) is hidden (CSS mutual exclusion)
- [ ] TTS speaking indicator hidden during recording (CSS mutual exclusion)

**Pass:** Red indicator visible; text input and speaking indicator hidden.

---

### 3. 再點 Mic 後是否進入 Transcribing

**Precondition:** Recording is active (step 2 passed).

- [ ] Click mic again → `data-recording` clears / becomes false
- [ ] `data-transcribing="true"` set on `#pet-mode-root`
- [ ] Spinning transcribing indicator (`#pet-transcribing-indicator`) becomes visible
- [ ] Text input panel still hidden during transcribing (CSS mutual exclusion)
- [ ] Transcribing indicator disappears when STT completes (or errors out)

**Pass:** Transcribing indicator visible after second click; input panel hidden throughout.

---

### 4. STT 成功後 Transcript 是否送到 /chat

**Precondition:** faster-whisper installed and `/stt/transcribe` available. Record a short audible phrase (e.g., "你好").

- [ ] Transcribing indicator disappears → Pet bubble enters "thinking" state
- [ ] Backend `/chat` receives the transcript (not raw audio bytes)
- [ ] `presenceState.voiceTranscript` is cleared after send (no stale transcript on next recording)
- [ ] DevTools Network tab (or backend log) confirms POST to `/chat` with `message` = transcript text

**Pass:** Transcript delivered to `/chat`; thinking bubble shows; voice transcript cleared.

---

### 5. Pet 是否出現 Thinking → Reply

**Precondition:** Step 4 passed; `/chat` responding.

- [ ] Pet bubble shows "thinking" state (spinner / thinking text) while waiting for `/chat`
- [ ] Pet mood expression changes to "focused" during thinking
- [ ] On `/chat` response: bubble transitions to "speaking" or "long_reply" state
- [ ] Reply text is clean character-facing text (no raw JSON, no traceback, no `source=` prefixes)
- [ ] Pet expression updates to mood from response

**Pass:** thinking → reply transition clean; no raw diagnostics in bubble text.

---

### 6. TTS ON 時是否會朗讀回覆

**Precondition:** Pet menu → "語音播放: 關" → toggle to "語音播放: 開" (TTS enabled).

- [ ] Pet menu shows "語音播放: 開" after toggle
- [ ] After a `/chat` reply arrives: `speechSynthesis.speak()` fires → audible speech
- [ ] `data-speaking="true"` set on `#pet-mode-root` during speech
- [ ] Speech uses reply text (not thinking text, not error text)
- [ ] When recording starts during TTS: previous speech cancelled (`stopPetSpeech()` called)

**Pass:** Audible TTS after reply; `data-speaking` attribute correct; stopped on new recording.

---

### 7. TTS OFF 時是否不朗讀

**Precondition:** TTS disabled (Pet menu shows "語音播放: 關").

- [ ] Send a chat via voice → reply arrives → no audible speech
- [ ] `data-speaking` attribute does not appear on `#pet-mode-root`
- [ ] Send a chat via Pet direct text input → no audible speech
- [ ] Toggle TTS OFF mid-reply: current speech stops; subsequent replies silent

**Pass:** No speech fired when TTS is off.

---

### 8. Quiet Mode ON 時行為

**Precondition:** Pet menu → toggle Quiet Mode ON.

#### 8a. Idle Bubble Suppressed
- [ ] Idle rotation stops — bubble stays collapsed or shows `idle_default` without cycling
- [ ] Pet hint text (`#pet-hint`) hidden (CSS `display:none` when Quiet Mode ON)
- [ ] No new idle-rotation texts cycle automatically

#### 8b. Voice Recording 仍可用
- [ ] Click mic → recording starts normally (Quiet Mode does NOT block recording)
- [ ] Recording indicator appears; text input hidden
- [ ] Record phrase → STT → `/chat` → reply → bubble updates normally

#### 8c. Chat Reply TTS 行為符合設計
- [ ] With TTS ON + Quiet Mode ON: TTS still fires for `"speaking"` / `"long_reply"` states
- [ ] With TTS OFF + Quiet Mode ON: no speech (same as non-Quiet Mode)
- [ ] Error/timeout states: TTS blocked by `speakPetReply` state guard (same as non-Quiet Mode)

**Pass:** Idle suppressed; recording unaffected; TTS behaviour unchanged by Quiet Mode.

---

### 9. Voice Settings Panel

**Precondition:** Pet menu → click "語音設定 ▶" to expand voice settings panel.

- [ ] Panel expands; all controls visible: voice selector, rate, pitch, volume sliders, reset button
- [ ] Voice selector (`#pet-tts-voice-select`) populates with system voices from `speechSynthesis.getVoices()`
- [ ] Rate slider (`#pet-tts-rate`): range 0.7–1.3, step 0.05; default 1.00; value shown beside slider
- [ ] Pitch slider (`#pet-tts-pitch`): range 0.8–1.3, step 0.05; default 1.00; value shown beside slider
- [ ] Volume slider (`#pet-tts-volume`): range 0.0–1.0, step 0.05; default 1.00; value shown beside slider
- [ ] Changing a slider → value label updates immediately
- [ ] Settings persist across Pet Window close and reopen (localStorage: `pet_tts_rate`, `pet_tts_pitch`, `pet_tts_volume`, `pet_tts_voice`)
- [ ] "重設語音設定" button resets all sliders to defaults (rate 1.00, pitch 1.00, volume 1.00)
- [ ] Reset also clears voice selector to browser default

**Pass:** All controls present, ranges correct, localStorage persistence confirmed, reset works.

---

### 10. 錄音時文字輸入是否隱藏或互斥

**Precondition:** Pet Window open; `#pet-direct-input-panel` accessible.

- [ ] Start recording → `.pet-direct-input-panel` not visible (CSS: `[data-recording="true"] .pet-direct-input-panel { display:none }`)
- [ ] Transcribing state → `.pet-direct-input-panel` still hidden (CSS: `[data-transcribing="true"] .pet-direct-input-panel { display:none }`)
- [ ] Open Pet direct text input during recording → `cancelPetVoiceRecording()` called → recording cancelled; text input opens
- [ ] Start recording while text input open → `closePetDirectInput()` called → text input closes; recording starts

**Pass:** Text input and recording are fully mutually exclusive in both directions.

---

### 11. Transcribing 時是否不能再次錄音

**Precondition:** Recording active → stopped → transcribing state active.

- [ ] Click mic during transcribing → `openPetVoiceRecording()` returns early (`isTranscribingActive()` guard)
- [ ] No new recording starts while transcribing
- [ ] Transcribing indicator remains visible; not replaced by recording indicator
- [ ] After transcribing completes (or errors): mic can be clicked again normally

**Pass:** `isTranscribingActive()` guard prevents re-recording; state machine remains consistent.

---

### 12. 錯誤情境文案是否乾淨

**Test each error condition independently. All messages must be clean Chinese strings — no raw exceptions, no tracebacks, no internal field names.**

#### 12a. 沒麥克風 (No Mic Device)
- [ ] OS mic disabled / unplugged → click mic → bubble shows: **"找不到麥克風裝置。請確認麥克風已連接。"**
- [ ] No raw `NotFoundError` or JS exception visible

#### 12b. 權限拒絕 (Mic Permission Denied)
- [ ] OS mic permission denied → click mic → bubble shows: **"麥克風權限被拒絕。請在系統設定中開啟麥克風權限。"**
- [ ] No raw `NotAllowedError` visible

#### 12c. STT Unavailable (faster-whisper Not Installed)
- [ ] Backend running but `faster-whisper` not installed → after transcribing → bubble shows: **"語音辨識目前不可用。"**
- [ ] Backend returns `{ status: "unavailable" }` — not a 500 error

#### 12d. Backend Offline
- [ ] Backend not running → after transcribing → bubble shows: **"後端離線，無法辨識語音。"**
- [ ] No raw HTTP error / connection refused message visible

#### 12e. Empty Audio
- [ ] Record in silence (no speech) → transcribing completes → bubble shows: **"沒有偵測到語音，請再試一次。"**
- [ ] Backend returns `{ status: "empty" }` — handled gracefully

**Pass for each:** Clean Chinese message shown; no raw exception/traceback/field name visible.

---

### 13. Pet Direct Text Input 是否沒有被 Voice 狀態破壞

**Precondition:** No voice activity. Ensure TTS OFF for clean test. Then TTS ON for step 3.

- [ ] Open Pet direct text input (e.g., keyboard shortcut or menu) → input field appears
- [ ] Type a message → submit → Pet bubble shows reply; Full App chat updates
- [ ] Pet expression updates with mood from reply
- [ ] With TTS ON: TTS speaks the reply from direct text input
- [ ] Voice recording in progress → text input hidden (mutual exclusion — same as item 10)
- [ ] No console errors related to Provider Settings changes (TASK-189/190 regression check)
- [ ] `#pet-direct-input-panel` state not corrupted by previous voice recording/transcribing session

**Pass:** Direct text input works independently; voice state does not corrupt it.

---

### 14. Full App Chat / Pet Reply Mirror 是否正常

**Precondition:** Full App open; Pet Window open. Backend live.

- [ ] Send chat in Full App → reply arrives in Full App chat area
- [ ] Pet bubble mirrors the reply (IPC `pet:speech` fired from `renderer.js`)
- [ ] Pet expression updates in Pet Window to match mood in reply
- [ ] Pet bubble shows reply text only (no raw JSON, no `source=`, no diagnostics)
- [ ] Voice recording from Pet Window does not crash or affect Full App chat display
- [ ] TTS fires in Pet Window for mirrored reply (if TTS ON)
- [ ] No console errors in either window

**Pass:** Full App → Pet mirror works; voice path does not interfere with Full App chat.

---

## Findings

**No bugs found.** All 101 automated voice/STT/TTS tests pass. No regressions introduced by TASK-188, TASK-189, or TASK-190 (which touched only Full App renderer files, not Pet Window).

**TASK-192 status:** Manual smoke checklist expanded to 14 executable items (2026-05-31). Awaiting Windows manual smoke run.

### Areas with No Automated Test Coverage (Manual-only)

| Area | Gap reason |
|---|---|
| Actual `getUserMedia` mic capture | Browser API — Node.js test harness cannot mock OS audio devices |
| `speechSynthesis.speak()` audio output | Browser TTS API — no audio output in smoke tests |
| faster-whisper transcription quality | Requires real model + audio — mocked in pytest |
| Voice selector dropdown content | Requires real browser `getVoices()` list |
| 30-second recording timeout in UI | Requires real-time wait — not tested in automated suite |
| Click-through state during recording | Windows IPC — requires live Electron |

### Pre-existing Limitations (Not Regressions)

| # | Limitation | Status |
|---|---|---|
| L1 | faster-whisper "tiny" model may struggle with accented speech or background noise | Known — transcription quality depends on model and hardware |
| L2 | TTS voice availability depends on system language packs | Known — graceful fallback to browser default |
| L3 | `speechSynthesis` may not fire `voiceschanged` on all platforms | Known — `getVoices()` called on both load and event |
| L4 | STT `POST /stt/transcribe` multipart request built with manual boundary in main.js (no npm dep) | Known — brittle if boundary format changes; works on tested Node versions |
