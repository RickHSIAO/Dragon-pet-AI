"use strict";
/**
 * TASK-176: window picker preload.
 * Receives a list of { index, name } objects from main process via window-picker:list.
 * Renders a clickable list of window names; user clicks to select.
 * Sends window-picker:selected (with integer index, NOT raw source ID) on click.
 * Sends window-picker:cancel on Esc.
 * Source IDs never pass through this preload — only ordinal indices.
 * contextIsolation: true, nodeIntegration: false.
 */
const { ipcRenderer } = require("electron");

const WINDOW_PICKER_LIST_CHANNEL     = "window-picker:list";
const WINDOW_PICKER_SELECTED_CHANNEL = "window-picker:selected";
const WINDOW_PICKER_CANCEL_CHANNEL   = "window-picker:cancel";

window.addEventListener("DOMContentLoaded", () => {
  const listEl  = document.getElementById("window-list");
  const noWinEl = document.getElementById("no-windows");

  ipcRenderer.on(WINDOW_PICKER_LIST_CHANNEL, (_event, windowList) => {
    if (!Array.isArray(windowList) || windowList.length === 0) {
      if (listEl)  listEl.style.display  = "none";
      if (noWinEl) noWinEl.style.display = "block";
      return;
    }

    windowList.forEach(({ index, name }) => {
      const item    = document.createElement("div");
      item.className = "window-item";

      const idxEl  = document.createElement("span");
      idxEl.className = "window-index";
      idxEl.textContent = String(index + 1);

      const nameEl = document.createElement("span");
      nameEl.className = "window-name";
      nameEl.textContent = typeof name === "string" ? name : "";

      item.appendChild(idxEl);
      item.appendChild(nameEl);

      item.addEventListener("click", () => {
        ipcRenderer.send(WINDOW_PICKER_SELECTED_CHANNEL, index);
      });

      if (listEl) listEl.appendChild(item);
    });
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      ipcRenderer.send(WINDOW_PICKER_CANCEL_CHANNEL);
    }
  });
});
