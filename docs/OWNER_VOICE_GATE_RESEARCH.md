# Owner Voice Gate Research

Status: TASK-258 RESEARCH - OWNER VOICE GATE FEASIBILITY / NO RUNTIME CHANGE; TASK-259 DONE - WINDOWS OWNER VOICE PROBE SMOKE PASS; TASK-260 DESIGNED - OWNER VOICE ENROLLMENT STORAGE PLAN / NO RUNTIME CHANGE; TASK-261 DONE - WINDOWS OWNER VOICE STORAGE/UI SMOKE PASS; TASK-262 DONE - WINDOWS OWNER VOICE CALIBRATION SMOKE PASS; TASK-263 DONE - Windows Unicode owner voice enrollment storage smoke PASS; TASK-264 DONE - Windows stored centroid verification smoke PASS

Date: 2026-06-04

## 1. Problem statement

Dragon Pet AI now has a local Full App voice path:

```text
Full App Mic -> 16 kHz PCM WAV -> backend /stt/transcribe
-> funasr-local sidecar -> Paraformer-zh STT -> OpenCC s2tw
-> proper noun correction -> correctedTranscript -> /chat
```

The next feasibility question is whether future Manual Mic and Conversation Mode
can optionally accept only the owner's voice before STT. The goal is a
convenience filter:

- Reduce accidental triggers from nearby people, TV audio, or room background.
- Avoid spending STT and `/chat` work on obvious non-owner speech.
- Keep failed voice-gate attempts out of STT, `/chat`, and history.

This task is research only. It does not add enrollment, speaker verification,
runtime hooks, microphone access, IPC, storage, or background listening.

## 2. Safety boundary

TASK-258 makes no runtime change.

- No Manual Mic runtime change.
- No Conversation Mode runtime change.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No always listening.
- No background monitoring.
- No microphone access.
- No recording.
- No raw audio persistence.
- No voiceprint stored in formal app storage.
- No new IPC channel.
- No Pet Window, Output Queue, or Diagnostics Drawer change.

Future owner-voice work should preserve the existing explicit user-action model:
only audio already captured by Manual Mic or an explicitly started Conversation
Mode session may be checked.

## 3. Threat model and limitation

Owner voice gate is not security-grade authentication.

It can help reject unrelated speakers and background speech, but it must not be
trusted for account access, purchases, destructive operations, secrets, or
high-risk commands. Replay recordings, voice changers, close impersonation, and
AI voice clones may pass a similarity threshold. Noisy rooms and short utterances
can also cause false rejects for the real owner or false accepts for similar
voices.

Recommended product wording:

> Owner Voice Gate is a local convenience filter. It is not identity proof.

## 4. Proposed future architecture

Recommended future flow:

```text
Enrollment:
  explicit user action
  -> capture several short owner samples
  -> local speaker embedding model
  -> average / normalize owner embedding
  -> save only embedding + metadata
  -> discard raw audio

Manual Mic / Conversation Mode:
  explicit user action
  -> existing 16 kHz PCM WAV capture
  -> speaker verification before STT
  -> pass:
       STT -> normalized/corrected transcript -> existing send flow -> /chat
  -> fail:
       discard audio bytes in memory
       no STT
       no /chat
       no history
       no transcript preview
```

Implementation notes for future tasks:

- Put embedding work in the `.venv-funasr` Python 3.10 sidecar first, not
  `backend.venv` Python 3.14, because PyTorch and torchaudio are already known
  to work there.
- Keep the first probe offline and file-based with synthetic or user-supplied
  WAV paths; do not open the microphone from a probe script.
- Store enrollment output only after a separate UX task defines reset/delete,
  consent wording, and storage format.
- Use cosine similarity against one or more L2-normalized embeddings.
- Gate only speech-like segments with a minimum duration, for example 1.0-2.0 s.

## 5. Candidate comparison

