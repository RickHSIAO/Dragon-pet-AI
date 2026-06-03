# Voice / TTS Research Note and Local Speech Roadmap

**Task:** TASK-227
**Status:** IMPLEMENTED - DOCS ONLY / NO WINDOWS SMOKE REQUIRED
**Date:** 2026-06-01
**Scope:** Voice / TTS / STT research note only. No runtime speech behavior is
implemented here.

This document records voice, TTS, and STT research context for Dragon Pet AI.
It is a roadmap and safety note, not an implementation. It does not change
renderer behavior, Pet Window behavior, backend behavior, `/chat`, IPC, TTS,
STT, audio skeletons, prompts, providers, assets, or persistence.

---

## 1. Purpose

The goal is to clarify Dragon Pet AI's future speech direction before adding any
new runtime audio path.

This note:

- Records a user-provided AI VTuber / livestream companion voice architecture as
  external reference material.
- Separates what applies to Dragon Pet AI from what should not be copied.
- Defines a local-first speech roadmap for a desktop pet.
- Records TTS/STT safety boundaries.
- Links speech work to the Interaction Output Queue / Priority Design.

This is not runtime. It is a research and architecture checkpoint.

---

## 2. External AI VTuber Architecture Summary

The user provided an external AI livestream / Discord voice architecture as a
reference. It is useful for research comparison, but it is not the target
architecture for Dragon Pet AI.

Reference components:

- STT: Groq Whisper `large-v3-turbo`.
- LLM: Anthropic Claude Haiku 4.5 with prompt cache plus a partially fine-tuned
  local LLM.
- TTS: ElevenLabs Tiffy Taiwanese Bilingual Narrator.
- Discord integration: `discord.js` and `@discordjs/voice`.
- Main program: Python 3.13 / `aiohttp`.
- Overlay: HTML/JS through Cloudflare Tunnel.
- Latency chain: cloud server -> Discord bot -> Discord voice channel -> user
  computer.
- Future local TTS direction: GPT-SoVITS local.
- Custom voice data requirement: approximately 30 minutes of good emotional
  recording data for voice work.

This architecture is optimized for livestream or Discord character use. Dragon
Pet AI is a local-first desktop pet and should avoid inheriting cloud or Discord
latency unless a future task explicitly designs an optional integration.

---

## 3. What Applies to Dragon Pet AI

Useful ideas:

- Persona/context pack influences voice style and script tone.
- Local-first speech is a good fit for a desktop pet.
- TTS should be a post-reply audio layer, not a new chat driver.
- STT should be explicit user action only.
- Output queue / priority rules should govern speech timing.
- GPT-SoVITS, F5-TTS, and CosyVoice are worth future local speech research.

---

## 4. What Should Not Be Copied

Dragon Pet AI should not copy these pieces by default:

- Discord voice chain.
- Cloudflare Tunnel overlay.
- Livestream chat / superchat queue model.
- Cloud-first TTS as primary runtime.
- Always-on voice routing.
- Any architecture that adds unnecessary latency for a local desktop pet.

---

## 5. Dragon Pet AI Local-First Voice Direction

Recommended direction:

- Desktop pet remains local-first.
- Local TTS is preferred.
- Cloud TTS may be an optional future provider, not the default.
- TTS is a post-reply audio layer.
- TTS must not call `/chat`.
- TTS must not affect chat history.
- TTS must not read diagnostics preview.
- TTS must obey `docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md`.
- STT must be push-to-talk or another explicit user action.
- No always-listening mode.
- No unconfirmed ambient audio to an LLM.

---

## 6. Current TTS Lab Status

Current known status:

- The user has an external TTS lab.
- ChatTTS WebUI can run as a local TTS experiment.
- Dragon Pet AI is not wired to that TTS lab.
- Any future TTS provider should start as a lab spike before entering Dragon Pet
  AI runtime.
- No external TTS provider is currently a Dragon Pet AI runtime dependency.

---

## 7. Candidate TTS / Speech Models

### ChatTTS

Potential value:

- Useful local research candidate.
- Good for quick speech experimentation.

