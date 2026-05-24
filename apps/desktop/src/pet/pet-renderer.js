const PET_MODE_DEFAULTS = Object.freeze({
  expression: "neutral",
  hint: "\u54fc\uff0c\u6c5d\u53eb\u543e\u51fa\u4f86\u505a\u4ec0\u9ebc\uff1f",
  avatarSrc: "../renderer/assets/pet/christina/expressions/christina_neutral.png",
  bubbleMessage: "Bubble chat is not wired yet.",
});

function setText(element, value) {
  if (element) {
    element.textContent = value;
  }
}

function setBubbleState(documentRef, expanded) {
  const root = documentRef.getElementById("pet-mode-root");
  const bubble = documentRef.getElementById("pet-bubble");

  const state = expanded ? "expanded" : "collapsed";

  if (root) {
    root.dataset.bubbleState = state;
  }

  if (bubble) {
    bubble.dataset.state = state;
    bubble.setAttribute("aria-expanded", expanded ? "true" : "false");
    bubble.hidden = !expanded;
  }
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

function expandBubble(documentRef = document) {
  setBubbleState(documentRef, true);
}

function collapseBubble(documentRef = document) {
  setBubbleState(documentRef, false);
}

function toggleBubble(documentRef = document) {
  const bubble = documentRef.getElementById("pet-bubble");
  const shouldExpand = !bubble || bubble.dataset.state !== "expanded";
  setBubbleState(documentRef, shouldExpand);
}

function handlePlaceholderSubmit(event, documentRef = document) {
  if (event && typeof event.preventDefault === "function") {
    event.preventDefault();
  }

  const message = documentRef.getElementById("pet-bubble-message");
  setText(message, PET_MODE_DEFAULTS.bubbleMessage);
}

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

  collapseBubble(documentRef);
  closeMenu(documentRef);

  if (bubblePlaceholder && !bubblePlaceholder.textContent.trim()) {
    setText(
      bubblePlaceholder,
      "\u5c0d\u8a71\u6ce1\u6ce1\u9810\u7559\u5340\u3002TASK-118 \u53ea\u505a UI state\uff0c\u4e0d\u9023\u63a5 /chat\u3002"
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

  if (chatForm && typeof chatForm.addEventListener === "function") {
    chatForm.addEventListener("submit", (event) => handlePlaceholderSubmit(event, documentRef));
  }

  if (openFullAppHook && typeof openFullAppHook.addEventListener === "function") {
    openFullAppHook.addEventListener("click", () => handleOpenFullApp(documentRef));
  }

  if (root && typeof root.addEventListener === "function") {
    root.addEventListener("contextmenu", (event) => {
      if (event && typeof event.preventDefault === "function") {
        event.preventDefault();
      }
      openMenu(documentRef);
    });
  }

  if (contextMenuHook && typeof contextMenuHook.addEventListener === "function") {
    contextMenuHook.addEventListener("click", () => openMenu(documentRef));
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
    PET_MODE_DEFAULTS,
    collapseBubble,
    closeMenu,
    expandBubble,
    handleOpenFullApp,
    handleHidePetWindow,
    handlePlaceholderSubmit,
    handleResetPetPosition,
    initializePetMode,
    openMenu,
    setBubbleState,
    setMenuState,
    toggleBubble,
  };
}
