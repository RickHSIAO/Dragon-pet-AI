"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app";
const PET_RESET_POSITION_CHANNEL = "pet:reset-position";
const PET_HIDE_WINDOW_CHANNEL = "pet:hide-window";
const PET_SPEECH_RECEIVED_CHANNEL = "pet:speech-received";
const PET_QUIET_MODE_SET_CHANNEL = "pet:set-quiet-mode";  // TASK-162
const PET_SCALE_SET_CHANNEL = "pet:set-scale";            // TASK-166B
const PET_CLICK_THROUGH_SET_CHANNEL = "pet:set-click-through";  // TASK-166D
const PET_STT_TRANSCRIBE_CHANNEL = "stt:transcribe";           // TASK-167B
const PET_CHAT_MIRROR_CHANNEL = "pet:chat-mirror";             // TASK-193
const PET_UNREAD_DOT_RECEIVED_CHANNEL = "pet:unread-dot-received";  // TASK-204
const PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet:expression-suggestion-received"; // TASK-218
const EXPRESSION_SUGGESTION_ALLOWLIST_PET = new Set([             // TASK-218: pet-preload-side allowlist
  "neutral", "focused", "happy", "proud", "annoyed", "sleepy",
]);

function sanitizePetSpeechPayload(payload = {}) {
  return {
    reply: typeof payload.reply === "string" ? payload.reply : "",
    mood: typeof payload.mood === "string" ? payload.mood : "neutral",
    source: typeof payload.source === "string" ? payload.source : "unknown",
  };
}

// TASK-193: sanitize mirror payload before sending to main — text-only, no blobs.
function sanitizeMirrorPayload(payload = {}) {
  return {
    userMessage: typeof payload.userMessage === "string" ? payload.userMessage.slice(0, 2000) : "",
    reply: typeof payload.reply === "string" ? payload.reply.slice(0, 800) : "",
    mood: typeof payload.mood === "string" ? payload.mood.slice(0, 30) : "neutral",
    source: typeof payload.source === "string" ? payload.source.slice(0, 30) : "unknown",
    inputMethod: payload.inputMethod === "voice" ? "voice" : "text",  // TASK-195
  };
}

function sanitizeUnreadPayload(payload = {}) {  // TASK-204
  return {
    unreadCount: typeof payload.unreadCount === "number" && payload.unreadCount >= 0
      ? payload.unreadCount : 0,
  };
}

function onUnreadUpdate(callback) {  // TASK-204
  if (typeof callback !== "function") {
    return () => {};
  }
  const listener = (_event, payload) => {
    callback(sanitizeUnreadPayload(payload));
  };
  ipcRenderer.on(PET_UNREAD_DOT_RECEIVED_CHANNEL, listener);
  return () => {
    ipcRenderer.removeListener(PET_UNREAD_DOT_RECEIVED_CHANNEL, listener);
  };
}

// TASK-218: expose narrow listener for expression suggestion events from main.
function onExpressionSuggestion(callback) {
  if (typeof callback !== "function") return () => {};
  const listener = (_event, payload) => {
    const rawExpression = typeof payload === "object" && payload !== null &&
      typeof payload.expression === "string" ? payload.expression : "";
    const safeExpression = EXPRESSION_SUGGESTION_ALLOWLIST_PET.has(rawExpression)
      ? rawExpression : "neutral";
    callback({
      expression: safeExpression,
      source: "interaction_expression_suggestion",
      ts: typeof payload.ts === "number" && payload.ts > 0 ? payload.ts : Date.now(),
    });
  };
  ipcRenderer.on(PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL, listener);
  return () => ipcRenderer.removeListener(PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL, listener);
}

function onSpeechUpdate(callback) {
  if (typeof callback !== "function") {
    return () => {};
  }

  const listener = (_event, payload) => {
    callback(sanitizePetSpeechPayload(payload));
  };

  ipcRenderer.on(PET_SPEECH_RECEIVED_CHANNEL, listener);
  return () => {
    ipcRenderer.removeListener(PET_SPEECH_RECEIVED_CHANNEL, listener);
  };
}

contextBridge.exposeInMainWorld(
  "dragonPet",
  Object.freeze({
    openFullApp: () => ipcRenderer.invoke(PET_OPEN_FULL_APP_CHANNEL),
    resetPetPosition: () => ipcRenderer.invoke(PET_RESET_POSITION_CHANNEL),
    hidePetWindow: () => ipcRenderer.invoke(PET_HIDE_WINDOW_CHANNEL),
    onSpeechUpdate,
    onUnreadUpdate,      // TASK-204
    onExpressionSuggestion, // TASK-218
    setQuietMode: (value) => ipcRenderer.invoke(PET_QUIET_MODE_SET_CHANNEL, value === true),  // TASK-162
    setScale: (value) => ipcRenderer.invoke(PET_SCALE_SET_CHANNEL, value),  // TASK-166B
    setClickThrough: (enabled) => ipcRenderer.invoke(PET_CLICK_THROUGH_SET_CHANNEL, enabled === true),  // TASK-166D
    // TASK-167B: send audio ArrayBuffer to main for STT transcription via backend.
    // Returns Promise<{transcript: string, status: string}>.
    transcribeAudio: (arrayBuffer) => ipcRenderer.invoke(PET_STT_TRANSCRIBE_CHANNEL, arrayBuffer),
    // TASK-193: send user text + AI reply to Full App chat via IPC bridge.
    // Payload is text-only; main sanitizes and forwards to fullAppWindow if available.
    mirrorChatToFullApp: (payload) => ipcRenderer.invoke(PET_CHAT_MIRROR_CHANNEL, sanitizeMirrorPayload(payload)),
  })
);
