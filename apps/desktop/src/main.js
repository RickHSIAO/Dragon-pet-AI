/**
 * dragon-pet-ai — Electron main process
 *
 * TASK-003: Minimal skeleton window.
 * - Opens a BrowserWindow pointing to renderer/index.html
 * - Full App renderer calls backend directly via fetch
 * - Pet Mode has a narrow IPC bridge for focusing the Full App only
 * - No shell execution, no file system access, no live2D
 */

const { app, BrowserWindow, ipcMain, screen } = require("electron");
const fs = require("fs");
const path = require("path");

const BACKEND_URL = "http://localhost:8000";
const PET_MODE_ENABLED = process.env.PET_MODE_ENABLED === "true";
const PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app";
const PET_RESET_POSITION_CHANNEL = "pet:reset-position";
const PET_HIDE_WINDOW_CHANNEL = "pet:hide-window";
const PET_WINDOW_WIDTH = 220;
const PET_WINDOW_HEIGHT = 280;
const PET_WINDOW_STATE_FILE = "pet-window-state.json";
const PET_WINDOW_EDGE_MARGIN = 24;
const PET_WINDOW_SAVE_DEBOUNCE_MS = 300;

let fullAppWindow = null;
let petWindow = null;
let petWindowSaveTimer = null;

function getPetWindowStatePath() {
  return path.join(app.getPath("userData"), PET_WINDOW_STATE_FILE);
}

function getDefaultPetWindowBounds() {
  const workArea = screen.getPrimaryDisplay().workArea;
  const x = Math.max(
    workArea.x,
    workArea.x + workArea.width - PET_WINDOW_WIDTH - PET_WINDOW_EDGE_MARGIN
  );
  const y = Math.max(
    workArea.y,
    workArea.y + workArea.height - PET_WINDOW_HEIGHT - PET_WINDOW_EDGE_MARGIN
  );

  return {
    x,
    y,
    width: PET_WINDOW_WIDTH,
    height: PET_WINDOW_HEIGHT,
  };
}

function isPetWindowBoundsVisible(bounds) {
  if (!bounds || !Number.isFinite(bounds.x) || !Number.isFinite(bounds.y)) {
    return false;
  }

  const normalizedBounds = {
    x: Math.round(bounds.x),
    y: Math.round(bounds.y),
    width: PET_WINDOW_WIDTH,
    height: PET_WINDOW_HEIGHT,
  };

  return screen.getAllDisplays().some(({ workArea }) => {
    const centerX = normalizedBounds.x + normalizedBounds.width / 2;
    const centerY = normalizedBounds.y + normalizedBounds.height / 2;
    const displayLeft = workArea.x;
    const displayRight = workArea.x + workArea.width;
    const displayTop = workArea.y;
    const displayBottom = workArea.y + workArea.height;

    return (
      centerX >= displayLeft &&
      centerX <= displayRight &&
      centerY >= displayTop &&
      centerY <= displayBottom
    );
  });
}

function loadPetWindowBounds() {
  try {
    const raw = fs.readFileSync(getPetWindowStatePath(), "utf8");
    const parsed = JSON.parse(raw);
    const savedBounds = {
      x: Number(parsed.x),
      y: Number(parsed.y),
      width: PET_WINDOW_WIDTH,
      height: PET_WINDOW_HEIGHT,
    };

    if (isPetWindowBoundsVisible(savedBounds)) {
      return savedBounds;
    }
  } catch (_error) {
    // Missing or invalid local state should never block Pet Mode startup.
  }

  return getDefaultPetWindowBounds();
}

function savePetWindowBounds(win = petWindow) {
  if (!win || win.isDestroyed()) {
    return;
  }

  const bounds = win.getBounds();
  const state = {
    x: bounds.x,
    y: bounds.y,
    width: PET_WINDOW_WIDTH,
    height: PET_WINDOW_HEIGHT,
  };

  try {
    fs.writeFileSync(getPetWindowStatePath(), `${JSON.stringify(state, null, 2)}\n`, "utf8");
  } catch (_error) {
    // Position persistence is best-effort and should not affect runtime use.
  }
}

function schedulePetWindowBoundsSave() {
  if (petWindowSaveTimer) {
    clearTimeout(petWindowSaveTimer);
  }

  petWindowSaveTimer = setTimeout(() => {
    petWindowSaveTimer = null;
    savePetWindowBounds();
  }, PET_WINDOW_SAVE_DEBOUNCE_MS);
}

function createWindow() {
  if (fullAppWindow && !fullAppWindow.isDestroyed()) {
    fullAppWindow.show();
    if (fullAppWindow.isMinimized()) {
      fullAppWindow.restore();
    }
    fullAppWindow.focus();
    return fullAppWindow;
  }

  fullAppWindow = new BrowserWindow({
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

  fullAppWindow.on("closed", () => {
    fullAppWindow = null;
  });

  fullAppWindow.loadFile(path.join(__dirname, "renderer", "index.html"));

  // Pass backend URL to renderer via URL query param
  // (avoids need for IPC or preload for skeleton phase)
  fullAppWindow.loadURL(
    `file://${path.join(__dirname, "renderer", "index.html")}?backend=${encodeURIComponent(BACKEND_URL)}`
  );

  return fullAppWindow;
}

function showFullAppWindow() {
  const win = createWindow();
  if (win.isMinimized()) {
    win.restore();
  }
  win.show();
  win.focus();
  return win;
}

function createPetWindow() {
  if (petWindow && !petWindow.isDestroyed()) {
    petWindow.focus();
    return petWindow;
  }

  const petBounds = loadPetWindowBounds();

  petWindow = new BrowserWindow({
    x: petBounds.x,
    y: petBounds.y,
    width: PET_WINDOW_WIDTH,
    height: PET_WINDOW_HEIGHT,
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
      preload: path.join(__dirname, "pet", "pet-preload.js"),
    },
  });

  petWindow.once("ready-to-show", () => {
    if (petWindow && !petWindow.isDestroyed()) {
      petWindow.show();
    }
  });

  petWindow.on("move", () => {
    schedulePetWindowBoundsSave();
  });

  petWindow.on("close", () => {
    savePetWindowBounds();
  });

  petWindow.on("closed", () => {
    if (petWindowSaveTimer) {
      clearTimeout(petWindowSaveTimer);
      petWindowSaveTimer = null;
    }
    petWindow = null;
  });

  petWindow.loadFile(path.join(__dirname, "pet", "pet.html"));
  return petWindow;
}

function resetPetWindowPosition() {
  if (!petWindow || petWindow.isDestroyed()) {
    return { ok: false };
  }

  const bounds = getDefaultPetWindowBounds();
  petWindow.setBounds(bounds);
  savePetWindowBounds(petWindow);
  return { ok: true };
}

function hidePetWindow() {
  if (!petWindow || petWindow.isDestroyed()) {
    return { ok: false };
  }

  savePetWindowBounds(petWindow);
  petWindow.hide();
  return { ok: true };
}

ipcMain.handle(PET_OPEN_FULL_APP_CHANNEL, () => {
  showFullAppWindow();
  return { ok: true };
});

ipcMain.handle(PET_RESET_POSITION_CHANNEL, () => resetPetWindowPosition());

ipcMain.handle(PET_HIDE_WINDOW_CHANNEL, () => hidePetWindow());

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
