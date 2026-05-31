"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_SHOW_WINDOW_CHANNEL = "pet:show-window";
const PET_SPEECH_UPDATE_CHANNEL = "pet:speech-update";
const PET_CHAT_MIRROR_RECEIVED_CHANNEL = "pet:chat-mirror-received";  // TASK-193
const CHAT_HISTORY_APPEND_CHANNEL = "chat-history:append";  // TASK-194
const CHAT_HISTORY_LOAD_CHANNEL   = "chat-history:load";    // TASK-194
const CHAT_HISTORY_CLEAR_CHANNEL  = "chat-history:clear";   // TASK-194
const SCREEN_CAPTURE_ONCE_CHANNEL   = "screen:capture-once";    // TASK-171A
const SCREEN_CAPTURE_WINDOW_CHANNEL = "screen:capture-window";  // TASK-176
const CLIPBOARD_WRITE_TEXT_CHANNEL  = "clipboard:write-text";   // TASK-196

function sanitizePetSpeechPayload(payload = {}) {
  return {
    reply: typeof payload.reply === "string" ? payload.reply : "",
    mood: typeof payload.mood === "string" ? payload.mood : "neutral",
    source: typeof payload.source === "string" ? payload.source : "unknown",
  };
}

// TASK-193: expose listener for Pet chat mirror events forwarded from main.
// Only text payloads are forwarded — main sanitizes before sending to this window.
function onChatMirrorFromPet(callback) {
  if (typeof callback !== "function") return () => {};
  const listener = (_event, payload) => {
    callback({
      userMessage: typeof payload.userMessage === "string" ? payload.userMessage : "",
      reply: typeof payload.reply === "string" ? payload.reply : "",
      mood: typeof payload.mood === "string" ? payload.mood : "neutral",
      source: typeof payload.source === "string" ? payload.source : "unknown",
      inputMethod: payload.inputMethod === "voice" ? "voice" : "text",  // TASK-195
    });
  };
  ipcRenderer.on(PET_CHAT_MIRROR_RECEIVED_CHANNEL, listener);
  return () => ipcRenderer.removeListener(PET_CHAT_MIRROR_RECEIVED_CHANNEL, listener);
}

// TASK-194: validate entry before forwarding to main — only safe text fields accepted.
function sanitizeChatHistoryEntry(entry = {}) {
  return {
    role: entry.role === "user" || entry.role === "pet" ? entry.role : "",
    text: typeof entry.text === "string" ? entry.text.slice(0, 2000) : "",
    source: typeof entry.source === "string" ? entry.source.slice(0, 30) : "unknown",
  };
}

contextBridge.exposeInMainWorld(
  "dragonPet",
  Object.freeze({
    showPetWindow: () => ipcRenderer.invoke(PET_SHOW_WINDOW_CHANNEL),
    updatePetSpeech: (payload) =>
      ipcRenderer.invoke(PET_SPEECH_UPDATE_CHANNEL, sanitizePetSpeechPayload(payload)),
    // TASK-171A: narrow Full App screenshot capture surface.
    captureScreen: () => ipcRenderer.invoke(SCREEN_CAPTURE_ONCE_CHANNEL),
    // TASK-176: explicit window picker capture surface.
    captureWindow: () => ipcRenderer.invoke(SCREEN_CAPTURE_WINDOW_CHANNEL),
    // TASK-193: register listener for Pet chat mirror events.
    onChatMirrorFromPet,
    // TASK-194: chat history persistence IPC.
    chatHistoryAppend: (entry) => ipcRenderer.invoke(CHAT_HISTORY_APPEND_CHANNEL, sanitizeChatHistoryEntry(entry)),
    chatHistoryLoad:   () => ipcRenderer.invoke(CHAT_HISTORY_LOAD_CHANNEL),
    chatHistoryClear:  () => ipcRenderer.invoke(CHAT_HISTORY_CLEAR_CHANNEL),
    // TASK-196: narrow clipboard IPC bridge — routes via main IPC to avoid file:// secure-context restriction.
    writeClipboardText: (text) => {
      if (typeof text !== "string") return Promise.resolve(false);
      const safe = text.slice(0, 20000);
      if (!safe) return Promise.resolve(false);
      return ipcRenderer.invoke(CLIPBOARD_WRITE_TEXT_CHANNEL, safe);
    },
  })
);
