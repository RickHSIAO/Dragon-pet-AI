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
const interactionDiagnosticsContainer = document.getElementById("interaction-reaction-preview");
const interactionDiagnosticsSummary = document.getElementById("interaction-diagnostics-summary");
const interactionDiagnosticsToggle = document.getElementById("interaction-diagnostics-toggle");
const interactionDiagnosticsDetails = document.getElementById("interaction-diagnostics-details");
const showPetWindowBtn = document.getElementById("show-pet-window-btn");
const showPetWindowStatus = document.getElementById("show-pet-window-status");
// TASK-171A: Full App screenshot capture controls.
const captureScreenBtn = document.getElementById("capture-screen-btn");
const captureScreenStatus = document.getElementById("capture-screen-status");
// TASK-176: window picker capture controls.
const captureWindowBtn    = document.getElementById("capture-window-btn");
const captureWindowStatus = document.getElementById("capture-window-status");
// TASK-172A: analyze + clear controls.
const analyzeScreenBtn = document.getElementById("analyze-screen-btn");
const analyzeScreenStatus = document.getElementById("analyze-screen-status");
const analyzeScreenSummaryEl = document.getElementById("analyze-screen-summary");
const clearScreenBtn = document.getElementById("clear-screen-btn");
// TASK-172B: ask Christina about current OCR summary.
const askScreenBtn    = document.getElementById("ask-screen-btn");
const askScreenStatus = document.getElementById("ask-screen-status");
const clearChatBtn    = document.getElementById("clear-chat-btn");  // TASK-194
const copyChatBtn     = document.getElementById("copy-chat-btn");   // TASK-196
const exportChatBtn    = document.getElementById("export-chat-btn");    // TASK-205
const exportChatStatus = document.getElementById("export-chat-status"); // TASK-205
const clearChatStatus = document.getElementById("clear-chat-status");   // TASK-208
const chatSearchInput    = document.getElementById("chat-search-input");    // TASK-198
const chatSearchCountEl  = document.getElementById("chat-search-count");    // TASK-198
const chatSearchClearBtn = document.getElementById("chat-search-clear-btn"); // TASK-198
const chatNewMsgBtn      = document.getElementById("chat-new-message-btn");  // TASK-202
const chatEmptyState     = document.getElementById("chat-empty-state");      // TASK-208
const SEND_BUTTON_DEFAULT_TEXT = sendBtn ? (sendBtn.textContent || "Send") : "Send";
const EDIT_SEND_BUTTON_TEXT = "送出修改";
// TASK-241: Full App voice input constants
const FULL_APP_RECORDING_MAX_MS    = 30000;
const FULL_APP_STT_TIMEOUT_MS      = 30000;
const FULL_APP_VOICE_CHAT_MAX_CHARS = 2000;
// TASK-243: Voice Conversation Mode constants
const FULL_APP_CONVERSATION_SILENCE_MS       = 1000;
const FULL_APP_CONVERSATION_MIN_SPEECH_MS    = 300;
const FULL_APP_CONVERSATION_MAX_UTTERANCE_MS = 30000;
const FULL_APP_CONVERSATION_VAD_INTERVAL_MS  = 100;
const FULL_APP_CONVERSATION_RMS_THRESHOLD    = 0.035;
// TASK-244b: Voice Pipeline Diagnostics constants
const FULL_APP_VOICE_MIME_PRIORITY = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus"];
const FULL_APP_VOICE_AUDIO_CONSTRAINTS = { echoCancellation: true, noiseSuppression: true, autoGainControl: true };
// TASK-252: PCM capture constants for FunASR WAV input
const FULL_APP_STT_PCM_SAMPLE_RATE = 16000;
const FULL_APP_STT_PCM_BUFFER_SIZE = 4096;
// TASK-256: Startup Warmup constants — best-effort preload, no mic, no chat
var STARTUP_WARMUP_ENABLED        = true;  // var: exposed to vm sandbox for smoke tests
var STARTUP_STT_WARMUP_ENABLED    = true;  // var: exposed to vm sandbox
var STARTUP_OLLAMA_WARMUP_ENABLED = true;  // var: exposed to vm sandbox
const STARTUP_WARMUP_DELAY_MS     = 3000;  // delay after health check before warmup fires
// TASK-266: Owner Voice Gate Manual Mic dry-run policy.
// TASK-266/267: Owner Voice Gate dry-run policies.
// Status-only: never hard-block Manual Mic or Conversation Mode STT/chat flow.
// Candidate paths stay empty until a future explicit temp-file policy supplies one.
var OWNER_VOICE_MANUAL_MIC_DRY_RUN_ENABLED = true; // var: exposed to vm sandbox
var fullAppOwnerVoiceDryRunCandidatePath = "";     // var: test/future policy hook only
var OWNER_VOICE_CONVERSATION_MODE_DRY_RUN_ENABLED = true; // var: exposed to vm sandbox
var fullAppOwnerVoiceConversationDryRunCandidatePath = ""; // var: test/future policy hook only
// TASK-179: gentle hint shown after OCR summary exists.
const ocrAskHintEl = document.getElementById("ocr-ask-hint");
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
// TASK-189: plain-English provider state summary
const providerStatusSummaryEl = document.getElementById("provider-status-summary");
// TASK-083: pet avatar expression area
const petFace        = document.getElementById("pet-face");
const petDisplayHint = document.getElementById("pet-display-hint");
// TASK-056 / TASK-060: provider key save/clear/test controls
// Safety: key value is never logged, never stored in localStorage/sessionStorage,
// never sent to external providers, cleared from DOM immediately after every save attempt.
// Test Connection: only calls local backend POST /provider/settings/test.
// No api_key, prompt, memory_context, or chat history is sent to test endpoint.
// No automatic test after Save Key.
const providerApiKeyInput       = document.getElementById("provider-api-key-placeholder");
const saveProviderKeyBtn        = document.getElementById("save-provider-key-btn");
const clearProviderKeyBtn       = document.getElementById("clear-provider-key-btn");
const saveProviderSettingsBtn   = document.getElementById("save-provider-settings-btn");
const testProviderConnectionBtn = document.getElementById("test-provider-connection-btn");
const providerKeyMsg            = document.getElementById("provider-key-msg");
const providerTestMsg           = document.getElementById("provider-test-msg");
// TASK-241: Full App voice input DOM refs
const voiceInputBtn    = document.getElementById("voice-input-btn");
const voiceInputStatus = document.getElementById("voice-input-status");
// TASK-242: voice settings toggle DOM refs
const voiceInputEnabledToggle = document.getElementById("voice-input-enabled-toggle");
const voiceAutosendToggle     = document.getElementById("voice-autosend-toggle");
// TASK-243: Voice Conversation Mode DOM refs
const conversationModeBtn    = document.getElementById("conversation-mode-btn");
const conversationModeStatus = document.getElementById("conversation-mode-status");
// TASK-244: Voice Quality Diagnostics DOM refs
const voiceDiagnosticsDisplay = document.getElementById("voice-diagnostics-display");
const vadRmsThresholdInput    = document.getElementById("vad-rms-threshold-input");
const vadSilenceMsSelect      = document.getElementById("vad-silence-ms-select");
// TASK-244b: Voice Pipeline Diagnostics DOM refs
const voicePreviewPlayBtn    = document.getElementById("voice-preview-play-btn");
const voicePreviewAudio      = document.getElementById("voice-preview-audio");
const voicePreviewStatus     = document.getElementById("voice-preview-status");
// TASK-261/263: Owner Voice Gate settings + file enrollment DOM refs. No mic or runtime gate.
const ownerVoiceGateRefreshBtn = document.getElementById("owner-voice-gate-refresh-btn");
const ownerVoiceGateState = document.getElementById("owner-voice-gate-state");
const ownerVoiceGateProvider = document.getElementById("owner-voice-gate-provider");
const ownerVoiceGateModel = document.getElementById("owner-voice-gate-model");
const ownerVoiceGateEmbeddingDim = document.getElementById("owner-voice-gate-embedding-dim");
const ownerVoiceGateSampleCount = document.getElementById("owner-voice-gate-sample-count");
const ownerVoiceGateLastScore = document.getElementById("owner-voice-gate-last-score");
const ownerVoiceGateStorageOwner = document.getElementById("owner-voice-gate-storage-owner");
const ownerVoiceGateSafetyAccepted = document.getElementById("owner-voice-gate-safety-accepted");
const ownerVoiceGateEnabledToggle = document.getElementById("owner-voice-gate-enabled-toggle");
const ownerVoiceGateThreshold = document.getElementById("owner-voice-gate-threshold");
const ownerVoiceGateEnrollPaths = document.getElementById("owner-voice-gate-enroll-paths");
const ownerVoiceGateEnrollBtn = document.getElementById("owner-voice-gate-enroll-btn");
const ownerVoiceGateSaveThresholdBtn = document.getElementById("owner-voice-gate-save-threshold-btn");
const ownerVoiceGateDeleteBtn = document.getElementById("owner-voice-gate-delete-btn");
const ownerVoiceGateReenrollBtn = document.getElementById("owner-voice-gate-reenroll-btn");
const ownerVoiceGateStatusSummary = document.getElementById("owner-voice-gate-status-summary");
const ownerVoiceGateSettingsStatus = document.getElementById("owner-voice-gate-settings-status");

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let currentMood = "neutral";
let isSending   = false;
// TASK-241: Full App voice input state — isolated from isSending / chat state
var fullAppRecording    = false; // var: exposed to vm sandbox for smoke tests
var fullAppTranscribing = false; // var: exposed to vm sandbox for smoke tests
let _fullAppMicStream    = null;
let _fullAppRecorder     = null;
let _fullAppChunks       = [];
let _fullAppRecordingTimer = null;
// TASK-242: voice input settings state — session-only, not persisted
var fullAppVoiceInputEnabled    = true;  // var: exposed to vm sandbox for smoke tests
var fullAppVoiceAutoSendEnabled = false; // var: exposed to vm sandbox for smoke tests
// TASK-243: Voice Conversation Mode state — session-only, not persisted
var fullAppVoiceConversationEnabled         = false; // var: exposed to vm sandbox
var fullAppVoiceConversationState           = "off"; // off|waiting|speaking|transcribing|sending|error — var: exposed to vm sandbox
var fullAppVoiceConversationStream          = null;
var fullAppVoiceConversationAudioContext    = null;
var fullAppVoiceConversationAnalyser        = null;
var fullAppVoiceConversationVadTimer        = null;
var fullAppVoiceConversationRecorder        = null;
var fullAppVoiceConversationChunks          = [];
var fullAppVoiceConversationSpeechStartedAt = 0;
var fullAppVoiceConversationLastVoiceAt     = 0;
// TASK-252: PCM capture state — manual mic and conversation modes
let _fullAppPcmChunks    = [];
let _fullAppPcmCtx       = null;
let _fullAppPcmSource    = null;
let _fullAppPcmProcessor = null;
let _convPcmChunks       = [];
let _convPcmCtx          = null;
let _convPcmSource       = null;
let _convPcmProcessor    = null;
// TASK-244: Voice Quality Diagnostics state — session-only, not persisted
var fullAppVoiceDiagnostics = {
  mode: "none",
  recordingStartedAt: 0,
  recordingEndedAt: 0,
  durationMs: 0,
  blobSizeBytes: 0,
  mimeType: "",
  chunksCount: 0,
  transcriptLength: 0,
  transcriptPreview: "",
  emptyTranscript: false,
  autoSendEnabled: false,
  conversationState: "off",
  stopReason: "none",
  lastRms: 0,
  maxRms: 0,
  rmsThreshold: FULL_APP_CONVERSATION_RMS_THRESHOLD,
  silenceDurationMs: FULL_APP_CONVERSATION_SILENCE_MS,
  minSpeechMs: FULL_APP_CONVERSATION_MIN_SPEECH_MS,
  maxUtteranceMs: FULL_APP_CONVERSATION_MAX_UTTERANCE_MS,
  speechStarted: false,
  silenceMsAtStop: 0,
  sttStatus: "none",
  selectedMimeType: "",
  bytesPerSecond: 0,
  constraintsEchoCancellation: false,
  constraintsNoiseSuppression: false,
  constraintsAutoGainControl: false,
  lastAudioPreviewAvailable: false,
  lastAudioObjectUrlCreated: false,
  objectUrlActive: false,
  previewStatus: "",
  previewErrorName: "",
  previewErrorMessage: "",
  audioElementErrorCode: -1,
  audioCanPlayTypeResult: "",
  audioBlobTypeCanPlayResult: "",
  // TASK-245: STT language-lock diagnostics — populated from /stt/transcribe response metadata
  sttLanguage: "",
  languageLocked: false,
  sttTask: "",
  sttProvider: "",
  sttModel: "",
  detectedLanguage: "",
  // TASK-246: STT model quality diagnostics — populated from /stt/transcribe response metadata
  sttRequestedModel: "",
  sttResolvedModel: "",
  sttModelSource: "",
  sttModelLoadStatus: "",
  sttModelLoadError: "",
  // TASK-247: STT transcript correction diagnostics — populated from /stt/transcribe response metadata
  sttRawTranscriptPreview: "",
  sttCorrectedTranscriptPreview: "",
  sttCorrectionApplied: false,
  sttCorrectionMode: "",
  sttCorrectionReason: "",
  // TASK-248: matched alias / canonical term diagnostics
  sttMatchedAlias: "",
  sttCanonicalTerm: "",
  // TASK-249: STT provider selection diagnostics — populated from /stt/transcribe response
  sttProviderRequested: "",
  sttProviderResolved: "",
  sttProviderSource: "",
  sttProviderLoadStatus: "",
  sttProviderLoadError: "",
  sttProviderFallbackReason: "",
  // TASK-255: voice capture focus/minimize resilience diagnostics
  voiceCaptureFocusSafe: true,
  lastVisibilityState: "visible",
  lastWindowFocusState: "focused",
  audioContextState: "none",
  captureInterruptedReason: null,
  captureInterruptedByVisibility: false,
  // TASK-256: startup warmup diagnostics — populated by _triggerStartupWarmup()
  startupWarmupEnabled: true,
  sttWarmupStatus: "pending",
  sttWarmupLatencyMs: 0,
  sttWarmupError: null,
  ollamaWarmupStatus: "pending",
  ollamaWarmupLatencyMs: 0,
  ollamaWarmupError: null,
  lastStartupWarmupAt: 0,
  // TASK-266/267: Owner Voice Gate dry-run status. These fields are
  // status-only and must never hard-block runtime behavior.
  ownerVoiceDryRunEnabled: false,
  ownerVoiceDryRunSource: "none",
  ownerVoiceDryRunStatus: "disabled",
  ownerVoiceDryRunReason: "not_checked",
  ownerVoiceScore: null,
  ownerVoiceThreshold: 0.65,
  ownerVoiceAccepted: null,
  ownerVoiceCheckedAt: "",
  rawAudioPersisted: false,
  candidateEmbeddingPersisted: false,
  storedCentroidExposed: false,
  runtimeHardBlocked: false
};
// TASK-244: session-only VAD tuning vars — override constants for this session only, not persisted
var fullAppConversationRmsThreshold = FULL_APP_CONVERSATION_RMS_THRESHOLD;
var fullAppConversationSilenceMs    = FULL_APP_CONVERSATION_SILENCE_MS;
// TASK-244b: in-memory audio preview — no disk write
var fullAppLastAudioBlob           = null; // var: exposed to vm sandbox
var fullAppLastAudioObjectUrl      = null; // var: exposed to vm sandbox
var fullAppVoiceDiagnosticsHistory = [];   // var: max 2 recent recording snapshots
// TASK-060: track in-flight test connection to prevent double-click
let isTestingConnection = false;
// TASK-060: cache last-loaded provider settings for Test Connection enable conditions
let currentProviderSettings = {};
let providerSettingsLoaded = false;
let lastChatSource = "not_checked";
let lastChatStatusMessage = "No chat response yet.";
var currentOwnerVoiceGateSettings = {}; // var: exposed to vm sandbox for smoke tests

function setShowPetWindowStatus(message, isError = false) {
  if (!showPetWindowStatus) {
    return;
  }

  showPetWindowStatus.textContent = message;
  showPetWindowStatus.className = isError
    ? "header-action-status error"
    : "header-action-status";
}

async function showPetWindowFromFullApp() {
  const api =
    typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;

  if (!api || typeof api.showPetWindow !== "function") {
    setShowPetWindowStatus("Pet Mode bridge unavailable.", true);
    return null;
  }

  setShowPetWindowStatus("Showing Pet Window...");

  try {
    const result = await api.showPetWindow();
    if (result && result.ok) {
      setShowPetWindowStatus("Pet Window shown.");
      const replayedPending = flushPendingInteractionExpressionMirror();
      if (!replayedPending) {
        sendInteractionExpressionMirrorNow(currentInteractionExpressionSuggestion);
      }
    } else if (result && result.reason === "pet_mode_disabled") {
      setShowPetWindowStatus("Pet Mode disabled. Start with PET_MODE_ENABLED=true.", true);
    } else {
      setShowPetWindowStatus("Pet Window is not available.", true);
    }
    return result || null;
  } catch (_error) {
    setShowPetWindowStatus("Pet Window request failed.", true);
    return null;
  }
}



// ---------------------------------------------------------------------------
// TASK-171A: user-triggered primary-display screenshot capture (Full App only).
// Safety: only on explicit click; in-memory dataUrl only; never disk/chat/OCR/vision/background.
// ---------------------------------------------------------------------------
let lastScreenshotDataUrl = null;
let captureScreenInFlight = false;

const CAPTURE_FAILURE_MESSAGES = {
  "permission-denied":          "無法截圖，缺少螢幕擷取權限。",
  "no-source":                  "找不到可截圖的螢幕。",
  "capture-failed":             "截圖失敗，請稍後再試。",
  "primary-display-ambiguous":  "無法確認主要螢幕來源，請重試。",
  // TASK-174: click-to-select display picker error codes.
  "screen-pick-cancelled":      "已取消擷取螢幕。",
  "selected-display-ambiguous": "無法確認選取的螢幕來源，請重試。",
  "screen-picker-failed":       "無法開啟螢幕選擇器，請重試。",
  // TASK-175: region drag-to-select error codes.
  "region-pick-cancelled":      "已取消選取區域。",
  "region-too-small":           "選取範圍太小，請重新拖曳較大區域。",
  "region-crop-failed":         "區域擷取失敗，請稍後再試。",
  // TASK-176: window picker error codes.
  "window-pick-cancelled":      "已取消選取視窗。",
  "window-picker-failed":       "無法開啟視窗選擇器，請重試。",
  "no-window-source":           "找不到可截圖的視窗。",
  "window-capture-failed":      "視窗截圖失敗，請稍後再試。",
};

function setCaptureScreenStatus(message, isError) {
  if (!captureScreenStatus) return;
  captureScreenStatus.textContent = message;
  captureScreenStatus.className = isError === true
    ? "header-action-status error"
    : "header-action-status";
}

async function captureScreenFromFullApp() {
  if (captureScreenInFlight) return null;
  const api = (typeof window !== "undefined" && window.dragonPet) ? window.dragonPet : null;
  if (!api || typeof api.captureScreen !== "function") {
    setCaptureScreenStatus("螢幕擷取功能未啟用。", true);
    return null;
  }
  captureScreenInFlight = true;
  if (captureScreenBtn) captureScreenBtn.disabled = true;
  setCaptureScreenStatus("擷取中…", false);
  let result = null;
  try {
    result = await api.captureScreen();
  } catch (_error) {
    result = { ok: false, error: "capture-failed" };
  } finally {
    captureScreenInFlight = false;
    if (captureScreenBtn) captureScreenBtn.disabled = false;
  }
  if (result && result.ok && typeof result.dataUrl === "string"
      && result.dataUrl.startsWith("data:image/")) {
    lastScreenshotDataUrl = result.dataUrl;
    lastScreenSummary = null;         // TASK-172A: new capture clears prior summary
    setAnalyzeScreenSummary(null);    // TASK-172A: hide old summary panel
    updateAnalyzeButtonState();       // TASK-172A: enable analyze button
    setCaptureScreenStatus("螢幕截圖完成。尚未儲存，可供後續分析使用。", false);
    return { ok: true };
  }
  const reason = (result && typeof result.error === "string") ? result.error : "capture-failed";
  const safeMessage = CAPTURE_FAILURE_MESSAGES[reason] || CAPTURE_FAILURE_MESSAGES["capture-failed"];
  setCaptureScreenStatus(safeMessage, true);
  return { ok: false };
}

// ---------------------------------------------------------------------------
// TASK-176: explicit window picker capture (Full App only).
// Safety: only on explicit click; in-memory dataUrl only; never disk/chat/OCR/background.
// Feeds into the same lastScreenshotDataUrl / analyze / ask / clear pipeline.
// ---------------------------------------------------------------------------
let captureWindowInFlight = false;

function setCaptureWindowStatus(message, isError) {
  if (!captureWindowStatus) return;
  captureWindowStatus.textContent = message;
  captureWindowStatus.className = isError === true
    ? "header-action-status error"
    : "header-action-status";
}

async function captureWindowFromFullApp() {
  if (captureWindowInFlight) return null;
  const api = (typeof window !== "undefined" && window.dragonPet) ? window.dragonPet : null;
  if (!api || typeof api.captureWindow !== "function") {
    setCaptureWindowStatus("視窗擷取功能未啟用。", true);
    return null;
  }
  captureWindowInFlight = true;
  if (captureWindowBtn) captureWindowBtn.disabled = true;
  setCaptureWindowStatus("選取視窗中…", false);
  let result = null;
  try {
    result = await api.captureWindow();
  } catch (_error) {
    result = { ok: false, error: "window-capture-failed" };
  } finally {
    captureWindowInFlight = false;
    if (captureWindowBtn) captureWindowBtn.disabled = false;
  }
  if (result && result.ok && typeof result.dataUrl === "string"
      && result.dataUrl.startsWith("data:image/")) {
    lastScreenshotDataUrl = result.dataUrl;
    lastScreenSummary = null;
    setAnalyzeScreenSummary(null);
    updateAnalyzeButtonState();
    setCaptureWindowStatus("視窗截圖完成。尚未儲存，可供後續分析使用。", false);
    return { ok: true };
  }
  const reason = (result && typeof result.error === "string") ? result.error : "window-capture-failed";
  const safeMessage = CAPTURE_FAILURE_MESSAGES[reason] || CAPTURE_FAILURE_MESSAGES["capture-failed"];
  setCaptureWindowStatus(safeMessage, true);
  return { ok: false };
}

// ---------------------------------------------------------------------------
// TASK-172A: user-confirmed screenshot OCR summary (Full App only).
// Privacy: no cloud vision, no /chat, no background monitoring, no disk save.
// OCR is unavailable in this slice — clean fallback shown until wired up.
// ---------------------------------------------------------------------------
let lastScreenSummary = null;
let analyzeInFlight = false;
let askScreenInFlight = false;

const ANALYZE_CONFIRM_MSG =
  "截圖內容可能含有密碼、API 金鑰或私密訊息。\n請確認截圖內容後再繼續分析。";

const ANALYZE_FAILURE_MESSAGES = {
  "ocr-unavailable":      "分析功能目前不可用。",
  "ocr-init-failed":      "分析功能初始化失敗，請稍後再試。",
  "ocr-timeout":          "分析逾時，請稍後再試。",
  "invalid-dataurl":      "截圖格式錯誤，請重新擷取。",
  "ocr-failed":           "分析失敗，請稍後再試。",
  "screenshot-too-large": "截圖過大，無法分析。",
  "no-screenshot":        "請先擷取螢幕截圖。",
  "screenshot-cleared":   "截圖已清除，請重新擷取。",
  "no-text":              "未偵測到可用文字。",
  "backend-offline":      "後端無法連線，請稍後再試。",
};

function setAnalyzeScreenStatus(message, isError) {
  if (!analyzeScreenStatus) return;
  analyzeScreenStatus.textContent = message;
  analyzeScreenStatus.className = isError === true
    ? "header-action-status error"
    : "header-action-status";
}

function setAnalyzeScreenSummary(text) {
  if (!analyzeScreenSummaryEl) return;
  if (!text) {
    analyzeScreenSummaryEl.hidden = true;
    analyzeScreenSummaryEl.textContent = "";
    return;
  }
  analyzeScreenSummaryEl.textContent = text;
  analyzeScreenSummaryEl.hidden = false;
}

function updateAnalyzeButtonState() {
  const hasScreenshot = typeof lastScreenshotDataUrl === "string"
    && lastScreenshotDataUrl.startsWith("data:image/");
  if (analyzeScreenBtn) analyzeScreenBtn.disabled = !hasScreenshot || analyzeInFlight;
  if (clearScreenBtn) clearScreenBtn.hidden = !hasScreenshot;
}

function clearScreenshot() {
  lastScreenshotDataUrl = null;
  lastScreenSummary = null;
  updateAnalyzeButtonState();
  updateAskButtonState();
  setAnalyzeScreenStatus("", false);
  setAnalyzeScreenSummary(null);
  // Clear both capture status spans so neither shows stale "截圖完成" after clear.
  setCaptureWindowStatus("", false);
  setCaptureScreenStatus("截圖已清除。", false);
}

// TASK-172B: ask Christina about current OCR summary.
// Privacy: sends only bounded summary text via existing sendMessage(); no dataUrl, no image bytes.
const ASK_SCREEN_CONFIRM_MSG =
  "螢幕摘要將傳送給 Christina 作為對話內容。\n" +
  "摘要可能含有：私訊或個人訊息、帳戶或財務資料、API 金鑰或密碼、工作文件。\n" +
  "確定要繼續嗎？";
const CHAT_SUMMARY_PREFIX = "請根據以下螢幕摘要幫我判斷：\n\n";

function setAskScreenStatus(message, isError) {
  if (!askScreenStatus) return;
  askScreenStatus.textContent = message;
  askScreenStatus.className = isError === true
    ? "header-action-status error"
    : "header-action-status";
}

function updateAskButtonState() {
  const hasSummary =
    typeof lastScreenSummary === "string" && lastScreenSummary.trim().length > 0;
  if (askScreenBtn) {
    askScreenBtn.hidden    = !hasSummary;
    askScreenBtn.disabled  = !hasSummary || askScreenInFlight || analyzeInFlight || isSending;
  }
  if (askScreenStatus && !hasSummary) {
    askScreenStatus.textContent = "";
    askScreenStatus.className   = "header-action-status";
  }
  // TASK-179: show/hide gentle hint alongside the ask button.
  if (ocrAskHintEl) ocrAskHintEl.hidden = !hasSummary;
}

async function askScreenFromFullApp() {
  if (askScreenInFlight || isSending) return;
  const summary = lastScreenSummary;
  if (!summary || typeof summary !== "string" || !summary.trim()) {
    setAskScreenStatus("請先分析螢幕截圖。", true);
    return;
  }
  const confirmFn =
    typeof window !== "undefined" && typeof window.confirm === "function"
      ? window.confirm.bind(window)
      : () => false;
  if (!confirmFn(ASK_SCREEN_CONFIRM_MSG)) return;
  const message = CHAT_SUMMARY_PREFIX + summary;
  askScreenInFlight = true;
  updateAskButtonState();
  try {
    await sendMessage(message);
  } finally {
    askScreenInFlight = false;
    updateAskButtonState();
  }
}

// TASK-172A-OCR-BACKEND: backend local OCR via POST /ocr/extract (Option B).
// Renderer uses existing fetch() — no new IPC, no require(), no nodeIntegration change.
// Privacy: dataUrl sent to localhost backend only; no external upload; no /chat call.
const OCR_DATAURL_MAX_LEN = 20 * 1024 * 1024; // 20 MB string-length guard
const OCR_TIMEOUT_MS = 30000;

