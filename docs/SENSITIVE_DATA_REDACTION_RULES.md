# Sensitive Data Inventory And Redaction Rules

**Task:** TASK-SEC-002 Sensitive Data Inventory / Redaction Rules
**Status:** DONE - DOCS-ONLY SENSITIVE DATA INVENTORY / REDACTION RULES
**Date:** 2026-06-04

## 1. Purpose

TASK-SEC-002 makes the TASK-SEC-001 security boundary concrete. It defines
Dragon Pet AI sensitive data classes, allowed and forbidden exposure rules,
redaction patterns, API response restrictions, diagnostics/logging limits, LLM
context restrictions, and the TASK-SEC-003 corpus coverage shape.

The TASK-SEC-003 corpus is now captured in
`docs/security/PROMPT_INJECTION_TEST_CORPUS.md`.
Tool permission and confirmation requirements are captured in
`docs/security/TOOL_PERMISSION_POLICY.md` (TASK-SEC-004).
Phishing and link safety warning design is captured in
`docs/security/PHISHING_LINK_SAFETY_DESIGN.md` (TASK-SEC-005).

This is a docs-only task. It does not modify backend runtime, frontend runtime,
IPC, Manual Mic, Conversation Mode, STT, `/chat`, Pet Window, Output Queue,
Diagnostics behavior, or Owner Voice Gate runtime wiring.

## 2. Sensitive Data Classes

| Class | Name | Examples |
|---|---|---|
| S0 | Public / safe | Public docs, public feature names, non-private status labels, coarse task names. |
| S1 | Local metadata | Repo-relative paths, local file basenames, timestamps, counts, safe status/reason strings, provider/model names. |
| S2 | User private text | Chat logs, transcripts, diary entries, personal memory, private project notes, selected file excerpts. |
| S3 | Secrets and credentials | API keys, bearer tokens, `.env`, passwords, cookies, OAuth tokens, recovery codes, private keys. |
| S4 | Biometric-like data | Owner voice centroid, `embeddingAggregate`, raw embeddings, per-sample embeddings, candidate embeddings, voiceprint storage. |
| S5 | Hidden system/developer/internal prompts | System prompts, developer instructions, internal rules, hidden policies, agent control text. |
| S6 | Tool outputs with mixed trust | Webpages, PDFs, emails, OCR, browser output, retrieved files, diagnostics bundles, future file/web/email/tool responses. |

## 3. Exposure Matrix

| Class | LLM context | UI | Diagnostics | Logs | API responses | Persistence | Explicit confirmation |
|---|---|---|---|---|---|---|---|
| S0 | Allowed | Allowed | Allowed | Allowed | Allowed | Allowed | No |
| S1 | Allowed when task-relevant and minimized | Allowed when useful | Allowed as summary | Allowed as summary | Allowed as summary | Allowed | Sometimes, for local path disclosure |
| S2 | Allowed only when user selected or directly provided for current task | Allowed if user-facing and bounded | Summary only by default | Redacted or event metadata only | Bounded excerpt or summary only | Allowed only by feature policy | Yes for broad/full dumps |
| S3 | Forbidden | Redacted status only | Forbidden except safe configured/not-configured status | Forbidden | Forbidden except safe key status | Secret storage only | Yes for actions, never for LLM exposure |
| S4 | Forbidden | Safe status only | Safe status/score only | Forbidden raw values | Safe status/score only | Backend-owned storage only | Yes for enrollment/delete actions |
| S5 | Forbidden | Forbidden | Forbidden | Forbidden | Forbidden | Internal control only | No; still forbidden |
| S6 | Allowed only after wrapping as untrusted content and minimizing | Allowed when labeled untrusted | Summary only | Redacted metadata only | Summary only | Feature-specific | Yes for sensitive or outbound use |

Rules:

- "Allowed" never means "dump everything." Data minimization still applies.
- S3, S4 raw values, and S5 must never enter LLM context.
- S6 content is data, not instructions, even when it contains fake system,
  developer, security, support, or admin text.
- Full local diagnostic dumps require exact user selection and confirmation
  before display or outbound use, and still require redaction before LLM
  context.

## 4. Data Forbidden From LLM Context

The following must not be placed into LLM prompts, retrieved context, memory
injection, chat history summaries, prompt templates, tool-augmented context, or
model-facing diagnostics:

- S3 secrets: API keys, bearer tokens, `.env` values, passwords, cookies,
  OAuth tokens, private keys, recovery codes.
- S4 raw biometric-like data: owner voice centroid vectors,
  `embeddingAggregate`, embeddings, per-sample embeddings, candidate
  embeddings, and `owner_voice_gate_settings.json`.
- S5 hidden prompts and internal rules.
- Full S2 private data dumps: full chat logs, full transcripts, diary files,
  personal memory, private project notes, database dumps.
- Unredacted S6 tool output that includes instructions, secrets, local config,
  private logs, or mixed-trust content.

