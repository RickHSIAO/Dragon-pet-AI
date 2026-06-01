const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const desktopRoot = path.resolve(__dirname, "..");
const mainPath = path.join(desktopRoot, "src", "main.js");
const rendererPath = path.join(desktopRoot, "src", "renderer", "renderer.js");
const rendererHtmlPath = path.join(desktopRoot, "src", "renderer", "index.html");
const rendererPreloadPath = path.join(desktopRoot, "src", "renderer", "preload.js");
const petRendererPath = path.join(desktopRoot, "src", "pet", "pet-renderer.js");
const petPreloadPath = path.join(desktopRoot, "src", "pet", "pet-preload.js");
const petHtmlPath = path.join(desktopRoot, "src", "pet", "pet.html");

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function assertIncludes(haystack, needle, label) {
  assert.equal(haystack.includes(needle), true, `${label} should include ${needle}`);
}

function assertNotIncludes(haystack, needle, label) {
  assert.equal(haystack.includes(needle), false, `${label} should not include ${needle}`);
}

function assertRegex(haystack, regex, label) {
  assert.equal(regex.test(haystack), true, `${label} should match ${regex}`);
}

function testMainHasPetWindowPrototype() {
  const main = readText(mainPath);
  assertIncludes(main, "let petWindow = null", "main.js");
  assertIncludes(main, "let fullAppWindow = null", "main.js");
  assertIncludes(main, "function createPetWindow()", "main.js");
  assertIncludes(main, "PET_MODE_ENABLED", "main.js");
  assertIncludes(main, 'process.env.PET_MODE_ENABLED === "true"', "main.js");
  assertIncludes(main, 'path.join(__dirname, "pet", "pet.html")', "main.js");
  assertIncludes(main, 'path.join(__dirname, "pet", "pet-preload.js")', "main.js");
  assertIncludes(main, 'path.join(__dirname, "renderer", "preload.js")', "main.js");
}

function testPetWindowOptionsAreSafeAndPetSpecific() {
  const main = readText(mainPath);
  assertIncludes(main, "PET_WINDOW_WIDTH = 300", "main.js");
  assertIncludes(main, "PET_WINDOW_HEIGHT = 400", "main.js");
  // TASK-166B: window dimensions are now resolved from active scale
  assertRegex(main, /width:\s*petBounds\.width/, "main.js");
  assertRegex(main, /height:\s*petBounds\.height/, "main.js");
  assertRegex(main, /frame:\s*false/, "main.js");
  assertRegex(main, /transparent:\s*true/, "main.js");
  assertRegex(main, /alwaysOnTop:\s*true/, "main.js");
  assertRegex(main, /resizable:\s*false/, "main.js");
  assertRegex(main, /show:\s*false/, "main.js");
  assertRegex(main, /nodeIntegration:\s*false/, "main.js");
  assertRegex(main, /contextIsolation:\s*true/, "main.js");
  assertRegex(main, /sandbox:\s*true/, "main.js");
  assertIncludes(main, 'once("ready-to-show"', "main.js");
}

function testPetWindowPositionPersistenceIsLocalAndGuarded() {
  const main = readText(mainPath);
  assertIncludes(main, 'PET_WINDOW_STATE_FILE = "pet-window-state.json"', "main.js");
  assertIncludes(main, 'app.getPath("userData")', "main.js");
  assertIncludes(main, "function getPetWindowStatePath()", "main.js");
  assertIncludes(main, "function getDefaultPetWindowBounds(", "main.js");  // TASK-166B: accepts dims param
  assertIncludes(main, "function isPetWindowBoundsVisible(bounds)", "main.js");
  assertIncludes(main, "function ensurePetWindowVisibleBounds(win = petWindow", "main.js");
  assertIncludes(main, "function validatePetWindowBoundsOnDisplayChange()", "main.js");
  assertIncludes(main, "function loadPetWindowBounds()", "main.js");
  assertIncludes(main, "function savePetWindowBounds(win = petWindow)", "main.js");
  assertIncludes(main, "function schedulePetWindowBoundsSave()", "main.js");
  assertIncludes(main, "screen.getAllDisplays()", "main.js");
  assertIncludes(main, "screen.getPrimaryDisplay().workArea", "main.js");
  assertIncludes(main, "normalizedBounds.x >= displayLeft", "main.js");
  assertIncludes(main, "normalizedBounds.x + normalizedBounds.width <= displayRight", "main.js");
  assertIncludes(main, "normalizedBounds.y >= displayTop", "main.js");
  assertIncludes(main, "normalizedBounds.y + normalizedBounds.height <= displayBottom", "main.js");
  assertIncludes(main, "fs.readFileSync(getPetWindowStatePath()", "main.js");
  assertIncludes(main, "fs.writeFileSync(getPetWindowStatePath()", "main.js");
  assertIncludes(main, "const petBounds = loadPetWindowBounds();", "main.js");
  assertRegex(main, /x:\s*petBounds\.x/, "main.js");
  assertRegex(main, /y:\s*petBounds\.y/, "main.js");
  assertIncludes(main, 'petWindow.on("move"', "main.js");
  assertIncludes(main, 'petWindow.on("close"', "main.js");
  assertIncludes(main, "schedulePetWindowBoundsSave();", "main.js");
  assertIncludes(main, "savePetWindowBounds();", "main.js");
  assertIncludes(main, 'screen.on("display-added", validatePetWindowBoundsOnDisplayChange)', "main.js");
  assertIncludes(main, 'screen.on("display-removed", validatePetWindowBoundsOnDisplayChange)', "main.js");
  assertIncludes(main, 'screen.on("display-metrics-changed", validatePetWindowBoundsOnDisplayChange)', "main.js");
}

function testPetWindowPositionRestoreAndFallbackRules() {
  const main = readText(mainPath);
  assertRegex(
    main,
    /if \(isPetWindowBoundsVisible\(savedBounds\)\) \{\s*return savedBounds;\s*\}/,
    "main.js"
  );
  assertRegex(
    main,
    /return getDefaultPetWindowBounds\(\);/,
    "main.js"
  );
  assertRegex(
    main,
    // TASK-166B: loadPetWindowBounds uses scale-resolved dims
    /width:\s*dims\.width/,
    "main.js"
  );
  assertRegex(
    main,
    /height:\s*dims\.height/,
    "main.js"
  );
  assertIncludes(main, "PET_WINDOW_EDGE_MARGIN = 24", "main.js");
}

function testPetWindowResetPersistsSafeDefault() {
  const main = readText(mainPath);
  // TASK-166B: reset now resolves active scale and passes dims to getDefaultPetWindowBounds
  assertRegex(
    main,
    /function resetPetWindowPosition\(\)[\s\S]*const dims = getScaleDimensions\(loadPetScale\(\)\);[\s\S]*const bounds = getDefaultPetWindowBounds\(dims\);[\s\S]*petWindow\.setBounds\(bounds\);[\s\S]*savePetWindowBounds\(petWindow\);[\s\S]*return \{ ok: true \};/,
    "main.js"
  );
}

function testPetWindowHideShowPreservesAndValidatesPosition() {
  const main = readText(mainPath);
  assertRegex(
    main,
    /function hidePetWindow\(\)[\s\S]*savePetWindowBounds\(petWindow\);[\s\S]*petWindow\.hide\(\);/,
    "main.js"
  );
  assertRegex(
    main,
    /function showPetWindow\(\)[\s\S]*const win = petWindow && !petWindow\.isDestroyed\(\) \? petWindow : createPetWindow\(\);[\s\S]*ensurePetWindowVisibleBounds\(win, \{ persist: true \}\);[\s\S]*win\.show\(\);[\s\S]*win\.focus\(\);/,
    "main.js"
  );
}

function testPetWindowScalePresetsAndMediumDefault() {
  // TASK-166B: replaces testPetWindowSizeRemainsFixedAt300By400
  const main = readText(mainPath);
  assertIncludes(main, "PET_WINDOW_WIDTH = 300", "main.js");
  assertIncludes(main, "PET_WINDOW_HEIGHT = 400", "main.js");
  assertNotIncludes(main, "PET_WINDOW_WIDTH = 260", "main.js");
  assertNotIncludes(main, "PET_WINDOW_HEIGHT = 340", "main.js");
  // Scale preset constants
  assertIncludes(main, 'PET_SCALE_SMALL  = Object.freeze({ name: "small",  width: 225, height: 300 })', "main.js");
  assertIncludes(main, 'PET_SCALE_MEDIUM = Object.freeze({ name: "medium", width: 300, height: 400 })', "main.js");
  assertIncludes(main, 'PET_SCALE_LARGE  = Object.freeze({ name: "large",  width: 375, height: 500 })', "main.js");
  // BrowserWindow uses petBounds (scale-resolved)
  assertRegex(
    main,
    /width:\s*petBounds\.width[\s\S]*height:\s*petBounds\.height[\s\S]*resizable:\s*false[\s\S]*title:\s*"Dragon Pet AI - Pet Mode"/,
    "main.js"
  );
}

function testFullAppWindowStillExists() {
  const main = readText(mainPath);
  assertIncludes(main, "function createWindow()", "main.js");
  assertIncludes(main, "function showFullAppWindow()", "main.js");
  assertIncludes(main, 'path.join(__dirname, "renderer", "index.html")', "main.js");
  assertIncludes(main, "BACKEND_URL", "main.js");
  assertIncludes(main, "createWindow();", "main.js");
}