async function runOcrAnalysis(dataUrl) {
  if (typeof dataUrl !== "string" || !dataUrl.startsWith("data:image/")) {
    return { ok: false, error: "invalid-dataurl" };
  }
  if (dataUrl.length > OCR_DATAURL_MAX_LEN) {
    return { ok: false, error: "screenshot-too-large" };
  }
  let fetchResult = null;
  try {
    // AbortController for timeout — available in Electron renderer and modern browsers.
    // Falls back to no timeout in test sandboxes where AbortController is absent.
    let signal;
    let timeoutId = null;
    if (typeof AbortController !== "undefined") {
      const controller = new AbortController();
      signal = controller.signal;
      timeoutId = setTimeout(() => controller.abort(), OCR_TIMEOUT_MS);
    }
    const res = await fetch(`${BACKEND_URL}/ocr/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: dataUrl }),
      signal,
    });
    if (timeoutId !== null) clearTimeout(timeoutId);
    if (!res.ok) {
      return { ok: false, error: "ocr-failed" };
    }
    fetchResult = await res.json();
  } catch (_e) {
    const isAbort = _e && _e.name === "AbortError";
    return { ok: false, error: isAbort ? "ocr-timeout" : "backend-offline" };
  }
  if (!fetchResult || typeof fetchResult.ok !== "boolean") {
    return { ok: false, error: "ocr-failed" };
  }
  return fetchResult;
}

function cleanOcrText(raw) {
  if (typeof raw !== "string") return "";
  const trimmed = raw.trim();
  // Collapse 3+ newlines to 2, normalize runs of spaces on each line
  const collapsed = trimmed
    .replace(/\n{3,}/g, "\n\n")
    .replace(/[ \t]{3,}/g, "  ");
  const MAX_OCR_CHARS = 800;
  const bounded = collapsed.length > MAX_OCR_CHARS ? collapsed.slice(0, MAX_OCR_CHARS) : collapsed;
  return bounded;
}

async function analyzeScreenFromFullApp() {
  if (analyzeInFlight) return;
  if (!lastScreenshotDataUrl || !lastScreenshotDataUrl.startsWith("data:image/")) {
    setAnalyzeScreenStatus(ANALYZE_FAILURE_MESSAGES["no-screenshot"], true);
    return;
  }
  // Explicit sensitive-content confirmation required before every analysis.
  const confirmFn =
    typeof window !== "undefined" && typeof window.confirm === "function"
      ? window.confirm.bind(window)
      : () => false;
  const userConfirmed = confirmFn(ANALYZE_CONFIRM_MSG);
  if (!userConfirmed) {
    return; // silently do nothing; button stays enabled
  }
  analyzeInFlight = true;
  if (analyzeScreenBtn) analyzeScreenBtn.disabled = true;
  setAnalyzeScreenStatus("正在分析…", false);
  setAnalyzeScreenSummary(null);
  let result = null;
  try {
    result = await runOcrAnalysis(lastScreenshotDataUrl);
  } catch (_err) {
    result = { ok: false, error: "ocr-failed" };
  } finally {
    analyzeInFlight = false;
    updateAnalyzeButtonState();
  }
  if (result && result.ok) {
    const cleaned = cleanOcrText(result.text);
    if (!cleaned) {
      setAnalyzeScreenStatus(ANALYZE_FAILURE_MESSAGES["no-text"], false);
      lastScreenSummary = null;
      updateAskButtonState();
    } else {
      lastScreenSummary = cleaned;
      updateAskButtonState();
      setAnalyzeScreenStatus("", false);
      setAnalyzeScreenSummary("螢幕摘要：\n" + cleaned);
    }
    return;
  }
  const failReason = (result && typeof result.error === "string") ? result.error : "ocr-failed";
  const failMsg = ANALYZE_FAILURE_MESSAGES[failReason] || ANALYZE_FAILURE_MESSAGES["ocr-failed"];
  const isErr = failReason !== "no-text";
  setAnalyzeScreenStatus(failMsg, isErr);
  lastScreenSummary = null;
  updateAskButtonState();
}

function updatePetSpeechFromChatResponse(data) {
  const api =
    typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;

  if (!api || typeof api.updatePetSpeech !== "function" || !data) {
    return null;
  }

  const payload = {
    reply: typeof data.reply === "string" ? data.reply : "",
    mood: typeof data.mood === "string" ? data.mood : "neutral",
    source: typeof data.source === "string" ? data.source : "unknown",
  };

  const result = api.updatePetSpeech(payload);
  if (result && typeof result.catch === "function") {
    result.catch(() => {});
  }

  return result || null;
}

// TASK-157: in-character thinking text shown in Pet Window while waiting for /chat.
const PET_THINKING_REPLY_TEXT =
  "吾、吾才不是在認真思考呢……等一下！";

function updatePetThinkingState() {
  const api =
    typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!api || typeof api.updatePetSpeech !== "function") return null;
  const result = api.updatePetSpeech({
    reply: PET_THINKING_REPLY_TEXT,
    mood: "focused",
    source: "pet_thinking",
  });
  if (result && typeof result.catch === "function") result.catch(() => {});
  return result || null;
}

// ---------------------------------------------------------------------------
// Idle State (TASK-108) — Companion Behavior Loop
// Safety: idle logic is UI-only. No /chat calls, no network, no file access.
// ---------------------------------------------------------------------------
const IDLE_THRESHOLD_SHORT_MS  = 3 * 60 * 1000;    // 3 min  → neutral expression + hint
const IDLE_THRESHOLD_LONG_MS   = 10 * 60 * 1000;   // 10 min → sleepy expression + hint
const IDLE_THRESHOLD_RETURN_MS = 15 * 60 * 1000;   // 15 min — epoch for return greeting (TASK-110)
const IDLE_CHECK_INTERVAL_MS   = 60 * 1000;         // polling cadence: 1 min

let lastActivityTime = Date.now();
let currentIdleState  = "active"; // "active" | "short_idle" | "long_idle"
// TASK-110: return-from-away greeting flags.
// awayGreetingEligible: set by idleTick once elapsed ≥ IDLE_THRESHOLD_RETURN_MS;
//   cleared after greeting fires.
// awayGreetingFired: spam guard — prevents duplicate greeting within the same away
//   session; reset when user re-enters long_idle so the next away cycle works.
let awayGreetingEligible = false;
let awayGreetingFired    = false;
// TASK-111: companion hint lock — idleTick will not override important greetings
// for HINT_LOCK_MS ms after they are shown. High-priority states (chat response,
// pending, error, offline) bypass the lock entirely by calling setPetExpression
// directly; only idleTick checks the lock.
const HINT_LOCK_MS = 8 * 1000; // 8 seconds
let hintLockedUntil = 0;       // epoch ms; 0 = always unlocked

// TASK-200: unread indicator — counts new pet replies while Full App is not focused.
let unreadChatCount = 0;
const UNREAD_BASE_TITLE = "Dragon Pet AI";

// TASK-207: tracks last-inserted date key so same-day duplicates are skipped.
let lastDateKey = null;

// TASK-208: two-step clear confirmation to prevent accidental chat-history deletion.
const CLEAR_CHAT_CONFIRM_MS = 6000;
const CLEAR_CHAT_DEFAULT_TEXT = clearChatBtn
  ? (clearChatBtn.textContent || "清除對話記錄")
  : "清除對話記錄";
let clearChatConfirmPending = false;
let clearChatConfirmTimer = null;
let clearChatStatusTimer = null;
// TASK-209: short-lived undo state for the most recent successful clear.
const UNDO_CLEAR_MS = 10000;
let lastClearedChatEntries = [];
let undoClearTimer = null;
// TASK-210: short-lived undo state for the most recent single-message delete.
const UNDO_DELETE_MESSAGE_MS = 10000;
let lastDeletedChatMessage = null;
let undoDeleteMessageTimer = null;
// TASK-211: edit state for one formal user message at a time.
let editingMessageState = null;
let chatContextMenu = null;
const CHAT_CONTEXT_MENU_MARGIN = 8;
const CHAT_CONTEXT_MENU_FALLBACK_WIDTH = 128;
const CHAT_CONTEXT_MENU_ITEM_HEIGHT = 34;

// TASK-214: Interaction event log — pure local memory, max 20 entries.
// Records sanitized metadata only; no raw text, no API keys, no media.
const INTERACTION_EVENT_ALLOWLIST = new Set([
  "chat_message_sent",
  "pet_window_opened",
  "full_app_focused",
  "chat_history_cleared",
  "message_deleted",
  "message_edited",
]);
const INTERACTION_EVENT_MAX = 20;
var recentInteractionEvents = []; // var: exposed to vm sandbox for smoke tests

// TASK-215: Reaction hint layer — derives a semantic hint from each sanitized interaction event.
// Pure local renderer memory; no UI side-effects, no Pet Window, no /chat, no TTS, no history write.
const INTERACTION_REACTION_HINT_ALLOWLIST = new Set([
  "user_active",
  "message_management",
  "correction",
  "reset",
  "attention_returned",
  "pet_attention",
  "none",
]);
const INTERACTION_REACTION_HINT_MAX = 20;
var recentInteractionReactionHints = []; // var: exposed to vm sandbox for smoke tests
var currentInteractionReactionHint = "none"; // var: exposed to vm sandbox for smoke tests

// TASK-220: Reaction bubble layer — fixed local text only, no raw message text.
const INTERACTION_REACTION_BUBBLE_ALLOWLIST = new Set([
  "user_active",
  "message_management",
  "correction",
  "reset",
  "attention_returned",
  "none",
]);
const INTERACTION_REACTION_BUBBLE_TEXT = Object.freeze({
  user_active: "哼，總算肯理吾了。",
  message_management: "整理好了？手腳還算俐落。",
  correction: "又改？下次可要想清楚。",
  reset: "清空了。重新開始也無妨。",
  attention_returned: "回來了？吾才沒有等汝。",
  none: "",
});
const INTERACTION_REACTION_BUBBLE_MAX = 20;
const INTERACTION_REACTION_BUBBLE_TTL_MS = 3000;
var recentInteractionReactionBubbles = []; // var: exposed to vm sandbox for smoke tests
var currentInteractionReactionBubble = { id: "none", text: "", source: "interaction_reaction_bubble" };

// TASK-221: Companion behavior policy layer.
// Pure local decision summary only; it does not drive mirror side effects.
const COMPANION_BEHAVIOR_DECISION_REASONS = new Set([
  "none",
  "user_active",
  "message_management",
  "correction",
  "reset",
  "attention_returned",
  "pet_attention",
]);
const COMPANION_BEHAVIOR_ACTION_ALLOWLIST = new Set([
  "none",
  "mirror_expression",
  "show_reaction_bubble",
  "mirror_expression_and_bubble",
]);
const COMPANION_BEHAVIOR_DECISION_MAX = 20;
var recentCompanionBehaviorDecisions = []; // var: exposed to vm sandbox for smoke tests
var currentCompanionBehaviorDecision = {
  reason: "none",
  reactionHint: "none",
  expression: "neutral",
  bubbleId: "none",
  shouldMirrorExpression: false,
  shouldShowBubble: false,
  action: "none",
  ts: 0,
};

// TASK-223: Character state layer — pure local state summary only.
const CHARACTER_ATTENTION_STATE_ALLOWLIST = new Set([
  "idle",
  "active",
  "returned",
  "managing",
  "correcting",
  "reset",
]);
const CHARACTER_ENERGY_STATE_ALLOWLIST = new Set([
  "calm",
  "attentive",
  "lively",
  "resting",
]);
const CHARACTER_MOOD_STATE_ALLOWLIST = new Set([
  "neutral",
  "focused",
  "happy",
  "proud",
  "annoyed",
  "sleepy",
]);
const CHARACTER_INTERACTION_LEVEL_ALLOWLIST = new Set([
  "none",
  "low",
  "medium",
  "high",
]);
const CHARACTER_STATE_MAX = 20;
var recentCharacterStates = []; // var: exposed to vm sandbox for smoke tests
var currentCharacterState = {
  attention: "idle",
  energy: "calm",
  mood: "neutral",
  recentInteractionLevel: "none",
  source: "character_state_layer",
  reason: "none",
  ts: 0,
};

// TASK-238: Output Queue engine delegated to window.dragonOutputQueue module (output-queue.js).
const OUTPUT_QUEUE_ENABLED = window.dragonOutputQueue.OUTPUT_QUEUE_ENABLED;
var outputQueueItems = window.dragonOutputQueue.outputQueueItems;
var recentOutputQueueItems = window.dragonOutputQueue.recentOutputQueueItems;
function sanitizeOutputQueueReason(v) { return window.dragonOutputQueue.sanitizeOutputQueueReason(v); }
function sanitizeOutputQueuePayload(p) { return window.dragonOutputQueue.sanitizeOutputQueuePayload(p); }
function cloneOutputQueueItemSummary(item) { return window.dragonOutputQueue.cloneOutputQueueItemSummary(item); }
function cloneOutputQueueNextItemSummary(item) { return window.dragonOutputQueue.cloneOutputQueueNextItemSummary(item); }
function updateOutputQueueSnapshot() { return window.dragonOutputQueue.updateOutputQueueSnapshot(); }
function sanitizeOutputQueueItem(input) { return window.dragonOutputQueue.sanitizeOutputQueueItem(input); }
function enqueueOutputQueueItem(input) { return window.dragonOutputQueue.enqueueOutputQueueItem(input); }
function getOutputQueueSnapshot() { return window.dragonOutputQueue.getOutputQueueSnapshot(); }
function clearOutputQueue(reason) { return window.dragonOutputQueue.clearOutputQueue(reason); }
function outputPriorityIndex(value) { return window.dragonOutputQueue.outputPriorityIndex(value); }
function compareOutputPriority(a, b) { return window.dragonOutputQueue.compareOutputPriority(a, b); }
function shouldOutputPreempt(activeItem, incomingItem) { return window.dragonOutputQueue.shouldOutputPreempt(activeItem, incomingItem); }
function getOutputQueuePriorityWinner(items) { return window.dragonOutputQueue.getOutputQueuePriorityWinner(items); }
function cloneOutputQueueActiveItemSummary(item) { return window.dragonOutputQueue.cloneOutputQueueActiveItemSummary(item); }
function getActiveOutputItemSnapshot() { return window.dragonOutputQueue.getActiveOutputItemSnapshot(); }
function setActiveOutputItemForDiagnosticsOnly(item) { return window.dragonOutputQueue.setActiveOutputItemForDiagnosticsOnly(item); }
function clearActiveOutputItem() { return window.dragonOutputQueue.clearActiveOutputItem(); }
function formatOutputQueueSnapshotPreview(snapshot) { return window.dragonOutputQueue.formatOutputQueueSnapshotPreview(snapshot); }

function defaultCompanionExpressionForReason(reason) {
  switch (reason) {
    case "user_active":        return "focused";
    case "correction":         return "annoyed";
    case "attention_returned": return "happy";
    case "pet_attention":      return "proud";
    case "message_management":
    case "reset":
    case "none":
    default:                   return "neutral";
  }
}

function defaultCompanionBubbleIdForReason(reason) {
  switch (reason) {
    case "user_active":
    case "message_management":
    case "correction":
    case "reset":
    case "attention_returned":
      return reason;
    case "pet_attention":
    case "none":
    default:
      return "none";
  }
}

function deriveCompanionBehaviorAction(shouldMirrorExpression, shouldShowBubble) {
  if (shouldMirrorExpression && shouldShowBubble) return "mirror_expression_and_bubble";
  if (shouldMirrorExpression) return "mirror_expression";
  if (shouldShowBubble) return "show_reaction_bubble";
  return "none";
}

function defaultCharacterStateForReason(reason) {
  switch (reason) {
    case "user_active":
      return { attention: "active", energy: "attentive", mood: "focused" };
    case "message_management":
      return { attention: "managing", energy: "calm", mood: "neutral" };
    case "correction":
      return { attention: "correcting", energy: "attentive", mood: "annoyed" };
    case "reset":
      return { attention: "reset", energy: "calm", mood: "neutral" };
    case "attention_returned":
      return { attention: "returned", energy: "lively", mood: "happy" };
    case "pet_attention":
      return { attention: "active", energy: "lively", mood: "proud" };
    case "none":
    default:
      return { attention: "idle", energy: "calm", mood: "neutral" };
  }
}

function deriveRecentInteractionLevel(events) {
  const count = Array.isArray(events) ? events.length : 0;
  if (count <= 0) return "none";
  if (count <= 2) return "low";
  if (count <= 5) return "medium";
  return "high";
}

function deriveCharacterState(context = {}) {
  const source = context && typeof context === "object" ? context : {};
  const decision = source.behaviorDecision && typeof source.behaviorDecision === "object"
    ? source.behaviorDecision
    : {};
  const rawReason = typeof decision.reactionHint === "string"
    ? decision.reactionHint
    : (typeof decision.reason === "string"
      ? decision.reason
      : (typeof source.reactionHint === "string" ? source.reactionHint : ""));
  const safeReason = COMPANION_BEHAVIOR_DECISION_REASONS.has(rawReason) ? rawReason : "none";
  const defaults = defaultCharacterStateForReason(safeReason);

  const rawMood = typeof decision.expression === "string"
    ? decision.expression
    : (typeof source.expression === "string" ? source.expression : "");
  const mood = rawMood
    ? (CHARACTER_MOOD_STATE_ALLOWLIST.has(rawMood) ? rawMood : "neutral")
    : defaults.mood;

  const rawAttention = typeof source.attention === "string" ? source.attention : "";
  const attention = rawAttention
    ? (CHARACTER_ATTENTION_STATE_ALLOWLIST.has(rawAttention) ? rawAttention : "idle")
    : defaults.attention;

  const rawEnergy = typeof source.energy === "string" ? source.energy : "";
  const energy = rawEnergy
    ? (CHARACTER_ENERGY_STATE_ALLOWLIST.has(rawEnergy) ? rawEnergy : "calm")
    : defaults.energy;

  const events = Array.isArray(source.recentInteractionEvents)
    ? source.recentInteractionEvents
    : recentInteractionEvents;

  return {
    attention,
    energy,
    mood: safeReason === "none" ? "neutral" : mood,
    recentInteractionLevel: deriveRecentInteractionLevel(events),
    source: "character_state_layer",
    reason: safeReason,
    ts: Date.now(),
  };
}

function recordCharacterState(state = {}) {
  const source = state && typeof state === "object" ? state : {};
  const entry = {
    attention: CHARACTER_ATTENTION_STATE_ALLOWLIST.has(source.attention) ? source.attention : "idle",
    energy: CHARACTER_ENERGY_STATE_ALLOWLIST.has(source.energy) ? source.energy : "calm",
    mood: CHARACTER_MOOD_STATE_ALLOWLIST.has(source.mood) ? source.mood : "neutral",
    recentInteractionLevel: CHARACTER_INTERACTION_LEVEL_ALLOWLIST.has(source.recentInteractionLevel)
      ? source.recentInteractionLevel
      : "none",
    source: "character_state_layer",
    reason: COMPANION_BEHAVIOR_DECISION_REASONS.has(source.reason) ? source.reason : "none",
    ts: Number.isFinite(source.ts) && source.ts > 0 ? source.ts : Date.now(),
  };
  recentCharacterStates.push(entry);
  if (recentCharacterStates.length > CHARACTER_STATE_MAX) {
    recentCharacterStates.shift();
  }
  currentCharacterState = entry;
  return currentCharacterState;
}

function deriveCompanionBehaviorDecision(context = {}) {
  const source = context && typeof context === "object" ? context : {};
  const rawHint = typeof source.reactionHint === "string" ? source.reactionHint : "";
  const safeReason = COMPANION_BEHAVIOR_DECISION_REASONS.has(rawHint) ? rawHint : "none";
  const rawExpression = typeof source.expression === "string" ? source.expression : "";
  let safeExpression = rawExpression
    ? (INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST.has(rawExpression) ? rawExpression : "neutral")
    : defaultCompanionExpressionForReason(safeReason);
  if (safeReason === "none") safeExpression = "neutral";

  const rawBubbleId = typeof source.bubbleId === "string" ? source.bubbleId : "";
  let safeBubbleId = rawBubbleId
    ? (INTERACTION_REACTION_BUBBLE_ALLOWLIST.has(rawBubbleId) ? rawBubbleId : "none")
    : defaultCompanionBubbleIdForReason(safeReason);
  if (safeReason === "none" || safeReason === "pet_attention") safeBubbleId = "none";

  const shouldMirrorExpression = safeReason !== "none";
  const shouldShowBubble = safeBubbleId !== "none";
  const action = deriveCompanionBehaviorAction(shouldMirrorExpression, shouldShowBubble);
  return {
    reason: safeReason,
    reactionHint: safeReason,
    expression: safeExpression,
    bubbleId: safeBubbleId,
    shouldMirrorExpression,
    shouldShowBubble,
    action,
    ts: Date.now(),
  };
}

function recordCompanionBehaviorDecision(decision = {}) {
  const source = decision && typeof decision === "object" ? decision : {};
  const safeReason = COMPANION_BEHAVIOR_DECISION_REASONS.has(source.reason) ? source.reason : "none";
  const safeReactionHint = INTERACTION_REACTION_HINT_ALLOWLIST.has(source.reactionHint)
    ? source.reactionHint
    : safeReason;
  const safeExpression = INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST.has(source.expression)
    ? source.expression
    : "neutral";
  const safeBubbleId = INTERACTION_REACTION_BUBBLE_ALLOWLIST.has(source.bubbleId)
    ? source.bubbleId
    : "none";
  const shouldMirrorExpression = Boolean(source.shouldMirrorExpression);
  const shouldShowBubble = Boolean(source.shouldShowBubble);
  const derivedAction = deriveCompanionBehaviorAction(shouldMirrorExpression, shouldShowBubble);
  const safeAction = COMPANION_BEHAVIOR_ACTION_ALLOWLIST.has(source.action)
    ? source.action
    : derivedAction;
  const safeTs = Number.isFinite(source.ts) && source.ts > 0 ? source.ts : Date.now();
  const entry = {
    reason: safeReason,
    reactionHint: safeReactionHint,
    expression: safeExpression,
    bubbleId: safeBubbleId,
    shouldMirrorExpression,
    shouldShowBubble,
    action: safeAction,
    ts: safeTs,
  };
  recentCompanionBehaviorDecisions.push(entry);
  if (recentCompanionBehaviorDecisions.length > COMPANION_BEHAVIOR_DECISION_MAX) {
    recentCompanionBehaviorDecisions.shift();
  }
  currentCompanionBehaviorDecision = entry;
  recordCharacterState(deriveCharacterState({
    behaviorDecision: currentCompanionBehaviorDecision,
    reactionHint: currentInteractionReactionHint,
    expression: currentInteractionExpressionSuggestion,
    recentInteractionEvents,
    recentCompanionBehaviorDecisions,
  }));
  return currentCompanionBehaviorDecision;
}

function recordCurrentCompanionBehaviorDecision() {
  return recordCompanionBehaviorDecision(deriveCompanionBehaviorDecision({
    reactionHint: currentInteractionReactionHint,
    expression: currentInteractionExpressionSuggestion,
    bubbleId: currentInteractionReactionBubble && currentInteractionReactionBubble.id
      ? currentInteractionReactionBubble.id
      : "none",
  }));
}

function deriveInteractionReactionHint(event) {
  switch (event.type) {
    case "chat_message_sent":    return "user_active";
    case "message_deleted":      return "message_management";
    case "message_edited":       return "correction";
    case "chat_history_cleared": return "reset";
    case "full_app_focused":     return "attention_returned";
    case "pet_window_opened":    return "pet_attention";
    default:                     return "none";
  }
}

function recordInteractionReactionHint(hint, event = {}) {
  const safeHint = INTERACTION_REACTION_HINT_ALLOWLIST.has(hint) ? hint : "none";
  const HINT_SAFE_KEYS = new Set(["source", "role", "messageLength"]);
  const safe = {};
  for (const [k, v] of Object.entries(event)) {
    if (HINT_SAFE_KEYS.has(k)) safe[k] = v;
  }
  const entry = { hint: safeHint, ts: Date.now(), eventType: event.type || "unknown", ...safe };
  recentInteractionReactionHints.push(entry);
  if (recentInteractionReactionHints.length > INTERACTION_REACTION_HINT_MAX) {
    recentInteractionReactionHints.shift();
  }
  currentInteractionReactionHint = safeHint;
  const expression = deriveInteractionExpressionSuggestion(safeHint); // TASK-217
  recordInteractionExpressionSuggestion(expression, safeHint);        // TASK-217
  const bubble = deriveInteractionReactionBubble(safeHint);           // TASK-220
  recordInteractionReactionBubble(bubble, safeHint);                  // TASK-220
  recordCurrentCompanionBehaviorDecision();                           // TASK-221
  renderInteractionReactionPreview(); // TASK-216/217
}

function deriveInteractionReactionBubble(hint) {
  const safeId = INTERACTION_REACTION_BUBBLE_ALLOWLIST.has(hint) ? hint : "none";
  return {
    id: safeId,
    text: INTERACTION_REACTION_BUBBLE_TEXT[safeId] || "",
    source: "interaction_reaction_bubble",
  };
}

function recordInteractionReactionBubble(bubble, hint) {
  const rawId = bubble && typeof bubble.id === "string" ? bubble.id : "";
  const safeId = INTERACTION_REACTION_BUBBLE_ALLOWLIST.has(rawId) ? rawId : "none";
  const entry = {
    id: safeId,
    text: INTERACTION_REACTION_BUBBLE_TEXT[safeId] || "",
    source: "interaction_reaction_bubble",
    ts: Date.now(),
    hint: INTERACTION_REACTION_HINT_ALLOWLIST.has(hint) ? hint : "none",
  };
  recentInteractionReactionBubbles.push(entry);
  if (recentInteractionReactionBubbles.length > INTERACTION_REACTION_BUBBLE_MAX) {
    recentInteractionReactionBubbles.shift();
  }
  currentInteractionReactionBubble = {
    id: entry.id,
    text: entry.text,
    source: entry.source,
  };
  enqueueReactionBubbleOutputDiagnostics(currentInteractionReactionBubble);
  mirrorInteractionReactionBubble(currentInteractionReactionBubble);
  return currentInteractionReactionBubble;
}

function enqueueReactionBubbleOutputDiagnostics(bubble) {
  const rawId = bubble && typeof bubble.id === "string" ? bubble.id : "";
  const safeId = INTERACTION_REACTION_BUBBLE_ALLOWLIST.has(rawId) ? rawId : "none";
  if (safeId === "none") return null;
  return enqueueOutputQueueItem({
    source: "reaction_bubble",
    priority: "P4_NORMAL_REACTION",
    channel: "pet_bubble",
    payload: { bubbleId: safeId },
    ttlMs: INTERACTION_REACTION_BUBBLE_TTL_MS,
    interruptible: true,
    ttsEligible: false,
    historyEligible: false,
    copyExportEligible: false,
    reason: "interaction_reaction_bubble",
  });
}

// TASK-217: Expression suggestion layer — maps reaction hint → local expression suggestion.
// Pure local renderer memory; no Pet Window, no IPC, no /chat, no TTS, no history write.
const INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST = new Set([
  "neutral",
  "focused",
  "happy",
  "proud",
  "annoyed",
  "sleepy",
]);
const INTERACTION_EXPRESSION_SUGGESTION_MAX = 20;
const INTERACTION_EXPRESSION_MIRROR_COOLDOWN_MS = 300;
var recentInteractionExpressionSuggestions = []; // var: exposed to vm sandbox for smoke tests
var currentInteractionExpressionSuggestion = "neutral"; // var: exposed to vm sandbox for smoke tests
var pendingInteractionExpressionMirror = null; // var: exposed to vm sandbox for smoke tests
var interactionExpressionMirrorTimer = null; // var: exposed to vm sandbox for smoke tests
var lastInteractionExpressionMirrorAt = 0; // var: exposed to vm sandbox for smoke tests

function deriveInteractionExpressionSuggestion(hint) {
  switch (hint) {
    case "user_active":        return "focused";
    case "message_management": return "neutral";
    case "correction":         return "annoyed";
    case "reset":              return "neutral";
    case "attention_returned": return "happy";
    case "pet_attention":      return "proud";
    case "none":               return "neutral";
    default:                   return "neutral";
  }
}

function recordInteractionExpressionSuggestion(expression, hint) {
  const safeExpression = INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST.has(expression) ? expression : "neutral";
  const entry = { expression: safeExpression, ts: Date.now(), hint };
  recentInteractionExpressionSuggestions.push(entry);
  if (recentInteractionExpressionSuggestions.length > INTERACTION_EXPRESSION_SUGGESTION_MAX) {
    recentInteractionExpressionSuggestions.shift();
  }
  currentInteractionExpressionSuggestion = safeExpression;
  enqueueExpressionMirrorOutputDiagnostics(safeExpression); // TASK-231
  mirrorInteractionExpressionSuggestion(safeExpression); // TASK-218
}

// TASK-218/219: mirror expression suggestion to Pet Window via narrow IPC bridge.
// Only sends allowlisted expression strings; no speech, no bubble, no TTS.
function sendInteractionExpressionMirrorNow(expression) {
  const safeExpression = INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST.has(expression)
    ? expression : "neutral";
  const bridge = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!bridge || typeof bridge.sendPetExpressionSuggestion !== "function") return false;
  lastInteractionExpressionMirrorAt = Date.now();
  bridge.sendPetExpressionSuggestion({ expression: safeExpression });
  return true;
}

function flushPendingInteractionExpressionMirror() {
  if (interactionExpressionMirrorTimer) {
    clearTimeout(interactionExpressionMirrorTimer);
    interactionExpressionMirrorTimer = null;
  }
  if (!pendingInteractionExpressionMirror) return false;
  const expression = pendingInteractionExpressionMirror;
  pendingInteractionExpressionMirror = null;
  return sendInteractionExpressionMirrorNow(expression);
}

function scheduleInteractionExpressionMirror(expression) {
  const safeExpression = INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST.has(expression)
    ? expression : "neutral";
  const elapsed = Date.now() - lastInteractionExpressionMirrorAt;
  if (!lastInteractionExpressionMirrorAt || elapsed >= INTERACTION_EXPRESSION_MIRROR_COOLDOWN_MS) {
    return sendInteractionExpressionMirrorNow(safeExpression);
  }

  pendingInteractionExpressionMirror = safeExpression;
  if (!interactionExpressionMirrorTimer) {
    const delay = Math.max(0, INTERACTION_EXPRESSION_MIRROR_COOLDOWN_MS - elapsed);
    interactionExpressionMirrorTimer = setTimeout(() => {
      interactionExpressionMirrorTimer = null;
      flushPendingInteractionExpressionMirror();
    }, delay);
  }
  return false;
}

function mirrorInteractionExpressionSuggestion(expression) {
  return scheduleInteractionExpressionMirror(expression);
}

// TASK-231: Enqueue expression mirror diagnostics item (local only).
// Does not dispatch, does not affect mirror scheduling or TASK-219 debounce behavior.
function enqueueExpressionMirrorOutputDiagnostics(expression) {
  const safeExpression = INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST.has(expression) ? expression : null;
  if (!safeExpression) return null;
  return enqueueOutputQueueItem({
    source: "expression_mirror",
    priority: "P4_NORMAL_REACTION",
    channel: "visual_expression",
    payload: { expression: safeExpression },
    ttlMs: 0,
    interruptible: true,
    ttsEligible: false,
    historyEligible: false,
    copyExportEligible: false,
    reason: "interaction_expression_suggestion",
  });
}

// TASK-232: Enqueue chat reply diagnostics item (local only).
// Does not store reply text; payload carries only source, mood, and replyLength.
function enqueueChatReplyOutputDiagnostics(data) {
  const reply = data && typeof data.reply === "string" ? data.reply : null;
  if (reply === null) return null;
  const safeSource = window.dragonOutputQueue.CHAT_REPLY_SAFE_SOURCE_ALLOWLIST.has(data.source) ? data.source : "unknown";
  const safeMood = CHARACTER_MOOD_STATE_ALLOWLIST.has(data.mood) ? data.mood : "neutral";
  const replyLength = Math.max(0, Math.min(10000, reply.length));
  return enqueueOutputQueueItem({
    source: "chat_reply",
    priority: "P2_LLM_REPLY",
    channel: "full_app_chat",
    payload: { source: safeSource, mood: safeMood, replyLength },
    ttlMs: 0,
    interruptible: false,
    ttsEligible: false,
    historyEligible: true,
    copyExportEligible: true,
    reason: "chat_reply_rendered",
  });
}

// TASK-220: mirror fixed reaction bubble text to Pet Window via narrow IPC.
// Text is derived from allowlisted ids only; caller-provided text is ignored.
function mirrorInteractionReactionBubble(bubble) {
  const rawId = bubble && typeof bubble.id === "string" ? bubble.id : "";
  const safeId = INTERACTION_REACTION_BUBBLE_ALLOWLIST.has(rawId) ? rawId : "none";
  const safeText = INTERACTION_REACTION_BUBBLE_TEXT[safeId] || "";
  if (!safeText) return false;
  const bridge = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!bridge || typeof bridge.sendPetReactionBubble !== "function") return false;
  bridge.sendPetReactionBubble({
    id: safeId,
    text: safeText,
    source: "interaction_reaction_bubble",
    ts: Date.now(),
    ttlMs: INTERACTION_REACTION_BUBBLE_TTL_MS,
  });
  return true;
}

// TASK-239: Diagnostics Drawer engine delegated to window.dragonDiagnosticsDrawer module (diagnostics-drawer.js).
function formatCharacterStatePreview(state) { return window.dragonDiagnosticsDrawer.formatCharacterStatePreview(state); }
function formatInteractionDiagnosticsPreview(context) { return window.dragonDiagnosticsDrawer.formatInteractionDiagnosticsPreview(context); }
function formatInteractionDiagnosticsSummary(context) { return window.dragonDiagnosticsDrawer.formatInteractionDiagnosticsSummary(context); }
function formatInteractionDiagnosticsDetails(context) { return window.dragonDiagnosticsDrawer.formatInteractionDiagnosticsDetails(context); }
function ensureInteractionDiagnosticsDrawerElements(c, s, t, d) { return window.dragonDiagnosticsDrawer.ensureInteractionDiagnosticsDrawerElements(c, s, t, d); }
function renderInteractionReactionPreview() {
  window.dragonDiagnosticsDrawer.renderInteractionDiagnosticsPreview({
    elements: {
      root: interactionDiagnosticsContainer || document.getElementById("interaction-reaction-preview"),
      summary: interactionDiagnosticsSummary || document.getElementById("interaction-diagnostics-summary"),
      toggle: interactionDiagnosticsToggle || document.getElementById("interaction-diagnostics-toggle"),
      details: interactionDiagnosticsDetails || document.getElementById("interaction-diagnostics-details"),
    },
    reactionHint: currentInteractionReactionHint,
    expression: currentInteractionExpressionSuggestion,
    behaviorDecision: currentCompanionBehaviorDecision,
    characterState: currentCharacterState,
    outputQueueSnapshot: getOutputQueueSnapshot(),
  });
}
function toggleInteractionDiagnosticsDrawer() {
  window.dragonDiagnosticsDrawer.toggleInteractionDiagnosticsDrawer();
  renderInteractionReactionPreview();
}

function recordInteractionEvent(type, payload = {}) {
  if (!INTERACTION_EVENT_ALLOWLIST.has(type)) return;
  const SAFE_KEYS = new Set(["source", "role", "messageLength", "count"]);
  const safe = {};
  for (const [k, v] of Object.entries(payload)) {
    if (SAFE_KEYS.has(k)) safe[k] = v;
  }
  const event = { type, ts: Date.now(), ...safe };
  recentInteractionEvents.push(event);
  if (recentInteractionEvents.length > INTERACTION_EVENT_MAX) {
    recentInteractionEvents.shift();
  }
  const hint = deriveInteractionReactionHint(event);
  recordInteractionReactionHint(hint, event);
}

// TASK-113: smarter auto-scroll helpers — user sends always scroll,
// AI replies only scroll when user is already near the bottom.
const CHAT_NEAR_BOTTOM_THRESHOLD_PX = 80;

function isChatNearBottom() {
  return (chatArea.scrollHeight - chatArea.scrollTop - (chatArea.clientHeight || 0))
    < CHAT_NEAR_BOTTOM_THRESHOLD_PX;
}

function scrollChatToBottom() {
  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(() => { chatArea.scrollTop = chatArea.scrollHeight; });
  } else {
    chatArea.scrollTop = chatArea.scrollHeight;
  }
}

function maybeScrollChatToBottom() {
  if (isChatNearBottom()) {
    scrollChatToBottom();
  } else {
    // TASK-202: don't force scroll while user reads history; show jump button instead.
    // Suppressed while search is active to avoid disrupting highlighted results.
    if (!isChatSearchActive()) showNewMessageBtn();
  }
}

// TASK-202: show/hide "↓ 新訊息" jump-to-bottom button.
function showNewMessageBtn() {
  if (chatNewMsgBtn) chatNewMsgBtn.hidden = false;
}
function hideNewMessageBtn() {
  if (chatNewMsgBtn) chatNewMsgBtn.hidden = true;
}

function isChatSearchActive() {
  return chatSearchInput && (chatSearchInput.value || "").trim().length > 0;
}

function hasFormalChatMessage() {
  if (!chatArea) return false;
  return Array.from(chatArea.children || []).some((child) => {
    const classes = typeof child.className === "string" ? child.className : "";
    const isUserOrPet = classes.includes("user") || classes.includes("pet");
    return isUserOrPet && child.dataset && child.dataset.formalChat === "true";
  });
}

function updateEmptyChatState() {
  if (!chatEmptyState) return;
  const shouldShow = !hasFormalChatMessage() && !isChatSearchActive();
  chatEmptyState.hidden = !shouldShow;
  chatEmptyState.setAttribute("aria-hidden", shouldShow ? "false" : "true");
}

function setClearChatStatus(message, timeoutMs = 0) {
  if (!clearChatStatus) return;
  if (clearChatStatusTimer) {
    clearTimeout(clearChatStatusTimer);
    clearChatStatusTimer = null;
  }
  clearChatStatus.replaceChildren();
  clearChatStatus.textContent = message || "";
  if (message && timeoutMs > 0) {
    clearChatStatusTimer = setTimeout(() => {
      clearChatStatus.textContent = "";
      clearChatStatusTimer = null;
    }, timeoutMs);
  }
}

function collectUndoableChatEntries() {
  if (!chatArea) return [];
  return Array.from(chatArea.children || [])
    .filter((child) => {
      const classes = typeof child.className === "string" ? child.className : "";
      const isUserOrPet = classes.includes("user") || classes.includes("pet");
      return isUserOrPet && child.dataset && child.dataset.formalChat === "true";
    })
    .map((child) => {
      const classes = child.className.split(" ");
      const ts = Number(child.dataset.ts || 0);
      return {
        role: classes.includes("user") ? "user" : "pet",
        text: child.dataset.msgText || "",
        source: child.dataset.source || "unknown",
        ts: Number.isFinite(ts) ? ts : 0,
      };
    })
    .filter((entry) => entry.text);
}

function collectFormalChatMessageElements() {
  if (!chatArea) return [];
  return Array.from(chatArea.children || []).filter((child) => {
    const classes = typeof child.className === "string" ? child.className : "";
    const isUserOrPet = classes.includes("user") || classes.includes("pet");
    return isUserOrPet && child.dataset && child.dataset.formalChat === "true";
  });
}

function clearUndoClearState({ clearStatus = false } = {}) {
  lastClearedChatEntries = [];
  if (undoClearTimer) {
    clearTimeout(undoClearTimer);
    undoClearTimer = null;
  }
  if (clearStatus) setClearChatStatus("");
}

function clearUndoDeleteMessageState({ clearStatus = false } = {}) {
  lastDeletedChatMessage = null;
  if (undoDeleteMessageTimer) {
    clearTimeout(undoDeleteMessageTimer);
    undoDeleteMessageTimer = null;
  }
  if (clearStatus) setClearChatStatus("");
}

function setComposerValue(value) {
  if (!msgInput) return;
  msgInput.value = value || "";
  msgInput.style.height = "auto";
  msgInput.style.height = Math.min(msgInput.scrollHeight || 40, 100) + "px";
}

function clearEditingMessageState({ restoreInput = false, clearStatus = false } = {}) {
  const prev = editingMessageState;
  editingMessageState = null;
  if (restoreInput && prev) setComposerValue(prev.inputBeforeEdit || "");
  if (!isSending && sendBtn) sendBtn.textContent = SEND_BUTTON_DEFAULT_TEXT;
  if (clearStatus) setClearChatStatus("");
}

function showEditMessageState() {
  if (!clearChatStatus) return;
  if (clearChatStatusTimer) {
    clearTimeout(clearChatStatusTimer);
    clearChatStatusTimer = null;
  }
  clearChatStatus.textContent = "正在編輯最後一則訊息";
  const cancelBtn = document.createElement("button");
  cancelBtn.type = "button";
  cancelBtn.className = "chat-edit-cancel-btn";
  cancelBtn.textContent = "取消";
  cancelBtn.addEventListener("click", () => {
    cancelEditUserMessage();
  });
  clearChatStatus.appendChild(cancelBtn);
}

function showUndoClearState(entries) {
  clearUndoClearState();
  clearUndoDeleteMessageState();
  clearEditingMessageState();
  lastClearedChatEntries = entries.map((entry) => ({ ...entry }));
  if (!clearChatStatus) return;
  if (clearChatStatusTimer) {
    clearTimeout(clearChatStatusTimer);
    clearChatStatusTimer = null;
  }
  clearChatStatus.textContent = "對話紀錄已清除。";
  const undoBtn = document.createElement("button");
  undoBtn.type = "button";
  undoBtn.className = "clear-chat-undo-btn";
  undoBtn.textContent = "復原";
  undoBtn.addEventListener("click", () => {
    undoClearChat();
  });
  clearChatStatus.appendChild(undoBtn);
  undoClearTimer = setTimeout(() => {
    clearUndoClearState({ clearStatus: true });
  }, UNDO_CLEAR_MS);
}

async function persistChatHistoryEntries(entries) {
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!api || typeof api.chatHistoryAppend !== "function") return;
  for (const entry of entries) {
    await api.chatHistoryAppend({
      role: entry.role,
      text: entry.text,
      source: entry.source,
      ts: entry.ts,
    });
  }
}

async function rewritePersistedChatHistory(entries) {
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!api ||
      typeof api.chatHistoryClear !== "function" ||
      typeof api.chatHistoryAppend !== "function") {
    return false;
  }
  await api.chatHistoryClear();
  await persistChatHistoryEntries(entries);
  return true;
}

function renderFormalChatEntries(entries, { preserveSearch = false } = {}) {
  closeChatContextMenu();
  const searchQuery = preserveSearch && chatSearchInput ? chatSearchInput.value : "";
  lastDateKey = null;
  chatArea.replaceChildren();
  for (const entry of entries) {
    appendMessage(entry.role, entry.text, {
      noHistory: true,
      source: entry.source,
      ts: entry.ts,
    });
  }
  hideNewMessageBtn();
  if (chatSearchInput && !preserveSearch) chatSearchInput.value = "";
  filterChatMessages(searchQuery);
  updateEmptyChatState();
}

function isEditableUserEntryAtIndex(entries, index) {
  if (!Array.isArray(entries) || index < 0 || index >= entries.length) return false;
  const entry = entries[index];
  if (!entry || entry.role !== "user") return false;
  let lastUserIndex = -1;
  entries.forEach((item, idx) => {
    if (item && item.role === "user") lastUserIndex = idx;
  });
  if (index !== lastUserIndex) return false;
  const trailing = entries.slice(index + 1);
  return trailing.length <= 1 && trailing.every((item) => item && item.role === "pet");
}

function isLastEditableUserMessage(messageEl) {
  if (!messageEl || !messageEl.dataset) return false;
  const classes = typeof messageEl.className === "string" ? messageEl.className.split(" ") : [];
  if (!classes.includes("user") || messageEl.dataset.formalChat !== "true") return false;
  const messageEls = collectFormalChatMessageElements();
  const index = messageEls.indexOf(messageEl);
  return isEditableUserEntryAtIndex(collectUndoableChatEntries(), index);
}

function closeChatContextMenu() {
  if (chatContextMenu && typeof chatContextMenu.remove === "function") {
    chatContextMenu.remove();
  }
  chatContextMenu = null;
}

function createContextMenuButton(label, className, onClick) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = className;
  btn.textContent = label;
  btn.setAttribute("role", "menuitem");
  btn.tabIndex = 0;
  btn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    onClick();
  });
  btn.addEventListener("keydown", (e) => {
    if (e.key !== "Enter" && e.key !== " ") return;
    e.preventDefault();
    e.stopPropagation();
    onClick();
  });
  return btn;
}

function getChatContextViewportSize() {
  const docEl = typeof document !== "undefined" ? document.documentElement : null;
  const body = typeof document !== "undefined" ? document.body : null;
  return {
    width: Number(window.innerWidth || (docEl && docEl.clientWidth) || (body && body.clientWidth) || 1024),
    height: Number(window.innerHeight || (docEl && docEl.clientHeight) || (body && body.clientHeight) || 768),
  };
}

function getChatContextMenuSize(menu) {
  if (menu && typeof menu.getBoundingClientRect === "function") {
    const rect = menu.getBoundingClientRect();
    if (rect && rect.width > 0 && rect.height > 0) {
      return { width: rect.width, height: rect.height };
    }
  }
  const childCount = menu && menu.children ? menu.children.length : 2;
  return {
    width: menu && menu.offsetWidth ? menu.offsetWidth : CHAT_CONTEXT_MENU_FALLBACK_WIDTH,
    height: menu && menu.offsetHeight ? menu.offsetHeight : (childCount * CHAT_CONTEXT_MENU_ITEM_HEIGHT) + 8,
  };
}

function positionChatContextMenu(menu, pointerX, pointerY) {
  if (!menu) return;
  const viewport = getChatContextViewportSize();
  const size = getChatContextMenuSize(menu);
  const maxLeft = Math.max(CHAT_CONTEXT_MENU_MARGIN, viewport.width - size.width - CHAT_CONTEXT_MENU_MARGIN);
  const maxTop = Math.max(CHAT_CONTEXT_MENU_MARGIN, viewport.height - size.height - CHAT_CONTEXT_MENU_MARGIN);
  const left = Math.min(Math.max(CHAT_CONTEXT_MENU_MARGIN, Number(pointerX) || 0), maxLeft);
  const top = Math.min(Math.max(CHAT_CONTEXT_MENU_MARGIN, Number(pointerY) || 0), maxTop);
  menu.style.left = `${Math.round(left)}px`;
  menu.style.top = `${Math.round(top)}px`;
}

function showChatMessageContextMenu(messageEl, event) {
  if (!messageEl || !messageEl.dataset || messageEl.dataset.formalChat !== "true") return false;
  const classes = typeof messageEl.className === "string" ? messageEl.className.split(" ") : [];
  const isUserOrPet = classes.includes("user") || classes.includes("pet");
  if (!isUserOrPet) return false;
  if (event && typeof event.preventDefault === "function") event.preventDefault();
  if (event && typeof event.stopPropagation === "function") event.stopPropagation();
  closeChatContextMenu();

  const menu = document.createElement("div");
  menu.className = "chat-context-menu";
  menu.setAttribute("role", "menu");
  menu.setAttribute("aria-label", "訊息操作");

  const copyItem = createContextMenuButton("複製", "chat-context-menu-item", () => {
    copySingleMessage(messageEl.dataset.msgText || "", copyItem);
    closeChatContextMenu();
  });
  menu.appendChild(copyItem);
  menu.appendChild(createContextMenuButton("刪除", "chat-context-menu-item", () => {
    closeChatContextMenu();
    deleteSingleChatMessage(messageEl);
  }));
  if (classes.includes("user") && isLastEditableUserMessage(messageEl)) {
    menu.appendChild(createContextMenuButton("編輯", "chat-context-menu-item", () => {
      closeChatContextMenu();
      startEditUserMessage(messageEl);
    }));
  }

  chatArea.appendChild(menu);
  chatContextMenu = menu;
  positionChatContextMenu(
    menu,
    event && typeof event.clientX === "number" ? event.clientX : 0,
    event && typeof event.clientY === "number" ? event.clientY : 0
  );
  const firstAction = Array.from(menu.children || []).find((child) => !child.disabled && typeof child.focus === "function");
  if (firstAction) firstAction.focus();
  return true;
}

function isInsideChatContextMenu(target) {
  let node = target;
  while (node) {
    if (node === chatContextMenu) return true;
    node = node.parentNode;
  }
  return false;
}

function showUndoDeleteMessageState(deletedEntry, deletedIndex) {
  clearUndoDeleteMessageState();
  clearUndoClearState();
  clearEditingMessageState();
  lastDeletedChatMessage = {
    entry: { ...deletedEntry },
    index: deletedIndex,
  };
  if (!clearChatStatus) return;
  if (clearChatStatusTimer) {
    clearTimeout(clearChatStatusTimer);
    clearChatStatusTimer = null;
  }
  clearChatStatus.textContent = "已刪除 1 則訊息。";
  const undoBtn = document.createElement("button");
  undoBtn.type = "button";
  undoBtn.className = "clear-chat-undo-btn single-message-undo-btn";
  undoBtn.textContent = "復原";
  undoBtn.addEventListener("click", () => {
    undoSingleMessageDelete();
  });
  clearChatStatus.appendChild(undoBtn);
  undoDeleteMessageTimer = setTimeout(() => {
    clearUndoDeleteMessageState({ clearStatus: true });
  }, UNDO_DELETE_MESSAGE_MS);
}

function resetClearChatConfirmation({ clearStatus = false } = {}) {
  clearChatConfirmPending = false;
  if (clearChatConfirmTimer) {
    clearTimeout(clearChatConfirmTimer);
    clearChatConfirmTimer = null;
  }
  if (clearChatBtn) {
    clearChatBtn.textContent = CLEAR_CHAT_DEFAULT_TEXT;
    clearChatBtn.classList.remove("confirm-pending");
  }
  if (clearStatus) setClearChatStatus("");
}

function beginClearChatConfirmation() {
  clearChatConfirmPending = true;
  if (clearChatBtn) {
    clearChatBtn.textContent = "再次點擊確認";
    clearChatBtn.classList.add("confirm-pending");
  }
  setClearChatStatus("再次點擊將清除所有對話紀錄");
  if (clearChatConfirmTimer) clearTimeout(clearChatConfirmTimer);
  clearChatConfirmTimer = setTimeout(() => {
    resetClearChatConfirmation({ clearStatus: true });
  }, CLEAR_CHAT_CONFIRM_MS);
}

async function handleClearChatClick() {
  if (!clearChatConfirmPending) {
    beginClearChatConfirmation();
    return;
  }
  resetClearChatConfirmation();
  await clearChatHistory();
}

// Avoid persisting default form values before the backend settings snapshot has
// been restored and rendered.
saveProviderSettingsBtn.disabled = true;

// ---------------------------------------------------------------------------
// Pet Expression (TASK-083) — mood → inline SVG face mapping
//
// Safety: SVG strings are static literals; no user input is interpolated.
// Renderer never calls Ollama directly; all /chat calls go to BACKEND_URL.
// ---------------------------------------------------------------------------

// Base dragon face parts shared by all expressions.
// Horns: two small filled triangles at the top of the 80×80 viewBox.
// Face: filled circle with a 1.5px accent stroke.
const _HORNS = `
  <polygon points="26,21 20,7 33,17" fill="#e94560" opacity="0.7"/>
  <polygon points="54,21 60,7 47,17" fill="#e94560" opacity="0.7"/>`;

const _FACE_NORMAL  = `<circle cx="40" cy="44" r="26" fill="#1e1e3a" stroke="#e94560" stroke-width="1.5"/>`;
const _FACE_ERROR   = `<circle cx="40" cy="44" r="26" fill="#1e1e3a" stroke="#9b2020" stroke-width="1.5"/>`;
const _FACE_OFFLINE = `<circle cx="40" cy="44" r="26" fill="#12122a" stroke="#3a3a5a" stroke-width="1.5" stroke-dasharray="4,3"/>`;

// Accent colour palette
const _A  = "#e94560";  // main accent
const _AD = "#7a2035";  // dimmed accent
const _ER = "#ff5555";  // error red
const _DM = "#4a4060";  // dim/offline

// ---------------------------------------------------------------------------
// SVG expression map — 10 supported moods
// ---------------------------------------------------------------------------
const PET_EXPRESSIONS = {

  neutral: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: neutral">${_HORNS}${_FACE_NORMAL}
    <circle cx="30" cy="42" r="4.5" fill="${_A}"/><circle cx="31" cy="41" r="2" fill="#0d0d1a"/>
    <circle cx="50" cy="42" r="4.5" fill="${_A}"/><circle cx="51" cy="41" r="2" fill="#0d0d1a"/>
    <line x1="33" y1="54" x2="47" y2="54" stroke="${_A}" stroke-width="2" stroke-linecap="round"/>
  </svg>`,

  happy: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: happy">${_HORNS}${_FACE_NORMAL}
    <path d="M26 44 Q30 37 34 44" stroke="${_A}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M46 44 Q50 37 54 44" stroke="${_A}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <path d="M31 53 Q40 63 49 53" stroke="${_A}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <circle cx="26" cy="50" r="3.5" fill="${_A}" opacity="0.3"/>
    <circle cx="54" cy="50" r="3.5" fill="${_A}" opacity="0.3"/>
  </svg>`,

  focused: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: focused">${_HORNS}${_FACE_NORMAL}
    <rect x="24" y="40" width="12" height="4.5" rx="2.2" fill="${_A}"/>
    <rect x="44" y="40" width="12" height="4.5" rx="2.2" fill="${_A}"/>
    <line x1="23" y1="35" x2="36" y2="37.5" stroke="${_A}" stroke-width="1.8" stroke-linecap="round"/>
    <line x1="44" y1="37.5" x2="57" y2="35" stroke="${_A}" stroke-width="1.8" stroke-linecap="round"/>
    <path d="M33 55 Q40 52 47 55" stroke="${_A}" stroke-width="2" fill="none" stroke-linecap="round"/>
  </svg>`,

  proud: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: proud">${_HORNS}${_FACE_NORMAL}
    <path d="M26 44 Q30 37 34 44" stroke="${_A}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <circle cx="50" cy="42" r="4.5" fill="${_A}"/><circle cx="51" cy="41" r="2" fill="#0d0d1a"/>
    <path d="M34 54 Q42 62 49 55" stroke="${_A}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  </svg>`,

  annoyed: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: annoyed">${_HORNS}${_FACE_NORMAL}
    <circle cx="30" cy="43" r="4.5" fill="${_A}"/><circle cx="31" cy="42" r="2" fill="#0d0d1a"/>
    <circle cx="50" cy="43" r="4.5" fill="${_A}"/><circle cx="51" cy="42" r="2" fill="#0d0d1a"/>
    <line x1="23" y1="34" x2="36" y2="37" stroke="${_A}" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="44" y1="37" x2="57" y2="34" stroke="${_A}" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M33 57 Q40 51 47 57" stroke="${_A}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
    <circle cx="26" cy="49" r="4" fill="${_A}" opacity="0.18"/>
    <circle cx="54" cy="49" r="4" fill="${_A}" opacity="0.18"/>
  </svg>`,

  sleepy: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: sleepy">${_HORNS}${_FACE_NORMAL}
    <path d="M25 42 A5 5 0 0 1 35 42" fill="${_A}"/>
    <path d="M45 42 A5 5 0 0 1 55 42" fill="${_A}"/>
    <ellipse cx="40" cy="55" rx="5.5" ry="3.5" fill="${_A}" opacity="0.65"/>
    <text x="58" y="33" font-family="sans-serif" font-size="10" fill="${_A}" opacity="0.8">z</text>
    <text x="63" y="25" font-family="sans-serif" font-size="7"  fill="${_A}" opacity="0.5">z</text>
  </svg>`,

  worried: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: worried">${_HORNS}${_FACE_NORMAL}
    <circle cx="30" cy="43" r="4.5" fill="${_A}"/><circle cx="31" cy="42" r="2" fill="#0d0d1a"/>
    <circle cx="50" cy="43" r="4.5" fill="${_A}"/><circle cx="51" cy="42" r="2" fill="#0d0d1a"/>
    <line x1="25" y1="36" x2="35" y2="34" stroke="${_A}" stroke-width="2" stroke-linecap="round"/>
    <line x1="45" y1="34" x2="55" y2="36" stroke="${_A}" stroke-width="2" stroke-linecap="round"/>
    <path d="M32 55 Q36 51 40 55 Q44 59 48 55" stroke="${_A}" stroke-width="2" fill="none" stroke-linecap="round"/>
  </svg>`,

  pending: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: thinking">${_HORNS}${_FACE_NORMAL}
    <circle cx="30" cy="42" r="4.5" fill="${_A}"/><circle cx="31" cy="41" r="2" fill="#0d0d1a"/>
    <circle cx="50" cy="42" r="4.5" fill="${_A}"/><circle cx="51" cy="41" r="2" fill="#0d0d1a"/>
    <line x1="34" y1="54" x2="46" y2="54" stroke="${_A}" stroke-width="1.5" stroke-linecap="round"/>
    <circle cx="31" cy="68" r="2.5" fill="${_A}" opacity="0.5"/>
    <circle cx="40" cy="70" r="2.5" fill="${_A}" opacity="0.75"/>
    <circle cx="49" cy="68" r="2.5" fill="${_A}" opacity="0.5"/>
  </svg>`,

  error: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: error">${_HORNS}${_FACE_ERROR}
    <line x1="25" y1="37" x2="34" y2="46" stroke="${_ER}" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="34" y1="37" x2="25" y2="46" stroke="${_ER}" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="46" y1="37" x2="55" y2="46" stroke="${_ER}" stroke-width="2.5" stroke-linecap="round"/>
    <line x1="55" y1="37" x2="46" y2="46" stroke="${_ER}" stroke-width="2.5" stroke-linecap="round"/>
    <path d="M33 57 Q40 51 47 57" stroke="${_ER}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  </svg>`,

  offline: `<svg viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Christina: offline">
    <polygon points="26,21 20,7 33,17" fill="${_DM}" opacity="0.5"/>
    <polygon points="54,21 60,7 47,17" fill="${_DM}" opacity="0.5"/>
    ${_FACE_OFFLINE}
    <circle cx="30" cy="43" r="4.5" fill="${_DM}"/>
    <circle cx="50" cy="43" r="4.5" fill="${_DM}"/>
    <path d="M33 55 Q40 60 47 55" stroke="${_DM}" stroke-width="2" fill="none" stroke-linecap="round"/>
    <line x1="16" y1="62" x2="64" y2="26" stroke="#5a5a7a" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
  </svg>`,
};

/** All moods the backend may return that have a defined expression. */
const KNOWN_MOODS = new Set(Object.keys(PET_EXPRESSIONS));

/**
 * Update the pet face to reflect the given mood.
 * Tries to load a PNG asset first; falls back to inline SVG placeholder.
 * Unknown moods fall back to "neutral" for the expression (mood label is unaffected).
 *
 * Asset path: assets/pet/christina/expressions/christina_<mood>.png
 * Safety: safeMood is always a key from KNOWN_MOODS — no user input in path or SVG.
 *
 * TASK-086: image-with-SVG-fallback strategy
 *   1. Set inline SVG immediately (no flash while probe runs).
 *   2. Probe PNG asset via Image(); if onload fires, replace SVG with <img>.
 *   3. If onerror fires (file absent), SVG placeholder remains — UI never breaks.
 *   4. Stale-mood guard: discard onload result if expression changed mid-flight.
 *   5. typeof Image guard: no-op in non-browser / test environments without Image.
 */
function setPetExpression(mood) {
  const safeMood = KNOWN_MOODS.has(mood) ? mood : "neutral";

  // ── 1. Immediate SVG placeholder — no visible flash ───────────────────────
  petFace.innerHTML = PET_EXPRESSIONS[safeMood];
  petFace.setAttribute("data-mood", safeMood);
  petFace.setAttribute("aria-label", `Christina expression: ${safeMood}`);

  // ── 2. Probe PNG asset ─────────────────────────────────────────────────────
  // Guard: Image may be undefined in non-browser / unit-test environments.
  if (typeof Image === "undefined") return;
  const imgPath = `assets/pet/christina/expressions/christina_${safeMood}.png`;
  const probe = new Image();

  probe.onload = function () {
    // ── 3. Stale-mood guard ────────────────────────────────────────────────
    // If the mood changed while the probe was in-flight, discard this result.
    if (petFace.getAttribute("data-mood") !== safeMood) return;
    // Replace SVG with <img>; keep object-fit so horns/head stay inside 80×80.
    const el = document.createElement("img");
    el.src = imgPath;
    el.alt = `Christina expression: ${safeMood}`;
    el.style.cssText = "width:100%;height:100%;object-fit:contain;";
    petFace.innerHTML = "";
    petFace.appendChild(el);
  };

  probe.onerror = function () {
    // PNG absent or failed — SVG placeholder already set above; nothing to do.
  };

  probe.src = imgPath;
}

/** Update the small hint text under the pet face. */
function setPetHint(text) {
  petDisplayHint.textContent = text;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// TASK-195: format Unix ms timestamp as HH:mm local time.
function formatMsgTime(ts) {
  try {
    const d = new Date(ts);
    return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
  } catch (_e) {
    return "";
  }
}

// TASK-203: full date+time string for the title/tooltip on message metadata.
function formatFullTimestamp(ts) {
  try {
    const d = new Date(ts);
    const date = d.getFullYear() + "-" +
      String(d.getMonth() + 1).padStart(2, "0") + "-" +
      String(d.getDate()).padStart(2, "0");
    const time = String(d.getHours()).padStart(2, "0") + ":" +
      String(d.getMinutes()).padStart(2, "0") + ":" +
      String(d.getSeconds()).padStart(2, "0");
    return `${date} ${time}`;
  } catch (_e) {
    return "";
  }
}

// TASK-195: map stored source value to a visible label; "" means no label shown.
function sourceLabelFor(source) {
  if (source === "pet_text" || source === "pet_input") return "Pet";
  if (source === "pet_voice") return "Voice";
  return "";  // "full_app", "unknown" and others are unlabelled — native Full App chat
}

// TASK-196: prefer preload IPC bridge; fall back to navigator.clipboard.
// Bridge returns a Promise (ipcRenderer.invoke) so we wrap in Promise.resolve to handle both
// sync mocks (tests) and the real async IPC path uniformly.
function writeToClipboard(text) {
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (api && typeof api.writeClipboardText === "function") {
    return Promise.resolve(api.writeClipboardText(text)).then((ok) => {
      if (ok === false) throw new Error("clipboard write failed");
    });
  }
  const clip = typeof navigator !== "undefined" ? navigator.clipboard : null;
  if (!clip || typeof clip.writeText !== "function") {
    return Promise.reject(new Error("clipboard unavailable"));
  }
  return clip.writeText(text);
}

// TASK-196: copy single message text to clipboard with brief button feedback.
function copySingleMessage(text, btn) {
  writeToClipboard(text).then(() => {
    if (!btn) return;
    btn.classList.add("copied");
    btn.textContent = "已複製";
    setTimeout(() => { btn.textContent = "複製"; btn.classList.remove("copied"); }, 1500);
  }).catch(() => {
    if (btn) {
      btn.textContent = "複製失敗";
      setTimeout(() => { btn.textContent = "複製"; }, 1500);
    }
  });
}

// TASK-207: returns "YYYY-MM-DD" string for a valid ts, null for ts=0 (no-timestamp entries).
function getMessageDateKey(ts) {
  if (!ts || ts <= 0) return null;
  const d = new Date(ts);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

// TASK-207: computes today/昨天/YYYY/MM/DD label at render time (not stored).
function formatDateSeparatorLabel(dateKey) {
  if (!dateKey) return "";
  const todayKey = getMessageDateKey(Date.now());
  if (dateKey === todayKey) return "今天";
  const yesterday = new Date(Date.now() - 86400000);
  const pad = (n) => String(n).padStart(2, "0");
  const yestKey = `${yesterday.getFullYear()}-${pad(yesterday.getMonth() + 1)}-${pad(yesterday.getDate())}`;
  if (dateKey === yestKey) return "昨天";
  return dateKey.replace(/-/g, "/");
}

// TASK-207: insert a date divider row if dateKey changed since last insert.
function maybeInsertDateSeparator(ts) {
  const dateKey = getMessageDateKey(ts);
  if (!dateKey || dateKey === lastDateKey) return;
  lastDateKey = dateKey;
  const sep = document.createElement("div");
  sep.className = "message date-separator";
  sep.dataset.dateKey = dateKey;
  const label = document.createElement("span");
  label.className = "date-separator-label";
  label.textContent = formatDateSeparatorLabel(dateKey);
  sep.appendChild(label);
  chatArea.appendChild(sep);
}

// TASK-205: shared transcript builder — used by copyAllChat and exportChatToFile.
function buildChatTranscript() {
  const messages = Array.from(chatArea.querySelectorAll(".message.user, .message.pet, .message.date-separator"));
  if (!messages.length) return "";
  const lines = [];
  let hasUserOrPet = false;
  for (const el of messages) {
    const classes = el.className.split(" ");
    if (classes.includes("date-separator")) {
      const labelEl = el.querySelector(".date-separator-label");
      const lbl = labelEl ? labelEl.textContent.trim() : (el.dataset.dateKey || "");
      if (lbl) lines.push(`── ${lbl} ──`);
      continue;
    }
    if (!el.dataset || el.dataset.formalChat !== "true") continue;
    hasUserOrPet = true;
    const name = classes.includes("user") ? "你" : "克莉絲蒂娜";
    const text = el.dataset.msgText || "";
    if (!text) continue;
    const meta = el.querySelector(".msg-meta");
    const rawMeta = meta ? meta.textContent.trim() : "";
    const time = rawMeta.includes("·") ? rawMeta.split("·").pop().trim() : rawMeta;
    lines.push(time ? `${name} ${time}:` : `${name}:`);
    lines.push(text);
    lines.push("");
  }
  if (!hasUserOrPet) return "";
  return lines.join("\n").trimEnd();
}

// TASK-196: format and copy all user/pet messages as plain text.
function copyAllChat() {
  const output = buildChatTranscript();
  if (!output) return;
  writeToClipboard(output).then(() => {
    if (!copyChatBtn) return;
    const prev = copyChatBtn.textContent;
    copyChatBtn.textContent = "已複製！";
    setTimeout(() => { copyChatBtn.textContent = prev; }, 1500);
  }).catch(() => {
    if (copyChatBtn) {
      const prev = copyChatBtn.textContent;
      copyChatBtn.textContent = "複製失敗";
      setTimeout(() => { copyChatBtn.textContent = prev; }, 1500);
    }
  });
}

// TASK-205: generate default export filename as dragon-pet-chat-YYYYMMDD-HHmm.txt
function generateExportFilename() {
  const d = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  const ymd = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
  const hm  = `${pad(d.getHours())}${pad(d.getMinutes())}`;
  return `dragon-pet-chat-${ymd}-${hm}.txt`;
}

// TASK-205: export full conversation to a user-chosen file via Save Dialog.
async function exportChatToFile() {
  if (!exportChatBtn) return;
  const transcript = buildChatTranscript();
  if (!transcript) {
    if (exportChatStatus) {
      exportChatStatus.textContent = "沒有可匯出的對話";
      setTimeout(() => { exportChatStatus.textContent = ""; }, 2000);
    }
    return;
  }
  if (!window.dragonPet || typeof window.dragonPet.saveTextFile !== "function") return;
  exportChatBtn.disabled = true;
  try {
    const result = await window.dragonPet.saveTextFile({
      defaultPath: generateExportFilename(),
      content: transcript,
    });
    if (result && result.canceled) {
      if (exportChatStatus) {
        exportChatStatus.textContent = "已取消匯出";
        setTimeout(() => { exportChatStatus.textContent = ""; }, 1500);
      }
      return;
    }
    if (result && result.ok) {
      if (exportChatStatus) {
        exportChatStatus.textContent = "已匯出對話";
        setTimeout(() => { exportChatStatus.textContent = ""; }, 2000);
      }
    } else {
      if (exportChatStatus) {
        exportChatStatus.textContent = "匯出失敗";
        setTimeout(() => { exportChatStatus.textContent = ""; }, 2000);
      }
    }
  } catch (_) {
    if (exportChatStatus) {
      exportChatStatus.textContent = "匯出失敗";
      setTimeout(() => { exportChatStatus.textContent = ""; }, 2000);
    }
  } finally {
    exportChatBtn.disabled = false;
  }
}

// TASK-200: title-based unread indicator for background pet replies.
function markUnread() {
  unreadChatCount += 1;
  document.title = `(${unreadChatCount}) Dragon Pet AI`;
  // TASK-204: notify Pet Window to show unread dot
  if (window.dragonPet && typeof window.dragonPet.notifyUnreadDot === "function") {
    window.dragonPet.notifyUnreadDot(unreadChatCount);
  }
}
function clearUnread() {
  if (unreadChatCount === 0) return;
  unreadChatCount = 0;
  document.title = UNREAD_BASE_TITLE;
  // TASK-204: notify Pet Window to hide unread dot
  if (window.dragonPet && typeof window.dragonPet.notifyUnreadDot === "function") {
    window.dragonPet.notifyUnreadDot(0);
  }
}

function appendMessage(role, text, {
  autoScroll = false,
  noHistory = false,
  source = "unknown",
  ts = 0,
  countsAsChat = true,
} = {}) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const sender = document.createElement("div");
  sender.className = "sender";
  sender.textContent =
    role === "user"   ? "You" :
    role === "pet"    ? "Christina" :
    role === "error"  ? "Error" :
    "System";

  const body = document.createElement("div");
  body.className = "msg-body"; // TASK-201: identify body div for search highlight
  body.textContent = text;

  wrap.appendChild(sender);
  wrap.appendChild(body);

  // TASK-195: source label + timestamp metadata line — small, muted, non-intrusive.
  const srcLabel = sourceLabelFor(source);
  const timeStr  = ts > 0 ? formatMsgTime(ts) : "";
  if (srcLabel || timeStr) {
    const meta = document.createElement("div");
    meta.className = "msg-meta";
    meta.textContent = srcLabel && timeStr ? `${srcLabel} · ${timeStr}` : srcLabel || timeStr;
    // TASK-203: full date+time tooltip if available; honest fallback for old records.
    if (ts > 0) {
      meta.title = formatFullTimestamp(ts);
    } else if (srcLabel && (role === "user" || role === "pet")) {
      // Old history entry written before TASK-195 ts persistence — no fabricated time.
      meta.title = "舊紀錄沒有時間資料";
    }
    wrap.appendChild(meta);
  }

  // TASK-211: message operations are exposed only through the custom context menu.
  if (role === "user" || role === "pet") {
    wrap.dataset.msgText = text;
    wrap.dataset.formalChat = countsAsChat ? "true" : "false";
    wrap.dataset.source = source;
    wrap.dataset.ts = String(typeof ts === "number" ? ts : 0);
    if (countsAsChat && !noHistory) {
      clearUndoClearState({ clearStatus: true });
      clearUndoDeleteMessageState({ clearStatus: true });
      clearEditingMessageState({ clearStatus: true });
    }
    if (countsAsChat) {
      wrap.addEventListener("contextmenu", (e) => {
        showChatMessageContextMenu(wrap, e);
      });
    }
  }

  // TASK-207: insert date divider before first message of a new day.
  if ((role === "user" || role === "pet") && ts > 0) maybeInsertDateSeparator(ts);

  chatArea.appendChild(wrap);
  updateEmptyChatState();

  // TASK-113: caller controls scroll via autoScroll flag.
  // User sends always pass { autoScroll: true }; AI replies use maybeScrollChatToBottom().
  if (autoScroll) scrollChatToBottom();
  // TASK-194: persist user/pet messages only; skip ephemeral roles and history-load replay.
  if (!noHistory && (role === "user" || role === "pet")) {
    saveChatHistoryEntry(role, text, source, ts);
  }
  // TASK-200: badge real pet replies while Full App is hidden / not focused.
  if (role === "pet" && !noHistory && document.hidden) {
    markUnread();
  }
  return wrap;
}

async function deleteSingleChatMessage(messageEl) {
  const messageEls = collectFormalChatMessageElements();
  const deletedIndex = messageEls.indexOf(messageEl);
  if (deletedIndex < 0) return false;
  const entries = collectUndoableChatEntries();
  const deletedEntry = entries[deletedIndex];
  if (!deletedEntry) return false;
  const nextEntries = entries.filter((_, idx) => idx !== deletedIndex);
  try {
    const rewritten = await rewritePersistedChatHistory(nextEntries);
    if (!rewritten) throw new Error("history unavailable");
  } catch (_e) {
    setClearChatStatus("刪除訊息失敗", 2000);
    return false;
  }
  renderFormalChatEntries(nextEntries, { preserveSearch: true });
  showUndoDeleteMessageState(deletedEntry, deletedIndex);
  recordInteractionEvent("message_deleted", { role: deletedEntry.role, source: deletedEntry.source });
  return true;
}

async function undoSingleMessageDelete() {
  if (!lastDeletedChatMessage) return false;
  const restore = {
    entry: { ...lastDeletedChatMessage.entry },
    index: lastDeletedChatMessage.index,
  };
  const entries = collectUndoableChatEntries();
  const insertIndex = Math.max(0, Math.min(restore.index, entries.length));
  const nextEntries = [
    ...entries.slice(0, insertIndex),
    restore.entry,
    ...entries.slice(insertIndex),
  ];
  clearUndoDeleteMessageState();
  try {
    const rewritten = await rewritePersistedChatHistory(nextEntries);
    if (!rewritten) throw new Error("history unavailable");
  } catch (_e) {
    setClearChatStatus("復原訊息失敗", 2000);
    return false;
  }
  renderFormalChatEntries(nextEntries, { preserveSearch: true });
  setClearChatStatus("已復原 1 則訊息", 2000);
  return true;
}

function startEditUserMessage(messageEl) {
  if (isSending || !messageEl || !messageEl.dataset) return false;
  const classes = typeof messageEl.className === "string" ? messageEl.className.split(" ") : [];
  if (!classes.includes("user") || messageEl.dataset.formalChat !== "true") return false;
  const messageEls = collectFormalChatMessageElements();
  const editIndex = messageEls.indexOf(messageEl);
  if (editIndex < 0) return false;
  if (!isEditableUserEntryAtIndex(collectUndoableChatEntries(), editIndex)) return false;
  const originalText = messageEl.dataset.msgText || "";
  if (!originalText) return false;

  const existingDraft = editingMessageState
    ? editingMessageState.inputBeforeEdit
    : (msgInput ? msgInput.value : "");
  clearUndoClearState();
  clearUndoDeleteMessageState();
  editingMessageState = {
    index: editIndex,
    originalText,
    source: messageEl.dataset.source || "unknown",
    ts: Number(messageEl.dataset.ts || 0) || 0,
    inputBeforeEdit: existingDraft || "",
  };
  setComposerValue(originalText);
  if (sendBtn) sendBtn.textContent = EDIT_SEND_BUTTON_TEXT;
  showEditMessageState();
  if (msgInput && typeof msgInput.focus === "function") msgInput.focus();
  return true;
}

function cancelEditUserMessage() {
  if (!editingMessageState) return false;
  clearEditingMessageState({ restoreInput: true });
  setClearChatStatus("已取消編輯", 1500);
  if (msgInput && typeof msgInput.focus === "function") msgInput.focus();
  return true;
}

async function undoClearChat() {
  if (!lastClearedChatEntries.length) return false;
  const entries = lastClearedChatEntries.map((entry) => ({ ...entry }));
  clearUndoClearState();
  try {
    const rewritten = await rewritePersistedChatHistory(entries);
    if (!rewritten) throw new Error("history unavailable");
    renderFormalChatEntries(entries);
    setClearChatStatus("已復原對話紀錄", 2000);
    return true;
  } catch (_e) {
    setClearChatStatus("復原對話失敗", 2000);
    return false;
  }
}

function saveChatHistoryEntry(role, text, source, ts) {
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!api || typeof api.chatHistoryAppend !== "function") return;
  const result = api.chatHistoryAppend({ role, text, source, ts });
  if (result && typeof result.catch === "function") result.catch(() => {});
}

async function loadAndRenderChatHistory() {
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!api || typeof api.chatHistoryLoad !== "function") return;
  let entries;
  try {
    entries = await api.chatHistoryLoad();
  } catch (_e) {
    return;
  }
  if (!Array.isArray(entries) || entries.length === 0) return;
  lastDateKey = null; // TASK-207: reset so history replay inserts separators fresh.
  let renderedCount = 0;
  for (const entry of entries) {
    if (!entry || !entry.role || !entry.text) continue;
    appendMessage(entry.role, entry.text, {
      noHistory: true,
      source: typeof entry.source === "string" ? entry.source : "unknown",
      ts: typeof entry.ts === "number" ? entry.ts : 0,
    });
    renderedCount++;
  }
  // TASK-195: low-profile restore separator — not saved to history (role="status").
  appendMessage("status", `已還原 ${renderedCount} 筆對話紀錄。`);
  // TASK-195 follow-up 3: clear "No chat response yet." once history is present.
  lastChatStatusMessage = "已載入最近對話";
  syncChatRuntimeProviderStatus();
  maybeScrollChatToBottom();
  updateEmptyChatState();
}

async function clearChatHistory() {
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!api || typeof api.chatHistoryClear !== "function") return false;
  const undoEntries = collectUndoableChatEntries();
  clearUndoDeleteMessageState();
  clearEditingMessageState();
  try {
    await api.chatHistoryClear();
  } catch (_e) {
    setClearChatStatus("清除對話失敗", 2000);
    return false;
  }
  lastDateKey = null; // TASK-207: reset so next messages start fresh.
  chatArea.replaceChildren();
  hideNewMessageBtn(); // TASK-202: no messages — dismiss jump button
  // TASK-198: reset search state after clearing so the empty chat shows cleanly.
  if (chatSearchInput) chatSearchInput.value = "";
  filterChatMessages("");
  updateEmptyChatState();
  if (undoEntries.length) {
    showUndoClearState(undoEntries);
  } else {
    clearUndoClearState();
    setClearChatStatus("對話紀錄已清除", 2000);
  }
  recordInteractionEvent("chat_history_cleared", { count: undoEntries.length });
  return true;
}

