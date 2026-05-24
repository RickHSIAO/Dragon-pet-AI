const PET_MODE_DEFAULTS = Object.freeze({
  expression: "neutral",
  hint: "\u54fc\uff0c\u6c5d\u53eb\u543e\u51fa\u4f86\u505a\u4ec0\u9ebc\uff1f",
  avatarSrc: "../renderer/assets/pet/christina/expressions/christina_neutral.png",
  bubbleMessage: "\u6253\u5b57\u8acb\u958b Full App\u3002",
});

const PET_BACKEND_DEFAULT_URL = "http://localhost:8000";
const PET_CHAT_TIMEOUT_MS = 100000;
const PET_REPLY_LONG_THRESHOLD = 160;
const PET_LONG_REPLY_HINT = "\u56de\u8986\u8f03\u9577\uff0c\u53ef\u958b Full App \u67e5\u770b\u5b8c\u6574\u5167\u5bb9\u3002";
let petChatPending = false;

const CHRISTINA_EXPRESSION_ASSETS = Object.freeze({
  neutral: "../renderer/assets/pet/christina/expressions/christina_neutral.png",
  focused: "../renderer/assets/pet/christina/expressions/christina_focused.png",
  happy: "../renderer/assets/pet/christina/expressions/christina_happy.png",
  proud: "../renderer/assets/pet/christina/expressions/christina_proud.png",
  annoyed: "../renderer/assets/pet/christina/expressions/christina_annoyed.png",
  worried: "../renderer/assets/pet/christina/expressions/christina_worried.png",
  sleepy: "../renderer/assets/pet/christina/expressions/christina_sleepy.png",
});