function testPetOpenFullAppIpcIsFixedAndNarrow() {
  const main = readText(mainPath);
  assertIncludes(main, 'PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app"', "main.js");
  assertIncludes(main, 'PET_SHOW_WINDOW_CHANNEL = "pet:show-window"', "main.js");
  assertIncludes(main, 'PET_RESET_POSITION_CHANNEL = "pet:reset-position"', "main.js");
  assertIncludes(main, 'PET_HIDE_WINDOW_CHANNEL = "pet:hide-window"', "main.js");
  assertIncludes(main, 'PET_SPEECH_UPDATE_CHANNEL = "pet:speech-update"', "main.js");
  assertIncludes(main, 'PET_SPEECH_RECEIVED_CHANNEL = "pet:speech-received"', "main.js");
  assertIncludes(main, "ipcMain.handle(PET_OPEN_FULL_APP_CHANNEL, () =>", "main.js");
  assertIncludes(main, "ipcMain.handle(PET_SHOW_WINDOW_CHANNEL, () => showPetWindow())", "main.js");
  assertIncludes(main, "ipcMain.handle(PET_RESET_POSITION_CHANNEL, () => resetPetWindowPosition())", "main.js");
  assertIncludes(main, "ipcMain.handle(PET_HIDE_WINDOW_CHANNEL, () => hidePetWindow())", "main.js");
  assertIncludes(main, "ipcMain.handle(PET_SPEECH_UPDATE_CHANNEL", "main.js");
  assertIncludes(main, "function sanitizePetSpeechPayload(payload = {})", "main.js");
  assertIncludes(main, "function forwardPetSpeechUpdate(payload = {})", "main.js");
  assertIncludes(main, "PET_SPEECH_REPLY_MAX_LENGTH = 800", "main.js");
  assertIncludes(main, "reply, mood, source", "main.js");
  assertIncludes(main, "petWindow.webContents.send(PET_SPEECH_RECEIVED_CHANNEL, safePayload)", "main.js");
  assertIncludes(main, 'reason: "pet_window_hidden"', "main.js");
  assertIncludes(main, "showFullAppWindow();", "main.js");
  assertIncludes(main, "win.restore();", "main.js");
  assertIncludes(main, "win.show();", "main.js");
  assertIncludes(main, "win.focus();", "main.js");
  assertIncludes(main, "function resetPetWindowPosition()", "main.js");
  assertIncludes(main, "function hidePetWindow()", "main.js");
  assertIncludes(main, "function showPetWindow()", "main.js");
  assertIncludes(main, 'return { ok: false, reason: "pet_mode_disabled" }', "main.js");
  assertIncludes(main, "const win = petWindow && !petWindow.isDestroyed() ? petWindow : createPetWindow()", "main.js");
  assertIncludes(main, "petWindow.setBounds(bounds)", "main.js");
  assertIncludes(main, "petWindow.hide();", "main.js");
  assertIncludes(main, "win.show();", "main.js");
  assertIncludes(main, "win.focus();", "main.js");
  // ipcMain.on() is legitimately used in Screen Context picker functions
  // (TASK-174/175/176) with proper ipcMain.removeListener() cleanup.
  // Guard: pet IPC channels must still use ipcMain.handle(), not ipcMain.on().
  assertNotIncludes(main, "ipcMain.on(PET_", "main.js");
  // Guard: every ipcMain.on() must be paired with ipcMain.removeListener().
  assertIncludes(main, "ipcMain.removeListener(", "main.js");
}

function testPetSpeechPayloadSanitizersDropDiagnostics() {
  const main = readText(mainPath);
  const rendererPreload = readText(rendererPreloadPath);
  const petPreload = readText(petPreloadPath);

  assertIncludes(main, "function sanitizePetSpeechPayload(payload = {})", "main.js");
  assertIncludes(main, "return { reply, mood, source };", "main.js");

  for (const [label, text] of [
    ["renderer/preload.js", rendererPreload],
    ["pet-preload.js", petPreload],
  ]) {
    assertIncludes(text, "function sanitizePetSpeechPayload(payload = {})", label);
    assertRegex(
      text,
      /return \{\s*reply:[\s\S]*mood:[\s\S]*source:[\s\S]*\};/,
      label
    );
    assertNotIncludes(text, "diagnostics:", label);
    assertNotIncludes(text, "details:", label);
    assertNotIncludes(text, "debug:", label);
    assertNotIncludes(text, "provider:", label);
  }

  for (const field of ["diagnostics:", "details:", "debug:", "provider:"]) {
    assertNotIncludes(main, field, "main.js");
  }
}

function testPetWindowDoesNotReplaceFullAppByDefault() {
  const main = readText(mainPath);
  assertIncludes(main, "if (PET_MODE_ENABLED)", "main.js");
  assertNotIncludes(main, "const PET_MODE_ENABLED = true", "main.js");
}

function testNoRendererDirectOllamaAccess() {
  for (const [label, filePath] of [
    ["renderer.js", rendererPath],
    ["renderer/preload.js", rendererPreloadPath],
    ["pet-renderer.js", petRendererPath],
    ["pet-preload.js", petPreloadPath],
  ]) {
    const text = readText(filePath);
    assertNotIncludes(text, "localhost:11434", label);
    assertNotIncludes(text, "127.0.0.1:11434", label);
    assertNotIncludes(text, "11434", label);
  }
}

function testFullAppShowPetEntryAndPreloadAreNarrow() {
  const html = readText(rendererHtmlPath);
  const renderer = readText(rendererPath);
  const preload = readText(rendererPreloadPath);

  assertIncludes(html, 'id="show-pet-window-btn"', "index.html");
  assertIncludes(html, 'id="show-pet-window-status"', "index.html");
  assertIncludes(renderer, "showPetWindowFromFullApp", "renderer.js");
  assertIncludes(renderer, "api.showPetWindow()", "renderer.js");
  assertIncludes(renderer, "Pet Mode disabled. Start with PET_MODE_ENABLED=true.", "renderer.js");
  assertIncludes(preload, 'PET_SHOW_WINDOW_CHANNEL = "pet:show-window"', "renderer/preload.js");
  assertIncludes(preload, 'PET_SPEECH_UPDATE_CHANNEL = "pet:speech-update"', "renderer/preload.js");
  assertIncludes(preload, 'contextBridge.exposeInMainWorld(', "renderer/preload.js");
  assertIncludes(preload, '"dragonPet"', "renderer/preload.js");
  assertIncludes(preload, "showPetWindow: () => ipcRenderer.invoke(PET_SHOW_WINDOW_CHANNEL)", "renderer/preload.js");
  assertIncludes(preload, "updatePetSpeech: (payload) =>", "renderer/preload.js");
  assertIncludes(preload, "sanitizePetSpeechPayload(payload)", "renderer/preload.js");
  assertNotIncludes(preload, "exposeInMainWorld(\"ipcRenderer\"", "renderer/preload.js");
  assertNotIncludes(preload, "send(", "renderer/preload.js");
  assertNotIncludes(preload, "sendSync", "renderer/preload.js");
  assertNotIncludes(preload, 'require("fs")', "renderer/preload.js");
  assertNotIncludes(preload, 'require("node:fs")', "renderer/preload.js");
  assertNotIncludes(preload, "shell", "renderer/preload.js");
  assertNotIncludes(preload, "process", "renderer/preload.js");
}

function testPetRendererUsesOnlyBackendChatPath() {
  const text = readText(petRendererPath);
  assertIncludes(text, "sendPetChatMessage", "pet-renderer.js");
  assertIncludes(text, '`${backendUrl}/chat`', "pet-renderer.js");
  assertIncludes(text, "buildChatPayload", "pet-renderer.js");
  assertIncludes(text, 'use_memory: false', "pet-renderer.js");
  assertNotIncludes(text, "fetch('/chat'", "pet-renderer.js");
  assertNotIncludes(text, 'fetch("/chat"', "pet-renderer.js");
  assertNotIncludes(text, "localhost:11434", "pet-renderer.js");
  assertNotIncludes(text, "127.0.0.1:11434", "pet-renderer.js");
  assertNotIncludes(text, "11434", "pet-renderer.js");
}

function testPetPreloadExposesOnlyFixedPetActions() {
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app"', "pet-preload.js");
  assertIncludes(preload, 'PET_RESET_POSITION_CHANNEL = "pet:reset-position"', "pet-preload.js");
  assertIncludes(preload, 'PET_HIDE_WINDOW_CHANNEL = "pet:hide-window"', "pet-preload.js");
  assertIncludes(preload, 'PET_SPEECH_RECEIVED_CHANNEL = "pet:speech-received"', "pet-preload.js");
  assertIncludes(preload, 'contextBridge.exposeInMainWorld(', "pet-preload.js");
  assertIncludes(preload, '"dragonPet"', "pet-preload.js");
  assertIncludes(preload, "openFullApp: () => ipcRenderer.invoke(PET_OPEN_FULL_APP_CHANNEL)", "pet-preload.js");
  assertIncludes(preload, "resetPetPosition: () => ipcRenderer.invoke(PET_RESET_POSITION_CHANNEL)", "pet-preload.js");
  assertIncludes(preload, "hidePetWindow: () => ipcRenderer.invoke(PET_HIDE_WINDOW_CHANNEL)", "pet-preload.js");
  assertIncludes(preload, "onSpeechUpdate", "pet-preload.js");
  assertIncludes(preload, "ipcRenderer.on(PET_SPEECH_RECEIVED_CHANNEL, listener)", "pet-preload.js");
  assertIncludes(preload, "ipcRenderer.removeListener(PET_SPEECH_RECEIVED_CHANNEL, listener)", "pet-preload.js");
  assertNotIncludes(preload, "removeAllListeners", "pet-preload.js");
  assertNotIncludes(preload, "exposeInMainWorld(\"ipcRenderer\"", "pet-preload.js");
  assertNotIncludes(preload, "send(", "pet-preload.js");
  assertNotIncludes(preload, "sendSync", "pet-preload.js");
  assertNotIncludes(preload, 'require("fs")', "pet-preload.js");
  assertNotIncludes(preload, 'require("node:fs")', "pet-preload.js");
  assertNotIncludes(preload, "shell", "pet-preload.js");
  assertNotIncludes(preload, "process", "pet-preload.js");
}


