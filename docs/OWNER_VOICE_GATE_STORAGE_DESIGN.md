# Owner Voice Gate Storage Design

Status: TASK-260 DESIGNED - OWNER VOICE ENROLLMENT STORAGE PLAN / NO RUNTIME CHANGE; TASK-261 DONE - WINDOWS OWNER VOICE STORAGE/UI SMOKE PASS; TASK-262 DONE - WINDOWS OWNER VOICE CALIBRATION SMOKE PASS; TASK-263 DONE - Windows Unicode owner voice enrollment storage smoke PASS; TASK-264 DONE - Windows stored centroid verification smoke PASS; TASK-265 DONE - Windows backend verify-files smoke PASS; TASK-266 DONE - Manual Mic dry-run only / no hard block; TASK-267 DONE - Conversation Mode dry-run only / no hard block

Date: 2026-06-05

## 1. Purpose

TASK-260 designs the future owner voice enrollment, local embedding storage,
reset/delete UX, threshold calibration, and diagnostics boundary for Dragon Pet
AI's owner voice gate.

This is a design checkpoint only. It does not add runtime code, storage files,
IPC, microphone access, enrollment UI, speaker verification execution, or
background listening.

The owner voice gate remains a convenience filter. It is not security-grade
authentication.

## 2. Inputs From TASK-259

TASK-259 proved that the local offline probe is feasible on this Windows machine:

| Field | Result |
|---|---|
| Provider | `funasr-campp` |
| Model | `iic/speech_campplus_sv_zh-cn_16k-common` |
| Python | `.venv-funasr` Python 3.10.11 |
| torch | 2.12.0+cpu |
| CUDA | false |
| Embedding dimension | 192 |
| ownerScore | 0.9232 |
| otherScore | 0.052 |
| thresholdSuggestion | 0.65 |
| rawAudioPersisted | false |
| embeddingPersisted | false |
| micAccessed | false |
| runtimeIntegrated | false |

The smoke test strongly separated owner vs non-owner speech, but it is still a
small sample. TASK-260 therefore designs calibration and storage before runtime
integration.

## 3. Safety Boundary

TASK-260 does not:

- No Manual Mic runtime change.
- No Conversation Mode runtime change.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No IPC channel.
- No microphone access.
- No recording.
- No raw audio persistence.
- No formal voiceprint persistence.
- No always listening.
- No background monitoring.
- No Pet Window runtime change.
- No Output Queue change.
- No Diagnostics Drawer runtime change.
- No commit or push.

Future implementation must keep enrollment explicit, visible, local-only, and
user-controlled.

## 4. Product Boundary

Owner Voice Gate is a local convenience filter:

- It may reduce accidental triggers from nearby people, TV audio, or background
  speech.
- It should not authorize purchases, secrets, destructive commands, account
  actions, or any high-risk operation.
- Replay recordings, voice changers, close impersonation, and AI voice clones
  may bypass it.
- Bad rooms, short speech, illness, or microphone changes may false-reject the
  real owner.

Recommended UI wording:

> Owner Voice Gate helps reduce accidental voice triggers. It is not identity
> proof and should not be used for security-sensitive actions.

## 5. Enrollment Flow

Future enrollment should be explicit:

```text
User opens Owner Voice Gate settings
-> clicks Enroll Owner Voice
-> accepts local-only / not-security warning
-> records 3 samples, each 8-15 seconds
-> app computes one embedding per sample
-> app normalizes embeddings
-> app creates one centroid embedding
-> app stores centroid + metadata only
-> app discards raw audio bytes
-> app shows enrollment quality summary
```

Recommended first version:

- Required samples: 3.
- Target sample length: 8-15 seconds each.
- Minimum accepted speech length: 5 seconds after VAD trimming.
- Recommended prompt style: natural phrases, not repeated single words.
- Enrollment should fail cleanly if any sample is too short, silent, or not
  processable.

Do not write raw enrollment audio to repo, userData, logs, temp folders, or
diagnostics. If any future implementation needs temporary audio bytes, use
memory first. If OS temp is absolutely required by a dependency, use a scoped
temp file and delete it immediately in a `finally` path.

