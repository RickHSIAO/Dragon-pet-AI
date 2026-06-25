# Owner Voice Gate Storage Design

## Status

TASK-260: DESIGNED - OWNER VOICE ENROLLMENT STORAGE PLAN / NO RUNTIME CHANGE

## Storage Path

Backend-owned local settings path:

```text
backend/data/owner_voice_gate_settings.json
```

The file is ignored by Git.

## Stored Values

Store the centroid only, plus safe metadata required for thresholding and UI
state. Keep the data local and user-controlled.

Forbidden stored values:

- raw audio
- temporary WAV files
- per-sample embeddings
- raw verification traces
- external account identifiers
- secrets

## Runtime Boundaries

- No Manual Mic runtime change.
- No Conversation Mode runtime change.
- No `/stt/transcribe` behavior change.
- No `/chat` schema change.
- No raw audio persistence.
- Not security-grade.

Owner Voice Gate remains a convenience filter until a separate product and
security design says otherwise.
