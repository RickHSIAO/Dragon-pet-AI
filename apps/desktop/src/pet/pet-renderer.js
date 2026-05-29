const PET_MODE_DEFAULTS = Object.freeze({
  expression: "neutral",
  hint: "\u54fc\uff0c\u6c5d\u53eb\u543e\u51fa\u4f86\u505a\u4ec0\u9ebc\uff1f",
  avatarSrc: "../renderer/assets/pet/christina/expressions/christina_neutral.png",
  bubbleMessage: "\u6253\u5b57\u8acb\u958b Full App\u3002",
});

const PET_BACKEND_DEFAULT_URL = "http://localhost:8000";
const PET_CHAT_TIMEOUT_MS = 100000;
const PET_REPLY_LONG_THRESHOLD = 160;
const PET_REPLY_PREVIEW_LIMIT = 120;
const PET_LONG_REPLY_HINT = "\u56de\u8986\u8f03\u9577\uff0c\u53ef\u958b Full App \u67e5\u770b\u5b8c\u6574\u5167\u5bb9\u3002";
const PET_IDLE_REPLY = "\u543e\u5728\u3002\u8981\u627e\u543e\u5c31\u53bb Full App \u8aaa\u8a71\u3002";
const PET_HANDOFF_REPLY = "\u53bb Full App \u8aaa\uff0c\u543e\u6703\u807d\u3002";
const PET_MOOD_SMOKE_REPLY = "\u8868\u60c5\u6620\u5c04\u6e2c\u8a66\u3002";
const PET_MOOD_SMOKE_API_NAME = "__dragonPetMoodExpressionSmoke";
// TASK-157: source token that signals Full App is waiting for a /chat reply.
// Pet renderer routes this to the "thinking" bubble state.
const PET_THINKING_SOURCE = "pet_thinking";
const PET_RECENT_REPLY_VISIBLE_MS = 90000;
const PET_HANDOFF_HINT_MS = 6000;
// TASK-159: quiet period after app launch before first idle rotation tick
const PET_IDLE_LAUNCH_QUIET_MS = 120000;
// TASK-159: cooldown after any user-facing activity before idle rotation resumes
const PET_IDLE_COOLDOWN_MS = 90000;
// TASK-158: interval between idle presence line rotations
const PET_IDLE_ROTATION_MS = 60000;
// TASK-167A: voice push-to-talk
const PET_RECORDING_MAX_MS = 30000;  // 30-second hard cap on a single recording
const PET_VOICE_MIC_DENIED_MSG = "麥克風權限被拒絕。請在系統設定中開啟麥克風權限。";
const PET_VOICE_NO_MIC_MSG = "找不到麥克風裝置。請確認麥克風已連接。";
const PET_VOICE_UNSUPPORTED_MSG = "此環境不支援語音錄音。";
const PET_VOICE_RECORDING_STATUS = "錄音中…";
// TASK-167B: STT transcription
const PET_STT_TIMEOUT_MS = 30000;  // 30-second timeout for backend STT
const PET_TRANSCRIBING_STATUS = "轉錄中…";
const PET_STT_UNAVAILABLE_MSG = "語音辨識目前不可用。";
const PET_STT_TIMEOUT_MSG = "語音辨識超時，請再試一次。";
const PET_STT_EMPTY_MSG = "沒有偵測到語音，請再試一次。";
const PET_STT_ERROR_MSG = "語音辨識出錯，請再試一次。";
const PET_STT_OFFLINE_MSG = "後端離線，無法辨識語音。";
// TASK-167C: voice transcript → /chat handoff
const PET_VOICE_CHAT_MAX_CHARS = 2000;
// TASK-168B: TTS playback — max characters sent to SpeechSynthesis
const PET_TTS_MAX_CHARS = 300;
// TASK-169: localStorage keys for TTS settings persistence
const PET_TTS_LS_VOICE  = "pet_tts_voice";
const PET_TTS_LS_RATE   = "pet_tts_rate";
const PET_TTS_LS_PITCH  = "pet_tts_pitch";
const PET_TTS_LS_VOLUME = "pet_tts_volume";
// TASK-169: safe bounds and defaults for speech controls
const PET_TTS_RATE_MIN  = 0.7;
const PET_TTS_RATE_MAX  = 1.3;
const PET_TTS_RATE_DEF  = 1.0;
const PET_TTS_PITCH_MIN = 0.8;
const PET_TTS_PITCH_MAX = 1.3;
const PET_TTS_PITCH_DEF = 1.0;
const PET_TTS_VOL_MIN   = 0.0;
const PET_TTS_VOL_MAX   = 1.0;
const PET_TTS_VOL_DEF   = 1.0;
const PET_VOICE_TRANSCRIPT_TOO_LONG_MSG = "語音太長，請縮短後再試。";
// TASK-158: short in-character idle presence lines (static local set)
const PET_IDLE_LINES = Object.freeze([
  // neutral
  "\u2026\u2026\u543e\u5728\u9019\u88e1\u3002",
  "\u6709\u4ec0\u9ebc\u4e8b\u55ce\uff1f",
  // tsundere / proud
  "\u54fc\uff0c\u6c5d\u53c8\u5728\u505a\u4ec0\u9ebc\uff1f",
  "\u543e\u624d\u6c92\u6709\u5728\u7b49\u6c5d\u5462\u3002",
  // sleepy
  "\u2026\u2026\u547c\uff0c\u7a0d\u5fae\u6709\u9ede\u77aa\u3002",
  "\u9019\u9ebc\u5b89\u975c\uff0c\u543e\u90fd\u5feb\u7761\u8457\u4e86\u3002",
  // focused
  "\u543e\u5728\u601d\u8003\u4e00\u4e9b\u91cd\u8981\u7684\u4e8b\u3002",
  "\u5225\u6253\u64fe\u543e\uff0c\u543e\u5728\u60f3\u6771\u897f\u3002",
  // companion / protective
  "\u6c5d\u9084\u597d\u55ce\uff1f",
  "\u6709\u9700\u8981\u7684\u8a71\uff0c\u543e\u5728\u9019\u88e1\u3002",
]);
const PET_DETAIL_TEXT_LIMIT = 140;
const PET_UNSAFE_DETAIL_PATTERN =
  /<think\b|<\/think>|thinking|done thinking|reasoning|traceback|stack trace|api[_-]?key|[{[}\]]/i;
const PET_UNSAFE_DETAIL_TOKENS = Object.freeze(["localhost", "127.0.0.1", ["114", "34"].join("")]);
let petChatPending = false;
let petTtsEnabled = false;     // TASK-168B: TTS is OFF by default
let petSpeakingActive = false; // TASK-168B: true while SpeechSynthesis is speaking
let petTtsVoiceName = "";     // TASK-169: name of selected TTS voice ("" = browser default)
let petTtsRate      = 1.0;   // TASK-169: current speech rate
let petTtsPitch     = 1.0;   // TASK-169: current pitch
let petTtsVolume    = 1.0;   // TASK-169: current volume
const petPresenceStates = typeof WeakMap === "function" ? new WeakMap() : null;
let fallbackPetPresenceState = null;

const CHRISTINA_EXPRESSION_ASSETS = Object.freeze({
  neutral: "../renderer/assets/pet/christina/expressions/christina_neutral.png",
  focused: "../renderer/assets/pet/christina/expressions/christina_focused.png",
  happy: "../renderer/assets/pet/christina/expressions/christina_happy.png",
  proud: "../renderer/assets/pet/christina/expressions/christina_proud.png",
  annoyed: "../renderer/assets/pet/christina/expressions/christina_annoyed.png",
  worried: "../renderer/assets/pet/christina/expressions/christina_worried.png",
  sleepy: "../renderer/assets/pet/christina/expressions/christina_sleepy.png",
});

const PET_MOOD_EXPRESSION_MAP = Object.freeze({
  neutral: "neutral",
  default: "neutral",
  idle: "neutral",
  calm: "neutral",
  focused: "focused",
  thinking: "focused",
  pending: "focused",
  listening: "focused",
  happy: "happy",
  joy: "happy",
  proud: "proud",
  smug: "proud",
  confident: "proud",
  annoyed: "annoyed",
  angry: "annoyed",
  upset: "annoyed",
  worried: "worried",
  error: "worried",
  offline: "worried",
  sad: "worried",
  anxious: "worried",
  sleepy: "sleepy",
  tired: "sleepy",
});

const PET_BUBBLE_STATE_EXPRESSIONS = Object.freeze({
  collapsed: "neutral",
  idle_default: "neutral",
  expanded: "neutral",
  handoff: "neutral",
  speaking: "neutral",
  thinking: "focused",
  composing: "neutral",
  empty_input: "annoyed",
  pending: "focused",
  success: "neutral",
  backend_offline: "worried",
  timeout: "sleepy",
  llm_local_error: "worried",
  fallback_mock: "proud",
  long_reply: "focused",
});