## 6. Storage Location

TASK-260 originally considered Electron `userData`. TASK-261 resolves storage
ownership to the backend so the future speaker verification boundary can read
the settings without Electron-to-backend file sharing.

TASK-261 storage stub path:

```text
backend/data/owner_voice_gate_settings.json
```

The path can be overridden for tests through `OWNER_VOICE_GATE_FILE_PATH`.
An empty override disables persistence for isolated tests. The renderer must not
store owner voice gate settings or voiceprint data in `localStorage`.

Do not store it in:

- The repo.
- Electron renderer `localStorage`.
- Chat history.
- Memory tables.
- Diagnostics logs.
- Export/copy transcript output.
- Pet Window state files.

## 7. Storage Schema

TASK-261 storage stub schema:

```json
{
  "schemaVersion": 1,
  "enabled": false,
  "enrolled": false,
  "provider": "funasr-campp",
  "modelId": "iic/speech_campplus_sv_zh-cn_16k-common",
  "embeddingDim": 192,
  "embeddingAggregate": null,
  "sampleCount": 0,
  "threshold": 0.65,
  "calibrationStats": {
    "ownerScore": null,
    "otherScore": null,
    "meanSelfScore": null,
    "minSelfScore": null
  },
  "safetyNoticeAccepted": false,
  "createdAt": null,
  "updatedAt": null
}
```

Future enrolled schema after a later enrollment task:

```json
{
  "schemaVersion": 1,
  "enabled": true,
  "enrolled": true,
  "provider": "funasr-campp",
  "modelId": "iic/speech_campplus_sv_zh-cn_16k-common",
  "embeddingDim": 192,
  "embeddingAggregate": {
    "kind": "centroid",
    "vector": [0.0123]
  },
  "sampleCount": 3,
  "threshold": 0.65,
  "safetyNoticeAccepted": true,
  "createdAt": "2026-06-04T00:00:00.000Z",
  "updatedAt": "2026-06-04T00:00:00.000Z",
  "calibrationStats": {
    "meanSelfScore": 0.91,
    "minSelfScore": 0.84,
    "negativeSampleScore": 0.05,
    "recommendedThreshold": 0.65
  },
  "enabled": false,
  "safetyNoticeAccepted": true
}
```

Allowed stored values:

- `schemaVersion`
- `provider`
- `modelId`
- `embeddingDim`
- `embeddingAggregate.kind`
- `embeddingAggregate.vector`
- `sampleCount`
- `threshold`
- `createdAt`
- `updatedAt`
- `calibrationStats`
- `enabled`
- `safetyNoticeAccepted`

Forbidden stored values:

- Raw audio.
- Base64 audio.
- Full transcript.
- Complete per-sample raw waveform.
- Per-sample raw embedding vectors in the first version.
- Microphone device name unless explicitly needed and separately reviewed.
- Unnecessary personal data.

## 8. Embedding Aggregation

Recommended first strategy:

1. Extract one embedding per enrollment sample.
2. L2-normalize each embedding.
3. Average the normalized embeddings.
4. L2-normalize the average to create one centroid.
5. Store the centroid only.
6. Store quality metadata only:
   - `sampleCount`
   - `meanSelfScore`
   - `minSelfScore`
   - optional `negativeSampleScore`

Do not store per-sample embeddings in version 1. A future multi-centroid design
can be considered only if single-centroid false reject behavior is poor.

Rejected first-version strategies:

- Single sample only: too brittle.
- Raw per-sample embedding store: larger privacy surface.
- Median / robust clustering: premature for the first local gate.
- Multi-centroid storage: useful later, but harder to explain and delete cleanly.

## 9. Threshold Strategy

Initial threshold:

```text
0.65
```

Rationale:

- TASK-259 smoke produced ownerScore 0.9232 and otherScore 0.052.
- 0.65 sits well below the observed owner score and well above the observed
  other score.
- It should be treated as a first-pass default, not a universal truth.

Calibration recommendation:

