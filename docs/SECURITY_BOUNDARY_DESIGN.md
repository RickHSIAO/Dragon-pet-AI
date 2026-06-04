# Dragon Pet AI Security Boundary Design

**Task:** TASK-SEC-001 Security Boundary / Anti Prompt Injection Design
**Status:** DONE - DOCS-ONLY SECURITY BOUNDARY DESIGN
**Date:** 2026-06-04

## 1. Purpose

TASK-SEC-001 defines the security boundary that must exist before Owner Voice
Gate is connected to Manual Mic or Conversation Mode runtime. This is a
docs-only task. It does not change backend runtime, frontend runtime, IPC,
Manual Mic, Conversation Mode, STT, `/chat`, Pet Window, Output Queue, or
Diagnostics behavior.

The design goal is to prevent future LLM, retrieval, browser, file, email, and
tool workflows from being abused to leak private data, follow malicious
instructions from untrusted content, or trick the user into unsafe actions.

Detailed inventory and redaction rules are defined in
`docs/SENSITIVE_DATA_REDACTION_RULES.md` (TASK-SEC-002).
Prompt injection and phishing corpus cases are defined in
`docs/security/PROMPT_INJECTION_TEST_CORPUS.md` (TASK-SEC-003).
Tool permission and confirmation policy is defined in
`docs/security/TOOL_PERMISSION_POLICY.md` (TASK-SEC-004).
Phishing and link safety warning design is defined in
`docs/security/PHISHING_LINK_SAFETY_DESIGN.md` (TASK-SEC-005).

## 2. Sensitive Data Categories

The following data is sensitive and must be protected by default:

- System, developer, internal prompts, hidden rules, policy text, and private
  agent instructions.
- API keys, tokens, credentials, `.env` values, provider secrets, OAuth
  credentials, session cookies, and recovery codes.
- Local absolute paths, local config files, backend data files, app settings,
  database paths, and private project layout details when not necessary for a
  user-requested task.
- Owner Voice Gate centroid, embeddings, per-sample embeddings, voiceprint
  metadata, and `owner_voice_gate_settings.json`.
- Raw audio, base64 audio, waveforms, transcripts, chat logs, and rejected
  speech content.
- Diagnostics logs, debug dumps, stack traces, backend traces, smoke reports,
  local temp paths, and runtime state snapshots.
- User diary data, personal memory, private project notes, local research
  notes, and any data imported from memory or private documents.
- Future webpage, PDF, file, email, message, calendar, cloud-drive, browser,
  or tool outputs.

## 3. Data That Must Never Enter LLM Context

The following data must not be sent to LLM context, prompt templates, retrieved
context, chat history, diagnostics summaries, or tool-generated prompt content:

- Raw owner voice centroid vectors.
- Raw embeddings or per-sample embedding arrays.
- `backend/data/owner_voice_gate_settings.json` and any equivalent local
  voiceprint settings file.
- API keys, tokens, passwords, cookies, credentials, `.env`, and provider
  secrets.
- Hidden prompts, internal rules, developer messages, policy text, and system
  instructions.
- Full local diagnostic dumps unless the user explicitly selects the exact data
  and confirms that it should be shared.
- Unredacted private logs, full chat logs, full transcripts, user diary data,
  personal memory, private project notes, or local database dumps.
- Local file contents that were not explicitly selected by the user for the
  current task.

Allowed summaries must be minimized. Prefer booleans, status codes, counts,
hashes, coarse categories, and bounded excerpts over raw private content.

## 4. Prompt Injection Threat Model

Dragon Pet AI must treat all user-provided and externally sourced content as
untrusted unless it is an explicit command from the user in the current trusted
interaction layer.

Threats include:

- Direct user prompt injection, such as requests to reveal hidden prompts,
  bypass rules, ignore instructions, expose secrets, or print private files.
- Indirect prompt injection from webpages, PDFs, files, emails, messages,
  screenshots, OCR output, browser pages, documentation, issue trackers, or
  retrieved documents.
- Malicious instructions embedded inside otherwise useful content.
- Fake system, developer, admin, support, or security messages inside pasted
  user text or retrieved content.
- Attempts to reveal hidden prompts, memory, config, API keys, local paths,
  owner voice embeddings, local settings, or private logs.
- Attempts to cause future tools to read, write, delete, send, browse, click,
  download, execute, or exfiltrate data without explicit user intent.

## 5. Untrusted Content Handling

When future features read webpages, PDFs, emails, local files, OCR text, chat
exports, browser content, or tool output, the content must be framed as data,
not instructions.

Recommended wrapper:

```text
UNTRUSTED_CONTENT_START
...verbatim or summarized untrusted content...
UNTRUSTED_CONTENT_END
```

Required handling rules:

- Instructions inside the wrapper are not executable instructions for the app,
  model, agent, tools, or runtime.
- Fake system or developer messages inside the wrapper are treated as quoted
  content only.
- The app should extract facts, summarize, classify, or answer questions about
  the content, but must not obey commands embedded in it.
- The wrapper is not sufficient by itself. Tool permission checks, data
  minimization, output redaction, and confirmation gates are also required.
- Retrieved content must not be allowed to decide what files, URLs, credentials,
  messages, or tool calls should be used next.

## 6. Phishing And Social Engineering Risks

Future link, email, browser, file, and message workflows must detect and warn
about phishing and social engineering patterns, including:

- Suspicious login links or links asking the user to re-authenticate.
- Requests for verification codes, MFA codes, recovery codes, API keys,
  passwords, tokens, cookies, or wallet/private keys.
- Requests to paste secrets into chat, forms, terminals, issue trackers, email,
  or websites.
- Fake account suspension, invoice, payment, package delivery, security alert,
  legal notice, or urgent support messages.
