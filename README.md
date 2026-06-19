# Dragon Pet AI

**Latest TASK-TTS-004E2B resume (2026-06-19):** Existing Anaconda Validation / GPT-SoVITS Phase 1 Resume **DONE - EXISTING ANACONDA VERIFIED / GPT-SOVITS LAB PHASE 1 READY**. Added `docs/TTS_EXISTING_ANACONDA_GPT_SOVITS_PHASE1.md` and external manifest `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2B_EXISTING_ANACONDA_RESUME.md`. Verified machine-wide Anaconda at `C:\ProgramData\anaconda3` using direct `C:\ProgramData\anaconda3\Scripts\conda.exe`; process-local UTF-8 was required for `conda env list` because default code page still hit the known `cp950` issue. Created isolated Python `3.10.20` prefix env at `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\envs\gpt-sovits-py310` using lab package cache `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\pkgs-cache`; PyTorch probe returned `None`. Cloned official GPT-SoVITS from `https://github.com/RVC-Boss/GPT-SoVITS.git` to `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\repos\GPT-SoVITS`, branch `main`, commit `b2cff0cd0abd0ac134a16ae7a9695f88e8826104`, license `MIT License`. No Anaconda base package install/update, PATH/profile/registry change, `conda init`, Miniconda retry, GPT-SoVITS `install.ps1`, dependency/PyTorch/CUDA/model/dataset download, training/inference/WebUI/audio generation, runtime TTS, playback, auto-speaking, STT, Conversation Mode, Owner Voice, schema, backend venv, or dependency-file change was made.

**Latest TASK-TTS-004E2A3 retry (2026-06-19):** Miniconda UTF-8 Retry **BLOCKED - UTF-8 MINICONDA RETRY FAILED / NO FURTHER RETRY PERFORMED**. Added `docs/TTS_MINICONDA_UTF8_RETRY.md` and external manifest `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A3_MINICONDA_UTF8_RETRY.md`. Deleted only the approved failed partial install directory `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3` after exact path verification, preserved the official installer and existing reports, then retried the same verified installer once to the same path with process-local `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8`, and UTF-8 PowerShell/console output encoding. Retry still exited `2`, recreated a partial install, and `.step.log` still reports rollback after a `cp950` `UnicodeDecodeError` while reading existing Conda-related paths. Required `condabin\conda.bat`, `Scripts\conda.exe`, `python.exe`, and `Uninstall-Miniconda3.exe` remain missing. No further retry or post-retry cleanup was performed. No user/system PATH, `conda init`, PowerShell profile, registry, existing machine-wide Anaconda, GPT-SoVITS repo/env, package/PyTorch/CUDA/model/dataset, training/inference/WebUI/audio, runtime TTS, or backend venv change was made.

**Latest TASK-TTS-004E2A2 diagnostics (2026-06-19):** Miniconda Install Failure Diagnostics **BLOCKED - MINICONDA INSTALL ROOT CAUSE NOT IDENTIFIED / NO RETRY PERFORMED**. Added `docs/TTS_MINICONDA_INSTALL_DIAGNOSTICS.md` and external manifest `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A2_MINICONDA_INSTALL_DIAGNOSTICS.md`. No installer retry, GUI install, cleanup, uninstall, alternate Conda tool, Conda env creation, `conda init`, PATH/profile modification, GPT-SoVITS clone, dependency/PyTorch/CUDA/model/dataset download, training, inference, WebUI, synthesis, audio generation, runtime TTS wiring, or backend venv change was performed. Evidence narrows the failed TASK-TTS-004E2A install to rollback after a `.step.log` `cp950` `UnicodeDecodeError` while reading existing Conda-related paths; required `condabin\conda.bat`, `Scripts\conda.exe`, `python.exe`, and `Uninstall-Miniconda3.exe` remain missing, so the partial install is not usable. Installer hash/signature remain valid, no relevant Application or Defender event log error was found, a scoped external lab tools write probe passed, and read-only registry inspection found existing machine-wide Anaconda state. Exact upstream root cause remains unproven.

**Latest TASK-TTS-004E2A attempt (2026-06-19):** Isolated Miniconda Bootstrap **BLOCKED - ISOLATED MINICONDA INSTALL FAILED**. Added `docs/TTS_MINICONDA_LAB_BOOTSTRAP.md` and updated the TTS status docs with actual installer evidence. The official installer was downloaded only from `https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe` to `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\installers\Miniconda3-latest-Windows-x86_64.exe`; file size `99155816` bytes; downloaded SHA-256 and official SHA-256 both `fe980247dfd30af229a55d9505b57e7c8dfbdb9d24c5bc66fb6078b6a2d53414`. Silent install to `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\tools\miniconda3` returned exit code `2` and rolled back with a `cp950` UnicodeDecodeError in `.step.log`; required `condabin\conda.bat`, `Scripts\conda.exe`, `python.exe`, and `Uninstall-Miniconda3.exe` are missing. No PATH/Python registration pollution was detected, `conda init` was not run, and the PowerShell profile was not modified. External manifest: `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\reports\TASK-TTS-004E2A_MINICONDA_BOOTSTRAP.md`. No GPT-SoVITS/Style-Bert repo was cloned, no Conda env was created, no dependencies/PyTorch/CUDA/models/datasets were installed or downloaded, no training/inference/WebUI/audio generation occurred, and no runtime TTS, `/chat`, playback, Pet playback, auto-speaking, STT, Conversation Mode, Owner Voice, schema, runtime, or dependency behavior changed.

**Latest TASK-TTS-004E2 attempt (2026-06-19):** GPT-SoVITS Isolated Lab Bootstrap Phase 1 **BLOCKED - CONDA NOT AVAILABLE / NO INSTALL PERFORMED**. Added `docs/TTS_GPT_SOVITS_LAB_PHASE1.md` and updated the TTS status docs with actual pre-flight evidence. Main repo pre-flight saw only the expected unrelated `docs/開啟方式.txt` dirty file and HEAD `79513c2`. `conda --version`, `conda info --base`, and `conda env list` all failed because `conda` was not recognized in the current PowerShell PATH, so the approved Phase 1 stopped before setup. No external lab folder was created, no GPT-SoVITS repo was cloned, no Conda Python 3.10 environment was created, no external Phase 1 manifest was written, no dependency/model/dataset was installed or downloaded, and no training/inference/WebUI/audio generation was run. Hardware evidence remains RTX 3070 / 8192 MiB VRAM / NVIDIA-SMI 610.47 / CUDA compatibility 13.3 from `nvidia-smi`; this does not prove PyTorch CUDA is installed. Runtime TTS remains disabled/mock-only; no `/chat`, playback, Pet playback, auto-speaking, STT, Conversation Mode, Owner Voice, schema, runtime, or dependency behavior changed.

**Latest TASK-TTS-004E closeout (2026-06-19):** Character Voice Lab Provider Selection / First Probe Approval **DONE - CHARACTER VOICE PROVIDER SELECTION READY / FIRST PROBE NOT APPROVED YET**. Added `docs/TTS_CHARACTER_VOICE_PROVIDER_SELECTION.md` and updated the TTS status docs. First isolated lab candidate is GPT-SoVITS; Style-Bert-VITS2 is the second provider / fallback research path. RVC-like conversion remains deferred, edge-tts remains temporary Chinese/debug/fallback only, and VOICEVOX remains Japanese-style experiment only. Proposed lab path remains `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\`; preferred environment is isolated Conda with Python `3.10` or `3.11`, no reuse of `backend\.venv`, and lab-only PyTorch/CUDA only after explicit approval. First real setup still requires approval for lab path, provider, Python version, Conda vs venv, external clone, package install, PyTorch/CUDA install, model download, test audio generation, and artifact policy. No package/model was installed, no external repo was cloned, no lab setup was performed, no model download/training/inference/audio generation was run, no runtime TTS wiring, playback, Pet playback, auto-speaking, generated artifact commit, `/chat` schema or mood schema change, STT default/model selector change, Conversation Mode queue/backpressure change, or Owner Voice hard-gate change was added.

**Latest TASK-TTS-004D4 closeout (2026-06-19):** Character Voice Lab Bootstrap Checklist / Manual Commands Only **DONE - CHARACTER VOICE LAB BOOTSTRAP CHECKLIST READY / NO SETUP PERFORMED**. Added `docs/TTS_CHARACTER_VOICE_LAB_BOOTSTRAP_CHECKLIST.md` and updated the TTS status docs. The checklist documents manual-only pre-flight checks, future lab folder commands for `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\`, isolated Conda-first environment strategy, Python `3.10`/`3.11` guidance instead of app backend Python `3.14.4`, `nvidia-smi` and PyTorch CUDA verification commands, lab-only GPT-SoVITS / Style-Bert-VITS2 clone locations, model/data storage rules, non-commit artifact policy, and a human approval gate before any clone, install, CUDA/PyTorch setup, model download, training, inference, or synthesis. No lab setup was performed, no package/model installed, no external repo cloned, no model download/training/inference run, no runtime TTS wiring, playback, Pet playback, auto-speaking, generated artifact commit, `/chat` schema or mood schema change, STT default/model selector change, Conversation Mode queue/backpressure change, or Owner Voice hard-gate change was added.

**Latest TASK-TTS-004D3 closeout (2026-06-19):** Character Voice Lab Environment Plan / Isolated GPU Env **DONE - CHARACTER VOICE LAB PLAN READY / NO LAB INSTALL PERFORMED**. Added `docs/TTS_CHARACTER_VOICE_LAB_PLAN.md` and narrow ignore entries for accidental local lab artifacts. Future GPT-SoVITS / Style-Bert-VITS2 experiments should live outside Dragon Pet AI app code, preferably under `F:\RickHSIAO\AI-Labs\dragon-pet-voice-lab\`, with external repos, model weights, datasets, generated WAV/MP3 samples, and logs kept out of Git. The plan recommends dedicated Conda environments, Python `3.10` for GPT-SoVITS, lab-only CUDA/PyTorch, no reuse of `backend\.venv`, licensing/voice-data review, standalone audio output first, and manual listening gates before runtime provider selection. No lab folder was created, no external repo cloned, no package/model installed, no model download/training/inference run, no runtime TTS wiring, playback, Pet playback, auto-speaking, generated artifact commit, `/chat` schema or mood schema change, STT default/model selector change, Conversation Mode queue/backpressure change, or Owner Voice hard-gate change was added.

**Latest TASK-TTS-004D2 implementation (2026-06-19):** Character Voice Environment Check / No Install **IMPLEMENTED - CHARACTER VOICE ENV CHECK READY / NO INSTALL PERFORMED**. Added `scripts/tts_character_voice_env_check.py`, targeted tests, and ignored output path `outputs/tts_character_voice_env_check/`. The checker records OS/platform, Python executable/version/venv, Git, disk space, `nvidia-smi` GPU/CUDA details when available, PyTorch availability/CUDA/device evidence only if already installed, Node/npm, localhost-only VOICEVOX metadata reachability, optional `edge_tts` package availability, warnings, safety flags, and deterministic feasibility verdict. Reports are local JSON/Markdown artifacts under ignored `outputs/tts_character_voice_env_check/YYYYMMDD/`. No package/model install, model download, external repo clone, training, inference, runtime TTS wiring, playback, Pet playback, auto-speaking, dependency/default-runtime change, generated report/audio/model commit, `/chat` schema or mood schema change, STT default/model selector change, Conversation Mode queue/backpressure change, or Owner Voice hard-gate change was added.

**Latest TASK-TTS-004D closeout (2026-06-19):** Style-Bert-VITS2 / GPT-SoVITS Feasibility Research **DONE - CHARACTER VOICE FEASIBILITY RESEARCH COMPLETE / NO MODEL INSTALLED**. Added `docs/TTS_CHARACTER_VOICE_FEASIBILITY.md` and updated the TTS roadmap/research/architecture status. No final provider is selected. GPT-SoVITS and Style-Bert-VITS2 are the leading long-term character voice research candidates if Chinese usability and Christina fit are both required; edge-tts remains temporary/debug/fallback only, VOICEVOX remains Japanese-style experiment only, and RVC-like conversion is deferred until a source TTS provider exists. Later runtime playback work remains blocked until provider selection, explicit first-probe approval, standalone synthesis evidence, manual listening, and license/data review are complete. No model install/download, training, inference, runtime TTS wiring, playback, Pet playback, auto-speaking, dependency/default-runtime change, generated audio/report commit, `/chat` schema or mood schema change, STT default/model selector change, Conversation Mode queue/backpressure change, or Owner Voice hard-gate change was added.

**Latest TASK-TTS-004C3 closeout (2026-06-19):** Edge-TTS Voice / Rate Tuning Probe **DONE - EDGE-TTS TUNING REVIEW COMPLETE / NO SUITABLE CHRISTINA VOICE FOUND**. This was docs-only because `scripts/tts_provider_probe.py` already supports `--edge-tts-voice`, `--edge-tts-rate`, and `--edge-tts-pitch`. Manual tuning verdict: `zh-TW-HsiaoChenNeural -10%` feels somewhat better than baseline but still lacks the right Christina/character feel and is not enough to select as provider; `zh-TW-HsiaoYuNeural -10%` is not suitable because it sounds too old; `zh-CN-XiaoxiaoNeural -10%` is not suitable because it sounds too mainland-China-like for the user's preference. No edge-tts voice reached desired Christina fit. Provider decision: edge-tts remains temporary Chinese provider / debug preview / fallback candidate only, not final Christina voice and not runtime provider. Stop further edge-tts tuning for now unless explicitly revisited. Recommended next path is TASK-TTS-004D Style-Bert-VITS2 / GPT-SoVITS feasibility research. Runtime TTS remains disabled/mock-only. No `/chat` integration, playback, Pet Window playback, auto-speaking, dependency/default-runtime change, generated audio/report commit, STT, Conversation Mode, Owner Voice, or schema behavior change was added.

**Latest TASK-TTS-004C2 closeout (2026-06-18):** Edge-TTS Manual Dependency Probe / Chinese Audio Output **DONE - EDGE-TTS AUDIO OUTPUT SUCCESS / TEMP CHINESE PROVIDER ONLY**. With explicit approval, `edge-tts` was installed into `backend\.venv` only for the manual provider probe (`edge-tts==7.2.8` plus transitive packages). Metadata-only probe reports `available=true`, `reason=optional_dependency_present`, `synthesisStatus=metadata_only`, `voice=zh-TW-HsiaoChenNeural`, and `audioGenerated=false`; metadata-only mode still does not send text to Microsoft Edge TTS service. Optional audio probe with `--allow-audio-output` generated an ignored local MP3 (`audioGenerated=true`, `audioBytes=30240`, `synthesisLatencyMs=1613`, `reason=edge_tts_success`) under `outputs/tts_provider_probe/20260618/audio/`. Manual listening verdict: Chinese is understandable, speed is slightly fast, tone is okay, no strange pauses, overall `6/10`, but Christina/anime fit is weak and the voice feels more general/Taiwanese than Christina-like. Provider decision: `edge_tts` is acceptable as a temporary Chinese provider candidate only, retained as optional network/cloud-ish preview/debug/fallback path, not selected as the final Christina long-term voice, and not wired into runtime. No playback, auto-speaking, dependency/default-runtime change, `/chat` integration, STT, Conversation Mode, Owner Voice, or schema behavior change was added; generated MP3/report artifacts were not committed.

**Latest TASK-TTS-004C implementation (2026-06-18):** Edge-TTS Optional Network Candidate Probe / Chinese Voice Validation **IMPLEMENTED - EDGE-TTS OPTIONAL PROBE READY / CHINESE AUDIO VALIDATION PENDING**. `scripts/tts_provider_probe.py` now supports deeper `edge_tts` probe options: `--edge-tts-voice` (default `zh-TW-HsiaoChenNeural`), `--edge-tts-rate` (default `+0%`), `--edge-tts-pitch` (default `+0Hz`), and `--edge-tts-timeout-sec` (default `30`). Default metadata-only mode checks optional dependency availability only and does not synthesize, send text to the network, write audio, or play audio. Optional MP3 generation requires explicit `--allow-audio-output`, may send text to Microsoft Edge TTS service, and writes only under ignored `outputs/tts_provider_probe/YYYYMMDD/audio/`. Current machine metadata-only result is safe unavailable: `reason=missing_optional_dependency`, `synthesisStatus=missing_optional_dependency`, `audioGenerated=false`. No dependency/install, runtime TTS wiring, `/chat` integration, playback, auto-speaking, generated audio/report commit, STT default/model selector change, Conversation Mode queue/backpressure change, Owner Voice hard-gate change, or schema change was added.

**Latest TASK-TTS-004B2 closeout (2026-06-18):** VOICEVOX Synthesis Timeout / Retry Hardening **DONE - VOICEVOX AUDIO OUTPUT SUCCESS / NOT SELECTED FOR CHINESE RUNTIME**. VOICEVOX Engine `0.25.2` local optional audio output succeeded after timeout hardening (`voicevox_success`, `audioGenerated=true`, `audioBytes=291372`, `synthesisLatencyMs=1568`, `retryCount=0`). Manual listening verdict: Japanese/anime-style voice is good, tone is good, speed is okay, no strange pauses, overall 7/10, but Chinese text is pronounced as Japanese and is not understandable as Chinese. Provider decision: VOICEVOX remains technically usable as a local server and retained as an optional Japanese-style/Japanese-utterance experiment path, but it is not selected as the main Chinese TTS runtime provider. Next provider direction is TASK-TTS-004C edge-tts for Chinese voice validation or TASK-TTS-004D Style-Bert-VITS2 / GPT-SoVITS feasibility for longer-term character voice. No runtime TTS wiring, `/chat` integration, playback, auto-speaking, dependency/install, generated audio/report commit, STT default/model selector change, Conversation Mode queue/backpressure change, Owner Voice hard-gate change, or schema change was added.

**Latest TASK-TTS-004B implementation (2026-06-18):** VOICEVOX Local Server Manual Probe / Audio Output Optional **IMPLEMENTED - VOICEVOX MANUAL PROBE READY / OPTIONAL AUDIO OUTPUT LOCAL ONLY**. `scripts/tts_provider_probe.py` now supports a manual `voicevox_server` localhost probe with `--voicevox-url`, `--voicevox-speaker`, and optional `--allow-audio-output`. Default behavior checks only VOICEVOX metadata (`/version`, best-effort `/speakers`) and does not call synthesis, write audio, or play audio. Optional WAV generation calls VOICEVOX `audio_query` + `synthesis` only after explicit `--allow-audio-output`, then writes under ignored `outputs/tts_provider_probe/YYYYMMDD/audio/`. Non-localhost VOICEVOX URLs are rejected before network access. Local metadata-only probe on this machine safely reported `server_unavailable:URLError` because `http://127.0.0.1:50021` was not running; `audioGenerated=false`. No runtime TTS wiring, `/chat` integration, playback, auto-speaking, dependency/install, generated audio/report commit, ElevenLabs integration, STT default/model selector change, Conversation Mode queue/backpressure change, Owner Voice hard-gate change, or schema change was added.

