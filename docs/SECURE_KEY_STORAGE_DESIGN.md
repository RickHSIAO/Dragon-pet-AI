# Secure Key Storage Design

> dragon-pet-ai
> Phase: 4 — LLM Adapter Integration
> Status: DESIGN (TASK-049); ABSTRACTION IMPLEMENTED (TASK-053 DONE); KEY SAVE/CLEAR ENDPOINTS IN_PROGRESS (TASK-054)
> Last Updated: 2026-05-20
> Owner: TASK-049

---

## 1. Purpose

BYOK requires storing or referencing user-owned LLM API keys safely. API keys are sensitive credentials — if leaked they grant access to the user's provider account, potentially incurring charges or exposing usage history.

Key principles:

- The app must avoid exposing, logging, or storing keys unsafely at every layer: backend, frontend, database, logs, crash reports, and debug exports.
- Persistent key storage is not enabled in the current dev phase. TASK-053 adds a storage abstraction and test fake backend; TASK-054 wires save/clear endpoints to that abstraction while runtime storage remains unavailable by default.
- This document defines design and recommendations only. No storage implementation is added in TASK-049.
- The `POST /provider/settings/key` endpoint (designed in TASK-048) must not be implemented until the storage strategy defined here is accepted and TASK-053 (Secure Key Storage Implementation) is complete.

---

## 2. Current Baseline

| Component | Status |
|---|---|
| API key handling — dev phase | Environment variable only (`LLM_API_KEY`) |
| Provider Settings API | Non-secret API implemented; key save/clear endpoints wired to storage abstraction |
| Provider Settings UI | Non-secret UI implemented; key controls still disabled |
| Key storage abstraction | Implemented in TASK-053 with safe unavailable runtime backend and fake test backend |
| Key stored in SQLite | No — explicitly forbidden until secure storage is designed and approved |
| Key stored in any file | No — no persistent key storage exists |
| Live provider call required | No — design task only |
| User-facing key management UI | Placeholder controls only; key save/clear/test disabled until UI enablement work |

---

## 2.1 TASK-053/TASK-054 Implementation Status

TASK-053 implements the storage abstraction:

- `backend/app/services/key_storage_service.py` defines the backend interface.
- Runtime default is a safe unavailable backend; it does not persist keys.
- `InMemoryKeyStorageBackend` exists for tests only.
- `KeyringKeyStorageBackend` is optional and only usable if the `keyring` package is installed.
- No key is stored in SQLite.
- No key is stored in a plain config file.
- TASK-054 wires `POST /provider/settings/key` and `DELETE /provider/settings/key` to this abstraction.
- Runtime default storage remains unavailable and returns safe errors for save/clear.
- Tests use `InMemoryKeyStorageBackend` to verify save, clear, idempotent clear, and replace behavior.
- No live provider test connection is enabled.

---

## 3. Storage Options

### Option A — Environment Variable Only

**Description:** The user sets `LLM_API_KEY` as a shell / OS environment variable before starting the backend. The backend reads it at startup via `os.environ`. No app-managed persistence.

**Pros:**
- Safest current development path
- No app-managed secret persistence — the app never writes the key anywhere
- Easy to avoid frontend exposure — key is never in the app process's writable storage
- Easy to clear: unset the env var or restart without it
- No OS keychain integration complexity
- Suitable for developers and technical users running the backend manually

**Cons:**
- Poor UX for non-technical desktop users
- Requires restarting the backend to change the key
- Requires shell setup (export / .env file) which non-technical users find difficult
- Not suitable for a packaged desktop app where users do not have shell access
- Leaks if the user's shell history logs the `export` command

**Verdict:** Recommended for dev phase and internal testing. Not suitable for general consumer BYOK UX.

---

### Option B — OS Keychain / Credential Manager

**Description:** The backend stores and retrieves the key through the OS's secure credential store. Examples: Windows Credential Manager (`keyring` / `wincredential`), macOS Keychain (`keyring` / `security` CLI), Linux Secret Service via `libsecret` / `keyring`.

**Pros:**
- Best future desktop direction — the key lives in the user's OS-protected credential store
- Avoids plain-text app config files entirely
- User-specific and protected by OS account authentication
- Supports deletion (remove credential entry) and rotation (overwrite credential entry)
- Does not require the app to manage encryption keys
- Standard approach for desktop apps that handle credentials (e.g. git credential helpers, password managers)
- Python `keyring` library provides a cross-platform abstraction

**Cons:**
- Platform-specific integration complexity: Windows CNG, macOS Security framework, Linux D-Bus / libsecret differ significantly
- Testing complexity: unit tests cannot easily mock OS keychain in CI without a real credential store
- Packaging complexity: may require additional OS permissions or entitlements in packaged app
- Linux desktop environments vary (GNOME Keyring vs. KDE Wallet vs. headless server with no keychain)
- First-time setup may prompt the user for OS authentication (expected behavior, but can surprise users)

