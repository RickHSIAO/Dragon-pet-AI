"use strict";
/**
 * TASK-174: picker window preload.
 * Sends screen-picker:selected (with displayId) on click,
 * and screen-picker:cancel on Esc. Main process owns picker lifetime.
 * contextIsolation: true, nodeIntegration: false.
 * Normal renderer never receives raw display IDs from this module.
 */
const { ipcRenderer } = require("electron");

const SCREEN_PICKER_SELECTED_CHANNEL = "screen-picker:selected";
const SCREEN_PICKER_CANCEL_CHANNEL   = "screen-picker:cancel";

// Display ID injected via URL query string by main process when creating window.
const params    = new URLSearchParams(window.location.search);
const displayId = params.get("displayId") || "";

window.addEventListener("click", () => {
  ipcRenderer.send(SCREEN_PICKER_SELECTED_CHANNEL, displayId);
});

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    ipcRenderer.send(SCREEN_PICKER_CANCEL_CHANNEL);
  }
});