function testQuietModePersistenceIpcAndStorageInMain() {
  // TASK-162: verify quiet mode persistence functions + IPC handler exist in main.js
  const main = readText(mainPath);
  assertIncludes(main, 'PET_QUIET_MODE_SET_CHANNEL = "pet:set-quiet-mode"', "main.js");
  assertIncludes(main, "function loadPetQuietMode()", "main.js");
  assertIncludes(main, "function savePetQuietMode(value)", "main.js");
  assertIncludes(main, "return parsed.quietMode === true;", "main.js");
  assertIncludes(main, "const quietMode = value === true;", "main.js");
  assertIncludes(main, "ipcMain.handle(PET_QUIET_MODE_SET_CHANNEL", "main.js");
  assertIncludes(main, "savePetQuietMode(value);", "main.js");
}

function testQuietModePersistenceSaveMergesExistingState() {
  // TASK-162: savePetWindowBounds must merge-write to preserve quietMode alongside position
  const main = readText(mainPath);
  // Verify merge pattern: read existing then spread before writing
  assertIncludes(main, "let existing = {};", "main.js");
  assertIncludes(main, "existing = JSON.parse(raw);", "main.js");
  assertIncludes(main, "const state = { ...existing,", "main.js");
}

function testQuietModePersistenceStartupUrlParam() {
  // TASK-162: main.js must pass ?quietMode= URL param when loading pet.html
  const main = readText(mainPath);
  assertIncludes(main, "const initialQuietMode = loadPetQuietMode();", "main.js");
  assertIncludes(main, "?quietMode=${initialQuietMode}", "main.js");
  assertIncludes(main, "petWindow.loadURL(", "main.js");
}

function testQuietModePersistencePreloadExposesSetter() {
  // TASK-162: pet-preload.js must expose setQuietMode via the narrow IPC channel
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_QUIET_MODE_SET_CHANNEL = "pet:set-quiet-mode"', "pet-preload.js");
  assertIncludes(preload, "setQuietMode: (value) => ipcRenderer.invoke(PET_QUIET_MODE_SET_CHANNEL", "pet-preload.js");
  assertIncludes(preload, "value === true", "pet-preload.js");
  // Must not expose filesystem or broad APIs
  assertNotIncludes(preload, 'require("fs")', "pet-preload.js");
  assertNotIncludes(preload, 'require("node:fs")', "pet-preload.js");
}

function testQuietModePersistenceRendererCallsPersistOnToggle() {
  // TASK-162: pet-renderer.js must call dragonPet.setQuietMode on menu toggle
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "dragonPetApi.setQuietMode(newQuietMode)", "pet-renderer.js");
  assertIncludes(renderer, "typeof dragonPetApi.setQuietMode === \"function\"", "pet-renderer.js");
  // Must read URL param for startup restore
  assertIncludes(renderer, "new URLSearchParams(window.location.search)", "pet-renderer.js");
  assertIncludes(renderer, 'urlParams.get("quietMode") === "true"', "pet-renderer.js");
  // Must guard against missing window/dragonPet (Node test env safety)
  assertIncludes(renderer, 'typeof window !== "undefined" && window.dragonPet ? window.dragonPet : null', "pet-renderer.js");
}

function testPetOverlayShellSkipsTaskbar() {
  // TASK-166A: companion overlay must not appear as a normal app in the taskbar
  const main = readText(mainPath);
  assertRegex(main, /skipTaskbar:\s*true/, "main.js");
}

function testPetOverlayShellTransparentBackground() {
  // TASK-166A: explicit #00000000 backgroundColor ensures GPU-driver transparency compat
  const main = readText(mainPath);
  assertIncludes(main, 'backgroundColor: "#00000000"', "main.js");
  // Sanity: transparent and frame:false must still be present
  assertRegex(main, /transparent:\s*true/, "main.js");
  assertRegex(main, /frame:\s*false/, "main.js");
}



function testPetScalePresetsConstants() {
  // TASK-166B: verify scale preset constants exist with correct dimensions
  const main = readText(mainPath);
  assertIncludes(main, 'PET_SCALE_SET_CHANNEL = "pet:set-scale"', "main.js");
  assertIncludes(main, "function getScaleDimensions(scaleName)", "main.js");
  assertIncludes(main, "function loadPetScale()", "main.js");
  assertIncludes(main, "function savePetScale(scaleName)", "main.js");
  assertIncludes(main, "width: 225", "main.js");
  assertIncludes(main, "height: 300", "main.js");
  assertIncludes(main, "width: 375", "main.js");
  assertIncludes(main, "height: 500", "main.js");
}

function testPetScaleLoadFallsBackToMedium() {
  // TASK-166B: loadPetScale must fall back to "medium" for unknown values
  const main = readText(mainPath);
  assertIncludes(main, 'if (s === "small" || s === "large") return s;', "main.js");
  assertIncludes(main, 'return "medium";', "main.js");
}

function testPetScalePersistsMergesExistingState() {
  // TASK-166B: savePetScale uses merge-write like quietMode and position
  const main = readText(mainPath);
  assertIncludes(main, "function savePetScale(scaleName)", "main.js");
  assertIncludes(main, "const state = { ...existing, scale };", "main.js");
}

function testPetScaleIpcHandlerExists() {
  // TASK-166B: set-scale IPC handler must clamp position and resize window
  const main = readText(mainPath);
  assertIncludes(main, "ipcMain.handle(PET_SCALE_SET_CHANNEL", "main.js");
  assertIncludes(main, "petWindow.setBounds({ x, y, width: dims.width, height: dims.height })", "main.js");
  assertIncludes(main, "screen.getDisplayNearestPoint", "main.js");
}

function testPetScalePreloadExposesSetter() {
  // TASK-166B: pet-preload.js must expose setScale via narrow IPC channel
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_SCALE_SET_CHANNEL = "pet:set-scale"', "pet-preload.js");
  assertIncludes(preload, "setScale: (value) => ipcRenderer.invoke(PET_SCALE_SET_CHANNEL, value)", "pet-preload.js");
  assertNotIncludes(preload, 'require("fs")', "pet-preload.js");
}

function testPetScaleStartupUrlParam() {
  // TASK-166B: main.js must pass ?scale= URL param when loading pet.html
  const main = readText(mainPath);
  assertIncludes(main, "const initialScale = loadPetScale();", "main.js");
  assertIncludes(main, "&scale=${initialScale}", "main.js");
}

function testPetScaleResetPositionUsesActiveDims() {
  // TASK-166B: reset uses active scale dims, not hardcoded 300x400
  const main = readText(mainPath);
  assertIncludes(main, "const dims = getScaleDimensions(loadPetScale());", "main.js");
  assertIncludes(main, "const bounds = getDefaultPetWindowBounds(dims);", "main.js");
}

function testPetScaleDefaultBoundsAcceptsDimsParam() {
  // TASK-166B: getDefaultPetWindowBounds accepts dims parameter
  const main = readText(mainPath);
  assertRegex(main, /function getDefaultPetWindowBounds\(dims = PET_SCALE_MEDIUM\)/, "main.js");
}

function testClickThroughIpcChannelInMain() {
  // TASK-166D: verify click-through IPC channel constant and handler exist in main.js
  const main = readText(mainPath);
  assertIncludes(main, 'PET_CLICK_THROUGH_SET_CHANNEL = "pet:set-click-through"', "main.js");
  assertIncludes(main, "ipcMain.handle(PET_CLICK_THROUGH_SET_CHANNEL", "main.js");
  assertIncludes(main, "setIgnoreMouseEvents(true, { forward: true })", "main.js");
  assertIncludes(main, "setIgnoreMouseEvents(false)", "main.js");
  assertIncludes(main, "const enabled = value === true;", "main.js");
  // TASK-166E click-fix: when CT goes OFF, OS focus must be restored
  assertRegex(
    main,
    /setIgnoreMouseEvents\(false\)[\s\S]{0,120}petWindow\.focus\(\)/,
    "main.js CT-off handler must call petWindow.focus() (TASK-166E click-fix)"
  );
}

function testClickThroughPreloadExposesSetter() {
  // TASK-166D: pet-preload.js must expose setClickThrough via narrow IPC channel
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_CLICK_THROUGH_SET_CHANNEL = "pet:set-click-through"', "pet-preload.js");
  assertIncludes(preload, "setClickThrough: (enabled) => ipcRenderer.invoke(PET_CLICK_THROUGH_SET_CHANNEL", "pet-preload.js");
  assertIncludes(preload, "enabled === true", "pet-preload.js");
  assertNotIncludes(preload, 'require("fs")', "pet-preload.js");
}

function testClickThroughRendererHasFunctions() {
  // TASK-166D: pet-renderer.js must export click-through helpers
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "function getPetClickThrough", "pet-renderer.js");
  assertIncludes(renderer, "function setPetClickThrough", "pet-renderer.js");
  assertIncludes(renderer, "function forceClickThroughOff", "pet-renderer.js");
  assertIncludes(renderer, "clickThrough: false", "pet-renderer.js");
  // recovery strip
  assertIncludes(renderer, 'addEventListener("pointerenter"', "pet-renderer.js");
  assertIncludes(renderer, "forceClickThroughOff(documentRef)", "pet-renderer.js");
}

function testClickThroughForwardFlagIsPresent() {
  // TASK-166D: { forward: true } must be present so renderer still receives mousemove while click-through is ON
  const main = readText(mainPath);
  assertIncludes(main, "{ forward: true }", "main.js");
}



// ── TASK-166E: Pet Direct Text Input window-level checks ──────────────────────

function testDirectInputRendererHasFunctions() {
  // TASK-166E: all four direct input functions must be present and exported
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "function isPetDirectInputOpen", "pet-renderer.js");
  assertIncludes(renderer, "function openPetDirectInput", "pet-renderer.js");
  assertIncludes(renderer, "function closePetDirectInput", "pet-renderer.js");
  assertIncludes(renderer, "function handlePetDirectSend", "pet-renderer.js");
  assertIncludes(renderer, "isPetDirectInputOpen,", "pet-renderer.js exports");
  assertIncludes(renderer, "openPetDirectInput,", "pet-renderer.js exports");
  assertIncludes(renderer, "closePetDirectInput,", "pet-renderer.js exports");
  assertIncludes(renderer, "handlePetDirectSend,", "pet-renderer.js exports");
}