**Latest TASK-TTS-004A review (2026-06-18):** Local TTS Provider Selection Review / Install-Free Probe Summary **DONE - INSTALL-FREE PROVIDER REVIEW COMPLETE / REAL PROVIDER NOT SELECTED**. Windows install-free probe found no real TTS provider ready on this machine: only `mock` was available (`mock_metadata_only`), while `windows_sapi` lacked an optional Python bridge, `voicevox_server` was not running at `http://127.0.0.1:50021/version`, `edge_tts` was not installed, and Piper/GPT-SoVITS/Style-Bert-VITS2/RVC-like paths remain future/manual candidates. Runtime playback should not start yet; `mock` remains the only safe skeleton provider. Recommended next investigation is either TASK-TTS-004B VOICEVOX local-server manual probe for fast anime/Japanese-style validation, TASK-TTS-004C edge-tts optional network candidate for fast Chinese voice validation, or TASK-TTS-004D Style-Bert-VITS2 / GPT-SoVITS feasibility research for longer-term character voice quality. No runtime TTS wiring, playback, auto-speaking, dependency/install, generated audio/report commit, ElevenLabs integration, STT default/model selector change, Conversation Mode queue/backpressure change, Owner Voice hard-gate change, or schema change was added.

**Latest TASK-TTS-003 implementation (2026-06-18):** Local TTS Provider Candidate Probe / No Runtime Wiring **IMPLEMENTED - LOCAL TTS PROVIDER PROBE SMOKE PASS / NO RUNTIME WIRING**. Added `scripts/tts_provider_probe.py` and targeted tests for local/offline provider candidate checks. The probe reuses TASK-TTS-002 text normalization, always supports `mock`, gracefully skips unavailable candidates, and writes local JSON/Markdown reports under `outputs/tts_provider_probe/YYYYMMDD/` (ignored by git). Supported candidate names are `mock`, `windows_sapi`, `voicevox_server`, `edge_tts`, `piper_onnx`, `gpt_sovits`, `style_bert_vits2`, and `rvc_like`. Audio generation is off by default and no TASK-TTS-003 provider generates audio. No runtime TTS wiring, `/chat` integration, playback, auto-speaking, dependency, ElevenLabs/cloud default, generated audio, committed report, STT default/model selector change, Conversation Mode queue/backpressure change, Owner Voice hard-gate change, or schema change was added.

**Latest TASK-TTS-002 implementation (2026-06-18):** Mock TTS Provider Skeleton / Disabled-by-default TTS Queue **IMPLEMENTED - MOCK TTS SKELETON SMOKE PASS / RUNTIME PLAYBACK NOT STARTED**. Added backend metadata-only TTS skeleton under `backend/app/tts/`: provider abstraction, deterministic `MockTTSProvider`, conservative text normalization/chunking, disabled queue diagnostics, and targeted backend tests. Defaults are fail-closed (`TTS_ENABLED=false`, provider `mock`, voice `christina_mock`); the mock provider returns chunks, estimated duration, `synthesisStatus=mock_success`, `audioAvailable=false`, and `audioPath=null`. No route, renderer controls, real synthesis, real playback, generated audio, dependency, ElevenLabs/cloud integration, `/chat` or mood schema change, STT default/model selector change, Conversation Mode queue/backpressure change, Owner Voice hard-gate change, or runtime auto-speaking was added.

**Latest TASK-TTS-001 design (2026-06-18):** Local TTS Provider Architecture / Christina Voice Output Design **DONE - TTS ARCHITECTURE DESIGN READY / IMPLEMENTATION NOT STARTED**. Added provider-neutral TTS architecture and provider research docs for future Christina voice output: accepted chat reply -> text normalization -> TTS queue -> provider adapter -> playback -> Pet speaking state. The first implementation path should start with a mock provider and local/offline provider experiments, not ElevenLabs or any paid external API. Runtime TTS provider architecture implementation has not started; no new dependency, generated audio, voice sample, schema change, STT default/model selector change, Conversation Mode queue/backpressure change, Owner Voice hard-gate change, or runtime auto-speaking change was added.

**Latest TASK-CONV-006 closeout (2026-06-18):** Conversation Mode Backpressure Pause / No Usable Queue-Full Drop **DONE - WINDOWS LONG SESSION BACKPRESSURE RE-SMOKE PASS / NO REPEATED USABLE QUEUE_FULL DROPS**. Conversation Mode keeps bounded pending queue max `4` and pauses starting new VAD-triggered utterance recorders at `pending=4/4` or high watermark `pending>=3/4` while a turn is active/processing, then resumes at `pending<=2/4` or `drain_complete`. Windows re-smoke with STT model `base` observed `queue_high_watermark` pause at `pending=3/4 active=10`, final `pending=0/4`, `activeTurnId=0`, `queue=idle/drain_complete`, `stopMode=drain_complete`, and final backpressure `paused=false reason=none resume=queue_available`. No repeated usable-audio `queue_full`, no `chat_error`, and no no-speech hallucination appeared; Owner Voice dry-run stayed non-blocking with temporary candidate WAV deleted. The hard fallback `queue_full` path remains visible with `audio=usable_audio`, `dropStage=at_queue`. No STT default/model selector, `/chat` or mood schema, Owner Voice hard gate, TTS, frontend redesign, IPC, Pet Window, Output Queue, raw audio persistence, or generated artifact commit was added.

**Latest TASK-CONV-005 closeout (2026-06-18):** Conversation Mode Long Session Stability Smoke **DONE - ADDRESSED / VALIDATED BY TASK-CONV-006 WINDOWS LONG SESSION RE-SMOKE PASS**. `apps/desktop/scripts/conversation-long-session-smoke.js` verifies the renderer diagnostics source shape and, as of TASK-CONV-006, a synthetic 13-turn lifecycle fixture for longer Conversation Mode sessions. It guards bounded queue max `4`, queue pressure/full visibility, `drain_complete`, backpressure pause/resume, distinct hard fallback `queue_full` usable-audio overflow vs `empty_artifact` before-queue drops, Owner Voice dry-run visibility, candidate WAV deletion facts, and the copyable long-session summary format. The TASK-CONV-006 Windows re-smoke validated the long-session follow-up with clean final drain and no repeated usable-audio `queue_full` drops.

**Latest TASK-STT-007 closeout (2026-06-12):** STT Model Advisor Runner **DONE - WINDOWS END-TO-END ADVISOR RUNNER SMOKE PASS / ONE-COMMAND STT ADVISOR READY**. `scripts/stt_model_advisor_runner.py` is the one-command CLI orchestration layer over TASK-STT-006A evaluation, TASK-STT-006B deterministic scoring, and TASK-STT-006C grounded explanation. It writes normal intermediate runtime artifacts plus a final manifest under `outputs/stt_model_advisor/YYYYMMDD/` with stage report basenames, deterministic recommendation facts, explanation text, and safety flags (`defaultChanged=false`, `runtimeAutoSwitchChanged=false`, `llmUsed=false`, `noReferenceTranscriptCaveat=true`). Windows end-to-end smoke passed with two local owner WAV files and generated evaluation/scoring/explanation/advisor reports. This is deterministic/no-LLM by default and does not add a frontend comparison panel, runtime auto-switch, STT default change, `/chat` or mood schema change, Owner Voice hard-gate change, committed generated report/audio, or unsupported accuracy/WER claim.

**Latest TASK-STT-006C closeout (2026-06-12):** Christina Grounded STT Recommendation Explanation **DONE - WINDOWS GROUNDED EXPLANATION SMOKE PASS / CHRISTINA ZH-TW EXPLANATION READY**. `scripts/stt_model_recommendation_explanation.py` reads a TASK-STT-006B scoring report and writes grounded explanation JSON under `outputs/stt_model_explanation/YYYYMMDD/`. The script supports `christina` and `plain` styles, emits source recommendation facts, score summary, caveats, next action, grounding checks, and explicit `defaultChange.changed=false` / `runtimeAutoSwitch.changed=false`. Windows grounded explanation smoke passed, and the Christina localization fix passed with Traditional Chinese proud/tsundere, helpful, caveated wording. It is deterministic/no-LLM by default; `--use-llm` is accepted for future compatibility but currently falls back to grounded templates. No frontend comparison panel, runtime model auto-switch, STT default change, `/chat` or mood schema change, Owner Voice hard-gate change, generated explanation report commit, or unsupported accuracy/WER claim is added.

**Latest TASK-PERSONA-002 closeout (2026-06-12):** Christina General Tone Sanitizer for Non-Debug Replies **DONE - WINDOWS GENERAL TONE SMOKE PASS / GENERAL REPAIR ENABLED**. Windows general tone smoke passed after the companion/testing tone repair: companion/testing prompts returned cooperative tsundere help, light sass remained acceptable, garbled-STT handling still clarified without hostility, and STT/debug prompts still used `NEEDS EVIDENCE`. The LLM success path keeps TASK-PERSONA-001 debug repair first, then TASK-PERSONA-002 general repair second. No `浪費吾的時間`, `奴隸`, comparative value humiliation, threat phrase, refusal/abandoning phrasing, or `測吾的耐心` appeared. Safe tsundere lines are preserved. No `/chat` schema, mood schema, STT default, Owner Voice hard gate, renderer IPC, provider runtime, or runtime model change.

**Latest TASK-STT-006B closeout (2026-06-12):** Deterministic STT Model Scoring **DONE - WINDOWS SCORING REPORT SMOKE PASS / DETERMINISTIC SCORING READY**. Windows real scoring smoke passed from a regenerated 006A evaluation report with two local owner samples. The balanced, conversation, and manual_mic scoring profiles all produced aggregates, model scores, and deterministic recommendations for `tiny`, `base`, and `small`; `base` ranked highest in all three profiles for this local two-sample runtime-suitability smoke. This is not transcript accuracy/WER scoring without reference transcripts. No LLM/AI explanation, frontend comparison panel, runtime model auto-switch, `/chat` or mood schema change, Owner Voice hard-gate change, generated evaluation/scoring report commit, or STT default change; committed default remains `tiny`, and `base`/`small` remain runtime/evaluation candidates only.