- Compute owner self-score distribution from enrollment samples.
- If a negative sample exists, compute negative sample score.
- Recommended threshold:

```text
if negative sample exists:
  max(0.65, midpoint(minSelfScore, negativeSampleScore))
else:
  min(0.75, max(0.65, minSelfScore - 0.10))
```

False reject / false accept tradeoff:

- Higher threshold: fewer non-owner accepts, more owner rejects.
- Lower threshold: fewer owner rejects, more non-owner accepts.
- Default UX should prefer avoiding false accepts for auto-send Conversation
  Mode, while still keeping the feature clearly non-security.

Suggested future setting:

- Conservative: 0.72
- Balanced: 0.65
- Permissive: 0.58

## 10. Reset / Delete UX

Required future controls:

- Disable Owner Voice Gate.
- Delete owner voiceprint.
- Re-enroll owner voice.
- View local-only safety notice.
- View last calibration summary.

Deletion behavior:

- Delete/reset `backend/data/owner_voice_gate_settings.json`.
- Clear in-memory owner embedding state.
- Turn `enabled` off.
- Do not delete chat history.
- Do not delete STT settings.
- Do not delete unrelated Pet Window state.
- Do not export voiceprint by default.

Clear Chat must not delete owner voiceprint.

App uninstall should follow the app's normal local data cleanup behavior. If the
app later adds an "Erase all local data" action, it should include owner voice
gate storage deletion in that broader action.

## 11. TASK-261 UI / Storage Stub

TASK-261 implements the first non-runtime Owner Voice Gate surface:

- Backend-owned storage service: `backend/app/services/owner_voice_gate_storage.py`.
- Narrow backend endpoints:
  - `GET /owner-voice-gate/status`
  - `POST /owner-voice-gate/settings`
  - `POST /owner-voice-gate/delete`
- Full App settings UI section: `#owner-voice-gate-section`.
- Renderer calls only the three owner voice gate endpoints.
- `enabled=true` while `enrolled=false` returns a clean `not_enrolled` result
  and leaves `enabled=false`.
- `threshold` is clamped to `0.40..0.95`.
- `safetyNoticeAccepted` is persisted as a boolean.
- Delete resets the stub to defaults and removes the stub file if present.

TASK-261 still does not implement enrollment. It does not store a real
`embeddingAggregate`; the field remains `null`. It does not write raw audio,
base64 audio, transcript, waveform, or per-sample embeddings.

## 12. TASK-262 Calibration Probe

TASK-262 extends `scripts/owner_voice_gate_probe.py` with multi-sample
calibration support. It remains offline and file-path-only; it does not
open a microphone or persist raw audio or embeddings.

New CLI arguments:

- `--owner-sample PATH` (repeatable): owner WAV sample paths for calibration.
- `--other-sample PATH` (repeatable): other-speaker WAV sample paths.
- `--owner-dir DIR`: directory of owner WAV files (all `*.wav` in the directory).
- `--other-dir DIR`: directory of other-speaker WAV files.
- `--output-json PATH`: optional path to write calibration report JSON.

Calibration flow:

1. Collect all owner samples and compute one embedding per sample.
2. Compute owner centroid: normalized mean of all owner embeddings.
3. Compute `ownerSelfScores`: cosine(centroid, each owner embedding).
4. Compute `otherScores`: cosine(centroid, each other-speaker embedding).
5. Compute `ownerStats` (mean, min, max, p10, p90) and `otherStats` (mean, max, p90).
6. Compute threshold suggestions:
   - If other samples exist: midpoint-based calibration using ownerMin and otherMax.
   - If owner-only: conservative fallback from ownerMin (85/90/95 percentiles).
   - All thresholds clamped to `[0.40, 0.95]`.
7. Compute `scoreGap` (ownerMin - otherMax) and `separationQuality`.
8. Output clean JSON to stdout; optionally write to `--output-json` path.

Output fields (TASK-262 additions):

