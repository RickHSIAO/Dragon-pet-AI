# Owner Voice Gate Storage Design

Status: TASK-260 DESIGNED - OWNER VOICE ENROLLMENT STORAGE PLAN / NO RUNTIME CHANGE

Date: 2026-06-04

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

Recommended future storage path:

```text
userData/owner-voice-gate.json
```

This file should be controlled by the main process or an existing narrow
settings/storage boundary. TASK-260 does not add that runtime.

Do not store it in:

- The repo.
- `backend/data`.
- Chat history.
- Memory tables.
- Diagnostics logs.
- Export/copy transcript output.
- Pet Window state files.

## 7. Storage Schema

Proposed JSON schema:

```json
{
  "schemaVersion": 1,
  "provider": "funasr-campp",
  "modelId": "iic/speech_campplus_sv_zh-cn_16k-common",
  "embeddingDim": 192,
  "embeddingAggregate": {
    "kind": "centroid",
    "vector": [0.0123]
  },
  "sampleCount": 3,
  "threshold": 0.65,
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

- Delete `userData/owner-voice-gate.json`.
- Clear in-memory owner embedding state.
- Turn `enabled` off.
- Do not delete chat history.
- Do not delete STT settings.
- Do not delete unrelated Pet Window state.
- Do not export voiceprint by default.

Clear Chat must not delete owner voiceprint.

App uninstall should follow normal userData behavior. If the app later adds an
"Erase all local data" action, it should include owner voiceprint deletion in
that broader action.

## 11. Future Runtime Architecture

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

- TASK-263: Manual Mic gate.
- TASK-264: Conversation Mode gate.

Both must be disabled by default until enrollment exists and the user explicitly
enables the gate.

## 12. Future Diagnostics Fields

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

## 13. Future Tasks

Recommended sequence:

- TASK-261 Owner Voice Enrollment UI / Local Storage Stub
- TASK-262 Owner Voice Gate Calibration Probe
- TASK-263 Owner Voice Gate Runtime Integration for Manual Mic
- TASK-264 Owner Voice Gate Runtime Integration for Conversation Mode

Do not jump directly from TASK-260 to runtime gating. Enrollment storage,
delete/reset UX, and threshold calibration should be settled first.

## 14. Validation Plan

Because TASK-260 is docs-only, validation is regression-oriented:

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

Expected runtime result: unchanged.
