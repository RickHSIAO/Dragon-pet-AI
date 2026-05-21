/**
 * dragon-pet-ai — renderer process (TASK-003 skeleton)
 *
 * Responsibilities:
 * - Read user message from input
 * - POST to backend /chat
 * - Display user message and pet reply in chat area
 * - Show clear error if backend is unreachable
 *
 * Safety: no shell execution, no file access, no AI API calls here.
 * Backend URL is read from the URL query param set by main.js.
 */

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const params = new URLSearchParams(window.location.search);
const BACKEND_URL = params.get("backend") || "http://localhost:8000";

// ---------------------------------------------------------------------------
// DOM refs
// ---------------------------------------------------------------------------
const chatArea    = document.getElementById("chat-area");
const msgInput    = document.getElementById("message-input");
const sendBtn     = document.getElementById("send-btn");
const moodLabel   = document.getElementById("mood-label");
const chatSourceStatus = document.getElementById("chat-source-status");
const chatProviderStatus = document.getElementById("chat-provider-status");
const chatRuntimeStatus = document.getElementById("chat-runtime-status");
const memoryForm  = document.getElementById("memory-form");
const memoryType  = document.getElementById("memory-type");
const memoryContent = document.getElementById("memory-content");
const memoryImportance = document.getElementById("memory-importance");
const memoryConfidence = document.getElementById("memory-confidence");
const memoryStatus = document.getElementById("memory-status");
const memoryList = document.getElementById("memory-list");
const refreshMemoryBtn = document.getElementById("refresh-memory-btn");
const refreshPreviewBtn = document.getElementById("refresh-preview-btn");
const memoryPreviewMeta = document.getElementById("memory-preview-meta");
const memoryContextText = document.getElementById("memory-context-text");
// TASK-023: memory-aware chat toggle (per-request opt-in)
const useMemoryToggle = document.getElementById("use-memory-toggle");
// TASK-027: audit logs section
const refreshAuditBtn  = document.getElementById("refresh-audit-btn");
const auditLimitInput  = document.getElementById("audit-limit");
const auditOffsetInput = document.getElementById("audit-offset");
const auditStatusEl    = document.getElementById("audit-status");
const auditList        = document.getElementById("audit-list");
// TASK-052: provider settings UI, non-secret settings only
const providerSettingsForm = document.getElementById("provider-settings-form");
const providerSettingsProvider = document.getElementById("provider-settings-provider");
const providerSettingsModel = document.getElementById("provider-settings-model");
const providerRealEnabled = document.getElementById("provider-real-enabled");
const providerLlmChatEnabled = document.getElementById("provider-llm-chat-enabled");
const providerFallbackToMock = document.getElementById("provider-fallback-to-mock");
const refreshProviderSettingsBtn = document.getElementById("refresh-provider-settings-btn");
const providerKeyStatus = document.getElementById("provider-key-status");
const providerLastTestStatus = document.getElementById("provider-last-test-status");
const providerResolvedProvider = document.getElementById("provider-resolved-provider");
const providerCurrentProvider = document.getElementById("provider-current-provider");
const providerCurrentModel = document.getElementById("provider-current-model");
const providerRealEnabledStatus = document.getElementById("provider-real-enabled-status");
const providerLlmChatEnabledStatus = document.getElementById("provider-llm-chat-enabled-status");
const providerFallbackStatus = document.getElementById("provider-fallback-status");
const providerSettingsStatus = document.getElementById("provider-settings-status");
const providerUsageSummary = document.getElementById("provider-usage-summary");
const providerWarning = document.getElementById("provider-warning");
// TASK-056 / TASK-060: provider key save/clear/test controls
// Safety: key value is never logged, never stored in localStorage/sessionStorage,
// never sent to external providers, cleared from DOM immediately after every save attempt.
// Test Connection: only calls local backend POST /provider/settings/test.
// No api_key, prompt, memory_context, or chat history is sent to test endpoint.
// No automatic test after Save Key.
const providerApiKeyInput       = document.getElementById("provider-api-key-placeholder");
const saveProviderKeyBtn        = document.getElementById("save-provider-key-btn");
const clearProviderKeyBtn       = document.getElementById("clear-provider-key-btn");
const testProviderConnectionBtn = document.getElementById("test-provider-connection-btn");
const providerKeyMsg            = document.getElementById("provider-key-msg");
const providerTestMsg           = document.getElementById("provider-test-msg");

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let currentMood = "neutral";
let isSending   = false;
// TASK-060: track in-flight test connection to prevent double-click
let isTestingConnection = false;
// TASK-060: cache last-loaded provider settings for Test Connection enable conditions
let currentProviderSettings = {};
let lastChatSource = "not_checked";
let lastChatStatusMessage = "No chat response yet.";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function appendMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const sender = document.createElement("div");
  sender.className = "sender";
  sender.textContent =
    role === "user"   ? "You" :
    role === "pet"    ? "Dragon Pet" :
    role === "error"  ? "Error" :
    "System";

  const body = document.createElement("div");
  body.textContent = text;

  wrap.appendChild(sender);
  wrap.appendChild(body);
  chatArea.appendChild(wrap);
  chatArea.scrollTop = chatArea.scrollHeight;
  return wrap;
}

function setMood(mood) {
  currentMood = mood || "neutral";
  moodLabel.textContent = currentMood;
}