```json
{
  "ownerSampleCount": 3,
  "otherSampleCount": 2,
  "ownerSelfScores": [0.98, 0.97, 0.96],
  "otherScores": [0.05, 0.12],
  "ownerStats": {"mean": 0.97, "min": 0.96, "max": 0.98, "p10": 0.962, "p90": 0.978},
  "otherStats": {"mean": 0.085, "max": 0.12, "p90": 0.116},
  "scoreGap": 0.84,
  "thresholdSuggestion": 0.54,
  "balancedThreshold": 0.54,
  "conservativeThreshold": 0.79,
  "permissiveThreshold": 0.29,
  "separationQuality": "strong",
  "rawAudioPersisted": false,
  "embeddingPersisted": false,
  "micAccessed": false,
  "runtimeIntegrated": false
}
```

Threshold strategy:

- Do not treat any suggested threshold as a universal truth.
- `balancedThreshold`: midpoint of ownerMin and otherMax.
- `conservativeThreshold`: 60% of the way from midpoint toward ownerMin.
- `permissiveThreshold`: 60% of the way from midpoint toward otherMax.
- `separationQuality`: `strong` (gap ≥ 0.35), `moderate` (gap ≥ 0.15), `weak` (gap < 0.15), `overlap` (gap ≤ 0).
- If `overlap`: status still `ok`, but `separationQuality=overlap` is a warning that the
  current samples do not reliably separate owner from other speakers.
- All thresholds clamped to `[THRESHOLD_MIN=0.40, THRESHOLD_MAX=0.95]`.

Safety boundary (unchanged from TASK-259/261):

- No Manual Mic runtime change.
- No Conversation Mode runtime change.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No new IPC channel.
- No microphone access.
- No `getUserMedia`.
- No recording.
- No raw audio persistence.
- No embedding persistence to production storage.
- No always listening.
- No background monitoring.
- No Pet Window, Output Queue, or Diagnostics Drawer change.

Runtime remains unchanged:

- No Manual Mic gate.
- No Conversation Mode gate.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No IPC channel.
- No microphone access.
- No recording.
- No always listening.
- No background monitoring.
- No Pet Window, Output Queue, or Diagnostics Drawer runtime changes.

Windows calibration smoke PASS (TASK-262 closeout):

- Repeated sample args mode PASS with two owner WAVs, one other-speaker WAV,
  and `--output-json`.
- Directory mode PASS with owner/other directories and `--output-json`.
- Directory mode result: status `ok`, reason `calibration_probe_complete`,
  modelLoaded=true, modelLoadSeconds `9.391`, embeddingDim `192`.
- ownerSampleCount `2`, otherSampleCount `1`.
- ownerSelfScores `[0.9806, 0.9806]`.
- otherScores `[0.0778]`.
- ownerStats mean/min/max/p10/p90 `0.9806`.
- otherStats mean/max/p90 `0.0778`.
- scoreGap `0.9028`; separationQuality `strong`.
- thresholdSuggestion / balancedThreshold `0.5292`.
- conservativeThreshold `0.8`.
- permissiveThreshold `0.4`.
- rawAudioPersisted=false, embeddingPersisted=false, micAccessed=false,
  runtimeIntegrated=false.

Threshold storage recommendation after TASK-262:

- Keep stored default threshold at `0.65` for the first runtime gate.
- Treat `0.5292` as a local calibration result from a small sample set, not as
  a universal production default.
- Expose `0.8` as conservative mode if runtime UX offers presets.
- Reserve `0.4` / permissiveThreshold for debug or explicit permissive
  experiments, not the first runtime default.

## 13. TASK-263 File Enrollment / Centroid Storage

TASK-263 implements enrollment from existing owner WAV files. It is the first
task that writes a real owner voiceprint, but it still does not connect that
voiceprint to Manual Mic or Conversation Mode runtime gating.

Implemented path:

```text
Full App Owner Voice Gate settings
-> user pastes existing owner WAV file paths
-> POST /owner-voice-gate/enroll-files
-> backend invokes .venv-funasr scripts/owner_voice_gate_enroll.py
-> sidecar validates 16 kHz mono PCM WAV files
-> sidecar extracts CAM++ embeddings in memory
-> L2 normalize each sample embedding
-> average embeddings
-> L2 normalize centroid
-> backend writes owner_voice_gate_settings.json
```

