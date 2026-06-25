# Owner Voice Gate Research

This is the active concise research boundary for Owner Voice Gate. Historical
task evidence remains in Git history.

## Status

TASK-259 established the local file-path probe boundary. Owner Voice Gate is a
convenience filter and is not security-grade.

## Current Boundary

- No Manual Mic runtime change.
- No Conversation Mode runtime change.
- No raw audio persistence.
- No `/chat` schema change.
- No hard authentication guarantee.
- Existing WAV file paths may be used for controlled local enrollment or
  verification probes.

## Product Meaning

Owner Voice Gate may help label whether a local candidate voice sounds like the
enrolled owner, but it must not be used as production authorization or account
security. It should remain inspectable, reversible, and local-only.
