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

Recommended follow-up: TASK-245 — Extract Context Menu / Search Modules.

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