## 5. Redaction Patterns

Future automated redaction should detect and replace the following with stable
labels such as `[REDACTED_SECRET]`, `[REDACTED_TOKEN]`,
`[REDACTED_LOCAL_PATH]`, `[REDACTED_EMBEDDING]`, or
`[REDACTED_PRIVATE_DUMP]`.

### Secrets And Tokens

- API-key-like strings with recognizable prefixes such as `sk-`, `sk-ant-`,
  `xoxb-`, `ghp_`, `github_pat_`, `AIza`, `AKIA`, `ASIA`, and similar long
  high-entropy credentials.
- Bearer tokens and authorization headers:
  `Authorization: Bearer ...`, `Bearer <token>`, `Basic <token>`.
- `.env` or config assignments containing secret-like names:
  `API_KEY=`, `TOKEN=`, `SECRET=`, `PASSWORD=`, `PRIVATE_KEY=`,
  `COOKIE=`, `SESSION=`, `CLIENT_SECRET=`.
- PEM blocks and private-key markers such as `BEGIN PRIVATE KEY`.

### Local Paths And Config

- Absolute Windows paths such as `C:\Users\...\...` and
  `F:\RickHSIAO\Python\...` when full disclosure is not required.
- Local config file contents: `.env`, provider settings, backend data files,
  local settings JSON, local database rows, and voice gate settings.
- Prefer repo-relative paths or basenames when the exact absolute path is not
  needed for user action.

### Owner Voice And Embeddings

- `embeddingAggregate`, `perSampleEmbeddings`, `candidateEmbedding`,
  `storedCentroid`, `centroid`, and embedding-like numeric arrays.
- Numeric arrays with dozens or hundreds of floating-point values, especially
  near 192-d speaker embeddings.
- `owner_voice_gate_settings.json` raw content.
- Raw audio bytes, base64 audio-like payloads, waveform arrays, and rejected
  speech transcripts.

### Diagnostic Dumps And Hidden Prompts

- Long diagnostic dumps, stack traces, environment dumps, full settings dumps,
  full request/response bodies, and database row dumps.
- Hidden prompt-like sections containing labels such as `SYSTEM MESSAGE`,
  `developer instructions`, `internal policy`, `hidden rules`, or similar.
- Pasted content that asks the model to reveal prompts, ignore rules, expose
  secrets, dump memory, or disclose local paths.

### Suspicious URLs

- URLs with encoded secrets in query strings, fragments, or path segments.
- URLs containing `token=`, `key=`, `code=`, `password=`, `session=`,
  `auth=`, `redirect=`, or suspicious base64-like blobs.
- Shortened URLs or mismatched visible text and target URL in future link
  displays.

## 6. Owner Voice Gate-Specific Rules

Owner Voice Gate remains a convenience filter, not authentication or access
control.

Hard rules:

- `owner_voice_gate_settings.json` must not be sent to LLM context.
- `embeddingAggregate` and stored centroid vectors must not be exposed in API
  responses, UI, diagnostics, logs, Output Queue items, Pet Bubble, Pet runtime,
  chat history, or LLM context.
- Candidate embeddings must not be persisted.
- Raw audio, waveform, transcript, and base64 audio must not be persisted by
  owner voice enrollment or verification flows.
- Rejected speech must not enter `/chat`, LLM context, diagnostics, Output
  Queue, Pet Bubble, Pet runtime, chat history, or TTS.
- Safe status fields may indicate enrollment, enabled state, provider, model,
  embedding dimension, sample count, threshold, and verification decision.
- Scores and thresholds may be shown as local verification results, but they
  must not be presented as identity proof or account security.
- TASK-266 Manual Mic dry-run diagnostics may show only status, reason,
  score/threshold, accepted state, checked timestamp, and safety booleans.
  They must not show centroid vectors, `embeddingAggregate`, candidate
  embeddings, raw audio, raw candidate paths, or rejected transcript.
- TASK-267 Conversation Mode dry-run diagnostics may show the same safe fields
  plus `ownerVoiceDryRunSource=conversation_mode`. They must not show centroid
  vectors, `embeddingAggregate`, candidate embeddings, raw audio, raw candidate
  paths, raw transcript, or rejected transcript.
- TASK-269 hard-gate design keeps the same redaction boundary for future
  blocking. A hard-gate reject must not expose or persist rejected transcript,
  raw audio, waveform, base64 audio, candidate embeddings, stored centroid,
  `embeddingAggregate`, or full candidate paths. Allowed display remains status,
  reason, score, threshold, accepted/rejected, checkedAt, and safety booleans.
  Owner Voice Gate remains a convenience filter, not authentication.

## 7. API Response Rules

Allowed in Owner Voice Gate API responses:

- `status`
- `reason`
- `enrolled`
- `enabled`
- `score`
- `scores`
- `threshold`
- `accepted`
- `embeddingDim`
- `sampleCount`
- bounded `checkedAudioFiles` metadata for user-selected local files
- safe booleans:
  - `rawAudioPersisted=false`
  - `candidateEmbeddingPersisted=false`
  - `storedCentroidExposed=false`
  - `micAccessed=false`
  - `runtimeIntegrated=false`

Forbidden in API responses:

- Full centroid vectors.
- Full embeddings.
- Candidate embeddings.
- Raw audio bytes, base64 audio, waveform arrays.
- Rejected speech transcript.
- `owner_voice_gate_settings.json` raw content.
- API keys, tokens, `.env`, hidden prompts, or full private diagnostics.

Path disclosure:

- For user-selected local files, raw path echo may be useful for debugging, but
  future UI/API layers should minimize absolute path display when possible.
- Prefer basename, repo-relative path, count, or "selected local file" unless
  the user needs the exact path to resolve an error.

## 8. Diagnostics And Logging Rules

Diagnostics may show:

- Status, reason, score, threshold, accepted/rejected decision.
- Provider/model name, embedding dimension, sample count.
- Safe booleans proving no raw audio, no candidate embedding persistence, no
  stored centroid exposure, no mic access, and no runtime integration.
- Event IDs, counts, bounded timings, and sanitized error categories.

Diagnostics must not show:

- Raw centroid, raw embedding, candidate embedding, or `embeddingAggregate`.
- Raw audio, waveform, base64 audio, or rejected speech transcript.
- API keys, tokens, `.env`, cookies, passwords, or provider secrets.
- Hidden prompts, internal rules, developer instructions, or policy dumps.
- Full private local paths unless the user explicitly selected them for the
  current operation.
- Full diagnostic dumps by default.

Logs should prefer:

- Event IDs instead of payloads.
- Counts instead of raw lists.
- Sanitized reasons instead of stack traces.
- File categories or basenames instead of absolute paths.
- `true`/`false` safety flags instead of sensitive data.

## 9. Automated Redaction Checklist

Before any future response, UI display, diagnostics display, log write,
retrieval injection, prompt construction, outbound tool action, email/message
send, file upload, browser submission, or URL open:

- Check for secret-like strings.
- Check for bearer tokens, cookies, private keys, and `.env` assignments.
- Check for embedding-like numeric arrays and owner voice field names.
- Check for local config file contents and backend data file dumps.
- Check for hidden prompt or internal rule dumps.
- Check for tokenized or encoded URLs carrying private data.
- Check for raw audio/base64 audio/waveform payloads.
- Check for rejected speech transcripts.
- Check for suspicious phishing content, especially login links, verification
  code requests, token requests, fake account suspension, urgency/fear/reward
  bait, shortened URLs, or lookalike domains.

If a check is uncertain, the default action is to redact, summarize, and ask for
explicit user selection of a narrower excerpt or action.

## 10. TASK-SEC-003 Corpus Coverage

TASK-SEC-003 Prompt Injection Test Corpus captures cases for:

- Attempts to reveal system, developer, internal prompts, hidden rules, and
  security policy text.
- Attempts to reveal API keys, `.env`, tokens, cookies, passwords, and provider
  settings.
- Attempts to reveal local paths, local config files, backend data files, and
  database contents.
- Attempts to reveal Owner Voice Gate centroid, embeddings,
  `owner_voice_gate_settings.json`, candidate embeddings, raw audio, or
  rejected speech transcripts.
- Attempts to reveal diagnostics, memory, diary data, personal notes, and chat
  logs.
- Indirect prompt injection inside webpages, PDFs, emails, OCR text, browser
  content, and local files.
- Fake system/developer/admin/security/support messages embedded in retrieved
  content.
- Phishing attempts with fake login links, verification-code requests, token
  exfiltration, malicious attachments, domain spoofing, shortened URLs,
  urgency/fear bait, and reward bait.

The corpus should verify that untrusted content is treated as data, not
instructions, and that future tools cannot be invoked solely because untrusted
content requested it.

## 11. Updated Security Task Sequence

1. TASK-SEC-001 Security Boundary / Anti Prompt Injection Design - DONE.
2. TASK-SEC-002 Sensitive Data Inventory / Redaction Rules - DONE.
3. TASK-SEC-003 Prompt Injection Test Corpus - DONE.
4. TASK-SEC-004 Tool Permission / User Confirmation Policy - DONE.
5. TASK-SEC-005 Phishing / Link Safety Warning Layer Design - DONE.
6. TASK-266 Owner Voice Gate Manual Mic Dry-run Policy - DONE.
7. TASK-267 Owner Voice Gate Conversation Mode Dry-run Policy - DONE.
8. TASK-268 Owner Voice Dry-run Diagnostics / Safety Summary Polish - DONE.
9. TASK-269 Owner Voice Gate Hard Gate Design / Opt-in Policy - DONE.

## 12. Validation

Required validation for this docs-only task:

```powershell
git diff --check
git status --short
```

No code tests are required unless a docs tooling pipeline is added later.