function setMood(mood) {
  currentMood = mood || "neutral";
  moodLabel.textContent = currentMood;
  // TASK-083: update pet expression to match mood (unknown moods fall back to neutral)
  setPetExpression(currentMood);
  // TASK-098: friendly hint label instead of raw mood name
  setPetHint(moodHintLabel(currentMood));
}

function setSending(state) {
  isSending = state;
  sendBtn.disabled = state;
  msgInput.disabled = state;
  sendBtn.textContent = state
    ? "Sending..."
    : (editingMessageState ? EDIT_SEND_BUTTON_TEXT : SEND_BUTTON_DEFAULT_TEXT);
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

// TASK-189: plain-English description of the current provider state for the status summary bar.
function calcProviderStatusSummary(settings) {
  const provider = settings.provider || "mock";
  const realEnabled = Boolean(settings.real_provider_enabled);
  const llmEnabled = Boolean(settings.llm_chat_enabled);
  const fallback = settings.fallback_to_mock !== false;
  const keyStatus = settings.key_status || "not_configured";

  if (!realEnabled || provider === "mock") {
    return { text: "目前：模擬模式 — 未連線真實 AI。", state: "mock" };
  }
  if (provider === "ollama") {
    if (!llmEnabled) {
      return { text: "目前：已選擇 Ollama — AI 聊天已停用。請啟用「AI 聊天」以使用。", state: "warning" };
    }
    if (fallback) {
      return { text: "目前：Ollama 含備援 — 有真實 AI 時優先使用，失敗時改用模擬。", state: "warning" };
    }
    return { text: "目前：Ollama 本地 AI 已連線。", state: "active" };
  }
  // Cloud provider
  const keyActive = ["configured", "not_tested", "test_success"].includes(keyStatus);
  const keyBad = ["invalid", "test_failed"].includes(keyStatus);
  if (keyBad) {
    return { text: `目前：已選擇 ${provider} — API 金鑰無效或連線測試失敗。`, state: "error" };
  }
  if (!keyActive) {
    return { text: `目前：已選擇 ${provider} — API 金鑰未設定。`, state: "error" };
  }
  if (!llmEnabled) {
    return { text: `目前：已選擇 ${provider} — AI 聊天已停用。請啟用「AI 聊天」以使用。`, state: "warning" };
  }
  return { text: `目前：${provider} 雲端 AI 已連線。`, state: "active" };
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
    return "Ollama 已回覆。本地 AI 正常運作。";
  }
  if (source === "llm_local_error") {
    return "本地 AI 失敗 — 模型可能仍在載入中。請確認 Ollama 正在執行且模型名稱正確。";
  }
  if (source === "mock") {
    if (settings.resolved_provider === "ollama" && !settings.llm_chat_enabled) {
      return "使用模擬模式 — AI 聊天已停用。請在 AI 設定中啟用「啟用 AI 聊天」。";
    }
    if (settings.resolved_provider === "ollama" && settings.fallback_to_mock !== false) {
      return "使用模擬備援 — 已設定 Ollama，但發生錯誤且已啟用備援模式。";
    }
    if (settings.provider === "ollama" || settings.resolved_provider === "ollama") {
      return "使用模擬模式 — 已選擇 Ollama 但未回應。請確認 Ollama 是否已啟動。";
    }
    return "使用模擬 provider。";
  }
  if (source === "llm_real") {
    return "雲端 AI 已回覆。";
  }
  if (source === "llm_real_error") {
    return "雲端 AI 失敗。請確認 API 金鑰與 provider 設定。";
  }
  if (source === "pending") {
    return isOllamaChatPath(settings)
      ? "等待本地 Ollama 回應中。第一次回覆可能需要較久，模型可能正在喚醒。"
      : "等待後端回覆中。";
  }
  if (source === "backend_offline") {
    return "後端無法連線。請確認後端服務正在執行。";
  }
  return "將在下一次回覆後顯示狀態。";
}

