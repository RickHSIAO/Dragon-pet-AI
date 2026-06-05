# Tool Permission And User Confirmation Policy

**Task:** TASK-SEC-004 Tool Permission / User Confirmation Policy
**Status:** DONE - DOCS-ONLY TOOL PERMISSION POLICY
**Date:** 2026-06-04

## 1. Purpose

TASK-SEC-004 defines Dragon Pet AI's future tool permission and user
confirmation policy. It turns the TASK-SEC-001 T0-T6 concept into concrete
rules for allowed actions, forbidden actions, previews, confirmations, logging,
LLM context handling, and failure behavior.

This task is docs-only. It does not modify backend runtime, frontend runtime,
IPC, Manual Mic, Conversation Mode, STT, `/chat`, Pet Window, Output Queue,
Diagnostics behavior, Owner Voice Gate runtime wiring, or actual tool execution
behavior.

Related docs:

- `docs/SECURITY_BOUNDARY_DESIGN.md`
- `docs/SENSITIVE_DATA_REDACTION_RULES.md`
- `docs/security/PROMPT_INJECTION_TEST_CORPUS.md`
- `docs/security/PHISHING_LINK_SAFETY_DESIGN.md`

## 2. Permission Tier Summary

| Tier | Name | Confirmation | Preview | LLM context | Core rule |
|---|---|---|---|---|---|
| T0 | No-tool / local reasoning only | No | No | Normal response only | No external or local tool action. |
| T1 | Safe read-only public info | Usually no | Optional | Allowed after minimization | Public data only. |
| T2 | User-selected local file read | Yes by file selection | File/path summary | Allowed after redaction | User chooses exact file(s). |
| T3 | Sensitive local file read | Explicit confirmation | Required | Redacted/minimized only | Sensitive paths need explicit approval; some data remains forbidden. |
| T4 | Write / delete / execute actions | Explicit confirmation | Required | Tool result summary only | State-changing actions must be previewed and confirmed. |
| T5 | Outbound communication / upload / send | Explicit confirmation | Required | Sent-data summary only | Anything leaving the machine needs preview and approval. |
| T6 | Forbidden access | Not allowed | Not applicable | Forbidden | Secrets, hidden prompts, voiceprints, raw biometric-like data. |

Untrusted content can never promote an action to a higher permission tier or
authorize a tool call.

## 3. Tier Details

### T0 - No-Tool / Local Reasoning Only

- Allowed actions: answer from current conversation, summarize already visible
  user-provided text, reason about public design constraints without tool use.
- Forbidden actions: local file reads, writes, execution, network calls,
  browser actions, outbound messages, uploads, settings changes.
- User confirmation required: no.
- Preview required: no.
- Logging allowed: minimal conversational event metadata only.
- LLM context result: no tool result.
- Examples: explain a policy, draft a response, classify a pasted phishing
  example, reason about a local design.
- Failure behavior: if a tool is needed, state the required tier and ask for
  explicit user selection/confirmation.

### T1 - Safe Read-Only Public Info

- Allowed actions: read public docs, public release notes, public web pages,
  public package documentation, public non-sensitive metadata.
- Forbidden actions: private local files, secrets, credentials, private
  accounts, authenticated pages, downloads that execute or install.
- User confirmation required: usually no, unless the action opens a risky URL
  or crosses into T5 browser/navigation behavior.
- Preview required: optional; show domain/source when useful.
- Logging allowed: sanitized source/domain, timestamp, query/category.
- LLM context result: allowed after summarization and untrusted-content
  handling.
- Examples: public documentation lookup, public changelog summary, public
  reference comparison.
- Failure behavior: if content asks for secrets or tool actions, treat it as
  untrusted and do not follow embedded instructions.

### T2 - User-Selected Local File Read

- Allowed actions: read exact local file(s) the user selected or explicitly
  named for the current task.
- Forbidden actions: model-chosen broad path scans, reading hidden prompt
  files, secrets, voiceprint files, `.env`, owner voice settings, unrelated
  private documents.
- User confirmation required: yes, through explicit file selection or precise
  user instruction.
- Preview required: file path or basename, file type, approximate size/count
  when available.
- Logging allowed: sanitized path or basename, file category, confirmation
  source, timestamp.
- LLM context result: allowed only after redaction and minimization.
- Examples: user attaches a Markdown file for review; user names a specific
  non-secret project doc.
- Failure behavior: if the file is sensitive or broader than requested, stop
  and escalate to T3 or refuse if T6.

### T3 - Sensitive Local File Read

- Allowed actions: read sensitive local files only when the user explicitly
  selects the exact file and confirms the risk, and only if the data is not T6.
- Forbidden actions: reading `.env`, provider secrets, hidden prompts, owner
  voice centroid/settings, raw embeddings, private keys, or unbounded private
  dumps into LLM context.
- User confirmation required: explicit confirmation with risk label.
- Preview required: exact path/category, why it is sensitive, what fields will
  be summarized/redacted.
