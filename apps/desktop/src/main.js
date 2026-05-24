/**
 * dragon-pet-ai — Electron main process
 *
 * TASK-003: Minimal skeleton window.
 * - Opens a BrowserWindow pointing to renderer/index.html
 * - No IPC handlers yet (renderer calls backend directly via fetch)
 * - No shell execution, no file system access, no live2D
 */

const { app, BrowserWindow } = require("electron");
const path = require("path");

const BACKEND_URL = "http://localhost:8000";
const PET_MODE_ENABLED = process.env.PET_MODE_ENABLED === "true";

let petWindow = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 480,
    height: 680,
    minWidth: 360,
    minHeight: 500,
    title: "Dragon Pet AI",
    webPreferences: {
      // nodeIntegration disabled — renderer uses fetch() for backend calls
      nodeIntegration: false,
      contextIsolation: true,
    },
    resizable: true,
    // alwaysOnTop can be enabled by user preference in a later task
    alwaysOnTop: false,
  });

  win.loadFile(path.join(__dirname, "renderer", "index.html"));

  // Pass backend URL to renderer via URL query param
  // (avoids need for IPC or preload for skeleton phase)
  win.loadURL(
    `file://${path.join(__dirname, "renderer", "index.html")}?backend=${encodeURIComponent(BACKEND_URL)}`
  );
}

function createPetWindow() {
  if (petWindow && !petWindow.isDestroyed()) {
    petWindow.focus();
    return petWindow;
  }

  petWindow = new BrowserWindow({
    width: 220,
    height: 280,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    show: false,
    title: "Dragon Pet AI - Pet Mode",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
    },
  });

  petWindow.once("ready-to-show", () => {
    if (petWindow && !petWindow.isDestroyed()) {
      petWindow.show();
    }
  });

  petWindow.on("closed", () => {
    petWindow = null;
  });

  petWindow.loadFile(path.join(__dirname, "pet", "pet.html"));
  return petWindow;
}

app.whenReady().then(() => {
  createWindow();
  if (PET_MODE_ENABLED) {
    createPetWindow();
  }

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
      if (PET_MODE_ENABLED) {
        createPetWindow();
      }
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
