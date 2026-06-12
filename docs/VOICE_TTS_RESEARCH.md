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
- TASK-STT-002 Local Whisper / faster-whisper spike. **Covered by TASK-STT-002
  (IMPLEMENTED - LOCAL QUALITY PROBE / NO RUNTIME DEFAULT CHANGE; 2026-06-11):**
  Added `scripts/stt_quality_probe.py` for repeatable Chinese STT model quality
  comparison across faster-whisper `tiny`, `base`, `small`, and optional
  `medium`, using explicit WAV/reference pairs or a private manifest. Missing
  models are skipped by default unless `--allow-download` is passed. No runtime
  default changed.
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

- TASK-244 VAD quality diagnostics and threshold tuning. **Covered by TASK-244 (IMPLEMENTED - NEEDS WINDOWS VOICE QUALITY SMOKE; implemented 2026-06-03):**
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

- Legacy STT model config note: earlier TASK-STT-007 draft, Configurable STT model via env var. **Covered by TASK-246 (DONE - MODEL CONFIG
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

- **TASK-STT-001 Chinese STT Punctuation Restoration / Transcript Readability. IMPLEMENTED (2026-06-05):**
  Adds a local deterministic punctuation layer after existing transcript correction. Processing
  order: raw STT transcript -> safe-dictionary correction -> punctuation restoration -> final
  transcript. `rawTranscript` is preserved; `correctedTranscript` remains the safe-dictionary
  output; `punctuatedTranscript` / `finalTranscript` are added for ok responses; `transcript`
  equals `finalTranscript`, so Manual Mic textarea fill and Conversation Mode `/chat` use the
  readable version. Diagnostics add `punctuationApplied`, `punctuationMode`, and
  `punctuationReason`. First version is conservative text-only punctuation because the current
  backend provider paths do not expose stable segment/pause metadata after joining transcripts:
  it only adds a terminal CJK sentence mark for sufficiently long unpunctuated text and leaves
  empty, short ambiguous, non-CJK, and already-punctuated text unchanged. No LLM rewrite,
  paraphrase, invented words, hidden prompts, new IPC, `/stt/transcribe` request schema change,
  `/chat` schema change, Pet Window / Output Queue change, recording behavior change, or Owner
  Voice Gate behavior change.

- **TASK-STT-002 Chinese STT Quality Baseline / Model Comparison. IMPLEMENTED (2026-06-11):**
  Adds `scripts/stt_quality_probe.py`, a local benchmark that accepts repeated
  `--sample <wav> --reference <text>` pairs or a JSON manifest with `id`,
  `path`, `reference`, `sourceType`, and optional `notes`. It compares
  faster-whisper `tiny`, `base`, `small`, and optional `medium`; missing models
  are cleanly skipped by default unless `--allow-download` is passed. Each
  result preserves raw STT output and reports raw/corrected/punctuated/final
  transcripts, reference, character error rate, raw character error rate,
  latency, audio duration, real-time factor, repeated-token warning,
  empty-transcript warning, and error text. `sourceType` values
  `manual_mic`, `conversation_mode`, and `external_clean_reference` help
  distinguish capture/VAD issues from model quality issues. Recommended
  non-private Chinese sample categories: long natural sentence, short phrase,
  names such as `克莉絲蒂娜`, numbers/dates, technical words, repeated-syllable
  stress, normal volume, and quiet volume. Current runtime still selects
  faster-whisper `tiny` by default through `DRAGON_PET_STT_MODEL`; test-only
  overrides can set `DRAGON_PET_STT_MODEL=small` before backend start, but this
  task does not change the default.

- **TASK-STT-003 Runtime STT Model Override / base-small Candidate Smoke. IMPLEMENTED (2026-06-11):**
  Adds `DRAGON_STT_MODEL` as the preferred short runtime override for Manual
  Mic and Conversation Mode candidate smoke. Legacy `DRAGON_PET_STT_MODEL`
  still works; `DRAGON_STT_MODEL` has priority when both are set. Allowed
  runtime values are `tiny`, `base`, and `small`; invalid values fall back to
  `tiny` and surface `modelFallbackReason=invalid_model`. Diagnostics include
  requested/resolved model, model source, model env, model fallback reason,
  load status/error, provider load/fallback, and raw/corrected/punctuated/final
  transcript previews. TASK-STT-002 samples make `base` the first runtime
  candidate and keep `small` as a slower quality candidate, especially for
  names and mixed Chinese/English technical terms. The committed default is not
  changed.

- **TASK-STT-004 STT No-Speech / Silence Hallucination Guard. DONE - WINDOWS RUNTIME NO-SPEECH SMOKE PASS / DEFAULT UNCHANGED (2026-06-11):**
  Windows runtime smoke found that faster-whisper `small` can hallucinate a
  subtitle-credit-like transcript on intentional Manual Mic silence. This is a
  no-speech detection failure, not a transcript correction problem. The backend
  now computes WAV PCM audio energy diagnostics and combines strong silence
  evidence with faster-whisper segment metadata (`no_speech_prob`, avg logprob,
  compression ratio, segment count) and conservative subtitle-credit pattern
  checks. Guarded results return `status=no_speech` with empty final transcript.
  Manual Mic does not fill textarea or auto-send; Conversation Mode does not
  enqueue/send chat and still rearms or drains according to existing policy.
  Real speech is not suppressed merely because it contains a suspicious token.
  Windows runtime closeout passed for Manual Mic silence and real speech with
  both `DRAGON_STT_MODEL=small` and `DRAGON_STT_MODEL=base`, plus Conversation
  Mode silence / no-speech path. Silence did not fill hallucinated subtitle
  credit or creator-CTA text and did not send normal chat. Default runtime model
  remains `tiny`; `base` and `small` remain override candidates only.

- **TASK-STT-005 Runtime STT Model Selection UI / base-small Candidate Setting. DONE - WINDOWS RUNTIME MODEL SWITCH SMOKE PASS / DEFAULT UNCHANGED (2026-06-12):**
  Adds a session-only Full App `STT model` selector for runtime testing:
  `Default / env`, `tiny`, `base`, and `small`. `Default / env` sends no
  request model and preserves existing env/default resolution. Explicit
  `tiny`/`base`/`small` selections are sent as a multipart `model` field to
  `/stt/transcribe` for Manual Mic and Conversation Mode. The committed default
  remains `tiny`; `base` remains the first runtime candidate from TASK-STT-002
  and `small` remains the slower quality candidate. Diagnostics now distinguish
  UI selected model, request model sent, backend requested/resolved model,
  source, fallback reason, provider load state, and model load error. Invalid
  request values fall back safely without crashing. This does not add a new IPC
  channel and does not change `/chat`, mood schema, Owner Voice hard-gate
  behavior, queue/pre-roll/drain policy, raw audio persistence, or committed
  sample handling. Windows runtime model-switch smoke passed for `base` Manual
  Mic, `small` Manual Auto-send, `Default / env` Manual Auto-send, and `base`
  Conversation Mode. The committed default remains `tiny`; `base` and `small`
  remain runtime candidates only.

- **TASK-STT-006A Backend STT Model Evaluation Report. DONE - WINDOWS AUDIO SAMPLE EVALUATION PASS / REPORT DATA COLLECTION READY (2026-06-12):**
  Adds `scripts/stt_model_evaluation_report.py` for backend-side data
  collection before any recommendation or AI explanation layer. The script
  compares `tiny`, `base`, and `small` over the same local user-provided audio
  samples through the runtime STT service path, then writes JSON under
  `outputs/stt_model_evaluation/YYYYMMDD/`. The report captures safe
  environment info, redacted sample basename, duration/file size, latency/RTF,
  raw/final transcript, no-speech guard diagnostics, audio RMS/peak/speech
  signals, provider/model load state, fallback, and per-model errors. This does
  not choose a `recommendedModel`, does not add subjective AI explanation, and
  does not add a frontend comparison panel. The committed default remains
  `tiny`; `base` and `small` remain runtime candidates only. Windows sample
  evaluation passed on two local owner WAV samples with all three models
  producing 2/2 successful results and no `no_speech` or error result. Observed
  sample evidence: `tiny avgLatencyMs=2689.5`, `base avgLatencyMs=1758.0`, and
  `small avgLatencyMs=4751.0`. These latency values are recorded only as sample
  evidence; they are not a recommendation and do not make `base` the default.

- **TASK-STT-006B Deterministic STT Model Scoring. DONE - WINDOWS SCORING REPORT SMOKE PASS / DETERMINISTIC SCORING READY (2026-06-12):**
  Adds `scripts/stt_model_scoring_report.py` for deterministic scoring of a
  TASK-STT-006A evaluation report. The report aggregates success/error/no-speech
  rates, latency/RTF, transcript signal, speech evidence, no-speech guard /
  hallucination-risk signals, fallback counts, and provider/model load errors,
  then produces 0-100 runtime-suitability scores for `tiny`, `base`, and
  `small`. Profiles `manual_mic`, `conversation`, and `balanced` adjust the
  weights; `conversation` penalizes slow models harder. This is not true
  transcript accuracy or WER scoring unless reference transcripts are added in a
  later task. It does not add LLM/AI explanation, does not auto-switch runtime
  models, and does not change the committed default `tiny`; `base` and `small`
  remain runtime candidates only.

  Windows scoring smoke PASS used a regenerated two-sample 006A local owner WAV
  evaluation report. `base` ranked highest in all three runtime-suitability
  profiles for this smoke only: balanced `base=92.24`, `tiny=86.72`,
  `small=79.03`; conversation `base=94.21`, `tiny=83.06`, `small=70.70`;
  manual_mic `base=91.37`, `tiny=89.18`, `small=85.57`. This is local
  runtime evidence, not true transcript accuracy/WER and not a final default
  recommendation. The committed default remains `tiny`; no runtime auto-switch
  is added.

- **TASK-STT-006C Christina Grounded STT Recommendation Explanation. DONE - WINDOWS GROUNDED EXPLANATION SMOKE PASS / CHRISTINA ZH-TW EXPLANATION READY (2026-06-12):**
  Adds `scripts/stt_model_recommendation_explanation.py` as the explanation
  stage after deterministic scoring. It reads a TASK-STT-006B scoring report and
  writes `outputs/stt_model_explanation/YYYYMMDD/` JSON containing source
  recommendation facts, model score summary, grounded explanation text, caveats,
  next action, forbidden-claim checks, and explicit `defaultChange.changed=false`
  / `runtimeAutoSwitch.changed=false`. Styles are `christina` and `plain`.
  The completed pipeline is now evaluation report -> deterministic scoring ->
  grounded Christina/plain explanation. Windows grounded explanation smoke PASS
  confirmed report generation, and Christina zh-TW localization PASS confirmed
  Traditional Chinese, proud/tsundere, helpful, caveated wording. The current
  implementation is deterministic/no-LLM by default; `--use-llm` is accepted
  only as a future-compatible flag and still falls back to grounded templates.
  This is not model auto-switching, not a frontend comparison panel, and not a
  default change. The explanation remains runtime-suitability-only evidence:
  there is no reference transcript, no true accuracy/WER claim, no default
  change, no runtime auto-switch, and no LLM used in the current implementation.

- **TASK-STT-007 STT Model Advisor Runner. IMPLEMENTED - AUTOMATED ADVISOR RUNNER SMOKE PASS / NEEDS WINDOWS END-TO-END RUNNER SMOKE (2026-06-12):**
  Adds `scripts/stt_model_advisor_runner.py` as the one-command local advisor
  CLI. It orchestrates evaluation -> deterministic scoring -> grounded
  Christina/plain explanation by importing and reusing the existing 006A, 006B,
  and 006C functions, then writes a final manifest under
  `outputs/stt_model_advisor/YYYYMMDD/`. The manifest records stage report
  basenames, deterministic recommendation facts, explanation text, and safety
  flags. This remains runtime-suitability evidence only: no reference
  transcript/no WER, no default change, no runtime auto-switch, no frontend
  comparison panel, and no LLM used by default. Runtime model selection remains
  manual through the TASK-STT-005 selector.

- TASK-STT-016 LLM-based semantic correction. **(PLANNED; future):** Optional
  follow-up to apply a local LLM pass over the corrected transcript for further semantic
  accuracy. Must be guarded by explicit user opt-in and must not replace the deterministic
  layer from TASK-247/248.

TASK-257 DONE - WINDOWS PET WINDOW CLICK/SHOW SMOKE PASS (2026-06-04): Pet Window Click / Show Pet Idempotent Behavior.

- **TASK-258 Owner Voice Gate Research. RESEARCH - OWNER VOICE GATE FEASIBILITY / NO RUNTIME CHANGE (2026-06-04):**
  Adds `docs/OWNER_VOICE_GATE_RESEARCH.md`. Evaluates local speaker verification / speaker
  embedding options for a future owner voice gate before STT. Recommended first probe:
  FunASR CAM++ / 3D-Speaker in `.venv-funasr` Python 3.10; fallbacks: sherpa-onnx speaker
  identification and SpeechBrain ECAPA-TDNN. Boundary: convenience filter only, not
  security-grade authentication; no runtime wiring, no mic access, no raw audio persistence,
  no `/stt/transcribe` or `/chat` change, no IPC, no Pet Window / Output Queue / Diagnostics
  Drawer change.

- **TASK-259 Owner Voice Gate Probe. DONE - WINDOWS OWNER VOICE PROBE SMOKE PASS (2026-06-04):**
  Adds `scripts/owner_voice_gate_probe.py`, an offline file-path-only speaker embedding probe
  for `.venv-funasr` Python 3.10. `--check-only` performs dependency checks and prints clean
  JSON; audio mode accepts existing mono 16 kHz PCM WAV files via `--enroll-a`, `--verify-a`,
  and optional `--verify-b`. Current check-only result: torch 2.12.0+cpu, funasr, modelscope,
  numpy, and soundfile are available; model is not loaded in check-only mode. Windows real-WAV
  probe PASS: FunASR CAM++ model `iic/speech_campplus_sv_zh-cn_16k-common` loaded locally in
  10.425 s, 192-dim embeddings extracted, ownerScore 0.9232 vs otherScore 0.052, and
  thresholdSuggestion 0.65 separates owner/non-owner clearly in this smoke. No runtime wiring,
  no mic access, no recording, no raw audio persistence, no embedding persistence, no IPC,
  and no `/stt/transcribe` or `/chat` change.

- **TASK-260 Owner Voice Gate Enrollment Storage Design. DESIGNED - OWNER VOICE ENROLLMENT STORAGE PLAN / NO RUNTIME CHANGE (2026-06-04):**
  Adds `docs/OWNER_VOICE_GATE_STORAGE_DESIGN.md`. Defines future explicit enrollment, local
  owner voice storage, centroid-only 192-d embedding aggregate, threshold
  calibration, reset/delete voiceprint UX, and diagnostics fields. Recommended first enrollment:
  3 samples of 8-15 seconds, normalize each embedding, average, normalize centroid, store centroid
  only. Forbidden storage: raw audio, base64 audio, full transcript, raw waveform, per-sample
  embeddings in v1, and unnecessary personal data. No runtime wiring, no mic access, no recording,
  no raw audio persistence, no formal voiceprint persistence, no IPC, and no `/stt/transcribe` or
  `/chat` change.

- **TASK-261 Owner Voice Gate UI / Storage Stub. DONE - WINDOWS OWNER VOICE STORAGE/UI SMOKE PASS (2026-06-04):**
  Adds backend-owned local storage stub `backend/data/owner_voice_gate_settings.json`, override
  `OWNER_VOICE_GATE_FILE_PATH`, and narrow endpoints `GET /owner-voice-gate/status`,
  `POST /owner-voice-gate/settings`, and `POST /owner-voice-gate/delete`. Adds a Full App
  settings UI for safety notice acceptance, enable/disable, threshold save, delete reset, and a
  disabled re-enroll placeholder. Stores only safe stub fields (`enabled`, `threshold`,
  `safetyNoticeAccepted`, metadata/null placeholders); rejects raw audio, base64 audio,
  transcript, waveform, per-sample embeddings, and real embedding values. No Manual Mic or
  Conversation Mode gate yet; no speaker verification runtime integration.

- **TASK-262 Owner Voice Gate Multi-Sample Calibration Probe. DONE - WINDOWS OWNER VOICE CALIBRATION SMOKE PASS (2026-06-04):**
  Extends `scripts/owner_voice_gate_probe.py` with multi-sample calibration support:
  `--owner-sample PATH` (repeatable), `--other-sample PATH` (repeatable), `--owner-dir DIR`,
  `--other-dir DIR`, `--output-json PATH`. Computes owner centroid (normalized mean of all owner
  embeddings), `ownerSelfScores` (centroid vs each owner sample), `otherScores` (centroid vs each
  other-speaker sample), `ownerStats` (mean/min/max/p10/p90), `otherStats` (mean/max/p90),
  `scoreGap` (ownerMin - otherMax), `balancedThreshold`, `conservativeThreshold`,
  `permissiveThreshold`, and `separationQuality`. Windows smoke PASS in repeated sample args mode
  and directory mode. Directory mode produced ownerSelfScores `[0.9806, 0.9806]`, otherScores
  `[0.0778]`, scoreGap `0.9028`, separationQuality `strong`, thresholdSuggestion/balancedThreshold
  `0.5292`, conservativeThreshold `0.8`, permissiveThreshold `0.4`. Because this used only
  2 owner samples and 1 other sample, keep `0.65` as the first future runtime balanced default;
  do not treat `0.5292` as universal. All thresholds clamped to [0.40, 0.95] and
  documented as local calibration hints only. No Manual Mic, Conversation Mode, STT, `/chat`,
  IPC, Pet Window, Output Queue, or Diagnostics Drawer change.

- **TASK-263 Owner Voice Enrollment File Import / Centroid Storage. DONE - Windows Unicode owner voice enrollment storage smoke PASS (2026-06-04):**
  Adds explicit file-path enrollment from existing owner WAV files. The new
  `.venv-funasr` sidecar `scripts/owner_voice_gate_enroll.py` validates 16 kHz
  mono PCM WAV input, loads FunASR CAM++, extracts embeddings in memory, and
  returns one 192-d centroid. Backend `POST /owner-voice-gate/enroll-files`
  accepts only `paths`, `threshold`, and `safetyNoticeAccepted`, rejects audio
  bytes/base64/transcript/waveform/embedding fields, and stores only the final
  centroid plus metadata in backend-owned Owner Voice Gate storage. The stored
  centroid is sensitive local voiceprint data. UI shows file-path enrollment
  controls and status only; it does not render the full vector. No Manual Mic,
  Conversation Mode, STT, `/chat`, IPC, mic, recording, raw audio persistence,
  per-sample embedding persistence, Pet Window, Output Queue, or Diagnostics
  Drawer change. Follow-up fix preserves Windows non-ASCII/Unicode path strings
  when backend invokes the `.venv-funasr` sidecar, prechecks existence with
  `Path.is_file()`, decodes sidecar JSON as UTF-8, and keeps missing-file errors
  as clean `audio_file_not_found` not-enrolled results. Backend Unicode API
  smoke PASS with `enrolled=true`, `sampleCount=2`, `embeddingDim=192`,
  `embeddingPersisted=true`, `status=disabled`, `reason=enrolled`, and
  `embeddingAggregate=null`.

- **TASK-264 Owner Voice Gate Verification Probe / Stored Centroid Scoring. DONE - Windows stored centroid verification smoke PASS (2026-06-04):**
  Adds `scripts/owner_voice_gate_verify.py`, a `.venv-funasr` script-only
  verification probe. It reads backend-owned Owner Voice Gate settings,
  confirms enrollment exists, validates existing 16 kHz mono PCM WAV candidate
  paths, loads FunASR CAM++, extracts candidate embeddings in memory, compares
  a normalized candidate centroid against the stored owner centroid with cosine
  similarity, and returns clean JSON fields such as `score`, `scores`,
  `threshold`, `accepted`, `embeddingDim`, and `sampleCount`. It does not expose
  `embeddingAggregate`, does not persist raw audio, transcripts, waveforms,
  base64 audio, or candidate embeddings, and does not add a backend verify
  endpoint. Manual Mic, Conversation Mode, STT, `/chat`, IPC, Pet Window,
  Output Queue, and Diagnostics Drawer runtime remain unchanged. Windows smoke
  PASS: owner2.wav scored `0.9806` and accepted at threshold `0.65`; other.wav
  scored `0.0778` and rejected.

- **TASK-265 Owner Voice Gate Backend Verification Endpoint / No Runtime Wiring. DONE - Windows backend verify-files smoke PASS (2026-06-04):**
  Adds `POST /owner-voice-gate/verify-files` backend endpoint. Request body:
  `{ "paths": [str, ...], "threshold": float (optional) }`. The endpoint
  validates fields (rejects rawAudio/base64Audio/transcript/embeddingAggregate),
  checks that the owner voice centroid is enrolled, validates that WAV paths
  exist before calling the sidecar, then invokes
  `run_owner_voice_verification_sidecar()` which calls
  `scripts/owner_voice_gate_verify.py` under `.venv-funasr` Python. Response
  includes `score`, `scores`, `threshold`, `accepted`, `embeddingDim`,
  `sampleCount`, `checkedAudioFiles`, and hardcoded
  `rawAudioPersisted=false`, `candidateEmbeddingPersisted=false`,
  `storedCentroidExposed=false`, `micAccessed=false`,
  `runtimeIntegrated=false`. The stored `embeddingAggregate` vector never
  appears in the response. No mic, no audio bytes from renderer, no IPC, no
  STT pipeline, no `/chat` wiring. 7 new pytest tests; smoke section
  `[14/14]` added to `stt_provider_smoke.py`.

- **TASK-SEC-001 Security Boundary / Anti Prompt Injection Design. DONE - DOCS-ONLY SECURITY BOUNDARY DESIGN (2026-06-04):**
  Adds `docs/SECURITY_BOUNDARY_DESIGN.md` before Owner Voice Gate runtime
  wiring. Defines sensitive data categories, data forbidden from LLM context,
  direct and indirect prompt injection risks, phishing/social engineering
  risks, untrusted-content handling, future tool permission tiers, output
  redaction checks, Owner Voice Gate security boundaries, and runtime
  integration preconditions. Owner Voice Gate remains a convenience filter, not
  authentication. Stored centroid and embeddings are sensitive biometric-like
  local data and must not enter LLM context, UI display, API responses, logs,
  diagnostics, Output Queue, Pet Bubble, or Pet runtime. Before Manual Mic or
  Conversation Mode runtime wiring, TASK-SEC-002 Sensitive Data Inventory /
  Redaction Rules, TASK-SEC-003 corpus, TASK-SEC-004 tool policy, and
  TASK-SEC-005 phishing/link safety design are now complete; next complete
  dry-run policy tasks. No runtime behavior changed.

- **TASK-266 Owner Voice Gate Manual Mic Dry-run Policy. DONE - DRY-RUN ONLY / NO HARD BLOCK (2026-06-04):**
  Adds status-only Manual Mic Owner Voice dry-run diagnostics in the existing
  Voice Diagnostics panel. Accept, reject, disabled, `not_computed`, and verify
  error states do not block Manual Mic STT, textarea fill, or auto-send. The
  dry-run reuses `/owner-voice-gate/verify-files` only when a safe candidate WAV
  path policy exists; otherwise it reports `no_candidate_file_policy`. No raw
  audio persistence, no hard gate, no `/stt/transcribe` or `/chat` schema
  change, no IPC, no Pet Window, and no Output Queue change.

- **TASK-267 Owner Voice Gate Conversation Mode Dry-run Policy. DONE - DRY-RUN ONLY / NO HARD BLOCK (2026-06-05):**
  Adds status-only Conversation Mode Owner Voice dry-run diagnostics with
  `ownerVoiceDryRunSource=conversation_mode` in the existing Voice Diagnostics
  panel. Accept, reject, disabled, `not_computed`, and verify error states do
  not block Conversation Mode STT or `/chat`. The dry-run reuses
  `/owner-voice-gate/verify-files` only when a safe candidate WAV path policy
  exists; otherwise it reports `no_candidate_file_policy`. TASK-266 Manual Mic
  dry-run remains intact. No raw audio persistence, no hard gate, no
  `/stt/transcribe` or `/chat` schema change, no IPC, no Pet Window, and no
  Output Queue change.

- **TASK-268 Owner Voice Dry-run Diagnostics / Safety Summary Polish. DONE - DIAGNOSTICS POLISH ONLY / NO HARD BLOCK (2026-06-05):**
  Polishes existing Voice Diagnostics wording for Owner Voice dry-run status.
  Manual Mic and Conversation Mode now display readable source labels, readable
  state/reason text, safe scalar verification fields, and the safety summary
  `Dry-run only; existing voice flow is not blocked` with
  `runtimeHardBlocked=false`. No backend verification behavior changed. No hard
  gate, no authentication claim, no `/stt/transcribe` or `/chat` schema change,
  no IPC, no Pet Window, and no Output Queue change.

Each future task must explicitly define safety boundaries, user controls,
provider scope, queue priority, and no-regression checks.

---

## 12. Relationship to Existing Docs

Related docs:

- `docs/INTERACTIVE_COMPANION_ARCHITECTURE.md`
- `docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md`
- `docs/CHRISTINA_PERSONA_CONTEXT_PACK.md`
- `docs/OWNER_VOICE_GATE_RESEARCH.md`
- `docs/OWNER_VOICE_GATE_STORAGE_DESIGN.md`

Relationship:

- Persona pack controls speech style guidance and TTS-safe script style.
- Output queue controls timing, priority, and interruption rules.
- Voice/TTS research controls provider candidates, licensing, and local-first
  roadmap.
- Owner voice gate research controls the future speaker-verification feasibility
  boundary and candidate comparison.
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