function testDirectInputNoNewIpc() {
  // TASK-166E: Pet direct input calls /chat via fetch from renderer — no new IPC channel
  const main = readText(mainPath);
  assertNotIncludes(main, "pet:send-chat", "main.js");
  const preload = readText(petPreloadPath);
  assertNotIncludes(preload, "pet:send-chat", "pet-preload.js");
}

function testDirectInputHtmlElements() {
  // TASK-166E: required HTML elements exist in pet.html
  const html = readText(petHtmlPath);
  assertIncludes(html, 'id="pet-direct-input-panel"', "pet.html");
  assertIncludes(html, 'id="pet-direct-input-form"', "pet.html");
  assertIncludes(html, 'id="pet-direct-input-field"', "pet.html");
  assertIncludes(html, 'id="pet-direct-input-send"', "pet.html");
  assertIncludes(html, 'id="pet-direct-input-close"', "pet.html");
}


function testDirectInputClickFixFocusRestoredInMain() {
  // TASK-166E click-fix: when CT goes OFF via IPC, main.js must call petWindow.focus()
  // so the window regains OS focus and the direct input field can receive keyboard events.
  const main = readText(mainPath);
  assertRegex(
    main,
    /setIgnoreMouseEvents\(false\)[\s\S]{0,120}petWindow\.focus\(\)/,
    "main.js must call petWindow.focus() after setIgnoreMouseEvents(false) (TASK-166E click-fix)"
  );
  // forceClickThroughOff in renderer must return the IPC promise
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "return api.setClickThrough(false);", "pet-renderer.js");
  // openPetDirectInput must be declared async
  assertRegex(renderer, /async function openPetDirectInput/, "pet-renderer.js");
  // defensive pointerdown listener on panel
  assertRegex(renderer, /directInputPanel[\s\S]{0,200}pointerdown[\s\S]{0,200}forceClickThroughOff/, "pet-renderer.js");
  // defensive focus listener on field
  assertRegex(renderer, /directInputField[\s\S]{0,200}"focus"[\s\S]{0,200}forceClickThroughOff/, "pet-renderer.js");
}

// ── TASK-167A: Pet Voice / Mic push-to-talk window-level smoke tests ─────────

function testVoiceRecordingFunctionsExportedFromRenderer() {
  // TASK-167A: all voice functions + constants must be in module.exports
  const renderer = readText(petRendererPath);
  const exportedNames = [
    "isPetRecordingActive",
    "setRecordingState",
    "openPetVoiceRecording",
    "cancelPetVoiceRecording",
    "stopPetVoiceRecording",
    "transcribeAudioBlob",
    "PET_RECORDING_MAX_MS",
    "PET_VOICE_MIC_DENIED_MSG",
    "PET_VOICE_NO_MIC_MSG",
    "PET_VOICE_UNSUPPORTED_MSG",
    "PET_VOICE_RECORDING_STATUS",
  ];
  for (const name of exportedNames) {
    assertRegex(renderer, new RegExp(`\\b${name}\\b`), `pet-renderer.js — ${name} must be exported`);
  }
}

function testNoNewIpcChannelsForMic() {
  // TASK-167A: getUserMedia is a browser API — no new IPC channels should exist for mic capture.
  // The preload must NOT expose mic-specific bridges (getUserMedia works directly in renderer).
  const preload = readText(petPreloadPath);
  assertNotIncludes(preload, "mic", "pet-preload.js — no mic IPC channel expected");
  assertNotIncludes(preload, "getUserMedia", "pet-preload.js — getUserMedia must not be bridged via IPC");
  assertNotIncludes(preload, "MediaRecorder", "pet-preload.js — MediaRecorder must not be bridged via IPC");
  // Main must also have no new IPC channel registered for mic
  const main = readText(mainPath);
  assertNotIncludes(main, "pet:mic", "main.js — no pet:mic IPC channel expected");
  assertNotIncludes(main, "getUserMedia", "main.js — getUserMedia is renderer-side, not in main");
}

function testMicPermissionHandlerInMain() {
  // TASK-167A: main.js must have a narrow setPermissionRequestHandler for Pet window
  // that allows 'media' and denies everything else.
  const main = readText(mainPath);
  assertIncludes(main, "setPermissionRequestHandler", "main.js — mic permission handler must be present");
  // Handler must allow 'media'
  assertRegex(main, /permission\s*===\s*["']media["']/, "main.js — handler must check for 'media' permission");
  // Handler must be scoped to petWindow (not the main renderer session)
  assertRegex(main, /petWindow[\s\S]{0,200}setPermissionRequestHandler/, "main.js — handler must be on petWindow");
}


// ── TASK-167B: STT IPC bridge and transcription smoke tests ──────────────────

function testSttIpcBridgeExposedInPreload() {
  // TASK-167B: pet-preload.js must expose dragonPet.transcribeAudio via IPC
  const preload = fs.readFileSync(
    path.join(__dirname, "../src/pet/pet-preload.js"), "utf8"
  );
  assertIncludes(preload, "stt:transcribe", "pet-preload.js -- stt:transcribe channel defined");
  assertIncludes(preload, "transcribeAudio", "pet-preload.js -- transcribeAudio exposed on dragonPet");
  assertIncludes(preload, "ipcRenderer.invoke", "pet-preload.js -- transcribeAudio uses ipcRenderer.invoke");
}

function testSttIpcHandlerInMain() {
  // TASK-167B: main.js must register an ipcMain.handle for stt:transcribe
  const main = fs.readFileSync(
    path.join(__dirname, "../src/main.js"), "utf8"
  );
  assertIncludes(main, "stt:transcribe", "main.js -- stt:transcribe channel");
  assertIncludes(main, "ipcMain.handle", "main.js -- ipcMain.handle registers stt handler");
  // handler must POST to /stt/transcribe (backend endpoint)
  assertIncludes(main, "/stt/transcribe", "main.js -- handler POSTs to /stt/transcribe");
  // must use Node http (no electron-fetch / axios added)
  assertIncludes(main, "require(\"http\")", "main.js -- uses built-in http for STT request");
}

function testSttHandlerNoPersistenceInMain() {
  // TASK-167B: stt:transcribe IPC handler must not write audio to disk
  const main = fs.readFileSync(
    path.join(__dirname, "../src/main.js"), "utf8"
  );
  // Find the stt handler block — anchor on the handler comment directly above ipcMain.handle
  const sttHandlerMatch = main.match(/\/\/ TASK-167B: stt:transcribe IPC handler[\s\S]*?ipcMain\.handle\(PET_STT_TRANSCRIBE_CHANNEL[\s\S]*?\}\s*\)\s*;/);
  assert(sttHandlerMatch, "main.js -- stt:transcribe handler block found");
  assertNotIncludes(sttHandlerMatch[0], "createWriteStream", "main.js -- no createWriteStream in stt handler");
  assertNotIncludes(sttHandlerMatch[0], "fs.write", "main.js -- no fs.write in stt handler");
  assertNotIncludes(sttHandlerMatch[0], "writeFile", "main.js -- no writeFile in stt handler");
}

function testSttTranscribeAudioBlobFunctionsInRenderer() {
  // TASK-167B: pet-renderer.js must export transcribeAudioBlob + STT state helpers
  const renderer = fs.readFileSync(
    path.join(__dirname, "../src/pet/pet-renderer.js"), "utf8"
  );
  assertIncludes(renderer, "transcribeAudioBlob", "pet-renderer.js -- transcribeAudioBlob defined");
  assertIncludes(renderer, "isTranscribingActive", "pet-renderer.js -- isTranscribingActive exported");
  assertIncludes(renderer, "setTranscribingState", "pet-renderer.js -- setTranscribingState exported");
  // transcribeAudioBlob function body must not forward to /chat — extract just that function
  const transcribeFnMatch = renderer.match(/async function transcribeAudioBlob[\s\S]*?\n\}/);
  assert(transcribeFnMatch, "pet-renderer.js -- transcribeAudioBlob function body found");
  assertNotIncludes(transcribeFnMatch[0], "sendPetChatMessage",
    "pet-renderer.js -- transcribeAudioBlob does not call sendPetChatMessage (TASK-167C boundary)");
  assertNotIncludes(transcribeFnMatch[0], "fetch(",
    "pet-renderer.js -- transcribeAudioBlob does not call fetch() directly");
}

// ---------------------------------------------------------------------------
// TASK-193: Pet chat mirror IPC channel checks
// ---------------------------------------------------------------------------

function testTask193ChatMirrorChannelInPetPreload() {
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_CHAT_MIRROR_CHANNEL = "pet:chat-mirror"', "pet-preload.js");
  assertIncludes(preload, "mirrorChatToFullApp:", "pet-preload.js");
  assertIncludes(preload, "ipcRenderer.invoke(PET_CHAT_MIRROR_CHANNEL", "pet-preload.js");
  assertIncludes(preload, "sanitizeMirrorPayload", "pet-preload.js");
}

function testTask193ChatMirrorChannelInMain() {
  const main = readText(mainPath);
  assertIncludes(main, 'PET_CHAT_MIRROR_CHANNEL = "pet:chat-mirror"', "main.js");
  assertIncludes(main, 'PET_CHAT_MIRROR_RECEIVED_CHANNEL = "pet:chat-mirror-received"', "main.js");
  assertIncludes(main, "ipcMain.handle(PET_CHAT_MIRROR_CHANNEL", "main.js");
}

function testTask193ChatMirrorChannelInRendererPreload() {
  const preload = readText(rendererPreloadPath);
  assertIncludes(preload, 'PET_CHAT_MIRROR_RECEIVED_CHANNEL = "pet:chat-mirror-received"', "renderer/preload.js");
  assertIncludes(preload, "onChatMirrorFromPet", "renderer/preload.js");
  assertIncludes(preload, "ipcRenderer.on(PET_CHAT_MIRROR_RECEIVED_CHANNEL", "renderer/preload.js");
  assertIncludes(preload, "ipcRenderer.removeListener(PET_CHAT_MIRROR_RECEIVED_CHANNEL", "renderer/preload.js");
}