| Candidate | Windows install difficulty | Python fit | Torch / torchaudio / ffmpeg | CPU speed expectation | 16 kHz WAV PCM | Offline/local | Embedding-only storage | License / model size / dependency risk | Fit |
|---|---:|---|---|---|---|---|---|---|---|
| SpeechBrain ECAPA-TDNN (`speechbrain/spkrec-ecapa-voxceleb`) | Medium | Package supports Python >=3.8.1; better in `.venv-funasr` than Python 3.14 | PyTorch stack; torchaudio may be involved by recipes | Good enough for short utterance probe on CPU; model is not tiny | Yes, standard speaker-verification use case | Yes after model download | Yes, save embedding vector only | Apache-2.0 package/model; Hugging Face model uses pickle weights, so pin and cache deliberately | Strong first Python baseline |
| Resemblyzer | Low to medium | Python 3.5+ per upstream README, but old dependency stack may not love Python 3.14; likely better in Python 3.10 | PyTorch, librosa, scipy, webrtcvad | Usually lightweight for short clips | Yes after loading/resampling | Yes after package/model install | Yes, 256-d voice embedding | Apache-2.0; older maintenance/dependency risk | Good fallback/prototype |
| sherpa-onnx speaker identification | Low to medium | PyPI supports Python >=3.7; likely compatible with Python 3.10 and possibly 3.14 | ONNX Runtime style; no PyTorch runtime required | Promising CPU path | Yes, model examples target WAV speaker identification | Yes after model download | Yes, embedding/registered speaker data possible | Apache-style project; model availability/release workflow needs probe | Best low-dependency fallback |
| WeSpeaker / `wespeakerruntime` | Medium | Runtime binding says Python >=3.6; full toolkit recommends Python 3.9 and PyTorch >=2.0 | Runtime offers ONNX models; full toolkit uses torch/torchaudio/sox | Good in runtime path | Yes, extracts embedding from WAV | Yes after model download | Yes | Apache; package is old, full toolkit deps heavier | Viable fallback if runtime works on Windows |
| FunASR CAM++ / 3D-Speaker | Medium to high | FunASR requires Python >=3.8 and PyTorch/torchaudio; already available in `.venv-funasr`; 3D-Speaker docs use Python 3.8 | PyTorch + torchaudio; FunASR already present | CAM++ is small (~7.2M params in FunASR model zoo), likely good on CPU | Yes; speech models are 16 kHz oriented | Yes after model download/cache | Yes, 192-d style embedding expected for CAM++ | FunASR MIT; model license/modelscope availability must be verified before shipping | Most aligned with current stack, good first Dragon-specific candidate |
| pyannote.audio | High | Latest PyPI requires Python >=3.10 | PyTorch, torchcodec, ffmpeg; HF token/user conditions for open pipeline | Strong but heavier; CPU can be slow for diarization pipelines | Yes | Community pipeline runs locally after model access; premium runs cloud | Yes for embedding models, but full pipeline is overkill | Open-source toolkit, but model access/token/telemetry settings add product friction | Not first choice |
| NVIDIA NeMo speaker verification / TitaNet | High | PyPI requires Python >=3.10; heavy framework | PyTorch Lightning / NeMo stack; NVIDIA ecosystem | Good models but heavy; often GPU-oriented | Yes | Yes after model download | Yes | Apache-2.0, but dependency and install surface too broad for this app | Not recommended for v0 |

Sources checked:

- SpeechBrain PyPI and ECAPA model card: https://pypi.org/project/speechbrain/ and https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb
- Resemblyzer README: https://github.com/resemble-ai/Resemblyzer
- sherpa-onnx speaker identification: https://k2-fsa.github.io/sherpa/onnx/speaker-identification/index.html
- WeSpeaker README and runtime package: https://github.com/wenet-e2e/wespeaker and https://pypi.org/project/wespeakerruntime/
- FunASR README / model zoo and 3D-Speaker README: https://github.com/modelscope/FunASR and https://github.com/modelscope/3D-Speaker
- pyannote.audio PyPI / Hugging Face: https://pypi.org/project/pyannote-audio/ and https://huggingface.co/pyannote
- NVIDIA NeMo diarization docs and PyPI: https://docs.nvidia.com/nemo-framework/user-guide/24.12/nemotoolkit/asr/speaker_diarization/intro.html and https://pypi.org/project/nemo-toolkit/

