"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_SHOW_WINDOW_CHANNEL = "pet:show-window";
const PET_SPEECH_UPDATE_CHANNEL = "pet:speech-update";
const SCREEN_CAPTURE_ONCE_CHANNEL   = "screen:capture-once";    // TASK-171A
const SCREEN_CAPTURE_WINDOW_CHANNEL = "screen:capture-window";  // TASK-176

function sanitizePetSpeechPayload(payload = {}) {
  return {
    reply: typeof payload.reply === "string" ? payload.reply : "",
    mood: typeof payload.mood === "string" ? payload.mood : "neutral",
    source: typeof payload.source === "string" ? payload.source : "unknown",
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
  })
);