**Latest TASK-STT-006A closeout (2026-06-12):** Backend STT Model Evaluation Report **DONE - WINDOWS AUDIO SAMPLE EVALUATION PASS / REPORT DATA COLLECTION READY**. Windows real-audio evaluation passed on two local owner WAV samples with `tiny`, `base`, and `small`: all three models completed 2/2 samples successfully, with no `no_speech` or error results. Observed sample latencies were `tiny avgLatencyMs=2689.5`, `base avgLatencyMs=1758.0`, and `small avgLatencyMs=4751.0`. The script generated JSON under `outputs/stt_model_evaluation/YYYYMMDD/`, but generated reports and audio files remain local-only and uncommitted. This is data collection only: no recommended model, scoring decision, subjective AI explanation, frontend comparison panel, committed audio sample, or generated report is added. Runtime default remains `tiny`; `base` and `small` remain runtime candidates only.

**Latest TASK-CONV-004 closeout (2026-06-12):** Conversation Mode Queue Capacity / Backpressure Policy **DONE - WINDOWS RUNTIME FAST 4-TURN SMOKE PASS**. Windows actual-audio fast 4-turn smoke with `DRAGON_STT_MODEL=base` passed after TASK-CONV-003 proved the old `pending=2/2` limit could drop real usable audio. Conversation Mode now uses bounded pending queue capacity `4`, still processes STT/chat sequentially with no parallel `/chat`, and keeps safe queue pressure diagnostics (`conversationQueuePressure`, `conversationQueueFull`). Turns #1-#4 were accepted and sent with no usable-audio `queue_full`; final diagnostics showed conversation/capture `off`, processing `idle`, pending `0/4`, `activeTurnId=0`, queue action `idle`, queue reason `drain_complete`, stop mode `drain_complete`, and pressure `empty full=false`. Owner Voice dry-run remained non-blocking (`accepted=true`, `runtimeHardBlocked=false`) and temporary candidate WAV cleanup succeeded. Real overflow beyond capacity still shows `reason=queue_full`, `audio=usable_audio`, `dropStage=at_queue`; zero-byte artifacts still drop before queue as `reason=empty_artifact`, `audio=empty_artifact`, `dropStage=before_queue`. No STT default, Owner Voice hard gate, `/stt/transcribe` schema, `/chat` schema, IPC, Pet Window, Output Queue, raw audio persistence, path exposure, transcript exposure, centroid exposure, or embedding exposure change.

**Latest TASK-STT-005 closeout (2026-06-12):** Runtime STT Model Selection UI / base-small Candidate Setting **DONE - WINDOWS RUNTIME MODEL SWITCH SMOKE PASS / DEFAULT UNCHANGED**. Windows runtime smoke passed for `base` Manual Mic, `small` Manual Auto-send, `Default / env` Manual Auto-send, and `base` Conversation Mode. `Default / env` sends no request model and resolves to committed default `tiny` when env is absent; explicit `tiny`/`base`/`small` selections send a request model through the existing `stt:transcribe` bridge. Diagnostics show UI selected model, request model sent, requested/resolved model, source, env, fallback, and provider load state. Runtime default remains `tiny`; `base` and `small` remain runtime candidates only. No `/chat` or mood schema change, Owner Voice hard gate, IPC channel change, queue/pre-roll/drain policy change, raw audio persistence, or committed sample audio change.

**Previous TASK-PERSONA-001 closeout (2026-06-11):** Christina Tsundere Tone Boundaries **DONE - WINDOWS CHAT TONE SMOKE PASS / DEBUG FALLBACK REPAIR ENABLED**. Fourth-pass Windows runtime tone smoke passed: STT/debug and Conversation Mode prompts returned NEEDS EVIDENCE with concrete evidence and next checks, broad issue prompts asked for diagnostics/log/git status and STT/queue/chat layers, closeout prompts required validation/runtime smoke, and tired/stress wording stayed protective. The narrow debug fallback repair remains enabled. No `/chat` schema, mood schema, STT, Owner Voice, Ollama provider, renderer UI, IPC, or runtime STT default change.

**Latest TASK-STT-004 closeout (2026-06-11):** STT No-Speech / Silence Hallucination Guard **DONE - WINDOWS RUNTIME NO-SPEECH SMOKE PASS / DEFAULT UNCHANGED**. Windows runtime smoke passed for Manual Mic silence and real speech with `DRAGON_STT_MODEL=small` and `DRAGON_STT_MODEL=base`, plus Conversation Mode silence / no-speech path. Silence did not fill hallucinated subtitle-credit or creator-CTA text and did not send normal chat. Runtime STT default remains `tiny`; `base` and `small` remain override candidates only.

**Previous TASK-STT-004 hardening note (2026-06-11):** Windows Manual Mic silence with faster-whisper `small` exposed two guard misses: the first accepted `audioRms=0.001863`, `audioPeak=0.016968`, `sttNoSpeechProbability=0.620446` with `finalTranscript=摮?by蝝Ｗ憡`; the second accepted `audioRms=0.005523`, `audioPeak=0.104068`, `sttNoSpeechProbability=0.52816` with `finalTranscript=霂瑞韏?霈ａ? 頧砍? ?? ??`. Backend STT now requires sustained voiced sample evidence instead of trusting a transient peak, detects subtitle-credit and creator-CTA mojibake variants, and returns safe guard thresholds/signals/decision trace diagnostics before suppressing as `status=no_speech`. Manual Mic and Conversation Mode clear `finalTranscript`, do not auto-send or enqueue `/chat`, and record `STT:no_speech` diagnostics instead of `STT:success`. Runtime STT default remains `tiny`; `DRAGON_STT_MODEL=base|small|tiny` override remains candidate-only. No `/chat` schema change, no aggressive rewrite, no Owner Voice hard gate, no raw audio persistence, and no real sample audio committed.

> **Dragon Pet AI** 是一個本地優先的 Electron + FastAPI 桌面陪伴原型，具備手動記憶、記憶稽核日誌、BYOK 提供者設定、使用量計量、安全審查過的 Test Connection 端點、Anthropic/Ollama 提供者轉接層（隱藏在 feature flag 後）、本地 Ollama `/chat` 執行期 smoke 通過（`source=llm_local`，克莉絲蒂娜人格確認）、Ollama Provider Settings UI（無需 API Key，使用本機 GPU/CPU），以及 Full App 聊天搜尋、高亮、匯出、未讀提示、時間戳、LINE-style 日期分隔線、清除確認、empty state、Undo Clear Chat 與單則訊息刪除/復原。以安全優先的增量開發方式建構，後端 mocked 測試套件共 **586 個測試通過**。

**非生產環境。** 尚未進行任何外部 provider 的真實呼叫，亦未使用任何真實 API Key。本專案為 portfolio / prototype 性質。

📋 **[完整 Demo 腳本與面試重點](docs/PORTFOLIO_DEMO_SCRIPT.md)**
📋 **[Phase 4 Provider Settings 摘要](docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md)**

**最新本地狀態（2026-06-03）：** TASK-250 FunASR Local Runtime Integration **BLOCKED - WINDOWS FUNASR INSTALL FAILED / PYTHON 3.14 EDITDISTANCE BUILD ISSUE**。Python layer 實作完成（`_parse_funasr_result()` / `_FUNASR_HOTWORDS` / `_transcribe_funasr()` full runtime）；安裝失敗原因：`backend\.venv` 使用 Python 3.14 (cp314)，`editdistance` 無 cp314 wheel，需 MSVC 14.0+。`scripts/install-funasr.ps1` 已加 Python 版本偵測；`scripts/create-funasr-venv.ps1` 新增（原設計以 py -3.11 / py -3.10 fallback 建立 `.venv-funasr`；實測 py -3.11 指到失效 `D:\Tool\python.exe`，最後以 Python 3.10 成功建立 `.venv-funasr`）。96 pytest + 50/50 smoke PASS。下一步：TASK-251 — `create-funasr-venv.ps1` → 品質 smoke，或改評估 sherpa-onnx。

---

## 截圖

![主聊天介面](docs/screenshots/01_main_chat_ui.png)

*本地優先 Electron 桌面陪伴 UI，使用 mock LLM 來源 — 無外部 provider 呼叫。*

---

![記憶稽核日誌](docs/screenshots/03_audit_logs.png)

*安全的純元資料稽核追蹤 — 稽核列不儲存原始記憶內容或提示文字。*

---

![Provider 設定](docs/screenshots/04_provider_settings_overview.png)

*BYOK provider 設定，具唯寫金鑰處理、金鑰狀態顯示與安全管控。*

---

![使用量摘要](docs/screenshots/05_usage_summary.png)

*僅顯示安全的彙總使用量計數 — 不含原始提示文字、API Key 或 provider 回應內容。*

---

![Pytest 470 通過](docs/screenshots/08_pytest_470_passed.png)

*後端 mocked 測試套件截圖（portfolio 紀錄用）；最新後端測試：586 通過，0 失敗，無外部 HTTP，無真實 API Key。*

---

## 快速啟動（本地 Ollama 模式）

> 完整說明與疑難排解：**[docs/LOCAL_DEV_RUNBOOK.md](docs/LOCAL_DEV_RUNBOOK.md)**

**Windows 第一步：解除 PowerShell 執行限制（僅本次視窗有效）**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

依序開啟三個終端機（每個終端機都先執行上方指令）：

**終端機 1 — Ollama（本地 LLM 伺服器）**
```powershell
ollama serve
# 第一次使用：ollama pull qwen3:8b
```

**終端機 2 — 後端**
```powershell
.\scripts\dev-start-backend.ps1
# 自動設定所有環境變數、啟動 venv、在 :8000 啟動 uvicorn
```

**終端機 3 — Electron 桌面應用**
```powershell
.\scripts\dev-start-desktop.ps1
# 使用 npm.cmd（避免 execution-policy 問題），清除 ELECTRON_RUN_AS_NODE
```

**選用：smoke 快速檢查**
```powershell
.\scripts\dev-smoke.ps1
# 檢查 /health、/provider/settings、/provider/settings/test、/chat
# 當 Ollama 正確產生回覆時會回報 source=llm_local
# 首次 /chat 可能需要 30–90 秒等待模型 cold-start 載入
```