## 6. Recommendation

First candidate for Dragon Pet AI:

1. FunASR CAM++ / 3D-Speaker in `.venv-funasr`.

Reasons:

- It aligns with the already successful `.venv-funasr` Python 3.10 sidecar.
- Torch CPU is already present there.
- It avoids adding another runtime family before proving the concept.
- CAM++ is listed in FunASR's model zoo as a small speaker diarization model.
- It is more likely to behave well with Chinese speech than VoxCeleb-only
  English-first baselines.

Practical caveat: use it as a probe first. Verify model download/cache behavior,
Windows import stability, exact embedding extraction API, model license terms,
and threshold behavior before any runtime design.

Fallback candidates:

1. sherpa-onnx speaker identification.
   This is the cleanest fallback if PyTorch-side speaker embedding becomes too
   heavy or fragile. It has a dedicated speaker-identification docs page and
   pretrained model releases, and it reduces the torch/torchaudio risk.

2. SpeechBrain ECAPA-TDNN.
   This is the best-known Python baseline for speaker verification and is useful
   for sanity-checking similarity scores. It is less ideal as the Dragon default
   because it adds another PyTorch package family and the common model is
   English/VoxCeleb-oriented.

Not recommended for the first implementation:

- pyannote.audio: excellent diarization toolkit, but too heavy for a simple
  owner gate. It also needs ffmpeg/torchcodec and Hugging Face access-token/user
  conditions for the main community pipeline.
- NVIDIA NeMo: too broad and heavy for this desktop convenience filter.
- Full 3D-Speaker training recipes: good research project, but Python 3.8/conda
  recipe and repo clone workflow are not a narrow app dependency.

## 7. Suggested future tasks

- TASK-259 Owner Voice Gate Probe / Offline Embedding Test
  - Add `scripts/owner_voice_gate_probe.py`.
  - Accept file paths only; no microphone access.
  - Run in `.venv-funasr`.
  - Produce embeddings in memory and compare cosine similarity.
  - Do not save raw audio.
  - Do not save embeddings into formal storage.

- TASK-260 Owner Voice Gate Enrollment Storage Design / Threshold Multi-Sample Probe
  - Completed in `docs/OWNER_VOICE_GATE_STORAGE_DESIGN.md`.
  - Defines enrollment sample count.
  - Defines local embedding storage format.
  - Defines reset/delete voiceprint UX.
  - Defines threshold tuning and false accept / false reject diagnostics.
  - Keeps no raw audio persistence and convenience-filter-only wording.

- TASK-261 Owner Voice Gate for Manual Mic / Conversation Mode
  - Add disabled-by-default session setting.
  - Gate before `/stt/transcribe` work.
  - Pass -> existing STT -> correctedTranscript -> existing send flow.
  - Fail -> discard, no STT, no `/chat`, no history.
  - Add smoke tests proving no always-listening, no new IPC, no raw audio
    persistence, and no schema change.

## 8. Open questions

- What enrollment duration is enough for this user and room? Start with 3-5
  samples of 3-5 seconds each.
- What similarity threshold balances false rejects and false accepts?
- Should threshold be per-device/per-room tuned?
- How does it behave with TV speech behind the owner's speech?
- How does it behave with overlapping speakers?
- Should Conversation Mode require a longer owner-confirmed speech segment than
  Manual Mic?
- How should "failed owner gate" be surfaced without leaking transcript-like
  content?
- Where should embedding storage live, and how is it reset/deleted?
- Should multiple owner embeddings be supported for different microphones or
  room acoustics?