function setSending(state) {
  isSending = state;
  sendBtn.disabled = state;
  msgInput.disabled = state;
  sendBtn.textContent = state ? "Sending..." : "Send";
}

function isFetchNetworkError(err) {
  const name = err && err.name ? String(err.name) : "";
  const message = err && err.message ? String(err.message) : "";
  return name === "TypeError" && message.toLowerCase().includes("fetch");
}

function providerSummary(settings = currentProviderSettings) {
  const provider = settings.provider || "mock";
  const resolved = settings.resolved_provider || "mock";
  const model = settings.model || "default";
  return `provider: ${provider} | resolved: ${resolved} | model: ${model}`;
}

function isOllamaChatPath(settings = currentProviderSettings) {
  return (
    (settings.provider === "ollama" || settings.resolved_provider === "ollama") &&
    Boolean(settings.real_provider_enabled) &&
    Boolean(settings.llm_chat_enabled)
  );
}

function sourceStatusMessage(source, settings = currentProviderSettings) {
  if (source === "llm_local") {
    return "source=llm_local - local Ollama reply received through the backend.";
  }
  if (source === "llm_local_error") {
    return "source=llm_local_error - local provider failed safely. Check Ollama server, model name, or timeout.";
  }
  if (source === "mock") {
    if (settings.resolved_provider === "ollama" && !settings.llm_chat_enabled) {
      return "source=mock - LLM chat is disabled, so /chat is using mock.";
    }
    if (settings.resolved_provider === "ollama" && settings.fallback_to_mock !== false) {
      return "source=mock - Ollama is configured, but fallback_to_mock is enabled or a provider failure fell back to mock.";
    }
    if (settings.provider === "ollama" || settings.resolved_provider === "ollama") {
      return "source=mock - Ollama is selected but /chat resolved to mock. Refresh settings and check backend state.";
    }
    return "source=mock - mock provider response.";
  }
  if (source === "llm_real") {
    return "source=llm_real - cloud provider response through the backend.";
  }
  if (source === "llm_real_error") {
    return "source=llm_real_error - cloud provider failed safely.";
  }
  if (source === "pending") {
    return isOllamaChatPath(settings)
      ? "Waiting for local Ollama. The first response can take longer while the model wakes up."
      : "Waiting for backend chat response.";
  }
  if (source === "backend_offline") {
    return "source=backend_offline - backend is not reachable.";
  }
  return "Chat source will appear after the next response.";
}

function setChatRuntimeStatus(source, message = "", state = "normal") {
  lastChatSource = source || lastChatSource || "not_checked";
  lastChatStatusMessage = message || sourceStatusMessage(lastChatSource);

  chatSourceStatus.textContent = `source: ${lastChatSource}`;
  chatSourceStatus.className =
    state === "error"
      ? "chat-runtime-pill error"
      : state === "pending"
        ? "chat-runtime-pill pending"
        : "chat-runtime-pill";
  chatProviderStatus.textContent = providerSummary();
  chatRuntimeStatus.textContent = lastChatStatusMessage;
  chatRuntimeStatus.className = state === "error" ? "status-note error" : "status-note";
}

function syncChatRuntimeProviderStatus() {
  chatProviderStatus.textContent = providerSummary();
  if (lastChatSource === "not_checked") {
    setChatRuntimeStatus("not_checked", sourceStatusMessage("not_checked"));
  } else {
    chatRuntimeStatus.textContent = lastChatStatusMessage;
  }
}

function safeChatErrorMessage(status, detail) {
  const category = typeof detail === "string" ? detail : "";
  if (category === "ollama_unavailable") {
    return "Local Ollama is unavailable. Start Ollama, then retry.";
  }
  if (category === "model_not_found") {
    return "Local model was not found. Pull the configured model, then retry.";
  }
  if (category === "provider_timeout") {
    return "Provider timed out. Local models can take longer on cold start; retry after the model is loaded.";
  }
  if (category === "invalid_response") {
    return "Provider returned an invalid response. Check provider logs and try again.";
  }
  if (category === "provider_error") {
    return "Provider call failed safely. Check provider settings and try again.";
  }
  return `Backend returned HTTP ${status}.`;
}

function setMemoryStatus(text, isError = false) {
  memoryStatus.textContent = text;
  memoryStatus.className = isError ? "memory-status error" : "memory-status";
}

function formatBackendError(err) {
  const isNetworkError = isFetchNetworkError(err);
  if (isNetworkError) {
    return `Cannot reach backend at ${BACKEND_URL}. Start the backend first.`;
  }
  return err.message || "Memory request failed.";
}

async function parseJsonResponse(res) {
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (!res.ok) {
    const detail = data && data.detail ? data.detail : `HTTP ${res.status}`;
    throw new Error(`Backend returned ${detail}`);
  }
  return data;
}

function renderMemoryList(memories) {
  memoryList.replaceChildren();

  if (!memories.length) {
    const empty = document.createElement("div");
    empty.className = "memory-empty";
    empty.textContent = "No active memories.";
    memoryList.appendChild(empty);
    return;
  }

  for (const memory of memories) {
    const item = document.createElement("article");
    item.className = "memory-item";

    const header = document.createElement("div");
    header.className = "memory-item-header";

    const title = document.createElement("div");
    title.className = "memory-item-title";
    title.textContent = `#${memory.id} ${memory.memory_type}`;

    const deactivateBtn = document.createElement("button");
    deactivateBtn.type = "button";
    deactivateBtn.textContent = "Deactivate";
    deactivateBtn.addEventListener("click", () => deactivateMemory(memory.id));

    header.appendChild(title);
    header.appendChild(deactivateBtn);

    const content = document.createElement("div");
    content.className = "memory-item-content";
    content.textContent = memory.content;

    const meta = document.createElement("div");
    meta.className = "memory-item-meta";
    meta.textContent =
      `importance=${memory.importance} | confidence=${memory.confidence} | source=${memory.source || "none"}`;

    item.appendChild(header);
    item.appendChild(content);
    item.appendChild(meta);
    memoryList.appendChild(item);
  }
}