**Verdict:** Recommended for future production desktop release. Should be implemented in TASK-053.

---

### Option C — Encrypted Local File

**Description:** The backend stores the key in a local file, encrypted with a separate key derived from a passphrase or a machine-specific secret.

**Pros:**
- Cross-platform: a single Python implementation works everywhere
- Easier to implement than OS keychain in some environments (e.g. headless Linux server)
- Does not require OS keychain integration

**Cons:**
- Key management problem: the encryption key must come from somewhere. Common approaches (hardcoded key, machine-id-derived key, passphrase prompt) each have significant weaknesses.
- A hardcoded encryption key provides no real protection — the attacker who has the file likely has the binary too.
- Machine-id-derived key is fragile across reinstalls and does not protect against local user access.
- Passphrase prompt defeats the UX benefit of persistent storage.
- Can create a false sense of security — encrypted files are not equivalent to OS keychain protection.
- Higher implementation risk: custom crypto code is error-prone; cryptographic libraries still need to be chosen and audited.
- The encrypted file itself still needs to be stored somewhere, and that location may be accessible to other local processes.

**Verdict:** Not recommended for MVP. If used in future, must be backed by a security review. OS keychain is preferred.

---

### Option D — Plain Local Config File or SQLite

**Description:** The backend stores the key in a plain `.env` file, `config.json`, `settings.toml`, or in a SQLite column without encryption.

**Pros:**
- Easiest to implement — a single file write or INSERT statement

**Cons:**
- Not acceptable for real API keys under any circumstances
- High leakage risk: the file may be included in backups, screenshots, debug exports, git commits, or crash reports
- SQLite database files are frequently included in backup tools and cloud sync
- Any local user or process with file system read access can extract the key immediately
- Violation of BYOK Product and Settings Design rules and TASK-048 API key handling rules

**Verdict:** Explicitly forbidden for real API keys. Never implement this path.

---

## 4. Recommendation

| Phase | Recommended Storage | Rationale |
|---|---|---|
| Dev / internal testing (current) | Environment Variable Only (Option A) | Safest, simplest, no persistence risk |
| Future production desktop MVP | OS Keychain / Credential Manager (Option B) | Industry standard, OS-protected, supports deletion |
| Explicitly forbidden | Plain SQLite / plain config file (Option D) | Unacceptable leakage risk |
| Deferred / not recommended for MVP | Encrypted local file (Option C) | Higher complexity, weaker protection than OS keychain |

---

## 5. Recommended MVP Strategy

The following sequence is required before any real user API key can be stored persistently:

1. **Do not implement persistent user key storage yet.** The current dev phase uses environment variables only. This remains the only approved path until TASK-053 is complete.
2. **Continue using environment variables for dev / testing.** `LLM_API_KEY` env var is the only approved key source during development and internal smoke tests.
3. **Implement Provider Settings UI/API only after key storage design is accepted.** `POST /provider/settings/key` (designed in TASK-048) must not be implemented until TASK-053 (Secure Key Storage Implementation) is complete and reviewed.
4. **When implementing BYOK for real users, prefer OS keychain.** Use Python `keyring` library or equivalent. Platform-specific fallbacks (Windows Credential Manager, macOS Keychain, Linux libsecret) are acceptable in that order.
5. **Plain SQLite must not store real API keys.** This constraint must be enforced in code review and documented in the implementation task.
6. **Any persistent key write path must be tested** for the conditions listed in Section 9 (Testing Requirements).

---

## 6. Key Lifecycle

The following operations must be supported by the future key storage implementation:

| Operation | Description | Safety Rule |
|---|---|---|
| **Add key** | User submits key via `POST /provider/settings/key`. Backend writes to secure storage. | Key must never be echoed back in response. Must not be written to SQLite, logs, or plain file. |
| **Replace key** | User submits a new key when one already exists. Backend overwrites the previous stored secret. | Old key must be securely overwritten — not merely appended. No old key value should remain in storage after replace. |
| **Clear key** | User triggers `DELETE /provider/settings/key`. Backend removes the stored secret. | Clear must be available at all times. On success, `key_status` returns `not_configured`. Must be idempotent. |
| **Test key** | User triggers `POST /provider/settings/test`. Backend reads key from secure storage and uses it for one minimal provider call. | Key is read internally only — never sent to frontend. `explicit_cost_ack: true` required. |
| **Rotate key** | User replaces an existing key with a new one (same as Replace key in MVP). | Future: may include a grace period where the old key remains valid until the new key is confirmed. Not in Phase 4 scope. |
| **App uninstall** | User uninstalls the desktop app. | OS keychain entries are **not** automatically removed by app uninstall in most OS implementations. Documentation must inform the user how to manually clear credentials after uninstall. |
| **Debug export** | Any diagnostic export or crash report generated by the app. | Debug exports must exclude API key values. The export routine must explicitly filter any field whose name matches `api_key`, `LLM_API_KEY`, `key`, `token`, `Bearer`, or `sk-` prefix patterns. |

