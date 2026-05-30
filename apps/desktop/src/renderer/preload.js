"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_SHOW_WINDOW_CHANNEL = "pet:show-window";
const PET_SPEECH_UPDATE_CHANNEL = "pet:speech-update";
const PET_CHAT_MIRROR_RECEIVED_CHANNEL = "pet:chat-mirror-received";  // TASK-193
const SCREEN_CAPTURE_ONCE_CHANNEL   = "screen:capture-once";    // TASK-171A
const SCREEN_CAPTURE_WINDOW_CHANNEL = "screen:capture-window";  // TASK-176

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
    });
  };
  ipcRenderer.on(PET_CHAT_MIRROR_RECEIVED_CHANNEL, listener);
  return () => ipcRenderer.removeListener(PET_CHAT_MIRROR_RECEIVED_CHANNEL, listener);
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
  })
);
