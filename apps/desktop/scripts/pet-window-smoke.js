const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

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
  assertNotIncludes(main, "ipcMain.on(", "main.js");
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
  ];

  for (const test of tests) {
    test();
    console.log(`[PASS] ${test.name}`);
  }

  console.log(`[PASS] pet window smoke complete (${tests.length} checks)`);
}

run();
