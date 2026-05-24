const PET_MODE_DEFAULTS = Object.freeze({
  expression: "neutral",
  hint: "\u54fc\uff0c\u6c5d\u53eb\u543e\u51fa\u4f86\u505a\u4ec0\u9ebc\uff1f",
  avatarSrc: "../renderer/assets/pet/christina/expressions/christina_neutral.png",
});

function setText(element, value) {
  if (element) {
    element.textContent = value;
  }
}

function initializePetMode(documentRef = document) {
  const root = documentRef.getElementById("pet-mode-root");
  const avatarContainer = documentRef.getElementById("pet-avatar-container");
  const avatar = documentRef.getElementById("pet-avatar");
  const hint = documentRef.getElementById("pet-hint");
  const bubble = documentRef.getElementById("pet-bubble");
  const bubblePlaceholder = documentRef.getElementById("pet-bubble-placeholder");

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

  if (bubble) {
    bubble.dataset.state = "placeholder";
    bubble.setAttribute("aria-expanded", "false");
  }

  if (bubblePlaceholder && !bubblePlaceholder.textContent.trim()) {
    setText(
      bubblePlaceholder,
      "\u5c0d\u8a71\u6ce1\u6ce1\u9810\u7559\u5340\u3002TASK-115 \u4e0d\u9023\u63a5 /chat\u3002"
    );
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
    initializePetMode,
  };
}
