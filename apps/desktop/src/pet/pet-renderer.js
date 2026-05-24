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
    expandBubble,
    handlePlaceholderSubmit,
    initializePetMode,
    setBubbleState,
    toggleBubble,
  };
}
