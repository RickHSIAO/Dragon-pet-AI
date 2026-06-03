/**
 * dragon-pet-ai — Electron main process
 *
 * TASK-003: Minimal skeleton window.
 * - Opens a BrowserWindow pointing to renderer/index.html
 * - Full App renderer calls backend directly via fetch
 * - Full App and Pet Mode use narrow IPC bridges for window visibility only
 * - No shell execution, no file system access, no live2D
 */

const { app, BrowserWindow, clipboard, desktopCapturer, dialog, ipcMain, Menu, screen } = require("electron");
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
const PET_CHAT_MIRROR_CHANNEL = "pet:chat-mirror";             // TASK-193: Pet → main → Full App
const PET_CHAT_MIRROR_RECEIVED_CHANNEL = "pet:chat-mirror-received";  // TASK-193: main → Full App
const CHAT_HISTORY_FILE = "chat-history.json";                 // TASK-194
const CHAT_HISTORY_APPEND_CHANNEL = "chat-history:append";    // TASK-194
const CHAT_HISTORY_LOAD_CHANNEL   = "chat-history:load";      // TASK-194
const CHAT_HISTORY_CLEAR_CHANNEL  = "chat-history:clear";     // TASK-194
const CLIPBOARD_WRITE_TEXT_CHANNEL = "clipboard:write-text";  // TASK-196
const PET_UNREAD_DOT_CHANNEL = "pet:unread-dot";              // TASK-204: Full App → main
const PET_UNREAD_DOT_RECEIVED_CHANNEL = "pet:unread-dot-received";  // TASK-204: main → Pet Window
const PET_EXPRESSION_SUGGESTION_CHANNEL = "pet:expression-suggestion";           // TASK-218: Full App → main
const PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet:expression-suggestion-received"; // TASK-218: main → Pet Window
const PET_REACTION_BUBBLE_CHANNEL = "pet:reaction-bubble";                       // TASK-220: Full App → main
const PET_REACTION_BUBBLE_RECEIVED_CHANNEL = "pet:reaction-bubble-received";     // TASK-220: main → Pet Window
const INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN = new Set([
  "neutral", "focused", "happy", "proud", "annoyed", "sleepy",
]); // TASK-218: expression allowlist for main sanitization
const REACTION_BUBBLE_TEXT_BY_ID_MAIN = Object.freeze({                          // TASK-220: fixed text mapping
  user_active: "哼，總算肯理吾了。",
  message_management: "整理好了？手腳還算俐落。",
  correction: "又改？下次可要想清楚。",
  reset: "清空了。重新開始也無妨。",
  attention_returned: "回來了？吾才沒有等汝。",
  none: "",
});
const REACTION_BUBBLE_ALLOWLIST_MAIN = new Set(Object.keys(REACTION_BUBBLE_TEXT_BY_ID_MAIN));
const REACTION_BUBBLE_SOURCE = "interaction_reaction_bubble";
const REACTION_BUBBLE_TTL_MS = 3000;
const CHAT_EXPORT_CHANNEL    = "chat:export-transcript";      // TASK-205: Full App → main
const CHAT_HISTORY_MAX_ENTRIES    = 200;                      // TASK-194: bounded history cap
const CHAT_HISTORY_TEXT_MAX       = 2000;                     // TASK-194: per-entry text cap
const SCREEN_CAPTURE_ONCE_CHANNEL    = "screen:capture-once";      // TASK-171A
const SCREEN_PICKER_SELECTED_CHANNEL = "screen-picker:selected";  // TASK-174
const SCREEN_PICKER_CANCEL_CHANNEL   = "screen-picker:cancel";    // TASK-174
const SCREEN_REGION_SELECTED_CHANNEL = "screen-region:selected";  // TASK-175
const SCREEN_REGION_CANCEL_CHANNEL   = "screen-region:cancel";    // TASK-175
const MIN_REGION_LOGICAL_PX          = 16;                        // TASK-175: minimum selectable region in logical px
const SCREEN_CAPTURE_WINDOW_CHANNEL  = "screen:capture-window";   // TASK-176
const WINDOW_PICKER_LIST_CHANNEL     = "window-picker:list";      // TASK-176: main → picker (name list)
const WINDOW_PICKER_SELECTED_CHANNEL = "window-picker:selected";  // TASK-176: picker → main (index)
const WINDOW_PICKER_CANCEL_CHANNEL   = "window-picker:cancel";    // TASK-176: picker → main
const WINDOW_CAPTURE_THUMB_SIZE      = 1920;                      // TASK-176: max thumbnail dimension for window capture
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
const PET_CHAT_MIRROR_USER_MAX_LENGTH = 2000;  // TASK-193: max user message chars forwarded to Full App

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