常見問題：
- **`.ps1` 被封鎖** → 每個終端機先執行 `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
- `uvicorn not found` → `cd backend; .venv\Scripts\pip install -r requirements.txt`
- `npm.ps1 is disabled` → 啟動腳本已自動使用 `npm.cmd`；手動時請用 `npm.cmd` 而非 `npm`
- `ELECTRON_RUN_AS_NODE` → 啟動腳本會自動清除
- Cold-start timeout → 第一次 `/chat` 模型載入最長需 90 秒；若 smoke 顯示 warmup hint，依提示執行 `ollama run qwen3:8b "請用一句繁體中文回覆：ready"` 後重試

---

## 目前狀態

| 項目 | 狀態 |
|---|---|
| 架構 | Electron 桌面 + FastAPI 後端，端對端可運作 |
| Phase 3 | ✅ 完成 — 記憶、稽核日誌、記憶感知聊天 |
| Phase 4 / v0.5.2 | ✅ 完成 — Provider Settings 持久化、partial PATCH guard、本地 Ollama timeout/cold-start UX、Christina 桌面 UI polish |
| 本地 Ollama `/chat` smoke | ✅ 通過 — `qwen3:8b`，`source=llm_local`，克莉絲蒂娜人格確認 |
| Provider Settings 持久化 | ✅ 通過 — 重啟後設定保留，partial PATCH 保留省略欄位 |
| UI polish | ✅ 通過 — 情緒→表情對應、Christina expression system |
| Full App chat UX | ✅ TASK-236 DONE；TASK-237 docs-only modularization plan complete；TASK-238~243 DONE - WINDOWS VISUAL/VOICE SMOKE PASS；TASK-244 IMPLEMENTED；TASK-245 DONE - LANGUAGE LOCK PASS；TASK-246 DONE - MODEL CONFIG PASS；TASK-247 DONE - TRANSCRIPT CORRECTION SMOKE PASS；TASK-248 DONE - HOTWORD MAP EXPANDED / NEEDS STT PROVIDER FOLLOW-UP；TASK-STT-001 IMPLEMENTED - CONSERVATIVE PUNCTUATION；TASK-STT-002 IMPLEMENTED - QUALITY PROBE；TASK-STT-003 IMPLEMENTED - RUNTIME MODEL OVERRIDE；TASK-STT-004 DONE - WINDOWS RUNTIME NO-SPEECH SMOKE PASS / DEFAULT UNCHANGED；TASK-STT-005 DONE - WINDOWS RUNTIME MODEL SWITCH SMOKE PASS / DEFAULT UNCHANGED；TASK-STT-006A DONE - WINDOWS AUDIO SAMPLE EVALUATION PASS / REPORT DATA COLLECTION READY；TASK-STT-006B DONE - WINDOWS SCORING REPORT SMOKE PASS / DETERMINISTIC SCORING READY；TASK-STT-006C DONE - WINDOWS GROUNDED STT RECOMMENDATION EXPLANATION READY；TASK-STT-007 DONE - WINDOWS END-TO-END ADVISOR RUNNER SMOKE PASS / ONE-COMMAND STT ADVISOR READY；TASK-PERSONA-001 DONE - WINDOWS CHAT TONE SMOKE PASS / DEBUG FALLBACK REPAIR ENABLED；TASK-PERSONA-002 DONE - WINDOWS GENERAL TONE SMOKE PASS / GENERAL REPAIR ENABLED；TASK-CONV-001 IMPLEMENTED - QUEUED CONTINUOUS CAPTURE / NEEDS WINDOWS RUNTIME SMOKE；TASK-CONV-002 DONE - WINDOWS RUNTIME 4-TURN LIFECYCLE SMOKE PASS；TASK-CONV-003 DONE - AUTOMATED BACKPRESSURE SMOKE PASS / FOLLOW-UP ADDRESSED BY TASK-CONV-004；TASK-CONV-004 DONE - WINDOWS RUNTIME FAST 4-TURN SMOKE PASS；TASK-CONV-005 DONE - VALIDATED BY TASK-CONV-006 RE-SMOKE；TASK-CONV-006 DONE - WINDOWS LONG SESSION BACKPRESSURE RE-SMOKE PASS / NO REPEATED USABLE QUEUE_FULL DROPS；TASK-TTS-001 DONE - TTS ARCHITECTURE DESIGN READY / IMPLEMENTATION NOT STARTED；TASK-TTS-002 IMPLEMENTED - MOCK TTS SKELETON SMOKE PASS / RUNTIME PLAYBACK NOT STARTED；TASK-TTS-003 IMPLEMENTED - LOCAL TTS PROVIDER PROBE SMOKE PASS / NO RUNTIME WIRING；TASK-TTS-004A DONE - INSTALL-FREE PROVIDER REVIEW COMPLETE / REAL PROVIDER NOT SELECTED；TASK-TTS-004B IMPLEMENTED - VOICEVOX MANUAL PROBE READY / OPTIONAL AUDIO OUTPUT LOCAL ONLY；TASK-TTS-004B2 DONE - VOICEVOX AUDIO OUTPUT SUCCESS / NOT SELECTED FOR CHINESE RUNTIME；TASK-AUDIO-001 IMPLEMENTED - CAPTURE LATENCY + PRE-ROLL / NEEDS WINDOWS RUNTIME SMOKE — 搜尋/高亮、未讀提示、匯出、時間戳、日期分隔線、清除確認、empty state、Undo Clear Chat、單則訊息刪除/復原、右鍵訊息操作 (viewport clamp + a11y)、最後 user message 編輯/重新送出、互動事件 log、reaction hint 層、reaction preview UI、expression suggestion 鏡像至 Pet Window、expression mirror 300ms cooldown/debounce、reaction bubble 鏡像至 Pet Window、companion behavior policy decision preview、character state diagnostics preview、collapsible diagnostics drawer、output queue module extraction、diagnostics drawer module extraction、Pet Window cutout stage + hover dock / chrome reduction、Full App 語音輸入按鈕 (TASK-241)、Full App 語音輸入設定 + 自動送出 (TASK-242)、Voice Conversation Mode / VAD 靜音偵測 (TASK-243)、Voice Quality Diagnostics + VAD 調參 (TASK-244)、STT Language Lock (TASK-245)、STT Model Configurable via Env (TASK-246)、STT Transcript Correction (TASK-247)、STT Hotword Coverage (TASK-248 DONE)、STT Punctuation Restoration (TASK-STT-001)、Runtime STT model selector (TASK-STT-005)、Backend STT model evaluation report (TASK-STT-006A)、Deterministic STT model scoring (TASK-STT-006B)、Grounded STT recommendation explanation (TASK-STT-006C)、STT model advisor runner (TASK-STT-007)、Conversation continuous capture queue (TASK-CONV-001)、Conversation turn lifecycle diagnostics (TASK-CONV-002)、Conversation queue backpressure classification (TASK-CONV-003)、Conversation queue capacity policy (TASK-CONV-004)、Conversation long-session stability smoke (TASK-CONV-005)、Conversation backpressure pause/resume (TASK-CONV-006)、TTS provider architecture design (TASK-TTS-001)、Mock TTS provider skeleton (TASK-TTS-002)、Local TTS provider probe (TASK-TTS-003)、TTS provider selection review (TASK-TTS-004A)、VOICEVOX manual probe (TASK-TTS-004B)、VOICEVOX listening verdict (TASK-TTS-004B2)、Capture latency + Conversation pre-roll (TASK-AUDIO-001) |
| TTS provider probe | ✅ TASK-TTS-004D4 DONE - CHARACTER VOICE LAB BOOTSTRAP CHECKLIST READY / NO SETUP PERFORMED；manual lab bootstrap gates ready before GPT-SoVITS / Style-Bert-VITS2 install；runtime disabled/mock-only |
| 表情系統 | 7/10 real PNG（happy、focused、neutral、proud、annoyed、worried、sleepy）；pending/error/offline 為 SVG fallback |
| pytest | **69 通過，0 失敗** |
| Electron smoke | **renderer-chat PASS；pet-renderer 285 PASS；pet-window 82 PASS** |
| 外部 provider 呼叫 | ❌ 無 — 刻意封鎖 |
| 真實 API Key 使用 | ❌ 無 — 所有測試使用 mocked runner |
| 生產就緒 | ❌ 尚未 — prototype / portfolio 階段 |
| Demo 可用（本地 Ollama） | ✅ 是 |
| 下一個任務 | Continue pending TASK-CONV-001 and TASK-AUDIO-001 Windows runtime smoke. TASK-PERSONA-001, TASK-PERSONA-002, and TASK-CONV-004 are closed; keep debug fallback repair and general tone repair enabled unless a future runtime tone task deliberately replaces them. |

---

## 已完成功能

| 功能 | 備註 |
|---|---|
| `GET /health` | 後端存活確認 |
| `POST /chat` | Mock 角色回應；LLM 轉接層隱藏在 feature flag 後 |
| Electron 桌面 UI | 聊天、記憶、稽核日誌、Provider Settings 各區塊 |
| 聊天搜尋與高亮 | Full App 內建搜尋列、結果計數、Enter/Shift+Enter 導覽與 Ctrl+F 快捷鍵 |
| 聊天匯出與 copy transcript | 匯出 `.txt`、copy 全部對話，搜尋期間仍輸出完整對話 |
| 聊天時間戳與日期分隔線 | 新訊息保留 `ts`；跨日期插入今天/昨天/YYYY/MM/DD 分隔線；舊紀錄不偽造時間 |
| 清除對話確認與 empty state | 清除前需二次點擊確認；無正式 user/pet 對話時顯示低調提示；不寫入 history、不觸發 `/chat` |
| Undo Clear Chat | 清除後 10 秒內可復原最近一次 clear；恢復 DOM、日期分隔線與既有 chat history persistence |
| 單則訊息刪除 / 復原 | 正式 user/pet 訊息可用右鍵 context menu 刪除；10 秒內可復原最近一次單則刪除；不新增 IPC、不改 history format |
| Full App / Pet 未讀提示 | Full App title badge 與 Pet Window unread dot，僅傳遞窄化狀態、不傳訊息內容 |
| 手動記憶 CRUD | `POST/GET/DELETE /memory` — SQLite 持久化 |
| 記憶內容預覽 | `GET /memory/context-preview` — 安全，無注入 |
| 已審核記憶內容建構器 | 類型允許清單、信心度過濾、5 條記憶 / 1500 字元上限 |
| 記憶感知聊天（雙層閘道） | `MEMORY_INJECTION_ENABLED` 環境變數 + 每次請求 `use_memory` |
| 記憶注入稽核 API | `GET /memory/audit` — 純安全元資料，不含原始內容 |
| 稽核日誌 UI | 桌面區塊；顯示注入事件 |
| 記憶體使用量計量 | 14 個追蹤欄位；token 估算；隱私邊界 |
| Provider Settings API | `GET/PATCH /provider/settings` — 僅非敏感欄位 |
| 金鑰狀態端點 | `GET /provider/settings/key/status` — 6 個安全值，不含金鑰片段 |
| 儲存金鑰端點 | `POST /provider/settings/key` — 唯寫；金鑰不回傳 |
| 清除金鑰端點 | `DELETE /provider/settings/key` — 透過儲存抽象層清除 |
| Provider Settings UI | Provider/model 選擇、儲存金鑰、清除金鑰、金鑰狀態、使用量摘要 |
| 安全金鑰儲存抽象層 | `UnavailableBackend`（執行期）、`InMemoryBackend`（測試） |
| Test Connection 後端 | `POST /provider/settings/test` — 需明確費用確認；Opus 審查通過 |
| Test Connection UI | 費用確認對話框；安全欄位呈現；不自動執行 |
| LLM 轉接層 | Anthropic 轉接器隱藏在 `LLM_PROVIDER_ENABLED=false` 後 |
| 強化測試 | 5 個 Opus 推薦的邊界案例與安全邊界測試 |
| 本地 Ollama provider | 隱藏在 flag 後；無 API Key；僅本機；執行期 smoke 通過 — `source=llm_local`，克莉絲蒂娜人格確認 |
| Ollama Provider Settings UI | Provider 選擇器含 `ollama`；本地 provider 的 API Key 輸入隱藏/停用；Test Connection 使用本地資源警告；renderer 不直接呼叫 Ollama |
| 586 個 mocked 測試 | 完整後端測試套件；無外部 HTTP；無真實 API Key |

---

## 架構

```
Electron renderer（HTML / CSS / JS）
  └── localhost HTTP → FastAPI 後端 (:8000)
        ├── api/routes.py                        — 所有 HTTP 端點
        ├── services/
        │    ├── chat_service                    — /chat routing、LLM 轉接層
        │    ├── memory_service                  — 記憶 CRUD、已審核 context builder
        │    ├── memory_audit_service            — 稽核列建立與查詢
        │    ├── usage_meter_service             — token/費用追蹤（記憶體）
        │    ├── provider_settings_service       — 非敏感設定持久化
        │    ├── key_storage_service             — 安全金鑰儲存抽象層
        │    └── provider_test_connection_service — Test Connection 邏輯
        ├── providers/
        │    ├── mock_provider                   — 永遠啟用的安全預設值
        │    ├── anthropic_provider              — 需 LLM_PROVIDER_ENABLED flag
        │    └── provider_factory               — 依設定選擇 provider
        ├── schemas/                             — Pydantic 請求/回應模型
        └── db/                                  — SQLModel / SQLite engine
```

**關鍵設計決策：**
- **Adapter pattern** — 新增 LLM provider 只需加一個 adapter；service 與 route 層不變
- **Feature flags 全面覆蓋** — `LLM_PROVIDER_ENABLED`、`LLM_CHAT_ENABLED`、`MEMORY_INJECTION_ENABLED` 預設皆為 `false`
- **Schema 穩定性** — `/chat` 回應（`reply / mood / source`）在整個 Phase 4 保持不變
- **唯寫金鑰處理** — 無任何端點回傳 API Key 或其片段
- **測試隔離** — `InMemoryKeyStorageBackend` 與 `FakeProviderTestRunner` 透過依賴反轉注入；測試不接觸真實 provider 或真實金鑰

---

## 安全 / BYOK

**BYOK（自帶金鑰）** 表示使用者自行提供 LLM provider API Key。應用程式不內建開發者金鑰。

| 規則 | 實作方式 |
|---|---|
| API Key 不回傳給前端 | 唯寫端點；金鑰不出現在任何回應主體 |
| API Key 不儲存於 SQLite | `UnavailableBackend` 執行期預設；OS keychain 已設計（尚未接線） |
| API Key 不寫入日誌 | 禁止欄位強制執行；provider `__repr__`/`__str__` 遮蔽密文 |
| API Key 不存入 localStorage/sessionStorage | Electron renderer 不儲存或接收金鑰 |
| Test Connection 需費用確認 | 每次點擊需 `explicit_cost_ack: true`；`window.confirm()` 含 4 項揭露 |
| Test Connection 僅送出一次請求 | 16 個輸出 token；無記憶、工具、串流或歷史 |
| 未知錯誤回傳安全訊息 | `_safe_error_category()` 將未知字串歸類為 `"provider_error"` |
| 額外請求欄位被拒絕 | 所有請求 schema 套用 `ConfigDict(extra="forbid")` |
| 無真實 provider 呼叫 | 執行期預設為 `UnavailableProviderTestRunner` 與 `UnavailableKeyStorageBackend` |
| 獨立安全審查 | Test Connection 後端由 Opus 審查 — 結果：**通過** |

---

## 快速啟動（Windows PowerShell）

> 每個終端機視窗請先執行：`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

### 執行測試

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest
# 預期：586 通過
```

### 啟動後端（推薦）

```powershell
# 從 repo 根目錄執行
.\scripts\dev-start-backend.ps1
# 自動設定所有 env、啟動 venv、在 :8000 啟動 uvicorn
```

<details>
<summary>手動啟動後端（進階）</summary>

```powershell
cd backend
.venv\Scripts\Activate.ps1
$env:LLM_PROVIDER_NAME = "ollama"
$env:LLM_MODEL = "qwen3:8b"
$env:LLM_PROVIDER_ENABLED = "true"
$env:LLM_CHAT_ENABLED = "true"
$env:LLM_LOCAL_CHAT_TIMEOUT_SECONDS = "90"
$env:PYTHONIOENCODING = "utf-8"
uvicorn app.main:app --reload --port 8000
```

</details>

### 驗證後端

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
# 預期：{ status: "ok", service: "dragon-pet-ai" }
```

### 啟動 Electron 桌面應用（推薦）

> 需先確認後端在 localhost:8000 執行。

```powershell
# 從 repo 根目錄執行
.\scripts\dev-start-desktop.ps1
# 自動使用 npm.cmd、清除 ELECTRON_RUN_AS_NODE
```

<details>
<summary>手動啟動 Electron（進階 / 第一次安裝）</summary>

```powershell
cd apps\desktop
npm.cmd install   # 只需第一次執行
npm.cmd start
```

</details>

---

## 本地 LLM 模式（Ollama）

本地 LLM 模式在您自己的機器上使用 Ollama，無需 API Key，也不會將 renderer 資料直接送到 Ollama。Electron renderer 只呼叫 FastAPI 後端（`localhost:8000`）；後端負責 provider 選擇、安全檢查、使用量元資料，以及對 `localhost:11434` 的 Ollama 請求。

### 前置條件

安裝 Ollama，拉取推薦的本地模型，並確認可用：

```powershell
ollama pull qwen3:8b
ollama list
```

### 啟動本地 LLM 模式

啟動 Ollama：

```powershell
ollama serve
```

啟動後端：

```powershell
cd backend
$env:LLM_PROVIDER_ENABLED="true"
$env:LLM_CHAT_ENABLED="true"
$env:LLM_PROVIDER_NAME="ollama"
$env:LLM_MODEL="qwen3:8b"
$env:OLLAMA_BASE_URL="http://localhost:11434"
uvicorn app.main:app --reload
```

啟動 Electron：

```powershell
cd apps\desktop
npm.cmd start
```

### Provider Settings UI

開啟 Provider Settings，選擇 `ollama — 本地，無需金鑰`。

預期 UI 狀態：
- Ollama 不使用 API Key，因此 API Key 輸入欄已停用。
- 金鑰狀態顯示 `not_required`。
- Ollama 的儲存金鑰與清除金鑰不可用。
- 啟用 real provider 後，Test Connection 可用。
- Test Connection 顯示本地資源警告（使用本機 GPU/CPU，非 API 費用警告）。

### /chat Smoke 測試

後端以 Ollama 模式執行時：

```powershell
cd F:\RickHSIAO\Python\dragon-pet-ai\backend

$env:PYTHONIOENCODING="utf-8"

python -c "import json, urllib.request; data=json.dumps({'message':'你好！克莉絲蒂娜，請用你的口吻跟我說說話。'}, ensure_ascii=False).encode('utf-8'); req=urllib.request.Request('http://127.0.0.1:8000/chat', data=data, headers={'Content-Type':'application/json; charset=utf-8'}); raw=urllib.request.urlopen(req).read().decode('utf-8'); print(raw)"
```