Storage write after successful enrollment:

- `enrolled=true`
- `enabled=false`
- `provider=funasr-campp`
- `modelId=iic/speech_campplus_sv_zh-cn_16k-common`
- `embeddingDim=192`
- `embeddingAggregate=<192 float centroid>`
- `sampleCount=N`
- `threshold=<clamped 0.40..0.95>`
- `calibrationStats.meanSelfScore/minSelfScore/maxSelfScore`
- `safetyNoticeAccepted=true`
- `createdAt` / `updatedAt`

Sensitive data boundary:

- `embeddingAggregate` is a sensitive local voiceprint.
- It is stored only in backend-owned Owner Voice Gate storage.
- It is not written to chat history, STT state, Pet state, renderer
  `localStorage`, exports, or diagnostics drawers.
- API status/settings responses mask the centroid by default.
- UI shows only enrollment state, sample count, threshold, provider/model,
  embedding dimension, and aggregate score summary.

Forbidden persistence remains:

- No raw audio.
- No base64 audio.
- No transcripts.
- No waveforms.
- No per-sample embeddings.
- No formal runtime gate decision history.

Delete/reset behavior:

- `POST /owner-voice-gate/delete` deletes the owner voice storage file or resets
  it to defaults.
- Delete clears `embeddingAggregate`, `enrolled`, `sampleCount`, `enabled`, and
  calibration stats.
- Delete does not touch chat history, STT state, Pet state, provider settings,
  or app memory.

Runtime remains unchanged:

- No Manual Mic gate.
- No Conversation Mode gate.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No new IPC channel.
- No microphone access, recording, always listening, or background monitoring.
- No Pet Window, Output Queue, or Diagnostics Drawer change.

TASK-263 Windows Unicode path follow-up:

- Windows smoke found that direct `.venv-funasr` sidecar enrollment could load
  samples from a non-ASCII user temp path, and backend `Path.exists()` could see
  the same files, but `POST /owner-voice-gate/enroll-files` returned
  `audio_file_not_found` for the Unicode path.
- Root cause: backend enrollment path preparation eagerly canonicalized paths
  with `Path(...).resolve()` before invoking the sidecar. That extra path
  rewrite was unnecessary for file import enrollment and brittle for Windows
  non-ASCII user profile paths.
- Fix: backend now trims and `expanduser()`s each path, validates existence
  with `Path.is_file()`, preserves the caller-provided Unicode spelling for the
  `.venv-funasr` sidecar argv, and decodes sidecar JSON stdout as UTF-8.
- Missing files still return a clean `audio_file_not_found` not-enrolled result
  without stack traces or raw paths.
- ASCII enrollment paths remain supported.
- Windows Unicode backend API smoke PASS with two owner WAVs under
  `C:\Users\雪狼丸\AppData\Local\Temp`: `enrolled=true`, `sampleCount=2`,
  `embeddingDim=192`, `embeddingPersisted=true`, `status=disabled`,
  `reason=enrolled`, `safetyNoticeAccepted=true`, and `embeddingAggregate=null`
  in the API response.
- No raw audio, base64 audio, transcript, waveform, per-sample embedding, mic,
  recording, STT, chat, IPC, Pet Window, Output Queue, or Diagnostics Drawer
  behavior changed.

## 14. TASK-264 Stored Centroid Verification Probe

TASK-264 adds a script-only verification probe for the stored centroid. It is
the first consumer of the persisted owner voice centroid, but it does not wire
the gate into Manual Mic, Conversation Mode, STT, chat, IPC, or Pet runtime.

Implemented path:

```text
Existing candidate WAV path(s)
  -> scripts/owner_voice_gate_verify.py
  -> read backend/data/owner_voice_gate_settings.json
  -> validate enrollment and stored 192-d centroid
  -> validate candidate WAV metadata
  -> FunASR CAM++ embedding in .venv-funasr
  -> L2 normalize candidate embedding(s)
  -> aggregate candidate centroid if multiple samples
  -> cosine similarity against stored centroid
  -> JSON score / threshold / accepted
```