// TASK-098: friendly user-facing label for chat source
function sourceLabel(source) {
  const LABELS = {
    "llm_local":       "Local Ollama",
    "llm_local_error": "Ollama Error",
    "llm_real":        "Cloud AI",
    "llm_real_error":  "Cloud Error",
    "mock":            "Mock fallback",
    "backend_offline": "Backend offline",
    "pending":         "Thinking…",
    "error":           "Error",
    "not_checked":     "—",
  };
  return LABELS[source] || source || "—";
}

// TASK-098: friendly hint text for pet display state
function moodHintLabel(mood) {
  const HINTS = {
    "neutral":  "Listening",
    "focused":  "Focused",
    "happy":    "Happy",
    "proud":    "Proud",
    "annoyed":  "Annoyed",
    "worried":  "Worried",
    "sleepy":   "Sleepy",
    "pending":  "Thinking…",
    "error":    "Something went wrong",
    "offline":  "Offline",
  };
  return HINTS[mood] || mood || "";
}

// ---------------------------------------------------------------------------
// Idle Timer (TASK-108) — UI-only, no /chat calls
// ---------------------------------------------------------------------------

/**
 * Lock the companion hint/expression against idleTick overrides for durationMs ms.
 * Startup greeting and return-from-away greeting call this so the idle timer cannot
 * immediately replace the greeting hint with a low-priority idle update.
 *
 * Exposed as a top-level named function so smoke tests can extend the lock with a
 * large value to test lock behaviour without real-time delays.
 *
 * Safety: no /chat, no fetch, no external API. Pure timestamp arithmetic.
 */