- How should the app communicate replay/voice-clone limitations?

## 9. Validation plan for TASK-258

Because this task is docs-only research, validation is regression-oriented:

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

Expected runtime result: no changed runtime files and no voice behavior change.

## 10. TASK-259 probe implementation

Status: DONE - WINDOWS OWNER VOICE PROBE SMOKE PASS

TASK-259 adds `scripts/owner_voice_gate_probe.py` as an offline, file-path-only
speaker embedding probe. It is not connected to Manual Mic, Conversation Mode,
`/stt/transcribe`, `/chat`, IPC, Pet Window, Output Queue, or Diagnostics Drawer.

Probe behavior:

- `--help` prints CLI usage.
- `--check-only` performs local dependency checks and returns JSON.
- No audio arguments means dependency check only; no model load and no recording.
- `--load-model` attempts a local-cache-only FunASR CAM++ model load.
- `--allow-download` is required before the probe may allow model download/update.
- Audio mode requires existing mono 16 kHz PCM WAV files:
  - `--enroll-a path\to\owner1.wav`
  - `--verify-a path\to\owner2.wav`
  - optional `--verify-b path\to\other.wav`
- Embeddings are kept in memory only. The JSON report includes only dimension and
  cosine similarity scores, never full embedding vectors.

Current local dependency result from `.venv-funasr`:

- Python: 3.10.11
- `torchAvailable`: true (`2.12.0+cpu`)
- `funasrAvailable`: true
- `modelscopeAvailable`: true
- `numpyAvailable`: true
- `soundfileAvailable`: true
- `modelLoaded`: false in `--check-only`

JSON report fields include:

```json
{
  "status": "ok|unavailable|error",
  "reason": "dependency_check_only|missing_dependency|missing_model|embedding_failed|...",
  "provider": "funasr-campp",
  "python": "3.10.11",
  "torchAvailable": true,
  "modelLoaded": false,
  "embeddingDim": null,
  "ownerScore": null,
  "otherScore": null,
  "thresholdSuggestion": 0.65,
  "rawAudioPersisted": false,
  "embeddingPersisted": false,
  "micAccessed": false,
  "runtimeIntegrated": false,
  "message": "..."
}
```

Safety result:

- No microphone access.
- No `getUserMedia` / `MediaRecorder`.
- No raw audio copy into repo.
- No sample folder.
- No formal voiceprint storage.
- No raw stack traces on stdout.
- No full embedding vector printed.
- No runtime integration.

Windows owner voice probe smoke result:

```json
{
  "provider": "funasr-campp",
  "modelId": "iic/speech_campplus_sv_zh-cn_16k-common",
  "status": "ok",
  "reason": "embedding_probe_complete",
  "modelLoaded": true,
  "modelLoadSeconds": 10.425,
  "embeddingDim": 192,
  "ownerScore": 0.9232,
  "otherScore": 0.052,
  "thresholdSuggestion": 0.65,
  "rawAudioPersisted": false,
  "embeddingPersisted": false,
  "micAccessed": false,
  "runtimeIntegrated": false,
  "python": "3.10.11",
  "torchVersion": "2.12.0+cpu",
  "cudaAvailable": false
}
```

Audio validation:

| File | Duration | Channels | Sample rate | Format | Result |
|---|---:|---:|---:|---|---|
| `owner1.wav` | 10.581 s | mono | 16 kHz | PCM WAV | valid |
| `owner2.wav` | 12.181 s | mono | 16 kHz | PCM WAV | valid |
| `other.wav` | 12.075 s | mono | 16 kHz | PCM WAV | valid |

Closeout conclusion:

- Offline owner voice probe PASS.
- CAM++ model can load locally on this Windows machine.
- 192-dimensional speaker embedding extraction works.
- ownerScore 0.9232 vs otherScore 0.052 gives strong separation in this smoke.
- thresholdSuggestion 0.65 is reasonable for a first pass.
- Probe remains offline and file-based.
- No microphone access.
- No raw audio persistence.
- No embedding persistence.
- No runtime integration.
- Manual Mic, Conversation Mode, STT, and chat flow are unchanged.