async function createMemory() {
  const content = memoryContent.value.trim();
  if (!content) {
    setMemoryStatus("Memory content cannot be blank.", true);
    memoryContent.focus();
    return;
  }

  setMemoryStatus("Saving memory...");

  try {
    const res = await fetch(`${BACKEND_URL}/memory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        memory_type: memoryType.value,
        content,
        importance: Number(memoryImportance.value || 50),
        confidence: memoryConfidence.value,
        source: "manual",
      }),
    });

    await parseJsonResponse(res);
    memoryContent.value = "";
    setMemoryStatus("Memory saved.");
    await loadMemories();
    await loadMemoryContextPreview();
  } catch (err) {
    setMemoryStatus(formatBackendError(err), true);
  }
}

async function loadMemories() {
  setMemoryStatus("Loading memories...");

  try {
    const res = await fetch(`${BACKEND_URL}/memory`);
    const memories = await parseJsonResponse(res);
    renderMemoryList(memories);
    setMemoryStatus(`Loaded ${memories.length} active memories.`);
  } catch (err) {
    renderMemoryList([]);
    setMemoryStatus(formatBackendError(err), true);
  }
}

async function deactivateMemory(id) {
  setMemoryStatus(`Deactivating memory #${id}...`);

  try {
    const res = await fetch(`${BACKEND_URL}/memory/${id}`, {
      method: "DELETE",
    });
    await parseJsonResponse(res);
    setMemoryStatus(`Memory #${id} deactivated.`);
    await loadMemories();
    await loadMemoryContextPreview();
  } catch (err) {
    setMemoryStatus(formatBackendError(err), true);
  }
}

async function loadMemoryContextPreview() {
  try {
    const res = await fetch(`${BACKEND_URL}/memory/context-preview`);
    const preview = await parseJsonResponse(res);
    memoryPreviewMeta.textContent = `count: ${preview.count} - source: ${preview.source}`;
    memoryContextText.textContent = preview.context_text;
  } catch (err) {
    memoryPreviewMeta.textContent = "count: 0 - source: manual_memory_preview";
    memoryContextText.textContent = formatBackendError(err);
  }
}

// ---------------------------------------------------------------------------
// Audit Logs (TASK-027) — GET /memory/audit
// ---------------------------------------------------------------------------

/**
 * Load memory injection audit records from GET /memory/audit.
 *
 * Safety rules enforced here:
 * - Only safe metadata fields are rendered (id, timestamps, IDs, counts).
 * - selected_memory_ids is displayed as a plain list of integers only.
 *   It is NOT expanded into memory content via additional API calls.
 * - No prompt text, no approved context text, no raw memory content.
 * - /chat payload is never modified by this function.
 */
function setAuditStatus(text, isError = false) {
  auditStatusEl.textContent = text;
  auditStatusEl.className = isError ? "audit-status error" : "audit-status";
}

function renderAuditList(items, meta) {
  auditList.replaceChildren();

  if (meta) {
    const summary = document.createElement("div");
    summary.className = "audit-summary";
    summary.textContent =
      `Showing ${items.length} of ${meta.count} records  |  limit: ${meta.limit}  offset: ${meta.offset}`;
    auditList.appendChild(summary);
  }

  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "audit-empty";
    empty.textContent = "No audit records found.";
    auditList.appendChild(empty);
    return;
  }

  for (const item of items) {
    const card = document.createElement("article");
    card.className = "audit-card";

    // Title row
    const title = document.createElement("div");
    title.className = "audit-card-title";
    title.textContent = `Audit #${item.id}`;
    card.appendChild(title);

    // Metadata rows — safe fields only, no memory content
    const rows = [
      ["Created",         formatDateTime(item.created_at)],
      ["Conversation",    item.conversation_id != null ? `#${item.conversation_id}` : "none"],
      ["Selected IDs",    item.selected_memory_ids && item.selected_memory_ids.length
                            ? `[${item.selected_memory_ids.join(", ")}]`
                            : "[]"],
      ["Selected count",  String(item.selected_count)],
      ["Context chars",   String(item.total_context_chars)],
      ["Flag enabled",    item.feature_flag_enabled ? "true" : "false"],
      ["Exclusion",       item.exclusion_summary
                            ? JSON.stringify(item.exclusion_summary)
                            : "none"],
    ];

    const table = document.createElement("dl");
    table.className = "audit-card-meta";
    for (const [label, value] of rows) {
      const dt = document.createElement("dt");
      dt.textContent = label;
      const dd = document.createElement("dd");
      dd.textContent = value;
      table.appendChild(dt);
      table.appendChild(dd);
    }
    card.appendChild(table);
    auditList.appendChild(card);
  }
}

function formatDateTime(isoString) {
  if (!isoString) return "unknown";
  try {
    return new Date(isoString).toLocaleString();
  } catch {
    return isoString;
  }
}

async function loadAuditLogs() {
  const limit  = Math.max(1, Math.min(100, Number(auditLimitInput.value)  || 20));
  const offset = Math.max(0,              Number(auditOffsetInput.value) || 0);

  setAuditStatus("Loading audit logs...");

  try {
    const res = await fetch(
      `${BACKEND_URL}/memory/audit?limit=${limit}&offset=${offset}`
    );
    const data = await parseJsonResponse(res);

    renderAuditList(data.items, {
      count:  data.count,
      limit:  data.limit,
      offset: data.offset,
    });
    setAuditStatus(
      `Loaded ${data.items.length} record(s). Total in DB: ${data.count}.`
    );
  } catch (err) {
    renderAuditList([], null);
    setAuditStatus(formatBackendError(err), true);
  }
}

// ---------------------------------------------------------------------------
// Provider Settings (TASK-052) - local backend only, non-secret settings only
// ---------------------------------------------------------------------------
function setProviderSettingsStatus(message, isError = false) {
  providerSettingsStatus.textContent = message;
  providerSettingsStatus.className = isError
    ? "provider-settings-status error"
    : "provider-settings-status";
}

function formatCountMap(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    return "none";
  }
  const entries = Object.entries(value);
  if (!entries.length) return "none";
  return entries.map(([key, count]) => `${key}: ${count}`).join(", ");
}