Risks / unknowns:

- Runtime stability and voice consistency need testing.
- Character voice control may be limited.
- Must not be wired directly into Dragon Pet AI without a separate safe runtime
  task.

### GPT-SoVITS

Potential value:

- Strong candidate for local-first character voice research.
- Better fit for custom voice style experiments.

Risks / unknowns:

- Requires careful data preparation.
- Voice licensing and consent must be explicit.
- Training/inference complexity needs separate spike work.

### F5-TTS

Potential value:

- Research candidate for zero-shot or style-driven TTS.

Risks / unknowns:

- Needs quality, latency, and runtime packaging evaluation.
- Must be isolated from production runtime until explicitly designed.

### CosyVoice

Potential value:

- Research candidate for multilingual or style-controlled speech.

Risks / unknowns:

- Runtime footprint and licensing need review.
- Voice consistency and packaging need separate spike work.

### ElevenLabs

Potential value:

- High-quality cloud TTS reference.
- May be useful as optional future provider.

Risks / unknowns:

- Cloud dependency.
- Cost and account management.
- Voice licensing requirements.
- Not suitable as default local-first runtime.

---

## 8. STT Future Direction

Recommended STT direction:

- STT is an explicit feature, not ambient listening.
- Use push-to-talk or an explicit record button.
- No always listening.
- No wake-word capture by default.
- Do not store raw audio by default.
- Transcript may require user confirmation before `/chat`.
- Candidate providers: local Whisper, faster-whisper, or optional cloud STT.
- STT should not be coupled to Discord by default.

---

## 9. TTS Safety Rules

Future TTS must obey:

- TTS default off.
- TTS must never call `/chat` by itself.
- TTS must only read TTS-safe text.
- TTS must never read:
  - debug preview
  - metadata
  - JSON
  - source labels
  - hidden details
  - thinking text
  - provider diagnostics
  - raw event payload
- TTS must not read reaction bubbles unless a future task explicitly allows it.
- TTS must not write chat history.
- TTS must not export audio by default.
- TTS must support stop/cancel before default-on behavior is considered.
- TTS must obey Interaction Output Queue / Priority Design.

---

## 10. Voice Licensing / Ethics Rules

Voice work must remain legally and ethically clean:

- Do not clone a streamer, VTuber, voice actor, or private person's voice
  without clear authorization.
- Keep source recordings legally usable and documented.
- Separate speech mode from singing mode.
- Voice cloning requires explicit permission and appropriate source data.
- Do not imply official affiliation with a character, performer, or voice owner.
- Avoid uploading private user voice data to cloud services without explicit
  consent and documentation.

---

## 11. Proposed Future Tasks

Suggested research and implementation tasks:

- TASK-TTS-001 ChatTTS lab evaluation: seed / speaker / quality notes.
- TASK-TTS-002 GPT-SoVITS local character voice spike.
- TASK-TTS-003 F5-TTS / CosyVoice comparison spike.
- TASK-TTS-004 TTS provider interface design, docs-only.
- TASK-TTS-005 Dragon Pet AI audio skeleton, disabled by default.
- TASK-TTS-006 Local TTS provider integration behind user controls.
- TASK-STT-001 Push-to-talk STT design. **Covered by TASK-241 (DONE - WINDOWS VISUAL SMOKE PASS 2026-06-02).**
  Full App mic button: toggle-to-record, stop → STT → fills textarea, no auto-send,
  no always-listening. Narrow `transcribeAudio(arrayBuffer)` bridge in renderer
  preload routes to existing `stt:transcribe` IPC handler. No new IPC channel.
- TASK-STT-002 Local Whisper / faster-whisper spike.
- TASK-STT-003 Confirmed transcript to `/chat` flow. **Covered by TASK-241 + TASK-242 (DONE - WINDOWS VISUAL SMOKE PASS 2026-06-02):**
  TASK-241: transcript fills Full App input; user presses Send to trigger existing `/chat` flow.
  TASK-242: Auto-send Transcript toggle (default OFF) calls `sendMessage(trimmed)` after successful
  STT, using all existing guards (isSending, editingMessageState, validation, history). Empty
  transcript blocked. Concurrent send blocked. Auto-send never bypasses sendMessage. No new IPC.
  No Pet Window calls. Session-only toggle. Windows visual smoke PASS (2026-06-02).
