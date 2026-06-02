(function () {
  "use strict";

  // TASK-238: Output Queue engine — extracted from renderer.js.
  // Exposes window.dragonOutputQueue; renderer.js delegates via thin wrappers.
  // Classic browser script (no ESM, no bundler). Loaded before renderer.js.

  const OUTPUT_QUEUE_ENABLED = false;
  const OUTPUT_QUEUE_MAX = 50;
  const OUTPUT_QUEUE_RECENT_MAX = 20;
  const OUTPUT_PRIORITY_ALLOWLIST = new Set([
    "P0_CRITICAL",
    "P1_USER_DIRECT",
    "P2_LLM_REPLY",
    "P3_IMPORTANT_REACTION",
    "P4_NORMAL_REACTION",
    "P5_IDLE_AMBIENT",
    "P6_DIAGNOSTICS",
  ]);
  const OUTPUT_CHANNEL_ALLOWLIST = new Set([
    "visual_expression",
    "pet_bubble",
    "full_app_chat",
    "tts_audio",
    "diagnostics_preview",
    "notification",
  ]);
  const OUTPUT_SOURCE_ALLOWLIST = new Set([
    "chat_reply",
    "manual_pet_input",
    "reaction_bubble",
    "expression_mirror",
    "idle_reaction",
    "tts_playback",
    "stt_transcript",
    "notification",
    "diagnostics_preview",
    "safety_error",
  ]);
  const CHAT_REPLY_SAFE_SOURCE_ALLOWLIST = new Set([
    "llm_local",
    "llm_real",
    "llm_local_error",
    "llm_real_error",
    "unknown",
  ]);
  const OUTPUT_FORBIDDEN_KEYS = new Set([
    "message",
    "text",
    "body",
    "rawText",
    "content",
    "reply",
    "transcript",
    "audio",
    "html",
    "innerHTML",
    "metadata",
    "debug",
    "thinking",
  ]);
  const OUTPUT_SAFE_PAYLOAD_KEYS = new Set([
    "expression",
    "bubbleId",
    "state",
    "action",
    "reason",
    "source",
    "mood",
    "replyLength",
  ]);
  const OUTPUT_PRIORITY_ORDER = [
    "P0_CRITICAL",
    "P1_USER_DIRECT",
    "P2_LLM_REPLY",
    "P3_IMPORTANT_REACTION",
    "P4_NORMAL_REACTION",
    "P5_IDLE_AMBIENT",
    "P6_DIAGNOSTICS",
  ];

  // Module-private allowlist values for sanitizeOutputQueuePayload.
  // Mirror definitions in renderer.js — must stay in sync.
  const _EXPRESSION_ALLOWLIST = new Set(["neutral", "focused", "happy", "proud", "annoyed", "sleepy"]);
  const _BUBBLE_ID_ALLOWLIST = new Set(["user_active", "message_management", "correction", "reset", "attention_returned", "none"]);
  const _ACTION_ALLOWLIST = new Set(["none", "mirror_expression", "show_reaction_bubble", "mirror_expression_and_bubble"]);
  const _MOOD_ALLOWLIST = new Set(["neutral", "focused", "happy", "proud", "annoyed", "sleepy"]);
  const _ATTENTION_ALLOWLIST = new Set(["idle", "active", "returned", "managing", "correcting", "reset"]);
  const _ENERGY_ALLOWLIST = new Set(["calm", "attentive", "lively", "resting"]);
  const _INTERACTION_LEVEL_ALLOWLIST = new Set(["none", "low", "medium", "high"]);

  var outputQueueItems = [];
  var recentOutputQueueItems = [];
  var currentActiveOutputItem = null;
  var currentOutputQueueSnapshot = {
    enabled: OUTPUT_QUEUE_ENABLED,
    length: 0,
    recentLength: 0,
    nextItem: null,
    winnerItem: null,
    activeItem: null,
  };
  var outputQueueIdCounter = 0;

  function sanitizeOutputQueueReason(value) {
    if (typeof value !== "string") return "";
    return value.replace(/[^a-zA-Z0-9_:/.-]/g, "").slice(0, 80);
  }

  function sanitizeOutputQueuePayload(payload) {
    const source = payload && typeof payload === "object" ? payload : {};
    const safe = {};
    for (const [key, value] of Object.entries(source)) {
      if (OUTPUT_FORBIDDEN_KEYS.has(key) || !OUTPUT_SAFE_PAYLOAD_KEYS.has(key)) continue;
      if (key === "expression") {
        safe.expression = _EXPRESSION_ALLOWLIST.has(value) ? value : "neutral";
      } else if (key === "bubbleId") {
        safe.bubbleId = _BUBBLE_ID_ALLOWLIST.has(value) ? value : "none";
      } else if (key === "action") {
        safe.action = _ACTION_ALLOWLIST.has(value) ? value : "none";
      } else if (key === "reason") {
        safe.reason = sanitizeOutputQueueReason(value);
      } else if (key === "state" && value && typeof value === "object") {
        safe.state = {
          mood: _MOOD_ALLOWLIST.has(value.mood) ? value.mood : "neutral",
          attention: _ATTENTION_ALLOWLIST.has(value.attention) ? value.attention : "idle",
          energy: _ENERGY_ALLOWLIST.has(value.energy) ? value.energy : "calm",
          recentInteractionLevel: _INTERACTION_LEVEL_ALLOWLIST.has(value.recentInteractionLevel)
            ? value.recentInteractionLevel
            : "none",
        };
      } else if (key === "source") {
        safe.source = CHAT_REPLY_SAFE_SOURCE_ALLOWLIST.has(value) ? value : "unknown";
      } else if (key === "mood") {
        safe.mood = _MOOD_ALLOWLIST.has(value) ? value : "neutral";
      } else if (key === "replyLength") {
        safe.replyLength = Math.max(0, Math.min(10000, typeof value === "number" && Number.isFinite(value) ? Math.floor(value) : 0));
      }
    }
    return safe;
  }

  function cloneOutputQueueItemSummary(item) {
    if (!item || typeof item !== "object") return null;
    return {
      id: item.id,
      source: item.source,
      priority: item.priority,
      channel: item.channel,
      payload: sanitizeOutputQueuePayload(item.payload),
      createdAt: item.createdAt,
      ttlMs: item.ttlMs,
      interruptible: item.interruptible,
      ttsEligible: item.ttsEligible,
      historyEligible: item.historyEligible,
      copyExportEligible: item.copyExportEligible,
      reason: item.reason,
    };
  }

  function cloneOutputQueueNextItemSummary(item) {
    if (!item || typeof item !== "object") return null;
    if (!OUTPUT_SOURCE_ALLOWLIST.has(item.source)) return null;
    if (!OUTPUT_PRIORITY_ALLOWLIST.has(item.priority)) return null;
    if (!OUTPUT_CHANNEL_ALLOWLIST.has(item.channel)) return null;
    return {
      id: typeof item.id === "string" ? item.id.slice(0, 80) : "",
      source: item.source,
      priority: item.priority,
      channel: item.channel,
      reason: sanitizeOutputQueueReason(item.reason),
      ttlMs: Number.isFinite(item.ttlMs) && item.ttlMs > 0 ? item.ttlMs : 0,
    };
  }

  function outputPriorityIndex(value) {
    const raw = value && typeof value === "object" ? value.priority : value;
    const priority = OUTPUT_PRIORITY_ALLOWLIST.has(raw) ? raw : "P6_DIAGNOSTICS";
    return OUTPUT_PRIORITY_ORDER.indexOf(priority);
  }

  function compareOutputPriority(a, b) {
    return outputPriorityIndex(b) - outputPriorityIndex(a);
  }

  function getOutputQueuePriorityWinner(items) {
    if (!Array.isArray(items) || items.length === 0) return null;
    let winner = null;
    for (const item of items) {
      if (!item || !OUTPUT_SOURCE_ALLOWLIST.has(item.source)
          || !OUTPUT_PRIORITY_ALLOWLIST.has(item.priority)
          || !OUTPUT_CHANNEL_ALLOWLIST.has(item.channel)) continue;
      if (!winner || compareOutputPriority(item, winner) > 0) {
        winner = item;
      }
    }
    return winner ? cloneOutputQueueNextItemSummary(winner) : null;
  }

  function cloneOutputQueueActiveItemSummary(item) {
    if (!item || typeof item !== "object") return null;
    if (!OUTPUT_SOURCE_ALLOWLIST.has(item.source)) return null;
    if (!OUTPUT_PRIORITY_ALLOWLIST.has(item.priority)) return null;
    if (!OUTPUT_CHANNEL_ALLOWLIST.has(item.channel)) return null;
    return {
      source: item.source,
      priority: item.priority,
      channel: item.channel,
      reason: sanitizeOutputQueueReason(item.reason),
      ttlMs: Number.isFinite(item.ttlMs) && item.ttlMs > 0 ? item.ttlMs : 0,
    };
  }

  function getActiveOutputItemSnapshot() {
    return cloneOutputQueueActiveItemSummary(currentActiveOutputItem);
  }

  function updateOutputQueueSnapshot() {
    currentOutputQueueSnapshot = {
      enabled: OUTPUT_QUEUE_ENABLED,
      length: outputQueueItems.length,
      recentLength: recentOutputQueueItems.length,
      nextItem: outputQueueItems.length ? cloneOutputQueueNextItemSummary(outputQueueItems[0]) : null,
      winnerItem: getOutputQueuePriorityWinner(outputQueueItems),
      activeItem: getActiveOutputItemSnapshot(),
    };
    return currentOutputQueueSnapshot;
  }

  function sanitizeOutputQueueItem(input) {
    const source = input && typeof input === "object" ? input : null;
    if (!source) return null;
    if (!OUTPUT_SOURCE_ALLOWLIST.has(source.source)) return null;
    if (!OUTPUT_PRIORITY_ALLOWLIST.has(source.priority)) return null;
    if (!OUTPUT_CHANNEL_ALLOWLIST.has(source.channel)) return null;
    const createdAt = Number.isFinite(source.createdAt) && source.createdAt > 0
      ? source.createdAt
      : Date.now();
    const ttlMs = Number.isFinite(source.ttlMs) && source.ttlMs > 0 ? source.ttlMs : 0;
    outputQueueIdCounter += 1;
    return {
      id: typeof source.id === "string" && source.id.startsWith("oq_")
        ? source.id.slice(0, 80)
        : "oq_" + createdAt + "_" + outputQueueIdCounter,
      source: source.source,
      priority: source.priority,
      channel: source.channel,
      payload: sanitizeOutputQueuePayload(source.payload),
      createdAt,
      ttlMs,
      interruptible: source.interruptible === true,
      ttsEligible: source.ttsEligible === true,
      historyEligible: source.historyEligible === true,
      copyExportEligible: source.copyExportEligible === true,
      reason: sanitizeOutputQueueReason(source.reason),
    };
  }

  function enqueueOutputQueueItem(input) {
    const item = sanitizeOutputQueueItem(input);
    if (!item) {
      updateOutputQueueSnapshot();
      return null;
    }
    outputQueueItems.push(item);
    if (outputQueueItems.length > OUTPUT_QUEUE_MAX) {
      outputQueueItems.splice(0, outputQueueItems.length - OUTPUT_QUEUE_MAX);
    }
    recentOutputQueueItems.push(cloneOutputQueueItemSummary(item));
    if (recentOutputQueueItems.length > OUTPUT_QUEUE_RECENT_MAX) {
      recentOutputQueueItems.splice(0, recentOutputQueueItems.length - OUTPUT_QUEUE_RECENT_MAX);
    }
    updateOutputQueueSnapshot();
    return cloneOutputQueueItemSummary(item);
  }

  function getOutputQueueSnapshot() {
    return {
      enabled: OUTPUT_QUEUE_ENABLED,
      length: outputQueueItems.length,
      recentLength: recentOutputQueueItems.length,
      nextItem: outputQueueItems.length ? cloneOutputQueueNextItemSummary(outputQueueItems[0]) : null,
      winnerItem: getOutputQueuePriorityWinner(outputQueueItems),
      activeItem: getActiveOutputItemSnapshot(),
    };
  }

  function clearOutputQueue(reason) {
    sanitizeOutputQueueReason(reason);
    // Splice for in-place mutation — renderer.js holds a stable reference to this array.
    outputQueueItems.splice(0);
    updateOutputQueueSnapshot();
    return currentOutputQueueSnapshot;
  }

  function shouldOutputPreempt(activeItem, incomingItem) {
    const active = OUTPUT_PRIORITY_ORDER[outputPriorityIndex(activeItem)] || "P6_DIAGNOSTICS";
    const incoming = OUTPUT_PRIORITY_ORDER[outputPriorityIndex(incomingItem)] || "P6_DIAGNOSTICS";
    if (incoming === "P6_DIAGNOSTICS") return false;
    if (!activeItem) return true;
    if (incoming === "P0_CRITICAL") return true;
    if (incoming === "P1_USER_DIRECT") return active !== "P0_CRITICAL" && active !== "P1_USER_DIRECT";
    if (active === "P2_LLM_REPLY"
        && ["P3_IMPORTANT_REACTION", "P4_NORMAL_REACTION", "P5_IDLE_AMBIENT"].includes(incoming)) {
      return false;
    }
    if (incoming === "P3_IMPORTANT_REACTION") {
      return active === "P4_NORMAL_REACTION" || active === "P5_IDLE_AMBIENT";
    }
    if (incoming === "P4_NORMAL_REACTION") {
      return active === "P5_IDLE_AMBIENT" || active === "P6_DIAGNOSTICS";
    }
    return false;
  }

  function setActiveOutputItemForDiagnosticsOnly(item) {
    const sanitized = cloneOutputQueueActiveItemSummary(item);
    currentActiveOutputItem = sanitized;
    updateOutputQueueSnapshot();
    return sanitized;
  }

  function clearActiveOutputItem() {
    currentActiveOutputItem = null;
    updateOutputQueueSnapshot();
  }

  function formatOutputQueueSnapshotPreview(snapshot) {
    const source = (snapshot != null && typeof snapshot === "object") ? snapshot : getOutputQueueSnapshot();
    const enabled = source.enabled === true ? "enabled" : "disabled";
    const length = Number.isFinite(source.length) && source.length >= 0 ? source.length : 0;
    const recentLength = Number.isFinite(source.recentLength) && source.recentLength >= 0 ? source.recentLength : 0;
    const next = source.nextItem && typeof source.nextItem === "object" ? source.nextItem : null;
    const hasValidNext = next
      && OUTPUT_PRIORITY_ALLOWLIST.has(next.priority)
      && OUTPUT_CHANNEL_ALLOWLIST.has(next.channel)
      && OUTPUT_SOURCE_ALLOWLIST.has(next.source);
    const nextText = hasValidNext
      ? next.priority + "/" + next.channel + "/" + next.source
      : "none";
    const winner = source.winnerItem && typeof source.winnerItem === "object" ? source.winnerItem : null;
    const hasValidWinner = winner
      && OUTPUT_PRIORITY_ALLOWLIST.has(winner.priority)
      && OUTPUT_CHANNEL_ALLOWLIST.has(winner.channel)
      && OUTPUT_SOURCE_ALLOWLIST.has(winner.source);
    const winnerText = hasValidWinner
      ? winner.priority + "/" + winner.channel + "/" + winner.source
      : "none";
    const active = source.activeItem && typeof source.activeItem === "object" ? source.activeItem : null;
    const hasValidActive = active
      && OUTPUT_PRIORITY_ALLOWLIST.has(active.priority)
      && OUTPUT_CHANNEL_ALLOWLIST.has(active.channel)
      && OUTPUT_SOURCE_ALLOWLIST.has(active.source);
    const activeText = hasValidActive
      ? active.priority + "/" + active.channel + "/" + active.source
      : "none";
    return "Queue: " + enabled
      + " · Items: " + length
      + " · Recent: " + recentLength
      + " · Next: " + nextText
      + " · Winner: " + winnerText
      + " · Active: " + activeText;
  }

  const api = {
    OUTPUT_QUEUE_ENABLED,
    CHAT_REPLY_SAFE_SOURCE_ALLOWLIST,
    get outputQueueItems() { return outputQueueItems; },
    get recentOutputQueueItems() { return recentOutputQueueItems; },
    sanitizeOutputQueueReason,
    sanitizeOutputQueuePayload,
    cloneOutputQueueItemSummary,
    cloneOutputQueueNextItemSummary,
    updateOutputQueueSnapshot,
    sanitizeOutputQueueItem,
    enqueueOutputQueueItem,
    getOutputQueueSnapshot,
    clearOutputQueue,
    outputPriorityIndex,
    compareOutputPriority,
    shouldOutputPreempt,
    getOutputQueuePriorityWinner,
    cloneOutputQueueActiveItemSummary,
    getActiveOutputItemSnapshot,
    setActiveOutputItemForDiagnosticsOnly,
    clearActiveOutputItem,
    formatOutputQueueSnapshotPreview,
  };

  window.dragonOutputQueue = api;
})();