Recommended next design task:

- TASK-260 Owner Voice Gate Enrollment Storage Design, or
- TASK-260 Owner Voice Gate Threshold / Multi-Sample Probe.

Design should cover enrollment sample count, local embedding storage format,
reset/delete voiceprint UX, threshold tuning, false accept / false reject
diagnostics, no raw audio persistence, and the convenience-filter limitation.

## 11. TASK-260 storage design

Status: DESIGNED - OWNER VOICE ENROLLMENT STORAGE PLAN / NO RUNTIME CHANGE

TASK-260 adds `docs/OWNER_VOICE_GATE_STORAGE_DESIGN.md` as the docs-only design
checkpoint for future owner voice enrollment storage.

Design summary:

- Enrollment should be explicit through an "Enroll Owner Voice" action.
- First version should require 3 samples, each 8-15 seconds.
- Each sample produces one normalized embedding.
- The app should average normalized embeddings and normalize the result into one
  centroid.
- Store the centroid only, plus metadata and calibration stats.
- Do not store raw audio, base64 audio, full transcript, raw waveform, or
  per-sample embeddings in the first version.
- Recommended future storage path: `userData/owner-voice-gate.json`.
- Initial threshold remains 0.65, informed by TASK-259 ownerScore 0.9232 vs
  otherScore 0.052.
- Delete owner voiceprint should delete only owner voice gate storage and clear
  in-memory embedding state; Clear Chat must not delete the voiceprint.

Future sequence:

- TASK-261 Owner Voice Enrollment UI / Local Storage Stub.
- TASK-262 Owner Voice Gate Calibration Probe.
- TASK-263 Owner Voice Enrollment File Import / Centroid Storage.
- TASK-264 Owner Voice Gate Verification Probe / Stored Centroid Scoring.
- TASK-SEC-001 Security Boundary / Anti Prompt Injection Design.
- TASK-SEC-002 Sensitive Data Inventory / Redaction Rules (DONE).
- TASK-SEC-003 Prompt Injection Test Corpus (DONE).
- TASK-SEC-004 Tool Permission / User Confirmation Policy.
- TASK-SEC-005 Phishing / Link Safety Warning Layer.
- TASK-266 Owner Voice Gate Manual Mic Dry-run Policy.
- TASK-267 Owner Voice Gate Conversation Mode Dry-run Policy.

Runtime remains unchanged by TASK-260.

## 12. TASK-261 UI / storage stub

TASK-261 implements the first owner voice gate settings surface without
enrollment or runtime gating.

Implemented boundary:

- Backend-owned storage stub:
  `backend/data/owner_voice_gate_settings.json`.
- Test/alternate path override: `OWNER_VOICE_GATE_FILE_PATH`.
- Narrow endpoints:
  - `GET /owner-voice-gate/status`
  - `POST /owner-voice-gate/settings`
  - `POST /owner-voice-gate/delete`
- Full App Owner Voice Gate settings UI.
- `threshold` default remains `0.65`, clamped to `0.40..0.95`.
- `enabled=true` before enrollment returns clean `not_enrolled` and keeps the
  gate disabled.
- `embeddingAggregate` remains `null`; no real voiceprint is saved.

Safety boundary remains unchanged:

- No microphone access.
- No recording.
- No raw audio persistence.
- No base64 audio persistence.
- No transcript persistence.
- No real embedding persistence.
- No Manual Mic gate.
- No Conversation Mode gate.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No IPC channel.
- No Pet Window, Output Queue, or Diagnostics Drawer runtime change.

Next completed step after TASK-261 was TASK-262 Owner Voice Gate Calibration
Probe / Multi-Sample Threshold Review. TASK-263 now implements file-based
enrollment and centroid storage. Do not jump directly to Manual Mic or
Conversation Mode runtime gating.