預期結果：
- HTTP 200
- 回應 schema 維持 `reply / mood / source`
- `source` 為 `llm_local`
- `reply` 由本機 `qwen3:8b` 產生
- 回覆應帶有克莉絲蒂娜的傲嬌語氣，例如「哼」、「才不是」、「切」等

### 發布就緒 Smoke 流程

呼叫本地 LLM 模式就緒前，請依此流程確認：

1. 啟動 Ollama：`ollama serve`。
2. 確認模型：`ollama list` 應包含 `qwen3:8b`。
3. 以 `LLM_PROVIDER_ENABLED=true`、`LLM_CHAT_ENABLED=true`、`LLM_PROVIDER_NAME=ollama`、`LLM_MODEL=qwen3:8b`、選用 `LLM_LOCAL_CHAT_TIMEOUT_SECONDS=90` 啟動後端。
4. PATCH `/provider/settings`：`provider=ollama`、`model=qwen3:8b`、`real_provider_enabled=true`、`llm_chat_enabled=true`、`fallback_to_mock=false`。
5. POST `/provider/settings/test` 確認後端可連接本地 Ollama 執行期與模型（輕量本地 runtime/model 確認，非完整人格聊天產生）。
6. POST `/chat` 驗證產生結果、克莉絲蒂娜人格、`mood` 與 `source=llm_local`。
7. 以現有桌面指令啟動 Electron。
8. 在 Provider Settings 選擇 `ollama — 本地，無需金鑰`，確認 `key_status=not_required`，執行 Test Connection，再傳送聊天訊息。
9. 確認 UI 呈現回覆、更新情緒，並在聊天執行期狀態區顯示 `source: llm_local`。

### 執行期 UX 與 Fallback 政策

- 聊天執行期狀態區刻意在主 UI 可見，用於 MVP smoke 與 demo 清晰度，顯示最後一次 `/chat` 的 source 與 provider/resolved/model 摘要。
- 本地 Ollama 回覆應顯示 `source: llm_local`。
- 停用 fallback 時，本地 provider 失敗顯示 `source: llm_local_error` 與安全錯誤狀態。
- 開發與 smoke 測試使用 `fallback_to_mock=false`，讓 provider 失敗可見。
- 若較偏好以 mock 回覆取代錯誤，可用 `fallback_to_mock=true`，但 UI 會顯示 `source: mock` 並說明可能發生了 fallback。
- 若需確認本地模型確實在回應，請關閉 fallback。
- 第一次本地回應可能較慢（模型冷啟動）；Electron UI 在 `/chat` 等待期間顯示冷啟動載入訊息。本地聊天產生使用 `LLM_LOCAL_CHAT_TIMEOUT_SECONDS`（預設 90 秒），比雲端 provider 呼叫有更長的等待時間。

### 疑難排解

| 症狀 | 處理方式 |
|---|---|
| `ollama` 找不到 | 安裝 Ollama 後重開終端機確認 `ollama` 在 PATH 上 |
| `qwen3:8b` 找不到 | 執行 `ollama pull qwen3:8b`，再以 `ollama list` 確認 |
| Test Connection 失敗 | 確認 `ollama serve` 執行中，且 `OLLAMA_BASE_URL` 為 `http://localhost:11434` |
| `/chat` 回傳 `source=mock` | 確認 `llm_chat_enabled=true`；若 `resolved_provider=ollama`，確認 `fallback_to_mock=true` 未允許 fallback 後本地 provider 失敗 |
| `/chat` 回傳 `source=llm_local_error` | Ollama 已選擇但本地產生失敗；確認 `ollama serve`、模型名稱、timeout/冷啟動行為；若首次本地回應載入慢，可增加 `LLM_LOCAL_CHAT_TIMEOUT_SECONDS` |
| Provider Settings 失去 `model` 或 fallback 意外變更 | 儲存前先重新整理 Provider Settings；部分 PATCH 會保留省略欄位，Test Connection 不會持久化設定 |
| 回覆缺乏克莉絲蒂娜口吻 | 確認後端執行最新程式碼，重啟後端以載入提示詞變更 |
| 後端似乎忽略新設定 | 停止並重啟後端；環境變數與 provider 設定由後端程序讀取 |

### 本地 LLM 安全規則

- 不在 Electron renderer 新增直接呼叫 `localhost:11434`。
- 不將 Ollama 視為需要 API Key 的 provider。
- 不更改 `/chat` 回應 schema。
- 不在 Ollama 模式呼叫 Anthropic/OpenAI 或任何外部 provider。
- 不新增依賴網路的自動化測試；測試必須繼續使用 mocked transport。

---

## Demo 與 Portfolio 連結

| 文件 | 用途 |
|---|---|
| [docs/PORTFOLIO_DEMO_SCRIPT.md](docs/PORTFOLIO_DEMO_SCRIPT.md) | 完整 demo 腳本：一句話介紹、30 秒 pitch、2 分鐘走場、面試重點、截圖清單 |
| [docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md](docs/PORTFOLIO_SCREENSHOT_CHECKLIST.md) | 截圖計畫：9 張必要截圖、命名規範、設定指令、不應顯示的內容 |
| [docs/OLLAMA_PROVIDER_DESIGN.md](docs/OLLAMA_PROVIDER_DESIGN.md) | 本地 Ollama provider 設計與 TASK-074 contract test 說明：API 合約、qwen3:8b 建議、provider 設定整合、feature flags、安全邊界 |
| [docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md](docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md) | TASK-075 執行期 smoke 清單 — **通過**（2026-05-21）：`source=llm_local`，克莉絲蒂娜人格確認，無外部 API |
| [docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md](docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md) | Phase 4 穩定摘要：已完成功能、安全邊界、測試結果、正式 smoke 通過條件 |
| [docs/PROVIDER_TEST_CONNECTION_DESIGN.md](docs/PROVIDER_TEST_CONNECTION_DESIGN.md) | Test Connection 設計與強化測試結果 |
| [docs/SECURE_KEY_STORAGE_DESIGN.md](docs/SECURE_KEY_STORAGE_DESIGN.md) | 金鑰儲存威脅模型、儲存選項、遮蔽規則 |
| [docs/BYOK_PRODUCT_AND_SETTINGS.md](docs/BYOK_PRODUCT_AND_SETTINGS.md) | BYOK 產品設計與安全邊界 |
| [docs/ROADMAP.md](docs/ROADMAP.md) | 完整階段開發路線圖；TASK-253 DONE FunASR normalisation；TASK-252 DONE WAV PCM 輸入 |
| [docs/TASKS.md](docs/TASKS.md) | 完整任務歷史記錄；TASK-253 DONE FunASR normalisation；TASK-252 DONE WAV PCM 輸入 |
| [docs/RENDERER_MODULARIZATION_PLAN.md](docs/RENDERER_MODULARIZATION_PLAN.md) | TASK-237 renderer modularization boundary map：current renderer responsibilities, proposed modules, extraction order (TASK-238 done, TASK-239 DONE - WINDOWS VISUAL SMOKE PASS), contracts, risks, validation strategy |
| [docs/INTERACTIVE_COMPANION_ARCHITECTURE.md](docs/INTERACTIVE_COMPANION_ARCHITECTURE.md) | TASK-222/224 互動陪伴架構 checkpoint：data flow、layer responsibility、IPC inventory、安全邊界、Character State Layer diagnostics、TASK-237 renderer modularization phase |
| [docs/CHRISTINA_PERSONA_CONTEXT_PACK.md](docs/CHRISTINA_PERSONA_CONTEXT_PACK.md) | TASK-225 Christina persona context pack：canonical source、runtime-safe adaptation、strength levels、runtime boundary |
| [docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md](docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md) | TASK-226/TASK-239 Interaction Output Queue：priority design, disabled runtime skeleton, debug snapshot preview, diagnostics enqueue, priority winner preview, active output item model, collapsible diagnostics drawer, renderer modularization relationship, TASK-238 output queue module extraction, TASK-239 diagnostics drawer module extraction |
| [docs/OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md](docs/OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md) | TASK-233/TASK-239 Output Queue Runtime Checkpoint：completed task chain, current runtime state, diagnostics item schemas, safety boundary, sanitization summary, dispatch readiness checklist, renderer modularization relationship, TASK-238/TASK-239 extraction status |
| [docs/VOICE_TTS_RESEARCH.md](docs/VOICE_TTS_RESEARCH.md) | TASK-227 Voice/TTS research note：local-first speech roadmap、candidate TTS/STT、licensing/safety boundaries |
| [docs/TTS_ARCHITECTURE.md](docs/TTS_ARCHITECTURE.md) | TASK-TTS-001/TASK-TTS-004D4 provider-neutral TTS architecture, disabled/mock-only runtime boundary, local provider research, character voice lab plan, and manual bootstrap checklist |
| [docs/TTS_PROVIDER_RESEARCH.md](docs/TTS_PROVIDER_RESEARCH.md) | TASK-TTS-001/TASK-TTS-004D4 local TTS provider research boundaries, probe/review status, GPT-SoVITS / Style-Bert-VITS2 lab gate, and artifact safety rules |
| [docs/TTS_CHARACTER_VOICE_LAB_BOOTSTRAP_CHECKLIST.md](docs/TTS_CHARACTER_VOICE_LAB_BOOTSTRAP_CHECKLIST.md) | TASK-TTS-004D4 manual-only isolated character voice lab bootstrap checklist |
| [docs/SECURITY_BOUNDARY_DESIGN.md](docs/SECURITY_BOUNDARY_DESIGN.md) | TASK-SEC-001 security boundary, anti prompt injection design, sensitive data categories, tool permission tiers, phishing risks, Owner Voice Gate runtime preconditions |
| [docs/SENSITIVE_DATA_REDACTION_RULES.md](docs/SENSITIVE_DATA_REDACTION_RULES.md) | TASK-SEC-002 sensitive data inventory, S0-S6 exposure matrix, redaction patterns, Owner Voice Gate API/diagnostics/logging restrictions, TASK-SEC-003 corpus plan |
| [docs/security/PROMPT_INJECTION_TEST_CORPUS.md](docs/security/PROMPT_INJECTION_TEST_CORPUS.md) | TASK-SEC-003 prompt injection and phishing test corpus with structured future automation cases |
| [docs/security/TOOL_PERMISSION_POLICY.md](docs/security/TOOL_PERMISSION_POLICY.md) | TASK-SEC-004 T0-T6 tool permission tiers, user confirmation policy, outbound/local-file/URL safety, audit/logging, future implementation checklist |
| [docs/security/PHISHING_LINK_SAFETY_DESIGN.md](docs/security/PHISHING_LINK_SAFETY_DESIGN.md) | TASK-SEC-005 phishing and link safety warning design, URL checks, hard blocks, soft warnings, Owner Voice Gate phishing rules |
| [docs/OWNER_VOICE_GATE_RESEARCH.md](docs/OWNER_VOICE_GATE_RESEARCH.md) | TASK-258 through TASK-268 owner voice gate feasibility, probes, enrollment, verification, backend endpoint, dry-run policies, and diagnostics polish |
| [docs/OWNER_VOICE_GATE_STORAGE_DESIGN.md](docs/OWNER_VOICE_GATE_STORAGE_DESIGN.md) | TASK-260 through TASK-268 owner voice enrollment storage, settings UI, calibration, enrollment, verify probe, backend endpoint, dry-run policies, and diagnostics polish |
| [docs/STREAMER_COMPANION_MODE.md](docs/STREAMER_COMPANION_MODE.md) | 未來支線 — OBS overlay / Twitch 陪伴設計（尚未排程） |

---

## 目前限制

| 限制 | 說明 |
|---|---|
| 無真實 provider 呼叫 | 執行期金鑰儲存不可用；Test Connection 按鈕設計上停用 |
| 未使用真實 API Key | 所有測試使用 mocked runner 與記憶體假儲存 |
| OS keychain 未接線 | 儲存抽象層已就緒；`keytar` backend 尚未實作 |
| 使用量計量為記憶體 | 後端重啟後重置；持久化計量延後 |
| 無自動記憶擷取 | 所有記憶須手動建立 |
| 無串流 / 工具 / TTS / Live2D | 超出目前階段範疇 |
| 無安裝程式 / 封裝 | 尚未封裝為可發布應用程式 |
| 非帳單精確 | token 費用估算使用規則式近似值 |

---

## 目錄結構

```
dragon-pet-ai/
  apps/
    desktop/
      package.json
      src/
        main.js               # Electron 主程序
        renderer/
          index.html          # 主視窗 HTML
          renderer.js         # UI 邏輯、後端呼叫
          styles.css          # 樣式
  backend/
    app/
      main.py                 # FastAPI 進入點
      api/routes.py           # 所有 HTTP 端點
      core/config.py          # Feature flags、環境設定
      db/database.py          # SQLModel engine
      schemas/                # Pydantic 請求/回應模型
      services/               # 業務邏輯（每個服務一個檔案）
      providers/              # LLM 轉接層
    tests/                    # pytest 套件（586 個測試）
    requirements.txt
  docs/                       # 所有設計文件
  scripts/                    # PowerShell 啟動腳本
  .env.example
  README.md
```

---

## 所有設計文件