function testTask193MainMirrorHandlerSanitizesPayload() {
  const main = readText(mainPath);
  // handler must sanitize userMessage and reply (slice to max length)
  assertIncludes(main, "PET_CHAT_MIRROR_USER_MAX_LENGTH", "main.js");
  assertIncludes(main, "PET_SPEECH_REPLY_MAX_LENGTH", "main.js mirror uses reply max");
  // must be no-op when fullAppWindow missing
  assertIncludes(main, "full_app_unavailable", "main.js mirror handler must return ok:false when Full App unavailable");
  // must guard empty payload
  assertIncludes(main, "empty_payload", "main.js mirror handler must return ok:false for empty payload");
}

// ---------------------------------------------------------------------------
// TASK-194: Chat History Persistence IPC channel checks
// ---------------------------------------------------------------------------

function testTask194ChatHistoryChannelsInMain() {
  const main = readText(mainPath);
  assertIncludes(main, 'CHAT_HISTORY_APPEND_CHANNEL = "chat-history:append"', "main.js");
  assertIncludes(main, 'CHAT_HISTORY_LOAD_CHANNEL   = "chat-history:load"', "main.js");
  assertIncludes(main, 'CHAT_HISTORY_CLEAR_CHANNEL  = "chat-history:clear"', "main.js");
  assertIncludes(main, "ipcMain.handle(CHAT_HISTORY_APPEND_CHANNEL", "main.js");
  assertIncludes(main, "ipcMain.handle(CHAT_HISTORY_LOAD_CHANNEL", "main.js");
  assertIncludes(main, "ipcMain.handle(CHAT_HISTORY_CLEAR_CHANNEL", "main.js");
  assertIncludes(main, "getChatHistoryPath", "main.js");
  assertIncludes(main, "invalid_role", "main.js append handler must guard role");
  assertIncludes(main, "CHAT_HISTORY_MAX_ENTRIES", "main.js must cap history length");
  assertIncludes(main, "CHAT_HISTORY_TEXT_MAX", "main.js must cap text length");
}

// ---------------------------------------------------------------------------
// TASK-195: inputMethod mirror pipeline checks
// ---------------------------------------------------------------------------

function testTask195InputMethodInMirrorPipeline() {
  // pet-preload.js sanitizeMirrorPayload must include inputMethod
  const petPreload = readText(petPreloadPath);
  assertIncludes(petPreload, "inputMethod:", "pet-preload.js sanitizeMirrorPayload must include inputMethod field");
  assertIncludes(petPreload, '"voice"', "pet-preload.js must validate inputMethod voice value");
  // main.js mirror handler must forward inputMethod
  const main = readText(mainPath);
  assertIncludes(main, "inputMethod", "main.js mirror handler must forward inputMethod");
  assertRegex(main, /inputMethod.*voice.*text|voice.*inputMethod/, "main.js must guard inputMethod to voice|text");
  // renderer/preload.js listener must include inputMethod
  const preload = readText(rendererPreloadPath);
  assertIncludes(preload, "inputMethod:", "renderer/preload.js listener must include inputMethod field");
}

function testTask194ChatHistoryChannelsInRendererPreload() {
  const preload = readText(rendererPreloadPath);
  assertIncludes(preload, 'CHAT_HISTORY_APPEND_CHANNEL = "chat-history:append"', "renderer/preload.js");
  assertIncludes(preload, 'CHAT_HISTORY_LOAD_CHANNEL   = "chat-history:load"', "renderer/preload.js");
  assertIncludes(preload, 'CHAT_HISTORY_CLEAR_CHANNEL  = "chat-history:clear"', "renderer/preload.js");
  assertIncludes(preload, "chatHistoryAppend", "renderer/preload.js");
  assertIncludes(preload, "chatHistoryLoad", "renderer/preload.js");
  assertIncludes(preload, "chatHistoryClear", "renderer/preload.js");
  assertIncludes(preload, "sanitizeChatHistoryEntry", "renderer/preload.js");
}

function testTask195VisMenuHiddenInMain() {
  const main = readText(mainPath);
  assertIncludes(main, "Menu", "main.js must import Menu from electron");
  assertIncludes(main, "Menu.setApplicationMenu(null)", "main.js must remove native application menu");
}

// ---------------------------------------------------------------------------
// TASK-196: Clipboard bridge surface checks
// ---------------------------------------------------------------------------

function testTask196ClipboardBridgeInRendererPreload() {
  const preload = readText(rendererPreloadPath);
  assertIncludes(preload, "writeClipboardText", "renderer/preload.js must expose writeClipboardText");
  assertIncludes(preload, '"clipboard:write-text"', "renderer/preload.js must define clipboard:write-text IPC channel");
  assertIncludes(preload, "ipcRenderer.invoke(CLIPBOARD_WRITE_TEXT_CHANNEL", "renderer/preload.js must route clipboard write via ipcRenderer.invoke");
  assertIncludes(preload, "20000", "renderer/preload.js writeClipboardText must cap text at 20000 chars");
  assertNotIncludes(preload, 'exposeInMainWorld("clipboard"', "renderer/preload.js must not expose raw clipboard API");
  assertNotIncludes(preload, "clipboard.writeText", "renderer/preload.js must not call clipboard.writeText directly — routes via main IPC");
}

function testTask196ClipboardIpcHandlerInMain() {
  const main = readText(mainPath);
  assertIncludes(main, 'CLIPBOARD_WRITE_TEXT_CHANNEL = "clipboard:write-text"', "main.js must define clipboard:write-text channel constant");
  assertIncludes(main, "ipcMain.handle(CLIPBOARD_WRITE_TEXT_CHANNEL", "main.js must register clipboard:write-text IPC handler");
  assertIncludes(main, "clipboard.writeText", "main.js clipboard handler must call clipboard.writeText");
  assertRegex(main, /clipboard\s*[,}]/, "main.js must import clipboard from electron");
}

// ── TASK-204: Pet Window Unread Dot Badge ─────────────────────────────────────

function testTask204UnreadDotChannelsInMain() {
  const main = readText(mainPath);
  assertIncludes(main, 'PET_UNREAD_DOT_CHANNEL = "pet:unread-dot"', "main.js must define PET_UNREAD_DOT_CHANNEL");
  assertIncludes(main, 'PET_UNREAD_DOT_RECEIVED_CHANNEL = "pet:unread-dot-received"', "main.js must define PET_UNREAD_DOT_RECEIVED_CHANNEL");
  assertIncludes(main, "ipcMain.handle(PET_UNREAD_DOT_CHANNEL", "main.js must register unread-dot IPC handler");
  assertIncludes(main, "petWindow.webContents.send(PET_UNREAD_DOT_RECEIVED_CHANNEL", "main.js must forward unread count to petWindow");
}

function testTask204UnreadDotPayloadSanitizedInMain() {
  const main = readText(mainPath);
  const fnIdx = main.indexOf("ipcMain.handle(PET_UNREAD_DOT_CHANNEL");
  const fnText = main.slice(fnIdx, fnIdx + 400);
  assertIncludes(fnText, "unreadCount", "unread-dot IPC handler must use unreadCount field");
  assertIncludes(fnText, "typeof payload.unreadCount", "unread-dot handler must validate unreadCount type");
  assertIncludes(fnText, "pet_window_unavailable", "unread-dot handler must guard petWindow availability");
}

function testTask204UnreadDotChannelInRendererPreload() {
  const preload = readText(rendererPreloadPath);
  assertIncludes(preload, 'PET_UNREAD_DOT_CHANNEL = "pet:unread-dot"', "renderer preload.js must define PET_UNREAD_DOT_CHANNEL");
  assertIncludes(preload, "notifyUnreadDot", "renderer preload.js must expose notifyUnreadDot");
  assertIncludes(preload, "ipcRenderer.invoke(PET_UNREAD_DOT_CHANNEL", "renderer preload.js must invoke unread-dot IPC channel");
}

function testTask204UnreadDotChannelInPetPreload() {
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_UNREAD_DOT_RECEIVED_CHANNEL = "pet:unread-dot-received"', "pet-preload.js must define PET_UNREAD_DOT_RECEIVED_CHANNEL");
  assertIncludes(preload, "onUnreadUpdate", "pet-preload.js must expose onUnreadUpdate");
  assertIncludes(preload, "ipcRenderer.on(PET_UNREAD_DOT_RECEIVED_CHANNEL", "pet-preload.js must listen on unread-dot-received channel");
}

function testTask204UnreadDotHtmlAndCssExist() {
  const html = readText(petHtmlPath);
  const css = readText(path.join(desktopRoot, "src", "pet", "pet.css"));
  assertIncludes(html, 'id="pet-unread-dot"', "pet.html must contain #pet-unread-dot");
  assertIncludes(html, 'class="pet-unread-dot', "pet.html must give pet-unread-dot the CSS class");
  assertRegex(html, /id="pet-unread-dot"[\s\S]*hidden/, "pet.html #pet-unread-dot must start hidden");
  assertIncludes(css, ".pet-unread-dot", "pet.css must define .pet-unread-dot");
  assertIncludes(css, ".pet-unread-dot[hidden]", "pet.css must override [hidden] to display:none");
}

// ── TASK-218: Safe Pet Expression Suggestion Mirror ───────────────────────────