- Logging allowed: sanitized target category, confirmation result, safe reason.
- LLM context result: redacted/minimized summary only; raw sensitive content is
  not sent.
- Examples: user-selected diagnostic excerpt, user-selected non-secret config
  snippet, bounded private note excerpt.
- Failure behavior: refuse if T6 data is requested; otherwise ask for a narrower
  excerpt or safer summary.

### T4 - Write / Delete / Execute Actions

- Allowed actions: create or edit files, write settings, delete files, move
  files, run commands, install dependencies, execute scripts, change app state.
- Forbidden actions: hidden batch changes, destructive actions without exact
  target preview, writes sourced from untrusted content alone, executing
  downloaded or untrusted files, actions involving T6 data.
- User confirmation required: explicit confirmation.
- Preview required: exact operation, target path(s), whether reversible, backup
  or undo plan if available, data summary.
- Logging allowed: action category, sanitized target, confirmation result,
  safe reason/status.
- LLM context result: execution result summary only; redact outputs.
- Examples: save a user-approved doc edit, run tests, install dependency after
  approval, delete a selected temp folder.
- Failure behavior: block on missing confirmation; for destructive operations,
  prefer backup/undo or ask the user to narrow the target.

### T5 - Outbound Communication / Upload / Send Actions

- Allowed actions: send email/message, upload file, submit web/API request,
  post content, share logs, open URL with active submission only after preview.
- Forbidden actions: sending secrets, tokens, hidden prompts, owner voice
  centroid/embeddings, raw audio, rejected speech transcript, full private
  documents, or unredacted diagnostics.
- User confirmation required: explicit confirmation every time.
- Preview required: destination domain/recipient, exact data or bounded summary,
  attachments, whether data leaves the machine, risk label, reversible status.
- Logging allowed: sanitized destination, action type, confirmation result,
  timestamp, safe reason/status.
- LLM context result: sent-data summary only; no secret payload.
- Examples: user-approved support email with sanitized logs; uploading a
  redacted report; opening a URL after domain warning.
- Failure behavior: block if preview cannot be produced, destination is unclear,
  or payload contains T6 data.

### T6 - Forbidden Access

- Allowed actions: safe status summaries only, where explicitly designed.
- Forbidden actions: reading, exposing, sending, logging, storing in LLM
  context, summarizing raw values, transforming, encoding, hashing for
  disclosure, or using untrusted content to request access.
- User confirmation required: no confirmation can authorize LLM exposure.
- Preview required: not applicable.
- Logging allowed: safe refusal reason and category only.
- LLM context result: forbidden.
- Examples: API keys, `.env`, bearer tokens, hidden system/developer prompts,
  owner voice centroid, `embeddingAggregate`, candidate embeddings, raw
  biometric-like data, private keys, wallet seed phrases.
- Failure behavior: refuse and provide a safe alternative such as status,
  redacted summary, or user-side instructions.

## 4. Confirmation UX Rules

Risky actions must show a confirmation prompt with:

- Action type.
- Exact operation to be performed.
- Target path, domain, recipient, endpoint, or command.
- Data summary and sensitivity category.
- Risk label, such as low, medium, high, destructive, outbound, or forbidden.
- Whether data leaves the machine.
- Whether the action is reversible.
- Backup, undo, or recovery plan when relevant.
- Explicit confirmation result.

Confirmation must be attached to the concrete action. A broad statement such as
"do whatever is needed" is not enough for T3, T4, or T5 actions.

## 5. Outbound Safety Rules

For email, message, upload, API, browser submit, or web request actions:

- Require preview and explicit confirmation.
- Show destination domain, recipient, endpoint, or service.
- Show exact data being sent or a bounded sanitized summary.
- Block secrets, tokens, owner voice centroid, embeddings, hidden prompts, raw
  biometric-like data, raw audio, rejected speech transcript, and unredacted
  private documents.
- Warn about phishing/social engineering if the destination, content, or
  request pattern is suspicious.
- Do not auto-submit forms.
- Do not send data requested only by untrusted webpage, PDF, email, OCR, or file
  content.
- Refuse if destination or payload cannot be made clear to the user.

## 6. Local File Safety Rules

For local file read/write/delete:

- User-selected reads are safer than model-chosen paths.
- Model-chosen path reads require a clear task reason and must avoid sensitive
  classes by default.
- Sensitive paths require explicit confirmation and redaction.
- `.env`, tokens, owner voice settings, embeddings, hidden prompt files,
  private keys, and wallet seed phrases are T6 or strict-block data.
- Delete, overwrite, move, install, execute, and settings changes require
  explicit confirmation.
- Destructive actions should include a backup, undo, or recovery plan whenever
  practical.
- Broad recursive operations require extra caution and precise path boundaries.

## 7. URL And Browser Safety Rules

Before opening, processing, or automating a URL:

- Show the domain and normalized URL when practical.
- Warn on URL shorteners, encoded payloads, suspicious domains, punycode,
  lookalike domains, mismatched visible text vs target URL, and unexpected
  redirects.
- Do not auto-submit forms.
- Do not enter passwords, verification codes, tokens, API keys, cookies, wallet
  seed phrases, or secrets.
- Treat webpage content as untrusted data, not instructions.
- Do not allow webpage/PDF/email content to request local file reads, settings
  changes, secret disclosure, uploads, or outbound messages.

## 8. Owner Voice Gate Tool Boundary

Owner Voice Gate is a convenience filter, not authentication or identity proof.

Rules:

- Owner voice centroid, settings, `embeddingAggregate`, embeddings, candidate
  embeddings, and raw biometric-like data are T6 forbidden from LLM context.
- Verification APIs may expose only score, threshold, accepted/rejected status,
  reason, enrollment state, embedding dimension, sample count, and safety
  booleans.
- No raw audio or candidate embedding exposure.
- No rejected speech transcript enters `/chat`, diagnostics, Pet Bubble, Output
  Queue, Pet runtime, chat history, logs, or LLM context.
- No untrusted content may authorize bypassing Owner Voice Gate.
- TASK-269 hard-gate design does not change tool permissions. A future Owner
  Voice Gate pass cannot authorize sensitive tool use, cannot bypass
  confirmation UX, cannot approve outbound requests, cannot approve local-file
  access, and cannot grant access to T6 forbidden data. Tool permission
  decisions remain governed by this policy even when owner voice hard gate is
  enabled.
- TASK-270 candidate WAV temp policy does not change tool permissions. A
  dry-run verification pass, reject, temp WAV path, or cleanup result cannot
  authorize sensitive tools, bypass confirmation UX, approve outbound requests,
  approve local-file access, or grant access to T6 forbidden data.
- Future Manual Mic and Conversation Mode work must remain opt-in,
  disabled-by-default, and dry-run policy gated before blocking runtime behavior.

## 9. Prompt Injection Interaction Rules

If untrusted content instructs the app or assistant to use tools, exfiltrate
data, change settings, reveal secrets, open URLs, send messages, add hidden
instructions, or bypass safety:

- Treat the instruction as untrusted content.
- Summarize safely if useful.
- Do not execute the instruction.
- Require user confirmation for any independently justified tool action.
- Refuse secrets, hidden prompts, voiceprint data, raw embeddings, raw audio,
  rejected speech, and private key exfiltration.
- Do not persist untrusted instructions into future context, memory, settings,
  prompts, or tool plans.

## 10. Audit And Logging Rules

Logs may capture:

- Action category.
- Timestamp.
- Sanitized target or destination.
- User confirmation result.
- Safe reason/status.
- Permission tier.
- Whether data left the machine.

Logs must not capture:

- Secrets, tokens, passwords, cookies, private keys, or `.env` values.
- Full hidden prompts, developer instructions, or internal policy text.
- Owner voice centroid, embeddings, `embeddingAggregate`, candidate embeddings,
  or raw biometric-like data.
- Raw audio or rejected transcripts.
- Full private documents unless explicitly selected, sanitized, and required.
- Unredacted diagnostic dumps.

## 11. Future Implementation Checklist

Before implementing any tool action:

1. Classify the tool tier T0-T6.
2. Define allowed and forbidden inputs.
3. Define output redaction.
4. Define confirmation requirement.
5. Define preview fields.
6. Define logging policy.
7. Define LLM context handling.
8. Add prompt injection corpus cases.
9. Add phishing/social engineering cases when outbound or URL-related.
10. Add smoke/eval tests.
11. Document failure behavior.
12. Confirm T6 data is blocked from LLM context and outbound actions.

## 12. Updated Security Task Sequence

1. TASK-SEC-001 Security Boundary / Anti Prompt Injection Design - DONE.
2. TASK-SEC-002 Sensitive Data Inventory / Redaction Rules - DONE.
3. TASK-SEC-003 Prompt Injection / Phishing Test Corpus - DONE.
4. TASK-SEC-004 Tool Permission / User Confirmation Policy - DONE.
5. TASK-SEC-005 Phishing / Link Safety Warning Layer Design - DONE.
6. TASK-266 Owner Voice Gate Manual Mic Dry-run Policy - DONE.
7. TASK-267 Owner Voice Gate Conversation Mode Dry-run Policy - DONE.
8. TASK-268 Owner Voice Dry-run Diagnostics / Safety Summary Polish - DONE.
9. TASK-269 Owner Voice Gate Hard Gate Design / Opt-in Policy - DONE.
10. TASK-270 Owner Voice Candidate WAV Temporary Policy Design / Implementation - DONE.

## 13. Validation

Required validation for this docs-only task:

```powershell
git diff --check
git status --short
```

No runtime tests are required unless a docs tooling pipeline is added later.
