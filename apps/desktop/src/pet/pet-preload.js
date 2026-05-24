"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app";

contextBridge.exposeInMainWorld(
  "dragonPet",
  Object.freeze({
    openFullApp: () => ipcRenderer.invoke(PET_OPEN_FULL_APP_CHANNEL),
  })
);