function renderUsageSummary(usageSummary) {
  providerUsageSummary.replaceChildren();

  const safeSummary = usageSummary || {};
  const rows = [
    ["Requests", String(safeSummary.request_count || 0)],
    ["Source counts", formatCountMap(safeSummary.source_counts)],
    ["Provider counts", formatCountMap(safeSummary.provider_counts)],
    ["Model counts", formatCountMap(safeSummary.model_counts)],
    ["Input tokens", String(safeSummary.estimated_input_tokens || 0)],
    ["Output tokens", String(safeSummary.estimated_output_tokens || 0)],
    ["Total tokens", String(safeSummary.estimated_total_tokens || 0)],
    ["Fallbacks", String(safeSummary.fallback_count || 0)],
    ["Memory used", String(safeSummary.memory_used_count || 0)],
    ["Error counts", formatCountMap(safeSummary.error_counts)],
  ];

  for (const [label, value] of rows) {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    providerUsageSummary.appendChild(dt);
    providerUsageSummary.appendChild(dd);
  }
}

function renderProviderSettings(settings) {
  providerSettingsProvider.value = settings.provider || "mock";
  providerSettingsModel.value = settings.model || "";
  providerRealEnabled.checked = Boolean(settings.real_provider_enabled);
  providerLlmChatEnabled.checked = Boolean(settings.llm_chat_enabled);
  providerFallbackToMock.checked = settings.fallback_to_mock !== false;
  providerCurrentProvider.textContent = settings.provider || "mock";
  providerCurrentModel.textContent = settings.model || "default";
  providerKeyStatus.textContent = settings.key_status || "not_configured";
  providerLastTestStatus.textContent = settings.last_test_status || "not_tested";
  providerResolvedProvider.textContent = settings.resolved_provider || "mock";
  providerRealEnabledStatus.textContent = String(Boolean(settings.real_provider_enabled));
  providerLlmChatEnabledStatus.textContent = String(Boolean(settings.llm_chat_enabled));
  providerFallbackStatus.textContent = String(settings.fallback_to_mock !== false);
  providerWarning.textContent = settings.provider === "ollama"
    ? "Ollama runs locally and uses your CPU/GPU. No API key is required; the renderer still calls only the backend."
    : "Using a real provider may incur charges from your API provider.";
  renderUsageSummary(settings.usage_summary);
  // TASK-056 / TASK-060: cache settings and update all key UI controls
  currentProviderSettings = settings;
  syncChatRuntimeProviderStatus();
  updateKeyUIState(settings);
}

async function loadProviderSettings() {
  setProviderSettingsStatus("Loading provider settings...");

  try {
    const res = await fetch(`${BACKEND_URL}/provider/settings`);
    const settings = await parseJsonResponse(res);
    renderProviderSettings(settings);
    setProviderSettingsStatus("Provider settings loaded.");
  } catch (err) {
    renderUsageSummary(null);
    setProviderSettingsStatus(formatBackendError(err), true);
  }
}