---

## 7. API Integration Rules

The following rules govern how the future key storage layer integrates with the Provider Settings API (designed in TASK-048):

| Endpoint | Key Storage Interaction |
|---|---|
| `POST /provider/settings/key` | Accepts key in request body → writes to secure storage layer only. Never writes to SQLite column, plain file, or log. |
| `DELETE /provider/settings/key` | Deletes entry from secure storage. Idempotent — returns success even if no key exists. |
| `GET /provider/settings` | Returns `key_status` field only. Never reads key value for the response. |
| `PATCH /provider/settings` | Never accepts key. Non-key settings only. |
| `POST /provider/settings/test` | Reads key from secure storage internally for provider call. Never includes key in request to provider beyond Authorization header. Never returns key in response. |

The secure storage layer must be a dedicated internal module (e.g. `backend/app/core/key_storage.py`) that:
- Exposes `store_key(provider, key)`, `get_key(provider)`, `delete_key(provider)`, `has_key(provider)` — no other public interface
- Never logs key values
- Has a `__repr__` / `__str__` that does not expose key values if the module holds state

---

## 8. Key Status Model

The `key_status` field used across Provider Settings API endpoints uses the following canonical values. No endpoint returns the key value or any fragment of the key.

| Value | Meaning |
|---|---|
| `not_configured` | No key has been stored for this provider |
| `configured` | A key has been stored; it has not been tested yet, or was last tested successfully |
| `invalid` | The key failed format validation on save, or the provider rejected it with a 401 |
| `not_tested` | A key is stored but no test has been run since it was last saved |
| `test_success` | The most recent `POST /provider/settings/test` call returned 2xx |
| `test_failed` | The most recent `POST /provider/settings/test` call returned an error |

Rules:
- `configured` does not imply the key is valid — only that it has been stored.
- `key_status` must never contain the key value or any derivable fragment.
- Status transitions: `not_configured` → (save) → `not_tested` → (test success) → `test_success` / (test fail) → `test_failed` / (save new key) → `not_tested`.

---

## 9. Redaction Rules

The following redaction rules must be enforced across all layers of the backend:

| Location | Rule |
|---|---|
| Log lines (all levels) | API key must be redacted before any log call. Pattern match on `sk-`, `Bearer `, `api_key`, `token` prefixes and redact value. |
| Exception messages | If an exception message contains the key (e.g. from an HTTP library), the exception must be caught and re-raised with the key redacted. |
| `repr()` / `__repr__` | Any object that holds the key must implement `__repr__` returning `<...key=REDACTED>` or equivalent. |
| `str()` / `__str__` | Same as `__repr__`. |
| `stdout` / `stderr` | Key must not appear in any print statement, uvicorn access log, or framework debug output. |
| Crash traces shown to user | Crash report UI must filter key values. Backend must not include key in any error context forwarded to frontend. |
| Memory records (`Memory` table) | Key must never be stored in any `Memory` row. |
| Audit logs (`MemoryInjectionAudit` table) | Key must never be stored in any audit row. |
| Usage records | Key must never appear in any usage meter row or export. |
| Chat history | Key must never appear in any `Message` or conversation record. |
| Screenshots / debug exports | Debug export routine must explicitly exclude key-adjacent fields. |

---

## 10. Testing Requirements for Future Implementation

When TASK-053 (Secure Key Storage Implementation) is implemented, the following tests must be added:

| Test | What to verify |
|---|---|
| Key not returned by GET | `GET /provider/settings` response never contains `api_key` or key value |
| Key not in caplog | After `POST /provider/settings/key`, caplog at all levels contains no key value |
| Key not in stdout/stderr | After key save and test, captured stdout/stderr contains no key value |
| Key not in SQLite | After key save, no SQLite column contains the key value |
| Key clear removes stored key | After `DELETE /provider/settings/key`, `has_key(provider)` returns False |
| Replace key overwrites old key | After second `POST /provider/settings/key`, old key is no longer retrievable from storage |
| Provider test uses key without exposing it | `POST /provider/settings/test` response contains no key value; caplog contains no key value |
| No frontend bundle contains key | Electron renderer bundle and IPC messages contain no key value |
| No debug export contains key | Debug export output contains no key-adjacent values |
| repr redacts key | `repr(provider_adapter)` and `repr(key_storage)` do not contain key value |

---

## 11. Threat Model

The following threats are considered relevant to API key storage in a desktop BYOK app:

| Threat | Description | Mitigation |
|---|---|---|
| Accidental git commit | Developer commits `.env` file or config file containing key | `.gitignore` covers `.env` and config files; key is never written to app-managed config files |
| Log file exposure | Application logs written to disk contain key value | Redaction rules (Section 9) applied at all log call sites |
| Frontend renderer exposure | Key sent to Electron renderer process via IPC | Key is backend-only; no IPC message ever contains key; `GET /provider/settings` never returns key |
| Local database leakage | Key stored in SQLite accessible to local file system | Plain SQLite storage explicitly forbidden (Section 3, Option D); key stored in OS keychain only |
| Debug export leakage | Developer exports diagnostics; export contains key | Debug export routine must filter key-adjacent fields; tested in TASK-053 |
| Malicious local user | Another user account on the same machine reads the key | OS keychain storage is user-account-scoped on Windows and macOS, providing some isolation |
| Malware on machine | Local malware reads process memory or keychain | Cannot be fully solved at the application layer; OS keychain still reduces attack surface vs. plain file |
| OS account compromise | Attacker gains the user's OS credentials and accesses keychain | Cannot be solved at the application layer; this is the residual risk accepted in the threat model |
| Shell history exposure | User ran `export LLM_API_KEY=sk-...` in shell; key appears in `.bash_history` | Dev-phase limitation; documented; users advised to use `.env` files loaded by the backend, not shell export |

**Important:** Local malware and OS account compromise cannot be fully solved by application-level design. The design still minimizes accidental leakage (git, logs, database, frontend, debug export) which are the most common and preventable exposure vectors.

---

## 12. Future Implementation Sequence

The recommended task order, taking into account the dependency constraints in TASK-048:

| Task | Name | Type | Key Storage Dependency |
|---|---|---|---|
| TASK-050 | Usage Meter Implementation | Implementation | None — no key storage needed |
| TASK-051 | Backend Provider Settings API Implementation | Implementation | Depends on TASK-053 for key-writing endpoint |
| TASK-052 | Provider Settings UI Implementation | Implementation | Depends on TASK-051 |
| TASK-053 | Secure Key Storage Implementation | Implementation | This design (TASK-049) must be accepted first |
| TASK-054 | Provider Settings Key Endpoint Implementation | Implementation | Depends on TASK-053 |
| TASK-055 | Provider Settings Key UI Enablement Design | Design | Depends on TASK-054 |

**Current ordering note:** TASK-051 and TASK-052 implemented only safe non-secret surfaces. TASK-053 adds the key storage abstraction. TASK-054 wires `POST /provider/settings/key` and `DELETE /provider/settings/key` to that abstraction without enabling live provider tests.

Proposed adjusted order for implementation phase:
1. TASK-050 — Usage Meter Implementation (no key dependency; can start any time)
2. TASK-053 — Secure Key Storage Implementation (must precede key endpoint)
3. TASK-051 — Backend Provider Settings API Implementation (non-secret endpoints only)
4. TASK-052 — Provider Settings UI Implementation (non-secret UI only)
5. TASK-054 — Provider Settings Key Endpoint Implementation (depends on TASK-053)
6. TASK-055 — Provider Settings Key UI Enablement Design (depends on TASK-054)

---

## 13. Non-Goals

| Out of Scope | Reason |
|---|---|
| Key endpoint wiring | In progress in TASK-054 |
| Live provider test connection | Deferred until after key endpoints are safe |
| Encrypted file implementation | Not recommended for MVP; deferred |
| Provider API call | Design task — no live calls |
| Broad OS keychain compatibility validation | Deferred until packaging/live smoke phase |
| Payment or billing system | Not in Phase 4 |
| Hosted account management | Not in Phase 4 |
| Multi-user key isolation | Single-user desktop app in Phase 4 |
| Automatic key rotation | Future phase |
| Key revocation via provider API | Not in Phase 4 |

---

## 14. Relationship to Existing Documents

| Document | Relationship |
|---|---|
| `docs/PROVIDER_SETTINGS_API_DESIGN.md` | Defines the API surface that depends on this storage design. `POST /provider/settings/key` must not be implemented until this design is accepted. |
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | Defines the BYOK product model and key ownership rules. This document adds the concrete storage comparison and recommendation. |
| `docs/LLM_ADAPTER_DESIGN.md` | Section 5.7 (Redaction Utility Requirement) defines the redaction utility that must be used in the key storage layer. |
| `docs/USAGE_METER_DESIGN.md` | Section 3 (What Must Not Be Tracked) includes API key as a forbidden field. Key storage implementation must ensure key never flows into usage records. |
| `docs/COST_AND_MONETIZATION.md` | Defines live smoke go/no-go criteria. Any path that stores a real key and enables a live provider call must satisfy those criteria. |
