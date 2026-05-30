/**
 * dragon-pet-ai — Electron main process
 *
 * TASK-003: Minimal skeleton window.
 * - Opens a BrowserWindow pointing to renderer/index.html
 * - Full App renderer calls backend directly via fetch
 * - Full App and Pet Mode use narrow IPC bridges for window visibility only
 * - No shell execution, no file system access, no live2D
 */

const { app, BrowserWindow, desktopCapturer, ipcMain, screen } = require("electron");
const fs = require("fs");
const http = require("http");  // TASK-167B: used by stt:transcribe IPC handler
const path = require("path");

const BACKEND_URL = "http://localhost:8000";
const PET_MODE_ENABLED = process.env.PET_MODE_ENABLED === "true";
const PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app";
const PET_SHOW_WINDOW_CHANNEL = "pet:show-window";
const PET_RESET_POSITION_CHANNEL = "pet:reset-position";
const PET_HIDE_WINDOW_CHANNEL = "pet:hide-window";
const PET_SPEECH_UPDATE_CHANNEL = "pet:speech-update";
const PET_SPEECH_RECEIVED_CHANNEL = "pet:speech-received";
const PET_QUIET_MODE_SET_CHANNEL = "pet:set-quiet-mode";  // TASK-162
const PET_SCALE_SET_CHANNEL = "pet:set-scale";            // TASK-166B
const PET_CLICK_THROUGH_SET_CHANNEL = "pet:set-click-through";  // TASK-166D
const PET_STT_TRANSCRIBE_CHANNEL = "stt:transcribe";           // TASK-167B
const SCREEN_CAPTURE_ONCE_CHANNEL   = "screen:capture-once";      // TASK-171A
const SCREEN_PICKER_SELECTED_CHANNEL = "screen-picker:selected"; // TASK-174
const SCREEN_PICKER_CANCEL_CHANNEL   = "screen-picker:cancel";   // TASK-174
const PET_WINDOW_WIDTH = 300;   // Medium default — used as fallback constant
const PET_WINDOW_HEIGHT = 400;  // Medium default — used as fallback constant
// TASK-166B: scale preset dimensions
const PET_SCALE_SMALL  = Object.freeze({ name: "small",  width: 225, height: 300 });
const PET_SCALE_MEDIUM = Object.freeze({ name: "medium", width: 300, height: 400 });
const PET_SCALE_LARGE  = Object.freeze({ name: "large",  width: 375, height: 500 });
const PET_WINDOW_STATE_FILE = "pet-window-state.json";
const PET_WINDOW_EDGE_MARGIN = 24;
const PET_WINDOW_SAVE_DEBOUNCE_MS = 300;
const PET_SPEECH_REPLY_MAX_LENGTH = 800;

let fullAppWindow = null;
let petWindow = null;
let petWindowSaveTimer = null;

// TASK-166B: resolve scale name to dimension object; unknown/missing falls back to Medium
function getScaleDimensions(scaleName) {
  if (scaleName === "small") return PET_SCALE_SMALL;
  if (scaleName === "large") return PET_SCALE_LARGE;
  return PET_SCALE_MEDIUM;
}

function getPetWindowStatePath() {
  return path.join(app.getPath("userData"), PET_WINDOW_STATE_FILE);
}

// TASK-166B: accepts dims so reset and scale-change can use active scale dimensions
function getDefaultPetWindowBounds(dims = PET_SCALE_MEDIUM) {
  const workArea = screen.getPrimaryDisplay().workArea;
  const x = Math.max(
    workArea.x,
    workArea.x + workArea.width - dims.width - PET_WINDOW_EDGE_MARGIN
  );
  const y = Math.max(
    workArea.y,
    workArea.y + workArea.height - dims.height - PET_WINDOW_EDGE_MARGIN
  );

  return {
    x,
    y,
    width: dims.width,
    height: dims.height,
  };
}

function isPetWindowBoundsVisible(bounds) {
  if (!bounds || !Number.isFinite(bounds.x) || !Number.isFinite(bounds.y)) {
    return false;
  }

  // TASK-166B: use bounds.width/height when present so scale-aware bounds are validated correctly
  const normalizedBounds = {
    x: Math.round(bounds.x),
    y: Math.round(bounds.y),
    width: (bounds.width && Number.isFinite(bounds.width)) ? bounds.width : PET_WINDOW_WIDTH,
    height: (bounds.height && Number.isFinite(bounds.height)) ? bounds.height : PET_WINDOW_HEIGHT,
  };

  return screen.getAllDisplays().some(({ workArea }) => {
    const displayLeft = workArea.x;
    const displayRight = workArea.x + workArea.width;
    const displayTop = workArea.y;
    const displayBottom = workArea.y + workArea.height;

    return (
      normalizedBounds.x >= displayLeft &&
      normalizedBounds.x + normalizedBounds.width <= displayRight &&
      normalizedBounds.y >= displayTop &&
      normalizedBounds.y + normalizedBounds.height <= displayBottom
    );
  });
}