## 13. TASK-262 multi-sample calibration probe

Status: DONE - WINDOWS OWNER VOICE CALIBRATION SMOKE PASS

TASK-262 extends `scripts/owner_voice_gate_probe.py` with multi-sample
calibration support. It is still offline and file-path-only.

New CLI arguments:

- `--owner-sample PATH` (repeatable): owner WAV sample paths.
- `--other-sample PATH` (repeatable): other-speaker WAV sample paths.
- `--owner-dir DIR`: directory of owner WAV files.
- `--other-dir DIR`: directory of other-speaker WAV files.
- `--output-json PATH`: optional JSON report file output.

Calibration behavior:

1. Collect all owner samples; compute embeddings in memory only.
2. Compute owner centroid: normalized mean of all owner embeddings.
3. `ownerSelfScores`: cosine(centroid, each owner embedding).
4. `otherScores`: cosine(centroid, each other-speaker embedding).
5. `ownerStats`: mean, min, max, p10, p90 of ownerSelfScores.
6. `otherStats`: mean, max, p90 of otherScores.
7. Threshold suggestions clamped to `[0.40, 0.95]`:
   - `balancedThreshold`: midpoint(ownerMin, otherMax) when other samples exist.
   - `conservativeThreshold`: 60% of the way from midpoint toward ownerMin.
   - `permissiveThreshold`: 60% of the way from midpoint toward otherMax.
   - Owner-only fallback: conservative/balanced/permissive derived from ownerMin.
8. `scoreGap`: ownerMin - otherMax.
9. `separationQuality`: `strong` (≥ 0.35), `moderate` (≥ 0.15), `weak` (< 0.15), `overlap` (≤ 0), `owner_only`.
10. Thresholds are local calibration hints only — not universal truths.

Safety boundary (unchanged):

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

Windows calibration smoke PASS:

- Repeated sample args mode PASS: `--owner-sample owner1.wav`,
  `--owner-sample owner2.wav`, `--other-sample other.wav`, and
  `--output-json task262-calibration.json`.
- Directory mode PASS: `--owner-dir %TEMP%\dragon-pet-voice-probe\owner`,
  `--other-dir %TEMP%\dragon-pet-voice-probe\other`, and
  `--output-json task262-calibration-dir.json`.
- Directory mode loaded `iic/speech_campplus_sv_zh-cn_16k-common` locally
  with FunASR CAM++ in 9.391 s and produced 192-d embeddings.
- ownerSampleCount: 2; otherSampleCount: 1.
- ownerSelfScores: `[0.9806, 0.9806]`.
- otherScores: `[0.0778]`.
- ownerStats mean/min/max/p10/p90: `0.9806`.
- otherStats mean/max/p90: `0.0778`.
- scoreGap: `0.9028`.
- separationQuality: `strong`.
- thresholdSuggestion / balancedThreshold: `0.5292`.
- conservativeThreshold: `0.8`.
- permissiveThreshold: `0.4`.
- rawAudioPersisted=false, embeddingPersisted=false, micAccessed=false,
  runtimeIntegrated=false.

Threshold interpretation:

The smoke result shows strong separation for this Windows machine and these
three samples, but the sample count is still small. Do not treat `0.5292` as a
universal production default. For future runtime gating, keep `0.65` as the
first balanced default unless larger calibration data suggests otherwise.
Document `0.8` as conservative mode. Treat `0.4` as debug/permissive only, not
as the first runtime gate default.

Backwards compatibility:

- `--enroll-a` and `--verify-a` still work as before (treated as 2 owner samples).
- `--verify-b` still works (treated as 1 other-speaker sample).
- Legacy `ownerScore` and `otherScore` fields are set when only legacy args are used.

TASK-263 implements the first real local voiceprint write path:

- `scripts/owner_voice_gate_enroll.py` runs in `.venv-funasr` Python 3.10.
- Backend endpoint: `POST /owner-voice-gate/enroll-files`.
- Payload accepts local file paths only: `paths`, `threshold`, `safetyNoticeAccepted`.
- The endpoint rejects raw audio, base64 audio, transcripts, waveforms, and embedding vectors from the UI.
- Enrollment requires at least 2 owner WAV paths and safety notice acceptance.
- The sidecar validates 16 kHz mono PCM WAV files, loads FunASR CAM++, extracts embeddings in memory, L2-normalizes each embedding, averages, and L2-normalizes the centroid.
- Backend storage writes only the final 192-d centroid, `enrolled=true`, `sampleCount`, threshold, calibration stats, provider/model metadata, and timestamps.
- API status/settings responses mask the centroid by default; UI does not render `embeddingAggregate`.
- Gate remains disabled after enrollment until explicitly enabled.
- Delete clears the centroid and resets `enrolled=false`.

TASK-263 follow-up fixes Windows non-ASCII/Unicode path handling for
`/owner-voice-gate/enroll-files`. The backend no longer eagerly resolves owner
sample paths before invoking the `.venv-funasr` sidecar; it trims and
`expanduser()`s paths, validates that each path exists with `Path.is_file()`,
passes the caller-provided Unicode spelling through to sidecar argv, and decodes
sidecar JSON stdout as UTF-8. Missing files return a clean
`audio_file_not_found` not-enrolled result without stack traces or raw paths.
Windows Unicode backend API smoke PASS with two owner WAVs under
`C:\Users\雪狼丸\AppData\Local\Temp`: `enrolled=true`, `sampleCount=2`,
`embeddingDim=192`, `embeddingPersisted=true`, `status=disabled`,
`reason=enrolled`, and masked `embeddingAggregate=null`.

The stored centroid is sensitive local biometric-like data. It is still a
convenience-filter voiceprint, not security-grade authentication.

Safety boundary remains unchanged:

- No Manual Mic runtime gate.
- No Conversation Mode runtime gate.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No new IPC channel.
- No microphone access.
- No recording.
- No raw audio persistence.
- No transcript or waveform persistence.
- No always listening or background monitoring.
- No Pet Window, Output Queue, or Diagnostics Drawer change.

Recommended next tasks:

- TASK-264 Owner Voice Gate Verification Probe / Stored Centroid Scoring.
- TASK-SEC-001 Security Boundary / Anti Prompt Injection Design.
- TASK-SEC-002 Sensitive Data Inventory / Redaction Rules (DONE).
- TASK-SEC-003 Prompt Injection Test Corpus (DONE).
- TASK-SEC-004 Tool Permission / User Confirmation Policy.
- TASK-SEC-005 Phishing / Link Safety Warning Layer.
- TASK-266 Owner Voice Gate Manual Mic Dry-run Policy.
- TASK-267 Owner Voice Gate Conversation Mode Dry-run Policy.

Do not jump to runtime gating until the explicit runtime task accepts the
threshold strategy and keeps owner voice gate opt-in.

## 15. TASK-264 stored centroid verification probe

TASK-264 adds the first local verification probe against the stored owner
centroid. It intentionally remains script-only:

- Script: `scripts/owner_voice_gate_verify.py`.
- Runtime: `.venv-funasr` Python 3.10.
- Input: existing local WAV file paths via `--candidate-sample` or
  `--candidate-dir`.
- Storage input: backend-owned `owner_voice_gate_settings.json`.
- Model: FunASR CAM++ / 3D-Speaker 192-d embedding.
- Scoring: L2-normalized candidate embedding or aggregate candidate centroid
  compared to the stored owner centroid with cosine similarity.
- Decision: `accepted = score >= threshold`.

Expected report fields:

- `status`
- `reason`
- `enrolled`
- `score`
- `scores`
- `threshold`
- `accepted`
- `embeddingDim`
- `sampleCount`
- `rawAudioPersisted=false`
- `candidateEmbeddingPersisted=false`
- `storedCentroidExposed=false`
- `micAccessed=false`
- `runtimeIntegrated=false`