async function saveProviderSettings() {
  setProviderSettingsStatus("Saving non-secret provider settings...");

  try {
    const body = {
      provider: providerSettingsProvider.value,
      model: providerSettingsModel.value.trim() || null,
      real_provider_enabled: providerRealEnabled.checked,
      llm_chat_enabled: providerLlmChatEnabled.checked,
      fallback_to_mock: providerFallbackToMock.checked,
    };

    const res = await fetch(`${BACKEND_URL}/provider/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const settings = await parseJsonResponse(res);
    renderProviderSettings(settings);
    setProviderSettingsStatus("Non-secret provider settings saved.");
  } catch (err) {
    setProviderSettingsStatus(formatBackendError(err), true);
  }
}

// ---------------------------------------------------------------------------
// Provider Key Save / Clear (TASK-056)
// Security rules:
//   - Key value is NEVER written to any console.* call.
//   - Key value is NEVER stored in localStorage or sessionStorage.
//   - Key value is NEVER sent to any external URL (only http://127.0.0.1:8000).
//   - Input field is cleared immediately after every save attempt.
//   - Test Connection remains disabled (TASK-058 deferred).
// ---------------------------------------------------------------------------

/**
 * Show a safe message near the key controls.
 * Never include API key value in `text`.
 */
function setProviderKeyMsg(text, isError = false) {
  providerKeyMsg.textContent = text;
  providerKeyMsg.className = isError ? "provider-key-msg error" : "provider-key-msg";
}

/**
 * Update key UI control states based on current provider settings.
 * Called by renderProviderSettings() after every settings load.
 *
 * Rules:
 * - API key input: enabled only for key-based providers (not mock, not ollama).
 * - Save Key / Clear Key: hidden for mock and local (ollama) providers.
 * - Test Connection (TASK-060 / TASK-076):
 *     - Cloud providers (anthropic): requires key + real_provider_enabled + no in-flight.
 *     - Local providers (ollama):    requires real_provider_enabled + no in-flight (no key check).
 *     - mock:                        always disabled.
 */
function updateKeyUIState(settings) {
  const provider = settings.provider || "mock";
  const isRealProvider = provider !== "mock";
  // TASK-076: local providers (ollama) do not require an API key
  const isLocalProvider = provider === "ollama";
  const keyStatus = settings.key_status || "not_configured";
  const realProviderEnabled = Boolean(settings.real_provider_enabled);

  // A key exists in any of these states (relevant for cloud providers only)
  const keyExists = [
    "configured", "not_tested", "invalid", "test_success", "test_failed",
  ].includes(keyStatus);

  // API key input: enabled only for key-based real providers
  providerApiKeyInput.disabled = !isRealProvider || isLocalProvider;
  if (!isRealProvider) {
    providerApiKeyInput.placeholder = "Not required for mock provider";
  } else if (isLocalProvider) {
    providerApiKeyInput.placeholder = "Not required — Ollama runs locally, no API key needed";
  } else {
    providerApiKeyInput.placeholder = "Enter provider API key";
  }

  // Save Key / Clear Key: hidden for mock and local providers
  if (!isRealProvider || isLocalProvider) {
    saveProviderKeyBtn.disabled = true;
    saveProviderKeyBtn.style.display = isLocalProvider ? "none" : "";
    clearProviderKeyBtn.style.display = "none";
  } else {
    // Cloud provider path (anthropic)
    saveProviderKeyBtn.style.display = "";
    saveProviderKeyBtn.disabled = !providerApiKeyInput.value.trim();
    clearProviderKeyBtn.style.display = keyExists ? "" : "none";
    clearProviderKeyBtn.disabled = false;
  }

  // Test Connection: conditions differ by provider type
  // - Local (ollama): only needs real_provider_enabled; no key required
  // - Cloud (anthropic): needs key + real_provider_enabled
  let canTest;
  if (!isRealProvider) {
    canTest = false;
  } else if (isLocalProvider) {
    canTest = realProviderEnabled && !isTestingConnection;
  } else {
    canTest = keyExists && realProviderEnabled && !isTestingConnection;
  }
  testProviderConnectionBtn.disabled = !canTest;

  // Update button title to explain disabled state
  if (!isRealProvider) {
    testProviderConnectionBtn.title = "Configure a real provider before testing.";
  } else if (isLocalProvider && !realProviderEnabled) {
    testProviderConnectionBtn.title = "Enable real provider (real_provider_enabled) before testing.";
  } else if (isLocalProvider && isTestingConnection) {
    testProviderConnectionBtn.title = "Test in progress...";
  } else if (isLocalProvider) {
    testProviderConnectionBtn.title =
      "Sends one minimal request to your local Ollama server. No data leaves your device.";
  } else if (!keyExists) {
    testProviderConnectionBtn.title = "Save an API key before testing.";
  } else if (!realProviderEnabled) {
    testProviderConnectionBtn.title = "Enable real provider (real_provider_enabled) before testing.";
  } else if (isTestingConnection) {
    testProviderConnectionBtn.title = "Test in progress...";
  } else {
    testProviderConnectionBtn.title =
      "Test Connection requires explicit cost acknowledgement. " +
      "Sends exactly one minimal request to your provider via local backend.";
  }
}

/**
 * Save API key to local backend via POST /provider/settings/key.
 *
 * Safety invariants:
 * - The key value is NEVER passed to console.log / console.warn / console.error.
 * - The request body is NEVER logged.
 * - The input field is cleared immediately after fetch() completes.
 * - Only calls local backend (BACKEND_URL = http://127.0.0.1:8000 or localhost:8000).
 */
async function saveProviderKey() {
  const provider = providerSettingsProvider.value;
  const keyValue = providerApiKeyInput.value;

  if (!keyValue.trim()) {
    setProviderKeyMsg("API key cannot be empty.", true);
    return;
  }

  if (!provider || provider === "mock") {
    setProviderKeyMsg("Select a real provider before saving a key.", true);
    providerApiKeyInput.value = "";
    return;
  }

  saveProviderKeyBtn.disabled = true;
  saveProviderKeyBtn.textContent = "Saving…";
  setProviderKeyMsg("Saving key...");

  let res;
  try {
    // Safety: body is never logged. Key value is never written to console.
    res = await fetch(`${BACKEND_URL}/provider/settings/key`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider, api_key: keyValue }),
    });
  } catch (fetchErr) {
    // Network error — clear input before surfacing message
    providerApiKeyInput.value = "";
    saveProviderKeyBtn.textContent = "Save API Key";
    const isNetworkError = isFetchNetworkError(fetchErr);
    setProviderKeyMsg(
      isNetworkError
        ? `Could not reach backend. Make sure the backend is running on localhost.`
        : "Could not save key. Please try again.",
      true
    );
    updateKeyUIState({ provider, key_status: providerKeyStatus.textContent });
    return;
  }

  // Clear input immediately after fetch completes — key must not remain in DOM
  providerApiKeyInput.value = "";
  saveProviderKeyBtn.textContent = "Save API Key";

  if (res.status === 503) {
    setProviderKeyMsg(
      "Secure key storage is unavailable in this environment. " +
      "Use an environment variable to set your API key for now.",
      true
    );
    updateKeyUIState({ provider, key_status: providerKeyStatus.textContent });
  } else if (res.status === 400) {
    setProviderKeyMsg(
      "API key not accepted. Check that your key is correct and still active on your provider account.",
      true
    );
    updateKeyUIState({ provider, key_status: providerKeyStatus.textContent });
  } else if (!res.ok) {
    setProviderKeyMsg("Could not save key. Please try again.", true);
    updateKeyUIState({ provider, key_status: providerKeyStatus.textContent });
  } else {
    setProviderKeyMsg("Key saved successfully.");
    await loadProviderSettings();
  }
}

/**
 * Clear stored API key via DELETE /provider/settings/key.
 * Requires a confirmation dialog before calling the backend.
 * Idempotent: 404 response is treated as success.
 */
async function clearProviderKey() {
  const provider = providerSettingsProvider.value;

  const confirmed = window.confirm(
    "This will permanently delete your stored API key. " +
    "The provider will revert to mock mode. Continue?"
  );
  if (!confirmed) return;

  clearProviderKeyBtn.disabled = true;
  setProviderKeyMsg("Clearing key...");

  let res;
  try {
    res = await fetch(
      `${BACKEND_URL}/provider/settings/key?provider=${encodeURIComponent(provider)}`,
      { method: "DELETE" }
    );
  } catch (fetchErr) {
    clearProviderKeyBtn.disabled = false;
    const isNetworkError = isFetchNetworkError(fetchErr);
    setProviderKeyMsg(
      isNetworkError
        ? "Could not reach backend. Make sure the backend is running on localhost."
        : "Could not clear key. Please try again.",
      true
    );
    return;
  }

  clearProviderKeyBtn.disabled = false;

  if (res.status === 503) {
    setProviderKeyMsg(
      "Could not clear key. Secure key storage is unavailable in this environment.",
      true
    );
  } else if (res.ok || res.status === 404) {
    // 404 treated as idempotent success — key already not configured
    setProviderKeyMsg("Key cleared. Provider will fall back to mock mode.");
    await loadProviderSettings();
  } else {
    setProviderKeyMsg("Could not clear key. Please try again.", true);
  }
}

// ---------------------------------------------------------------------------
// Provider Test Connection (TASK-060)
// Security rules:
//   - Only calls local backend POST /provider/settings/test (never external provider).
//   - Request body contains ONLY: provider, model, explicit_cost_ack: true.
//   - No api_key, prompt, memory_context, conversation_history, tools in body.
//   - Response renders ONLY safe fields: status, safe_message, error_category,
//     source, usage_estimate. Never shows raw provider body, headers, diagnostics.
//   - Explicit cost acknowledgement (window.confirm) required on every click.
//   - No automatic test after Save Key.
//   - isTestingConnection flag prevents concurrent requests.
// ---------------------------------------------------------------------------

/**
 * Show a safe message in the test connection status area.
 * Never include API key value or raw provider body in `text`.
 */
function setProviderTestMsg(text, isError = false) {
  providerTestMsg.textContent = text;
  providerTestMsg.className = isError ? "provider-test-msg error" : "provider-test-msg";
}

/**
 * Run Test Connection: sends one minimal POST to local backend.
 *
 * Enable conditions vary by provider type:
 *   Cloud (anthropic):
 *     1. provider !== "mock"
 *     2. key_status is a "key exists" value
 *     3. real_provider_enabled === true
 *     4. isTestingConnection === false
 *   Local (ollama) — TASK-076:
 *     1. provider === "ollama"
 *     2. real_provider_enabled === true
 *     3. isTestingConnection === false  (no key required)
 *
 * Explicit acknowledgement is required via window.confirm() on every click.
 * For Ollama, the dialog shows a local resource warning (no monetary cost).
 * Cancelling the dialog sends no backend request.
 *
 * Request body sent: { provider, model, explicit_cost_ack: true }
 * Fields NOT sent: api_key, prompt, memory_context, conversation_history, tools.
 *
 * Safe response fields rendered: status, safe_message, error_category, source, usage_estimate.
 * Fields NOT rendered: raw provider body, API key, headers, diagnostics, prompt.
 */
async function runTestConnection() {
  // Guard: re-check enable conditions (button may be clicked programmatically)
  const provider = currentProviderSettings.provider || "mock";
  const keyStatus = currentProviderSettings.key_status || "not_configured";
  const realProviderEnabled = Boolean(currentProviderSettings.real_provider_enabled);
  const model = currentProviderSettings.model || "";
  // TASK-076: local providers bypass key check
  const isLocalProvider = provider === "ollama";

  const keyExists = [
    "configured", "not_tested", "invalid", "test_success", "test_failed",
  ].includes(keyStatus);

  if (!provider || provider === "mock") {
    setProviderTestMsg("Configure a real provider before testing.", true);
    return;
  }
  // Cloud providers require a saved key; local providers do not
  if (!isLocalProvider && !keyExists) {
    setProviderTestMsg("Save an API key before running Test Connection.", true);
    return;
  }
  if (!realProviderEnabled) {
    setProviderTestMsg("Enable real provider (real_provider_enabled) before testing.", true);
    return;
  }
  if (isTestingConnection) {
    return; // Silently ignore — button should already be disabled
  }

  // Acknowledgement dialog — content differs for local vs cloud providers
  let confirmed;
  if (isLocalProvider) {
    // TASK-076: local resource warning — no monetary cost
    confirmed = window.confirm(
      "Test Connection — Local Resource Warning\n\n" +
      "This will send a test request to your local Ollama server.\n" +
      "This will use your GPU/CPU for inference.\n" +
      "No data leaves your device.\n" +
      "The test sends exactly one minimal request.\n\n" +
      "Continue with Test Connection?"
    );
  } else {
    // Cloud provider — explicit cost acknowledgement
    confirmed = window.confirm(
      "Test Connection — Cost Acknowledgement\n\n" +
      "This may contact your configured provider.\n" +
      "This may incur provider charges.\n" +
      "The test sends exactly one minimal request.\n" +
      "No memory or chat history will be sent.\n\n" +
      "Continue with Test Connection?"
    );
  }
  if (!confirmed) {
    setProviderTestMsg("Test Connection cancelled.");
    return;
  }

  // Set in-flight state
  isTestingConnection = true;
  testProviderConnectionBtn.disabled = true;
  testProviderConnectionBtn.textContent = "Testing…";
  setProviderTestMsg("Sending test request to local backend...");

  let res;
  try {
    // Safety: body contains ONLY safe fields — no api_key, no prompt, no memory.
    res = await fetch(`${BACKEND_URL}/provider/settings/test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider,
        model: model || null,
        explicit_cost_ack: true,
      }),
    });
  } catch (fetchErr) {
    isTestingConnection = false;
    testProviderConnectionBtn.textContent = "Test Connection";
    updateKeyUIState(currentProviderSettings);
    const isNetworkError = isFetchNetworkError(fetchErr);
    setProviderTestMsg(
      isNetworkError
        ? "Could not reach backend. Make sure the backend is running on localhost."
        : "Test Connection request failed. Please try again.",
      true
    );
    return;
  }

  // Reset in-flight state before handling response
  isTestingConnection = false;
  testProviderConnectionBtn.textContent = "Test Connection";

  // Parse response safely — never render raw body
  let data = null;
  try {
    data = await res.json();
  } catch {
    data = null;
  }

  if (res.status === 400 && data && data.detail === "cost_ack_required") {
    // Should not occur if UI sends explicit_cost_ack: true — safe fallback message
    setProviderTestMsg(
      "Test Connection requires explicit cost acknowledgement. Please try again.",
      true
    );
  } else if (res.status === 503) {
    setProviderTestMsg(
      "Secure key storage is unavailable in this environment. " +
      "Set your API key as an environment variable and restart the backend.",
      true
    );
  } else if (res.status === 400) {
    // Other 400 errors (unknown provider, etc.)
    setProviderTestMsg(
      "Test Connection request was not accepted. Check provider and model settings.",
      true
    );
  } else if (!res.ok || !data) {
    setProviderTestMsg(
      "Test Connection failed. Please check your provider settings and try again.",
      true
    );
  } else {
    // Success or safe failure — render only safe fields from response
    // Never render: raw provider body, api_key, headers, diagnostics, prompt
    const status = data.status || "unknown";
    const safeMessage = data.safe_message || "";
    const errorCategory = data.error_category || "";
    const source = data.source || "";
    const usageEstimate = data.usage_estimate;

    // Build a safe display string from safe fields only
    let display = safeMessage || `Test result: ${status}`;
    if (errorCategory && status !== "success") {
      display += ` (${errorCategory})`;
    }
    if (source) {
      display += ` [source: ${source}]`;
    }
    if (usageEstimate) {
      const inputTok = usageEstimate.estimated_input_tokens;
      const outputTok = usageEstimate.estimated_output_tokens;
      if (inputTok != null || outputTok != null) {
        display += ` — tokens in: ${inputTok ?? "?"}, out: ${outputTok ?? "?"}`;
      }
    }

    const isError = status !== "success";
    setProviderTestMsg(display, isError);
  }

  // Refresh settings to pick up updated last_test_status / key_status
  await loadProviderSettings();
}

