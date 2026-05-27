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
function setClickThrough(documentRef, presenceState, value) {
  const next = value === true;
  presenceState.clickThrough = next;
  const root = documentRef ? documentRef.getElementById("pet-mode-root") : null;
  if (root) {
    root.dataset.clickThrough = next ? "true" : "false";
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
function forceClickThroughOff(documentRef) {
  if (!getPetClickThrough(documentRef)) return;  // already OFF, no-op
  setPetClickThrough(documentRef, false);
  var api = typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null;
  if (api && typeof api.setClickThrough === "function") {
    api.setClickThrough(false);
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
    bubbleOpenHook.addEventListener("click", () => handleChatHandoff(documentRef));
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

  // TASK-166D: recovery strip — pointerenter on drag handle forces click-through OFF
  var dragHandle = documentRef.getElementById("pet-drag-handle");
  if (dragHandle && typeof dragHandle.addEventListener === "function") {
    dragHandle.addEventListener("pointerenter", function () {
      forceClickThroughOff(documentRef);
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
        closeMenu(documentRef);
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
  };
}
