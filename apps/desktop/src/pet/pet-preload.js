"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app";
const PET_RESET_POSITION_CHANNEL = "pet:reset-position";
const PET_HIDE_WINDOW_CHANNEL = "pet:hide-window";
const PET_SPEECH_RECEIVED_CHANNEL = "pet:speech-received";
const PET_QUIET_MODE_SET_CHANNEL = "pet:set-quiet-mode";  // TASK-162
const PET_SCALE_SET_CHANNEL = "pet:set-scale";            // TASK-166B
const PET_CLICK_THROUGH_SET_CHANNEL = "pet:set-click-through";  // TASK-166D

function sanitizePetSpeechPayload(payload = {}) {
  return {
    reply: typeof payload.reply === "string" ? payload.reply : "",
    mood: typeof payload.mood === "string" ? payload.mood : "neutral",
    source: typeof payload.source === "string" ? payload.source : "unknown",
  };
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
    setQuietMode: (value) => ipcRenderer.invoke(PET_QUIET_MODE_SET_CHANNEL, value === true),  // TASK-162
    setScale: (value) => ipcRenderer.invoke(PET_SCALE_SET_CHANNEL, value),  // TASK-166B
    setClickThrough: (enabled) => ipcRenderer.invoke(PET_CLICK_THROUGH_SET_CHANNEL, enabled === true),  // TASK-166D
  })
);
