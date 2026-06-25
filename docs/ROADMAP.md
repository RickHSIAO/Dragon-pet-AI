# Roadmap

This roadmap is strategic. It does not track completed micro-tasks.

## 1. Stable Local Conversation

- Keep `/chat` schema stable.
- Preserve mock-safe defaults.
- Make local provider setup and fallback behavior understandable.
- Keep provider settings reliable without exposing raw provider bodies or keys.

## 2. Reliable Continuous STT

- Improve Conversation Mode reliability across longer sessions.
- Keep no-speech and suspicious-transcript suppression conservative.
- Maintain a session-only model/provider selector until a default change is
  explicitly approved.
- Keep raw audio out of Git and default persistence.

## 3. Owner Voice Gate Decision

- Decide whether Owner Voice Gate remains a dry-run convenience filter or
  graduates to a stronger product feature.
- Do not treat it as security-grade authentication without a new design.
- Preserve no raw-audio persistence and no raw embedding exposure.

## 4. Character-Quality Local TTS

- Resolve GPT-SoVITS Chinese text blockers.
- Keep voice-lab artifacts outside the application repository.
- Do not enable runtime speech until a provider, voice, dependency, and artifact
  policy are approved.

## 5. Safe Runtime TTS Integration

- Integrate TTS only after provider selection and local validation.
- Keep playback opt-in and controllable.
- Preserve `/chat`, STT, Owner Voice, and schema boundaries.

## 6. Packaging And Release

- Simplify setup.
- Keep generated reports and local evidence out of Git.
- Document user-facing workflows and known limits.
- Prepare release checks that validate behavior without becoming task journals.