Report shape:

- `status`
- `reason`
- `enrolled`
- `score`
- `scores`
- `threshold`
- `accepted`
- `embeddingDim`
- `sampleCount`
- `checkedAudioFiles`
- safety booleans for raw audio, transcript, waveform, base64 audio,
  candidate embedding persistence, stored centroid exposure, mic access, and
  runtime integration.

The probe must not persist raw candidate audio, candidate transcript,
candidate waveform, base64 audio, candidate per-sample embeddings, or candidate
aggregate embeddings. The probe must not expose `embeddingAggregate`, full
stored centroid values, or full candidate embedding vectors.

TASK-264 uses a script rather than a backend endpoint so the first verification
step stays outside runtime request paths. A future runtime task can reuse the
same scoring rules after threshold behavior and UX are explicitly accepted.

Windows stored-centroid smoke PASS:

- Owner candidate `owner2.wav`: `score=0.9806`, `threshold=0.65`,
  `accepted=true`.
- Other candidate `other.wav`: `score=0.0778`, `threshold=0.65`,
  `accepted=false`.
- `embeddingDim=192`, `sampleCount=1`, model
  `iic/speech_campplus_sv_zh-cn_16k-common`.
- `rawAudioPersisted=false`, `candidateEmbeddingPersisted=false`,
  `storedCentroidExposed=false`, `micAccessed=false`, and
  `runtimeIntegrated=false`.

## 15. Future Runtime Architecture

This is for future tasks only:

```text
Manual Mic / Conversation Mode WAV
-> speaker verification before STT
-> pass:
     STT -> correctedTranscript -> /chat
-> fail:
     discard audio bytes
     no STT
     no transcript
     no chat history
```

Runtime integration should be split by surface:

- TASK-265: Backend verification endpoint (DONE — see Section 19).
- TASK-SEC-001: Security boundary / anti prompt injection design (DONE).
- TASK-SEC-002: Sensitive data inventory / redaction rules (DONE).
- TASK-SEC-003: Prompt injection test corpus (DONE).
- TASK-SEC-004: Tool permission / user confirmation policy (DONE).
- TASK-SEC-005: Phishing / link safety warning layer design (DONE).
- TASK-266: Manual Mic dry-run policy (DONE).
- TASK-267: Conversation Mode dry-run policy (DONE).

Both must be disabled by default until enrollment exists and the user explicitly
enables the gate.

## 16. Future Diagnostics Fields

Suggested future diagnostics fields:

- `ownerVoiceGateEnabled`
- `ownerVoiceGateStatus`
- `ownerVoiceScore`
- `ownerVoiceThreshold`
- `ownerVoiceDecision`
- `ownerVoiceReason`
- `ownerVoiceModel`
- `ownerVoiceEmbeddingDim`
- `ownerVoiceLastCheckedAt`

Diagnostics must not show:

- Raw audio.
- Base64 audio.
- Full embedding vectors.
- Full transcript for rejected speech.
- Hidden prompt or private storage path details.

## 17. Future Tasks

Recommended sequence:

- TASK-265 Backend Verification Endpoint (DONE — Section 19)
- TASK-SEC-001 Security Boundary / Anti Prompt Injection Design (DONE)
- TASK-SEC-002 Sensitive Data Inventory / Redaction Rules (DONE)
- TASK-SEC-003 Prompt Injection Test Corpus (DONE)
- TASK-SEC-004 Tool Permission / User Confirmation Policy (DONE)
- TASK-SEC-005 Phishing / Link Safety Warning Layer Design (DONE)
- TASK-266 Owner Voice Gate Manual Mic Dry-run Policy (DONE)
- TASK-267 Owner Voice Gate Conversation Mode Dry-run Policy (DONE)

TASK-262 calibration is complete on Windows for the small smoke set. Runtime
gating should still remain explicit, opt-in, and threshold-aware.

## 18. Validation Plan

Because TASK-261 adds a UI/storage stub only, validation is regression-oriented:

```powershell
node apps\desktop\scripts\renderer-chat-smoke.js
node apps\desktop\scripts\pet-window-smoke.js
node apps\desktop\scripts\pet-renderer-smoke.js
backend.venv\Scripts\python.exe -m pytest backend\tests\test_stt_routes.py -v -p no:cacheprovider
backend.venv\Scripts\python.exe scripts\stt_provider_smoke.py
git diff --check
git status --short
git diff --stat
git diff --name-only
```

## 19. TASK-265 Backend Verification Endpoint

TASK-265 adds `POST /owner-voice-gate/verify-files` to the backend API.

### New storage service additions

- `OWNER_VOICE_VERIFICATION_TIMEOUT_SECONDS = 600` constant.
- `_OWNER_VOICE_VERIFY_SCRIPT` path constant pointing to
  `scripts/owner_voice_gate_verify.py`.
- `run_owner_voice_verification_sidecar(paths, threshold, settings_path)`:
  calls the verify script under `.venv-funasr` Python, parses the last JSON
  object from stdout (same `_last_json_object` helper used by enrollment).
- `OwnerVoiceGateStorageService.verify_from_files(paths, threshold)`:
  returns `not_enrolled` immediately if no centroid. Validates paths via
  `_prepare_owner_voice_enrollment_paths`. Extracts only safe fields from the
  sidecar report — `embeddingAggregate` never appears in output. Hardcodes
  `rawAudioPersisted=False`, `candidateEmbeddingPersisted=False`,
  `storedCentroidExposed=False`, `micAccessed=False`,
  `runtimeIntegrated=False`.
- `validate_owner_voice_gate_verify_fields(body)`: allows only `paths` and
  `threshold`; rejects all `_FORBIDDEN_STORAGE_FIELDS`.
- `verify_owner_voice_gate_from_files(paths, threshold)`: public module-level
  function delegating to `_service.verify_from_files()`.

### Endpoint contract

```
POST /owner-voice-gate/verify-files
Request:  { "paths": [str, ...], "threshold": float (optional) }
Response: { "status", "reason", "enrolled", "score", "scores",
            "threshold", "accepted", "embeddingDim", "sampleCount",
            "checkedAudioFiles", "rawAudioPersisted", "candidateEmbeddingPersisted",
            "storedCentroidExposed", "micAccessed", "runtimeIntegrated", "message" }
```

### Safety invariants

- `embeddingAggregate` never in the response body.
- No raw audio persistence across the entire request path.
- No candidate embedding persistence.
- No `getUserMedia` / `MediaRecorder` in any code path.
- No IPC channel, no `/chat`, no STT pipeline calls.

### Windows backend endpoint smoke

PASS on 2026-06-04:

- Owner WAV `%TEMP%\dragon-pet-voice-probe\owner2.wav`: `status=ok`,
  `reason=verification_complete`, `score=0.9806`, `threshold=0.65`,
  `accepted=true`, `embeddingDim=192`.
- Other WAV `%TEMP%\dragon-pet-voice-probe\other.wav`: `status=ok`,
  `reason=verification_complete`, `score=0.0778`, `threshold=0.65`,
  `accepted=false`, `embeddingDim=192`.
- Both responses kept `rawAudioPersisted=false`,
  `candidateEmbeddingPersisted=false`, `storedCentroidExposed=false`,
  `micAccessed=false`, and `runtimeIntegrated=false`, with no stored centroid
  or candidate embedding in the response.

Expected runtime result: unchanged.

Before any Manual Mic or Conversation Mode runtime wiring, TASK-SEC-002 has
inventoried sensitive fields and defined redaction rules. See
`docs/SENSITIVE_DATA_REDACTION_RULES.md`. Rejected speech must not enter
`/chat`, LLM context, diagnostics, Output Queue, Pet Bubble, or Pet runtime.
The stored centroid remains sensitive biometric-like local data and is
forbidden from LLM context, UI display, API responses, logs, and diagnostics.

## 20. TASK-266 Manual Mic Dry-run Policy

TASK-266 adds Manual Mic dry-run status only. It does not turn Owner Voice Gate
into a hard runtime gate.