function testTask218ExpressionSuggestionChannelsInMain() {
  const main = readText(mainPath);
  assertIncludes(main, 'PET_EXPRESSION_SUGGESTION_CHANNEL = "pet:expression-suggestion"',
    "main.js must define PET_EXPRESSION_SUGGESTION_CHANNEL");
  assertIncludes(main, 'PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet:expression-suggestion-received"',
    "main.js must define PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL");
  assertNotIncludes(main, 'PET_EXPRESSION_SUGGESTION_CHANNEL = "pet"',
    "main.js must not use generic pet channel for expression suggestion invoke");
  assertNotIncludes(main, 'PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet"',
    "main.js must not use generic pet channel for expression suggestion relay");
  assertIncludes(main, "ipcMain.handle(PET_EXPRESSION_SUGGESTION_CHANNEL",
    "main.js must register ipcMain.handle for expression suggestion");
  assertIncludes(main, "targetPetWindow.webContents.send(PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL",
    "main.js must forward expression suggestion to petWindow");
}

function testTask218ExpressionSuggestionSanitizesInMain() {
  const main = readText(mainPath);
  const sanitizeIdx = main.indexOf("function sanitizeExpressionSuggestionPayload");
  assert(sanitizeIdx >= 0, "main.js must define sanitizeExpressionSuggestionPayload");
  const sanitizeText = main.slice(sanitizeIdx, sanitizeIdx + 600);
  assertIncludes(sanitizeText, "INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN",
    "sanitizeExpressionSuggestionPayload must use expression allowlist");
  assertIncludes(sanitizeText, '"interaction_expression_suggestion"',
    "sanitizeExpressionSuggestionPayload must fix source field");

  const forwardIdx = main.indexOf("function forwardExpressionSuggestion");
  assert(forwardIdx >= 0, "main.js must define forwardExpressionSuggestion");
  const forwardText = main.slice(forwardIdx, forwardIdx + 600);
  assertIncludes(forwardText, "pet_window_unavailable",
    "forwardExpressionSuggestion must guard petWindow availability");
}

function testTask218ExpressionSuggestionBridgeInRendererPreload() {
  const preload = readText(rendererPreloadPath);
  assertIncludes(preload, 'PET_EXPRESSION_SUGGESTION_CHANNEL = "pet:expression-suggestion"',
    "renderer preload.js must define PET_EXPRESSION_SUGGESTION_CHANNEL");
  assertNotIncludes(preload, 'PET_EXPRESSION_SUGGESTION_CHANNEL = "pet"',
    "renderer preload.js must not use generic pet channel for expression suggestion invoke");
  assertIncludes(preload, "sendPetExpressionSuggestion",
    "renderer preload.js must expose sendPetExpressionSuggestion");
  assertIncludes(preload, "ipcRenderer.invoke(PET_EXPRESSION_SUGGESTION_CHANNEL",
    "renderer preload.js must invoke expression suggestion IPC channel");
}

function testTask218ExpressionSuggestionPetPreloadExposesListener() {
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet:expression-suggestion-received"',
    "pet-preload.js must define PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL");
  assertNotIncludes(preload, 'PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet"',
    "pet-preload.js must not use generic pet channel for expression suggestion received listener");
  assertIncludes(preload, "onExpressionSuggestion",
    "pet-preload.js must expose onExpressionSuggestion");
  assertIncludes(preload, "ipcRenderer.on(PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL",
    "pet-preload.js must listen on expression suggestion received channel");
}

function testTask218ExpressionSuggestionPreloadNoGenericIpc() {
  const rendererPreload = readText(rendererPreloadPath);
  const petPreload = readText(petPreloadPath);
  // Preloads must use contextBridge — not return the raw ipcRenderer object to the renderer.
  assertIncludes(rendererPreload, "contextBridge.exposeInMainWorld",
    "renderer preload.js must use contextBridge.exposeInMainWorld");
  assertIncludes(petPreload, "contextBridge.exposeInMainWorld",
    "pet preload.js must use contextBridge.exposeInMainWorld");
  assert(!rendererPreload.includes("module.exports = ipcRenderer") &&
    !rendererPreload.includes("global.ipcRenderer") &&
    !rendererPreload.includes("window.ipcRenderer"),
    "renderer preload.js must not expose raw ipcRenderer to renderer context");
}

function extractFunction(source, name) {
  const start = source.indexOf(`function ${name}`);
  assert(start >= 0, `${name} must exist`);
  const argsEnd = source.indexOf(")", start);
  assert(argsEnd >= 0, `${name} must have a parameter list`);
  const braceStart = source.indexOf("{", argsEnd);
  assert(braceStart >= 0, `${name} must have a body`);
  let depth = 0;
  for (let i = braceStart; i < source.length; i += 1) {
    const char = source[i];
    if (char === "{") depth += 1;
    if (char === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, i + 1);
    }
  }
  throw new Error(`${name} body was not closed`);
}

function runRendererPreloadHarness() {
  const invokeCalls = [];
  let exposedApi = null;
  const sandbox = {
    Date: { now: () => 218001 },
    require(name) {
      assert.equal(name, "electron");
      return {
        contextBridge: {
          exposeInMainWorld(nameArg, api) {
            assert.equal(nameArg, "dragonPet");
            exposedApi = api;
          },
        },
        ipcRenderer: {
          invoke(channel, payload) {
            invokeCalls.push({ channel, payload });
            return Promise.resolve({ ok: true });
          },
          on() {},
          removeListener() {},
        },
      };
    },
  };
  vm.runInNewContext(readText(rendererPreloadPath), sandbox, { filename: rendererPreloadPath });
  return { exposedApi, invokeCalls };
}

function runPetPreloadHarness() {
  const listeners = new Map();
  let exposedApi = null;
  const sandbox = {
    Date: { now: () => 218002 },
    require(name) {
      assert.equal(name, "electron");
      return {
        contextBridge: {
          exposeInMainWorld(nameArg, api) {
            assert.equal(nameArg, "dragonPet");
            exposedApi = api;
          },
        },
        ipcRenderer: {
          on(channel, listener) {
            listeners.set(channel, listener);
          },
          removeListener(channel, listener) {
            if (listeners.get(channel) === listener) listeners.delete(channel);
          },
          invoke() {
            return Promise.resolve({ ok: true });
          },
        },
      };
    },
  };
  vm.runInNewContext(readText(petPreloadPath), sandbox, { filename: petPreloadPath });
  return { exposedApi, listeners };
}

function runMainForwardExpressionHarness() {
  const main = readText(mainPath);
  const sendCalls = [];
  const allowlistMatch = main.match(/const INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN = new Set\(\[[\s\S]*?\]\);/);
  const channelMatch = main.match(/const PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet:expression-suggestion-received";/);
  assert(allowlistMatch, "main.js must define expression allowlist");
  assert(channelMatch, "main.js must define received channel as pet");
  const sandbox = {
    Date: { now: () => 218003 },
    petWindow: {
      isDestroyed: () => false,
      webContents: {
        send(channel, payload) {
          sendCalls.push({ channel, payload });
        },
      },
    },
  };
  vm.runInNewContext([
    allowlistMatch[0],
    channelMatch[0],
    extractFunction(main, "sanitizeExpressionSuggestionPayload"),
    extractFunction(main, "forwardExpressionSuggestion"),
    "globalThis.forwardExpressionSuggestion = forwardExpressionSuggestion;",
  ].join("\n"), sandbox, { filename: "main-expression-harness.js" });
  return { forwardExpressionSuggestion: sandbox.forwardExpressionSuggestion, sendCalls };
}

function testTask218RendererPreloadRuntimeBridgePayload() {
  const { exposedApi, invokeCalls } = runRendererPreloadHarness();
  assert(exposedApi && typeof exposedApi.sendPetExpressionSuggestion === "function",
    "renderer preload must expose dragonPet.sendPetExpressionSuggestion");
  exposedApi.sendPetExpressionSuggestion({ expression: "annoyed", text: "FORBIDDEN" });
  assert.equal(invokeCalls.length, 1, "sendPetExpressionSuggestion must invoke once");
  assert.equal(invokeCalls[0].channel, "pet:expression-suggestion",
    "sendPetExpressionSuggestion must invoke narrow expression suggestion channel");
  assert.deepEqual(Object.keys(invokeCalls[0].payload).sort(), ["expression", "source", "ts"],
    "renderer preload payload must only include expression/source/ts");
  assert.equal(invokeCalls[0].payload.expression, "annoyed");
  assert.equal(invokeCalls[0].payload.source, "interaction_expression_suggestion");
}

function testTask218PetPreloadRuntimeListenerPayload() {
  const { exposedApi, listeners } = runPetPreloadHarness();
  const received = [];
  assert(exposedApi && typeof exposedApi.onExpressionSuggestion === "function",
    "pet preload must expose dragonPet.onExpressionSuggestion");
  exposedApi.onExpressionSuggestion((payload) => received.push(payload));
  const listener = listeners.get("pet:expression-suggestion-received");
  assert.equal(typeof listener, "function",
    "pet preload must listen on narrow expression suggestion received channel");
  listener({}, { expression: "neutral", source: "ignored", ts: 1, text: "FORBIDDEN" });
  listener({}, { expression: "annoyed", ts: 2 });
  listener({}, { expression: "happy", ts: 3 });
  listener({}, { expression: "not_allowed", ts: 4 });
  assert.deepEqual(received.map((payload) => payload.expression), ["neutral", "annoyed", "happy", "neutral"]);
  for (const payload of received) {
    assert.deepEqual(Object.keys(payload).sort(), ["expression", "source", "ts"],
      "pet preload listener payload must only include expression/source/ts");
    assert.equal(payload.source, "interaction_expression_suggestion");
  }
}

function testTask218MainForwardExpressionRuntimeRelay() {
  const { forwardExpressionSuggestion, sendCalls } = runMainForwardExpressionHarness();
  for (const expression of ["neutral", "annoyed", "happy"]) {
    const result = forwardExpressionSuggestion({ expression, ts: 10 });
    assert.equal(result.ok, true, `forwardExpressionSuggestion(${expression}) must succeed`);
  }
  assert.deepEqual(sendCalls.map((call) => call.channel), [
    "pet:expression-suggestion-received",
    "pet:expression-suggestion-received",
    "pet:expression-suggestion-received",
  ], "main relay must send all expression suggestions on narrow received channel");
  assert.deepEqual(sendCalls.map((call) => call.payload.expression), ["neutral", "annoyed", "happy"],
    "main relay must preserve allowlisted expressions");
  for (const call of sendCalls) {
    assert.deepEqual(Object.keys(call.payload).sort(), ["expression", "source", "ts"],
      "main relay payload must only include expression/source/ts");
    assert.equal(call.payload.source, "interaction_expression_suggestion");
  }
}

function testTask218MainForwardExpressionAbsentPetNoThrow() {
  const { forwardExpressionSuggestion } = runMainForwardExpressionHarness();
  const result = forwardExpressionSuggestion({ expression: "happy" }, null);
  assert.equal(result.ok, false,
    "forwardExpressionSuggestion must no-op cleanly when Pet Window is absent");
  assert.equal(result.reason, "pet_window_unavailable",
    "forwardExpressionSuggestion must report pet_window_unavailable when Pet Window is absent");
}

// TASK-218 fix: main relay allows neutral/annoyed
function testTask218FixMainRelayAllowsNeutral() {
  const main = readText(mainPath);
  const allowlistIdx = main.indexOf("INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN");
  assert(allowlistIdx >= 0, "main.js must define INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN");
  const allowlistText = main.slice(allowlistIdx, allowlistIdx + 300);
  assertIncludes(allowlistText, '"neutral"',
    "INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN must include neutral");
}

function testTask218FixMainRelayAllowsAnnoyed() {
  const main = readText(mainPath);
  const allowlistIdx = main.indexOf("INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN");
  assert(allowlistIdx >= 0, "main.js must define INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN");
  const allowlistText = main.slice(allowlistIdx, allowlistIdx + 300);
  assertIncludes(allowlistText, '"annoyed"',
    "INTERACTION_EXPRESSION_SUGGESTION_ALLOWLIST_MAIN must include annoyed");
}

function testTask218FixMainRelayNoVisibilityCheck() {
  const main = readText(mainPath);
  const fnIdx = main.indexOf("function forwardExpressionSuggestion");
  const fnText = main.slice(fnIdx, fnIdx + 600);
  assert(!fnText.includes("isVisible()"),
    "forwardExpressionSuggestion must NOT check petWindow.isVisible() — expression updates bypass visibility");
}

function testTask218FixPresenceStateHasExpressionOverride() {
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "expressionOverride: null",
    "createPetPresenceState must initialise expressionOverride to null");
  assertIncludes(renderer, "expressionOverride = { mood:",
    "handleInteractionExpressionSuggestion must set expressionOverride.mood");
  assertIncludes(renderer, "expressionOverride.gen",
    "restorePetPresence must compare expressionOverride.gen");
}