function lockCompanionHint(durationMs) {
  hintLockedUntil = Date.now() + durationMs;
}

/**
 * Mark user activity, resetting the idle clock.
 * If returning from idle, restores expression and shows a brief welcome-back hint.
 *
 * Safety: no /chat, no fetch, no file access, no external API.
 * Exposed as a top-level named function so smoke tests can call it directly.
 */
function resetActivity() {
  const wasIdle = currentIdleState !== "active";
  // TASK-110: capture return-from-away eligibility BEFORE resetting state.
  // awayGreetingEligible is set by idleTick when elapsed ≥ 15 min.
  // awayGreetingFired prevents the same away session from showing the greeting twice.
  const shouldReturnGreet = awayGreetingEligible && !awayGreetingFired;
  lastActivityTime = Date.now();
  currentIdleState = "active";

  if (isSending) return; // never override loading expression

  if (shouldReturnGreet) {
    // TASK-110: long-away return greeting — shown once per away session.
    // Safety: no /chat, no fetch, no network, no external API.
    awayGreetingEligible = false;
    awayGreetingFired    = true;
    setPetExpression("annoyed");
    setPetHint("哼，汝終於回來了。吾才沒有一直等汝。");
    lockCompanionHint(HINT_LOCK_MS); // TASK-111: protect return greeting from idle override
  } else if (wasIdle) {
    // Short/medium idle return — restore expression and show brief welcome-back.
    const resumeMood = KNOWN_MOODS.has(currentMood) ? currentMood : "neutral";
    setPetExpression(resumeMood === "sleepy" ? "neutral" : resumeMood);
    setPetHint("終於回來了嗎，汝這傢伙。");
  }
}

/**
 * Idle check tick — driven by setInterval(idleTick, IDLE_CHECK_INTERVAL_MS).
 * Exposed as a top-level named function so renderer smoke tests can call it
 * directly with a synthetic timestamp to avoid real-time delays.
 *
 * @param {number} [_now] - Optional current timestamp in ms. Defaults to Date.now().
 *   Smoke tests pass a future timestamp to simulate elapsed time without waiting.
 *   Production code omits this parameter (setInterval calls idleTick with no args).
 *
 * State machine (one-way escalation until resetActivity is called):
 *   active     → short_idle  (elapsed ≥ 3 min):  neutral expression + waiting hint
 *   short_idle → long_idle   (elapsed ≥ 10 min): sleepy expression  + sleepy hint
 *   long_idle  : no further state change until resetActivity() is called
 *
 * Safety: no /chat, no fetch, no file access. Only touches setPetExpression / setPetHint.
 */
function idleTick(_now) {
  if (isSending) return; // guard: never override loading/response expressions
  const now = typeof _now === "number" ? _now : Date.now();
  const elapsed = now - lastActivityTime;
  // TASK-111: hint lock — state machine always advances, but expression/hint changes
  // are suppressed while a greeting lock is active. High-priority states (pending,
  // error, chat response) bypass this entirely since they call setPetExpression directly.
  const locked = now < hintLockedUntil;
  if (elapsed >= IDLE_THRESHOLD_LONG_MS && currentIdleState !== "long_idle") {
    currentIdleState = "long_idle";
    // TASK-110: entering long_idle resets the spam guard.
    awayGreetingFired = false;
    if (!locked) {
      setPetExpression("sleepy");
      setPetHint("哼……吾才沒有等到想睡。");
    }
  } else if (elapsed >= IDLE_THRESHOLD_SHORT_MS && currentIdleState === "active") {
    currentIdleState = "short_idle";
    if (!locked) {
      setPetExpression("neutral");
      setPetHint("吾在這裡。汝只是暫時發呆吧？");
    }
  }
  // TASK-110: mark eligible when ≥ 15 min have elapsed and user is in long_idle.
  // This flag is consumed (and cleared) by resetActivity() the next time the user
  // interacts, showing the one-shot return greeting.
  if (currentIdleState === "long_idle" &&
      elapsed >= IDLE_THRESHOLD_RETURN_MS &&
      !awayGreetingFired) {
    awayGreetingEligible = true;
  }
}

// Start the idle check timer — fires every IDLE_CHECK_INTERVAL_MS (60 s in production).
// Tests bypass this by calling sandbox.idleTick() directly with a mocked Date.
setInterval(idleTick, IDLE_CHECK_INTERVAL_MS);

function setChatRuntimeStatus(source, message = "", state = "normal") {
  lastChatSource = source || lastChatSource || "not_checked";
  lastChatStatusMessage = message || sourceStatusMessage(lastChatSource);

  // Source pill: technical format — smoke tests depend on exact text "source: <value>"
  chatSourceStatus.textContent = `source: ${lastChatSource}`;
  chatSourceStatus.className =
    state === "error"
      ? "chat-runtime-pill error"
      : state === "pending"
        ? "chat-runtime-pill pending"
        : "chat-runtime-pill";

  // TASK-098: friendly label pill — user-facing, replaces raw provider summary after chat
  chatProviderStatus.textContent = sourceLabel(lastChatSource);
  chatProviderStatus.className =
    state === "error"
      ? "chat-runtime-pill error"
      : state === "pending"
        ? "chat-runtime-pill pending"
        : "chat-runtime-pill friendly";

  chatRuntimeStatus.textContent = lastChatStatusMessage;
  chatRuntimeStatus.className = state === "error" ? "status-note error" : "status-note";
}

// TASK-195: human-readable provider label shown before first chat
function friendlyProviderName(p) {
  if (p === "ollama")    return "Ollama";
  if (p === "anthropic") return "Anthropic";
  if (p === "mock")      return "Mock";
  if (typeof p === "string" && p.length > 0) return p.charAt(0).toUpperCase() + p.slice(1);
  return "—";
}

function syncChatRuntimeProviderStatus() {
  if (lastChatSource === "not_checked") {
    // Before first chat: show friendly provider name
    const p = currentProviderSettings.provider || "mock";
    chatProviderStatus.textContent = friendlyProviderName(p);
    chatProviderStatus.className = "chat-runtime-pill";
    chatRuntimeStatus.textContent = lastChatStatusMessage;
  } else {
    // After first chat: show friendly source label (TASK-098)
    chatProviderStatus.textContent = sourceLabel(lastChatSource);
    chatProviderStatus.className = "chat-runtime-pill friendly";
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
    empty.textContent = "目前無記憶。";
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
      `顯示 ${items.length} / ${meta.count} 筆  |  筆數: ${meta.limit}  位移: ${meta.offset}`;
    auditList.appendChild(summary);
  }

  if (!items.length) {
    const empty = document.createElement("div");
    empty.className = "audit-empty";
    empty.textContent = "目前無診斷紀錄。";
    auditList.appendChild(empty);
    return;
  }

  for (const item of items) {
    const card = document.createElement("article");
    card.className = "audit-card";

    // Title row
    const title = document.createElement("div");
    title.className = "audit-card-title";
    title.textContent = `診斷 #${item.id}`;
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

  setAuditStatus("載入診斷紀錄中...");

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
      `已載入 ${data.items.length} 筆紀錄。資料庫共 ${data.count} 筆。`
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
  providerRealEnabledStatus.dataset.bool = settings.real_provider_enabled ? "true" : "false";
  providerLlmChatEnabledStatus.textContent = String(Boolean(settings.llm_chat_enabled));
  providerLlmChatEnabledStatus.dataset.bool = settings.llm_chat_enabled ? "true" : "false";
  providerFallbackStatus.textContent = String(settings.fallback_to_mock !== false);
  providerFallbackStatus.dataset.bool = settings.fallback_to_mock !== false ? "true" : "false";
  providerWarning.textContent = settings.provider === "ollama"
    ? "Ollama runs locally and uses your CPU/GPU. No API key is required; the renderer still calls only the backend."
    : "Using a real provider may incur charges from your API provider.";
  renderUsageSummary(settings.usage_summary);
  // TASK-056 / TASK-060: cache settings and update all key UI controls
  currentProviderSettings = settings;
  syncChatRuntimeProviderStatus();
  updateKeyUIState(settings);
  // TASK-189: update plain-English status summary
  const { text: summaryText, state: summaryState } = calcProviderStatusSummary(settings);
  providerStatusSummaryEl.textContent = summaryText;
  providerStatusSummaryEl.className = `provider-status-summary ${summaryState}`;
}

async function loadProviderSettings() {
  providerSettingsLoaded = false;
  saveProviderSettingsBtn.disabled = true;
  setProviderSettingsStatus("Loading provider settings...");

  try {
    const res = await fetch(`${BACKEND_URL}/provider/settings`);
    const settings = await parseJsonResponse(res);
    renderProviderSettings(settings);
    providerSettingsLoaded = true;
    saveProviderSettingsBtn.disabled = false;
    setProviderSettingsStatus("Provider settings loaded.");
  } catch (err) {
    renderUsageSummary(null);
    saveProviderSettingsBtn.disabled = true;
    setProviderSettingsStatus(formatBackendError(err), true);
  }
}

async function saveProviderSettings() {
  if (!providerSettingsLoaded) {
    setProviderSettingsStatus(
      "Provider settings are still loading. Refresh settings before saving.",
      true
    );
    return;
  }
  setProviderSettingsStatus("Saving provider settings...");

  try {
    const body = {
      provider: providerSettingsProvider.value,
      real_provider_enabled: providerRealEnabled.checked,
      llm_chat_enabled: providerLlmChatEnabled.checked,
      fallback_to_mock: providerFallbackToMock.checked,
    };
    const modelValue = providerSettingsModel.value.trim();
    if (modelValue) {
      body.model = modelValue;
    }

    const res = await fetch(`${BACKEND_URL}/provider/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const settings = await parseJsonResponse(res);
    renderProviderSettings(settings);
    setProviderSettingsStatus("Provider settings saved.");
  } catch (err) {
    setProviderSettingsStatus(formatBackendError(err), true);
  }
}

// ---------------------------------------------------------------------------
// TASK-261/263: Owner Voice Gate settings UI + backend storage/file enrollment.
// Safety: no microphone access, no recording, no localStorage voiceprint, no
// STT request, no /chat request, no Pet Window call, no Output Queue call.
// ---------------------------------------------------------------------------

function setOwnerVoiceGateSettingsStatus(message, isError = false) {
  if (!ownerVoiceGateSettingsStatus) return;
  ownerVoiceGateSettingsStatus.textContent = message;
  ownerVoiceGateSettingsStatus.className = isError
    ? "owner-voice-gate-settings-status error"
    : "owner-voice-gate-settings-status";
}

function _ownerVoiceThresholdValue() {
  const rawValue = ownerVoiceGateThreshold ? parseFloat(ownerVoiceGateThreshold.value) : 0.65;
  if (Number.isNaN(rawValue)) return 0.65;
  return Math.max(0.40, Math.min(0.95, rawValue));
}

function _ownerVoiceEnrollmentPaths() {
  if (!ownerVoiceGateEnrollPaths) return [];
  return ownerVoiceGateEnrollPaths.value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function _ownerVoiceManualMicThreshold() {
  const value = currentOwnerVoiceGateSettings && currentOwnerVoiceGateSettings.threshold;
  const parsed = parseFloat(value);
  if (Number.isNaN(parsed)) return 0.65;
  return Math.max(0.40, Math.min(0.95, parsed));
}

function _ownerVoiceManualMicDryRunEnabled() {
  return OWNER_VOICE_MANUAL_MIC_DRY_RUN_ENABLED === true &&
    currentOwnerVoiceGateSettings &&
    currentOwnerVoiceGateSettings.enrolled === true &&
    currentOwnerVoiceGateSettings.enabled === true;
}

function _ownerVoiceConversationModeDryRunEnabled() {
  return OWNER_VOICE_CONVERSATION_MODE_DRY_RUN_ENABLED === true &&
    currentOwnerVoiceGateSettings &&
    currentOwnerVoiceGateSettings.enrolled === true &&
    currentOwnerVoiceGateSettings.enabled === true;
}

function _ownerVoiceDryRunSourceForRecordingMode(mode) {
  if (mode === "conversation") return "conversation_mode";
  if (mode === "manual_mic" || mode === "manual_auto_send") return "manual_mic";
  return "none";
}

function _setOwnerVoiceManualMicDryRunStatus(status, reason, patch = {}) {
  fullAppVoiceDiagnostics.ownerVoiceDryRunEnabled = _ownerVoiceManualMicDryRunEnabled();
  fullAppVoiceDiagnostics.ownerVoiceDryRunSource = "manual_mic";
  fullAppVoiceDiagnostics.ownerVoiceDryRunStatus = status || "unknown";
  fullAppVoiceDiagnostics.ownerVoiceDryRunReason = reason || "unknown";
  fullAppVoiceDiagnostics.ownerVoiceThreshold = _ownerVoiceManualMicThreshold();
  fullAppVoiceDiagnostics.ownerVoiceCheckedAt = new Date().toISOString();
  fullAppVoiceDiagnostics.ownerVoiceScore = Object.prototype.hasOwnProperty.call(patch, "ownerVoiceScore")
    ? patch.ownerVoiceScore
    : null;
  fullAppVoiceDiagnostics.ownerVoiceAccepted = Object.prototype.hasOwnProperty.call(patch, "ownerVoiceAccepted")
    ? patch.ownerVoiceAccepted
    : null;
  fullAppVoiceDiagnostics.rawAudioPersisted = false;
  fullAppVoiceDiagnostics.candidateEmbeddingPersisted = false;
  fullAppVoiceDiagnostics.storedCentroidExposed = false;
  fullAppVoiceDiagnostics.runtimeHardBlocked = false;
  renderFullAppVoiceDiagnostics();
}

function _setOwnerVoiceConversationModeDryRunStatus(status, reason, patch = {}) {
  fullAppVoiceDiagnostics.ownerVoiceDryRunEnabled = _ownerVoiceConversationModeDryRunEnabled();
  fullAppVoiceDiagnostics.ownerVoiceDryRunSource = "conversation_mode";
  fullAppVoiceDiagnostics.ownerVoiceDryRunStatus = status || "unknown";
  fullAppVoiceDiagnostics.ownerVoiceDryRunReason = reason || "unknown";
  fullAppVoiceDiagnostics.ownerVoiceThreshold = _ownerVoiceManualMicThreshold();
  fullAppVoiceDiagnostics.ownerVoiceCheckedAt = new Date().toISOString();
  fullAppVoiceDiagnostics.ownerVoiceScore = Object.prototype.hasOwnProperty.call(patch, "ownerVoiceScore")
    ? patch.ownerVoiceScore
    : null;
  fullAppVoiceDiagnostics.ownerVoiceAccepted = Object.prototype.hasOwnProperty.call(patch, "ownerVoiceAccepted")
    ? patch.ownerVoiceAccepted
    : null;
  fullAppVoiceDiagnostics.rawAudioPersisted = false;
  fullAppVoiceDiagnostics.candidateEmbeddingPersisted = false;
  fullAppVoiceDiagnostics.storedCentroidExposed = false;
  fullAppVoiceDiagnostics.runtimeHardBlocked = false;
  renderFullAppVoiceDiagnostics();
}

function _syncOwnerVoiceManualMicDryRunFromSettings() {
  const enabled = _ownerVoiceManualMicDryRunEnabled();
  fullAppVoiceDiagnostics.ownerVoiceDryRunEnabled = enabled;
  fullAppVoiceDiagnostics.ownerVoiceThreshold = _ownerVoiceManualMicThreshold();
  if (!enabled) {
    const reason = currentOwnerVoiceGateSettings && currentOwnerVoiceGateSettings.enrolled === true
      ? "owner_voice_gate_disabled"
      : "not_enrolled";
    _setOwnerVoiceManualMicDryRunStatus("disabled", reason);
  }
}

async function runOwnerVoiceConversationModeDryRun(audioBlob) {
  // _setOwnerVoiceConversationModeDryRunStatus() always forces runtimeHardBlocked=false.
  const enabled = _ownerVoiceConversationModeDryRunEnabled();
  if (!enabled) {
    const reason = currentOwnerVoiceGateSettings && currentOwnerVoiceGateSettings.enrolled === true
      ? "owner_voice_gate_disabled"
      : "not_enrolled";
    _setOwnerVoiceConversationModeDryRunStatus("disabled", reason);
    return { status: "disabled", reason };
  }

  if (!audioBlob || !fullAppOwnerVoiceConversationDryRunCandidatePath) {
    _setOwnerVoiceConversationModeDryRunStatus("not_computed", "no_candidate_file_policy");
    return { status: "not_computed", reason: "no_candidate_file_policy" };
  }

  _setOwnerVoiceConversationModeDryRunStatus("checking", "verify_files_pending");
  try {
    const res = await fetch(`${BACKEND_URL}/owner-voice-gate/verify-files`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        paths: [fullAppOwnerVoiceConversationDryRunCandidatePath],
        threshold: _ownerVoiceManualMicThreshold(),
      }),
    });
    const result = await parseJsonResponse(res);
    const score = typeof result.score === "number" ? result.score : null;
    const accepted = typeof result.accepted === "boolean" ? result.accepted : null;
    _setOwnerVoiceConversationModeDryRunStatus(result.status || "ok", result.reason || "verification_complete", {
      ownerVoiceScore: score,
      ownerVoiceAccepted: accepted,
    });
    return result;
  } catch (_err) {
    _setOwnerVoiceConversationModeDryRunStatus("error", "verify_files_error");
    return { status: "error", reason: "verify_files_error" };
  }
}

async function runOwnerVoiceManualMicDryRun(audioBlob) {
  // _setOwnerVoiceManualMicDryRunStatus() always forces runtimeHardBlocked=false.
  const enabled = _ownerVoiceManualMicDryRunEnabled();
  if (!enabled) {
    const reason = currentOwnerVoiceGateSettings && currentOwnerVoiceGateSettings.enrolled === true
      ? "owner_voice_gate_disabled"
      : "not_enrolled";
    _setOwnerVoiceManualMicDryRunStatus("disabled", reason);
    return { status: "disabled", reason };
  }

  if (!audioBlob || !fullAppOwnerVoiceDryRunCandidatePath) {
    _setOwnerVoiceManualMicDryRunStatus("not_computed", "no_candidate_file_policy");
    return { status: "not_computed", reason: "no_candidate_file_policy" };
  }

  _setOwnerVoiceManualMicDryRunStatus("checking", "verify_files_pending");
  try {
    const res = await fetch(`${BACKEND_URL}/owner-voice-gate/verify-files`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        paths: [fullAppOwnerVoiceDryRunCandidatePath],
        threshold: _ownerVoiceManualMicThreshold(),
      }),
    });
    const result = await parseJsonResponse(res);
    const score = typeof result.score === "number" ? result.score : null;
    const accepted = typeof result.accepted === "boolean" ? result.accepted : null;
    _setOwnerVoiceManualMicDryRunStatus(result.status || "ok", result.reason || "verification_complete", {
      ownerVoiceScore: score,
      ownerVoiceAccepted: accepted,
    });
    return result;
  } catch (_err) {
    _setOwnerVoiceManualMicDryRunStatus("error", "verify_files_error");
    return { status: "error", reason: "verify_files_error" };
  }
}

function renderOwnerVoiceGateStatus(settings) {
  if (!settings) return;
  currentOwnerVoiceGateSettings = { ...settings };
  const status = settings.status || (settings.enrolled ? "disabled" : "not_enrolled");
  if (ownerVoiceGateState) ownerVoiceGateState.textContent = status;
  if (ownerVoiceGateProvider) ownerVoiceGateProvider.textContent = settings.provider || "funasr-campp";
  if (ownerVoiceGateModel) {
    ownerVoiceGateModel.textContent =
      settings.modelId || "iic/speech_campplus_sv_zh-cn_16k-common";
  }
  if (ownerVoiceGateEmbeddingDim) {
    ownerVoiceGateEmbeddingDim.textContent = String(settings.embeddingDim || 192);
  }
  if (ownerVoiceGateSampleCount) {
    ownerVoiceGateSampleCount.textContent = String(settings.sampleCount || 0);
  }
  if (ownerVoiceGateLastScore) {
    const stats = settings.calibrationStats || {};
    const score = stats.meanSelfScore ?? stats.ownerScore;
    ownerVoiceGateLastScore.textContent =
      score === null || score === undefined ? "none" : String(score);
  }
  if (ownerVoiceGateStorageOwner) {
    ownerVoiceGateStorageOwner.textContent = settings.storageOwner || "backend";
  }
  if (ownerVoiceGateSafetyAccepted) {
    ownerVoiceGateSafetyAccepted.checked = Boolean(settings.safetyNoticeAccepted);
  }
  if (ownerVoiceGateEnabledToggle) {
    ownerVoiceGateEnabledToggle.checked = Boolean(settings.enabled);
    ownerVoiceGateEnabledToggle.disabled = false;
  }
  if (ownerVoiceGateThreshold) {
    ownerVoiceGateThreshold.value = String(settings.threshold ?? 0.65);
  }
  if (ownerVoiceGateReenrollBtn) {
    ownerVoiceGateReenrollBtn.disabled = false;
  }
  if (ownerVoiceGateStatusSummary) {
    const enrolledText = settings.enrolled ? "Enrolled" : "Not enrolled";
    const enabledText = settings.enabled ? "Enabled" : "Disabled";
    ownerVoiceGateStatusSummary.textContent = `Owner Voice Gate: ${enrolledText} / ${enabledText}`;
    ownerVoiceGateStatusSummary.className = settings.enabled
      ? "owner-voice-gate-status-summary active"
      : "owner-voice-gate-status-summary warning";
  }
  _syncOwnerVoiceManualMicDryRunFromSettings();
}

async function enrollOwnerVoiceGateFromFiles() {
  if (!ownerVoiceGateSafetyAccepted || !ownerVoiceGateSafetyAccepted.checked) {
    setOwnerVoiceGateSettingsStatus("Accept the safety notice before enrollment.", true);
    return null;
  }
  const paths = _ownerVoiceEnrollmentPaths();
  if (paths.length < 2) {
    setOwnerVoiceGateSettingsStatus("Provide at least two owner WAV file paths.", true);
    return null;
  }
  setOwnerVoiceGateSettingsStatus("Enrolling owner voice from local WAV file paths...");
  try {
    const res = await fetch(`${BACKEND_URL}/owner-voice-gate/enroll-files`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        paths,
        threshold: _ownerVoiceThresholdValue(),
        safetyNoticeAccepted: ownerVoiceGateSafetyAccepted.checked,
      }),
    });
    const settings = await parseJsonResponse(res);
    renderOwnerVoiceGateStatus(settings);
    if (settings.enrolled) {
      setOwnerVoiceGateSettingsStatus(
        `Owner voice enrolled from ${settings.sampleCount || paths.length} WAV samples. Gate remains disabled until explicitly enabled.`
      );
    } else {
      setOwnerVoiceGateSettingsStatus(settings.message || "Owner voice enrollment did not complete.", true);
    }
    return settings;
  } catch (err) {
    setOwnerVoiceGateSettingsStatus(formatBackendError(err), true);
    return null;
  }
}

async function loadOwnerVoiceGateStatus() {
  setOwnerVoiceGateSettingsStatus("Loading owner voice gate status...");
  try {
    const res = await fetch(`${BACKEND_URL}/owner-voice-gate/status`);
    const settings = await parseJsonResponse(res);
    renderOwnerVoiceGateStatus(settings);
    setOwnerVoiceGateSettingsStatus("Owner voice gate status loaded.");
    return settings;
  } catch (err) {
    setOwnerVoiceGateSettingsStatus(formatBackendError(err), true);
    return null;
  }
}

async function saveOwnerVoiceGateSettings(update) {
  setOwnerVoiceGateSettingsStatus("Saving owner voice gate settings...");
  try {
    const res = await fetch(`${BACKEND_URL}/owner-voice-gate/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(update),
    });
    const settings = await parseJsonResponse(res);
    renderOwnerVoiceGateStatus(settings);
    if (settings.reason === "not_enrolled") {
      setOwnerVoiceGateSettingsStatus(
        "Owner Voice Gate is not enrolled yet. Enable remains disabled.",
        true
      );
    } else {
      setOwnerVoiceGateSettingsStatus("Owner voice gate settings saved.");
    }
    return settings;
  } catch (err) {
    setOwnerVoiceGateSettingsStatus(formatBackendError(err), true);
    return null;
  }
}

