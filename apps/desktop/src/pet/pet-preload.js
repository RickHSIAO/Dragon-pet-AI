"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app";
const PET_RESET_POSITION_CHANNEL = "pet:reset-position";
const PET_HIDE_WINDOW_CHANNEL = "pet:hide-window";

contextBridge.exposeInMainWorld(
  "dragonPet",
  Object.freeze({
    openFullApp: () => ipcRenderer.invoke(PET_OPEN_FULL_APP_CHANNEL),
    resetPetPosition: () => ipcRenderer.invoke(PET_RESET_POSITION_CHANNEL),
    hidePetWindow: () => ipcRenderer.invoke(PET_HIDE_WINDOW_CHANNEL),
  })
);
