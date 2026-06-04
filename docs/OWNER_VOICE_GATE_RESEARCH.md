# Owner Voice Gate Research

Status: TASK-258 RESEARCH - OWNER VOICE GATE FEASIBILITY / NO RUNTIME CHANGE; TASK-259 DONE - WINDOWS OWNER VOICE PROBE SMOKE PASS

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
  - Define enrollment sample count.
  - Define local embedding storage format.
  - Define reset/delete voiceprint UX.
  - Define threshold tuning and false accept / false reject diagnostics.
  - Keep no raw audio persistence and convenience-filter-only wording.

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