- TASK-STT-004 Silence detection / VAD loop. **Covered by TASK-243 (DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS; implemented 2026-06-03, Windows visual smoke 2026-06-02):**
  Explicit conversation session (Start/Stop button). VAD via Web Audio API `AnalyserNode` RMS
  amplitude. States: off/waiting/speaking/transcribing/sending/error. Half-duplex guard: no
  recording while sending or transcribing. Auto-transcribe utterance after silence ≥ 1000 ms
  (after ≥ 300 ms speech). Max utterance 30 s. Reuses `transcribeFullAppAudioBlob` bridge
  (TASK-241 `stt:transcribe`). Fills textarea → `sendMessage(trimmed)` → re-arms to waiting.
  No direct `/chat` fetch and no sendMessage / isSending bypass. Conversation Mode defaults OFF,
  never starts on app launch, and cannot start when Voice Input is OFF. Stop Conversation releases
  mic stream, VAD timer, recorder, and audio context. No new IPC. No Pet Window calls. No TTS.
  No Output Queue or Diagnostics Drawer change. No audio persistence. No background listening.
  No always-listening. Session-only. 22 TASK-243 smoke tests PASS. Windows visual smoke PASS
  (2026-06-02): startup OFF/no auto mic, manual start, silence detection, auto STT + single send,
  half-duplex, consecutive utterances, stop, Voice Input OFF guard, empty/short audio handling, and
  general regression all confirmed.

- TASK-STT-005 VAD quality diagnostics and threshold tuning. **Covered by TASK-244 (IMPLEMENTED - NEEDS WINDOWS VOICE QUALITY SMOKE; implemented 2026-06-03):**
  Collapsible `<details>` diagnostics panel in Full App. Session-only RMS threshold number input
  (0.01–0.10, step 0.005) and silence duration select (800/1000/1200/1500 ms). Changes update
  session vars `fullAppConversationRmsThreshold` / `fullAppConversationSilenceMs`, which
  `_conversationVadTick` reads instead of the frozen constants. `fullAppVoiceDiagnostics` state
  object tracks: mode (manual_mic / manual_auto_send / conversation), recording start/end times,
  durationMs, Blob size, MIME type, chunk count, transcript length, transcript preview (capped 30
  chars, newlines stripped), emptyTranscript flag, autoSendEnabled, conversationState, stopReason
  (silence / max_duration / cancel / manual_stop), lastRms, maxRms, rmsThreshold,
  silenceDurationMs, minSpeechMs, maxUtteranceMs, speechStarted, silenceMsAtStop, sttStatus
  (none / success / empty / timeout / error). `renderFullAppVoiceDiagnostics` writes a multi-line
  string to `<pre id="voice-diagnostics-display">` via textContent only (never innerHTML).
  `updateFullAppVoiceDiagnostics` patches only known keys via hasOwnProperty. Diagnostics reset on
  every recording start; VAD tick updates lastRms/maxRms every 100 ms; stopReason/silenceMsAtStop
  set when utterance ends. Known VAD risks: (1) sentence-head clipping — MediaRecorder starts only
  after RMS exceeds threshold, so the first ~100 ms of an utterance may be missed; no pre-roll
  buffer yet, mitigation is lowering RMS threshold; (2) noise triggers — ambient sounds at or above
  threshold cause false positives; mitigation is raising threshold or reducing silence duration;
  (3) silence too short — 800 ms may cut mid-sentence pauses; (4) silence too long — 1500 ms
  increases latency. No localStorage. No new IPC. No Pet Window calls in diagnostics section. No
  audio persistence. No TTS. No always-listening. 22 TASK-244 smoke tests PASS (522 renderer-chat
  total). Windows voice quality smoke NEEDED.