// ---------------------------------------------------------------------------
// Backend call
// ---------------------------------------------------------------------------
async function sendMessage(text) {
  if (isSending || !text.trim()) return;
  setSending(true);

  // Show user message immediately
  appendMessage("user", text);
  const loadingMessage = appendMessage(
    "status",
    isOllamaChatPath()
      ? "Local model is waking up. First Ollama responses can take longer..."
      : "Waiting for backend reply..."
  );
  setChatRuntimeStatus("pending", sourceStatusMessage("pending"), "pending");
  msgInput.value = "";
  msgInput.style.height = "auto";

  try {
    // TASK-023: include use_memory from the per-request toggle.
    // Backend MEMORY_INJECTION_ENABLED must also be true for injection to occur.
    // Memory content is never returned in the /chat response.
    const useMemory = useMemoryToggle ? useMemoryToggle.checked : false;

    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, use_memory: useMemory }),
    });

    const data = await res.json().catch(() => null);
    if (!res.ok) {
      const detail = data && data.detail ? data.detail : "";
      throw new Error(safeChatErrorMessage(res.status, detail));
    }

    loadingMessage.remove();
    appendMessage("pet", data.reply);
    setMood(data.mood);
    const source = data.source || "unknown";
    const isSourceError = source === "llm_local_error" || source === "llm_real_error";
    setChatRuntimeStatus(
      source,
      sourceStatusMessage(source),
      isSourceError ? "error" : "normal"
    );
    await loadProviderSettings();

  } catch (err) {
    const isNetworkError = isFetchNetworkError(err);
    const errText = isNetworkError
      ? `Cannot reach backend at ${BACKEND_URL}.\nMake sure the backend is running:\n  cd backend && uvicorn app.main:app --reload`
      : `Something went wrong: ${err.message}`;

    loadingMessage.remove();
    setChatRuntimeStatus(
      isNetworkError ? "backend_offline" : "error",
      isNetworkError ? sourceStatusMessage("backend_offline") : err.message,
      "error"
    );
    appendMessage("error", errText);
  } finally {
    setSending(false);
    msgInput.focus();
  }
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------
sendBtn.addEventListener("click", () => {
  sendMessage(msgInput.value);
});