// ── TASK-220: Safe Pet Reaction Bubble Mirror ────────────────────────────────

function testTask220ReactionBubbleChannelsInMain() {
  const main = readText(mainPath);
  assertIncludes(main, 'PET_REACTION_BUBBLE_CHANNEL = "pet:reaction-bubble"',
    "main.js must define narrow reaction bubble invoke channel");
  assertIncludes(main, 'PET_REACTION_BUBBLE_RECEIVED_CHANNEL = "pet:reaction-bubble-received"',
    "main.js must define narrow reaction bubble received channel");
  assertNotIncludes(main, 'PET_REACTION_BUBBLE_CHANNEL = "pet"',
    "main.js must not use generic pet channel for reaction bubble invoke");
  assertNotIncludes(main, 'PET_REACTION_BUBBLE_RECEIVED_CHANNEL = "pet"',
    "main.js must not use generic pet channel for reaction bubble relay");
  assertIncludes(main, "ipcMain.handle(PET_REACTION_BUBBLE_CHANNEL",
    "main.js must register ipcMain.handle for reaction bubble");
  assertIncludes(main, "targetPetWindow.webContents.send(PET_REACTION_BUBBLE_RECEIVED_CHANNEL",
    "main.js must forward reaction bubble to Pet Window");
}

function testTask220ReactionBubbleSanitizesInMain() {
  const main = readText(mainPath);
  const sanitizeIdx = main.indexOf("function sanitizeReactionBubblePayload");
  assert(sanitizeIdx >= 0, "main.js must define sanitizeReactionBubblePayload");
  const sanitizeText = main.slice(sanitizeIdx, sanitizeIdx + 900);
  assertIncludes(sanitizeText, "REACTION_BUBBLE_ALLOWLIST_MAIN",
    "sanitizeReactionBubblePayload must use allowlist");
  assertIncludes(sanitizeText, "REACTION_BUBBLE_TEXT_BY_ID_MAIN",
    "sanitizeReactionBubblePayload must derive text from fixed mapping");
  assertIncludes(sanitizeText, "REACTION_BUBBLE_SOURCE",
    "sanitizeReactionBubblePayload must fix source via constant");
  const forwardIdx = main.indexOf("function forwardReactionBubble");
  assert(forwardIdx >= 0, "main.js must define forwardReactionBubble");
  const forwardText = main.slice(forwardIdx, forwardIdx + 700);
  assertIncludes(forwardText, "pet_window_unavailable",
    "forwardReactionBubble must guard absent Pet Window");
  assert(!forwardText.includes("isVisible()"),
    "forwardReactionBubble must not use visibility as a relay condition");
}

function testTask220ReactionBubbleBridgeInRendererPreload() {
  const preload = readText(rendererPreloadPath);
  assertIncludes(preload, 'PET_REACTION_BUBBLE_CHANNEL = "pet:reaction-bubble"',
    "renderer preload.js must define PET_REACTION_BUBBLE_CHANNEL");
  assertNotIncludes(preload, 'PET_REACTION_BUBBLE_CHANNEL = "pet"',
    "renderer preload.js must not use generic pet channel for reaction bubble");
  assertIncludes(preload, "sendPetReactionBubble",
    "renderer preload.js must expose sendPetReactionBubble");
  assertIncludes(preload, "ipcRenderer.invoke(PET_REACTION_BUBBLE_CHANNEL",
    "renderer preload.js must invoke narrow reaction bubble channel");
  assertIncludes(preload, "sanitizeReactionBubblePayload",
    "renderer preload.js must sanitize reaction bubble payload");
}

function testTask220ReactionBubblePetPreloadExposesListener() {
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_REACTION_BUBBLE_RECEIVED_CHANNEL = "pet:reaction-bubble-received"',
    "pet-preload.js must define PET_REACTION_BUBBLE_RECEIVED_CHANNEL");
  assertNotIncludes(preload, 'PET_REACTION_BUBBLE_RECEIVED_CHANNEL = "pet"',
    "pet-preload.js must not use generic pet channel for reaction bubble listener");
  assertIncludes(preload, "onReactionBubble",
    "pet-preload.js must expose onReactionBubble");
  assertIncludes(preload, "ipcRenderer.on(PET_REACTION_BUBBLE_RECEIVED_CHANNEL",
    "pet-preload.js must listen on reaction bubble received channel");
}

function runMainForwardReactionBubbleHarness() {
  const main = readText(mainPath);
  const sendCalls = [];
  const textMapMatch = main.match(/const REACTION_BUBBLE_TEXT_BY_ID_MAIN = Object\.freeze\(\{[\s\S]*?\}\);/);
  const allowlistMatch = main.match(/const REACTION_BUBBLE_ALLOWLIST_MAIN = new Set\(Object\.keys\(REACTION_BUBBLE_TEXT_BY_ID_MAIN\)\);/);
  const sourceMatch = main.match(/const REACTION_BUBBLE_SOURCE = "interaction_reaction_bubble";/);
  const ttlMatch = main.match(/const REACTION_BUBBLE_TTL_MS = 3000;/);
  const channelMatch = main.match(/const PET_REACTION_BUBBLE_RECEIVED_CHANNEL = "pet:reaction-bubble-received";/);
  assert(textMapMatch, "main.js must define reaction bubble text map");
  assert(allowlistMatch, "main.js must define reaction bubble allowlist");
  assert(sourceMatch, "main.js must define reaction bubble source");
  assert(ttlMatch, "main.js must define reaction bubble ttl");
  assert(channelMatch, "main.js must define reaction bubble received channel");
  const sandbox = {
    Date: { now: () => 220003 },
    petWindow: {
      isDestroyed: () => false,
      webContents: {
        send(channel, payload) {
          sendCalls.push({ channel, payload });
        },
      },
    },
  };
  vm.runInNewContext([
    textMapMatch[0],
    allowlistMatch[0],
    sourceMatch[0],
    ttlMatch[0],
    channelMatch[0],
    extractFunction(main, "sanitizeReactionBubblePayload"),
    extractFunction(main, "forwardReactionBubble"),
    "globalThis.forwardReactionBubble = forwardReactionBubble;",
  ].join("\n"), sandbox, { filename: "main-reaction-bubble-harness.js" });
  return { forwardReactionBubble: sandbox.forwardReactionBubble, sendCalls };
}

function testTask220RendererPreloadRuntimeBridgePayload() {
  const { exposedApi, invokeCalls } = runRendererPreloadHarness();
  assert(exposedApi && typeof exposedApi.sendPetReactionBubble === "function",
    "renderer preload must expose dragonPet.sendPetReactionBubble");
  exposedApi.sendPetReactionBubble({
    id: "correction",
    text: "RAW_USER_TEXT_FORBIDDEN",
    hint: "FORBIDDEN",
    reply: "FORBIDDEN",
  });
  assert.equal(invokeCalls.length, 1, "sendPetReactionBubble must invoke once");
  assert.equal(invokeCalls[0].channel, "pet:reaction-bubble",
    "sendPetReactionBubble must invoke narrow reaction bubble channel");
  assert.deepEqual(Object.keys(invokeCalls[0].payload).sort(), ["id", "source", "text", "ts", "ttlMs"],
    "renderer preload reaction bubble payload must only include id/text/source/ts/ttlMs");
  assert.equal(invokeCalls[0].payload.id, "correction");
  assert.equal(invokeCalls[0].payload.text, "又改？下次可要想清楚。");
  assert.equal(invokeCalls[0].payload.source, "interaction_reaction_bubble");
  assert.equal(invokeCalls[0].payload.ttlMs, 3000);
  assert.ok(!JSON.stringify(invokeCalls[0].payload).includes("RAW_USER_TEXT_FORBIDDEN"),
    "renderer preload must drop caller-provided text");
}