- TASK-STT-006 STT language lock to prevent zh auto-detect misclassification. **Covered by TASK-245
  (DONE - LANGUAGE LOCK PASS / NEEDS STT MODEL QUALITY FOLLOW-UP; 2026-06-03):** Root cause confirmed:
  `/stt/transcribe` route did not pass `language` to `transcribe_audio_bytes` — Whisper auto-detected
  and misclassified short Chinese utterances as Thai/Malay/Indonesian. Fix: `_STT_DEFAULT_LANGUAGE =
  "zh"` constant added to `routes.py`; route now calls `transcribe_audio_bytes(..., language="zh")`;
  response augmented with `language`, `languageLocked: true`, `task: "transcribe"`. `stt_service.py`
  adds `_STT_PROVIDER` / `_STT_MODEL_NAME` constants; ok response includes `provider`, `model`,
  `detectedLanguage` (from `TranscriptionInfo.language`). Renderer `fullAppVoiceDiagnostics` gains 6
  new fields populated after each IPC call; `renderFullAppVoiceDiagnostics` shows `STT 語言`,
  `已鎖定`, `STT 任務`, `STT 提供者`, `模型`, `偵測語言` via textContent. No new IPC; no new
  endpoint; no Pet Window / Output Queue / Diagnostics Drawer change; no audio persistence; no TTS;
  no always-listening. 10 renderer-chat smoke tests + 9 backend pytest tests. renderer-chat-smoke
  PASS; backend pytest PASS. **Windows smoke result (2026-06-03):** language lock PASS — no more
  Thai/Malay/Indonesian misclassification; BUT faster-whisper `tiny` model Chinese accuracy poor
  (「這是中文語音辨識測試」→「這文中位與英編輯測試」). Language lock fix validated; model quality
  issue is a separate problem requiring TASK-246 (Whisper model upgrade to `small` or `base`).

- TASK-STT-007 Configurable STT model via env var. **Covered by TASK-246 (DONE - MODEL CONFIG
  PASS / NEEDS TRANSCRIPT CORRECTION FOLLOW-UP; 2026-06-03):** Added `DRAGON_PET_STT_MODEL`
  env var support; allowed `tiny`/`base`/`small`; safe fallback; model resolution + load status
  surfaced in diagnostics. 10 renderer-chat + 13 backend pytest tests PASS. **Windows smoke
  result (2026-06-03):** env var model switching works; diagnostics show requestedModel /
  resolvedModel correctly. BUT switching tiny → base/small does NOT sufficiently improve zh
  accuracy. Root cause: raw Whisper output lacks context-aware post-processing / hotword
  normalization. "感覺沒有智能辨字系統". Language lock (TASK-245) not regressed.

- TASK-STT-008 STT transcript correction / context-aware normalization. **Covered by TASK-247
  (DONE - WINDOWS TRANSCRIPT CORRECTION SMOKE PASS / NEEDS HOTWORD COVERAGE FOLLOW-UP; 2026-06-03):**
  Added deterministic phrase/hotword correction helper `correct_transcript_text(raw_text)` to
  `stt_service.py`. `_STT_CORRECTION_MAP` covers known acoustic confusions: 中文語音編輯/邊記/
  中位與英編輯 → 中文語音辨識; 語音編輯/邊記測試 → 語音辨識測試; 克里斯蒂娜/克莉斯蒂娜/克麗絲蒂娜 →
  克莉絲蒂娜. `transcribe_audio_bytes()` ok path applies correction; `transcript` =
  `correctedTranscript`; `rawTranscript` preserved for diagnostics. 19 backend pytest + 10 renderer
  smoke tests PASS. Windows smoke PASS (2026-06-03): correction layer works; Auto-send / Conversation
  Mode use corrected transcript; raw not in history; regressions clear. Remaining issue: hotword
  coverage insufficient — proper nouns (esp. 克莉絲蒂娜) still produced as STT variants not yet in
  correction map. LLM semantic rewrite deferred to TASK-249+.