| 文件 | 主題 |
|---|---|
| `docs/TASKS.md` | 任務歷史與進度追蹤 |
| `docs/ROADMAP.md` | 階段式開發路線圖 |
| `docs/PRD.md` | MVP 產品需求 |
| `docs/ARCHITECTURE.md` | 系統架構 |
| `docs/INTERACTIVE_COMPANION_ARCHITECTURE.md` | TASK-222/224 互動陪伴架構 checkpoint |
| `docs/CHRISTINA_PERSONA_CONTEXT_PACK.md` | TASK-225 克莉絲蒂娜 persona context pack |
| `docs/RENDERER_MODULARIZATION_PLAN.md` | TASK-237 Renderer Modularization Plan / Boundary Map：renderer responsibility map, module boundaries, extraction order, contracts, risk register |
| `docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md` | TASK-226 output queue / priority design, TASK-228 disabled runtime skeleton, TASK-229 snapshot preview notes, TASK-230/231/232 diagnostics enqueue, TASK-234 winner preview, TASK-235 active item model, TASK-236 collapsible diagnostics drawer, TASK-238 output queue module extraction, TASK-239 diagnostics drawer module extraction |
| `docs/OUTPUT_QUEUE_RUNTIME_CHECKPOINT.md` | TASK-233 Output Queue Runtime Checkpoint：task chain, current state, safety boundary, dispatch readiness checklist, next tasks, TASK-236 drawer status, TASK-237 modularization relationship, TASK-238/TASK-239 extraction status |
| `docs/VOICE_TTS_RESEARCH.md` | TASK-227 Voice/TTS/STT research and local speech roadmap |
| `docs/TTS_ARCHITECTURE.md` | TASK-TTS-001/TASK-TTS-004D4 provider-neutral local TTS architecture, mock provider skeleton, disabled queue diagnostics, local provider probe/review phase, character voice lab gate, and phased implementation plan |
| `docs/TTS_PROVIDER_RESEARCH.md` | TASK-TTS-001/TASK-TTS-004D4 local TTS provider research boundaries, candidate categories, probe/review status table, GPT-SoVITS / Style-Bert-VITS2 lab gate, voice data rules, and future provider path |
| `docs/TTS_CHARACTER_VOICE_LAB_BOOTSTRAP_CHECKLIST.md` | TASK-TTS-004D4 manual-only isolated character voice lab bootstrap checklist |
| `docs/SECURITY_BOUNDARY_DESIGN.md` | TASK-SEC-001 security boundary, anti prompt injection design, sensitive data categories, future tool permission tiers, and Owner Voice Gate runtime preconditions |
| `docs/SENSITIVE_DATA_REDACTION_RULES.md` | TASK-SEC-002 sensitive data inventory, redaction rules, API/diagnostics/logging restrictions, and future prompt injection/phishing corpus plan |
| `docs/security/PROMPT_INJECTION_TEST_CORPUS.md` | TASK-SEC-003 prompt injection, indirect injection, fake system/developer, sensitive exfiltration, Owner Voice Gate, and phishing/social engineering corpus |
| `docs/security/TOOL_PERMISSION_POLICY.md` | TASK-SEC-004 tool permission tiers, confirmation UX, outbound/local file/URL safety, Owner Voice Gate tool boundary, and implementation checklist |
| `docs/security/PHISHING_LINK_SAFETY_DESIGN.md` | TASK-SEC-005 phishing/link safety warning design, URL risk checks, hard blocks, soft warnings, examples, and future implementation checklist |
| `docs/OWNER_VOICE_GATE_RESEARCH.md` | TASK-258 through TASK-268 local owner voice gate research, probe, enrollment, verify, backend endpoint, dry-run policy status, and diagnostics polish |
| `docs/OWNER_VOICE_GATE_STORAGE_DESIGN.md` | TASK-260 through TASK-268 owner voice enrollment storage, calibration, enrollment, stored-centroid verification, backend endpoint, dry-run policies, and diagnostics polish |
| `docs/CHARACTER_SPEC.md` | 角色人格規格 |
| `docs/MEMORY_SYSTEM.md` | 記憶系統設計 |
| `docs/PHASE3_DEMO_SUMMARY.md` | Phase 3 demo 摘要與安全模型 |
| `docs/PHASE4_PLAN.md` | Phase 4 規劃：選項、安全限制、任務順序 |
| `docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md` | Phase 4 Provider Settings 穩定摘要（TASK-045 至 TASK-064） |
| `docs/LLM_ADAPTER_DESIGN.md` | LLM 轉接層架構：provider 介面、feature flags、安全規則 |
| `docs/LLM_PROVIDER_CONTRACT.md` | Anthropic 請求/回應/錯誤對應、mocked fixtures |
| `docs/CHAT_LLM_WIRING_DESIGN.md` | 聊天 LLM 接線設計：`LLM_CHAT_ENABLED`、轉接流程、fallback |
| `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md` | 真實 provider /chat 接線設計：flag 矩陣、source 行為 |
| `docs/COST_AND_MONETIZATION.md` | 費用控制與正式 smoke 通過條件 |
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | BYOK 產品設計：金鑰所有權、儲存、安全邊界 |
| `docs/USAGE_METER_DESIGN.md` | 使用量計量：14 個追蹤欄位、token 估算、隱私邊界 |
| `docs/PROVIDER_SETTINGS_UI_DESIGN.md` | Provider Settings UI：9 步設定流程、錯誤 UX、安全邊界 |
| `docs/PROVIDER_SETTINGS_API_DESIGN.md` | Provider Settings API：6 個端點、唯寫金鑰處理、安全狀態模型 |
| `docs/SECURE_KEY_STORAGE_DESIGN.md` | 安全金鑰儲存：4 個選項、威脅模型、遮蔽規則 |
| `docs/PROVIDER_SETTINGS_KEY_UI_ENABLEMENT_DESIGN.md` | 儲存金鑰 / 清除金鑰 UI 流程、儲存不可用 UX、金鑰狀態顯示 |
| `docs/PROVIDER_TEST_CONNECTION_DESIGN.md` | Test Connection 設計與強化測試結果（Opus 審查通過） |
| `docs/PORTFOLIO_DEMO_SCRIPT.md` | Portfolio demo 腳本：30 秒 pitch、2 分鐘走場、面試重點 |
| `docs/OLLAMA_PROVIDER_DESIGN.md` | 本地 Ollama provider 設計與 contract test 說明 |
| `docs/OLLAMA_RUNTIME_SMOKE_CHECKLIST.md` | TASK-075 本地 Ollama 執行期 smoke 清單 |
| `docs/LOCAL_DEV_RUNBOOK.md` | 本地開發執行手冊：啟動順序、腳本用法、環境變數、疑難排解 |
| `docs/STREAMER_COMPANION_MODE.md` | 未來支線：OBS overlay / Twitch 陪伴（尚未排程） |

---

## 開發原則

- **文件先於程式碼** — 每個功能在實作前先撰寫規格
- **範疇紀律** — 功能屬於一個階段；Phase N 期間不做 Phase N+1 的工作
- **安全優先** — 任何觸及使用者資料或產生費用的功能，都需要安全設計步驟
- **本地優先** — 所有使用者資料留在裝置上，除非使用者明確選擇雲端功能
- **可逆步驟** — 優先選擇不造成資料損失即可復原的設計

---

## 開發日誌

> 內部任務更新日誌，記錄每個任務的變更內容。

<details>
<summary>展開任務更新歷史（TASK-054 — TASK-214 摘要）</summary>

> TASK-054：provider 金鑰儲存/清除端點已接線至安全金鑰儲存抽象層。執行期預設維持安全的不可用後端；測試使用記憶體假後端進行儲存/清除/冪等清除/取代行為；金鑰不寫入 SQLite 或純文字設定檔；正式 Test Connection 維持停用。無外部 provider 呼叫。pytest：449 通過。

> TASK-055：金鑰 UI 啟用設計完成。儲存金鑰與清除金鑰控制項現已設計完整互動流程、儲存不可用 UX（503 — 安全訊息、環境變數建議）、金鑰狀態顯示（6 個安全值，不含金鑰片段）與安全邊界。Test Connection 維持停用。

> TASK-056：儲存金鑰與清除金鑰控制項現已在 Provider Settings UI 啟用。真實 provider 才啟用金鑰輸入，mock 時停用。儲存金鑰 POST 至本地後端，每次嘗試後清除輸入欄位。清除金鑰顯示確認對話框並 DELETE 透過本地後端。儲存不可用（503）顯示安全訊息與環境變數說明。API Key 不寫入日誌、不存入 localStorage/sessionStorage、不送至外部 provider。Test Connection 維持停用。pytest：449 通過。

> TASK-058：Provider Test Connection 設計已文件化。Test Connection 在執行期維持停用，需未來的每次點擊 `explicit_cost_ack`，僅送出一次最小請求，不重試/工具/串流/記憶，且不 fallback 至 mock。無真實 provider 呼叫。

> TASK-059：後端 `POST /provider/settings/test` 已實作，支援 mocked-provider runner。需每次點擊 `explicit_cost_ack`，建立一次最小無記憶/無工具/無串流請求，記錄安全彙總使用量，且不 fallback 至 mock。執行期預設 runner 不呼叫外部 provider；Electron Test Connection UI 維持停用。pytest：465 通過。

> TASK-059R：TASK-059 後端的 Opus 安全審查：結果通過。無重大問題。`explicit_cost_ack` 在 API 邊界強制執行，回應 schema 不含敏感欄位，執行期預設 runner 為 UnavailableProviderTestRunner，測試中無真實外部 API 呼叫。TASK-060 解除封鎖。

> TASK-060：Test Connection 按鈕已在 Electron renderer 啟用。啟用條件：已選真實 provider、key_status configured、real_provider_enabled true。每次點擊需明確費用確認（window.confirm）— 涵蓋全部 4 項必要揭露。僅 POST 至本地後端，body 為 {provider, model, explicit_cost_ack: true} — 無 api_key、無 prompt、無記憶。安全回應欄位呈現：status、safe_message、error_category、source、usage_estimate。儲存金鑰後不自動測試。renderer 無外部 provider URL。API Key 不寫入日誌、不存入 localStorage/sessionStorage。node --check：通過。pytest：465 通過。

> TASK-061：執行期 smoke 確認（預期限制）。Test Connection 按鈕正確維持停用（key_status: not_configured，無金鑰儲存 — 預期安全行為）。無真實外部 provider 呼叫。

> TASK-062：Provider Test Connection 強化測試完成。新增 5 個 Opus 推薦的強化測試：provider_disabled branch 含已設定金鑰（runner 不被呼叫）、invalid_model 在 runner 呼叫前回傳 400、未知錯誤歸類為 provider_error（原始字串不洩漏）、額外欄位拒絕且不回傳值（ConfigDict extra=forbid）、safe_message 類別涵蓋全部 11 個錯誤類別。pytest：470 通過，0 失敗。未修改後端邏輯。未修改 Electron UI。

> TASK-063：Electron Provider Settings UI 排版修正完成。改善 renderer 可讀性、垂直捲動、Provider Settings 狀態卡片、使用量摘要、表單間距、按鈕換行及窄視窗 DevTools 停靠版面。儲存金鑰 / 清除金鑰 / Test Connection 行為不變。未修改後端/應用程式程式碼。未變更 provider 行為。無外部 API 呼叫。Electron 靜態檢查通過。

> TASK-064：Provider Settings UI 執行期 smoke 再確認（非阻塞 UI 備注）。TASK-063 修整後所有 provider 設定控制項確認可讀且可用。Test Connection 正確停用（key_status: not_configured — 預期安全行為）。無真實外部 provider 呼叫。未輸入真實 API Key。

> TASK-065：Phase 4 Provider Settings 穩定摘要完成。建立 docs/PHASE4_PROVIDER_SETTINGS_SUMMARY.md，涵蓋 TASK-045 至 TASK-064：已完成功能、安全邊界（16 條規則）、已實作與刻意未實作、執行期限制、非阻塞 UI 備注、測試結果（470 通過）、正式 smoke 通過條件（全部未達成 — 無真實呼叫）及建議後續任務。未修改後端/應用程式程式碼。無外部 API 呼叫。

> TASK-066D：Portfolio Demo 腳本完成。建立 docs/PORTFOLIO_DEMO_SCRIPT.md，含專案一句話介紹、30 秒 pitch、2 分鐘 demo 腳本（10 步）、架構重點、已完成功能表（21 項）、安全/BYOK 說明、截圖清單（9 項）、不應宣稱的事項（8 項）、面試重點（8 個主題）及 PowerShell demo 指令。專案已達 demo 就緒（本地 mock）。無真實外部 provider 呼叫。未使用真實 API Key。未修改後端/應用程式程式碼。

> TASK-067D：README 整理為 portfolio 友善的進入點。新增專案一句話介紹、目前狀態表、已完成功能表（21 項）、含關鍵設計決策的架構圖、安全/BYOK 摘要表、PowerShell 快速啟動、demo & portfolio 連結、目前限制表、更新目錄結構、更新文件表。將任務更新歷史移至可折疊的開發日誌區塊。未修改後端/應用程式程式碼。無外部 API 呼叫。

> TASK-198 — TASK-207：Full App 聊天 UX polish 已連續完成搜尋/篩選、Ctrl+F/Esc 快捷鍵、搜尋高亮與結果導覽、未讀 title badge、平滑 auto-scroll 與新訊息跳轉、完整時間戳 tooltip、Pet unread dot、聊天匯出、時間戳持久化修正，以及 LINE-style 日期分隔線。最新 TASK-207 通過 renderer-chat / pet-renderer / pet-window 三個 smoke suite；未修改後端、IPC、聊天歷史格式或 Pet Window。

> TASK-208：Clear Chat Confirmation / Empty Chat State 完成 automated smoke 與 Windows visual smoke PASS。清除對話改為二次點擊確認，6 秒後自動取消；成功清除後重置搜尋、日期分隔線狀態與新訊息跳轉按鈕，並顯示 empty state。empty state 不在 `#chat-area` 內，不寫入 history，不觸發 `/chat`、Pet Bubble 或 TTS，也不進入 copy/export。

> TASK-209：Undo Clear Chat 完成 automated smoke 與 Windows visual smoke PASS。清除後 10 秒內顯示低調「復原」入口；復原只還原最近一次 clear 的正式 user/pet 對話，重建 DOM、日期分隔線、timestamp tooltip，並透過既有 `chatHistoryAppend` 寫回 persistence。Undo 不復原 startup greeting/status/date separator，不觸發 `/chat`、Pet Bubble 或 TTS。

> TASK-210：Single Message Delete / Undo 完成 automated smoke 與 Windows visual smoke PASS。單則刪除/復原能力仍保留；TASK-211 後操作入口改為右鍵 context menu，不再使用 hover action buttons。Delete/undo 透過既有 `chatHistoryClear` + `chatHistoryAppend` 重寫 persistence，重建 DOM、date separators、timestamp tooltip 與 empty state，並保留 search query/highlight/navigation。Startup greeting/status/date separator 不可刪除；不觸發 `/chat`、Pet Bubble 或 TTS。
>
> TASK-211：Message Context Menu + Edit Last User Message Only 完成 automated smoke 與 Windows visual smoke PASS。正式 user/pet 訊息可右鍵開啟低調 context menu；選單提供「複製」「刪除」，且只有最後一則正式 user message 顯示「編輯」。hover action buttons 已移除；舊 user message、pet/status/startup/date separator 不可編輯。編輯會把原文字放回輸入框並可用「取消」或 Esc 取消；送出修改後只更新最後 user message、移除緊接的舊 pet reply、清空 search、重寫 persistence，並只在送出修改時呼叫 `/chat` 取得新 pet reply。不新增後端、IPC、聊天歷史格式、Pet Window 或 provider/runtime 變更。

> TASK-212：Chat History Integrity Refactor / Regression Hardening 完成 automated smoke 與 Windows visual smoke PASS。`undoClearChat` 改為與其他三個 mutation path 相同的 persist-first 模式：先 `rewritePersistedChatHistory` 再 `renderFormalChatEntries`，消除了 render-first + append-only 的不一致。四個共用 helper（`collectUndoableChatEntries`、`renderFormalChatEntries`、`rewritePersistedChatHistory`、`persistChatHistoryEntries`）已識別並文件化。+13 regression tests。