memoryForm.addEventListener("submit", (e) => {
  e.preventDefault();
  createMemory();
});

refreshMemoryBtn.addEventListener("click", () => {
  loadMemories();
});

refreshPreviewBtn.addEventListener("click", () => {
  loadMemoryContextPreview();
});

refreshAuditBtn.addEventListener("click", () => {
  loadAuditLogs();
});

refreshProviderSettingsBtn.addEventListener("click", () => {
  loadProviderSettings();
});

providerSettingsForm.addEventListener("submit", (e) => {
  e.preventDefault();
  saveProviderSettings();
});

// TASK-056: key save / clear event listeners
saveProviderKeyBtn.addEventListener("click", () => {
  saveProviderKey();
});

clearProviderKeyBtn.addEventListener("click", () => {
  clearProviderKey();
});

// TASK-060: Test Connection button.
// Sends POST to local backend only. No external provider URL. No api_key in body.
// Explicit cost acknowledgement required via window.confirm() inside runTestConnection().
testProviderConnectionBtn.addEventListener("click", () => {
  runTestConnection();
});

// Dynamically enable/disable Save Key as user types in the key input field.
// Safety: this handler never logs providerApiKeyInput.value.
// TASK-076: local providers (ollama) never enable Save Key.
providerApiKeyInput.addEventListener("input", () => {
  const selectedProvider = providerSettingsProvider.value;
  const isRealProvider = selectedProvider !== "mock";
  const isLocalProvider = selectedProvider === "ollama";
  saveProviderKeyBtn.disabled =
    !isRealProvider || isLocalProvider || !providerApiKeyInput.value.trim();
});