- TASK-STT-009 STT hotword coverage / alias expansion. **Covered by TASK-248
  (DONE - HOTWORD MAP EXPANDED / NEEDS STT PROVIDER FOLLOW-UP; 2026-06-03):**
  `_STT_CORRECTION_MAP` expanded from 8 to 48 entries: 19 克莉絲蒂娜 aliases (16 new),
  7 Dragon Pet AI, 4 Claude/Claude Code, 4 CodeX, 3 faster-whisper/Whisper, 6 feature terms.
  `correct_transcript_text()` returns `matchedAlias` / `canonicalTerm`. Renderer diagnostics
  shows "命中 alias / canonical" line. 13 backend pytest + 9 renderer smoke tests PASS.
  Windows smoke PARTIAL (2026-06-03): alias map logic correct; but faster-whisper `tiny`
  produces incoherent whole-sentence zh errors (「可以是DNA按」、「墨鯰墨鯰」、「先跟佩套AI」)
  that no correction map can fix. Root cause: STT provider ASR quality, not hotword coverage.
  Hotword map preserved as complement; STT provider replacement needed.

- TASK-STT-010 Free local Chinese STT provider evaluation. **Covered by TASK-249 (DONE - WINDOWS STT PROVIDER SMOKE PASS; 2026-06-03):**
  `DRAGON_PET_STT_PROVIDER` env var resolver; FunASR `_transcribe_funasr()` skeleton (safe unavailable
  if not installed; `paraformer-zh` model; no auto-download); sherpa-onnx design-only (always unavailable).
  7 provider metadata fields in every response. 6 renderer diagnostics fields. 85 pytest + 11 renderer
  smoke tests pass. Windows smoke: 35/35 PASS (provider resolution + metadata + clean unavailable).

  **Extended by TASK-250 (BLOCKED - WINDOWS FUNASR INSTALL FAILED / PYTHON 3.14 EDITDISTANCE BUILD ISSUE; 2026-06-03):**
  FunASR full runtime DONE in Python: `_parse_funasr_result()` multi-format parser; `_FUNASR_HOTWORDS` constant;
  `_transcribe_funasr()` complete (BytesIO, hotword boosting with TypeError fallback, correction layer,
  provider metadata in all paths). `scripts/funasr_probe.py` + `scripts/install-funasr.ps1` (with Python >= 3.14 guard).
  `scripts/create-funasr-venv.ps1` (new, Option A: py -3.11 / py -3.10 fallback venv to bypass cp314 editdistance build failure; dev machine used Python 3.10 — py -3.11 pointed to non-functional D:\Tool\python.exe).
  `.gitignore` updated (`.venv-funasr/` excluded). 11 new pytest (96 total); 50/50 provider smoke PASS.
  BLOCKED: `backend\.venv` is Python 3.14 (cp314); no pre-built editdistance wheel; build requires MSVC 14.0+.

- **TASK-STT-012 (TASK-251) FunASR Sidecar Bridge. DONE (2026-06-03):** Subprocess sidecar
  (`scripts/funasr_sidecar_transcribe.py`) runs under `.venv-funasr` Python 3.10 (dev machine:
  py -3.11 pointed to non-functional D:\Tool\python.exe; `.venv-funasr` built with Python 3.10);
  audio bytes via stdin; JSON result via stdout. `_run_funasr_sidecar()` in `stt_service.py` with
  300-second timeout. JSON parsed from last `{`-prefixed stdout line (robust to funasr progress noise).
  `DRAGON_PET_FUNASR_PYTHON` env var override. Live sidecar: status=ok, loadStatus=loaded.

- **TASK-STT-013 (TASK-252) WAV PCM Input for FunASR. DONE - WINDOWS MIC SMOKE PASS (2026-06-03):**
  Fixed Full App voice failure: MediaRecorder `audio/webm;codecs=opus` cannot be decoded by
  torchaudio (no ffmpeg). Solution: Web Audio API `ScriptProcessorNode` PCM capture at 16 kHz.
  `_encodeWavPcm()` encodes `Float32Array` → 16-bit mono WAV Blob. Both manual mic and
  conversation mode produce WAV. main.js Content-Type updated to `audio/wav`.
  **Windows mic smoke PASS**: FunASR sidecar receives Full App mic audio, Paraformer-zh
  produces Chinese transcript, accuracy clearly better than faster-whisper-local.
  Remaining: inter-character spaces + simplified Chinese → TASK-253; cold-start latency → TASK-254.