function getChatHistoryPath() {   // TASK-194
  return path.join(app.getPath("userData"), CHAT_HISTORY_FILE);
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

// TASK-194: bounded chat history persistence — text-only, best-effort.
function readChatHistoryEntries() {
  try {
    const raw = fs.readFileSync(getChatHistoryPath(), "utf8");
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed;
  } catch (_e) {
    // Missing or corrupt file: return empty history.
  }
  return [];
}

function writeChatHistoryEntries(entries) {
  try {
    fs.writeFileSync(getChatHistoryPath(), `${JSON.stringify(entries, null, 2)}\n`, "utf8");
  } catch (_error) {
    // Best-effort persistence; do not affect runtime use.
  }
}

function appendChatHistoryEntry(entry) {
  const entries = readChatHistoryEntries();
  entries.push(entry);
  writeChatHistoryEntries(entries.slice(-CHAT_HISTORY_MAX_ENTRIES));
}

function clearChatHistoryFile() {
  writeChatHistoryEntries([]);
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

function sanitizeExpressionSuggestionPayload(payload = {}) {
  const rawExpression = typeof payload.expression === "string" ? payload.expression : "";
  const safeExpression = INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN.has(rawExpression)
    ? rawExpression : "neutral";
  return {
    expression: safeExpression,
    source: "interaction_expression_suggestion",
    ts: typeof payload.ts === "number" && payload.ts > 0 ? payload.ts : Date.now(),
  };
}

// TASK-218: narrow expression suggestion relay — expression-only, no speech, no bubble, no TTS.
function forwardExpressionSuggestion(payload = {}, targetPetWindow = petWindow) {
  const safePayload = sanitizeExpressionSuggestionPayload(payload);
  if (!targetPetWindow || targetPetWindow.isDestroyed()) {
    return { ok: false, reason: "pet_window_unavailable" };
  }
  targetPetWindow.webContents.send(PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL, safePayload);
  return { ok: true };
}
ipcMain.handle(PET_EXPRESSION_SUGGESTION_CHANNEL, (_event, payload) => forwardExpressionSuggestion(payload));

function sanitizeReactionBubblePayload(payload = {}) {
  const rawId = typeof payload.id === "string" ? payload.id : "";
  const safeId = REACTION_BUBBLE_ALLOWLIST_MAIN.has(rawId) ? rawId : "none";
  return {
    id: safeId,
    text: REACTION_BUBBLE_TEXT_BY_ID_MAIN[safeId] || "",
    source: REACTION_BUBBLE_SOURCE,
    ts: typeof payload.ts === "number" && payload.ts > 0 ? payload.ts : Date.now(),
    ttlMs: REACTION_BUBBLE_TTL_MS,
  };
}

// TASK-220: narrow reaction bubble relay — fixed text only, no /chat, no TTS, no history.
function forwardReactionBubble(payload = {}, targetPetWindow = petWindow) {
  const safePayload = sanitizeReactionBubblePayload(payload);
  if (!targetPetWindow || targetPetWindow.isDestroyed()) {
    return { ok: false, reason: "pet_window_unavailable" };
  }
  targetPetWindow.webContents.send(PET_REACTION_BUBBLE_RECEIVED_CHANNEL, safePayload);
  return { ok: true };
}
ipcMain.handle(PET_REACTION_BUBBLE_CHANNEL, (_event, payload) => forwardReactionBubble(payload));

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

// TASK-175: shows a drag-to-select region overlay on the given display.
// Resolves with { x, y, width, height } in CSS logical pixels (relative to display top-left),
// or null on Esc/window close. Main process owns DPI conversion and crop.
async function showRegionPicker(display) {
  return new Promise((resolve) => {
    let settled = false;
    let win = null;

    function settle(result) {
      if (settled) return;
      settled = true;
      ipcMain.removeListener(SCREEN_REGION_SELECTED_CHANNEL, onSelected);
      ipcMain.removeListener(SCREEN_REGION_CANCEL_CHANNEL, onCancel);
      if (win && !win.isDestroyed()) win.destroy();
      resolve(result);
    }

    function onSelected(_event, rect) {
      settle(rect && typeof rect === "object" ? rect : null);
    }

    function onCancel() {
      settle(null);
    }

    ipcMain.on(SCREEN_REGION_SELECTED_CHANNEL, onSelected);
    ipcMain.on(SCREEN_REGION_CANCEL_CHANNEL, onCancel);

    const { x, y, width, height } = display.bounds;
    win = new BrowserWindow({
      x, y, width, height,
      frame:       false,
      transparent: true,
      alwaysOnTop: true,
      skipTaskbar: true,
      focusable:   true,
      webPreferences: {
        contextIsolation: true,
        nodeIntegration:  false,
        preload: path.join(__dirname, "picker", "region-picker-preload.js"),
      },
    });
    win.setIgnoreMouseEvents(false);
    win.loadFile(path.join(__dirname, "picker", "region-picker.html"));
    win.on("closed", () => {
      if (!settled) settle(null);
    });
  });
}

// TASK-176: shows a window picker listing all capturable windows by name.
// User clicks a window name; main process returns the selected source (never the source ID list).
// Returns { source } on success or { error } on cancel/failure.
// Active-window auto-detection is intentionally not implemented:
//   clicking the picker button focuses this app window, so "active window" always resolves
//   to dragon-pet-ai — defeating the purpose. Explicit selection is the correct UX.
async function showWindowPicker() {
  let rawSources;
  try {
    rawSources = await desktopCapturer.getSources({
      types: ["window"],
      thumbnailSize: { width: WINDOW_CAPTURE_THUMB_SIZE, height: WINDOW_CAPTURE_THUMB_SIZE },
      fetchWindowIcons: false,
    });
  } catch (_e) {
    return { error: "window-capture-failed" };
  }

  // Filter to named windows only (system/background processes often have no name).
  const sources = (rawSources || []).filter(
    (s) => typeof s.name === "string" && s.name.length > 0
  );
  if (sources.length === 0) {
    return { error: "no-window-source" };
  }

  // Build picker data: index + name only. Source IDs are kept here in main process.
  const pickerList = sources.map((s, i) => ({ index: i, name: s.name }));

  return new Promise((resolve) => {
    let settled = false;
    let win = null;

    function settle(result) {
      if (settled) return;
      settled = true;
      ipcMain.removeListener(WINDOW_PICKER_SELECTED_CHANNEL, onSelected);
      ipcMain.removeListener(WINDOW_PICKER_CANCEL_CHANNEL, onCancel);
      if (win && !win.isDestroyed()) win.destroy();
      resolve(result);
    }

    function onSelected(_event, index) {
      const src = (typeof index === "number" && index >= 0 && index < sources.length)
                  ? sources[index] : null;
      settle(src ? { source: src } : { error: "window-picker-failed" });
    }

    function onCancel() {
      settle({ error: "window-pick-cancelled" });
    }

    ipcMain.on(WINDOW_PICKER_SELECTED_CHANNEL, onSelected);
    ipcMain.on(WINDOW_PICKER_CANCEL_CHANNEL, onCancel);

    const workArea = screen.getPrimaryDisplay().workArea;
    const winW = Math.min(680, workArea.width  - 80);
    const winH = Math.min(520, workArea.height - 80);
    win = new BrowserWindow({
      x: Math.round(workArea.x + (workArea.width  - winW) / 2),
      y: Math.round(workArea.y + (workArea.height - winH) / 2),
      width: winW, height: winH,
      frame:       false,
      transparent: false,
      backgroundColor: "#1a1a2e",
      alwaysOnTop: true,
      skipTaskbar: true,
      focusable:   true,
      resizable:   false,
      webPreferences: {
        contextIsolation: true,
        nodeIntegration:  false,
        preload: path.join(__dirname, "picker", "window-picker-preload.js"),
      },
    });

    win.loadFile(path.join(__dirname, "picker", "window-picker.html"));

    win.webContents.on("dom-ready", () => {
      if (!win || win.isDestroyed()) return;
      win.webContents.send(WINDOW_PICKER_LIST_CHANNEL, pickerList);
    });

    win.on("closed", () => {
      if (!settled) settle({ error: "window-pick-cancelled" });
    });
  });
}

// TASK-176: screen:capture-window IPC handler.
// Presents an explicit window picker — active-window auto-detection is not used
// (interaction moves OS focus to this app, defeating any cursor/focus heuristic).
// Normal renderer never receives source IDs, source list, or raw window handles.
// No disk save, no /chat, no OCR, no background monitoring.
ipcMain.handle(SCREEN_CAPTURE_WINDOW_CHANNEL, async () => {
  if (pickerInFlight) {
    return { ok: false, error: "window-picker-failed" };
  }
  pickerInFlight = true;
  try {
    const pickerResult = await showWindowPicker();
    if (pickerResult.error) {
      return { ok: false, error: pickerResult.error };
    }
    const { source } = pickerResult;
    const thumbnail = source && source.thumbnail;
    if (!thumbnail || thumbnail.isEmpty()) {
      return { ok: false, error: "window-capture-failed" };
    }
    const dataUrl = thumbnail.toDataURL();
    if (typeof dataUrl !== "string" || !dataUrl.startsWith("data:image/")) {
      return { ok: false, error: "window-capture-failed" };
    }
    return { ok: true, dataUrl };
  } catch (_err) {
    const msg = _err && typeof _err.message === "string" ? _err.message.toLowerCase() : "";
    if (msg.includes("permission") || msg.includes("denied") || msg.includes("not authorized")) {
      return { ok: false, error: "permission-denied" };
    }
    return { ok: false, error: "window-capture-failed" };
  } finally {
    pickerInFlight = false;
  }
});

// TASK-174/175: screen:capture-once IPC handler.
// Phase 1 (TASK-174): click-to-select overlay on every connected display; user picks monitor.
// Phase 2 (TASK-175): drag-to-select region overlay on the chosen display; user drags a rect.
// Main process captures the selected display at physical resolution, crops to the region,
// and returns the cropped dataUrl. DPI/scaleFactor conversion is done here — the renderer
// only ever receives a plain { ok, dataUrl } result.
// Normal renderer never receives raw display IDs, source IDs, or desktopCapturer source list.
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

    // Phase 1: display picker (TASK-174)
    const selectedId = await showDisplayPicker(displays);
    if (selectedId === null) {
      return { ok: false, error: "screen-pick-cancelled" };
    }

    const targetDisplay = displays.find((d) => String(d.id) === selectedId);
    if (!targetDisplay) {
      return { ok: false, error: "screen-picker-failed" };
    }

    // Phase 2: region picker (TASK-175) — user drags a rect on the selected display
    const rawRect = await showRegionPicker(targetDisplay);
    if (rawRect === null) {
      return { ok: false, error: "region-pick-cancelled" };
    }

    // Validate minimum region size in logical pixels before any DPI math
    const logW = typeof rawRect.width  === "number" ? rawRect.width  : 0;
    const logH = typeof rawRect.height === "number" ? rawRect.height : 0;
    if (logW < MIN_REGION_LOGICAL_PX || logH < MIN_REGION_LOGICAL_PX) {
      return { ok: false, error: "region-too-small" };
    }

    // Phase 3: capture full display at physical resolution, then crop
    // scaleFactor converts logical (CSS) pixels to physical (bitmap) pixels.
    // display.bounds uses logical pixels; physical = logical × scaleFactor.
    // Multi-monitor setups may have negative bounds.x/y — irrelevant here because
    // the region rect is relative to the picker window's own top-left (= display top-left).
    const scaleFactor  = (typeof targetDisplay.scaleFactor === "number"
                          && targetDisplay.scaleFactor > 0)
                         ? targetDisplay.scaleFactor : 1;
    const physDisplayW = Math.round(targetDisplay.bounds.width  * scaleFactor);
    const physDisplayH = Math.round(targetDisplay.bounds.height * scaleFactor);

    const sources = await desktopCapturer.getSources({
      types: ["screen"],
      thumbnailSize: { width: physDisplayW, height: physDisplayH },
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

    // Convert region from logical to physical pixels and clamp to display bounds.
    // rawRect.{x,y} are relative to the picker window = relative to display top-left.
    const cropX = Math.max(0, Math.round(rawRect.x * scaleFactor));
    const cropY = Math.max(0, Math.round(rawRect.y * scaleFactor));
    const cropW = Math.min(Math.round(logW * scaleFactor), physDisplayW - cropX);
    const cropH = Math.min(Math.round(logH * scaleFactor), physDisplayH - cropY);

    if (cropW <= 0 || cropH <= 0) {
      return { ok: false, error: "region-too-small" };
    }

    let cropped;
    try {
      cropped = thumbnail.crop({ x: cropX, y: cropY, width: cropW, height: cropH });
    } catch (_cropErr) {
      return { ok: false, error: "region-crop-failed" };
    }

    if (!cropped || cropped.isEmpty()) {
      return { ok: false, error: "region-crop-failed" };
    }

    const dataUrl = cropped.toDataURL();
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
      `--${boundary}\r\nContent-Disposition: form-data; name="audio"; filename="audio.wav"\r\nContent-Type: audio/wav\r\n\r\n`,
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

// TASK-193: receive Pet Window chat event and forward to Full App chat area.
// Payload contains user text + AI reply — text-only, no audio blob, no base64.
// No-op if fullAppWindow is unavailable or destroyed.
ipcMain.handle(PET_CHAT_MIRROR_CHANNEL, (_event, payload = {}) => {
  const userMessage = typeof payload.userMessage === "string"
    ? payload.userMessage.slice(0, PET_CHAT_MIRROR_USER_MAX_LENGTH) : "";
  const reply = typeof payload.reply === "string"
    ? payload.reply.slice(0, PET_SPEECH_REPLY_MAX_LENGTH) : "";
  const mood = typeof payload.mood === "string" ? payload.mood.slice(0, 30) : "neutral";
  const source = typeof payload.source === "string" ? payload.source.slice(0, 30) : "unknown";
  const inputMethod = payload.inputMethod === "voice" ? "voice" : "text";  // TASK-195

  if (!userMessage || !reply) {
    return { ok: false, reason: "empty_payload" };
  }

  if (!fullAppWindow || fullAppWindow.isDestroyed()) {
    return { ok: false, reason: "full_app_unavailable" };
  }

  fullAppWindow.webContents.send(PET_CHAT_MIRROR_RECEIVED_CHANNEL, { userMessage, reply, mood, source, inputMethod });
  return { ok: true };
});

// TASK-194: chat history persistence — narrow IPC, text-only entries, no audio/screenshot/apikey.
ipcMain.handle(CHAT_HISTORY_APPEND_CHANNEL, (_event, entry = {}) => {
  const role = entry.role === "user" || entry.role === "pet" ? entry.role : null;
  if (!role) return { ok: false, reason: "invalid_role" };
  const text = typeof entry.text === "string" ? entry.text.slice(0, CHAT_HISTORY_TEXT_MAX) : "";
  if (!text) return { ok: false, reason: "empty_text" };
  const source = typeof entry.source === "string" ? entry.source.slice(0, 30) : "unknown";
  // TASK-206: use renderer-provided ts so stored time matches displayed time; fallback to now.
  const ts = typeof entry.ts === "number" && entry.ts > 0 ? entry.ts : Date.now();
  appendChatHistoryEntry({ role, text, source, ts });
  return { ok: true };
});

ipcMain.handle(CHAT_HISTORY_LOAD_CHANNEL, () => {
  const entries = readChatHistoryEntries();
  return entries
    .filter((e) => (e.role === "user" || e.role === "pet") && typeof e.text === "string" && e.text)
    .map((e) => ({
      role: e.role,
      text: typeof e.text === "string" ? e.text.slice(0, CHAT_HISTORY_TEXT_MAX) : "",
      source: typeof e.source === "string" ? e.source.slice(0, 30) : "unknown",
      ts: typeof e.ts === "number" ? e.ts : 0,  // TASK-206: was missing — root cause of lost timestamps
    }));
});

ipcMain.handle(CHAT_HISTORY_CLEAR_CHANNEL, () => {
  clearChatHistoryFile();
  return { ok: true };
});

// TASK-196: clipboard write from main process — avoids file:// secure-context restriction in renderer.
ipcMain.handle(CLIPBOARD_WRITE_TEXT_CHANNEL, (_event, text) => {
  if (typeof text !== "string") return false;
  const safe = text.slice(0, 20000);
  if (!safe) return false;
  try {
    clipboard.writeText(safe);
    return true;
  } catch (_) {
    return false;
  }
});

// TASK-205: export conversation — opens system Save Dialog and writes plain text.
// Content is capped; no raw error details returned to renderer.
ipcMain.handle(CHAT_EXPORT_CHANNEL, async (_event, payload = {}) => {
  const content     = typeof payload.content === "string" ? payload.content.slice(0, 200000) : "";
  const defaultPath = typeof payload.defaultPath === "string"
    ? path.basename(payload.defaultPath).slice(0, 255) : "dragon-pet-chat.txt";
  let saveResult;
  try {
    saveResult = await dialog.showSaveDialog({
      defaultPath,
      filters: [{ name: "Text Files", extensions: ["txt"] }],
    });
  } catch (_) {
    return { ok: false, canceled: false, error: "dialog_failed" };
  }
  if (saveResult.canceled || !saveResult.filePath) return { ok: false, canceled: true };
  try {
    await fs.promises.writeFile(saveResult.filePath, content, "utf8");
    return { ok: true, canceled: false };
  } catch (_) {
    return { ok: false, canceled: false, error: "write_failed" };
  }
});

// TASK-204: receive unread count from Full App and forward to Pet Window.
// Payload is count-only — no message content. Pet Window shows/hides unread dot.
ipcMain.handle(PET_UNREAD_DOT_CHANNEL, (_event, payload = {}) => {
  const unreadCount = typeof payload.unreadCount === "number" && payload.unreadCount >= 0
    ? payload.unreadCount : 0;
  if (!petWindow || petWindow.isDestroyed()) {
    return { ok: false, reason: "pet_window_unavailable" };
  }
  petWindow.webContents.send(PET_UNREAD_DOT_RECEIVED_CHANNEL, { unreadCount });
  return { ok: true };
});

app.whenReady().then(() => {
  Menu.setApplicationMenu(null);  // TASK-195: hide native File/Edit/View/Window/Help menu bar
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