// When provider dropdown changes, update key UI state.
// TASK-076: handle ollama (local provider — no key required).
providerSettingsProvider.addEventListener("change", () => {
  const selectedProvider = providerSettingsProvider.value;
  const isRealProvider = selectedProvider !== "mock";
  const isLocalProvider = selectedProvider === "ollama";

  // Clear key input and status message on any provider switch
  providerApiKeyInput.value = "";
  setProviderKeyMsg("");

  // Delegate full state update to updateKeyUIState using current cached settings
  // merged with the newly selected provider so enable conditions are correct.
  updateKeyUIState({
    ...currentProviderSettings,
    provider: selectedProvider,
    // Local provider always reports not_required; cloud providers keep their cached key_status
    key_status: isLocalProvider
      ? "not_required"
      : (currentProviderSettings.key_status || "not_configured"),
  });
});

msgInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(msgInput.value);
  }
});

// Auto-grow textarea
msgInput.addEventListener("input", () => {
  msgInput.style.height = "auto";
  msgInput.style.height = Math.min(msgInput.scrollHeight, 100) + "px";
});

// ---------------------------------------------------------------------------
// Startup
// ---------------------------------------------------------------------------
(async function startup() {
  appendMessage("status", "Connecting to backend...");

  try {
    const res = await fetch(`${BACKEND_URL}/health`);
    const data = await res.json();
    if (data.status === "ok") {
      // Remove the connecting status
      chatArea.lastChild.remove();
      appendMessage("pet", "Hey. I'm here. What's on your mind?");
      setMood("neutral");
      await loadMemories();
      await loadMemoryContextPreview();
      await loadAuditLogs();
      await loadProviderSettings();
    } else {
      throw new Error("Unexpected health response");
    }
  } catch {
    chatArea.lastChild.remove();
    appendMessage(
      "error",
      `Backend not reachable at ${BACKEND_URL}.\nStart the backend first:\n  cd backend\n  uvicorn app.main:app --reload`
    );
    setChatRuntimeStatus("backend_offline", sourceStatusMessage("backend_offline"), "error");
    setMemoryStatus(`Cannot reach backend at ${BACKEND_URL}.`, true);
    setProviderSettingsStatus(`Cannot reach backend at ${BACKEND_URL}.`, true);
  }

  msgInput.focus();
})();