- **TASK-STT-014 (TASK-253) FunASR Transcript Normalisation / Traditional Chinese Output. DONE - WINDOWS NORMALIZATION SMOKE PASS (2026-06-03):**
  Deterministic normalisation layer on `_transcribe_funasr()` ok-path. Two-stage pipeline:
  (1) `_remove_cjk_spaces()` — regex lookbehind/lookahead strips spaces between CJK Unified
  Ideographs (Unicode ranges 4E00–9FFF, 3400–4DBF, F900–FAFF); (2) `_simp_to_trad()` —
  `opencc-python-reimplemented` with `OpenCC("s2tw")` preferred (Simplified → Traditional Taiwan);
  falls back to 20-char static `str.maketrans()` map if opencc unavailable. Returns `(text, method)`
  tuple; `tradMethod` field surfaces "opencc" or "static" in every response. Nine new
  Paraformer-specific `_STT_CORRECTION_MAP` entries: jdden/jden pet ai, dragon pet a i,
  cloud/claud code, codex, t a s k, task, 克莉莉. Response adds normalizedTranscript,
  normalizationApplied, normalizationSteps, cjkSpacingRemoved, traditionalApplied, tradMethod;
  rawTranscript = pre-norm sidecar output. 27 new pytest (133 total); [7/7] smoke section
  (86/86 PASS). Windows manual smoke PASS: OpenCC s2tw active, all tested sentences normalised
  correctly. Remaining: cold-start latency 10–30 s → TASK-254.

- **TASK-STT-015 (TASK-254) Persistent FunASR Sidecar / Warm Model Server. DONE - WINDOWS WARM SIDECAR SMOKE PASS / NEEDS WINDOW UX FOLLOW-UP (2026-06-03):**
  New `scripts/funasr_sidecar_loop.py` — persistent stdin/stdout JSON loop that loads paraformer-zh
  once at startup and stays warm between calls. Protocol: ready → transcribe → result JSON messages;
  audio sent as base64 over stdin (never written to disk). `_PROTO_BUF = sys.stdout.buffer` saved before
  `sys.stdout = sys.stderr` redirect suppresses funasr/modelscope progress noise on protocol stream.
  `--hotwords` argparse arg passed at launch. Backend `_run_funasr()` dispatcher: persistent sidecar
  with 1 restart attempt → one-shot `_run_funasr_sidecar()` fallback. Module-level lock serializes
  concurrent calls; daemon stdout-reader thread + `queue.Queue`; 120 s startup timeout; 60 s
  per-request timeout. `DRAGON_PET_FUNASR_PERSISTENT=false` env disables (default: true). Response
  adds `funasrSidecarMode`, `funasrSidecarWarm`, `funasrSidecarRestarted`. `_transcribe_funasr()`
  delegates to `_run_funasr()`. TASK-253 normalisation + TASK-247/248 correction still apply on ok-path.
  18 new pytest (151 total); [8/8] smoke section. No audio to disk, no IPC, no schema change,
  Whisper path unmodified. Windows smoke PASS (2026-06-03): first call slower (warmup), subsequent
  Manual Mic and Conversation Mode clearly faster; OpenCC/correction regression PASS; no raw stack;
  no raw audio persistence. Follow-up: TASK-255 voice capture focus/minimize; TASK-256 Pet click/Show.