Safety boundary:

- No microphone access or recording.
- No raw audio, transcript, waveform, or base64 audio persistence.
- No candidate embedding persistence.
- No stored centroid in the output.
- No backend verify endpoint in TASK-264.
- No Manual Mic, Conversation Mode, `/stt/transcribe`, `/chat`, IPC, Pet
  Window, Output Queue, or Diagnostics Drawer runtime change.

After TASK-264 smoke passes, TASK-265 adds the backend verification endpoint.
After TASK-265, security work must run before runtime wiring:
TASK-SEC-001 Security Boundary / Anti Prompt Injection Design, TASK-SEC-002
Sensitive Data Inventory / Redaction Rules (DONE), TASK-SEC-003 Prompt Injection Test
Corpus (DONE), TASK-SEC-004 Tool Permission / User Confirmation Policy, and
TASK-SEC-005 Phishing / Link Safety Warning Layer. The next owner voice runtime
work should be TASK-266 Manual Mic dry-run policy, still opt-in and disabled by
default.

Windows stored-centroid smoke PASS:

- Owner candidate `owner2.wav`: `score=0.9806`, `threshold=0.65`,
  `accepted=true`.
- Other candidate `other.wav`: `score=0.0778`, `threshold=0.65`,
  `accepted=false`.
- Both reports used 192-d embeddings from
  `iic/speech_campplus_sv_zh-cn_16k-common` and kept `rawAudioPersisted=false`,
  `candidateEmbeddingPersisted=false`, `storedCentroidExposed=false`,
  `micAccessed=false`, and `runtimeIntegrated=false`.

## 14. TASK-265 — Backend Verification Endpoint / No Runtime Wiring

TASK-265 adds `POST /owner-voice-gate/verify-files` to the backend.

### What changed

- `run_owner_voice_verification_sidecar()` in
  `backend/app/services/owner_voice_gate_storage.py`: calls
  `scripts/owner_voice_gate_verify.py` under `.venv-funasr` Python, passes
  `--settings-json`, `--candidate-sample` args, optional `--threshold`.
- `OwnerVoiceGateStorageService.verify_from_files()`: returns `not_enrolled`
  when no centroid; validates WAV path existence before invoking sidecar;
  strips sidecar output to safe fields only (no `embeddingAggregate`).
- `validate_owner_voice_gate_verify_fields()`: allows only `paths` + `threshold`.
- `POST /owner-voice-gate/verify-files` route in `backend/app/api/routes.py`.

### Safety boundary

- No mic access; no audio bytes from the renderer.
- No raw audio, transcript, waveform, or base64 audio persistence.
- No candidate embedding persistence.
- `embeddingAggregate` (stored centroid vector) never in the API response.
- No Manual Mic, Conversation Mode, `/stt/transcribe`, `/chat`, IPC, Pet
  Window, Output Queue, or Diagnostics Drawer runtime change.

### Windows backend endpoint smoke

PASS on 2026-06-04:

- Owner candidate `%TEMP%\dragon-pet-voice-probe\owner2.wav`:
  `score=0.9806`, `threshold=0.65`, `accepted=true`, `embeddingDim=192`.
- Other candidate `%TEMP%\dragon-pet-voice-probe\other.wav`:
  `score=0.0778`, `threshold=0.65`, `accepted=false`, `embeddingDim=192`.
- Both endpoint responses returned `status=ok`, `reason=verification_complete`,
  `enrolled=true`, and kept `rawAudioPersisted=false`,
  `candidateEmbeddingPersisted=false`, `storedCentroidExposed=false`,
  `micAccessed=false`, and `runtimeIntegrated=false`.
- The API response did not expose the stored centroid or candidate embedding.

### Next task

TASK-SEC-004 Tool Permission / User Confirmation Policy, then TASK-266 Manual
Mic dry-run policy, still opt-in and disabled by default.