const BUBBLE_STATES = Object.freeze({
  collapsed: {
    expanded: false,
    source: "local",
    statusText: "local",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u9ede Full App \u6253\u5b57\uff0c\u543e\u6703\u5728\u9019\u88e1\u56de\u5634\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  idle_default: {
    expanded: true,
    source: "local",
    statusText: "idle",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: PET_IDLE_REPLY,
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  expanded: {
    expanded: true,
    source: "local",
    statusText: "local",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u54fc\uff0c\u6c5d\u8981\u543e\u8aaa\u8a71\uff0c\u5c31\u53bb Full App \u4e0b\u4ee4\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  handoff: {
    expanded: true,
    source: "local",
    statusText: "full app handoff",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: PET_HANDOFF_REPLY,
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  speaking: {
    expanded: true,
    source: "local",
    statusText: "local reply",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u543e\u5728\u9019\u88e1\u56de\u61c9\u6c5d\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  thinking: {
    expanded: true,
    source: "local",
    statusText: "thinking",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u543e\u6b63\u5728\u60f3\uff0c\u5225\u50ac\u3002",
    inputDisabled: true,
    sendDisabled: true,
    inputPlaceholder: "Thinking...",
  },
  composing: {
    expanded: true,
    source: "local",
    statusText: "dev composing",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u958b Full App \u6253\u5b57\u624d\u50cf\u6a23\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  empty_input: {
    expanded: true,
    source: "local",
    statusText: "empty input",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u4ec0\u9ebc\u90fd\u6c92\u8aaa\uff0c\u6c5d\u8981\u543e\u56de\u4ec0\u9ebc\uff1f",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  pending: {
    expanded: true,
    source: "local",
    statusText: "thinking",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u543e\u6b63\u5728\u60f3\uff0c\u5225\u50ac\u3002",
    inputDisabled: true,
    sendDisabled: true,
    inputPlaceholder: "Thinking...",
  },
  success: {
    expanded: true,
    source: "local",
    statusText: "local reply",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u543e\u5728\u9019\u88e1\u56de\u61c9\u6c5d\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  backend_offline: {
    expanded: true,
    source: "backend_offline",
    statusText: "backend offline",
    message: "\u5f8c\u7aef\u4f3c\u4e4e\u4e0d\u5728\uff0c\u6c5d\u5148\u53bb Full App \u628a\u5b83\u53eb\u9192\u3002",
    response: "\u543e\u7684\u9b54\u529b\u66ab\u6642\u5361\u4f4f\u4e86\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  timeout: {
    expanded: true,
    source: "timeout",
    statusText: "local timeout",
    message: "\u53bb Full App \u67e5\u770b\u672c\u5730\u6a21\u578b\u6216 provider \u72c0\u614b\u3002",
    response: "\u672c\u5730\u6a21\u578b\u53ef\u80fd\u9084\u5728\u9192\u4f86\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  llm_local_error: {
    expanded: true,
    source: "llm_local_error",
    statusText: "local model error",
    message: "\u53bb Full App \u6aa2\u67e5\u672c\u5730\u6a21\u578b\u6216 provider \u72c0\u614b\u3002",
    response: "\u543e\u7684\u9b54\u529b\u66ab\u6642\u5361\u4f4f\u4e86\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  fallback_mock: {
    expanded: true,
    source: "mock",
    statusText: "mock fallback",
    message: "\u76ee\u524d\u4f86\u6e90\u70ba mock fallback\uff0cFull App \u4ecd\u662f\u4e3b\u8981\u8f38\u5165\u8655\u3002",
    response: "\u9019\u662f\u66ab\u6642\u56de\u61c9\uff0c\u5225\u592a\u5f97\u610f\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  long_reply: {
    expanded: true,
    source: "local",
    statusText: "long reply",
    message: PET_LONG_REPLY_HINT,
    response: "\u543e\u8aaa\u592a\u591a\u4e86\uff0c\u6c5d\u53bb Full App \u770b\u5b8c\u6574\u5167\u5bb9\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
});

function setText(element, value) {
  if (element) {
    element.textContent = value;
  }
}

function sanitizeBubbleDetailText(value) {
  if (typeof value !== "string") return "";
  const compact = value.replace(/\s+/g, " ").trim();
  const compactLower = compact.toLowerCase();
  if (
    !compact ||
    PET_UNSAFE_DETAIL_PATTERN.test(compact) ||
    PET_UNSAFE_DETAIL_TOKENS.some((token) => compactLower.includes(token))
  ) {
    return "";
  }
  if (compact.length <= PET_DETAIL_TEXT_LIMIT) return compact;
  return `${compact.slice(0, PET_DETAIL_TEXT_LIMIT - 3).trim()}...`;
}

function mergeDetailText(...values) {
  const unique = [];
  for (const value of values) {
    const safe = sanitizeBubbleDetailText(value);
    if (safe && !unique.includes(safe)) {
      unique.push(safe);
    }
  }
  return sanitizeBubbleDetailText(unique.join(" | "));
}

class PetChatTimeoutError extends Error {
  constructor() {
    super("Pet Bubble chat request timed out.");
    this.name = "PetChatTimeoutError";
  }
}

class PetChatResponseError extends Error {
  constructor() {
    super("Pet Bubble chat response was not usable.");
    this.name = "PetChatResponseError";
  }
}

function getPetBackendUrl(windowRef = typeof window !== "undefined" ? window : null) {
  const search = windowRef && windowRef.location ? windowRef.location.search || "" : "";
  const params = new URLSearchParams(search);
  return params.get("backend") || PET_BACKEND_DEFAULT_URL;
}

function hasOwnKey(objectRef, key) {
  return Object.prototype.hasOwnProperty.call(objectRef, key);
}

function expressionAssetForMood(mood) {
  const normalizedMood = typeof mood === "string" ? mood.trim().toLowerCase() : "";
  const mappedMood = hasOwnKey(PET_MOOD_EXPRESSION_MAP, normalizedMood)
    ? PET_MOOD_EXPRESSION_MAP[normalizedMood]
    : normalizedMood;
  const safeMood = hasOwnKey(CHRISTINA_EXPRESSION_ASSETS, mappedMood)
    ? mappedMood
    : PET_MODE_DEFAULTS.expression;

  return {
    mood: safeMood,
    assetPath: hasOwnKey(CHRISTINA_EXPRESSION_ASSETS, safeMood)
      ? CHRISTINA_EXPRESSION_ASSETS[safeMood]
      : PET_MODE_DEFAULTS.avatarSrc,
  };
}

function normalizePetMood(mood) {
  return expressionAssetForMood(mood).mood;
}

function setPetExpression(documentRef, mood) {
  const { mood: normalizedMood, assetPath } = expressionAssetForMood(mood);
  const avatarContainer = documentRef.getElementById("pet-avatar-container");
  const avatar = documentRef.getElementById("pet-avatar");
  // TASK-156: also stamp root so DevTools can verify expression without
  // hunting inside the avatar container.
  const root = documentRef.getElementById("pet-mode-root");

  if (avatarContainer) {
    avatarContainer.dataset.expression = normalizedMood;
  }

  if (root) {
    root.dataset.expression = normalizedMood;
  }

  if (avatar) {
    avatar.onerror = () => {
      if (
        normalizedMood !== PET_MODE_DEFAULTS.expression &&
        avatar.getAttribute("src") === assetPath
      ) {
        if (avatarContainer) {
          avatarContainer.dataset.expression = PET_MODE_DEFAULTS.expression;
        }
        avatar.setAttribute("src", PET_MODE_DEFAULTS.avatarSrc);
        avatar.setAttribute("alt", `Christina ${PET_MODE_DEFAULTS.expression} expression`);
      }
    };
    avatar.setAttribute("src", assetPath);
    avatar.setAttribute("alt", `Christina ${normalizedMood} expression`);
  }

  return normalizedMood;
}

function expressionForBubbleState(state, responseMood) {
  if ((state === "speaking" || state === "success") && responseMood) {
    return normalizePetMood(responseMood);
  }

  return PET_BUBBLE_STATE_EXPRESSIONS[state] || PET_MODE_DEFAULTS.expression;
}

function setPetExpressionForBubbleState(documentRef, state, options = {}) {
  return setPetExpression(documentRef, expressionForBubbleState(state, options.mood));
}

function sourceStatusLabel(source) {
  if (source === "llm_local") return "local";
  if (source === "mock") return "mock fallback";
  if (source === "llm_local_error") return "local model error";
  if (source === "backend_offline") return "backend offline";
  if (source === "timeout") return "local timeout";
  return source || "unknown source";
}

function isLongReply(reply) {
  return typeof reply === "string" && reply.length > PET_REPLY_LONG_THRESHOLD;
}

function truncatePetReply(reply, limit = PET_REPLY_PREVIEW_LIMIT) {
  if (typeof reply !== "string") return "";
  const normalized = reply.trim();
  if (normalized.length <= limit) return normalized;
  return `${normalized.slice(0, limit).trimEnd()}\u2026`;
}

function stateForChatSource(source, reply) {
  // TASK-157: thinking signal from Full App pre-fetch phase
  if (source === PET_THINKING_SOURCE) return "thinking";
  if (source === "llm_local_error") return "llm_local_error";
  if (source === "mock") return "fallback_mock";
  if (isLongReply(reply)) return "long_reply";
  return "speaking";
}

function responseForBubbleState(state, reply) {
  if (state === "long_reply") return truncatePetReply(reply);
  if (state === "llm_local_error") return BUBBLE_STATES.llm_local_error.response;
  return typeof reply === "string" && reply ? reply : getBubbleStateConfig(state).response;
}

function visibleReplyForSpeechPayload(payload = {}) {
  return typeof payload.reply === "string" ? payload.reply : "";
}

function detailMessageForBubbleState(state) {
  if (state === "long_reply") return PET_LONG_REPLY_HINT;
  if (state === "backend_offline") return "\u5f8c\u7aef\u4f3c\u4e4e\u4e0d\u5728\uff0c\u6c5d\u5148\u53bb Full App \u628a\u5b83\u53eb\u9192\u3002";
  if (state === "timeout") return "\u53bb Full App \u67e5\u770b\u672c\u5730\u6a21\u578b\u6216 provider \u72c0\u614b\u3002";
  if (state === "llm_local_error") return "\u53bb Full App \u6aa2\u67e5\u672c\u5730\u6a21\u578b\u6216 provider \u72c0\u614b\u3002";
  if (state === "fallback_mock") return "\u76ee\u524d\u4f86\u6e90\u70ba mock fallback\uff0cFull App \u4ecd\u662f\u4e3b\u8981\u8f38\u5165\u8655\u3002";
  return PET_MODE_DEFAULTS.bubbleMessage;
}

function detailOptionsForSpeechPayload(payload = {}, state = "speaking", source = "unknown") {
  const sourceKnown = typeof source === "string" && source.trim() && source !== "unknown";
  const statusText = sanitizeBubbleDetailText(payload.status) ||
    (sourceKnown ? sanitizeBubbleDetailText(sourceStatusLabel(source)) : "");
  const message = mergeDetailText(
    payload.helper,
    payload.status,
    payload.details,
    payload.debug,
    sourceKnown ? detailMessageForBubbleState(state) : ""
  );

  return {
    statusText,
    message,
    detailsAvailable: Boolean(statusText || message),
  };
}

function createPetPresenceState() {
  return {
    recentReply: null,
    recentTimer: null,
    handoffActive: false,
    handoffTimer: null,
    timerApi: null,
    idleRotationTimer: null,  // TASK-158
    lastIdleLineIdx: -1,       // TASK-158
    idleCooldownUntil: 0,      // TASK-159
    quietMode: false,           // TASK-160
    clickThrough: false,        // TASK-166D
  };
}

function getPetPresenceState(documentRef) {
  if (!documentRef) return createPetPresenceState();

  if (petPresenceStates) {
    let state = petPresenceStates.get(documentRef);
    if (!state) {
      state = createPetPresenceState();
      petPresenceStates.set(documentRef, state);
    }
    return state;
  }

  if (!fallbackPetPresenceState || fallbackPetPresenceState.documentRef !== documentRef) {
    fallbackPetPresenceState = {
      documentRef,
      state: createPetPresenceState(),
    };
  }
  return fallbackPetPresenceState.state;
}

function getPresenceTimerApi(options = {}, presenceState = null) {
  if (options && options.timerApi) return options.timerApi;
  if (presenceState && presenceState.timerApi) return presenceState.timerApi;
  return globalThis;
}

function getPresenceNow(timerApi = globalThis) {
  if (timerApi && typeof timerApi.now === "number") return timerApi.now;
  return Date.now();
}

function clearPresenceTimer(presenceState, timerName, timerApi = globalThis) {
  const timer = presenceState[timerName];
  if (timer && timerApi && typeof timerApi.clearTimeout === "function") {
    timerApi.clearTimeout(timer);
  }
  presenceState[timerName] = null;
}

function schedulePresenceTimer(timerApi, callback, delayMs) {
  const timer = timerApi.setTimeout(callback, delayMs);
  if (timer && typeof timer.unref === "function") {
    timer.unref();
  }
  return timer;
}

// TASK-159: record a cooldown deadline — idle rotation will not fire before this time
function setIdleCooldown(presenceState, timerApi, durationMs) {
  const now = getPresenceNow(timerApi || globalThis);
  presenceState.idleCooldownUntil = now + durationMs;
}

// TASK-160: read quiet mode flag safely (unknown/invalid → false)
function getQuietMode(presenceState) {
  return presenceState.quietMode === true;
}

// TASK-160: set quiet mode — true suppresses idle rotation, false resumes it.
// Any non-true value normalises to false (fail-quiet/safe on unknown input).
function setQuietMode(documentRef, presenceState, value, timerApi) {
  const api = timerApi || globalThis;
  const nextMode = value === true;  // TASK-160: normalise — non-true → false
  presenceState.quietMode = nextMode;
  // TASK-166C: write data-quiet-mode on root so CSS can suppress #pet-hint when quiet
  const root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  if (root) {
    root.dataset.quietMode = nextMode ? "true" : "false";
  }
  const bubble = documentRef ? documentRef.getElementById("pet-bubble") : null;
  const currentState = bubble ? bubble.dataset.state : null;
  if (nextMode) {
    // turning ON: cancel rotation and collapse idle bubble (TASK-160 fix)
    stopIdleRotation(presenceState, api);
    if (currentState === "idle_default" || currentState === "collapsed") {
      setBubbleState(documentRef, "collapsed");
    }
  } else {
    // turning OFF: restore idle and restart rotation with cooldown (TASK-160 fix)
    if (currentState === "collapsed" || currentState === "idle_default") {
      setBubbleState(documentRef, "idle_default");
      setIdleCooldown(presenceState, api, PET_IDLE_COOLDOWN_MS);
      startIdleRotation(documentRef, presenceState, api);
    }
    // non-idle states (speaking/thinking/error): rotation resumes naturally on state clear
  }
  // update menu button label/state if present
  const menuBtn = documentRef ? documentRef.getElementById("pet-menu-quiet-mode") : null;
  if (menuBtn) {
    menuBtn.setAttribute("aria-pressed", nextMode ? "true" : "false");
    setText(menuBtn, nextMode ? "Quiet Mode: On" : "Quiet Mode: Off");
  }
}

// TASK-160: document-level quiet mode reader (for tests and menu rendering)
function getPetQuietMode(documentRef) {
  return getQuietMode(getPetPresenceState(documentRef));
}

// TASK-160: document-level quiet mode setter
function setPetQuietMode(documentRef, value, timerApi) {
  const presenceState = getPetPresenceState(documentRef);
  const api = timerApi || getPresenceTimerApi({}, presenceState);
  setQuietMode(documentRef, presenceState, value, api);
}

// TASK-160 fix: when quiet mode ON, collapse bubble instead of showing idle text
function setIdleQuietBubble(documentRef, presenceState) {
  if (presenceState.quietMode === true) {
    return setBubbleState(documentRef, "collapsed");
  }
  return setBubbleState(documentRef, "idle_default");
}

// TASK-166D: read click-through flag safely
function getClickThrough(presenceState) {
  return presenceState.clickThrough === true;
}

// TASK-166D: set click-through — true passes clicks through, false restores normal.
// Any non-true value normalises to false (fail-safe on unknown input).
// Session-local only — NOT persisted; default OFF so user is never stuck.
// TASK-166E click-fix2: also manages the CT recovery strip visibility and
// closes the direct input panel if CT turns ON while it is open.
function setClickThrough(documentRef, presenceState, value) {
  const next = value === true;
  presenceState.clickThrough = next;
  const root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  if (root) {
    root.dataset.clickThrough = next ? "true" : "false";
  }
  // TASK-166E click-fix2: show CT recovery strip only while CT is ON so the
  // user can hover the top of the window to exit click-through mode.
  var recoveryStrip = documentRef ? documentRef.getElementById("pet-ct-recovery-strip") : null;
  if (recoveryStrip) {
    recoveryStrip.hidden = !next;
  }
  // TASK-166E click-fix2: if CT is turning ON and the direct input panel is
  // currently open, close it — a visible-but-unreachable panel is confusing.
  if (next && isPetDirectInputOpen(documentRef)) {
    closePetDirectInput(documentRef);
  }
  // TASK-167A: if CT is turning ON and voice recording is active, cancel it.
  if (next && isPetRecordingActive(documentRef)) {
    cancelPetVoiceRecording(documentRef);
  }
  const menuBtn = documentRef ? documentRef.getElementById("pet-menu-click-through") : null;
  if (menuBtn) {
    menuBtn.setAttribute("aria-pressed", next ? "true" : "false");
    setText(menuBtn, next ? "Click-through: On" : "Click-through: Off");
  }
}

// TASK-166D: document-level click-through reader
function getPetClickThrough(documentRef) {
  return getClickThrough(getPetPresenceState(documentRef));
}

// TASK-166D: document-level click-through setter
function setPetClickThrough(documentRef, value) {
  const presenceState = getPetPresenceState(documentRef);
  setClickThrough(documentRef, presenceState, value);
}

// TASK-166D: force click-through OFF — called on menu open, details open, reset/hide.
// Calls the narrow IPC bridge so main process reflects the state.
// TASK-166E click-fix: returns the IPC Promise (or null) so async callers can await it.
function forceClickThroughOff(documentRef) {
  if (!getPetClickThrough(documentRef)) return null;  // already OFF, no-op
  setPetClickThrough(documentRef, false);
  var api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (api && typeof api.setClickThrough === "function") {
    return api.setClickThrough(false);  // TASK-166E click-fix: return Promise so openPetDirectInput can await
  }
  return null;
}



// ── TASK-166E: Pet Direct Text Input Panel ────────────────────────────────────

// TASK-166E: true when the direct input panel is visible and accepting input
function isPetDirectInputOpen(documentRef) {
  var panel = documentRef ? documentRef.getElementById("pet-direct-input-panel") : null;
  return Boolean(panel && panel.dataset.state === "open");
}

// TASK-166E: show the compact chat input panel.
// TASK-166E click-fix: async so we can await the IPC roundtrip that calls
// setIgnoreMouseEvents(false) + petWindow.focus() in main process before
// showing and focusing the input.  Without this, the panel is visible but
// unreachable — the window is still in click-through mode and has lost OS
// focus because the triggering click was forwarded through to the app behind.
async function openPetDirectInput(documentRef) {
  // TASK-167A: mutual exclusion — opening text input cancels any active voice recording.
  if (isPetRecordingActive(documentRef)) {
    cancelPetVoiceRecording(documentRef);
  }
  // Step 1: force CT OFF and await the IPC so main process processes it first.
  var ctPromise = forceClickThroughOff(documentRef);  // TASK-166D: must be OFF before input appears
  if (ctPromise && typeof ctPromise.then === "function") {
    try {
      await ctPromise;
    } catch (_e) {
      // IPC failure: fail safe — renderer state already set to OFF.
      // The user can still use the recovery strip to exit click-through.
    }
  }
  // Step 2: show panel and focus input (only after IPC has resolved).
  var panel = documentRef ? documentRef.getElementById("pet-direct-input-panel") : null;
  if (!panel) return;
  panel.dataset.state = "open";
  panel.hidden = false;
  var field = documentRef ? documentRef.getElementById("pet-direct-input-field") : null;
  if (field && typeof field.focus === "function") {
    field.focus();
  }
}

// TASK-166E: hide the input panel and clear the draft text.
function closePetDirectInput(documentRef) {
  var panel = documentRef ? documentRef.getElementById("pet-direct-input-panel") : null;
  if (!panel) return;
  panel.dataset.state = "closed";
  panel.hidden = true;
  var field = documentRef ? documentRef.getElementById("pet-direct-input-field") : null;
  if (field) {
    field.value = "";
  }
}

// ── TASK-167A: Pet Voice / Mic Push-to-talk ────────────────────────────────────

// TASK-167A: true when data-recording="true" is set on #pet-mode-root
function isPetRecordingActive(documentRef) {
  var root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  return Boolean(root && root.dataset.recording === "true");
}

// TASK-167A: manage data-recording attribute, indicator visibility, mic aria-pressed.
// presenceState.voiceRecordingTimer holds the active timeout ID (or null).
function setRecordingState(documentRef, presenceState, active) {
  var root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  if (root) {
    root.dataset.recording = active ? "true" : "false";
  }
  var indicator = documentRef ? documentRef.getElementById("pet-recording-indicator") : null;
  if (indicator) {
    indicator.hidden = !active;
  }
  var micBtn = documentRef ? documentRef.getElementById("pet-mic-hook") : null;
  if (micBtn) {
    micBtn.setAttribute("aria-pressed", active ? "true" : "false");
  }
  if (!active) {
    // Clear timeout when recording is being stopped or cancelled
    if (presenceState && presenceState.voiceRecordingTimer != null) {
      clearTimeout(presenceState.voiceRecordingTimer);
      presenceState.voiceRecordingTimer = null;
    }
    // Clear the MediaRecorder reference
    if (presenceState) {
      presenceState.voiceMediaRecorder = null;
    }
  }
}

// TASK-167B: true when data-transcribing="true" is set on #pet-mode-root.
function isTranscribingActive(documentRef) {
  var root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  return Boolean(root && root.dataset.transcribing === "true");
}

// TASK-167B: manage data-transcribing attribute and transcribing indicator visibility.
// presenceState.voiceTranscribingTimeout is set externally by the STT race timeout.
function setTranscribingState(documentRef, presenceState, active) {
  var root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  if (root) {
    root.dataset.transcribing = active ? "true" : "false";
  }
  var indicator = documentRef ? documentRef.getElementById("pet-transcribing-indicator") : null;
  if (indicator) {
    indicator.hidden = !active;
  }
  if (!active && presenceState && presenceState.voiceTranscribingTimeout != null) {
    clearTimeout(presenceState.voiceTranscribingTimeout);
    presenceState.voiceTranscribingTimeout = null;
  }
}

// TASK-167B: transcribe an audio Blob via the IPC STT bridge.
// Returns:
//   null          — IPC bridge unavailable (smoke/dev env) → caller: no-op
//   ""            — empty/silent audio → caller: show empty-audio message
//   "some text"   — successful transcript → caller: store + show in bubble
// Throws:
//   Error("stt_unavailable") — backend Whisper not installed
//   Error("stt_timeout")     — STT did not respond within PET_STT_TIMEOUT_MS
//   Error("stt_offline")     — backend unreachable
//   Error("stt_error")       — any other backend error
//
// Constraints (TASK-167B scope):
//   - Does NOT call /chat or sendPetChatMessage.
//   - Does NOT fetch() directly — routes through narrow IPC bridge only.
//   - Does NOT persist audio.
//   - No fake/mock transcription — real bridge or null.
async function transcribeAudioBlob(blob) {
  // Guard: IPC bridge must be present (not available in Node.js smoke test env)
  var api = (typeof window !== "undefined" && window !== null) ? window.dragonPet : null;
  if (!api || typeof api.transcribeAudio !== "function") {
    // STT bridge not wired (dev / smoke env) — silent no-op
    return null;
  }

  // Convert Blob to ArrayBuffer for IPC transport
  var arrayBuffer;
  try {
    arrayBuffer = await blob.arrayBuffer();
  } catch (_e) {
    throw new Error("stt_error");
  }

  // Race IPC call against hard timeout
  var timeoutId;
  var timeoutPromise = new Promise(function (_, reject) {
    timeoutId = setTimeout(function () {
      reject(new Error("stt_timeout"));
    }, PET_STT_TIMEOUT_MS);
  });

  var result;
  try {
    result = await Promise.race([api.transcribeAudio(arrayBuffer), timeoutPromise]);
  } catch (err) {
    clearTimeout(timeoutId);
    // Propagate named errors; wrap unknown ones
    if (err && (err.message === "stt_timeout" || err.message === "stt_offline")) {
      throw err;
    }
    throw new Error("stt_error");
  }
  clearTimeout(timeoutId);

  // Normalise backend response
  if (!result || typeof result !== "object") {
    throw new Error("stt_error");
  }
  var status = result.status || "error";
  if (status === "unavailable") throw new Error("stt_unavailable");
  if (status === "offline")     throw new Error("stt_offline");
  if (status === "error")       throw new Error("stt_error");
  if (status === "empty" || !result.transcript) return "";
  return String(result.transcript);
}

// TASK-167B: shared helper — build Blob from recorded chunks and run STT transcription.
// Must be called AFTER the recorder's final dataavailable event has fired (i.e. from
// the recorder's stop event, or when the recorder is already inactive).
// TASK-168B: returns true if window.speechSynthesis is available in this context.
function isPetTtsAvailable() {
  return typeof window !== "undefined" && !!window.speechSynthesis;
}

// TASK-168B: set or clear the speaking state on #pet-mode-root.
// Shows / hides the speaking indicator and stop button via data-speaking attribute.
// TASK-168B-FIX: also toggle indicator.hidden so the !important CSS guard is lifted,
// matching the same pattern used by setRecordingState / setTranscribingState.
function setSpeakingState(documentRef, active) {
  petSpeakingActive = !!active;
  var root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  if (root) {
    if (active) {
      root.dataset.speaking = "true";
    } else {
      delete root.dataset.speaking;
    }
  }
  var indicator = documentRef ? documentRef.getElementById("pet-speaking-indicator") : null;
  if (indicator) {
    indicator.hidden = !active;
  }
}

// TASK-168B: cancel any active TTS speech and clear speaking state.
// Safe to call when nothing is playing (no-op).
function stopPetSpeech(documentRef) {
  if (isPetTtsAvailable()) {
    try { window.speechSynthesis.cancel(); } catch (_e) { /* ignore */ }
  }
  setSpeakingState(documentRef, false);
}

// TASK-168B: speak a final assistant reply if TTS is enabled.
// Only speaks for final reply states ("speaking", "long_reply").
// Empty reply, thinking state, error states, recording/transcribing → no-op.
// Truncates to PET_TTS_MAX_CHARS; full text remains visible in bubble.
function speakPetReply(documentRef, reply, state) {
  // Guard: TTS must be enabled
  if (!petTtsEnabled) return;
  // Guard: SpeechSynthesis must be available
  if (!isPetTtsAvailable()) return;
  // Guard: only speak final reply states
  if (state !== "speaking" && state !== "long_reply") return;
  // Guard: do not speak while recording or transcribing (feedback loop prevention)
  if (isPetRecordingActive(documentRef)) return;
  if (isTranscribingActive(documentRef)) return;
  // Guard: empty or non-string reply
  var text = typeof reply === "string" ? reply.trim() : "";
  if (!text) return;
  // Truncate to TTS limit
  if (text.length > PET_TTS_MAX_CHARS) {
    text = text.slice(0, PET_TTS_MAX_CHARS);
  }
  // Cancel any in-progress speech before starting new utterance
  stopPetSpeech(documentRef);
  try {
    var utterance = new window.SpeechSynthesisUtterance(text);
    // TASK-169: apply voice selection and speech controls (all values clamped)
    var _voiceObj = getPetTtsVoiceObject();
    if (_voiceObj) { utterance.voice = _voiceObj; }
    utterance.rate   = clampTtsValue(petTtsRate,   PET_TTS_RATE_MIN,  PET_TTS_RATE_MAX,  PET_TTS_RATE_DEF);
    utterance.pitch  = clampTtsValue(petTtsPitch,  PET_TTS_PITCH_MIN, PET_TTS_PITCH_MAX, PET_TTS_PITCH_DEF);
    utterance.volume = clampTtsValue(petTtsVolume, PET_TTS_VOL_MIN,   PET_TTS_VOL_MAX,   PET_TTS_VOL_DEF);
    utterance.onstart = function () { setSpeakingState(documentRef, true); };
    utterance.onend = function () { setSpeakingState(documentRef, false); };
    utterance.onerror = function () { setSpeakingState(documentRef, false); };
    window.speechSynthesis.speak(utterance);
  } catch (_e) {
    // SpeechSynthesis failure — clear state silently, no Pet Bubble error
    setSpeakingState(documentRef, false);
  }
}

// TASK-168B: toggle TTS on/off. Stops any active speech when disabling.
function togglePetTts(documentRef) {
  petTtsEnabled = !petTtsEnabled;
  if (!petTtsEnabled) stopPetSpeech(documentRef);
  var btn = documentRef ? documentRef.getElementById("pet-menu-tts") : null;
  if (btn) {
    btn.setAttribute("aria-pressed", petTtsEnabled ? "true" : "false");
    btn.textContent = petTtsEnabled ? "語音播放: 開" : "語音播放: 關";
  }
  return petTtsEnabled;
}

// ── TASK-169: TTS Voice Selection / Speech Controls ───────────────────────────

// TASK-169: clamp numeric value within [min, max]; return def on NaN/invalid.
function clampTtsValue(value, min, max, def) {
  var n = parseFloat(value);
  if (isNaN(n)) return def;
  return Math.max(min, Math.min(max, n));
}

// TASK-169: load TTS settings from localStorage; validate and clamp.
// Falls back to safe defaults on any failure or unavailability.
function loadTtsSettings() {
  var voice = "";
  var rate  = PET_TTS_RATE_DEF;
  var pitch = PET_TTS_PITCH_DEF;
  var vol   = PET_TTS_VOL_DEF;
  try {
    if (typeof window !== "undefined" && window.localStorage) {
      var rv = window.localStorage.getItem(PET_TTS_LS_VOICE);
      if (typeof rv === "string") { voice = rv; }
      var rr = window.localStorage.getItem(PET_TTS_LS_RATE);
      if (rr !== null) { rate  = clampTtsValue(rr, PET_TTS_RATE_MIN,  PET_TTS_RATE_MAX,  PET_TTS_RATE_DEF); }
      var rp = window.localStorage.getItem(PET_TTS_LS_PITCH);
      if (rp !== null) { pitch = clampTtsValue(rp, PET_TTS_PITCH_MIN, PET_TTS_PITCH_MAX, PET_TTS_PITCH_DEF); }
      var rvol = window.localStorage.getItem(PET_TTS_LS_VOLUME);
      if (rvol !== null) { vol = clampTtsValue(rvol, PET_TTS_VOL_MIN, PET_TTS_VOL_MAX, PET_TTS_VOL_DEF); }
    }
  } catch (_e) { /* localStorage unavailable — use in-memory defaults */ }
  return { voice: voice, rate: rate, pitch: pitch, volume: vol };
}

// TASK-169: persist current TTS settings to localStorage. Silent no-op on failure.
function saveTtsSettings() {
  try {
    if (typeof window !== "undefined" && window.localStorage) {
      window.localStorage.setItem(PET_TTS_LS_VOICE,  petTtsVoiceName);
      window.localStorage.setItem(PET_TTS_LS_RATE,   String(petTtsRate));
      window.localStorage.setItem(PET_TTS_LS_PITCH,  String(petTtsPitch));
      window.localStorage.setItem(PET_TTS_LS_VOLUME, String(petTtsVolume));
    }
  } catch (_e) { /* ignore */ }
}

// TASK-169: look up the selected voice object from speechSynthesis.getVoices().
// Returns null if not found or voice list empty (caller uses browser default).
function getPetTtsVoiceObject() {
  if (!isPetTtsAvailable() || !petTtsVoiceName) return null;
  try {
    var voices = window.speechSynthesis.getVoices();
    for (var i = 0; i < voices.length; i++) {
      if (voices[i].name === petTtsVoiceName) return voices[i];
    }
  } catch (_e) {}
  return null; // selected voice gone — use browser default
}

// TASK-169: populate voice selector with available voices.
// Safe when selector is absent or voice list is empty.
function populatePetVoiceSelector(documentRef) {
  if (!isPetTtsAvailable()) return;
  var sel = documentRef ? documentRef.getElementById("pet-tts-voice-select") : null;
  if (!sel) return;
  try {
    var voices = window.speechSynthesis.getVoices();
    if (!voices || voices.length === 0) return; // wait for onvoiceschanged
    sel.innerHTML = "";
    var defOpt = documentRef.createElement ? documentRef.createElement("option") : null;
    if (defOpt) {
      defOpt.value = "";
      defOpt.textContent = "系統預設"; // 系統預設
      sel.appendChild(defOpt);
    }
    var found = false;
    for (var i = 0; i < voices.length; i++) {
      var v = voices[i];
      var opt = documentRef.createElement ? documentRef.createElement("option") : null;
      if (!opt) continue;
      opt.value = v.name;
      var label = v.name + " (" + v.lang + ")";
      if (label.length > 44) { label = label.slice(0, 41) + "..."; }
      opt.textContent = label;
      if (v.name === petTtsVoiceName) { opt.selected = true; found = true; }
      sel.appendChild(opt);
    }
    // If stored voice is missing from the current list, reset to default
    if (petTtsVoiceName && !found) {
      petTtsVoiceName = "";
      sel.value = "";
    }
  } catch (_e) {}
}

// TASK-169: sync slider inputs and value labels to current in-memory state.
function syncTtsControlDisplays(documentRef) {
  var rateVal   = documentRef ? documentRef.getElementById("pet-tts-rate-val")   : null;
  var pitchVal  = documentRef ? documentRef.getElementById("pet-tts-pitch-val")  : null;
  var volVal    = documentRef ? documentRef.getElementById("pet-tts-volume-val") : null;
  var rateIn    = documentRef ? documentRef.getElementById("pet-tts-rate")    : null;
  var pitchIn   = documentRef ? documentRef.getElementById("pet-tts-pitch")   : null;
  var volIn     = documentRef ? documentRef.getElementById("pet-tts-volume")  : null;
  if (rateVal)  rateVal.textContent  = petTtsRate.toFixed(2);
  if (pitchVal) pitchVal.textContent = petTtsPitch.toFixed(2);
  if (volVal)   volVal.textContent   = petTtsVolume.toFixed(2);
  if (rateIn)   rateIn.value   = String(petTtsRate);
  if (pitchIn)  pitchIn.value  = String(petTtsPitch);
  if (volIn)    volIn.value    = String(petTtsVolume);
}

// TASK-169: reset rate/pitch/volume to safe defaults; save + update UI.
// Voice selection is not reset (user may prefer to keep their voice).
function resetTtsControls(documentRef) {
  petTtsRate   = PET_TTS_RATE_DEF;
  petTtsPitch  = PET_TTS_PITCH_DEF;
  petTtsVolume = PET_TTS_VOL_DEF;
  saveTtsSettings();
  syncTtsControlDisplays(documentRef);
}

async function handlePetVoiceChatSend(documentRef, transcript, options) {
  if (petChatPending) return null;
  forceClickThroughOff(documentRef);
  closePetDirectInput(documentRef);
  petChatPending = true;
  setBubbleState(documentRef, "thinking");
  try {
    var data = await sendPetChatMessage(transcript, options || {});
    var nextState = stateForChatSource(data.source, data.reply);
    var statusText = sourceStatusLabel(data.source);
    var bubbleOptions = {
      source: data.source,
      statusText: statusText,
      message: detailMessageForBubbleState(nextState),
      response: responseForBubbleState(nextState, data.reply),
      mood: data.mood,
    };
    setBubbleState(documentRef, nextState, bubbleOptions);
    rememberRecentPetReply(documentRef, nextState, bubbleOptions, options || {});
    // TASK-168B: speak final reply if TTS enabled
    speakPetReply(documentRef, data.reply, nextState);
    return data;
  } catch (error) {
    var errorState = "llm_local_error";
    if (isPetChatTimeoutError(error)) errorState = "timeout";
    else if (isFetchNetworkError(error)) errorState = "backend_offline";
    setBubbleState(documentRef, errorState);
    return null;
  } finally {
    petChatPending = false;
  }
}

function _petSttTranscribeChunks(documentRef, presenceState, chunks, mimeType) {
  var audioBlob = null;
  try {
    audioBlob = new Blob(chunks || [], { type: mimeType || "audio/webm" });
  } catch (_e) {
    // Blob construction failure — exit transcribing state silently
    setTranscribingState(documentRef, presenceState, false);
    return;
  }

  transcribeAudioBlob(audioBlob).then(function (transcript) {
    setTranscribingState(documentRef, presenceState, false);

    if (transcript === null) {
      // IPC bridge not available (smoke / dev env) — silent no-op
      return;
    }

    if (!transcript) {
      setBubbleState(documentRef, "idle_default");
      var emptyEl = documentRef ? documentRef.getElementById("pet-bubble-response") : null;
      if (emptyEl) setText(emptyEl, PET_STT_EMPTY_MSG);
      return;
    }

    // TASK-167C: validate and auto-send to /chat.
    // Clear voiceTranscript — no longer persisted after handoff.
    if (presenceState) { presenceState.voiceTranscript = null; }
    var trimmed = transcript.trim();
    if (trimmed.length > PET_VOICE_CHAT_MAX_CHARS) {
      setBubbleState(documentRef, "idle_default");
      var longEl = documentRef ? documentRef.getElementById("pet-bubble-response") : null;
      if (longEl) setText(longEl, PET_VOICE_TRANSCRIPT_TOO_LONG_MSG);
      return;
    }
    // Auto-send valid transcript — no confirmation step (TASK-167C)
    handlePetVoiceChatSend(documentRef, trimmed, {});

  }).catch(function (err) {
    setTranscribingState(documentRef, presenceState, false);
    var errCode = (err && err.message) ? err.message : "";
    var errMsg;
    if (errCode === "stt_unavailable") {
      errMsg = PET_STT_UNAVAILABLE_MSG;
    } else if (errCode === "stt_timeout") {
      errMsg = PET_STT_TIMEOUT_MSG;
    } else if (errCode === "stt_offline") {
      errMsg = PET_STT_OFFLINE_MSG;
    } else {
      errMsg = PET_STT_ERROR_MSG;
    }
    setBubbleState(documentRef, "idle_default");
    var errEl = documentRef ? documentRef.getElementById("pet-bubble-response") : null;
    if (errEl) setText(errEl, errMsg);
  });
}

// TASK-167A/167B: stop recording and hand the audio to STT transcription.
// Uses a flag (voiceStopAndTranscribe) so the recorder's stop event — which fires
// AFTER the final dataavailable event — is the one that builds the Blob and calls STT.
// This is the correct async pattern; building the Blob synchronously right after
// recorder.stop() would race dataavailable and produce an empty Blob.
// Does NOT forward the transcript to /chat — that is deferred to TASK-167C.
function stopPetVoiceRecording(documentRef) {
  var presenceState = getPetPresenceState(documentRef);
  var recorder = presenceState ? presenceState.voiceMediaRecorder : null;
  var mimeType  = (recorder && recorder.mimeType) ? recorder.mimeType : "audio/webm";

  setRecordingState(documentRef, presenceState, false);

  if (recorder && recorder.state !== "inactive") {
    // Recorder still running: flag it so the stop event triggers transcription.
    if (presenceState) presenceState.voiceStopAndTranscribe = true;
    setTranscribingState(documentRef, presenceState, true);
    try {
      recorder.stop();
    } catch (_e) {
      if (presenceState) presenceState.voiceStopAndTranscribe = false;
      setTranscribingState(documentRef, presenceState, false);
    }
  } else {
    // Recorder already inactive — transcribe immediately from saved chunks.
    var savedChunks = (presenceState && presenceState.voiceChunks) ? presenceState.voiceChunks : [];
    setTranscribingState(documentRef, presenceState, true);
    _petSttTranscribeChunks(documentRef, presenceState, savedChunks, mimeType);
  }
}

// TASK-167A: cancel an in-progress recording, discarding the audio Blob.
// Safe to call when no recording is active (no-op).
function cancelPetVoiceRecording(documentRef) {
  var presenceState = getPetPresenceState(documentRef);
  var recorder = presenceState ? presenceState.voiceMediaRecorder : null;
  if (recorder && recorder.state !== "inactive") {
    try { recorder.stop(); } catch (_e) { /* ignore */ }
  }
  setRecordingState(documentRef, presenceState, false);
  // Release microphone track if stream is still held
  if (presenceState && presenceState.voiceMicStream) {
    try {
      presenceState.voiceMicStream.getTracks().forEach(function (t) { t.stop(); });
    } catch (_e) { /* ignore */ }
    presenceState.voiceMicStream = null;
  }
}

// TASK-167A: open voice recording.
// Toggle-to-record: calling while already recording → cancel (stop, discard).
// 1. If already recording → cancel and return.
// 2. Force CT OFF (same async pattern as openPetDirectInput / TASK-166E).
// 3. Close text input if open (mutual exclusion).
// 4. getUserMedia({ audio: true }) → show recording state.
// 5. MediaRecorder collects chunks; on stop → stopPetVoiceRecording.
// 6. Hard timeout: PET_RECORDING_MAX_MS → auto-stop.
// 7. Clean pet bubble fallbacks for all error cases — no stack traces.
async function openPetVoiceRecording(documentRef) {
  // TASK-168B: cancel any active TTS speech before recording starts
  // (prevents microphone feedback from speaker output)
  stopPetSpeech(documentRef);
  // Toggle: if already recording, stop and transcribe.
  // The separate cancel (✕) button discards without transcribing.
  if (isPetRecordingActive(documentRef)) {
    stopPetVoiceRecording(documentRef);
    return;
  }

  // TASK-167B: if STT transcription is in progress, ignore new recording requests
  if (isTranscribingActive(documentRef)) {
    return;
  }

  // Force CT OFF before recording starts (same pattern as TASK-166E)
  var ctPromise = forceClickThroughOff(documentRef);
  if (ctPromise && typeof ctPromise.then === "function") {
    try { await ctPromise; } catch (_e) { /* IPC failure — renderer state already OFF */ }
  }

  // Mutual exclusion: close text input if open
  if (isPetDirectInputOpen(documentRef)) {
    closePetDirectInput(documentRef);
  }

  // Check MediaRecorder availability (not available in all environments)
  if (typeof MediaRecorder === "undefined") {
    setBubbleState(documentRef, "backend_offline");
    var petBubbleResp = documentRef ? documentRef.getElementById("pet-bubble-response") : null;
    if (petBubbleResp) setText(petBubbleResp, PET_VOICE_UNSUPPORTED_MSG);
    return;
  }

  // Request microphone access
  var stream;
  try {
    var navObj = typeof navigator !== "undefined" ? navigator : null;
    if (!navObj || !navObj.mediaDevices || typeof navObj.mediaDevices.getUserMedia !== "function") {
      throw new Error("no_mic");
    }
    stream = await navObj.mediaDevices.getUserMedia({ audio: true });
  } catch (err) {
    var errName = err && err.name ? err.name : "";
    var errMsg  = err && err.message ? err.message : "";
    var friendlyMsg;
    if (errName === "NotAllowedError" || errName === "PermissionDeniedError") {
      friendlyMsg = PET_VOICE_MIC_DENIED_MSG;
    } else if (
      errName === "NotFoundError" ||
      errName === "DevicesNotFoundError" ||
      errMsg === "no_mic"
    ) {
      friendlyMsg = PET_VOICE_NO_MIC_MSG;
    } else {
      friendlyMsg = PET_VOICE_UNSUPPORTED_MSG;
    }
    setBubbleState(documentRef, "backend_offline");
    var bubbleEl = documentRef ? documentRef.getElementById("pet-bubble-response") : null;
    if (bubbleEl) setText(bubbleEl, friendlyMsg);
    return;
  }

  // Build MediaRecorder — prefer webm/opus for future Whisper compatibility (TASK-167B)
  var mimeType = "audio/webm;codecs=opus";
  if (typeof MediaRecorder.isTypeSupported === "function" && !MediaRecorder.isTypeSupported(mimeType)) {
    mimeType = "audio/webm";
    if (typeof MediaRecorder.isTypeSupported === "function" && !MediaRecorder.isTypeSupported(mimeType)) {
      mimeType = "";  // let the browser pick
    }
  }
  var recorder;
  try {
    recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
  } catch (_e) {
    // Stop stream tracks before bailing
    try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (_e2) { /* ignore */ }
    setBubbleState(documentRef, "backend_offline");
    var bubbleEl2 = documentRef ? documentRef.getElementById("pet-bubble-response") : null;
    if (bubbleEl2) setText(bubbleEl2, PET_VOICE_UNSUPPORTED_MSG);
    return;
  }

  // Store stream + recorder in presence state for cancel/stop
  var presenceState = getPetPresenceState(documentRef);
  if (presenceState) {
    presenceState.voiceMicStream         = stream;
    presenceState.voiceMediaRecorder     = recorder;
    presenceState.voiceStopAndTranscribe = false;  // TASK-167B: set true by stopPetVoiceRecording
  }

  // TASK-167B: store chunks reference in presenceState so stopPetVoiceRecording can reach it
  var chunks = [];
  if (presenceState) presenceState.voiceChunks = chunks;

  recorder.addEventListener("dataavailable", function (event) {
    if (event.data && event.data.size > 0) {
      chunks.push(event.data);
    }
  });

  // Capture mimeType now — recorder.mimeType may be empty after stop fires
  var _mimeTypeForStop = (recorder.mimeType) ? recorder.mimeType : "audio/webm";
  recorder.addEventListener("stop", function () {
    // Release mic tracks when recorder stops
    try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (_e) { /* ignore */ }
    if (presenceState) presenceState.voiceMicStream = null;
    // TASK-167B: if stopPetVoiceRecording set the flag, build Blob NOW (after dataavailable fired)
    // and kick off STT.  cancelPetVoiceRecording leaves the flag false so we skip this.
    if (presenceState && presenceState.voiceStopAndTranscribe) {
      presenceState.voiceStopAndTranscribe = false;
      _petSttTranscribeChunks(documentRef, presenceState, chunks, _mimeTypeForStop);
    }
  });

  // Show recording state BEFORE starting recorder
  setRecordingState(documentRef, presenceState, true);

  try {
    recorder.start();
  } catch (_e) {
    // Recorder failed to start — cancel cleanly
    try { stream.getTracks().forEach(function (t) { t.stop(); }); } catch (_e2) { /* ignore */ }
    setRecordingState(documentRef, presenceState, false);
    setBubbleState(documentRef, "backend_offline");
    var bubbleEl3 = documentRef ? documentRef.getElementById("pet-bubble-response") : null;
    if (bubbleEl3) setText(bubbleEl3, PET_VOICE_UNSUPPORTED_MSG);
    return;
  }

  // Hard timeout — auto-stop after PET_RECORDING_MAX_MS
  var timeoutId = setTimeout(function () {
    if (isPetRecordingActive(documentRef)) {
      stopPetVoiceRecording(documentRef);
    }
  }, PET_RECORDING_MAX_MS);
  if (presenceState) {
    presenceState.voiceRecordingTimer = timeoutId;
  }
}

// TASK-166E: validate input, then send through the existing /chat pipeline.
// State sequence: forceClickThroughOff → close input → thinking → reply | error
async function handlePetDirectSend(event, documentRef, options) {
  if (event && typeof event.preventDefault === "function") {
    event.preventDefault();
  }
  if (petChatPending) return null;

  var field = documentRef ? documentRef.getElementById("pet-direct-input-field") : null;
  var value = field && typeof field.value === "string" ? field.value.trim() : "";

  if (!value) {
    // TASK-166E: empty / whitespace — show empty_input state, keep panel open for retry
    setBubbleState(documentRef, "empty_input");
    if (field && typeof field.focus === "function") field.focus();
    return null;
  }

  // Send path: force CT off, close input, show thinking bubble, call /chat
  forceClickThroughOff(documentRef);  // TASK-166D: CT must be OFF while replying
  closePetDirectInput(documentRef);
  petChatPending = true;
  setBubbleState(documentRef, "thinking");

  try {
    var data = await sendPetChatMessage(value, options || {});
    var nextState = stateForChatSource(data.source, data.reply);
    var statusText = sourceStatusLabel(data.source);
    var bubbleOptions = {
      source: data.source,
      statusText,
      message: detailMessageForBubbleState(nextState),
      response: responseForBubbleState(nextState, data.reply),
      mood: data.mood,
    };
    setBubbleState(documentRef, nextState, bubbleOptions);
    rememberRecentPetReply(documentRef, nextState, bubbleOptions, options || {});
    // TASK-168B: speak final reply if TTS enabled
    speakPetReply(documentRef, data.reply, nextState);
    return data;
  } catch (error) {
    var errorState = "llm_local_error";
    if (isPetChatTimeoutError(error)) {
      errorState = "timeout";
    } else if (isFetchNetworkError(error)) {
      errorState = "backend_offline";
    }
    // TASK-166E: clean error fallback — no diagnostics, no raw URL, no stack trace
    setBubbleState(documentRef, errorState);
    return null;
  } finally {
    petChatPending = false;
  }
}

// TASK-158: pick the next idle line in sequence (cycles, no back-to-back repeat)
function pickNextIdleLine(presenceState) {
  const lines = PET_IDLE_LINES;
  const len = lines.length;
  if (len === 0) return PET_IDLE_REPLY;
  const last = typeof presenceState.lastIdleLineIdx === "number"
    ? presenceState.lastIdleLineIdx
    : -1;
  const next = (last + 1) % len;
  presenceState.lastIdleLineIdx = next;
  return lines[next];
}

// TASK-158: true when idle rotation may show a line without overwriting active state
function isIdleRotationEligible(documentRef, presenceState) {
  if (presenceState.quietMode === true) return false;  // TASK-166C regression: quiet mode must suppress idle
  if (presenceState.recentReply) return false;
  if (presenceState.handoffActive) return false;
  if (petChatPending) return false;
  const bubble = documentRef ? documentRef.getElementById("pet-bubble") : null;
  if (bubble) {
    const blockedStates = ["llm_local_error", "backend_offline", "timeout",
                           "thinking", "pending", "handoff"];
    if (blockedStates.indexOf(bubble.dataset.state) !== -1) return false;
  }
  return true;
}

// TASK-158: cancel any pending idle rotation timer
function stopIdleRotation(presenceState, timerApi) {
  clearPresenceTimer(presenceState, "idleRotationTimer", timerApi || globalThis);
}

// TASK-158: schedule the next idle line rotation tick
// TASK-159: first tick delayed by max(cooldownRemaining, PET_IDLE_ROTATION_MS)
function startIdleRotation(documentRef, presenceState, timerApi) {
  const api = timerApi || globalThis;
  stopIdleRotation(presenceState, api);
  if (presenceState.quietMode === true) return;  // TASK-160: quiet mode suppresses rotation
  const now = getPresenceNow(api);
  const cooldownUntil = typeof presenceState.idleCooldownUntil === "number"
    ? presenceState.idleCooldownUntil : 0;
  const cooldownRemaining = Math.max(0, cooldownUntil - now);  // TASK-159
  const delay = Math.max(cooldownRemaining, PET_IDLE_ROTATION_MS);  // TASK-159
  presenceState.idleRotationTimer = schedulePresenceTimer(
    api,
    function fireIdleRotation() {
      presenceState.idleRotationTimer = null;
      if (!isIdleRotationEligible(documentRef, presenceState)) {
        return;
      }
      if (presenceState.quietMode === true) return;  // TASK-166C: defense-in-depth quiet guard
      const line = pickNextIdleLine(presenceState);
      setBubbleState(documentRef, "idle_default", { response: line });
      startIdleRotation(documentRef, presenceState, api);
    },
    delay
  );
}

function setPetIdleDefault(documentRef = document, options = {}) {
  const presenceState = getPetPresenceState(documentRef);
  const timerApi = getPresenceTimerApi(options, presenceState);
  presenceState.timerApi = timerApi;

  clearPresenceTimer(presenceState, "recentTimer", timerApi);
  clearPresenceTimer(presenceState, "handoffTimer", timerApi);
  presenceState.recentReply = null;
  presenceState.handoffActive = false;

  setIdleCooldown(presenceState, timerApi, PET_IDLE_LAUNCH_QUIET_MS);  // TASK-159: launch quiet period
  const state = setIdleQuietBubble(documentRef, presenceState);  // TASK-160 fix
  startIdleRotation(documentRef, presenceState, timerApi);  // TASK-158
  return state;
}

function expireRecentPetReply(documentRef, presenceState, timerApi) {
  presenceState.recentTimer = null;
  presenceState.recentReply = null;

  if (!presenceState.handoffActive) {
    setIdleQuietBubble(documentRef, presenceState);  // TASK-160 fix
    setIdleCooldown(presenceState, timerApi, PET_IDLE_COOLDOWN_MS);  // TASK-159: post-activity cooldown
    startIdleRotation(documentRef, presenceState, timerApi);  // TASK-158
  }

  presenceState.timerApi = timerApi;
}

function rememberRecentPetReply(documentRef, state, bubbleOptions, options = {}) {
  const presenceState = getPetPresenceState(documentRef);
  const timerApi = getPresenceTimerApi(options, presenceState);
  const now = getPresenceNow(timerApi);
  presenceState.timerApi = timerApi;

  clearPresenceTimer(presenceState, "recentTimer", timerApi);
  clearPresenceTimer(presenceState, "handoffTimer", timerApi);
  stopIdleRotation(presenceState, timerApi);  // TASK-158: real reply, pause idle rotation
  presenceState.handoffActive = false;
  presenceState.recentReply = {
    state,
    options: { ...bubbleOptions },
    expiresAt: now + PET_RECENT_REPLY_VISIBLE_MS,
  };
  presenceState.recentTimer = schedulePresenceTimer(
    timerApi,
    () => expireRecentPetReply(documentRef, presenceState, timerApi),
    PET_RECENT_REPLY_VISIBLE_MS
  );
}

function restorePetPresence(documentRef = document, options = {}) {
  const presenceState = getPetPresenceState(documentRef);
  const timerApi = getPresenceTimerApi(options, presenceState);
  const now = getPresenceNow(timerApi);
  const recentReply = presenceState.recentReply;
  presenceState.timerApi = timerApi;

  if (recentReply && recentReply.expiresAt > now) {
    return setBubbleState(documentRef, recentReply.state, recentReply.options);
  }

  clearPresenceTimer(presenceState, "recentTimer", timerApi);
  presenceState.recentReply = null;
  const idleResult = setIdleQuietBubble(documentRef, presenceState);  // TASK-160 fix
  setIdleCooldown(presenceState, timerApi, PET_IDLE_COOLDOWN_MS);  // TASK-159: cooldown after show/restore
  startIdleRotation(documentRef, presenceState, timerApi);  // TASK-159
  return idleResult;
}

function showPetHandoffHint(documentRef = document, options = {}) {
  const presenceState = getPetPresenceState(documentRef);
  const timerApi = getPresenceTimerApi(options, presenceState);
  presenceState.timerApi = timerApi;

  clearPresenceTimer(presenceState, "handoffTimer", timerApi);
  presenceState.handoffActive = true;

  const state = setBubbleState(documentRef, "handoff");
  presenceState.handoffTimer = schedulePresenceTimer(
    timerApi,
    () => {
      presenceState.handoffTimer = null;
      presenceState.handoffActive = false;
      restorePetPresence(documentRef, { timerApi });
    },
    PET_HANDOFF_HINT_MS
  );

  return state;
}

function restorePetPresenceAfterShow(documentRef = document, options = {}) {
  return restorePetPresence(documentRef, options);
}


function isFetchNetworkError(error) {
  return (
    error instanceof TypeError ||
    (error && typeof error.message === "string" && /failed to fetch|network/i.test(error.message))
  );
}

function isPetChatTimeoutError(error) {
  return Boolean(error && error.name === "PetChatTimeoutError");
}

function createTimeoutSignal(timeoutMs, AbortControllerImpl = globalThis.AbortController) {
  if (typeof AbortControllerImpl !== "function") {
    return {
      signal: undefined,
      cancel() {},
    };
  }

  const controller = new AbortControllerImpl();
  return {
    signal: controller.signal,
    cancel() {
      controller.abort();
    },
  };
}

function fetchWithTimeout(fetchImpl, url, fetchOptions, timeoutMs, timerApi = globalThis) {
  const timeoutValue = Number.isFinite(timeoutMs) && timeoutMs > 0 ? timeoutMs : PET_CHAT_TIMEOUT_MS;
  const timeoutController = createTimeoutSignal(timeoutValue);
  let timer = null;

  const requestOptions = {
    ...fetchOptions,
    signal: fetchOptions.signal || timeoutController.signal,
  };

  const timeoutPromise = new Promise((_, reject) => {
    timer = timerApi.setTimeout(() => {
      timeoutController.cancel();
      reject(new PetChatTimeoutError());
    }, timeoutValue);
  });

  return Promise.race([fetchImpl(url, requestOptions), timeoutPromise]).finally(() => {
    if (timer) {
      timerApi.clearTimeout(timer);
    }
  });
}

function buildChatPayload(message) {
  return {
    message,
    use_memory: false,
  };
}

function parseChatResponse(data) {
  if (!data || typeof data.reply !== "string") {
    throw new PetChatResponseError();
  }

  return {
    reply: data.reply,
    mood: data && typeof data.mood === "string" ? data.mood : PET_MODE_DEFAULTS.expression,
    source: data && typeof data.source === "string" ? data.source : "unknown",
  };
}

function getBubbleStateConfig(state) {
  return BUBBLE_STATES[state] || BUBBLE_STATES.expanded;
}

function normalizeBubbleStateArgs(firstArg, secondArg, thirdArg) {
  if (firstArg && typeof firstArg.getElementById === "function") {
    return {
      documentRef: firstArg,
      state: typeof secondArg === "boolean" ? (secondArg ? "expanded" : "collapsed") : secondArg,
      options: thirdArg || {},
    };
  }

  return {
    documentRef: typeof document !== "undefined" ? document : null,
    state: typeof firstArg === "boolean" ? (firstArg ? "expanded" : "collapsed") : firstArg,
    options: secondArg || {},
  };
}

function setBubbleDetailsOpen(documentRef = document, open = false) {
  if (open) forceClickThroughOff(documentRef);  // TASK-166D: showing details must disable click-through
  const root = documentRef.getElementById("pet-mode-root");
  const bubble = documentRef.getElementById("pet-bubble");
  const details = documentRef.getElementById("pet-bubble-details");
  const detailsToggle = documentRef.getElementById("pet-bubble-details-toggle");
  const detailsAvailable = !bubble || bubble.dataset.hasDetails !== "false";
  const nextOpen = Boolean(open && detailsAvailable);
  const detailsState = nextOpen ? "open" : "closed";

  if (root) {
    root.dataset.bubbleDetails = detailsState;
  }

  if (bubble) {
    bubble.dataset.detailsOpen = nextOpen ? "true" : "false";
  }

  if (details) {
    details.hidden = !nextOpen;
  }

  if (detailsToggle) {
    detailsToggle.setAttribute("aria-expanded", nextOpen ? "true" : "false");
  }

  const menuDetailsToggle = documentRef.getElementById("pet-menu-toggle-details");
  if (menuDetailsToggle) {
    menuDetailsToggle.setAttribute("aria-expanded", nextOpen ? "true" : "false");
    setText(menuDetailsToggle, nextOpen ? "Hide Details" : "Show Details");
  }
}

function isBubbleDetailsOpen(documentRef = document) {
  const bubble = documentRef.getElementById("pet-bubble");
  return Boolean(bubble && bubble.dataset.detailsOpen === "true");
}

function toggleBubbleDetails(documentRef = document) {
  const bubble = documentRef.getElementById("pet-bubble");
  if (bubble && bubble.dataset.hasDetails === "false") {
    setBubbleDetailsOpen(documentRef, false);
    return false;
  }
  setBubbleDetailsOpen(documentRef, !isBubbleDetailsOpen(documentRef));
  return isBubbleDetailsOpen(documentRef);
}

function toggleDetailsFromMenu(documentRef = document) {
  const bubble = documentRef.getElementById("pet-bubble");

  if (bubble && bubble.dataset.hasDetails === "false") {
    setBubbleDetailsOpen(documentRef, false);
    return false;
  }

  if (!bubble || bubble.dataset.state === "collapsed" || bubble.hidden) {
    // TASK-166C: don't expose idle_default via Details menu while Quiet Mode ON
    const _quietPresenceState = getPetPresenceState(documentRef);
    if (_quietPresenceState && _quietPresenceState.quietMode === true) {
      return false;
    }
    setBubbleState(documentRef, "idle_default");
    setBubbleDetailsOpen(documentRef, true);
    return true;
  }

  toggleBubbleDetails(documentRef);
  return isBubbleDetailsOpen(documentRef);
}

function setBubbleState(firstArg, secondArg, thirdArg) {
  const { documentRef, state: requestedState, options } = normalizeBubbleStateArgs(
    firstArg,
    secondArg,
    thirdArg
  );

  if (!documentRef) {
    return null;
  }

  const state = requestedState && BUBBLE_STATES[requestedState] ? requestedState : "expanded";
  const config = getBubbleStateConfig(state);
  const expanded = Boolean(config.expanded);
  const root = documentRef.getElementById("pet-mode-root");
  const bubble = documentRef.getElementById("pet-bubble");
  const title = documentRef.getElementById("pet-bubble-title");
  const status = documentRef.getElementById("pet-bubble-status");
  const message = documentRef.getElementById("pet-bubble-message");
  const response = documentRef.getElementById("pet-bubble-response");
  const details = documentRef.getElementById("pet-bubble-details");
  const detailsToggle = documentRef.getElementById("pet-bubble-details-toggle");
  const placeholder = documentRef.getElementById("pet-bubble-placeholder");
  const form = documentRef.getElementById("pet-chat-form-hook");
  const input = documentRef.getElementById("pet-chat-input-hook");
  const send = documentRef.getElementById("pet-chat-send-hook");
  const detailStatusText = sanitizeBubbleDetailText(options.statusText || config.statusText);
  const detailMessageText = sanitizeBubbleDetailText(options.message || config.message);
  const detailsAvailable = options.detailsAvailable === false
    ? false
    : Boolean(detailStatusText || detailMessageText);

  if (root) {
    root.dataset.bubbleState = state;
    root.dataset.bubbleSource = options.source || config.source;
    root.dataset.bubbleDetails = "closed";
    root.dataset.bubbleHasDetails = detailsAvailable ? "true" : "false";
  }

  if (bubble) {
    bubble.dataset.state = state;
    bubble.dataset.source = options.source || config.source;
    bubble.dataset.detailsOpen = "false";
    bubble.dataset.hasDetails = detailsAvailable ? "true" : "false";
    bubble.setAttribute("aria-expanded", expanded ? "true" : "false");
    bubble.hidden = !expanded;
  }

  setText(title, options.title || "Bubble Chat");
  setText(status, detailStatusText);
  setText(message, detailMessageText);
  setText(response, options.response || config.response);

  if (status) {
    status.dataset.source = options.source || config.source;
  }

  if (details) {
    details.hidden = true;
    details.dataset.hasDetails = detailsAvailable ? "true" : "false";
  }

  if (detailsToggle) {
    detailsToggle.setAttribute("aria-expanded", "false");
    detailsToggle.disabled = !detailsAvailable;
  }

  const menuDetailsToggle = documentRef.getElementById("pet-menu-toggle-details");
  if (menuDetailsToggle) {
    menuDetailsToggle.setAttribute("aria-expanded", "false");
    menuDetailsToggle.hidden = !detailsAvailable;
    menuDetailsToggle.disabled = !detailsAvailable;
    menuDetailsToggle.setAttribute("aria-hidden", detailsAvailable ? "false" : "true");
    setText(menuDetailsToggle, "Show Details");
  }

  if (placeholder) {
    placeholder.dataset.state = state;
  }

  if (form) {
    form.hidden = true;
    form.dataset.devOnly = "true";
    form.setAttribute("aria-hidden", "true");
  }

  if (input) {
    input.hidden = true;
    input.disabled = Boolean(config.inputDisabled);
    input.setAttribute("placeholder", options.inputPlaceholder || config.inputPlaceholder);
    input.setAttribute("aria-invalid", state === "empty_input" ? "true" : "false");
    input.setAttribute("tabindex", "-1");
  }

  if (send) {
    send.hidden = true;
    send.disabled = Boolean(config.sendDisabled);
    send.setAttribute("tabindex", "-1");
  }

  setPetExpressionForBubbleState(documentRef, state, { mood: options.mood });

  return state;
}

function setMenuState(documentRef, open) {
  const root = documentRef.getElementById("pet-mode-root");
  const menu = documentRef.getElementById("pet-menu");
  const state = open ? "open" : "closed";

  if (root) {
    root.dataset.menuState = state;
  }

  if (menu) {
    menu.dataset.state = state;
    menu.setAttribute("aria-hidden", open ? "false" : "true");
    menu.hidden = !open;
  }
}

function openMenu(documentRef = document) {
  forceClickThroughOff(documentRef);  // TASK-166D: menu interaction must disable click-through
  setMenuState(documentRef, true);
}

function closeMenu(documentRef = document) {
  setMenuState(documentRef, false);
}

function isMenuOpen(documentRef = document) {
  const menu = documentRef.getElementById("pet-menu");
  return Boolean(menu && menu.dataset.state === "open");
}

function toggleMenu(documentRef = document) {
  setMenuState(documentRef, !isMenuOpen(documentRef));
}

function isElementOrDescendant(container, target) {
  if (!container || !target) {
    return false;
  }

  if (container === target) {
    return true;
  }

  if (typeof container.contains === "function") {
    return container.contains(target);
  }

  let node = target.parentElement || target.parentNode || null;
  while (node) {
    if (node === container) {
      return true;
    }
    node = node.parentElement || node.parentNode || null;
  }

  return false;
}

function closeMenuOnOutsideClick(event, documentRef = document) {
  if (!isMenuOpen(documentRef)) {
    return false;
  }

  const menu = documentRef.getElementById("pet-menu");
  const menuHook = documentRef.getElementById("pet-context-menu-hook");
  const target = event && event.target ? event.target : null;

  if (isElementOrDescendant(menu, target) || isElementOrDescendant(menuHook, target)) {
    return false;
  }

  closeMenu(documentRef);
  return true;
}

function expandBubble(documentRef = document) {
  setBubbleState(documentRef, "expanded");
}

function collapseBubble(documentRef = document) {
  setBubbleState(documentRef, "collapsed");
}

function toggleBubble(documentRef = document) {
  const bubble = documentRef.getElementById("pet-bubble");
  const shouldExpand = !bubble || bubble.dataset.state === "collapsed";
  setBubbleState(documentRef, shouldExpand ? "expanded" : "collapsed");
}

function handleBubbleInput(event, documentRef = document) {
  const input =
    event && event.target ? event.target : documentRef.getElementById("pet-chat-input-hook");
  const value = input && typeof input.value === "string" ? input.value.trim() : "";

  setBubbleState(documentRef, value ? "composing" : "expanded");
}

async function sendPetChatMessage(message, options = {}) {
  const fetchImpl =
    options.fetchImpl || (typeof fetch === "function" ? fetch.bind(globalThis) : null);

  if (!fetchImpl) {
    throw new TypeError("fetch is not available");
  }

  const backendUrl = options.backendUrl || getPetBackendUrl(options.windowRef);
  const response = await fetchWithTimeout(
    fetchImpl,
    `${backendUrl}/chat`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildChatPayload(message)),
    },
    options.timeoutMs,
    options.timerApi || globalThis
  );

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = data && data.detail ? data.detail : `HTTP ${response.status}`;
    throw new Error(detail);
  }

  return parseChatResponse(data);
}

async function handleChatSubmit(event, documentRef = document, options = {}) {
  if (event && typeof event.preventDefault === "function") {
    event.preventDefault();
  }

  const input = documentRef.getElementById("pet-chat-input-hook");
  const value = input && typeof input.value === "string" ? input.value.trim() : "";

  if (petChatPending) {
    return null;
  }

  if (!value) {
    setBubbleState(documentRef, "empty_input");
    return null;
  }

  petChatPending = true;
  setBubbleState(documentRef, "thinking");

  try {
    const data = await sendPetChatMessage(value, options);
    const nextState = stateForChatSource(data.source, data.reply);
    const statusText = sourceStatusLabel(data.source);

    setBubbleState(documentRef, nextState, {
      source: data.source,
      statusText,
      message: detailMessageForBubbleState(nextState),
      response: responseForBubbleState(nextState, data.reply),
      mood: data.mood,
    });

    if (input && data.source !== "llm_local_error") {
      input.value = "";
    }

    return data;
  } catch (error) {
    if (isPetChatTimeoutError(error)) {
      setBubbleState(documentRef, "timeout");
    } else if (isFetchNetworkError(error)) {
      setBubbleState(documentRef, "backend_offline");
    } else {
      setBubbleState(documentRef, "llm_local_error");
    }
    return null;
  } finally {
    petChatPending = false;
  }
}

const handlePlaceholderSubmit = handleChatSubmit;

function handleOpenFullApp(documentRef = document, dragonPetApi = null) {
  const message = documentRef.getElementById("pet-bubble-message");
  const api =
    dragonPetApi ||
    (typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null);

  if (!api || typeof api.openFullApp !== "function") {
    setText(message, "Full App switch is not available in this preview.");
    return null;
  }

  setText(message, "Opening Full App...");
  const result = api.openFullApp();

  if (result && typeof result.catch === "function") {
    result.catch(() => {
      setText(message, "Full App switch failed.");
    });
  }

  return result;
}

function handleFullAppHandoff(documentRef = document, dragonPetApi = null, options = {}) {
  showPetHandoffHint(documentRef, options);
  return handleOpenFullApp(documentRef, dragonPetApi);
}

function handleChatHandoff(documentRef = document, dragonPetApi = null, options = {}) {
  return handleFullAppHandoff(documentRef, dragonPetApi, options);
}

function callPetApiAction(documentRef, methodName, pendingMessage, fallbackMessage) {
  const message = documentRef.getElementById("pet-bubble-message");
  const api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;

  if (!api || typeof api[methodName] !== "function") {
    setText(message, fallbackMessage);
    return null;
  }

  setText(message, pendingMessage);
  const result = api[methodName]();

  if (result && typeof result.catch === "function") {
    result.catch(() => {
      setText(message, fallbackMessage);
    });
  }

  return result;
}

function handleResetPetPosition(documentRef = document) {
  forceClickThroughOff(documentRef);  // TASK-166D: position reset must disable click-through first
  return callPetApiAction(
    documentRef,
    "resetPetPosition",
    "Resetting Pet position...",
    "Reset Pet Position is not available in this preview."
  );
}

function handleHidePetWindow(documentRef = document) {
  forceClickThroughOff(documentRef);  // TASK-166D: hide window must disable click-through first
  return callPetApiAction(
    documentRef,
    "hidePetWindow",
    "Hiding Pet Window...",
    "Hide Pet Window is not available in this preview."
  );
}

function renderPetSpeechUpdate(documentRef = document, payload = {}, options = {}) {
  const reply = visibleReplyForSpeechPayload(payload);
  const mood = typeof payload.mood === "string" ? payload.mood : PET_MODE_DEFAULTS.expression;
  const source = typeof payload.source === "string" ? payload.source : "unknown";
  const nextState = stateForChatSource(source, reply);
  const detailOptions = detailOptionsForSpeechPayload(payload, nextState, source);
  const bubbleOptions = {
    source,
    statusText: detailOptions.statusText,
    message: detailOptions.message,
    detailsAvailable: detailOptions.detailsAvailable,
    response: responseForBubbleState(nextState, reply),
    mood,
  };

  const renderedState = setBubbleState(documentRef, nextState, bubbleOptions);
  // TASK-157: thinking is transient — do not persist it as a recent reply.
  // When the window is shown/focused, it should restore the last real reply
  // or idle, not re-show the thinking bubble.
  if (renderedState !== "thinking") {
    rememberRecentPetReply(documentRef, nextState, bubbleOptions, options);
  }
  return renderedState;
}

function buildPetMoodExpressionSmokeApi(documentRef = document, options = {}) {
  return Object.freeze({
    supportedMoods: Object.freeze(Object.keys(CHRISTINA_EXPRESSION_ASSETS)),
    apply(mood) {
      const renderedState = renderPetSpeechUpdate(
        documentRef,
        {
          reply: PET_MOOD_SMOKE_REPLY,
          mood: typeof mood === "string" ? mood : "",
          source: "unknown",
        },
        options
      );
      const avatarContainer = documentRef.getElementById("pet-avatar-container");
      const avatar = documentRef.getElementById("pet-avatar");
      const expression = avatarContainer
        ? avatarContainer.dataset.expression || PET_MODE_DEFAULTS.expression
        : PET_MODE_DEFAULTS.expression;

      return {
        ok: true,
        requestedMood: mood,
        expression,
        state: renderedState,
        src: avatar ? avatar.getAttribute("src") : "",
      };
    },
  });
}

function installPetMoodExpressionSmokeHook(
  documentRef = document,
  windowRef = typeof window !== "undefined" ? window : null,
  options = {}
) {
  if (!windowRef || hasOwnKey(windowRef, PET_MOOD_SMOKE_API_NAME)) {
    return windowRef ? windowRef[PET_MOOD_SMOKE_API_NAME] || null : null;
  }

  const smokeApi = buildPetMoodExpressionSmokeApi(documentRef, options);
  Object.defineProperty(windowRef, PET_MOOD_SMOKE_API_NAME, {
    configurable: true,
    enumerable: false,
    value: smokeApi,
  });
  return smokeApi;
}


// ── TASK-166B: Scale preset helpers ──────────────────────────────────────────

const PET_VALID_SCALES = Object.freeze(["small", "medium", "large"]);

function normalizeScale(value) {
  // Falls back to "medium" for any unknown/missing/invalid value
  if (value === "small" || value === "large") return value;
  return "medium";
}

// Set data-scale on the root element and update the S/M/L button pressed states
function setActiveScaleButton(documentRef, scale) {
  const normalizedScale = normalizeScale(scale);
  const root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  if (root) {
    root.dataset.scale = normalizedScale;
  }
  for (const s of PET_VALID_SCALES) {
    const btn = documentRef ? documentRef.getElementById(`pet-menu-scale-${s}`) : null;
    if (btn) {
      btn.setAttribute("aria-pressed", s === normalizedScale ? "true" : "false");
    }
  }
}

// Apply a scale change: update UI and invoke IPC
function applyScalePreset(documentRef, scale, dragonPetApi) {
  const normalizedScale = normalizeScale(scale);
  setActiveScaleButton(documentRef, normalizedScale);
  const api =
    dragonPetApi ||
    (typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null);
  if (api && typeof api.setScale === "function") {
    const result = api.setScale(normalizedScale);
    if (result && typeof result.catch === "function") {
      result.catch(function () {
        // IPC failure is non-fatal; UI state already updated
      });
    }
  }
}

function initializePetMode(documentRef = document) {
  const root = documentRef.getElementById("pet-mode-root");
  const dragRegion = documentRef.getElementById("pet-drag-region");
  const avatarContainer = documentRef.getElementById("pet-avatar-container");
  const avatar = documentRef.getElementById("pet-avatar");
  const hint = documentRef.getElementById("pet-hint");
  const bubble = documentRef.getElementById("pet-bubble");
  const bubbleOpenHook = documentRef.getElementById("pet-bubble-open-hook");
  const bubbleCloseHook = documentRef.getElementById("pet-bubble-close-hook");
  const bubbleMessage = documentRef.getElementById("pet-bubble-message");
  const bubblePlaceholder = documentRef.getElementById("pet-bubble-placeholder");
  const chatInput = documentRef.getElementById("pet-chat-input-hook");
  const chatForm = documentRef.getElementById("pet-chat-form-hook");
  const openFullAppHook = documentRef.getElementById("pet-open-full-app-hook");
  const contextMenuHook = documentRef.getElementById("pet-context-menu-hook");
  const menuToggleDetails = documentRef.getElementById("pet-menu-toggle-details");
  const menuResetPosition = documentRef.getElementById("pet-menu-reset-position");
  const menuHideWindow = documentRef.getElementById("pet-menu-hide-window");
  const menuQuietMode = documentRef.getElementById("pet-menu-quiet-mode");  // TASK-160
  const menuClickThrough = documentRef.getElementById("pet-menu-click-through");  // TASK-166D
  const directInputPanel = documentRef.getElementById("pet-direct-input-panel");  // TASK-166E
  const directInputForm  = documentRef.getElementById("pet-direct-input-form");   // TASK-166E
  const directInputField = documentRef.getElementById("pet-direct-input-field");  // TASK-166E
  const directInputClose = documentRef.getElementById("pet-direct-input-close");  // TASK-166E
  const micHook          = documentRef.getElementById("pet-mic-hook");            // TASK-167A
  const recordingCancel  = documentRef.getElementById("pet-recording-cancel");    // TASK-167A
  const menuTts          = documentRef.getElementById("pet-menu-tts");           // TASK-168B
  const ttsSpeakingStop    = documentRef.getElementById("pet-tts-stop");           // TASK-168B
  const menuTtsSettings    = documentRef.getElementById("pet-menu-tts-settings"); // TASK-169
  const ttsSettingsPanel   = documentRef.getElementById("pet-tts-settings");      // TASK-169
  const ttsVoiceSelect     = documentRef.getElementById("pet-tts-voice-select");  // TASK-169
  const ttsRateInput       = documentRef.getElementById("pet-tts-rate");          // TASK-169
  const ttsPitchInput      = documentRef.getElementById("pet-tts-pitch");         // TASK-169
  const ttsVolumeInput     = documentRef.getElementById("pet-tts-volume");        // TASK-169
  const ttsResetBtn        = documentRef.getElementById("pet-tts-reset");         // TASK-169

  if (root) {
    root.dataset.initialized = "true";
    root.dataset.mode = "pet";
  }

  if (avatarContainer) {
    avatarContainer.dataset.expression = PET_MODE_DEFAULTS.expression;
  }

  if (avatar && !avatar.getAttribute("src")) {
    avatar.setAttribute("src", PET_MODE_DEFAULTS.avatarSrc);
  }

  setText(hint, PET_MODE_DEFAULTS.hint);
  setText(bubbleMessage, PET_MODE_DEFAULTS.bubbleMessage);

  // TASK-162: apply persisted quiet mode from URL param before first idle render
  if (typeof window !== "undefined" && window.location &&
      typeof URLSearchParams !== "undefined") {
    try {
      var urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get("quietMode") === "true") {
        setPetQuietMode(documentRef, true);
      }
      // TASK-166B: apply persisted scale from URL param before first render
      var initialScale = normalizeScale(urlParams.get("scale"));
      setActiveScaleButton(documentRef, initialScale);
    } catch (_e) {
      // Fail safe: ignore corrupt URL params, keep defaults
    }
  }

  setPetIdleDefault(documentRef);
  closeMenu(documentRef);

  if (bubblePlaceholder && !bubblePlaceholder.textContent.trim()) {
    setText(
      bubblePlaceholder,
      "Display-only speech bubble. Type in Full App."
    );
  }

  if (dragRegion && typeof dragRegion.addEventListener === "function") {
    dragRegion.addEventListener("click", () => restorePetPresence(documentRef));
  }

  if (bubbleOpenHook && typeof bubbleOpenHook.addEventListener === "function") {
    bubbleOpenHook.addEventListener("click", () => openPetDirectInput(documentRef));  // TASK-166E
  }

  if (bubbleCloseHook && typeof bubbleCloseHook.addEventListener === "function") {
    bubbleCloseHook.addEventListener("click", (event) => {
      if (event && typeof event.stopPropagation === "function") {
        event.stopPropagation();
      }
      handleHidePetWindow(documentRef);
    });
  }

  if (chatInput && typeof chatInput.addEventListener === "function") {
    chatInput.addEventListener("input", (event) => handleBubbleInput(event, documentRef));
  }

  if (chatForm && typeof chatForm.addEventListener === "function") {
    chatForm.addEventListener("submit", (event) => {
      handleChatSubmit(event, documentRef);
    });
  }

  if (openFullAppHook && typeof openFullAppHook.addEventListener === "function") {
    openFullAppHook.addEventListener("click", () => handleFullAppHandoff(documentRef));
  }

  if (root && typeof root.addEventListener === "function") {
    root.addEventListener("contextmenu", (event) => {
      if (event && typeof event.preventDefault === "function") {
        event.preventDefault();
      }
      toggleMenu(documentRef);
    });
  }

  if (contextMenuHook && typeof contextMenuHook.addEventListener === "function") {
    contextMenuHook.addEventListener("click", () => toggleMenu(documentRef));
  }

  if (menuToggleDetails && typeof menuToggleDetails.addEventListener === "function") {
    menuToggleDetails.addEventListener("click", () => {
      toggleDetailsFromMenu(documentRef);
      closeMenu(documentRef);
    });
  }

  if (menuResetPosition && typeof menuResetPosition.addEventListener === "function") {
    menuResetPosition.addEventListener("click", () => {
      handleResetPetPosition(documentRef);
      closeMenu(documentRef);
    });
  }

  if (menuHideWindow && typeof menuHideWindow.addEventListener === "function") {
    menuHideWindow.addEventListener("click", () => {
      handleHidePetWindow(documentRef);
      closeMenu(documentRef);
    });
  }

  // TASK-160: quiet mode toggle
  if (menuQuietMode && typeof menuQuietMode.addEventListener === "function") {
    menuQuietMode.addEventListener("click", () => {
      var newQuietMode = !getPetQuietMode(documentRef);
      setPetQuietMode(documentRef, newQuietMode);
      // TASK-162: persist the new preference through the narrow IPC bridge
      var dragonPetApi =
        typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
      if (dragonPetApi && typeof dragonPetApi.setQuietMode === "function") {
        dragonPetApi.setQuietMode(newQuietMode);
      }
      closeMenu(documentRef);
    });
  }

  // TASK-166D: click-through toggle
  if (menuClickThrough && typeof menuClickThrough.addEventListener === "function") {
    menuClickThrough.addEventListener("click", function () {
      var newClickThrough = !getPetClickThrough(documentRef);
      setPetClickThrough(documentRef, newClickThrough);
      var _ctApi = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
      if (_ctApi && typeof _ctApi.setClickThrough === "function") {
        _ctApi.setClickThrough(newClickThrough);
      }
      closeMenu(documentRef);
    });
  }

  // TASK-168B: TTS toggle
  if (menuTts && typeof menuTts.addEventListener === "function") {
    menuTts.addEventListener("click", function () {
      togglePetTts(documentRef);
      closeMenu(documentRef);
    });
  }

  // TASK-168B: stop speech button
  if (ttsSpeakingStop && typeof ttsSpeakingStop.addEventListener === "function") {
    ttsSpeakingStop.addEventListener("click", function () {
      stopPetSpeech(documentRef);
    });
  }

  // TASK-169: TTS settings panel toggle
  if (menuTtsSettings && typeof menuTtsSettings.addEventListener === "function") {
    menuTtsSettings.addEventListener("click", function () {
      if (!ttsSettingsPanel) return;
      var isOpen = !ttsSettingsPanel.hidden;
      ttsSettingsPanel.hidden = isOpen;
      menuTtsSettings.setAttribute("aria-expanded", isOpen ? "false" : "true");
      menuTtsSettings.textContent = isOpen ? "語音設定 ▶" : "語音設定 ▼";
      if (!isOpen) {
        populatePetVoiceSelector(documentRef);
        syncTtsControlDisplays(documentRef);
      }
    });
  }

  // TASK-169: voice selector
  if (ttsVoiceSelect && typeof ttsVoiceSelect.addEventListener === "function") {
    ttsVoiceSelect.addEventListener("change", function () {
      petTtsVoiceName = ttsVoiceSelect.value || "";
      saveTtsSettings();
    });
  }

  // TASK-169: rate slider
  if (ttsRateInput && typeof ttsRateInput.addEventListener === "function") {
    ttsRateInput.addEventListener("input", function () {
      petTtsRate = clampTtsValue(ttsRateInput.value, PET_TTS_RATE_MIN, PET_TTS_RATE_MAX, PET_TTS_RATE_DEF);
      syncTtsControlDisplays(documentRef);
      saveTtsSettings();
    });
  }

  // TASK-169: pitch slider
  if (ttsPitchInput && typeof ttsPitchInput.addEventListener === "function") {
    ttsPitchInput.addEventListener("input", function () {
      petTtsPitch = clampTtsValue(ttsPitchInput.value, PET_TTS_PITCH_MIN, PET_TTS_PITCH_MAX, PET_TTS_PITCH_DEF);
      syncTtsControlDisplays(documentRef);
      saveTtsSettings();
    });
  }

  // TASK-169: volume slider
  if (ttsVolumeInput && typeof ttsVolumeInput.addEventListener === "function") {
    ttsVolumeInput.addEventListener("input", function () {
      petTtsVolume = clampTtsValue(ttsVolumeInput.value, PET_TTS_VOL_MIN, PET_TTS_VOL_MAX, PET_TTS_VOL_DEF);
      syncTtsControlDisplays(documentRef);
      saveTtsSettings();
    });
  }

  // TASK-169: reset TTS controls button
  if (ttsResetBtn && typeof ttsResetBtn.addEventListener === "function") {
    ttsResetBtn.addEventListener("click", function () {
      resetTtsControls(documentRef);
    });
  }

  // TASK-169: wire onvoiceschanged for async voice loading; safe if unsupported
  if (isPetTtsAvailable()) {
    try {
      window.speechSynthesis.onvoiceschanged = function () {
        populatePetVoiceSelector(documentRef);
      };
    } catch (_e) {}
  }

  // TASK-169: load persisted TTS settings and apply to state + controls on init
  (function () {
    var s = loadTtsSettings();
    petTtsVoiceName = s.voice;
    petTtsRate      = s.rate;
    petTtsPitch     = s.pitch;
    petTtsVolume    = s.volume;
    syncTtsControlDisplays(documentRef);
    populatePetVoiceSelector(documentRef);
  }());

  // TASK-166D: recovery strip — pointerenter on drag handle forces click-through OFF
  var dragHandle = documentRef.getElementById("pet-drag-handle");
  if (dragHandle && typeof dragHandle.addEventListener === "function") {
    dragHandle.addEventListener("pointerenter", function () {
      forceClickThroughOff(documentRef);
    });
  }

  // TASK-166E click-fix2: full-width CT recovery strip — only visible while CT is ON.
  // pointerenter and mousemove fire even under setIgnoreMouseEvents(true, { forward: true }),
  // so hovering the top of the Pet window reliably exits click-through mode.
  // Both events are wired as belt-and-suspenders because Electron/OS delivery varies.
  var recoveryStripEl = documentRef.getElementById("pet-ct-recovery-strip");
  if (recoveryStripEl && typeof recoveryStripEl.addEventListener === "function") {
    recoveryStripEl.addEventListener("pointerenter", function () {
      forceClickThroughOff(documentRef);
    });
    recoveryStripEl.addEventListener("mousemove", function () {
      forceClickThroughOff(documentRef);
    });
  }

  // TASK-166E: direct input panel — close button
  if (directInputClose && typeof directInputClose.addEventListener === "function") {
    directInputClose.addEventListener("click", function () {
      closePetDirectInput(documentRef);
    });
  }

  // TASK-166E: direct input panel — Esc key on field closes input
  if (directInputField && typeof directInputField.addEventListener === "function") {
    directInputField.addEventListener("keydown", function (event) {
      if (event && event.key === "Escape") {
        closePetDirectInput(documentRef);
        if (typeof event.stopPropagation === "function") event.stopPropagation();
      }
    });
  }

  // TASK-166E: direct input panel — form submit (Enter / Send button)
  if (directInputForm && typeof directInputForm.addEventListener === "function") {
    directInputForm.addEventListener("submit", function (event) {
      handlePetDirectSend(event, documentRef);
    });
  }

  // TASK-166E click-fix: defensive CT-off listeners on the direct input panel and field.
  // These guard against any path (Tab key, assistive tech, IPC race) where the panel
  // is visible but CT is still ON.  forceClickThroughOff is a no-op when already OFF.
  if (directInputPanel && typeof directInputPanel.addEventListener === "function") {
    directInputPanel.addEventListener("pointerdown", function () {
      forceClickThroughOff(documentRef);
    });
  }
  if (directInputField && typeof directInputField.addEventListener === "function") {
    directInputField.addEventListener("focus", function () {
      forceClickThroughOff(documentRef);
    });
  }

  // TASK-167A: mic / voice button — toggle-to-record
  if (micHook && typeof micHook.addEventListener === "function") {
    micHook.addEventListener("click", function () {
      openPetVoiceRecording(documentRef);
    });
  }

  // TASK-167A: recording cancel button
  if (recordingCancel && typeof recordingCancel.addEventListener === "function") {
    recordingCancel.addEventListener("click", function () {
      cancelPetVoiceRecording(documentRef);
    });
  }

  // TASK-166B: S/M/L scale preset buttons
  for (var _scaleKey of PET_VALID_SCALES) {
    (function (scaleKey) {
      var scaleBtn = documentRef.getElementById("pet-menu-scale-" + scaleKey);
      if (scaleBtn && typeof scaleBtn.addEventListener === "function") {
        scaleBtn.addEventListener("click", function () {
          applyScalePreset(documentRef, scaleKey, null);
          closeMenu(documentRef);
        });
      }
    }(_scaleKey));
  }

  if (typeof documentRef.addEventListener === "function") {
    documentRef.addEventListener("click", (event) => closeMenuOnOutsideClick(event, documentRef));
    documentRef.addEventListener("keydown", (event) => {
      if (event && event.key === "Escape") {
        if (isPetRecordingActive(documentRef)) {
          cancelPetVoiceRecording(documentRef);  // TASK-167A: Esc cancels voice recording first
        } else if (isPetDirectInputOpen(documentRef)) {
          closePetDirectInput(documentRef);  // TASK-166E: Esc closes direct input
        } else {
          closeMenu(documentRef);
        }
      }
    });
    documentRef.addEventListener("visibilitychange", () => {
      if (!documentRef.hidden) {
        restorePetPresenceAfterShow(documentRef);
      }
    });
  }

  const windowRef =
    documentRef.defaultView ||
    (typeof window !== "undefined" ? window : null);
  if (windowRef && typeof windowRef.addEventListener === "function") {
    windowRef.addEventListener("focus", () => restorePetPresenceAfterShow(documentRef));
  }
  installPetMoodExpressionSmokeHook(documentRef, windowRef);

  const api =
    typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (api && typeof api.onSpeechUpdate === "function") {
    api.onSpeechUpdate((payload) => {
      renderPetSpeechUpdate(documentRef, payload);
    });
  }
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => initializePetMode(document));
  } else {
    initializePetMode(document);
  }
}

if (typeof module !== "undefined") {
  module.exports = {
    BUBBLE_STATES,
    CHRISTINA_EXPRESSION_ASSETS,
    PET_BACKEND_DEFAULT_URL,
    PET_BUBBLE_STATE_EXPRESSIONS,
    PET_HANDOFF_HINT_MS,
    PET_HANDOFF_REPLY,
    PET_IDLE_REPLY,
    PET_LONG_REPLY_HINT,
    PET_MODE_DEFAULTS,
    PET_MOOD_SMOKE_API_NAME,
    PET_MOOD_SMOKE_REPLY,
    PET_RECENT_REPLY_VISIBLE_MS,
    PET_REPLY_PREVIEW_LIMIT,
    PET_REPLY_LONG_THRESHOLD,
    PET_MOOD_EXPRESSION_MAP,
    buildChatPayload,
    collapseBubble,
    closeMenu,
    closeMenuOnOutsideClick,
    detailOptionsForSpeechPayload,
    expandBubble,
    expressionAssetForMood,
    expressionForBubbleState,
    getPetBackendUrl,
    getBubbleStateConfig,
    handleBubbleInput,
    handleChatSubmit,
    handleFullAppHandoff,
    handleOpenFullApp,
    handleChatHandoff,
    handleHidePetWindow,
    handlePlaceholderSubmit,
    handleResetPetPosition,
    initializePetMode,
    installPetMoodExpressionSmokeHook,
    isLongReply,
    isBubbleDetailsOpen,
    isElementOrDescendant,
    isMenuOpen,
    openMenu,
    parseChatResponse,
    renderPetSpeechUpdate,
    restorePetPresenceAfterShow,
    sendPetChatMessage,
    setBubbleState,
    setBubbleDetailsOpen,
    setMenuState,
    setPetIdleDefault,
    setPetExpression,
    setPetExpressionForBubbleState,
    showPetHandoffHint,
    normalizePetMood,
    sanitizeBubbleDetailText,
    sourceStatusLabel,
    PET_IDLE_LINES,
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_COOLDOWN_MS,
    PET_IDLE_ROTATION_MS,
    PET_THINKING_SOURCE,
    isIdleRotationEligible,
    pickNextIdleLine,
    startIdleRotation,
    setIdleCooldown,
    stopIdleRotation,
    getPetClickThrough,
    setPetClickThrough,
    forceClickThroughOff,
    getPetQuietMode,
    setPetQuietMode,
    stateForChatSource,
    toggleBubbleDetails,
    toggleDetailsFromMenu,
    toggleBubble,
    toggleMenu,
    truncatePetReply,
    visibleReplyForSpeechPayload,
    // TASK-166B
    PET_VALID_SCALES,
    normalizeScale,
    setActiveScaleButton,
    applyScalePreset,
    // TASK-166E
    isPetDirectInputOpen,
    openPetDirectInput,
    closePetDirectInput,
    handlePetDirectSend,
    // TASK-167A
    PET_RECORDING_MAX_MS,
    PET_VOICE_MIC_DENIED_MSG,
    PET_VOICE_NO_MIC_MSG,
    PET_VOICE_UNSUPPORTED_MSG,
    PET_VOICE_RECORDING_STATUS,
    isPetRecordingActive,
    setRecordingState,
    openPetVoiceRecording,
    cancelPetVoiceRecording,
    stopPetVoiceRecording,
    transcribeAudioBlob,
    // TASK-167B
    PET_STT_TIMEOUT_MS,
    PET_TRANSCRIBING_STATUS,
    PET_STT_UNAVAILABLE_MSG,
    PET_STT_TIMEOUT_MSG,
    PET_STT_EMPTY_MSG,
    PET_STT_ERROR_MSG,
    PET_STT_OFFLINE_MSG,
    isTranscribingActive,
    setTranscribingState,
    // TASK-167C
    PET_VOICE_CHAT_MAX_CHARS,
    PET_VOICE_TRANSCRIPT_TOO_LONG_MSG,
    handlePetVoiceChatSend,
    // TASK-168B
    PET_TTS_MAX_CHARS,
    isPetTtsAvailable,
    setSpeakingState,
    stopPetSpeech,
    speakPetReply,
    togglePetTts,
    // TASK-169
    PET_TTS_LS_VOICE,
    PET_TTS_LS_RATE,
    PET_TTS_LS_PITCH,
    PET_TTS_LS_VOLUME,
    PET_TTS_RATE_MIN,
    PET_TTS_RATE_MAX,
    PET_TTS_RATE_DEF,
    PET_TTS_PITCH_MIN,
    PET_TTS_PITCH_MAX,
    PET_TTS_PITCH_DEF,
    PET_TTS_VOL_MIN,
    PET_TTS_VOL_MAX,
    PET_TTS_VOL_DEF,
    clampTtsValue,
    loadTtsSettings,
    saveTtsSettings,
    getPetTtsVoiceObject,
    populatePetVoiceSelector,
    syncTtsControlDisplays,
    resetTtsControls,
  };
}