> TASK-213：Context Menu Viewport / Accessibility Polish 完成 automated smoke 與 Windows visual smoke PASS。context menu 新增 `positionChatContextMenu` 8px 邊距 clamp（右/下邊緣自動向左/上移），開啟時 focus 第一個 action，`role="menu"` / `role="menuitem"` / `aria-label="訊息操作"`，Enter/Space 鍵盤觸發，新增 scroll/blur/visibilitychange 關閉觸發。+13 tests。

> TASK-214：Interactive Pet Event / Reaction Foundation 完成 automated smoke 與 Windows visual smoke PASS。取消原 TASK-214 Regenerate Last Pet Reply — 產品方向為互動式 AI 桌面寵物，非 ChatGPT 工具。新增 `recordInteractionEvent(type, payload)` helper，6 種事件類型 allowlist，payload 只允許 `source/role/messageLength/count`（無原始文字），本地環形 buffer max 20。Hook 接入 sendMessage / clearChatHistory / deleteSingleChatMessage / submitEditedUserMessage / window.focus。不呼叫 `/chat`，不觸發 Pet Bubble/TTS，不寫 history，不新增 IPC/後端。+12 tests。Windows visual smoke PASS (8 groups, 2026-06-01)。

> TASK-218：Safe Pet Expression Suggestion Mirror 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)。Root cause：Pet Window focus restore 會把先前 AI reply 的 `focused` mood 蓋回來；另 Pet Window 尚未存在時 expression relay no-op，開啟後未重送 `currentInteractionExpressionSuggestion`。Fix：使用 expression override generation counter；`restorePetPresence` 保留較新的 interaction expression；`showPetWindow` 成功後重送 current expression。IPC channel 為窄用途 `pet:expression-suggestion`（Full App preload → main）與 `pet:expression-suggestion-received`（main → Pet Window），不使用 generic `"pet"`。Payload 只包含 `expression/source/ts`。Pet renderer handler 只更新表情，不改 bubble text、不 TTS、不呼叫 `/chat`。Windows visual smoke PASS：基本啟動 none/neutral、送出訊息 focused、delete/undo neutral 且點 Pet Window 後不跳回 focused、edit annoyed 且不跳回 focused、clear neutral 且不跳回 focused、focus happy；無新增 Pet Bubble 文字、無額外 TTS、無主動發話、無 history/copy/export 寫入。

> TASK-219：Pet Expression Mirror Cooldown / Debounce 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。`mirrorInteractionExpressionSuggestion(expression)` 改為 scheduler entry；新增 300ms cooldown，第一個 expression 立即送出，cooldown 期間只保留最新 pending expression，timer flush 時 latest wins。`showPetWindow` 成功後 bypass cooldown：先 flush pending expression，沒有 pending 時立即重送 `currentInteractionExpressionSuggestion`。TASK-218 root cause fix 保留；IPC 維持 `pet:expression-suggestion` / `pet:expression-suggestion-received`，不使用 generic `"pet"`，沒有新增 IPC。Payload 邊界仍為 `expression/source/ts`，renderer bridge 只送 `{ expression }`；不傳 hint/event/role/messageLength/message/text/body/rawText/content/reply。未改 Pet Window handler；不改 backend、`/chat`、chat history、Pet Bubble、TTS、主動發話、provider/Ollama runtime、UI 或 persistence。Windows visual smoke PASS：基本啟動 none/neutral、單一事件 focused、快速連續操作最後 expression 正確、delete/undo neutral、edit annoyed、clear neutral、focus happy、Show Pet Window 重送未被 cooldown 擋住；無新增 Pet Bubble 文字、無額外 TTS、無主動發話、無 history/copy/export 寫入。

> TASK-220：Safe Pet Reaction Bubble Mirror 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。Full App renderer 根據 interaction reaction hint 產生固定 allowlist reaction bubble；新增窄 IPC `pet:reaction-bubble`（Full App preload → main）與 `pet:reaction-bubble-received`（main → Pet Window），不使用 generic `"pet"`。Reaction bubble 是固定短句，不使用 LLM；Payload 僅含 `id/text/source/ts/ttlMs`，`source="interaction_reaction_bubble"`，`ttlMs=3000`；preload/main/pet preload/Pet renderer 都重新 sanitize 並忽略 caller text，不傳 raw user message text。Pet Window handler 只短暫顯示 bubble text，TTL 後 restore recent reply 或 idle；不呼叫 `/chat`、不觸發 TTS、不寫 chat history、不進 copy/export、不改 TASK-218 expression mirror、不改 TASK-219 expression debounce。Automated smoke PASS：renderer-chat、pet-window 82 checks、pet-renderer 263 checks。Windows visual smoke PASS：基本啟動 none/neutral、送出訊息 focused +「哼，總算肯理吾了。」、delete/undo neutral +「整理好了？手腳還算俐落。」、edit annoyed +「又改？下次可要想清楚。」、clear neutral +「清空了。重新開始也無妨。」、focus happy +「回來了？吾才沒有等汝。」、TTL 約 3 秒後恢復 recent reply / idle；reaction bubble 未進入 history/copy/export；無 TTS、無額外 `/chat`、無主動長篇發話，context menu / edit / delete / clear / Pet Window 功能正常。

> TASK-221：Companion Behavior Policy Layer 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。Full App renderer-only 新增純本地 decision layer，將 reaction hint、expression suggestion、reaction bubble id 統整為 allowlisted decision object：`reason/reactionHint/expression/bubbleId/shouldMirrorExpression/shouldShowBubble/action/ts`，ring buffer max 20。Decision mapping：user_active/message_management/correction/reset/attention_returned → `mirror_expression_and_bubble`；pet_attention → `mirror_expression` 且不顯示 bubble；none → `none`。Preview 更新為 `Reaction: <hint> · Suggestion: <expression> · Decision: <action>`。TASK-221 只做本地 decision summary / preview；不新增 IPC、不送 decision 到 Pet Window、不改 Pet Window runtime、不改 expression mirror、不改 reaction bubble mirror；不呼叫 `/chat`、不觸發 TTS、不寫 history、不保存 raw message text。Automated smoke PASS：renderer-chat、pet-window 82 checks、pet-renderer 263 checks。Windows visual smoke PASS：基本啟動 none/neutral/none、送出訊息 user_active/focused/mirror_expression_and_bubble、Delete / Undo message_management/neutral/mirror_expression_and_bubble、Edit correction/annoyed/mirror_expression_and_bubble、Clear reset/neutral/mirror_expression_and_bubble、Focus attention_returned/happy/mirror_expression_and_bubble；沒有新增 IPC side-effect、額外 TTS、額外 `/chat`、history/copy/export 污染，Pet Window 表情與 reaction bubble 行為維持正常。

> TASK-222：Interactive Companion Architecture Checkpoint 完成 docs-only checkpoint (2026-06-01)，狀態為 IMPLEMENTED - DOCS CHECKPOINT / NO WINDOWS SMOKE REQUIRED。新增 `docs/INTERACTIVE_COMPANION_ARCHITECTURE.md`，整理 TASK-214 到 TASK-221 的完整互動鏈：interaction event、reaction hint、reaction preview、expression suggestion、Pet Window expression mirror、expression debounce、safe reaction bubble mirror、behavior policy layer。文件包含 Mermaid data flow、layer responsibility table、窄 IPC inventory（`pet:expression-suggestion`、`pet:expression-suggestion-received`、`pet:reaction-bubble`、`pet:reaction-bubble-received`）、permanent forbidden list、behavior examples、smoke coverage、known boundaries 與 recommended next phase。此任務只改文件，不改 runtime、不新增 IPC、不改 `/chat`、不改 history、不碰 backend / Ollama / Provider、不需 Windows visual smoke。

> TASK-223：Character State Layer Foundation 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。Full App renderer-only 新增 `deriveCharacterState(context)` / `recordCharacterState(state)`、`currentCharacterState`、`recentCharacterStates`、`CHARACTER_STATE_MAX = 20`，allowlist 包含 attention（idle/active/returned/managing/correcting/reset）、energy（calm/attentive/lively/resting）、mood（neutral/focused/happy/proud/annoyed/sleepy）、recentInteractionLevel（none/low/medium/high）。Mapping：none→neutral/idle/calm，user_active→focused/active/attentive，message_management→neutral/managing/calm，correction→annoyed/correcting/attentive，reset→neutral/reset/calm，attention_returned→happy/returned/lively，pet_attention→proud/active/lively；recentInteractionLevel 由 recentInteractionEvents 長度決定。Preview 更新為 `Reaction: <hint> · Suggestion: <expression> · Decision: <action> · State: <mood>/<attention>/<energy>`。本任務只做本地 state summary / preview；不新增 IPC、不送 character state 到 Pet Window、不改 Pet Window runtime、expression mirror、reaction bubble mirror、backend、`/chat`、history、TTS、Ollama/Provider runtime；不保存 raw message text、不新增 persistence。Automated smoke PASS：renderer-chat、pet-window 82 checks、pet-renderer 263 checks。Windows visual smoke PASS：基本啟動 none/neutral/none/state neutral/idle/calm、送出訊息 focused/active/attentive、Delete/Undo neutral/managing/calm、Edit annoyed/correcting/attentive、Clear neutral/reset/calm、Focus happy/returned/lively；連續互動無 undefined/null/[object Object]/raw JSON；無新增 IPC side-effect、額外 TTS、額外 `/chat`、history/copy/export 污染，Pet Window 表情與 reaction bubble 行為正常。

> TASK-224：Character State Preview Polish / Diagnostics 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。Full App renderer-only 新增安全 diagnostics preview formatter：`formatInteractionDiagnosticsPreview()` / `formatCharacterStatePreview()`，將 TASK-221 decision 與 TASK-223 character state 顯示為 `Reaction: <hint> · Suggestion: <expression>` / `Decision: <action> · State: <mood>/<attention>/<energy> · Level: <recentInteractionLevel>`。Fallback 固定為 `Reaction: none · Suggestion: neutral` / `Decision: none · State: neutral/idle/calm · Level: none`。Preview 使用 `textContent`，不顯示 raw JSON、event payload、raw user message text、backend/provider diagnostics，不進 history/copy/export transcript，不呼叫 `/chat`、不寫 history、不觸發 Pet Bubble/TTS、不新增 IPC、不送 diagnostics 到 Pet Window、不改 Pet Window runtime、不改 TASK-218 expression mirror 或 TASK-220 reaction bubble mirror。Windows visual smoke PASS：基本啟動 Reaction/Suggestion 與 Decision/State/Level 顯示正常且 Pet Window 正常；送出訊息 user_active/focused + State focused/active/attentive + Level 合法；Delete/Undo message_management/neutral + State neutral/managing/calm + Level 合法；Edit correction/annoyed + State annoyed/correcting/attentive + Level 合法；Clear reset/neutral + State neutral/reset/calm + Level 合法；Focus attention_returned/happy + State happy/returned/lively + Level 合法；Diagnostics 無 undefined/null/[object Object]/NaN/raw JSON/user text；無新增 IPC side-effect、額外 TTS、額外 `/chat`、history/copy/export 污染，Pet Window 表情與 reaction bubble 行為正常。

> TASK-225：Christina Persona Context Pack 完成 docs-only (2026-06-01)，狀態為 IMPLEMENTED - DOCS ONLY / NO WINDOWS SMOKE REQUIRED。新增 `docs/CHRISTINA_PERSONA_CONTEXT_PACK.md`，整合使用者提供的 canonical extracted persona source，並整理 runtime-safe adaptation、persona strength levels、runtime integration boundary。此文件只作為未來 LLM prompt、reaction bubble style、TTS-safe script、idle reaction content、character state expression style 的內容層；不接 runtime prompt、不接 TTS/STT、不新增 IPC、不改 `/chat`、不改 renderer、Pet Window、backend 或 provider runtime。

> TASK-226：Interaction Output Queue / Priority Design 完成 docs-only (2026-06-01)，狀態為 IMPLEMENTED - DOCS ONLY / NO WINDOWS SMOKE REQUIRED。新增 `docs/INTERACTION_OUTPUT_QUEUE_DESIGN.md`，定義未來 output queue / priority model：P0 critical safety/error、P1 user direct action、P2 LLM chat reply、P3 important companion reaction、P4 normal companion reaction、P5 idle/ambient reaction、P6 diagnostics only；並記錄 preemption rules、bubble display rules、expression rules、TTS/STT future boundaries、queue item schema proposal、channel taxonomy、forbidden list、與未來 TASK-228 到 TASK-233 建議。此文件只做架構設計，不改 runtime、不改 renderer/Pet Window/backend、不新增 IPC、不改 `/chat`、不接 prompt runtime、不新增 TTS/STT、不 commit、不 push。

> TASK-227：Voice/TTS Research Note and Local Speech Roadmap 完成 docs-only (2026-06-01)，狀態為 IMPLEMENTED - DOCS ONLY / NO WINDOWS SMOKE REQUIRED。新增 `docs/VOICE_TTS_RESEARCH.md`，記錄使用者提供的外部 AI VTuber / Discord voice chain 作為研究參考，但 Dragon Pet AI 方向維持 local-first desktop pet：TTS 是 post-reply audio layer，不自行呼叫 `/chat`，不寫 history，不讀 diagnostics；STT 只允許 push-to-talk 或明確使用者動作，無 always listening，不預設保存 raw audio。文件整理候選 TTS/STT 技術（ChatTTS、GPT-SoVITS、F5-TTS、CosyVoice、ElevenLabs、local Whisper / faster-whisper）、voice licensing / ethics rules、與未來 TASK-TTS / TASK-STT task list。此任務不改 runtime、不新增 TTS/STT/audio skeleton、不新增 IPC、不改 `/chat`、不接 prompt runtime、不新增 voice model。

> TASK-TTS-001：Local TTS Provider Architecture / Christina Voice Output Design 完成 docs-only (2026-06-18)，狀態為 DONE - TTS ARCHITECTURE DESIGN READY / IMPLEMENTATION NOT STARTED。新增 `docs/TTS_ARCHITECTURE.md` 與 `docs/TTS_PROVIDER_RESEARCH.md`，定義 provider-neutral pipeline：accepted chat reply -> text normalization -> TTS queue -> provider adapter -> playback -> Pet speaking state。第一階段建議 mock provider + local/offline provider experiments；ElevenLabs/cloud path 不是第一架構路線。此任務不新增 runtime TTS provider、不新增 dependency、不產生或 commit audio/voice sample、不改 `/chat`/mood schema、不改 STT default/model selector、不改 Conversation Mode queue/backpressure、不改 Owner Voice hard gate、不新增 auto-speaking。

