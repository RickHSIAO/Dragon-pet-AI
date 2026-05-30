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

> For use when running Pet Window in development. `npm start` with backend live.

### A. Mic Button / Recording

- [ ] Pet Window visible — mic button (🎤) visible in nav bar at S/M/L scales
- [ ] Click mic → recording indicator (pulsing red dot) appears
- [ ] Click mic again → recording stops, transcribing indicator (spinner) appears
- [ ] Press Esc during recording → recording cancelled, no STT call, bubble shows idle
- [ ] Click ✕ → recording cancelled cleanly
- [ ] 30-second hard timeout: wait 30 s without stopping → auto-stop and STT attempt

### B. Recording → Transcribing → Chat Handoff

- [ ] Record a short phrase → STT completes → transcript sent to `/chat`
- [ ] Pet bubble shows "thinking" during STT + chat
- [ ] Pet reply renders in bubble, TTS speaks if enabled
- [ ] `presenceState.voiceTranscript` is cleared after send (no stale transcript)

### C. TTS On/Off

- [ ] Pet menu "語音播放: 關" toggles TTS on → "語音播放: 開"
- [ ] With TTS ON: reply from `/chat` is spoken via `speechSynthesis`
- [ ] With TTS ON and recording starts: previous TTS speech is cancelled
- [ ] TTS OFF: no speech on reply

### D. TTS Settings Panel

- [ ] Click "語音設定 ▶" → voice settings panel expands
- [ ] Voice selector populates from `speechSynthesis.getVoices()`
- [ ] Rate/pitch/volume sliders adjust values (displayed beside slider)
- [ ] Values persist across Pet Window restart (localStorage)
- [ ] "重設語音設定" resets all sliders to defaults (rate 1.00, pitch 1.00, volume 1.00)

### E. Quiet Mode Interaction

- [ ] Quiet Mode ON: idle rotation stops, bubble collapses
- [ ] Quiet Mode ON: Pet hint text hidden
- [ ] Quiet Mode ON: voice recording still works (not suppressed)
- [ ] Quiet Mode ON: TTS still plays for chat replies
- [ ] Quiet Mode OFF: idle rotation resumes after cooldown

### F. Error Message Cleanliness

- [ ] Recording with mic blocked → Chinese error, no raw exception in bubble
- [ ] Backend down → STT offline message in Chinese, no raw traceback
- [ ] faster-whisper not installed → "語音辨識目前不可用", no raw error
- [ ] Empty audio → "沒有偵測到語音", no raw error

### G. Mutual Exclusion

- [ ] During recording: Pet text input panel not visible
- [ ] During transcribing: Pet text input panel not visible
- [ ] During recording: TTS speaking indicator not visible
- [ ] Open Pet direct text input → active recording is cancelled

### H. Pet Direct Text Input — Voice Regression

- [ ] Type in Pet text field, submit → chat reply appears, bubble updates
- [ ] Voice recording in progress: text input hidden
- [ ] TTS speaks on direct input reply if TTS ON
- [ ] No regression from TASK-189/190 Provider Settings changes (separate section)

---

## Findings

**No bugs found.** All 101 automated voice/STT/TTS tests pass. No regressions introduced by TASK-188, TASK-189, or TASK-190 (which touched only Full App renderer files, not Pet Window).

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