- **TASK-STT-016-adjacent (TASK-255) Voice Capture Focus/Minimize Resilience. DONE - WINDOWS FOCUS/MINIMIZE VOICE SMOKE PASS / NEEDS STARTUP WARMUP FOLLOW-UP (2026-06-04):**
  Root causes: (1) Chromium background throttling pauses 100 ms VAD `setInterval`; (2) `AudioContext`
  auto-suspended when window loses focus or is minimized. Fixes: `backgroundThrottling: false` in
  fullAppWindow webPreferences only (Pet Window excluded). `_resumeConversationAudioContextIfSuspended()`
  helper called every VAD tick and on `visibilitychange`/`focus` events. Does NOT cancel voice on
  hidden/blur. Six new `fullAppVoiceDiagnostics` fields: `voiceCaptureFocusSafe`, `lastVisibilityState`,
  `lastWindowFocusState`, `audioContextState`, `captureInterruptedReason`, `captureInterruptedByVisibility`.
  17 new renderer smoke tests PASS. No always-listening, no new IPC, no raw audio, no Pet Window /
  Output Queue / Diagnostics Drawer changes.

- **TASK-STT-016-adjacent (TASK-256) Startup Warmup / STT + Ollama Preload. DONE - WINDOWS STARTUP WARMUP SMOKE PASS (2026-06-04):**
  New `POST /stt/warmup` — starts funasr-local persistent sidecar without audio; skipped for other
  providers. New `POST /llm/warmup` — pings Ollama `/api/generate` with `keep_alive` and no prompt
  to load model into VRAM; skipped for non-Ollama/mock providers. Renderer fires both in parallel
  3 s after health-check PASS; best-effort, never throws. `STARTUP_WARMUP_ENABLED`,
  `STARTUP_STT_WARMUP_ENABLED`, `STARTUP_OLLAMA_WARMUP_ENABLED` constants. Eight new
  `fullAppVoiceDiagnostics` warmup fields. 12 new pytest; 15 new renderer smoke tests; `[9/9]`
  section in stt_provider_smoke.py. Windows smoke PASS: app does not open mic or auto-send on
  startup; STT warmup PASS; Ollama warmup PASS; first Manual Mic latency improved; first Ollama
  response latency improved; regression PASS. No mic, no audio bytes, no getUserMedia, no chat,
  no new IPC, no Pet Window / Output Queue / Diagnostics Drawer changes.

- **TASK-256b Diagnostics / Voice Panel Readability Polish. DONE - WINDOWS DIAGNOSTICS READABILITY SMOKE PASS (2026-06-04):**
  CSS-only change to `styles.css`. `.voice-diagnostics-display` 10px → 13px, `line-height` 1.55,
  `max-height` 200px → 340px. `.voice-diagnostics-summary` 12px → 14px + `font-weight: 500`.
  All tuning labels/hints/preview text ≥ 12px. Panel padding and section spacing increased.
  Windows smoke PASS: diagnostics readability visibly improved. No STT/warmup runtime changes.

- TASK-STT-016 LLM-based semantic correction. **(PLANNED; future):** Optional
  follow-up to apply a local LLM pass over the corrected transcript for further semantic
  accuracy. Must be guarded by explicit user opt-in and must not replace the deterministic
  layer from TASK-247/248.

Recommended next: TASK-257 — Pet Window Click / Show Pet Idempotent Behavior.

Each future task must explicitly define safety boundaries, user controls,
provider scope, queue priority, and no-regression checks.

Each future task must explicitly define safety boundaries, user controls,
provider scope, queue priority, and no-regression checks.

---

## 12. Relationship to Existing Docs

Related docs:

- `docs/INTERACTIVE_COMPANION_ARCHITECTURE.md`
- `docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md`
- `docs/CHRISTINA_PERSONA_CONTEXT_PACK.md`

Relationship:

- Persona pack controls speech style guidance and TTS-safe script style.
- Output queue controls timing, priority, and interruption rules.
- Voice/TTS research controls provider candidates, licensing, and local-first
  roadmap.
- None of these docs wire runtime behavior by themselves.

---

## 13. TASK-227 Runtime Boundary

TASK-227 is docs-only. It does not:

- Change renderer behavior.
- Change Pet Window behavior.
- Change backend behavior.
- Change `/chat` API schema.
- Change chat history persistence format.
- Add IPC.
- Add generic IPC.
- Add a TTS runtime path.
- Add STT.
- Add an audio skeleton.
- Call `/chat`.
- Change Ollama / Provider runtime.
- Change prompt runtime.
- Add assets.
- Add or train a voice model.
- Commit or push changes.