async function deleteOwnerVoiceGateVoiceprint() {
  setOwnerVoiceGateSettingsStatus("Deleting owner voice gate placeholder...");
  try {
    const res = await fetch(`${BACKEND_URL}/owner-voice-gate/delete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    const settings = await parseJsonResponse(res);
    renderOwnerVoiceGateStatus(settings);
    setOwnerVoiceGateSettingsStatus("Owner voice gate reset to defaults.");
    return settings;
  } catch (err) {
    setOwnerVoiceGateSettingsStatus(formatBackendError(err), true);
    return null;
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
    testProviderConnectionBtn.title = "Enable 'Use real AI' in Provider Settings before testing.";
  } else if (isLocalProvider && isTestingConnection) {
    testProviderConnectionBtn.title = "Test in progress...";
  } else if (isLocalProvider) {
    testProviderConnectionBtn.title =
      "Sends one minimal request to your local Ollama server. No data leaves your device.";
  } else if (!keyExists) {
    testProviderConnectionBtn.title = "Save an API key before testing.";
  } else if (!realProviderEnabled) {
    testProviderConnectionBtn.title = "Enable 'Use real AI' in Provider Settings before testing.";
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
    setProviderTestMsg("Enable 'Use real AI' in Provider Settings before testing.", true);
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
async function submitEditedUserMessage(text) {
  if (isSending || !editingMessageState) return false;
  const editedText = (text || "").trim();
  if (!editedText) return false;

  const editState = { ...editingMessageState };
  const entries = collectUndoableChatEntries();
  const target = entries[editState.index];
  if (!target || target.role !== "user" ||
      !isEditableUserEntryAtIndex(entries, editState.index)) {
    setClearChatStatus("編輯訊息失敗", 2000);
    return false;
  }

  const editedEntry = {
    ...target,
    text: editedText,
    source: editState.source || target.source || "unknown",
    ts: Date.now(),
  };
  const entriesWithoutOldReply = entries.map((entry, idx) =>
    idx === editState.index ? editedEntry : { ...entry }
  );
  if (entriesWithoutOldReply[editState.index + 1] &&
      entriesWithoutOldReply[editState.index + 1].role === "pet") {
    entriesWithoutOldReply.splice(editState.index + 1, 1);
  }

  setSending(true);
  try {
    const rewritten = await rewritePersistedChatHistory(entriesWithoutOldReply);
    if (!rewritten) throw new Error("history unavailable");
    clearEditingMessageState({ restoreInput: false, clearStatus: true });
    if (chatSearchInput) chatSearchInput.value = "";
    renderFormalChatEntries(entriesWithoutOldReply);
    const loadingMessage = appendMessage(
      "status",
      isOllamaChatPath()
        ? "本地 AI 喚醒中，第一次回覆可能需要較久..."
        : "等待後端回覆中...",
      { autoScroll: true }
    );
    setChatRuntimeStatus("pending", sourceStatusMessage("pending"), "pending");
    setPetExpression("pending");
    setPetHint("thinking…");
    updatePetThinkingState();
    setComposerValue("");

    try {
      const useMemory = useMemoryToggle ? useMemoryToggle.checked : false;
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: editedText, use_memory: useMemory }),
      });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        const detail = data && data.detail ? data.detail : "";
        throw new Error(safeChatErrorMessage(res.status, detail));
      }

      const replyEntry = {
        role: "pet",
        text: data.reply,
        source: "full_app",
        ts: Date.now(),
      };
      const finalEntries = [
        ...entriesWithoutOldReply.slice(0, editState.index + 1),
        replyEntry,
        ...entriesWithoutOldReply.slice(editState.index + 1),
      ];
      const finalRewrite = await rewritePersistedChatHistory(finalEntries);
      if (!finalRewrite) throw new Error("history unavailable");
      loadingMessage.remove();
      renderFormalChatEntries(finalEntries);
      enqueueChatReplyOutputDiagnostics({ reply: data.reply, mood: data.mood, source: data.source }); // TASK-232
      renderInteractionReactionPreview();
      if (document.hidden) markUnread();
      maybeScrollChatToBottom();

      const source = data.source || "unknown";
      const isSourceError = source === "llm_local_error" || source === "llm_real_error";
      updatePetSpeechFromChatResponse({
        reply: data.reply,
        mood: data.mood,
        source,
      });
      setMood(data.mood);
      if (isSourceError) {
        setPetExpression("error");
        setPetHint(moodHintLabel("error"));
      }
      setChatRuntimeStatus(
        source,
        sourceStatusMessage(source),
        isSourceError ? "error" : "normal"
      );
      await loadProviderSettings();
      recordInteractionEvent("message_edited", { source: editState.source || "full_app", role: "user", messageLength: editedText.length });
      return true;
    } catch (err) {
      const isNetworkError = isFetchNetworkError(err);
      const errText = isNetworkError
        ? `Cannot reach backend at ${BACKEND_URL}.\nMake sure the backend is running:\n  cd backend && uvicorn app.main:app --reload`
        : `Something went wrong: ${err.message}`;
      loadingMessage.remove();
      if (isNetworkError) {
        setPetExpression("offline");
        setPetHint(moodHintLabel("offline"));
      } else {
        setPetExpression("error");
        setPetHint(moodHintLabel("error"));
      }
      setChatRuntimeStatus(
        isNetworkError ? "backend_offline" : "error",
        isNetworkError ? sourceStatusMessage("backend_offline") : err.message,
        "error"
      );
      updatePetSpeechFromChatResponse({ reply: "", mood: "worried", source: "llm_local_error" });
      appendMessage("error", errText);
      maybeScrollChatToBottom();
      return false;
    }
  } catch (_e) {
    setClearChatStatus("編輯訊息失敗", 2000);
    return false;
  } finally {
    setSending(false);
    if (msgInput && typeof msgInput.focus === "function") msgInput.focus();
  }
}

async function sendMessage(text) {
  if (editingMessageState) {
    await submitEditedUserMessage(text);
    return;
  }
  if (isSending || !text.trim()) return;
  setSending(true);

  // Show user message immediately — always scroll so the user sees their own send.
  appendMessage("user", text, { autoScroll: true, source: "full_app", ts: Date.now() });
  recordInteractionEvent("chat_message_sent", { source: "full_app", role: "user", messageLength: text.length });
  const loadingMessage = appendMessage(
    "status",
    isOllamaChatPath()
      ? "本地 AI 喚醒中，第一次回覆可能需要較久..."
      : "等待後端回覆中...",
    { autoScroll: true }
  );
  setChatRuntimeStatus("pending", sourceStatusMessage("pending"), "pending");
  // TASK-083: show thinking expression while waiting for reply
  setPetExpression("pending");
  setPetHint("thinking…");
  updatePetThinkingState(); // TASK-157: mirror thinking state to Pet Window
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
    appendMessage("pet", data.reply, { source: "full_app", ts: Date.now() });
    enqueueChatReplyOutputDiagnostics({ reply: data.reply, mood: data.mood, source: data.source }); // TASK-232
    renderInteractionReactionPreview();
    maybeScrollChatToBottom(); // TASK-113: only scroll if user was near the bottom
    const source = data.source || "unknown";
    const isSourceError = source === "llm_local_error" || source === "llm_real_error";
    updatePetSpeechFromChatResponse({
      reply: data.reply,
      mood: data.mood,
      source,
    });
    setMood(data.mood); // also calls setPetExpression via setMood
    // TASK-083/098: if the source indicates a provider error, override expression to error
    // even though a safe fallback reply was returned.
    if (isSourceError) {
      setPetExpression("error");
      setPetHint(moodHintLabel("error"));
    }
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
    // TASK-083: show offline/error expression on failure
    if (isNetworkError) {
      setPetExpression("offline");
      setPetHint(moodHintLabel("offline"));
    } else {
      setPetExpression("error");
      setPetHint(moodHintLabel("error"));
    }
    setChatRuntimeStatus(
      isNetworkError ? "backend_offline" : "error",
      isNetworkError ? sourceStatusMessage("backend_offline") : err.message,
      "error"
    );
    // TASK-157: replace thinking bubble with clean error state in Pet Window
    updatePetSpeechFromChatResponse({ reply: "", mood: "worried", source: "llm_local_error" });
    appendMessage("error", errText);
    maybeScrollChatToBottom(); // TASK-113: scroll to error only if user was near bottom
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

if (showPetWindowBtn) {
  showPetWindowBtn.addEventListener("click", () => {
    showPetWindowFromFullApp();
  });
}

// TASK-171A: capture button click is the ONLY trigger.
if (captureScreenBtn) {
  captureScreenBtn.addEventListener("click", () => {
    captureScreenFromFullApp();
  });
}

// TASK-176: window capture button click is the ONLY trigger.
if (captureWindowBtn) {
  captureWindowBtn.addEventListener("click", () => {
    captureWindowFromFullApp();
  });
}

// TASK-172A: analyze button — only fires after screenshot exists + user confirms.
if (analyzeScreenBtn) {
  analyzeScreenBtn.addEventListener("click", () => {
    analyzeScreenFromFullApp();
  });
}

// TASK-172A: clear button — resets screenshot + summary, disables analyze.
if (clearScreenBtn) {
  clearScreenBtn.addEventListener("click", () => {
    clearScreenshot();
  });
}

// TASK-172B: ask button — sends OCR summary to chat after privacy confirmation.
if (askScreenBtn) {
  askScreenBtn.addEventListener("click", () => {
    askScreenFromFullApp();
  });
}

// TASK-194: clear chat history and reset chat DOM.
if (clearChatBtn) {
  clearChatBtn.addEventListener("click", () => {
    handleClearChatClick();
  });
}

// TASK-196: copy all user/pet messages to clipboard.
if (copyChatBtn) {
  copyChatBtn.addEventListener("click", () => {
    copyAllChat();
  });
}

// TASK-205: export conversation to file via Save Dialog.
if (exportChatBtn) {
  exportChatBtn.addEventListener("click", () => {
    exportChatToFile();
  });
}
if (interactionDiagnosticsToggle) {
  interactionDiagnosticsToggle.addEventListener("click", () => {
    toggleInteractionDiagnosticsDrawer();
  });
}

// TASK-198: chat search / filter wiring.
if (chatSearchInput) {
  chatSearchInput.addEventListener("input", () => {
    filterChatMessages(chatSearchInput.value);
  });
}
if (chatSearchClearBtn) {
  chatSearchClearBtn.addEventListener("click", () => {
    if (chatSearchInput) chatSearchInput.value = "";
    filterChatMessages("");
  });
}

// TASK-199: keyboard shortcuts — Ctrl+F / Cmd+F focuses chat search; Esc clears or blurs.
document.addEventListener("keydown", function (e) {
  if (e.key === "Escape" && chatContextMenu) {
    closeChatContextMenu();
    return;
  }
  if ((e.ctrlKey || e.metaKey) && e.key === "f") {
    e.preventDefault();
    if (chatSearchInput) {
      chatSearchInput.focus();
      chatSearchInput.select();
    }
  }
});
if (chatSearchInput) {
  chatSearchInput.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      if (chatSearchInput.value) {
        chatSearchInput.value = "";
        filterChatMessages("");
      } else {
        chatSearchInput.blur();
      }
    } else if (e.key === "Enter" && (chatSearchInput.value || "").trim()) {
      // TASK-201: Enter = next result, Shift+Enter = previous result.
      e.preventDefault();
      navigateToSearchResult(e.shiftKey ? -1 : 1);
    }
  });
}

// TASK-202: auto-hide jump button when user scrolls near bottom.
if (chatArea) {
  chatArea.addEventListener("scroll", () => {
    closeChatContextMenu();
    if (isChatNearBottom()) hideNewMessageBtn();
  });
}
document.addEventListener("pointerdown", (e) => {
  if (chatContextMenu && !isInsideChatContextMenu(e.target)) {
    closeChatContextMenu();
  }
});
// TASK-202: jump button click — scroll to bottom and dismiss badge.
if (chatNewMsgBtn) {
  chatNewMsgBtn.addEventListener("click", () => {
    scrollChatToBottom();
    hideNewMessageBtn();
  });
}

// ---------------------------------------------------------------------------
// TASK-241: Full App Voice Input
// Toggle-to-record mic button. Transcript fills #message-input for user review.
// No auto-send. No Pet Window calls. No audio persistence. No new IPC channels.
// ---------------------------------------------------------------------------

function setFullAppVoiceState(state) {
  // state: "idle" | "recording" | "transcribing"
  var isIdle         = state === "idle";
  var isRecording    = state === "recording";
  var isTranscribing = state === "transcribing";

  fullAppRecording    = isRecording;
  fullAppTranscribing = isTranscribing;

  if (voiceInputBtn) {
    if (isIdle) {
      delete voiceInputBtn.dataset.state;
      voiceInputBtn.disabled = false;
    } else {
      voiceInputBtn.dataset.state = state;
      voiceInputBtn.disabled = isTranscribing;
    }
  }

  if (voiceInputStatus) {
    if (isRecording) {
      voiceInputStatus.textContent = "錄音中… 再按停止";
      voiceInputStatus.dataset.state = "recording";
      voiceInputStatus.hidden = false;
    } else if (isTranscribing) {
      voiceInputStatus.textContent = "辨識中…";
      voiceInputStatus.dataset.state = "transcribing";
      voiceInputStatus.hidden = false;
    } else {
      voiceInputStatus.textContent = "";
      delete voiceInputStatus.dataset.state;
      voiceInputStatus.hidden = true;
    }
  }
}

async function transcribeFullAppAudioBlob(blob) {
  var api = (typeof window !== "undefined" && window !== null) ? window.dragonPet : null;
  if (!api || typeof api.transcribeAudio !== "function") {
    return null; // IPC bridge not wired — silent no-op
  }

  var arrayBuffer;
  try {
    arrayBuffer = await blob.arrayBuffer();
  } catch (_e) {
    throw new Error("stt_error");
  }

  var timeoutId;
  var timeoutPromise = new Promise(function (_, reject) {
    timeoutId = setTimeout(function () {
      reject(new Error("stt_timeout"));
    }, FULL_APP_STT_TIMEOUT_MS);
  });

  var result;
  try {
    result = await Promise.race([api.transcribeAudio(arrayBuffer), timeoutPromise]);
  } catch (err) {
    clearTimeout(timeoutId);
    if (err && (err.message === "stt_timeout" || err.message === "stt_offline")) throw err;
    throw new Error("stt_error");
  }
  clearTimeout(timeoutId);

  // TASK-245/246: update STT language-lock and model quality diagnostics from backend metadata.
  // Done before status checks so the fields are populated even for error/empty
  // responses — the caller's renderFullAppVoiceDiagnostics() will pick them up.
  if (result && typeof result === "object") {
    fullAppVoiceDiagnostics.sttLanguage          = result.language         ? String(result.language)         : "unknown";
    fullAppVoiceDiagnostics.languageLocked        = Boolean(result.languageLocked);
    fullAppVoiceDiagnostics.sttTask               = result.task             ? String(result.task)             : "unknown";
    fullAppVoiceDiagnostics.sttProvider           = result.provider         ? String(result.provider)         : "unknown";
    fullAppVoiceDiagnostics.sttModel              = result.model             ? String(result.model)             : "unknown";
    fullAppVoiceDiagnostics.detectedLanguage       = result.detectedLanguage  ? String(result.detectedLanguage)  : "none";
    fullAppVoiceDiagnostics.sttRequestedModel      = result.requestedModel    ? String(result.requestedModel)    : "unknown";
    fullAppVoiceDiagnostics.sttResolvedModel       = result.resolvedModel     ? String(result.resolvedModel)     : "unknown";
    fullAppVoiceDiagnostics.sttModelSource         = result.modelSource       ? String(result.modelSource)       : "unknown";
    fullAppVoiceDiagnostics.sttModelLoadStatus     = result.modelLoadStatus   ? String(result.modelLoadStatus)   : "unknown";
    fullAppVoiceDiagnostics.sttModelLoadError      = result.modelLoadError    ? String(result.modelLoadError)    : "none";
    // TASK-247: correction diagnostics — raw/corrected preview, max 30 chars, textContent only
    fullAppVoiceDiagnostics.sttRawTranscriptPreview      = result.rawTranscript      ? makeSafeTranscriptPreview(String(result.rawTranscript))      : "";
    fullAppVoiceDiagnostics.sttCorrectedTranscriptPreview = result.correctedTranscript ? makeSafeTranscriptPreview(String(result.correctedTranscript)) : "";
    fullAppVoiceDiagnostics.sttCorrectionApplied         = Boolean(result.correctionApplied);
    fullAppVoiceDiagnostics.sttCorrectionMode            = result.correctionMode  ? String(result.correctionMode)  : "";
    fullAppVoiceDiagnostics.sttCorrectionReason          = result.correctionReason ? String(result.correctionReason) : "";
    // TASK-248: matched alias / canonical term diagnostics
    fullAppVoiceDiagnostics.sttMatchedAlias  = result.matchedAlias  ? String(result.matchedAlias)  : "";
    fullAppVoiceDiagnostics.sttCanonicalTerm = result.canonicalTerm ? String(result.canonicalTerm) : "";
    // TASK-249: provider selection diagnostics
    fullAppVoiceDiagnostics.sttProviderRequested    = result.sttProviderRequested    ? String(result.sttProviderRequested)    : "unknown";
    fullAppVoiceDiagnostics.sttProviderResolved     = result.sttProviderResolved     ? String(result.sttProviderResolved)     : "unknown";
    fullAppVoiceDiagnostics.sttProviderSource       = result.sttProviderSource       ? String(result.sttProviderSource)       : "unknown";
    fullAppVoiceDiagnostics.sttProviderLoadStatus   = result.sttProviderLoadStatus   ? String(result.sttProviderLoadStatus)   : "unknown";
    fullAppVoiceDiagnostics.sttProviderLoadError    = result.sttProviderLoadError    ? String(result.sttProviderLoadError)    : "none";
    fullAppVoiceDiagnostics.sttProviderFallbackReason = result.sttProviderFallbackReason ? String(result.sttProviderFallbackReason) : "none";
  }

  if (!result || typeof result !== "object") throw new Error("stt_error");
  var status = result.status || "error";
  if (status === "unavailable") throw new Error("stt_unavailable");
  if (status === "offline")     throw new Error("stt_offline");
  if (status === "error")       throw new Error("stt_error");
  if (status === "empty" || !result.transcript) return "";
  return String(result.transcript);
}

function _fullAppSttTranscribeChunks(chunks, mimeType) {
  var audioBlob;
  try {
    audioBlob = new Blob(chunks || [], { type: mimeType || "audio/webm" });
  } catch (_e) {
    setFullAppVoiceState("idle");
    return;
  }

  // TASK-244: update diagnostics with blob/recording metadata
  try { fullAppVoiceDiagnostics.blobSizeBytes = audioBlob.size || 0; } catch (_e) {}
  fullAppVoiceDiagnostics.mimeType = mimeType || "";
  fullAppVoiceDiagnostics.chunksCount = (chunks || []).length;
  var _sttEndedAt = Date.now();
  fullAppVoiceDiagnostics.recordingEndedAt = _sttEndedAt;
  fullAppVoiceDiagnostics.durationMs = _sttEndedAt - (fullAppVoiceDiagnostics.recordingStartedAt || _sttEndedAt);
  // TASK-244b: pipeline diagnostics — selectedMimeType, bytesPerSecond, in-memory preview blob
  fullAppVoiceDiagnostics.selectedMimeType = mimeType || "";
  if (audioBlob && audioBlob.size > 0) {
    fullAppLastAudioBlob = audioBlob;
    fullAppVoiceDiagnostics.lastAudioPreviewAvailable = true;
    if (fullAppVoiceDiagnostics.durationMs > 0) {
      fullAppVoiceDiagnostics.bytesPerSecond = Math.round(audioBlob.size / (fullAppVoiceDiagnostics.durationMs / 1000));
    }
    if (voicePreviewPlayBtn) voicePreviewPlayBtn.disabled = false;
  }
  renderFullAppVoiceDiagnostics();

  // TASK-266: status-only Owner Voice Gate dry-run for Manual Mic.
  // Fire-and-forget: accept/reject/error must not block STT, textarea fill, or auto-send.
  runOwnerVoiceManualMicDryRun(audioBlob);

  transcribeFullAppAudioBlob(audioBlob).then(function (transcript) {
    setFullAppVoiceState("idle");

    if (transcript === null) {
      return; // IPC bridge not available — silent no-op
    }

    if (!transcript) {
      // TASK-244: empty transcript diagnostics
      fullAppVoiceDiagnostics.emptyTranscript = true;
      fullAppVoiceDiagnostics.sttStatus = "empty";
      renderFullAppVoiceDiagnostics();
      _recordVoiceDiagnosticsHistory();
      var emptyMsg = "未偵測到語音，請重試。";
      if (voiceInputStatus) {
        voiceInputStatus.textContent = emptyMsg;
        voiceInputStatus.hidden = false;
        setTimeout(function () {
          if (voiceInputStatus.textContent === emptyMsg) {
            voiceInputStatus.textContent = "";
            voiceInputStatus.hidden = true;
          }
        }, 3000);
      }
      return;
    }

    var trimmed = transcript.trim();
    if (trimmed.length > FULL_APP_VOICE_CHAT_MAX_CHARS) {
      var longMsg = "語音太長，請縮短後再試。";
      if (voiceInputStatus) {
        voiceInputStatus.textContent = longMsg;
        voiceInputStatus.hidden = false;
        setTimeout(function () {
          if (voiceInputStatus.textContent === longMsg) {
            voiceInputStatus.textContent = "";
            voiceInputStatus.hidden = true;
          }
        }, 4000);
      }
      return;
    }

    // TASK-244: success transcript diagnostics
    fullAppVoiceDiagnostics.transcriptLength  = trimmed.length;
    fullAppVoiceDiagnostics.transcriptPreview = makeSafeTranscriptPreview(trimmed);
    fullAppVoiceDiagnostics.emptyTranscript   = false;
    fullAppVoiceDiagnostics.sttStatus         = "success";
    renderFullAppVoiceDiagnostics();
    _recordVoiceDiagnosticsHistory();

    // Fill textarea for user review
    if (msgInput) {
      msgInput.value = trimmed;
      msgInput.dispatchEvent(new Event("input"));
      msgInput.focus();
    }
    // TASK-242: auto-send if toggle enabled and not busy
    if (fullAppVoiceAutoSendEnabled && !isSending && !editingMessageState && typeof sendMessage === "function") {
      sendMessage(trimmed);
    }
  }).catch(function (err) {
    setFullAppVoiceState("idle");
    // TASK-244: error diagnostics
    var errCode = (err && err.message) ? err.message : "";
    fullAppVoiceDiagnostics.sttStatus = errCode === "stt_timeout" ? "timeout" : "error";
    renderFullAppVoiceDiagnostics();
    _recordVoiceDiagnosticsHistory();
    var errText;
    if (errCode === "stt_unavailable") {
      errText = "語音辨識服務不可用。";
    } else if (errCode === "stt_timeout") {
      errText = "語音辨識逾時，請再試一次。";
    } else if (errCode === "stt_offline") {
      errText = "語音辨識服務離線。";
    } else {
      errText = "語音辨識失敗，請再試一次。";
    }
    if (voiceInputStatus) {
      voiceInputStatus.textContent = errText;
      voiceInputStatus.hidden = false;
      setTimeout(function () {
        if (voiceInputStatus.textContent === errText) {
          voiceInputStatus.textContent = "";
          voiceInputStatus.hidden = true;
        }
      }, 4000);
    }
  });
}

// TASK-252: WAV PCM capture helpers — encode Float32Array chunks as 16-bit mono WAV blob
function _encodeWavPcm(pcmChunks, sampleRate) {
  var numSamples = 0;
  for (var i = 0; i < pcmChunks.length; i++) numSamples += pcmChunks[i].length;
  var buffer = new ArrayBuffer(44 + numSamples * 2);
  var view   = new DataView(buffer);
  var writeStr = function (off, str) {
    for (var si = 0; si < str.length; si++) view.setUint8(off + si, str.charCodeAt(si));
  };
  writeStr(0, "RIFF");
  view.setUint32(4,  36 + numSamples * 2, true);
  writeStr(8,  "WAVE");
  writeStr(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1,  true);  // PCM
  view.setUint16(22, 1,  true);  // mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2,  true);
  view.setUint16(34, 16, true);
  writeStr(36, "data");
  view.setUint32(40, numSamples * 2, true);
  var offset = 44;
  for (var c = 0; c < pcmChunks.length; c++) {
    var chunk = pcmChunks[c];
    for (var s = 0; s < chunk.length; s++) {
      var sample = Math.max(-1, Math.min(1, chunk[s]));
      view.setInt16(offset, sample < 0 ? sample * 32768 : sample * 32767, true);
      offset += 2;
    }
  }
  return new Blob([buffer], { type: "audio/wav" });
}

function _startPcmCapture(stream) {
  try {
    _fullAppPcmChunks = [];
    var ctx = new AudioContext({ sampleRate: FULL_APP_STT_PCM_SAMPLE_RATE });
    _fullAppPcmCtx = ctx;
    _fullAppPcmSource = ctx.createMediaStreamSource(stream);
    _fullAppPcmProcessor = ctx.createScriptProcessor(FULL_APP_STT_PCM_BUFFER_SIZE, 1, 1);
    _fullAppPcmProcessor.onaudioprocess = function (ev) {
      _fullAppPcmChunks.push(new Float32Array(ev.inputBuffer.getChannelData(0)));
    };
    _fullAppPcmSource.connect(_fullAppPcmProcessor);
    _fullAppPcmProcessor.connect(ctx.destination);
  } catch (_e) { /* PCM capture unavailable — WAV encoding will produce silence */ }
}

function _stopPcmCapture() {
  try { if (_fullAppPcmProcessor) _fullAppPcmProcessor.disconnect(); } catch (_e) {}
  try { if (_fullAppPcmSource)    _fullAppPcmSource.disconnect();    } catch (_e) {}
  try { if (_fullAppPcmCtx && _fullAppPcmCtx.state !== "closed") _fullAppPcmCtx.close(); } catch (_e) {}
  _fullAppPcmProcessor = null;
  _fullAppPcmSource    = null;
  _fullAppPcmCtx       = null;
}

function _startConvPcmCapture(stream) {
  try {
    _convPcmChunks = [];
    var ctx = new AudioContext({ sampleRate: FULL_APP_STT_PCM_SAMPLE_RATE });
    _convPcmCtx = ctx;
    _convPcmSource = ctx.createMediaStreamSource(stream);
    _convPcmProcessor = ctx.createScriptProcessor(FULL_APP_STT_PCM_BUFFER_SIZE, 1, 1);
    _convPcmProcessor.onaudioprocess = function (ev) {
      _convPcmChunks.push(new Float32Array(ev.inputBuffer.getChannelData(0)));
    };
    _convPcmSource.connect(_convPcmProcessor);
    _convPcmProcessor.connect(ctx.destination);
  } catch (_e) { /* PCM capture unavailable */ }
}

function _stopConvPcmCapture() {
  try { if (_convPcmProcessor) _convPcmProcessor.disconnect(); } catch (_e) {}
  try { if (_convPcmSource)    _convPcmSource.disconnect();    } catch (_e) {}
  try { if (_convPcmCtx && _convPcmCtx.state !== "closed") _convPcmCtx.close(); } catch (_e) {}
  _convPcmProcessor = null;
  _convPcmSource    = null;
  _convPcmCtx       = null;
}

function stopFullAppVoiceInput() {
  var recorder = _fullAppRecorder;
  var mimeType = (recorder && recorder.mimeType) ? recorder.mimeType : "audio/webm";

  // TASK-244: record manual stop reason
  fullAppVoiceDiagnostics.stopReason = "manual_stop";

  if (_fullAppRecordingTimer !== null) {
    clearTimeout(_fullAppRecordingTimer);
    _fullAppRecordingTimer = null;
  }

  if (recorder && recorder.state !== "inactive") {
    recorder._stopAndTranscribe = true;
    setFullAppVoiceState("transcribing");
    try {
      recorder.stop();
    } catch (_e) {
      recorder._stopAndTranscribe = false;
      _fullAppRecorder = null;
      setFullAppVoiceState("idle");
    }
  } else {
    _stopPcmCapture();
    var savedWav = _encodeWavPcm(_fullAppPcmChunks, FULL_APP_STT_PCM_SAMPLE_RATE);
    _fullAppPcmChunks = [];
    setFullAppVoiceState("transcribing");
    _fullAppSttTranscribeChunks([savedWav], "audio/wav");
  }
}

function cancelFullAppVoiceInput() {
  var recorder = _fullAppRecorder;
  if (recorder && recorder.state !== "inactive") {
    try { recorder.stop(); } catch (_e) { /* ignore */ }
  }
  _stopPcmCapture();
  _fullAppPcmChunks = [];
  // Release microphone tracks
  if (_fullAppMicStream) {
    try {
      _fullAppMicStream.getTracks().forEach(function (t) { t.stop(); });
    } catch (_e) { /* ignore */ }
    _fullAppMicStream = null;
  }
  if (_fullAppRecordingTimer !== null) {
    clearTimeout(_fullAppRecordingTimer);
    _fullAppRecordingTimer = null;
  }
  _fullAppRecorder = null;
  _fullAppChunks = [];
  setFullAppVoiceState("idle");
}

async function openFullAppVoiceInput() {
  // Toggle: if already recording, stop and transcribe
  if (fullAppRecording) {
    stopFullAppVoiceInput();
    return;
  }

  // If transcribing, ignore new request
  if (fullAppTranscribing) {
    return;
  }

  // TASK-242: respect Voice Input Enabled toggle
  if (!fullAppVoiceInputEnabled) {
    return;
  }

  // Check MediaRecorder availability (not present in all environments)
  if (typeof MediaRecorder === "undefined") {
    if (voiceInputStatus) {
      voiceInputStatus.textContent = "此環境不支援語音輸入。";
      voiceInputStatus.hidden = false;
    }
    return;
  }

  // Request microphone access
  var stream;
  try {
    var navObj = typeof navigator !== "undefined" ? navigator : null;
    if (!navObj || !navObj.mediaDevices || typeof navObj.mediaDevices.getUserMedia !== "function") {
      throw new Error("no_mic");
    }
    stream = await navObj.mediaDevices.getUserMedia({ audio: FULL_APP_VOICE_AUDIO_CONSTRAINTS });
  } catch (err) {
    var errName    = err && err.name    ? err.name    : "";
    var errMsgStr  = err && err.message ? err.message : "";
    var statusText;
    if (errName === "NotAllowedError" || errName === "PermissionDeniedError") {
      statusText = "麥克風權限被拒絕。";
    } else if (errName === "NotFoundError" || errName === "DevicesNotFoundError" || errMsgStr === "no_mic") {
      statusText = "找不到麥克風裝置。";
    } else {
      statusText = "無法啟動語音輸入。";
    }
    if (voiceInputStatus) {
      voiceInputStatus.textContent = statusText;
      voiceInputStatus.hidden = false;
      setTimeout(function () {
        if (voiceInputStatus.textContent === statusText) {
          voiceInputStatus.textContent = "";
          voiceInputStatus.hidden = true;
        }
      }, 4000);
    }
    return;
  }

  // TASK-244b: capture audio track settings for diagnostics
  try {
    var _audioTrack = stream.getAudioTracks()[0];
    if (_audioTrack && typeof _audioTrack.getSettings === "function") {
      var _ts = _audioTrack.getSettings();
      fullAppVoiceDiagnostics.constraintsEchoCancellation = Boolean(_ts.echoCancellation);
      fullAppVoiceDiagnostics.constraintsNoiseSuppression = Boolean(_ts.noiseSuppression);
      fullAppVoiceDiagnostics.constraintsAutoGainControl  = Boolean(_ts.autoGainControl);
      renderFullAppVoiceDiagnostics();
    }
  } catch (_trackErr) {}

  // Build MediaRecorder — prefer webm/opus for Whisper compatibility
  var mimeType = selectVoiceMimeType();
  var recorder;
  try {
    recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
  } catch (_e) {
    try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (_e2) { /* ignore */ }
    if (voiceInputStatus) {
      voiceInputStatus.textContent = "此環境不支援語音輸入。";
      voiceInputStatus.hidden = false;
    }
    return;
  }

  _fullAppMicStream = stream;
  _fullAppRecorder  = recorder;
  _fullAppChunks    = [];
  recorder._stopAndTranscribe = false;

  recorder.addEventListener("dataavailable", function (event) {
    if (event.data && event.data.size > 0) {
      _fullAppChunks.push(event.data);
    }
  });

  recorder.addEventListener("stop", function () {
    try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (_e) { /* ignore */ }
    _fullAppMicStream = null;
    if (_fullAppRecorder && _fullAppRecorder._stopAndTranscribe) {
      _fullAppRecorder._stopAndTranscribe = false;
      // TASK-252: encode PCM chunks as WAV for FunASR compatibility
      _stopPcmCapture();
      var wavBlob = _encodeWavPcm(_fullAppPcmChunks, FULL_APP_STT_PCM_SAMPLE_RATE);
      _fullAppPcmChunks = [];
      _fullAppSttTranscribeChunks([wavBlob], "audio/wav");
    } else {
      _stopPcmCapture();
      _fullAppPcmChunks = [];
    }
  });

  setFullAppVoiceState("recording");
  // TASK-244: reset diagnostics for this manual recording
  resetFullAppVoiceDiagnosticsForRecording(fullAppVoiceAutoSendEnabled ? "manual_auto_send" : "manual_mic");

  // TASK-252: start PCM capture in parallel with MediaRecorder
  _startPcmCapture(stream);

  try {
    recorder.start();
  } catch (_e) {
    try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (_e2) { /* ignore */ }
    _fullAppMicStream = null;
    _fullAppRecorder  = null;
    setFullAppVoiceState("idle");
    if (voiceInputStatus) {
      voiceInputStatus.textContent = "此環境不支援語音輸入。";
      voiceInputStatus.hidden = false;
    }
    return;
  }

  // Hard timeout — auto-stop after FULL_APP_RECORDING_MAX_MS
  _fullAppRecordingTimer = setTimeout(function () {
    if (fullAppRecording) {
      stopFullAppVoiceInput();
    }
  }, FULL_APP_RECORDING_MAX_MS);
}

// TASK-241: voice input button wiring
if (voiceInputBtn) {
  voiceInputBtn.addEventListener("click", function () {
    if (fullAppRecording) {
      stopFullAppVoiceInput();
    } else if (!fullAppTranscribing) {
      openFullAppVoiceInput();
    }
  });
}

// TASK-242: voice settings toggle wiring
if (voiceInputEnabledToggle) {
  voiceInputEnabledToggle.addEventListener("change", function () {
    fullAppVoiceInputEnabled = Boolean(voiceInputEnabledToggle.checked);
    if (!fullAppVoiceInputEnabled && fullAppRecording) {
      cancelFullAppVoiceInput();
    }
  });
}
if (voiceAutosendToggle) {
  voiceAutosendToggle.addEventListener("change", function () {
    fullAppVoiceAutoSendEnabled = Boolean(voiceAutosendToggle.checked);
  });
}

// ---------------------------------------------------------------------------
// TASK-243: Voice Conversation Mode
// ---------------------------------------------------------------------------

function setConversationState(state) {
  fullAppVoiceConversationState = state;
  if (!conversationModeBtn) return;
  var statusMap = {
    "off":          { btn: "開始對話",       status: "",             hidden: true  },
    "waiting":      { btn: "停止對話",       status: "等待語音…",    hidden: false },
    "speaking":     { btn: "停止對話",       status: "偵測到聲音…",  hidden: false },
    "transcribing": { btn: "停止對話",       status: "辨識中…",      hidden: false },
    "sending":      { btn: "停止對話",       status: "傳送中…",      hidden: false },
    "error":        { btn: "開始對話",       status: "發生錯誤，請重試。", hidden: false }
  };
  var entry = statusMap[state] || statusMap["off"];
  conversationModeBtn.textContent = entry.btn;
  conversationModeBtn.dataset.state = state;
  conversationModeBtn.disabled = false;
  if (conversationModeStatus) {
    conversationModeStatus.textContent = entry.status;
    conversationModeStatus.hidden = entry.hidden;
    if (!entry.hidden) conversationModeStatus.dataset.state = state;
  }
}

function computeConversationRms(analyserNode) {
  var buf = new Float32Array(analyserNode.fftSize);
  analyserNode.getFloatTimeDomainData(buf);
  var sum = 0;
  for (var i = 0; i < buf.length; i++) sum += buf[i] * buf[i];
  return Math.sqrt(sum / buf.length);
}

function _conversationReleaseResources() {
  if (fullAppVoiceConversationVadTimer !== null) {
    clearInterval(fullAppVoiceConversationVadTimer);
    fullAppVoiceConversationVadTimer = null;
  }
  try {
    if (fullAppVoiceConversationRecorder && fullAppVoiceConversationRecorder.state !== "inactive") {
      fullAppVoiceConversationRecorder.stop();
    }
  } catch (_e) {}
  fullAppVoiceConversationRecorder = null;
  fullAppVoiceConversationChunks = [];
  try {
    if (fullAppVoiceConversationStream) {
      fullAppVoiceConversationStream.getTracks().forEach(function (t) { t.stop(); });
    }
  } catch (_e) {}
  fullAppVoiceConversationStream = null;
  try {
    if (fullAppVoiceConversationAudioContext && fullAppVoiceConversationAudioContext.state !== "closed") {
      fullAppVoiceConversationAudioContext.close();
    }
  } catch (_e) {}
  fullAppVoiceConversationAudioContext = null;
  fullAppVoiceConversationAnalyser = null;
  // TASK-252: release conv PCM capture resources
  _stopConvPcmCapture();
  _convPcmChunks = [];
}

function _startConversationUtteranceRecorder() {
  // TASK-244: reset diagnostics for this utterance recording
  resetFullAppVoiceDiagnosticsForRecording("conversation");
  fullAppVoiceDiagnostics.speechStarted = true;
  fullAppVoiceDiagnostics.maxRms = fullAppVoiceDiagnostics.lastRms;
  renderFullAppVoiceDiagnostics();

  fullAppVoiceConversationChunks = [];
  // TASK-244b: use shared mime type selector (same priority as manual mic)
  var mimeType = selectVoiceMimeType();
  var recorder;
  try {
    recorder = new MediaRecorder(
      fullAppVoiceConversationStream,
      mimeType ? { mimeType: mimeType } : {}
    );
  } catch (_e) {
    setConversationState("error");
    return;
  }
  fullAppVoiceConversationRecorder = recorder;
  recorder.addEventListener("dataavailable", function (ev) {
    if (ev.data && ev.data.size > 0) fullAppVoiceConversationChunks.push(ev.data);
  });
  recorder.addEventListener("stop", function () {
    // TASK-252: encode PCM chunks as WAV for FunASR compatibility
    _stopConvPcmCapture();
    var wavBlob = _encodeWavPcm(_convPcmChunks, FULL_APP_STT_PCM_SAMPLE_RATE);
    _convPcmChunks = [];
    _transcribeConversationChunks([wavBlob], "audio/wav");
  });
  // TASK-252: start PCM capture in parallel with MediaRecorder
  _startConvPcmCapture(fullAppVoiceConversationStream);
  recorder.start();
}

function _stopConversationUtteranceRecorder() {
  setConversationState("transcribing");
  try {
    if (fullAppVoiceConversationRecorder && fullAppVoiceConversationRecorder.state !== "inactive") {
      fullAppVoiceConversationRecorder.stop();
    }
  } catch (_e) {
    setConversationState("error");
  }
}

function _transcribeConversationChunks(chunks, mimeType) {
  var audioBlob;
  try {
    audioBlob = new Blob(chunks || [], { type: mimeType || "audio/webm" });
  } catch (_e) {
    if (fullAppVoiceConversationEnabled) setConversationState("waiting");
    return;
  }

  // TASK-244: update diagnostics with blob/recording metadata
  try { fullAppVoiceDiagnostics.blobSizeBytes = audioBlob.size || 0; } catch (_e) {}
  fullAppVoiceDiagnostics.mimeType = mimeType || "";
  fullAppVoiceDiagnostics.chunksCount = (chunks || []).length;
  var _convEndedAt = Date.now();
  fullAppVoiceDiagnostics.recordingEndedAt = _convEndedAt;
  fullAppVoiceDiagnostics.durationMs = _convEndedAt - (fullAppVoiceDiagnostics.recordingStartedAt || _convEndedAt);
  // TASK-244b: pipeline diagnostics — selectedMimeType, bytesPerSecond, in-memory preview blob
  fullAppVoiceDiagnostics.selectedMimeType = mimeType || "";
  if (audioBlob && audioBlob.size > 0) {
    fullAppLastAudioBlob = audioBlob;
    fullAppVoiceDiagnostics.lastAudioPreviewAvailable = true;
    if (fullAppVoiceDiagnostics.durationMs > 0) {
      fullAppVoiceDiagnostics.bytesPerSecond = Math.round(audioBlob.size / (fullAppVoiceDiagnostics.durationMs / 1000));
    }
    if (voicePreviewPlayBtn) voicePreviewPlayBtn.disabled = false;
  }
  renderFullAppVoiceDiagnostics();

  // TASK-267: status-only Owner Voice Gate dry-run for Conversation Mode.
  // Fire-and-forget: accept/reject/error/not_computed must not block STT or /chat.
  runOwnerVoiceConversationModeDryRun(audioBlob);

  transcribeFullAppAudioBlob(audioBlob).then(function (transcript) {
    if (!fullAppVoiceConversationEnabled) return;

    if (transcript === null || !transcript) {
      // TASK-244: empty/unavailable diagnostics
      fullAppVoiceDiagnostics.emptyTranscript = true;
      fullAppVoiceDiagnostics.sttStatus = "empty";
      renderFullAppVoiceDiagnostics();
      _recordVoiceDiagnosticsHistory();
      setConversationState("waiting");
      return;
    }

    var trimmed = transcript.trim();
    if (!trimmed || trimmed.length > FULL_APP_VOICE_CHAT_MAX_CHARS) {
      fullAppVoiceDiagnostics.emptyTranscript = true;
      fullAppVoiceDiagnostics.sttStatus = "empty";
      renderFullAppVoiceDiagnostics();
      setConversationState("waiting");
      return;
    }

    // TASK-244: success transcript diagnostics
    fullAppVoiceDiagnostics.transcriptLength  = trimmed.length;
    fullAppVoiceDiagnostics.transcriptPreview = makeSafeTranscriptPreview(trimmed);
    fullAppVoiceDiagnostics.emptyTranscript   = false;
    fullAppVoiceDiagnostics.sttStatus         = "success";
    renderFullAppVoiceDiagnostics();
    _recordVoiceDiagnosticsHistory();

    if (msgInput) {
      msgInput.value = trimmed;
      msgInput.dispatchEvent(new Event("input"));
    }

    if (!isSending && !editingMessageState && typeof sendMessage === "function") {
      setConversationState("sending");
      var result = sendMessage(trimmed);
      if (result && typeof result.then === "function") {
        result.then(function () {
          if (fullAppVoiceConversationEnabled) setConversationState("waiting");
        }).catch(function () {
          if (fullAppVoiceConversationEnabled) setConversationState("waiting");
        });
      } else {
        if (fullAppVoiceConversationEnabled) setConversationState("waiting");
      }
    } else {
      setConversationState("waiting");
    }
  }).catch(function () {
    // TASK-244: error diagnostics
    fullAppVoiceDiagnostics.sttStatus = "error";
    renderFullAppVoiceDiagnostics();
    _recordVoiceDiagnosticsHistory();
    if (fullAppVoiceConversationEnabled) setConversationState("waiting");
  });
}

// TASK-256: Best-effort startup warmup — fires once, 3s after backend health OK.
// No mic. No getUserMedia. No chat history. No Pet Window / TTS / Output Queue.
// Calls /stt/warmup and /llm/warmup in parallel; updates diagnostics; ignores errors.
function _triggerStartupWarmup() {
  if (!STARTUP_WARMUP_ENABLED) {
    fullAppVoiceDiagnostics.startupWarmupEnabled = false;
    fullAppVoiceDiagnostics.sttWarmupStatus = "disabled";
    fullAppVoiceDiagnostics.ollamaWarmupStatus = "disabled";
    return;
  }
  fullAppVoiceDiagnostics.startupWarmupEnabled = true;
  fullAppVoiceDiagnostics.lastStartupWarmupAt = Date.now();

  if (STARTUP_STT_WARMUP_ENABLED) {
    var sttT0 = Date.now();
    fullAppVoiceDiagnostics.sttWarmupStatus = "running";
    fetch(BACKEND_URL + "/stt/warmup", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        fullAppVoiceDiagnostics.sttWarmupStatus  = (data && data.warmupStatus) ? String(data.warmupStatus) : "unknown";
        fullAppVoiceDiagnostics.sttWarmupLatencyMs = Date.now() - sttT0;
        fullAppVoiceDiagnostics.sttWarmupError   = null;
      })
      .catch(function (err) {
        fullAppVoiceDiagnostics.sttWarmupStatus  = "error";
        fullAppVoiceDiagnostics.sttWarmupLatencyMs = Date.now() - sttT0;
        fullAppVoiceDiagnostics.sttWarmupError   = (err && err.name) ? err.name : "fetch_error";
      });
  } else {
    fullAppVoiceDiagnostics.sttWarmupStatus = "disabled";
  }

  if (STARTUP_OLLAMA_WARMUP_ENABLED) {
    var llmT0 = Date.now();
    fullAppVoiceDiagnostics.ollamaWarmupStatus = "running";
    fetch(BACKEND_URL + "/llm/warmup", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        fullAppVoiceDiagnostics.ollamaWarmupStatus  = (data && data.warmupStatus) ? String(data.warmupStatus) : "unknown";
        fullAppVoiceDiagnostics.ollamaWarmupLatencyMs = Date.now() - llmT0;
        fullAppVoiceDiagnostics.ollamaWarmupError   = null;
      })
      .catch(function (err) {
        fullAppVoiceDiagnostics.ollamaWarmupStatus  = "error";
        fullAppVoiceDiagnostics.ollamaWarmupLatencyMs = Date.now() - llmT0;
        fullAppVoiceDiagnostics.ollamaWarmupError   = (err && err.name) ? err.name : "fetch_error";
      });
  } else {
    fullAppVoiceDiagnostics.ollamaWarmupStatus = "disabled";
  }
}

// TASK-255: resume conversation AudioContext if it was auto-suspended by browser background
// policy (Chromium suspends AudioContext when page is hidden or backgrounded). Call this from
// the VAD tick and from focus/visibility restore handlers so VAD stays alive across focus changes.
function _resumeConversationAudioContextIfSuspended() {
  var ctx = fullAppVoiceConversationAudioContext;
  if (ctx) {
    fullAppVoiceDiagnostics.audioContextState = ctx.state || "unknown";
    if (ctx.state === "suspended") {
      ctx.resume().catch(function () {});
    }
  } else {
    fullAppVoiceDiagnostics.audioContextState = "none";
  }
}

function _conversationVadTick() {
  // TASK-255: resume AudioContext if throttled/suspended during background/minimize
  _resumeConversationAudioContextIfSuspended();
  var state = fullAppVoiceConversationState;
  if (state === "sending" || state === "transcribing") return;
  if (!fullAppVoiceConversationAnalyser) return;

  var rms = computeConversationRms(fullAppVoiceConversationAnalyser);
  var now = Date.now();

  // TASK-244: update VAD diagnostics every tick
  fullAppVoiceDiagnostics.lastRms = rms;
  if (rms > fullAppVoiceDiagnostics.maxRms) fullAppVoiceDiagnostics.maxRms = rms;
  fullAppVoiceDiagnostics.conversationState = state;
  renderFullAppVoiceDiagnostics();

  if (state === "waiting") {
    if (rms >= fullAppConversationRmsThreshold) {
      fullAppVoiceConversationSpeechStartedAt = now;
      fullAppVoiceConversationLastVoiceAt = now;
      setConversationState("speaking");
      _startConversationUtteranceRecorder();
    }
  } else if (state === "speaking") {
    if (rms >= fullAppConversationRmsThreshold) {
      fullAppVoiceConversationLastVoiceAt = now;
    }
    var silenceDuration = now - fullAppVoiceConversationLastVoiceAt;
    var speechDuration  = now - fullAppVoiceConversationSpeechStartedAt;
    var minMet   = speechDuration >= FULL_APP_CONVERSATION_MIN_SPEECH_MS;
    var timedOut = speechDuration >= FULL_APP_CONVERSATION_MAX_UTTERANCE_MS;
    if (timedOut || (minMet && silenceDuration >= fullAppConversationSilenceMs)) {
      // TASK-244: record stop reason and silence duration before stopping
      fullAppVoiceDiagnostics.stopReason = timedOut ? "max_duration" : "silence";
      fullAppVoiceDiagnostics.silenceMsAtStop = silenceDuration;
      _stopConversationUtteranceRecorder();
    }
  }
}

async function startConversationMode() {
  if (!fullAppVoiceInputEnabled) return;
  if (fullAppVoiceConversationEnabled) return;
  if (typeof MediaRecorder === "undefined") {
    setConversationState("error");
    return;
  }

  var stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: FULL_APP_VOICE_AUDIO_CONSTRAINTS });
  } catch (_e) {
    setConversationState("error");
    return;
  }

  // TASK-244b: capture audio track settings for diagnostics
  try {
    var _convTrack = stream.getAudioTracks()[0];
    if (_convTrack && typeof _convTrack.getSettings === "function") {
      var _cts = _convTrack.getSettings();
      fullAppVoiceDiagnostics.constraintsEchoCancellation = Boolean(_cts.echoCancellation);
      fullAppVoiceDiagnostics.constraintsNoiseSuppression = Boolean(_cts.noiseSuppression);
      fullAppVoiceDiagnostics.constraintsAutoGainControl  = Boolean(_cts.autoGainControl);
      renderFullAppVoiceDiagnostics();
    }
  } catch (_ctErr) {}

  var audioContext;
  try {
    audioContext = new AudioContext();
  } catch (_e) {
    try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (_e2) {}
    setConversationState("error");
    return;
  }

  var source = audioContext.createMediaStreamSource(stream);
  var analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  source.connect(analyser);

  fullAppVoiceConversationStream       = stream;
  fullAppVoiceConversationAudioContext = audioContext;
  fullAppVoiceConversationAnalyser     = analyser;
  fullAppVoiceConversationEnabled      = true;

  setConversationState("waiting");

  fullAppVoiceConversationVadTimer = setInterval(_conversationVadTick, FULL_APP_CONVERSATION_VAD_INTERVAL_MS);
}

function stopConversationMode() {
  // TASK-244: record cancel stop reason before releasing resources
  if (fullAppVoiceDiagnostics.stopReason === "none") {
    fullAppVoiceDiagnostics.stopReason = "cancel";
  }
  fullAppVoiceConversationEnabled = false;
  _conversationReleaseResources();
  setConversationState("off");
}

// TASK-243: conversation mode button wiring
if (conversationModeBtn) {
  conversationModeBtn.addEventListener("click", function () {
    if (fullAppVoiceConversationEnabled) {
      stopConversationMode();
    } else {
      startConversationMode();
    }
  });
}

// ---------------------------------------------------------------------------
// TASK-244: Voice Quality Diagnostics / VAD Tuning
// ---------------------------------------------------------------------------

// TASK-244b: Voice Pipeline Diagnostics helpers

function selectVoiceMimeType() {
  if (typeof MediaRecorder === "undefined" || typeof MediaRecorder.isTypeSupported !== "function") return "";
  var candidates = FULL_APP_VOICE_MIME_PRIORITY;
  for (var _mi = 0; _mi < candidates.length; _mi++) {
    if (MediaRecorder.isTypeSupported(candidates[_mi])) return candidates[_mi];
  }
  return "";
}

function _recordVoiceDiagnosticsHistory() {
  var d = fullAppVoiceDiagnostics;
  var entry = {
    mode:            d.mode,
    durationMs:      d.durationMs,
    blobSizeBytes:   d.blobSizeBytes,
    transcriptLength: d.transcriptLength,
    transcriptPreview: d.transcriptPreview,
    stopReason:      d.stopReason,
    selectedMimeType: d.selectedMimeType,
    bytesPerSecond:  d.bytesPerSecond,
    sttStatus:       d.sttStatus
  };
  fullAppVoiceDiagnosticsHistory.unshift(entry);
  if (fullAppVoiceDiagnosticsHistory.length > 2) fullAppVoiceDiagnosticsHistory.length = 2;
}

function _setVoicePreviewStatus(msg) {
  if (voicePreviewStatus) voicePreviewStatus.textContent = msg || "";
  fullAppVoiceDiagnostics.previewStatus = msg || "";
}

function revokeLastAudioObjectUrl() {
  if (voicePreviewAudio) {
    voicePreviewAudio.pause();
    voicePreviewAudio.src = "";
  }
  if (fullAppLastAudioObjectUrl) {
    try { URL.revokeObjectURL(fullAppLastAudioObjectUrl); } catch (_e) {}
    fullAppLastAudioObjectUrl = null;
  }
  fullAppVoiceDiagnostics.lastAudioObjectUrlCreated = false;
  fullAppVoiceDiagnostics.objectUrlActive = false;
  if (voicePreviewPlayBtn) voicePreviewPlayBtn.disabled = !fullAppVoiceDiagnostics.lastAudioPreviewAvailable;
}

function playLastAudioPreview() {
  if (!fullAppLastAudioBlob || fullAppLastAudioBlob.size === 0) {
    _setVoicePreviewStatus("尚無可播放錄音");
    renderFullAppVoiceDiagnostics();
    return;
  }
  var _el = voicePreviewAudio;
  if (!_el) { _setVoicePreviewStatus("play failed: no audio element"); renderFullAppVoiceDiagnostics(); return; }

  // canPlayType diagnostics before attempting play
  var _blobType = fullAppLastAudioBlob.type || fullAppVoiceDiagnostics.selectedMimeType || "";
  var _selType  = fullAppVoiceDiagnostics.selectedMimeType || _blobType;
  fullAppVoiceDiagnostics.audioCanPlayTypeResult     = (_el.canPlayType && _selType)  ? _el.canPlayType(_selType)  : "";
  fullAppVoiceDiagnostics.audioBlobTypeCanPlayResult = (_el.canPlayType && _blobType) ? _el.canPlayType(_blobType) : "";

  if (fullAppVoiceDiagnostics.audioCanPlayTypeResult === "" && _selType) {
    _setVoicePreviewStatus("此音訊格式目前無法播放，但仍可送 STT");
    renderFullAppVoiceDiagnostics();
    return;
  }

  // Revoke previous object URL only when replacing with a new one
  if (fullAppLastAudioObjectUrl) {
    _el.pause();
    _el.src = "";
    try { URL.revokeObjectURL(fullAppLastAudioObjectUrl); } catch (_re) {}
    fullAppLastAudioObjectUrl = null;
    fullAppVoiceDiagnostics.objectUrlActive = false;
  }

  // Reset error fields
  fullAppVoiceDiagnostics.previewErrorName    = "";
  fullAppVoiceDiagnostics.previewErrorMessage = "";
  fullAppVoiceDiagnostics.audioElementErrorCode = -1;

  try {
    var _url = URL.createObjectURL(fullAppLastAudioBlob);
    fullAppLastAudioObjectUrl = _url;
    fullAppVoiceDiagnostics.lastAudioObjectUrlCreated = true;
    fullAppVoiceDiagnostics.objectUrlActive = true;
    _setVoicePreviewStatus("播放中…");
    renderFullAppVoiceDiagnostics();
    _el.src = _url;
    // ended: status clears, URL stays alive for replay — do NOT revoke
    _el.onended = function () {
      _setVoicePreviewStatus("");
      renderFullAppVoiceDiagnostics();
    };
    _el.onerror = function () {
      var _code = (_el.error && _el.error.code != null) ? _el.error.code : -1;
      var _msg  = (_el.error && _el.error.message) ? _el.error.message.slice(0, 80) : "";
      fullAppVoiceDiagnostics.audioElementErrorCode = _code;
      fullAppVoiceDiagnostics.previewErrorName    = "MediaError";
      fullAppVoiceDiagnostics.previewErrorMessage = _msg || ("code " + _code);
      _setVoicePreviewStatus("audio error code: " + _code);
      renderFullAppVoiceDiagnostics();
    };
    _el.play().catch(function (_err) {
      var _name = (_err && _err.name)    ? _err.name              : "PlayError";
      var _msg  = (_err && _err.message) ? _err.message.slice(0, 80) : "";
      fullAppVoiceDiagnostics.previewErrorName    = _name;
      fullAppVoiceDiagnostics.previewErrorMessage = _msg;
      _setVoicePreviewStatus("play failed: " + _name);
      renderFullAppVoiceDiagnostics();
    });
  } catch (_e) {
    var _en = (_e && _e.name)    ? _e.name              : "Error";
    var _em = (_e && _e.message) ? _e.message.slice(0, 80) : "";
    fullAppVoiceDiagnostics.previewErrorName    = _en;
    fullAppVoiceDiagnostics.previewErrorMessage = _em;
    _setVoicePreviewStatus("play failed: " + _en);
    renderFullAppVoiceDiagnostics();
  }
}

function makeSafeTranscriptPreview(text) {
  if (!text || typeof text !== "string") return "";
  var safe = text.trim().replace(/[\r\n]+/g, " ");
  return safe.length > 30 ? safe.slice(0, 30) + "…" : safe;
}

function renderFullAppVoiceDiagnostics() {
  var el = voiceDiagnosticsDisplay;
  if (!el) return;
  var d = fullAppVoiceDiagnostics;
  var lines = [
    "模式: " + d.mode,
    "錄音時長 ms: " + d.durationMs,
    "Blob 大小 bytes: " + d.blobSizeBytes,
    "選取 MimeType: " + (d.selectedMimeType || "—"),
    "Blob 實際 type: " + (d.mimeType || "—"),
    "每秒位元組: " + d.bytesPerSecond,
    "Chunks: " + d.chunksCount,
    "Transcript 長度: " + d.transcriptLength,
    "Transcript 預覽: " + (d.transcriptPreview || "—"),
    "空 transcript: " + (d.emptyTranscript ? "是" : "否"),
    "Auto-send: " + (d.autoSendEnabled ? "開" : "關"),
    "對話狀態: " + d.conversationState,
    "停止原因: " + d.stopReason,
    "STT 狀態: " + d.sttStatus,
    "STT 語言: " + (d.sttLanguage || "unknown") + "  已鎖定: " + (d.languageLocked ? "是" : "否"),
    "STT 任務: " + (d.sttTask || "unknown"),
    "STT 提供者: " + (d.sttProvider || "unknown") + "  模型: " + (d.sttModel || "unknown"),
    "偵測語言: " + (d.detectedLanguage || "none"),
    "請求模型: " + (d.sttRequestedModel || "unknown") + "  解析模型: " + (d.sttResolvedModel || "unknown"),
    "模型來源: " + (d.sttModelSource || "unknown") + "  載入狀態: " + (d.sttModelLoadStatus || "unknown"),
    "模型載入錯誤: " + (d.sttModelLoadError || "none"),
    "原始 Transcript: " + (d.sttRawTranscriptPreview || "—"),
    "修正 Transcript: " + (d.sttCorrectedTranscriptPreview || "—"),
    "已修正: " + (d.sttCorrectionApplied ? "是" : "否") + "  修正模式: " + (d.sttCorrectionMode || "—"),
    "修正原因: " + (d.sttCorrectionReason || "—"),
    "命中 alias: " + (d.sttMatchedAlias || "—") + "  canonical: " + (d.sttCanonicalTerm || "—"),
    "STT Provider: " + (d.sttProviderResolved || "unknown") + "  來源: " + (d.sttProviderSource || "unknown"),
    "Provider 載入: " + (d.sttProviderLoadStatus || "unknown") + "  fallback: " + (d.sttProviderFallbackReason || "none"),
    "焦點安全: " + (d.voiceCaptureFocusSafe ? "是" : "否") + "  可見: " + (d.lastVisibilityState || "visible") + "  焦點: " + (d.lastWindowFocusState || "focused"),
    "AudioCtx 狀態: " + (d.audioContextState || "none") + "  中斷原因: " + (d.captureInterruptedReason || "none") + "  因可見性: " + (d.captureInterruptedByVisibility ? "是" : "否"),
    "Warmup: " + (d.startupWarmupEnabled ? "ON" : "OFF") + "  STT: " + (d.sttWarmupStatus || "pending") + " " + d.sttWarmupLatencyMs + "ms  Ollama: " + (d.ollamaWarmupStatus || "pending") + " " + d.ollamaWarmupLatencyMs + "ms",
    "Owner Voice dry-run: " + (d.ownerVoiceDryRunEnabled ? "ON" : "OFF") + "  source: " + (d.ownerVoiceDryRunSource || "none") + "  狀態: " + (d.ownerVoiceDryRunStatus || "disabled") + "  原因: " + (d.ownerVoiceDryRunReason || "unknown"),
    "Owner Voice score: " + (d.ownerVoiceScore === null || d.ownerVoiceScore === undefined ? "—" : d.ownerVoiceScore) + " / " + (d.ownerVoiceThreshold === null || d.ownerVoiceThreshold === undefined ? "—" : d.ownerVoiceThreshold) + "  accepted: " + (d.ownerVoiceAccepted === null || d.ownerVoiceAccepted === undefined ? "unknown" : (d.ownerVoiceAccepted ? "true" : "false")),
    "Owner Voice safety: rawAudioPersisted=" + d.rawAudioPersisted + " candidateEmbeddingPersisted=" + d.candidateEmbeddingPersisted + " storedCentroidExposed=" + d.storedCentroidExposed + " runtimeHardBlocked=" + d.runtimeHardBlocked,
    "---",
    "VAD 最後 RMS: " + d.lastRms.toFixed(4),
    "VAD 最高 RMS: " + d.maxRms.toFixed(4),
    "RMS 閾值: " + d.rmsThreshold.toFixed(4),
    "靜音時長 ms: " + d.silenceDurationMs,
    "最短說話 ms: " + d.minSpeechMs,
    "最長句子 ms: " + d.maxUtteranceMs,
    "偵測到說話: " + (d.speechStarted ? "是" : "否"),
    "停止時靜音 ms: " + d.silenceMsAtStop,
    "VAD 間隔 ms: " + FULL_APP_CONVERSATION_VAD_INTERVAL_MS,
    "---",
    "Audio約束 echo:" + d.constraintsEchoCancellation + " 降噪:" + d.constraintsNoiseSuppression + " 增益:" + d.constraintsAutoGainControl,
    "---",
    "錄音預覽: " + (d.lastAudioPreviewAvailable ? "可用" : "無") + "  objectUrlActive: " + (d.objectUrlActive ? "yes" : "no"),
    "canPlayType(selectedMimeType): " + (d.audioCanPlayTypeResult || "—"),
    "canPlayType(blob.type): "       + (d.audioBlobTypeCanPlayResult || "—"),
    "previewStatus: "   + (d.previewStatus || "—"),
    "previewError: "    + (d.previewErrorName ? d.previewErrorName + " — " + (d.previewErrorMessage || "") : "—"),
    "audioErrCode: "    + (d.audioElementErrorCode !== -1 ? d.audioElementErrorCode : "—")
  ];
  for (var _hi = 0; _hi < fullAppVoiceDiagnosticsHistory.length; _hi++) {
    var _h = fullAppVoiceDiagnosticsHistory[_hi];
    var _mt = _h.selectedMimeType ? _h.selectedMimeType.replace("audio/", "").replace(";codecs=opus", "+opus") : "—";
    if (_hi === 0) lines.push("---");
    lines.push("#" + (_hi + 1) + " " + _h.mode + " " + _h.durationMs + "ms " + _h.blobSizeBytes + "B " + _mt + " " + _h.bytesPerSecond + "B/s STT:" + _h.sttStatus);
  }
  el.textContent = lines.join("\n");
}

function updateFullAppVoiceDiagnostics(patch) {
  if (patch && typeof patch === "object") {
    var keys = Object.keys(patch);
    for (var i = 0; i < keys.length; i++) {
      if (Object.prototype.hasOwnProperty.call(fullAppVoiceDiagnostics, keys[i])) {
        fullAppVoiceDiagnostics[keys[i]] = patch[keys[i]];
      }
    }
  }
  renderFullAppVoiceDiagnostics();
}

function resetFullAppVoiceDiagnosticsForRecording(mode) {
  fullAppVoiceDiagnostics.mode              = mode || "none";
  fullAppVoiceDiagnostics.recordingStartedAt = Date.now();
  fullAppVoiceDiagnostics.recordingEndedAt   = 0;
  fullAppVoiceDiagnostics.durationMs         = 0;
  fullAppVoiceDiagnostics.blobSizeBytes      = 0;
  fullAppVoiceDiagnostics.mimeType           = "";
  fullAppVoiceDiagnostics.chunksCount        = 0;
  fullAppVoiceDiagnostics.transcriptLength   = 0;
  fullAppVoiceDiagnostics.transcriptPreview  = "";
  fullAppVoiceDiagnostics.emptyTranscript    = false;
  fullAppVoiceDiagnostics.autoSendEnabled    = fullAppVoiceAutoSendEnabled;
  fullAppVoiceDiagnostics.conversationState  = fullAppVoiceConversationState;
  fullAppVoiceDiagnostics.stopReason         = "none";
  fullAppVoiceDiagnostics.lastRms            = 0;
  fullAppVoiceDiagnostics.maxRms             = 0;
  fullAppVoiceDiagnostics.rmsThreshold       = fullAppConversationRmsThreshold;
  fullAppVoiceDiagnostics.silenceDurationMs  = fullAppConversationSilenceMs;
  fullAppVoiceDiagnostics.minSpeechMs        = FULL_APP_CONVERSATION_MIN_SPEECH_MS;
  fullAppVoiceDiagnostics.maxUtteranceMs     = FULL_APP_CONVERSATION_MAX_UTTERANCE_MS;
  fullAppVoiceDiagnostics.speechStarted      = false;
  fullAppVoiceDiagnostics.silenceMsAtStop    = 0;
  fullAppVoiceDiagnostics.sttStatus          = "none";
  fullAppVoiceDiagnostics.selectedMimeType   = "";
  fullAppVoiceDiagnostics.bytesPerSecond     = 0;
  fullAppVoiceDiagnostics.lastAudioPreviewAvailable = false;
  fullAppVoiceDiagnostics.lastAudioObjectUrlCreated = false;
  fullAppVoiceDiagnostics.objectUrlActive    = false;
  fullAppVoiceDiagnostics.previewStatus      = "";
  fullAppVoiceDiagnostics.previewErrorName   = "";
  fullAppVoiceDiagnostics.previewErrorMessage = "";
  fullAppVoiceDiagnostics.audioElementErrorCode = -1;
  fullAppVoiceDiagnostics.audioCanPlayTypeResult = "";
  fullAppVoiceDiagnostics.audioBlobTypeCanPlayResult = "";
  // TASK-245: reset language-lock fields — repopulated after each STT call
  fullAppVoiceDiagnostics.sttLanguage      = "";
  fullAppVoiceDiagnostics.languageLocked   = false;
  fullAppVoiceDiagnostics.sttTask          = "";
  fullAppVoiceDiagnostics.sttProvider      = "";
  fullAppVoiceDiagnostics.sttModel         = "";
  fullAppVoiceDiagnostics.detectedLanguage = "";
  // TASK-246: reset model quality fields — repopulated after each STT call
  fullAppVoiceDiagnostics.sttRequestedModel  = "";
  fullAppVoiceDiagnostics.sttResolvedModel   = "";
  fullAppVoiceDiagnostics.sttModelSource     = "";
  fullAppVoiceDiagnostics.sttModelLoadStatus = "";
  fullAppVoiceDiagnostics.sttModelLoadError  = "";
  // TASK-247: reset correction diagnostics — repopulated after each STT call
  fullAppVoiceDiagnostics.sttRawTranscriptPreview       = "";
  fullAppVoiceDiagnostics.sttCorrectedTranscriptPreview  = "";
  fullAppVoiceDiagnostics.sttCorrectionApplied           = false;
  fullAppVoiceDiagnostics.sttCorrectionMode              = "";
  fullAppVoiceDiagnostics.sttCorrectionReason            = "";
  // TASK-248: reset matched alias / canonical term diagnostics
  fullAppVoiceDiagnostics.sttMatchedAlias                = "";
  fullAppVoiceDiagnostics.sttCanonicalTerm               = "";
  // TASK-249: reset provider selection diagnostics — repopulated after each STT call
  fullAppVoiceDiagnostics.sttProviderRequested           = "";
  fullAppVoiceDiagnostics.sttProviderResolved            = "";
  fullAppVoiceDiagnostics.sttProviderSource              = "";
  fullAppVoiceDiagnostics.sttProviderLoadStatus          = "";
  fullAppVoiceDiagnostics.sttProviderLoadError           = "";
  fullAppVoiceDiagnostics.sttProviderFallbackReason      = "";
  // TASK-266/267: reset owner-voice dry-run status; settings sync will flip
  // enabled back on if Owner Voice Gate is enrolled+enabled.
  var _ownerVoiceDryRunSource = _ownerVoiceDryRunSourceForRecordingMode(mode);
  var _ownerVoiceDryRunEnabled = _ownerVoiceDryRunSource === "conversation_mode"
    ? _ownerVoiceConversationModeDryRunEnabled()
    : _ownerVoiceManualMicDryRunEnabled();
  fullAppVoiceDiagnostics.ownerVoiceDryRunEnabled        = _ownerVoiceDryRunEnabled;
  fullAppVoiceDiagnostics.ownerVoiceDryRunSource         = _ownerVoiceDryRunSource;
  fullAppVoiceDiagnostics.ownerVoiceDryRunStatus         = fullAppVoiceDiagnostics.ownerVoiceDryRunEnabled ? "pending" : "disabled";
  fullAppVoiceDiagnostics.ownerVoiceDryRunReason         = fullAppVoiceDiagnostics.ownerVoiceDryRunEnabled ? "recording_started" : "owner_voice_gate_disabled";
  fullAppVoiceDiagnostics.ownerVoiceScore                = null;
  fullAppVoiceDiagnostics.ownerVoiceThreshold            = _ownerVoiceManualMicThreshold();
  fullAppVoiceDiagnostics.ownerVoiceAccepted             = null;
  fullAppVoiceDiagnostics.ownerVoiceCheckedAt            = "";
  fullAppVoiceDiagnostics.rawAudioPersisted              = false;
  fullAppVoiceDiagnostics.candidateEmbeddingPersisted    = false;
  fullAppVoiceDiagnostics.storedCentroidExposed          = false;
  fullAppVoiceDiagnostics.runtimeHardBlocked             = false;
  // constraintsEchoCancellation/NoiseSuppression/AutoGainControl: not reset (carry over from stream)
  revokeLastAudioObjectUrl();
  if (voicePreviewPlayBtn) voicePreviewPlayBtn.disabled = true;
  if (voicePreviewStatus) voicePreviewStatus.textContent = "";
  renderFullAppVoiceDiagnostics();
}

// TASK-244: VAD tuning controls wiring — session-only, no persistence
if (vadRmsThresholdInput) {
  vadRmsThresholdInput.addEventListener("input", function () {
    var val = parseFloat(vadRmsThresholdInput.value);
    if (!isNaN(val) && val >= 0.01 && val <= 0.10) {
      fullAppConversationRmsThreshold = val;
      fullAppVoiceDiagnostics.rmsThreshold = val;
      renderFullAppVoiceDiagnostics();
    }
  });
}
if (vadSilenceMsSelect) {
  vadSilenceMsSelect.addEventListener("change", function () {
    var val = parseInt(vadSilenceMsSelect.value, 10);
    if (!isNaN(val)) {
      fullAppConversationSilenceMs = val;
      fullAppVoiceDiagnostics.silenceDurationMs = val;
      renderFullAppVoiceDiagnostics();
    }
  });
}

// TASK-244b: preview play button wiring — in-memory only, no disk write
if (voicePreviewPlayBtn) {
  voicePreviewPlayBtn.addEventListener("click", function () {
    playLastAudioPreview();
  });
}

// TASK-172A/172B: initialise button states on load (no screenshot yet).
updateAnalyzeButtonState();
updateAskButtonState();

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

if (ownerVoiceGateRefreshBtn) {
  ownerVoiceGateRefreshBtn.addEventListener("click", () => {
    loadOwnerVoiceGateStatus();
  });
}

if (ownerVoiceGateSafetyAccepted) {
  ownerVoiceGateSafetyAccepted.addEventListener("change", () => {
    saveOwnerVoiceGateSettings({
      safetyNoticeAccepted: ownerVoiceGateSafetyAccepted.checked,
    });
  });
}

if (ownerVoiceGateEnabledToggle) {
  ownerVoiceGateEnabledToggle.addEventListener("change", () => {
    saveOwnerVoiceGateSettings({
      enabled: ownerVoiceGateEnabledToggle.checked,
    });
  });
}

if (ownerVoiceGateSaveThresholdBtn) {
  ownerVoiceGateSaveThresholdBtn.addEventListener("click", () => {
    saveOwnerVoiceGateSettings({
      threshold: _ownerVoiceThresholdValue(),
    });
  });
}

if (ownerVoiceGateEnrollBtn) {
  ownerVoiceGateEnrollBtn.addEventListener("click", () => {
    enrollOwnerVoiceGateFromFiles();
  });
}

if (ownerVoiceGateReenrollBtn) {
  ownerVoiceGateReenrollBtn.addEventListener("click", () => {
    enrollOwnerVoiceGateFromFiles();
  });
}

if (ownerVoiceGateDeleteBtn) {
  ownerVoiceGateDeleteBtn.addEventListener("click", () => {
    deleteOwnerVoiceGateVoiceprint();
  });
}

// TASK-056: key save / clear event listeners
saveProviderKeyBtn.addEventListener("click", () => {
  saveProviderKey();
});

clearProviderKeyBtn.addEventListener("click", () => {
  clearProviderKey();
});

// TASK-060: Test Connection button.

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
  if (e.key === "Escape" && editingMessageState) {
    e.preventDefault();
    cancelEditUserMessage();
  } else if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(msgInput.value);
  }
});

// Auto-grow textarea
msgInput.addEventListener("input", () => {
  msgInput.style.height = "auto";
  msgInput.style.height = Math.min(msgInput.scrollHeight, 100) + "px";
});

// TASK-193: append Pet Window chat messages (user text + AI reply) to Full App chat.
// Fired by main process when Pet Window completes a successful /chat call.
// Payload is text-only — no audio blob, no base64, no raw diagnostics.
// No-op if window.dragonPet.onChatMirrorFromPet is unavailable (test env, preload absent).
function setupPetChatMirrorListener() {
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (!api || typeof api.onChatMirrorFromPet !== "function") return;
  api.onChatMirrorFromPet(function (payload) {
    if (!payload.userMessage || !payload.reply) return;
    // TASK-195: map inputMethod to source so voice vs text are visually distinguished.
    const userSource = payload.inputMethod === "voice" ? "pet_voice" : "pet_text";
    appendMessage("user", payload.userMessage, { autoScroll: true, source: userSource, ts: Date.now() });
    appendMessage("pet", payload.reply, { source: userSource, ts: Date.now() });
    maybeScrollChatToBottom();
    setMood(payload.mood);
  });
}
setupPetChatMirrorListener();

// TASK-108: idle timer — reset activity on user interactions.
// Adding extra listeners on existing elements is intentional (stacking is fine).
// Guards for window/document: addEventListener may be absent in test environments.
// Safety: resetActivity() is UI-only — no /chat, no fetch, no external API.
msgInput.addEventListener("keydown", resetActivity);
msgInput.addEventListener("input",   resetActivity);
sendBtn.addEventListener("click",    resetActivity);
if (typeof window !== "undefined" && typeof window.addEventListener === "function") {
  window.addEventListener("focus", resetActivity);
}
if (typeof document !== "undefined" && typeof document.addEventListener === "function") {
  document.addEventListener("pointerdown", resetActivity);
}

// TASK-200: clear unread indicator when Full App regains focus or becomes visible.
document.addEventListener("visibilitychange", () => {
  closeChatContextMenu();
  // TASK-255: track visibility state; do NOT cancel voice capture on hidden
  fullAppVoiceDiagnostics.lastVisibilityState = document.hidden ? "hidden" : "visible";
  if (!document.hidden) {
    clearUnread();
    // TASK-255: resume conversation AudioContext suspended by browser background policy
    _resumeConversationAudioContextIfSuspended();
  }
});
if (typeof window !== "undefined" && typeof window.addEventListener === "function") {
  window.addEventListener("focus", clearUnread);
  window.addEventListener("blur", closeChatContextMenu);
  window.addEventListener("focus", () => recordInteractionEvent("full_app_focused")); // TASK-214
  // TASK-255: resume AudioContext and track focus state — never cancel voice on blur
  window.addEventListener("focus", function () {
    fullAppVoiceDiagnostics.lastWindowFocusState = "focused";
    _resumeConversationAudioContextIfSuspended();
  });
  window.addEventListener("blur", function () {
    fullAppVoiceDiagnostics.lastWindowFocusState = "blurred";
  });
}

// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------
// TASK-198: Chat message search / filter — pure DOM visibility toggle.
// No data mutation, no history write, no /chat call, no backend change.
// ---------------------------------------------------------------------------
// TASK-201: search result navigation state.
let searchResults = [];     // matching wrap elements, populated by filterChatMessages
let searchActiveIndex = -1; // -1 = no active result

// TASK-201: escape HTML special chars before inserting raw text into innerHTML.
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

// TASK-201: wrap each case-insensitive match in a highlight span.
// Operates on already-escaped HTML so the span tags are safe.
function highlightText(rawText, query) {
  const safe = escapeHtml(rawText);
  const escapedQ = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp(`(${escapedQ})`, "gi");
  return safe.replace(re, '<span class="search-highlight">$1</span>');
}

// TASK-201: advance the active search result by delta (+1 forward, -1 backward).
function navigateToSearchResult(delta) {
  if (!searchResults.length) return;
  // Remove active class from previous result
  if (searchActiveIndex >= 0 && searchActiveIndex < searchResults.length) {
    const prev = searchResults[searchActiveIndex];
    prev.className = prev.className.replace(/\s*search-active/g, "").trim();
  }
  searchActiveIndex = (searchActiveIndex + delta + searchResults.length) % searchResults.length;
  const active = searchResults[searchActiveIndex];
  if (!active.className.includes("search-active")) {
    active.className = active.className + " search-active";
  }
  if (typeof active.scrollIntoView === "function") {
    active.scrollIntoView({ block: "nearest" });
  }
  // Update count chip to show position
  if (chatSearchCountEl && chatSearchInput) {
    const q = (chatSearchInput.value || "").trim();
    if (q) {
      chatSearchCountEl.textContent = `找到 ${searchResults.length} 筆，第 ${searchActiveIndex + 1} 筆`;
    }
  }
}

function filterChatMessages(query) {
  const q = (query || "").trim().toLowerCase();
  // Reset navigation — remove active class from all previous results
  for (const el of searchResults) {
    el.className = el.className.replace(/\s*search-active/g, "").trim();
  }
  searchResults = [];
  searchActiveIndex = -1;

  let matchCount = 0;
  for (const child of chatArea.children) {
    const isUserOrPet = typeof child.className === "string" &&
      (child.className.includes("user") || child.className.includes("pet")) &&
      child.dataset && child.dataset.formalChat === "true";
    // Find the msg-body div (set in appendMessage — TASK-201)
    const childrenArr = Array.from(child.children || []);
    const body = childrenArr.find(c => typeof c.className === "string" && c.className === "msg-body");

    if (!q) {
      child.style.display = "";
      // Restore plain text (remove any highlight spans)
      if (body && child.dataset && child.dataset.msgText !== undefined) {
        body.innerHTML = escapeHtml(child.dataset.msgText);
      }
      continue;
    }

    if (!isUserOrPet) {
      child.style.display = "none";
      continue;
    }

    const rawText = (child.dataset && child.dataset.msgText) || "";
    if (rawText.toLowerCase().includes(q)) {
      child.style.display = "";
      matchCount++;
      searchResults.push(child);
      if (body) body.innerHTML = highlightText(rawText, q);
    } else {
      child.style.display = "none";
      if (body) body.innerHTML = escapeHtml(rawText);
    }
  }

  if (chatSearchCountEl) {
    if (!q) {
      chatSearchCountEl.textContent = "";
    } else if (matchCount > 0) {
      chatSearchCountEl.textContent = `找到 ${matchCount} 筆`;
    } else {
      chatSearchCountEl.textContent = "沒有找到符合的對話";
    }
  }
  updateEmptyChatState();
}

// TASK-197: Non-blocking Ollama liveness probe run after startup settings load.
// Updates the provider status chip only — no chat, no history, no Pet/TTS side effects.
// ---------------------------------------------------------------------------
async function checkLocalProviderLiveness() {
  if (!isOllamaChatPath()) return;
  const el = typeof providerStatusSummaryEl !== "undefined" ? providerStatusSummaryEl : null;
  if (!el) return;
  const prevText = el.textContent;
  const prevClass = el.className;
  el.textContent = "正在檢查本地 AI...";
  el.className = "provider-status-summary pending";
  try {
    const res = await fetch(`${BACKEND_URL}/provider/health`);
    if (!res.ok) {
      el.textContent = prevText;
      el.className = prevClass;
      return;
    }
    const data = await res.json();
    if (data.ollama_reachable === true) {
      // If fallback mode is active, keep the fallback warning — it's more important
      // than the "ready" status and tells the user about the configuration risk.
      if (!currentProviderSettings.fallback_to_mock) {
        el.textContent = "Ollama 本地 AI 已就緒。";
        el.className = "provider-status-summary active";
      } else {
        el.textContent = prevText;
        el.className = prevClass;
      }
    } else {
      el.textContent = "Ollama 尚未回應。第一次聊天可能需要較久，請確認 Ollama 已啟動。";
      el.className = "provider-status-summary warning";
    }
  } catch {
    // Restore settings-based summary on error — liveness check is non-critical.
    el.textContent = prevText;
    el.className = prevClass;
  }
}

// ---------------------------------------------------------------------------
// Startup
// ---------------------------------------------------------------------------
(async function startup() {
  await loadAndRenderChatHistory();  // TASK-194: restore history before greeting
  appendMessage("status", "Connecting to backend...");

  // TASK-197: 8-second timeout on startup health check to prevent indefinite hang.
  const _healthCtrl = new AbortController();
  const _healthTimer = setTimeout(() => _healthCtrl.abort(), 8000);
  try {
    const res = await fetch(`${BACKEND_URL}/health`, { signal: _healthCtrl.signal });
    clearTimeout(_healthTimer);
    const data = await res.json();
    if (data.status === "ok") {
      // Remove the connecting status
      chatArea.lastChild.remove();
      appendMessage("pet", "哼，吾在這裡。汝有何事就直說吧。", { noHistory: true, countsAsChat: false });
      setMood("neutral"); // also initialises pet expression and friendly hint via setPetExpression / moodHintLabel
      // TASK-109: Startup greeting — static character line, no /chat call, no backend request.
      // setPetExpression("proud") overrides the neutral set above; currentMood stays "neutral"
      // so idle timer restores correctly after inactivity.
      // Safety: this line contains no user data, no LLM call, no network request.
      setPetExpression("proud");
      setPetHint("哼，汝終於把吾叫醒了。今天也要好好努力，知道嗎？");
      lockCompanionHint(HINT_LOCK_MS); // TASK-111: protect startup greeting from idle override
      await loadMemories();
      await loadMemoryContextPreview();
      await loadAuditLogs();
      await loadProviderSettings();
      await loadOwnerVoiceGateStatus();
      // TASK-197: async Ollama liveness probe — runs in background, no await.
      // Does not write chat history, does not trigger Pet, does not call /chat.
      checkLocalProviderLiveness();
      // TASK-256: best-effort startup warmup — fires after short delay, no mic, no chat.
      setTimeout(function () { _triggerStartupWarmup(); }, STARTUP_WARMUP_DELAY_MS);
    } else {
      throw new Error("Unexpected health response");
    }
  } catch {
    clearTimeout(_healthTimer);
    chatArea.lastChild.remove();
    appendMessage(
      "error",
      `Backend not reachable at ${BACKEND_URL}.\nStart the backend first:\n  cd backend\n  uvicorn app.main:app --reload`
    );
    setChatRuntimeStatus("backend_offline", sourceStatusMessage("backend_offline"), "error");
    setMemoryStatus(`Cannot reach backend at ${BACKEND_URL}.`, true);
    setProviderSettingsStatus(`Cannot reach backend at ${BACKEND_URL}.`, true);
    setOwnerVoiceGateSettingsStatus(`Cannot reach backend at ${BACKEND_URL}.`, true);
    // TASK-083: show offline expression on startup failure
    setPetExpression("offline");
    setPetHint(moodHintLabel("offline"));
  }

  renderInteractionReactionPreview(); // TASK-216: show initial state
  msgInput.focus();
})();