function ensurePetWindowVisibleBounds(win = petWindow, { persist = true } = {}) {
  if (!win || win.isDestroyed()) {
    return null;
  }

  const currentBounds = win.getBounds();
  // TASK-166B: preserve actual window size (respects active scale)
  const activeDims = {
    width:  (currentBounds.width  && Number.isFinite(currentBounds.width))  ? currentBounds.width  : PET_WINDOW_WIDTH,
    height: (currentBounds.height && Number.isFinite(currentBounds.height)) ? currentBounds.height : PET_WINDOW_HEIGHT,
  };
  const bounds = isPetWindowBoundsVisible(currentBounds)
    ? {
        x: Math.round(currentBounds.x),
        y: Math.round(currentBounds.y),
        width: activeDims.width,
        height: activeDims.height,
      }
    : getDefaultPetWindowBounds(activeDims);

  win.setBounds(bounds);

  if (persist) {
    savePetWindowBounds(win);
  }

  return bounds;
}

function validatePetWindowBoundsOnDisplayChange() {
  if (!petWindow || petWindow.isDestroyed()) {
    return;
  }

  ensurePetWindowVisibleBounds(petWindow, { persist: true });
}

function loadPetWindowBounds() {
  try {
    const raw = fs.readFileSync(getPetWindowStatePath(), "utf8");
    const parsed = JSON.parse(raw);
    // TASK-166B: use stored scale to determine correct saved dimensions
    const dims = getScaleDimensions(parsed.scale);
    const savedBounds = {
      x: Number(parsed.x),
      y: Number(parsed.y),
      width: dims.width,
      height: dims.height,
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

  // TASK-162: merge-write so quietMode field is preserved alongside position
  let existing = {};
  try {
    const raw = fs.readFileSync(getPetWindowStatePath(), "utf8");
    existing = JSON.parse(raw);
  } catch (_e) {
    // ignore; start from empty if file is missing or corrupt
  }

  // TASK-166B: save actual window dimensions so scale is encoded in position state
  const state = {
    ...existing,
    x: bounds.x,
    y: bounds.y,
    width: bounds.width,
    height: bounds.height,
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

function loadPetQuietMode() {  // TASK-162
  try {
    const raw = fs.readFileSync(getPetWindowStatePath(), "utf8");
    const parsed = JSON.parse(raw);
    return parsed.quietMode === true;
  } catch (_error) {
    // Missing or corrupt state falls back to default OFF.
    return false;
  }
}

function savePetQuietMode(value) {  // TASK-162
  const quietMode = value === true;
  let existing = {};
  try {
    const raw = fs.readFileSync(getPetWindowStatePath(), "utf8");
    existing = JSON.parse(raw);
  } catch (_error) {
    // Start from empty state if file is missing or corrupt.
  }
  const state = { ...existing, quietMode };
  try {
    fs.writeFileSync(getPetWindowStatePath(), `${JSON.stringify(state, null, 2)}\n`, "utf8");
  } catch (_error) {
    // Best-effort persistence; do not affect runtime use.
  }
}

function loadPetScale() {  // TASK-166B
  try {
    const raw = fs.readFileSync(getPetWindowStatePath(), "utf8");
    const parsed = JSON.parse(raw);
    const s = parsed.scale;
    if (s === "small" || s === "large") return s;
    return "medium";
  } catch (_error) {
    // Missing or corrupt state falls back to Medium.
    return "medium";
  }
}

function savePetScale(scaleName) {  // TASK-166B
  const scale =
    scaleName === "small" || scaleName === "large" ? scaleName : "medium";
  let existing = {};
  try {
    const raw = fs.readFileSync(getPetWindowStatePath(), "utf8");
    existing = JSON.parse(raw);
  } catch (_e) {
    // Start from empty state if file is missing or corrupt.
  }
  const state = { ...existing, scale };
  try {
    fs.writeFileSync(getPetWindowStatePath(), `${JSON.stringify(state, null, 2)}
`, "utf8");
  } catch (_error) {
    // Best-effort persistence; do not affect runtime use.
  }
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
      preload: path.join(__dirname, "renderer", "preload.js"),
    },
    resizable: true,
    // alwaysOnTop can be enabled by user preference in a later task
    alwaysOnTop: false,
  });

  fullAppWindow.on("closed", () => {
    fullAppWindow = null;
  });

  fullAppWindow.loadFile(path.join(__dirname, "renderer", "index.html"));

  // Pass backend URL to renderer via URL query param.
  // Preload remains narrow and only exposes window visibility controls.
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
    ensurePetWindowVisibleBounds(petWindow, { persist: true });
    petWindow.focus();
    return petWindow;
  }

  const petBounds = loadPetWindowBounds();  // TASK-166B: already scale-aware

  petWindow = new BrowserWindow({
    x: petBounds.x,
    y: petBounds.y,
    width: petBounds.width,    // TASK-166B: use scale-resolved dimensions
    height: petBounds.height,  // TASK-166B: use scale-resolved dimensions
    frame: false,
    transparent: true,
    backgroundColor: "#00000000",  // TASK-166A: explicit transparent for GPU driver compat
    alwaysOnTop: true,
    skipTaskbar: true,             // TASK-166A: companion overlay should not appear in taskbar
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

  // TASK-167A: narrow permission handler — allow microphone for voice push-to-talk only.
  // Deny all other permission requests so we don't accidentally open broad access.
  petWindow.webContents.session.setPermissionRequestHandler(
    (webContents, permission, callback) => {
      if (permission === "media") {
        callback(true);   // allow audio capture (microphone) for voice push-to-talk
      } else {
        callback(false);  // deny camera, notifications, etc.
      }
    }
  );

  const initialQuietMode = loadPetQuietMode();  // TASK-162
  const initialScale = loadPetScale();           // TASK-166B
  petWindow.loadURL(
    `file://${path.join(__dirname, "pet", "pet.html")}?quietMode=${initialQuietMode}&scale=${initialScale}`
  );
  return petWindow;
}

function resetPetWindowPosition() {
  if (!petWindow || petWindow.isDestroyed()) {
    return { ok: false };
  }

  // TASK-166B: reset uses active scale so window snaps to correct size at safe position
  const dims = getScaleDimensions(loadPetScale());
  const bounds = getDefaultPetWindowBounds(dims);
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

function showPetWindow() {
  if (!PET_MODE_ENABLED) {
    return { ok: false, reason: "pet_mode_disabled" };
  }

  const win = petWindow && !petWindow.isDestroyed() ? petWindow : createPetWindow();

  ensurePetWindowVisibleBounds(win, { persist: true });

  if (win.isMinimized()) {
    win.restore();
  }

  win.show();
  win.focus();
  return { ok: true };
}

function normalizePetSpeechField(value, fallback = "") {
  return typeof value === "string" ? value : fallback;
}

function sanitizePetSpeechPayload(payload = {}) {
  const reply = normalizePetSpeechField(payload.reply).slice(0, PET_SPEECH_REPLY_MAX_LENGTH);
  const mood = normalizePetSpeechField(payload.mood, "neutral");
  const source = normalizePetSpeechField(payload.source, "unknown");

  return { reply, mood, source };
}

function forwardPetSpeechUpdate(payload = {}) {
  const safePayload = sanitizePetSpeechPayload(payload);

  if (!petWindow || petWindow.isDestroyed()) {
    return { ok: false, reason: "pet_window_unavailable" };
  }

  if (!petWindow.isVisible()) {
    return { ok: false, reason: "pet_window_hidden" };
  }

  petWindow.webContents.send(PET_SPEECH_RECEIVED_CHANNEL, safePayload);
  return { ok: true };
}

ipcMain.handle(PET_OPEN_FULL_APP_CHANNEL, () => {
  showFullAppWindow();
  return { ok: true };
});

ipcMain.handle(PET_SHOW_WINDOW_CHANNEL, () => showPetWindow());

ipcMain.handle(PET_RESET_POSITION_CHANNEL, () => resetPetWindowPosition());

ipcMain.handle(PET_HIDE_WINDOW_CHANNEL, () => hidePetWindow());

ipcMain.handle(PET_SPEECH_UPDATE_CHANNEL, (_event, payload) => forwardPetSpeechUpdate(payload));

ipcMain.handle(PET_QUIET_MODE_SET_CHANNEL, (_event, value) => {  // TASK-162
  savePetQuietMode(value);
  return { ok: true };
});

ipcMain.handle(PET_SCALE_SET_CHANNEL, (_event, scaleName) => {  // TASK-166B
  const scale =
    scaleName === "small" || scaleName === "large" ? scaleName : "medium";
  const dims = getScaleDimensions(scale);
  savePetScale(scale);

  if (!petWindow || petWindow.isDestroyed()) {
    return { ok: false, reason: "no_pet_window" };
  }

  const cur = petWindow.getBounds();
  // Clamp position so the resized window stays inside the nearest display work area
  const display = screen.getDisplayNearestPoint({ x: cur.x, y: cur.y });
  const wa = display.workArea;
  const x = Math.min(Math.max(cur.x, wa.x), wa.x + wa.width  - dims.width);
  const y = Math.min(Math.max(cur.y, wa.y), wa.y + wa.height - dims.height);

  petWindow.setBounds({ x, y, width: dims.width, height: dims.height });
  savePetWindowBounds(petWindow);
  return { ok: true, scale };
});

ipcMain.handle(PET_CLICK_THROUGH_SET_CHANNEL, (_event, value) => {  // TASK-166D
  if (!petWindow || petWindow.isDestroyed()) {
    return { ok: false, reason: "no_pet_window" };
  }
  const enabled = value === true;  // TASK-166D: non-true fails safe to OFF
  if (enabled) {
    petWindow.setIgnoreMouseEvents(true, { forward: true });
  } else {
    petWindow.setIgnoreMouseEvents(false);
    petWindow.focus();  // TASK-166E click-fix: restore OS focus so the direct input can receive keyboard events
  }
  return { ok: true, clickThrough: enabled };
});


// TASK-174: guard against concurrent picker sessions.
let pickerInFlight = false;

// Opens a semi-transparent picker overlay on every connected display.
// Resolves with the selected display id string, or null on Esc/close.
// All picker windows are destroyed before this function returns.
async function showDisplayPicker(displays) {
  return new Promise((resolve) => {
    const pickerWindows = [];
    let settled = false;

    function cleanup() {
      for (const win of pickerWindows) {
        if (!win.isDestroyed()) win.destroy();
      }
      pickerWindows.length = 0;
    }

    function settle(result) {
      if (settled) return;
      settled = true;
      ipcMain.removeListener(SCREEN_PICKER_SELECTED_CHANNEL, onSelected);
      ipcMain.removeListener(SCREEN_PICKER_CANCEL_CHANNEL, onCancel);
      cleanup();
      resolve(result);
    }

    function onSelected(_event, displayId) {
      settle(typeof displayId === "string" && displayId.length > 0 ? displayId : null);
    }

    function onCancel() {
      settle(null);
    }

    ipcMain.on(SCREEN_PICKER_SELECTED_CHANNEL, onSelected);
    ipcMain.on(SCREEN_PICKER_CANCEL_CHANNEL, onCancel);

    for (const display of displays) {
      const { x, y, width, height } = display.bounds;
      const win = new BrowserWindow({
        x, y, width, height,
        frame:       false,
        transparent: true,
        alwaysOnTop: true,
        skipTaskbar: true,
        focusable:   true,
        webPreferences: {
          contextIsolation: true,
          nodeIntegration:  false,
          preload: path.join(__dirname, "picker", "picker-preload.js"),
        },
      });
      win.setIgnoreMouseEvents(false);
      win.loadFile(path.join(__dirname, "picker", "picker.html"), {
        query: { displayId: String(display.id) },
      });
      win.on("closed", () => {
        if (!settled) {
          const remaining = pickerWindows.filter((w) => !w.isDestroyed()).length;
          if (remaining === 0) settle(null);
        }
      });
      pickerWindows.push(win);
    }
  });
}

// TASK-174: screen:capture-once IPC handler.
// Shows a click-to-select overlay on every connected display; user clicks the
// desired monitor. Main process captures exactly the selected display.
// Replaces the cursor-position approach (rejected: clicking the button moves
// the cursor to the app-window monitor, so capture always targeted the wrong
// screen on dual-monitor setups).
// Normal renderer never receives raw display IDs or desktopCapturer source list.
// No disk save, no /chat, no OCR, no background monitoring.
ipcMain.handle(SCREEN_CAPTURE_ONCE_CHANNEL, async () => {
  if (pickerInFlight) {
    return { ok: false, error: "screen-picker-failed" };
  }
  pickerInFlight = true;
  try {
    const displays = screen.getAllDisplays();
    if (!displays || displays.length === 0) {
      return { ok: false, error: "no-source" };
    }

    const selectedId = await showDisplayPicker(displays);

    if (selectedId === null) {
      return { ok: false, error: "screen-pick-cancelled" };
    }

    const targetDisplay = displays.find((d) => String(d.id) === selectedId);
    if (!targetDisplay) {
      return { ok: false, error: "screen-picker-failed" };
    }

    const sources = await desktopCapturer.getSources({
      types: ["screen"],
      thumbnailSize: {
        width:  targetDisplay.size.width,
        height: targetDisplay.size.height,
      },
    });
    if (!sources || sources.length === 0) {
      return { ok: false, error: "no-source" };
    }

    // Match source to selected display by display_id.
    const targetId = String(targetDisplay.id);
    let selected = sources.find((s) => String(s.display_id) === targetId);
    if (!selected) {
      // Single-monitor: one source always corresponds to the only display — safe to use.
      // Multi-monitor: cannot safely identify which source matches — fail with clean error.
      if (sources.length === 1) {
        selected = sources[0];
      } else {
        return { ok: false, error: "selected-display-ambiguous" };
      }
    }

    const thumbnail = selected && selected.thumbnail;
    if (!thumbnail || thumbnail.isEmpty()) {
      return { ok: false, error: "capture-failed" };
    }
    const dataUrl = thumbnail.toDataURL();
    if (typeof dataUrl !== "string" || !dataUrl.startsWith("data:image/")) {
      return { ok: false, error: "capture-failed" };
    }
    return { ok: true, dataUrl };
  } catch (_err) {
    const msg = _err && typeof _err.message === "string" ? _err.message.toLowerCase() : "";
    if (msg.includes("permission") || msg.includes("denied") || msg.includes("not authorized")) {
      return { ok: false, error: "permission-denied" };
    }
    return { ok: false, error: "capture-failed" };
  } finally {
    pickerInFlight = false;
  }
});



// TASK-167B: stt:transcribe IPC handler.
// Receives an ArrayBuffer from the renderer, wraps it in a multipart POST to the
// backend /stt/transcribe endpoint (local Whisper), and returns the JSON result.
// No audio is persisted to disk. Click-through is unaffected here (renderer handles CT state).
ipcMain.handle(PET_STT_TRANSCRIBE_CHANNEL, (_event, arrayBuffer) => {
  return new Promise((resolve) => {
    let buffer;
    try {
      buffer = Buffer.from(arrayBuffer);
    } catch (_e) {
      resolve({ transcript: "", status: "error" });
      return;
    }

    if (!buffer.length) {
      resolve({ transcript: "", status: "empty" });
      return;
    }

    const boundary = "----DragonPetSTT" + Date.now();
    const partHeader = Buffer.from(
      `--${boundary}\r\nContent-Disposition: form-data; name="audio"; filename="audio.webm"\r\nContent-Type: audio/webm\r\n\r\n`,
      "utf8"
    );
    const partFooter = Buffer.from(`\r\n--${boundary}--\r\n`, "utf8");
    const body = Buffer.concat([partHeader, buffer, partFooter]);

    // Parse BACKEND_URL host/port (e.g. "http://localhost:8000")
    let hostname = "127.0.0.1";
    let port = 8000;
    try {
      const parsed = new URL(BACKEND_URL);
      hostname = parsed.hostname;
      port = parseInt(parsed.port, 10) || 8000;
    } catch (_e) { /* use defaults */ }

    const options = {
      hostname,
      port,
      path: "/stt/transcribe",
      method: "POST",
      headers: {
        "Content-Type": `multipart/form-data; boundary=${boundary}`,
        "Content-Length": body.length,
      },
    };

    const req = http.request(options, (res) => {
      const chunks = [];
      res.on("data", (chunk) => chunks.push(chunk));
      res.on("end", () => {
        try {
          const text = Buffer.concat(chunks).toString("utf8");
          resolve(JSON.parse(text));
        } catch (_e) {
          resolve({ transcript: "", status: "error" });
        }
      });
    });

    req.on("error", () => {
      resolve({ transcript: "", status: "offline" });
    });

    req.write(body);
    req.end();
  });
});

app.whenReady().then(() => {
  createWindow();
  if (PET_MODE_ENABLED) {
    createPetWindow();
  }

  screen.on("display-added", validatePetWindowBoundsOnDisplayChange);
  screen.on("display-removed", validatePetWindowBoundsOnDisplayChange);
  screen.on("display-metrics-changed", validatePetWindowBoundsOnDisplayChange);

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