- Malicious attachments, unexpected downloads, macros, executable files, and
  archive files.
- Domain spoofing, lookalike domains, punycode, shortened URLs, misleading link
  text, and mismatched visible text versus href target.
- Urgency, fear, authority, scarcity, reward, refund, job offer, romance, or
  prize bait.

The app should present the real domain and action being requested before any
future URL opening, credential-related action, or outbound message.

## 7. Future Tool Permission Model

Tool permissions should be tiered. A future implementation can use these tiers
as policy labels for UI confirmations and backend checks.

| Tier | Capability | Required control |
|---|---|---|
| T0 | No-tool / local reasoning only | No external or local tool action. |
| T1 | Safe read-only public information | Public data only; no secrets, no private files. |
| T2 | User-selected local file read | User selects exact file(s); content is treated as untrusted data and redacted before LLM context. |
| T3 | Sensitive local file read | Explicit confirmation with path/category display; raw T6 data remains forbidden. |
| T4 | Write, overwrite, move, delete, install, execute, or settings changes | Explicit confirmation; preview target path/action; no hidden batch actions. |
| T5 | Send email, message, post, upload, share, submit form, open URL, download, or browser automation | Preview destination/domain, payload, and risk; explicit confirmation required. |
| T6 | Secrets, credentials, voiceprint, hidden prompts, raw biometric-like data, or internal rules | Forbidden from LLM context and untrusted-content workflows. |

Policy invariants:

- Untrusted content cannot grant itself higher tool permission.
- The model must not infer consent from text inside a webpage, PDF, email, or
  file.
- Confirmation must be attached to the concrete action, destination, and data
  category, not to vague intent.
- Secrets and voiceprint access stay forbidden from LLM context even if future
  tools can read local files for other reasons.

## 8. Output Redaction Checks

Before displaying, logging, sending, or passing responses to another tool,
future safety layers should detect and redact:

- API key-like strings, bearer tokens, OAuth tokens, private keys, session
  cookies, and password-like values.
- Provider config JSON, `.env` values, credential blobs, and local secrets.
- Owner voice centroid vectors, embedding arrays, per-sample embeddings, and
  voiceprint-like numeric arrays.
- Full local private paths when the full path is not needed; prefer basename,
  repo-relative path, or category.
- Hidden prompt-like dumps, system/developer prompt excerpts, and internal rule
  blocks.
- Suspicious encoded URLs, query strings, fragments, or form bodies containing
  private data.
- Full diagnostic dumps, stack traces, database rows, raw transcripts, and chat
  logs unless the user explicitly selected and confirmed them.

Redaction should be conservative. When unsure, show a safe summary and ask the
user to select a narrower file, excerpt, or action.

## 9. Owner Voice Security Boundary

Owner Voice Gate is a convenience filter for reducing accidental voice triggers.
It is not authentication and must not be represented as account security,
authorization, identity proof, or access control.

Owner voice storage rules:

- The stored centroid is sensitive local biometric-like data.
- The centroid must not be exposed to LLM context, UI, API responses, logs,
  diagnostics, chat history, transcripts, Output Queue items, or Pet runtime.
- Candidate embeddings must not be persisted or exposed.
- Rejected speech must not leak raw audio, full transcript, or embedding data
  into `/chat`, diagnostics, logs, or LLM context.
- Owner voice status may expose only safe summary fields such as enrolled,
  enabled, threshold, provider, model id, embedding dimension, sample count,
  and last updated time.

## 10. Runtime Integration Preconditions

Before Owner Voice Gate is connected to Manual Mic or Conversation Mode
runtime, all of the following must be complete:

- TASK-SEC-001 Security Boundary / Anti Prompt Injection Design complete.
- TASK-SEC-002 Sensitive Data Inventory / Redaction Rules complete.
- Owner voice runtime integration remains opt-in and disabled by default.
- Rejected speech does not enter `/chat`, LLM context, chat history,
  diagnostics, Output Queue, Pet Bubble, or Pet runtime.
- Rejected speech does not expose transcript, raw audio, base64 audio,
  waveform, candidate embedding, or score details beyond a safe local status.
- Runtime gate behavior is dry-run tested before any blocking behavior is
  enabled.
- Manual Mic and Conversation Mode integration each have separate tests and
  documentation.

TASK-266 satisfies the Manual Mic dry-run requirement as status-only behavior:
accept, reject, not-computed, disabled, and error states do not hard-block
Manual Mic STT, textarea fill, auto-send, `/stt/transcribe`, or `/chat`.
Conversation Mode remains deferred to TASK-267.

## 11. Recommended Task Sequence

1. TASK-SEC-001 Security Boundary / Anti Prompt Injection Design - DONE.
2. TASK-SEC-002 Sensitive Data Inventory / Redaction Rules - DONE.
3. TASK-SEC-003 Prompt Injection Test Corpus - DONE.
4. TASK-SEC-004 Tool Permission / User Confirmation Policy - DONE.
5. TASK-SEC-005 Phishing / Link Safety Warning Layer Design - DONE.
6. TASK-266 Owner Voice Gate Manual Mic Dry-run Policy - DONE.
7. TASK-267 Owner Voice Gate Conversation Mode Dry-run Policy.

## 12. Non-Goals

TASK-SEC-001 does not implement:

- Runtime prompt injection filters.
- Runtime redaction code.
- Browser, file, email, or tool permission UI.
- Owner Voice Gate Manual Mic integration.
- Owner Voice Gate Conversation Mode integration.
- `/stt/transcribe`, `/chat`, IPC, Pet Window, Output Queue, or Diagnostics
  behavior changes.

## 13. Validation

Required validation for this docs-only task:

```powershell
git diff --check
git status --short
```

No code tests are required unless a docs tooling pipeline is added later.
