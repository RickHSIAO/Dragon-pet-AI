(function () {
  "use strict";

  // TASK-239: Diagnostics Drawer engine — extracted from renderer.js.
  // Exposes window.dragonDiagnosticsDrawer; renderer.js delegates via thin wrappers.
  // Classic browser script (no ESM, no bundler). Loaded after output-queue.js, before renderer.js.

  var _expanded = false;

  var _HINT_ALLOWLIST = new Set([
    "user_active",
    "message_management",
    "correction",
    "reset",
    "attention_returned",
    "pet_attention",
    "none",
  ]);
  var _EXPRESSION_ALLOWLIST = new Set([
    "neutral",
    "focused",
    "happy",
    "proud",
    "annoyed",
    "sleepy",
  ]);
  var _ACTION_ALLOWLIST = new Set([
    "none",
    "mirror_expression",
    "show_reaction_bubble",
    "mirror_expression_and_bubble",
  ]);
  var _MOOD_ALLOWLIST = new Set([
    "neutral",
    "focused",
    "happy",
    "proud",
    "annoyed",
    "sleepy",
  ]);
  var _ATTENTION_ALLOWLIST = new Set([
    "idle",
    "active",
    "returned",
    "managing",
    "correcting",
    "reset",
  ]);
  var _ENERGY_ALLOWLIST = new Set([
    "calm",
    "attentive",
    "lively",
    "resting",
  ]);
  var _LEVEL_ALLOWLIST = new Set([
    "none",
    "low",
    "medium",
    "high",
  ]);

  function formatCharacterStatePreview(state) {
    var source = state && typeof state === "object" ? state : {};
    var safeMood = _MOOD_ALLOWLIST.has(source.mood) ? source.mood : "neutral";
    var safeAttention = _ATTENTION_ALLOWLIST.has(source.attention) ? source.attention : "idle";
    var safeEnergy = _ENERGY_ALLOWLIST.has(source.energy) ? source.energy : "calm";
    var safeLevel = _LEVEL_ALLOWLIST.has(source.recentInteractionLevel) ? source.recentInteractionLevel : "none";
    return "State: " + safeMood + "/" + safeAttention + "/" + safeEnergy + " · Level: " + safeLevel;
  }

  function formatInteractionDiagnosticsPreview(context) {
    var source = context && typeof context === "object" ? context : {};
    var rawHint = typeof source.reactionHint === "string" ? source.reactionHint : "none";
    var rawExpression = typeof source.expression === "string" ? source.expression : "neutral";
    var decision = source.behaviorDecision && typeof source.behaviorDecision === "object"
      ? source.behaviorDecision
      : {};
    var safeHint = _HINT_ALLOWLIST.has(rawHint) ? rawHint : "none";
    var safeExpression = _EXPRESSION_ALLOWLIST.has(rawExpression) ? rawExpression : "neutral";
    var safeAction = decision && _ACTION_ALLOWLIST.has(decision.action) ? decision.action : "none";
    var state = source.characterState && typeof source.characterState === "object"
      ? source.characterState
      : {};
    var queueSnapshot = source.outputQueueSnapshot && typeof source.outputQueueSnapshot === "object"
      ? source.outputQueueSnapshot
      : null;
    var queuePreviewStr;
    if (typeof source.queuePreview === "string") {
      queuePreviewStr = source.queuePreview;
    } else if (window.dragonOutputQueue && typeof window.dragonOutputQueue.formatOutputQueueSnapshotPreview === "function") {
      queuePreviewStr = window.dragonOutputQueue.formatOutputQueueSnapshotPreview(queueSnapshot);
    } else {
      queuePreviewStr = "Queue: disabled · Items: 0 · Recent: 0 · Next: none";
    }
    return "Reaction: " + safeHint
      + " · Suggestion: " + safeExpression
      + "\nDecision: " + safeAction
      + " · " + formatCharacterStatePreview(state)
      + "\n" + queuePreviewStr;
  }

  function formatInteractionDiagnosticsSummary(context) {
    var source = context && typeof context === "object" ? context : {};
    var rawHint = typeof source.reactionHint === "string" ? source.reactionHint : "none";
    var rawExpression = typeof source.expression === "string" ? source.expression : "neutral";
    var safeHint = _HINT_ALLOWLIST.has(rawHint) ? rawHint : "none";
    var safeExpression = _EXPRESSION_ALLOWLIST.has(rawExpression) ? rawExpression : "neutral";
    var queueSnapshot = source.outputQueueSnapshot && typeof source.outputQueueSnapshot === "object"
      ? source.outputQueueSnapshot
      : null;
    var queueEnabled = queueSnapshot && queueSnapshot.enabled === true ? "Queue enabled" : "Queue disabled";
    var itemCount = queueSnapshot && Number.isFinite(queueSnapshot.length) && queueSnapshot.length >= 0
      ? queueSnapshot.length
      : 0;
    return "Reaction: " + safeHint
      + " · Suggestion: " + safeExpression
      + " · " + queueEnabled
      + " · Items " + itemCount;
  }

  function formatInteractionDiagnosticsDetails(context) {
    var hasContext = context && typeof context === "object" && Object.keys(context).length > 0;
    return hasContext ? formatInteractionDiagnosticsPreview(context) : formatInteractionDiagnosticsPreview({});
  }

  function ensureInteractionDiagnosticsDrawerElements(container, summaryEl, toggleEl, detailsEl) {
    if (!container || !summaryEl || !toggleEl || !detailsEl) return;
    if (summaryEl.parentNode || toggleEl.parentNode || detailsEl.parentNode) return;
    var row = document.createElement("div");
    row.className = "diagnostics-summary-row";
    row.appendChild(summaryEl);
    row.appendChild(toggleEl);
    container.appendChild(row);
    container.appendChild(detailsEl);
    if (container.dataset) {
      container.dataset.syntheticDiagnosticsText = "true";
    }
  }

  function renderInteractionDiagnosticsPreview(opts) {
    var o = opts && typeof opts === "object" ? opts : {};
    var elements = o.elements && typeof o.elements === "object" ? o.elements : {};
    var el = elements.root || null;
    if (!el) return;
    var summaryEl = elements.summary || null;
    var toggleEl = elements.toggle || null;
    var detailsEl = elements.details || null;
    var context = {
      reactionHint: o.reactionHint,
      expression: o.expression,
      behaviorDecision: o.behaviorDecision,
      characterState: o.characterState,
      outputQueueSnapshot: o.outputQueueSnapshot,
      queuePreview: o.queuePreview,
    };
    var summary = formatInteractionDiagnosticsSummary(context);
    var details = formatInteractionDiagnosticsDetails(context);

    if (!summaryEl || !toggleEl || !detailsEl) {
      el.textContent = summary;
      return;
    }

    ensureInteractionDiagnosticsDrawerElements(el, summaryEl, toggleEl, detailsEl);
    summaryEl.textContent = summary;
    detailsEl.textContent = details;
    detailsEl.hidden = !_expanded;
    toggleEl.textContent = _expanded ? "Diagnostics ▾" : "Diagnostics ▸";
    toggleEl.setAttribute("aria-expanded", _expanded ? "true" : "false");
    toggleEl.setAttribute("aria-controls", "interaction-diagnostics-details");
    if (toggleEl.type !== "button") toggleEl.type = "button";
    if (_expanded) {
      el.classList.add("is-expanded");
      el.classList.remove("is-collapsed");
    } else {
      el.classList.add("is-collapsed");
      el.classList.remove("is-expanded");
    }
    if (el.dataset && el.dataset.syntheticDiagnosticsText === "true") {
      el.textContent = summary + "\n" + details;
    }
  }

  function toggleInteractionDiagnosticsDrawer() {
    _expanded = !_expanded;
  }

  function isInteractionDiagnosticsExpanded() {
    return _expanded;
  }

  function setInteractionDiagnosticsExpandedForTests(val) {
    _expanded = !!val;
  }

  var api = {
    formatCharacterStatePreview: formatCharacterStatePreview,
    formatInteractionDiagnosticsPreview: formatInteractionDiagnosticsPreview,
    formatInteractionDiagnosticsSummary: formatInteractionDiagnosticsSummary,
    formatInteractionDiagnosticsDetails: formatInteractionDiagnosticsDetails,
    ensureInteractionDiagnosticsDrawerElements: ensureInteractionDiagnosticsDrawerElements,
    renderInteractionDiagnosticsPreview: renderInteractionDiagnosticsPreview,
    toggleInteractionDiagnosticsDrawer: toggleInteractionDiagnosticsDrawer,
    isInteractionDiagnosticsExpanded: isInteractionDiagnosticsExpanded,
    setInteractionDiagnosticsExpandedForTests: setInteractionDiagnosticsExpandedForTests,
  };
  window.dragonDiagnosticsDrawer = api;
})();