function testTask220PetPreloadRuntimeListenerPayload() {
  const { exposedApi, listeners } = runPetPreloadHarness();
  const received = [];
  assert(exposedApi && typeof exposedApi.onReactionBubble === "function",
    "pet preload must expose dragonPet.onReactionBubble");
  exposedApi.onReactionBubble((payload) => received.push(payload));
  const listener = listeners.get("pet:reaction-bubble-received");
  assert.equal(typeof listener, "function",
    "pet preload must listen on narrow reaction bubble received channel");
  listener({}, { id: "user_active", text: "RAW_USER_TEXT_FORBIDDEN", ts: 1, reply: "NOPE" });
  listener({}, { id: "reset", ts: 2 });
  listener({}, { id: "not_allowed", ts: 3 });
  assert.deepEqual(received.map((payload) => payload.id), ["user_active", "reset", "none"]);
  assert.equal(received[0].text, "哼，總算肯理吾了。");
  assert.equal(received[1].text, "清空了。重新開始也無妨。");
  assert.equal(received[2].text, "");
  for (const payload of received) {
    assert.deepEqual(Object.keys(payload).sort(), ["id", "source", "text", "ts", "ttlMs"],
      "pet preload listener payload must only include id/text/source/ts/ttlMs");
    assert.equal(payload.source, "interaction_reaction_bubble");
    assert.equal(payload.ttlMs, 3000);
    assert.ok(!JSON.stringify(payload).includes("RAW_USER_TEXT_FORBIDDEN"),
      "pet preload must ignore raw incoming text");
  }
}

function testTask220MainForwardReactionBubbleRuntimeRelay() {
  const { forwardReactionBubble, sendCalls } = runMainForwardReactionBubbleHarness();
  for (const id of ["user_active", "message_management", "attention_returned"]) {
    const result = forwardReactionBubble({ id, text: "RAW_USER_TEXT_FORBIDDEN", ts: 10 });
    assert.equal(result.ok, true, `forwardReactionBubble(${id}) must succeed`);
  }
  assert.deepEqual(sendCalls.map((call) => call.channel), [
    "pet:reaction-bubble-received",
    "pet:reaction-bubble-received",
    "pet:reaction-bubble-received",
  ], "main relay must send reaction bubbles on narrow received channel");
  assert.deepEqual(sendCalls.map((call) => call.payload.id), ["user_active", "message_management", "attention_returned"],
    "main relay must preserve allowlisted ids");
  for (const call of sendCalls) {
    assert.deepEqual(Object.keys(call.payload).sort(), ["id", "source", "text", "ts", "ttlMs"],
      "main relay reaction bubble payload must only include id/text/source/ts/ttlMs");
    assert.equal(call.payload.source, "interaction_reaction_bubble");
    assert.equal(call.payload.ttlMs, 3000);
    assert.ok(!JSON.stringify(call.payload).includes("RAW_USER_TEXT_FORBIDDEN"),
      "main relay must drop caller-provided raw text");
  }
}

function testTask220MainForwardReactionBubbleAbsentPetNoThrow() {
  const { forwardReactionBubble } = runMainForwardReactionBubbleHarness();
  const result = forwardReactionBubble({ id: "user_active" }, null);
  assert.equal(result.ok, false,
    "forwardReactionBubble must no-op cleanly when Pet Window is absent");
  assert.equal(result.reason, "pet_window_unavailable",
    "forwardReactionBubble must report pet_window_unavailable when Pet Window is absent");
}

function testTask220DoesNotTouchExpressionChannels() {
  const main = readText(mainPath);
  const rendererPreload = readText(rendererPreloadPath);
  const petPreload = readText(petPreloadPath);
  assertIncludes(main, 'PET_EXPRESSION_SUGGESTION_CHANNEL = "pet:expression-suggestion"',
    "TASK-220 must preserve expression suggestion invoke channel");
  assertIncludes(main, 'PET_EXPRESSION_SUGGESTION_RECEIVED_CHANNEL = "pet:expression-suggestion-received"',
    "TASK-220 must preserve expression suggestion received channel");
  assertIncludes(rendererPreload, "sendPetExpressionSuggestion",
    "TASK-220 must preserve renderer expression bridge");
  assertIncludes(petPreload, "onExpressionSuggestion",
    "TASK-220 must preserve pet expression listener");
}

function run() {
  const tests = [
    testMainHasPetWindowPrototype,
    testPetWindowOptionsAreSafeAndPetSpecific,
    testPetWindowPositionPersistenceIsLocalAndGuarded,
    testPetWindowPositionRestoreAndFallbackRules,
    testPetWindowResetPersistsSafeDefault,
    testPetWindowHideShowPreservesAndValidatesPosition,
    testPetWindowScalePresetsAndMediumDefault,
    testFullAppWindowStillExists,
    testPetOpenFullAppIpcIsFixedAndNarrow,
    testPetSpeechPayloadSanitizersDropDiagnostics,
    testPetWindowDoesNotReplaceFullAppByDefault,
    testNoRendererDirectOllamaAccess,
    testFullAppShowPetEntryAndPreloadAreNarrow,
    testPetRendererUsesOnlyBackendChatPath,
    testPetPreloadExposesOnlyFixedPetActions,
    // TASK-162
    testQuietModePersistenceIpcAndStorageInMain,
    testQuietModePersistenceSaveMergesExistingState,
    testQuietModePersistenceStartupUrlParam,
    testQuietModePersistencePreloadExposesSetter,
    testQuietModePersistenceRendererCallsPersistOnToggle,
    // TASK-166A
    testPetOverlayShellSkipsTaskbar,
    testPetOverlayShellTransparentBackground,
    // TASK-166B
    testPetScalePresetsConstants,
    testPetScaleLoadFallsBackToMedium,
    testPetScalePersistsMergesExistingState,
    testPetScaleIpcHandlerExists,
    testPetScalePreloadExposesSetter,
    testPetScaleStartupUrlParam,
    testPetScaleResetPositionUsesActiveDims,
    testPetScaleDefaultBoundsAcceptsDimsParam,
    // TASK-166D
    testClickThroughIpcChannelInMain,
    testClickThroughPreloadExposesSetter,
    testClickThroughRendererHasFunctions,
    testClickThroughForwardFlagIsPresent,
    // TASK-166E
    testDirectInputRendererHasFunctions,
    testDirectInputNoNewIpc,
    testDirectInputHtmlElements,
    // TASK-166E click-fix
    testDirectInputClickFixFocusRestoredInMain,
    // TASK-167A
    testVoiceRecordingFunctionsExportedFromRenderer,
    testNoNewIpcChannelsForMic,
    testMicPermissionHandlerInMain,
    // TASK-167B
    testSttIpcBridgeExposedInPreload,
    testSttIpcHandlerInMain,
    testSttHandlerNoPersistenceInMain,
    testSttTranscribeAudioBlobFunctionsInRenderer,
    // TASK-193
    testTask193ChatMirrorChannelInPetPreload,
    testTask193ChatMirrorChannelInMain,
    testTask193ChatMirrorChannelInRendererPreload,
    testTask193MainMirrorHandlerSanitizesPayload,
    // TASK-194
    testTask194ChatHistoryChannelsInMain,
    testTask194ChatHistoryChannelsInRendererPreload,
    // TASK-195
    testTask195InputMethodInMirrorPipeline,
    testTask195VisMenuHiddenInMain,
    // TASK-196
    testTask196ClipboardBridgeInRendererPreload,
    testTask196ClipboardIpcHandlerInMain,
    // TASK-204
    testTask204UnreadDotChannelsInMain,
    testTask204UnreadDotPayloadSanitizedInMain,
    testTask204UnreadDotChannelInRendererPreload,
    testTask204UnreadDotChannelInPetPreload,
    testTask204UnreadDotHtmlAndCssExist,
    // TASK-218
    testTask218ExpressionSuggestionChannelsInMain,
    testTask218ExpressionSuggestionSanitizesInMain,
    testTask218ExpressionSuggestionBridgeInRendererPreload,
    testTask218ExpressionSuggestionPetPreloadExposesListener,
    testTask218ExpressionSuggestionPreloadNoGenericIpc,
    testTask218RendererPreloadRuntimeBridgePayload,
    testTask218PetPreloadRuntimeListenerPayload,
    testTask218MainForwardExpressionRuntimeRelay,
    testTask218MainForwardExpressionAbsentPetNoThrow,
    // TASK-218 fix: main relay allows neutral/annoyed, no visibility guard
    testTask218FixMainRelayAllowsNeutral,
    testTask218FixMainRelayAllowsAnnoyed,
    testTask218FixMainRelayNoVisibilityCheck,
    testTask218FixPresenceStateHasExpressionOverride,
    // TASK-220
    testTask220ReactionBubbleChannelsInMain,
    testTask220ReactionBubbleSanitizesInMain,
    testTask220ReactionBubbleBridgeInRendererPreload,
    testTask220ReactionBubblePetPreloadExposesListener,
    testTask220RendererPreloadRuntimeBridgePayload,
    testTask220PetPreloadRuntimeListenerPayload,
    testTask220MainForwardReactionBubbleRuntimeRelay,
    testTask220MainForwardReactionBubbleAbsentPetNoThrow,
    testTask220DoesNotTouchExpressionChannels,
  ];

  for (const test of tests) {
    test();
    console.log(`[PASS] ${test.name}`);
  }

  console.log(`[PASS] pet window smoke complete (${tests.length} checks)`);
}

run();