const PET_BUBBLE_STATE_EXPRESSIONS = Object.freeze({
  collapsed: "neutral",
  expanded: "neutral",
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
    statusText: "speech bubble",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u9ede Full App \u6253\u5b57\uff0c\u543e\u6703\u5728\u9019\u88e1\u56de\u5634\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  expanded: {
    expanded: true,
    source: "local",
    statusText: "speech bubble",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u54fc\uff0c\u6c5d\u8981\u543e\u8aaa\u8a71\uff0c\u5c31\u53bb Full App \u4e0b\u4ee4\u3002",
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
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u5f8c\u7aef\u4f3c\u4e4e\u4e0d\u5728\uff0c\u6c5d\u5148\u53bb Full App \u628a\u5b83\u53eb\u9192\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  timeout: {
    expanded: true,
    source: "timeout",
    statusText: "local timeout",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u672c\u5730\u6a21\u578b\u53ef\u80fd\u9084\u5728\u9192\u4f86\u3002\u53bb Full App \u770b\u770b\u72c0\u614b\u5427\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  llm_local_error: {
    expanded: true,
    source: "llm_local_error",
    statusText: "local model error",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u543e\u7684\u9b54\u529b\u66ab\u6642\u5361\u4f4f\u4e86\u3002\u53bb Full App \u6aa2\u67e5\u72c0\u614b\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  fallback_mock: {
    expanded: true,
    source: "mock",
    statusText: "mock fallback",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response: "\u9019\u662f\u66ab\u6642\u56de\u61c9\uff0c\u5225\u592a\u5f97\u610f\u3002",
    inputDisabled: false,
    sendDisabled: false,
    inputPlaceholder: "Dev-only hidden Pet chat input",
  },
  long_reply: {
    expanded: true,
    source: "local",
    statusText: "long reply",
    message: PET_MODE_DEFAULTS.bubbleMessage,
    response:
      PET_LONG_REPLY_HINT,
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

function normalizePetMood(mood) {
  return CHRISTINA_EXPRESSION_ASSETS[mood] ? mood : PET_MODE_DEFAULTS.expression;
}

function setPetExpression(documentRef, mood) {
  const normalizedMood = normalizePetMood(mood);
  const avatarContainer = documentRef.getElementById("pet-avatar-container");
  const avatar = documentRef.getElementById("pet-avatar");
  const assetPath = CHRISTINA_EXPRESSION_ASSETS[normalizedMood];

  if (avatarContainer) {
    avatarContainer.dataset.expression = normalizedMood;
  }

  if (avatar) {
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

function stateForChatSource(source, reply) {
  if (source === "llm_local_error") return "llm_local_error";
  if (source === "mock") return "fallback_mock";
  if (isLongReply(reply)) return "long_reply";
  return "speaking";
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
  const placeholder = documentRef.getElementById("pet-bubble-placeholder");
  const form = documentRef.getElementById("pet-chat-form-hook");
  const input = documentRef.getElementById("pet-chat-input-hook");
  const send = documentRef.getElementById("pet-chat-send-hook");

  if (root) {
    root.dataset.bubbleState = state;
    root.dataset.bubbleSource = options.source || config.source;
  }

  if (bubble) {
    bubble.dataset.state = state;
    bubble.dataset.source = options.source || config.source;
    bubble.setAttribute("aria-expanded", expanded ? "true" : "false");
    bubble.hidden = !expanded;
  }

  setText(title, options.title || "Bubble Chat");
  setText(status, options.statusText || config.statusText);
  setText(message, options.message || config.message);
  setText(response, options.response || config.response);

  if (status) {
    status.dataset.source = options.source || config.source;
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
    const isLongReply = nextState === "long_reply";
    const stateMessage =
      nextState === "fallback_mock" || nextState === "llm_local_error"
        ? BUBBLE_STATES[nextState].message
        : isLongReply
          ? BUBBLE_STATES.long_reply.message
          : PET_MODE_DEFAULTS.bubbleMessage;

    setBubbleState(documentRef, nextState, {
      source: data.source,
      statusText,
      message: stateMessage,
      response: isLongReply ? PET_LONG_REPLY_HINT : data.reply,
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
  return callPetApiAction(
    documentRef,
    "resetPetPosition",
    "Resetting Pet position...",
    "Reset Pet Position is not available in this preview."
  );
}

function handleHidePetWindow(documentRef = document) {
  return callPetApiAction(
    documentRef,
    "hidePetWindow",
    "Hiding Pet Window...",
    "Hide Pet Window is not available in this preview."
  );
}

function renderPetSpeechUpdate(documentRef = document, payload = {}) {
  const reply = typeof payload.reply === "string" ? payload.reply : "";
  const mood = typeof payload.mood === "string" ? payload.mood : PET_MODE_DEFAULTS.expression;
  const source = typeof payload.source === "string" ? payload.source : "unknown";
  const nextState = stateForChatSource(source, reply);
  const isReplyLong = nextState === "long_reply";

  return setBubbleState(documentRef, nextState, {
    source,
    statusText: sourceStatusLabel(source),
    message: isReplyLong ? BUBBLE_STATES.long_reply.message : PET_MODE_DEFAULTS.bubbleMessage,
    response: isReplyLong ? PET_LONG_REPLY_HINT : reply,
    mood,
  });
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
  const menuOpenFullApp = documentRef.getElementById("pet-menu-open-full-app");
  const menuResetPosition = documentRef.getElementById("pet-menu-reset-position");
  const menuHideWindow = documentRef.getElementById("pet-menu-hide-window");
  const menuClose = documentRef.getElementById("pet-menu-close");

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

  setBubbleState(documentRef, "collapsed");
  closeMenu(documentRef);

  if (bubblePlaceholder && !bubblePlaceholder.textContent.trim()) {
    setText(
      bubblePlaceholder,
      "Display-only speech bubble. Type in Full App."
    );
  }

  if (dragRegion && typeof dragRegion.addEventListener === "function") {
    dragRegion.addEventListener("click", () => expandBubble(documentRef));
  }

  if (bubbleOpenHook && typeof bubbleOpenHook.addEventListener === "function") {
    bubbleOpenHook.addEventListener("click", () => expandBubble(documentRef));
  }

  if (bubbleCloseHook && typeof bubbleCloseHook.addEventListener === "function") {
    bubbleCloseHook.addEventListener("click", () => collapseBubble(documentRef));
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
    openFullAppHook.addEventListener("click", () => handleOpenFullApp(documentRef));
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

  if (menuOpenFullApp && typeof menuOpenFullApp.addEventListener === "function") {
    menuOpenFullApp.addEventListener("click", () => {
      handleOpenFullApp(documentRef);
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

  if (menuClose && typeof menuClose.addEventListener === "function") {
    menuClose.addEventListener("click", () => closeMenu(documentRef));
  }

  if (typeof documentRef.addEventListener === "function") {
    documentRef.addEventListener("keydown", (event) => {
      if (event && event.key === "Escape") {
        closeMenu(documentRef);
      }
    });
  }

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
    PET_LONG_REPLY_HINT,
    PET_MODE_DEFAULTS,
    PET_REPLY_LONG_THRESHOLD,
    buildChatPayload,
    collapseBubble,
    closeMenu,
    expandBubble,
    expressionForBubbleState,
    getPetBackendUrl,
    getBubbleStateConfig,
    handleBubbleInput,
    handleChatSubmit,
    handleOpenFullApp,
    handleHidePetWindow,
    handlePlaceholderSubmit,
    handleResetPetPosition,
    initializePetMode,
    isLongReply,
    isMenuOpen,
    openMenu,
    parseChatResponse,
    renderPetSpeechUpdate,
    sendPetChatMessage,
    setBubbleState,
    setMenuState,
    setPetExpression,
    setPetExpressionForBubbleState,
    normalizePetMood,
    sourceStatusLabel,
    stateForChatSource,
    toggleBubble,
    toggleMenu,
  };
}
