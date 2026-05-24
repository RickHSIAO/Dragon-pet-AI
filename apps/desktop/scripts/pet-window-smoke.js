const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const desktopRoot = path.resolve(__dirname, "..");
const mainPath = path.join(desktopRoot, "src", "main.js");
const rendererPath = path.join(desktopRoot, "src", "renderer", "renderer.js");
const petRendererPath = path.join(desktopRoot, "src", "pet", "pet-renderer.js");
const petPreloadPath = path.join(desktopRoot, "src", "pet", "pet-preload.js");

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
}

function testPetWindowOptionsAreSafeAndPetSpecific() {
  const main = readText(mainPath);
  assertIncludes(main, "PET_WINDOW_WIDTH = 220", "main.js");
  assertIncludes(main, "PET_WINDOW_HEIGHT = 280", "main.js");
  assertRegex(main, /width:\s*PET_WINDOW_WIDTH/, "main.js");
  assertRegex(main, /height:\s*PET_WINDOW_HEIGHT/, "main.js");
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
  assertIncludes(main, "function getDefaultPetWindowBounds()", "main.js");
  assertIncludes(main, "function isPetWindowBoundsVisible(bounds)", "main.js");
  assertIncludes(main, "function loadPetWindowBounds()", "main.js");
  assertIncludes(main, "function savePetWindowBounds(win = petWindow)", "main.js");
  assertIncludes(main, "function schedulePetWindowBoundsSave()", "main.js");
  assertIncludes(main, "screen.getAllDisplays()", "main.js");
  assertIncludes(main, "screen.getPrimaryDisplay().workArea", "main.js");
  assertIncludes(main, "const centerX = normalizedBounds.x + normalizedBounds.width / 2", "main.js");
  assertIncludes(main, "const centerY = normalizedBounds.y + normalizedBounds.height / 2", "main.js");
  assertIncludes(main, "fs.readFileSync(getPetWindowStatePath()", "main.js");
  assertIncludes(main, "fs.writeFileSync(getPetWindowStatePath()", "main.js");
  assertIncludes(main, "const petBounds = loadPetWindowBounds();", "main.js");
  assertRegex(main, /x:\s*petBounds\.x/, "main.js");
  assertRegex(main, /y:\s*petBounds\.y/, "main.js");
  assertIncludes(main, 'petWindow.on("move"', "main.js");
  assertIncludes(main, 'petWindow.on("close"', "main.js");
  assertIncludes(main, "schedulePetWindowBoundsSave();", "main.js");
  assertIncludes(main, "savePetWindowBounds();", "main.js");
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
  assertIncludes(main, "ipcMain.handle(PET_OPEN_FULL_APP_CHANNEL, () =>", "main.js");
  assertIncludes(main, "showFullAppWindow();", "main.js");
  assertIncludes(main, "win.restore();", "main.js");
  assertIncludes(main, "win.show();", "main.js");
  assertIncludes(main, "win.focus();", "main.js");
  assertNotIncludes(main, "ipcMain.on(", "main.js");
}

function testPetWindowDoesNotReplaceFullAppByDefault() {
  const main = readText(mainPath);
  assertIncludes(main, "if (PET_MODE_ENABLED)", "main.js");
  assertNotIncludes(main, "const PET_MODE_ENABLED = true", "main.js");
}

function testNoRendererDirectOllamaAccess() {
  for (const [label, filePath] of [
    ["renderer.js", rendererPath],
    ["pet-renderer.js", petRendererPath],
    ["pet-preload.js", petPreloadPath],
  ]) {
    const text = readText(filePath);
    assertNotIncludes(text, "localhost:11434", label);
    assertNotIncludes(text, "127.0.0.1:11434", label);
    assertNotIncludes(text, "11434", label);
  }
}

function testPetRendererDoesNotCallChat() {
  const text = readText(petRendererPath);
  assertNotIncludes(text, "fetch(", "pet-renderer.js");
  assertNotIncludes(text, "fetch('/chat'", "pet-renderer.js");
  assertNotIncludes(text, 'fetch("/chat"', "pet-renderer.js");
}

function testPetPreloadExposesOnlyOpenFullApp() {
  const preload = readText(petPreloadPath);
  assertIncludes(preload, 'PET_OPEN_FULL_APP_CHANNEL = "pet:open-full-app"', "pet-preload.js");
  assertIncludes(preload, 'contextBridge.exposeInMainWorld(', "pet-preload.js");
  assertIncludes(preload, '"dragonPet"', "pet-preload.js");
  assertIncludes(preload, "openFullApp: () => ipcRenderer.invoke(PET_OPEN_FULL_APP_CHANNEL)", "pet-preload.js");
  assertNotIncludes(preload, "exposeInMainWorld(\"ipcRenderer\"", "pet-preload.js");
  assertNotIncludes(preload, "send(", "pet-preload.js");
  assertNotIncludes(preload, "sendSync", "pet-preload.js");
  assertNotIncludes(preload, 'require("fs")', "pet-preload.js");
  assertNotIncludes(preload, 'require("node:fs")', "pet-preload.js");
  assertNotIncludes(preload, "shell", "pet-preload.js");
  assertNotIncludes(preload, "process", "pet-preload.js");
}

function run() {
  const tests = [
    testMainHasPetWindowPrototype,
    testPetWindowOptionsAreSafeAndPetSpecific,
    testPetWindowPositionPersistenceIsLocalAndGuarded,
    testFullAppWindowStillExists,
    testPetOpenFullAppIpcIsFixedAndNarrow,
    testPetWindowDoesNotReplaceFullAppByDefault,
    testNoRendererDirectOllamaAccess,
    testPetRendererDoesNotCallChat,
    testPetPreloadExposesOnlyOpenFullApp,
  ];

  for (const test of tests) {
    test();
    console.log(`[PASS] ${test.name}`);
  }

  console.log(`[PASS] pet window smoke complete (${tests.length} checks)`);
}

run();