### Runtime behavior

- Manual Mic STT continues when dry-run is disabled, accepted, rejected,
  not computed, or errored.
- Existing textarea fill and auto-send behavior remains unchanged.
- No Conversation Mode dry-run or gate is wired in this task.
- No `/stt/transcribe` schema or backend behavior changes.
- No `/chat` schema change; `/chat` remains `reply / mood / source`.
- No IPC, Pet Window, Output Queue, or Diagnostics Drawer dispatch change.

### Candidate audio policy

TASK-266 intentionally does not write Manual Mic audio to disk just to satisfy
`/owner-voice-gate/verify-files`. The current Manual Mic audio remains
in-memory. Dry-run verification may call `verify-files` only if a future
explicit temp-file policy supplies a safe candidate WAV path.

When no safe candidate path exists, Manual Mic diagnostics report:

- `ownerVoiceDryRunEnabled=true` when the gate is enrolled and enabled.
- `ownerVoiceDryRunStatus=not_computed`.
- `ownerVoiceDryRunReason=no_candidate_file_policy`.
- `rawAudioPersisted=false`.
- `candidateEmbeddingPersisted=false`.
- `storedCentroidExposed=false`.
- `runtimeHardBlocked=false`.

### Safe status fields

The existing Voice Diagnostics panel may show only:

- dry-run enabled state
- status/reason
- score/threshold
- accepted/rejected/unknown
- checked timestamp
- safety booleans

It must not show centroid vectors, `embeddingAggregate`, candidate embeddings,
raw audio, raw candidate paths, or rejected transcript as part of Owner Voice
dry-run status.

### Security statement

Owner Voice Gate remains a local convenience filter for reducing accidental
voice triggers. It is not authentication, identity proof, authorization, or a
security boundary.

## 21. TASK-267 Conversation Mode Dry-run Policy

TASK-267 adds Conversation Mode dry-run status only. It does not turn Owner
Voice Gate into a hard runtime gate.

### Runtime behavior

- Conversation Mode STT and `/chat` continue when dry-run is disabled,
  accepted, rejected, not computed, or errored.
- TASK-266 Manual Mic dry-run remains unchanged and uses
  `ownerVoiceDryRunSource=manual_mic`.
- TASK-267 Conversation Mode dry-run uses
  `ownerVoiceDryRunSource=conversation_mode`.
- No `/stt/transcribe` schema or backend behavior changes.
- No `/chat` schema change; `/chat` remains `reply / mood / source`.
- No IPC, Pet Window, Output Queue, or Diagnostics Drawer dispatch change.

### Candidate audio policy

TASK-267 intentionally does not write Conversation Mode audio to disk just to
satisfy `/owner-voice-gate/verify-files`. The current Conversation Mode audio
remains in-memory. Dry-run verification may call `verify-files` only if a
future explicit temp-file policy supplies a safe candidate WAV path.

When no safe candidate path exists, Conversation Mode diagnostics report:

- `ownerVoiceDryRunEnabled=true` when the gate is enrolled and enabled.
- `ownerVoiceDryRunSource=conversation_mode`.
- `ownerVoiceDryRunStatus=not_computed`.
- `ownerVoiceDryRunReason=no_candidate_file_policy`.
- `rawAudioPersisted=false`.
- `candidateEmbeddingPersisted=false`.
- `storedCentroidExposed=false`.
- `runtimeHardBlocked=false`.

### Safe status fields

The existing Voice Diagnostics panel may show only:

- dry-run source
- dry-run enabled state
- status/reason
- score/threshold
- accepted/rejected/unknown
- checked timestamp
- safety booleans

It must not show centroid vectors, `embeddingAggregate`, candidate embeddings,
raw audio, raw candidate paths, raw transcript, or rejected transcript as part
of Owner Voice dry-run status.

### Security statement

Owner Voice Gate remains a local convenience filter for reducing accidental
voice triggers. It is not authentication, identity proof, authorization, or a
security boundary. Reject, error, disabled, and `not_computed` results are
diagnostic-only and never hard-block Conversation Mode.