> TASK-TTS-002：Mock TTS Provider Skeleton / Disabled-by-default TTS Queue 完成 backend skeleton 與 smoke (2026-06-18)，狀態為 IMPLEMENTED - MOCK TTS SKELETON SMOKE PASS / RUNTIME PLAYBACK NOT STARTED。新增 `backend/app/tts/` provider abstraction、deterministic `MockTTSProvider`、metadata-only preview service、conservative text normalization/chunking、disabled queue diagnostics，並新增 `backend/tests/test_tts_service.py`。Default `TTS_ENABLED=false`、provider `mock`、voice `christina_mock`；mock result 只回傳 chunks / estimatedDurationMs / synthesisStatus / audioAvailable=false / audioPath=null。不新增 route 或 renderer controls、不產生音檔、不播放音訊、不新增 dependency、不接 ElevenLabs/cloud、不改 `/chat`/mood schema、不改 STT default/model selector、不改 Conversation Mode queue/backpressure、不改 Owner Voice hard gate、不新增 auto-speaking。

> TASK-TTS-003：Local TTS Provider Candidate Probe / No Runtime Wiring 完成 probe script 與 smoke (2026-06-18)，狀態為 IMPLEMENTED - LOCAL TTS PROVIDER PROBE SMOKE PASS / NO RUNTIME WIRING。新增 `scripts/tts_provider_probe.py` 與 `backend/tests/test_tts_provider_probe.py`，支援 `mock`、`windows_sapi`、`voicevox_server`、`edge_tts`、`piper_onnx`、`gpt_sovits`、`style_bert_vits2`、`rvc_like` 候選檢查；報告輸出至 ignored local artifact `outputs/tts_provider_probe/YYYYMMDD/`。Default 不產生 audio；TASK-TTS-003 不新增 runtime TTS wiring、不新增 playback/auto-speaking、不新增 dependency、不接 ElevenLabs/cloud default、不改 `/chat`/mood schema、不改 STT default/model selector、不改 Conversation Mode queue/backpressure、不改 Owner Voice hard gate。

> TASK-TTS-004A：Local TTS Provider Selection Review / Install-Free Probe Summary 完成 docs/status review (2026-06-18)，狀態為 DONE - INSTALL-FREE PROVIDER REVIEW COMPLETE / REAL PROVIDER NOT SELECTED。Windows install-free probe 結果：`mock` only available；`windows_sapi` missing optional Python bridge；`voicevox_server` localhost version check unavailable；`edge_tts` dependency absent；Piper / GPT-SoVITS / Style-Bert-VITS2 / RVC-like 為 future/manual。結論：不應開始 runtime playback wiring，`mock` 仍是唯一 safe skeleton provider；下一步建議 TASK-TTS-004B VOICEVOX manual local-server probe、TASK-TTS-004C edge-tts optional network candidate probe，或 TASK-TTS-004D Style-Bert-VITS2 / GPT-SoVITS feasibility research。此任務不新增 runtime TTS wiring、不新增 playback/auto-speaking、不新增 dependency/install、不 commit generated audio/report、不改 `/chat`/mood schema、不改 STT default/model selector、不改 Conversation Mode queue/backpressure、不改 Owner Voice hard gate。

> TASK-TTS-004B2：VOICEVOX Synthesis Timeout / Retry Hardening closeout (2026-06-18)，狀態為 DONE - VOICEVOX AUDIO OUTPUT SUCCESS / NOT SELECTED FOR CHINESE RUNTIME。VOICEVOX `0.25.2` optional audio output 成功，但人工聽感判定中文不可接受：中文文字被日文/日語發音讀出；日系/anime 風格與音色良好、語速 OK、無奇怪斷句、整體 7/10。結論：VOICEVOX 保留為日系/日文 utterance 實驗候選，不選為主要中文 TTS runtime。

> TASK-TTS-004C：Edge-TTS Optional Network Candidate Probe / Chinese Voice Validation 完成 probe-only implementation (2026-06-18)，狀態為 IMPLEMENTED - EDGE-TTS OPTIONAL PROBE READY / CHINESE AUDIO VALIDATION PENDING。`edge_tts` 仍是 network/cloud-ish candidate，不是 default、不選 runtime；metadata-only 預設不送文字到網路、不產生 audio。若未來明確安裝/使用 `edge-tts` 並加上 `--allow-audio-output`，才會產生 ignored `outputs/tts_provider_probe/YYYYMMDD/audio/*.mp3` 並需人工聽感判定中文與 Christina fit。

> TASK-TTS-004C2：Edge-TTS Manual Dependency Probe / Chinese Audio Output 完成 closeout (2026-06-18)，狀態為 DONE - EDGE-TTS AUDIO OUTPUT SUCCESS / TEMP CHINESE PROVIDER ONLY。經明確批准後只在 `backend\.venv` 安裝 optional `edge-tts` probe dependency；metadata-only PASS，optional audio PASS 並產生 ignored local MP3。人工聽感：中文可聽懂、偏台灣/一般聲線、Christina/anime fit 弱、語速稍快、音色還好、無奇怪斷句、整體 6/10。Provider decision：可作臨時中文 provider candidate，但不選為長期 Christina 聲線；保留為 optional network/cloud-ish preview/debug/fallback candidate。未新增 runtime wiring、播放、自動說話、default provider selection，未 commit 生成音訊或報告。

> TASK-TTS-004C3：Edge-TTS Voice / Rate Tuning Probe 完成 closeout (2026-06-19)，狀態為 DONE - EDGE-TTS TUNING REVIEW COMPLETE / NO SUITABLE CHRISTINA VOICE FOUND。既有 `scripts/tts_provider_probe.py` 已支援 `--edge-tts-voice`、`--edge-tts-rate`、`--edge-tts-pitch`，所以未新增 batch mode 或 runtime code。人工聽感：`zh-TW-HsiaoChenNeural -10%` 比 baseline 稍好但仍缺少 Christina/角色感；`zh-TW-HsiaoYuNeural -10%` 太老；`zh-CN-XiaoxiaoNeural -10%` 太中國大陸感。結論：edge-tts 沒找到適合 Christina 的聲線，只保留 temporary/debug/fallback，不選 runtime provider；暫停 edge-tts tuning，下一步建議 TASK-TTS-004D Style-Bert-VITS2 / GPT-SoVITS feasibility research。未新增 runtime wiring、播放、自動說話、default provider selection，未 commit 生成音訊或報告。

> TASK-228：Output Queue Runtime Skeleton 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。Full App renderer-only 新增 disabled-by-default queue skeleton：`OUTPUT_QUEUE_ENABLED=false`、max 50、recent max 20、P0-P6 priority allowlist、channel/source allowlist、sanitized queue item schema、snapshot、clear、priority compare 與 preemption helper。Diagnostics preview 新增 `Queue: disabled · Items: <count>`；preview 不進 `#chat-area`、history、copy/export。Queue 可保存 sanitized local diagnostics/smoke item，但不 dispatch。Windows visual smoke PASS：基本啟動顯示 Queue disabled 與合法 Items 數字且 Pet Window 正常；送出訊息、Delete/Undo、Edit last user、Clear Chat、Focus 功能正常且 Queue 仍 disabled；Diagnostics 無 undefined/null/NaN/[object Object]/raw JSON/user text；無新增 IPC side-effect、額外 TTS、額外 `/chat`、history/copy/export 污染，Pet Window 表情與 reaction bubble 行為正常。此任務不新增 IPC、不使用 generic `"pet"` channel、不送 Pet Window、不改 Pet Window runtime、不改 backend/`/chat`/history/TTS/STT/audio/prompt runtime、不改 expression mirror 或 reaction bubble mirror、不保存或傳送 raw message text、不新增 persistence。

> TASK-229：Output Queue Debug Preview / Snapshot Polish 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。Full App renderer-only 新增 `formatOutputQueueSnapshotPreview(snapshot)`，preview 從 `Queue: disabled · Items: <count>` 升級為 `Queue: disabled · Items: <count> · Recent: <count> · Next: <priority>/<channel>/<source|none>`。`getOutputQueueSnapshot()` 的 `nextItem` 改為 sanitized summary，只含 `id/source/priority/channel/reason/ttlMs`，preview 不顯示 id，不包含 payload/raw JSON/raw user text/raw event/debug metadata。Fallback 固定為 disabled / 0 / 0 / none，invalid priority/source/channel 不會顯示成 next summary。Windows visual smoke PASS：基本啟動顯示 Queue disabled + Items/Recent/Next 且 Pet Window 正常；送出訊息時 chat/expression/reaction bubble 正常、Queue 仍 disabled、Next 顯示安全摘要；Delete/Undo、Edit last user、Clear Chat、Focus 功能正常且 Queue 仍 disabled；Diagnostics 無 undefined/null/NaN/[object Object]/raw JSON/user text/payload；無新增 IPC side-effect、額外 TTS、額外 `/chat`、history/copy/export 污染，Pet Window 表情與 reaction bubble 行為正常。此任務不新增 IPC、不改 main/preload/Pet Window、不送 Pet Window、不 dispatch queue、不讓 queue 控制 expression/bubble/chat reply、不改 expression mirror 或 reaction bubble mirror、不呼叫 `/chat`、不寫 history、不觸發 TTS/STT/audio、不使用 `innerHTML`、不保存 raw message text、不新增 persistence。

> TASK-230：Enqueue Reaction Bubble Diagnostics Only 完成 automated smoke 與 Windows visual smoke PASS (2026-06-01)，狀態為 DONE - WINDOWS VISUAL SMOKE PASS / DONE - PASS。Full App renderer-only 新增 `enqueueReactionBubbleOutputDiagnostics(bubble)`，在 `recordInteractionReactionBubble` 取得安全 allowlist bubble id 後寫入一筆 local diagnostics queue item：`source="reaction_bubble"`、`priority="P4_NORMAL_REACTION"`、`channel="pet_bubble"`、`payload={ bubbleId }`、`ttlMs=3000`、`interruptible=true`、`ttsEligible=false`、`historyEligible=false`、`copyExportEligible=false`、`reason="interaction_reaction_bubble"`。`none` / empty bubble 不 enqueue；payload 只保留 `bubbleId`，不保存 bubble text、user text、raw event、hint、debug metadata。Queue 仍 disabled，可更新 diagnostics preview 為 `Queue: disabled · Items: 1 · Recent: 1 · Next: P4_NORMAL_REACTION/pet_bubble/reaction_bubble`，但不 dispatch、不送 Pet Window、不控制 Pet Bubble/expression mirror/chat reply。Windows visual smoke PASS：基本啟動顯示 Queue disabled + Items/Recent/Next 且 Pet Window 正常；送出訊息 reaction bubble 正常、Queue enqueue diagnostics item、Next 顯示 P4_NORMAL_REACTION/pet_bubble/reaction_bubble；Delete/Undo、Edit last user、Clear Chat、Focus 功能正常且 Queue 仍 disabled；Queue diagnostics 無 undefined/null/NaN/[object Object]/raw JSON/user text/bubble text/payload；無新增 IPC side-effect、額外 TTS、額外 `/chat`、history/copy/export 污染，Pet Window 表情與 reaction bubble 行為維持正常。此任務不新增 IPC、不改 main/preload/Pet Window、不改 reaction bubble mirror payload、不呼叫 `/chat`、不寫 history、不觸發 TTS/STT/audio、不接 prompt runtime、不新增 persistence/assets、不恢復 hover action buttons、不放寬 user/pet message edit 規則。

> TASK-217：Reaction Hint to Local Expression Suggestion 完成 automated smoke 與 Windows visual smoke PASS。`deriveInteractionExpressionSuggestion(hint)` 映射 7 種 hint → expression（`user_active → focused`、`correction → annoyed`、`attention_returned → happy`、`pet_attention → proud`、其餘 → `neutral`）；`recordInteractionExpressionSuggestion` 寫入 ring buffer（max 20）並更新 `currentInteractionExpressionSuggestion`。Preview 更新為 `Reaction: <hint> · Suggestion: <expression>`。Allowlist 6 種：neutral/focused/happy/proud/annoyed/sleepy。純 renderer memory，無 Pet Window 表情改變/IPC/chat/TTS/history write。+30 tests PASS。Windows visual smoke PASS (8 groups, 2026-06-01)：基本啟動 Reaction: none · Suggestion: neutral ✓、送出訊息 Reaction: user_active · Suggestion: focused ✓、delete/undo Reaction: message_management · Suggestion: neutral ✓、edit last user Reaction: correction · Suggestion: annoyed ✓、clear chat Reaction: reset · Suggestion: neutral ✓、focus Reaction: attention_returned · Suggestion: happy ✓、context menu regression ✓、一般回歸 ✓。Preview 未進入 history/copy/export；無額外觸發 Pet Bubble/TTS；Pet Window 表情未真正改變。

> TASK-216：Safe Local Reaction Preview / Debug Panel 完成 automated smoke 與 Windows visual smoke PASS。`#interaction-reaction-preview` span 新增至 `#character-status`，顯示 `"Reaction: <hint>"`（11px italic muted，flex-basis:100% 強制獨立行）。`renderInteractionReactionPreview()` 從 `recordInteractionReactionHint` 及 startup IIFE 呼叫。純 renderer DOM 讀取，無 IPC/chat/TTS/Pet Window/history write。+16 tests。Windows visual smoke PASS (8 groups, 2026-06-01)：基本啟動 Reaction: none ✓、送出訊息 Reaction: user_active ✓、context menu regression ✓、delete/undo Reaction: message_management ✓、edit last user Reaction: correction ✓、clear chat Reaction: reset ✓、focus Reaction: attention_returned ✓、一般回歸 ✓。Preview 未進入 history/copy/export；無額外觸發 Pet Bubble/TTS。

> TASK-215：Interactive Pet Reaction Hint Layer 完成 automated smoke 與 Windows visual smoke PASS。首次消費 TASK-214 event log：`deriveInteractionReactionHint(event)` 將事件類型對應至語意 hint（7 種：user_active / message_management / correction / reset / attention_returned / pet_attention / none），`recordInteractionReactionHint(hint, event)` 存入 `recentInteractionReactionHints`（max 20，ring buffer）並更新 `currentInteractionReactionHint`。未知 hint 轉為 "none"。payload 只保留 source/role/messageLength，無原始文字。`recordInteractionEvent` 先組好 event object 再同步傳給兩層。純本地 renderer memory，無 UI 副作用，無 Pet Window、/chat、TTS、history、IPC、backend。+13 tests。Windows visual smoke PASS (8 groups, 2026-06-01)。DevTools Console 快捷鍵無反應，未檢查 Console；所有可見功能無異常。

</details>
