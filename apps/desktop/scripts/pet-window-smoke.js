const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const desktopRoot = path.resolve(__dirname, "..");
const mainPath = path.join(desktopRoot, "src", "main.js");
const rendererPath = path.join(desktopRoot, "src", "renderer", "renderer.js");
const petRendererPath = path.join(desktopRoot, "src", "pet", "pet-renderer.js");

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
  assertIncludes(main, "function createPetWindow()", "main.js");
  assertIncludes(main, "PET_MODE_ENABLED", "main.js");
  assertIncludes(main, 'process.env.PET_MODE_ENABLED === "true"', "main.js");
  assertIncludes(main, 'path.join(__dirname, "pet", "pet.html")', "main.js");
}

function testPetWindowOptionsAreSafeAndPetSpecific() {
  const main = readText(mainPath);
  assertRegex(main, /width:\s*220/, "main.js");
  assertRegex(main, /height:\s*280/, "main.js");
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

function testFullAppWindowStillExists() {
  const main = readText(mainPath);
  assertIncludes(main, "function createWindow()", "main.js");
  assertIncludes(main, 'path.join(__dirname, "renderer", "index.html")', "main.js");
  assertIncludes(main, "BACKEND_URL", "main.js");
  assertIncludes(main, "createWindow();", "main.js");
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
  ]) {
    const text = readText(filePath);
    assertNotIncludes(text, "localhost:11434", label);
    assertNotIncludes(text, "127.0.0.1:11434", label);
  }
}

function testPetRendererDoesNotCallChat() {
  const text = readText(petRendererPath);
  assertNotIncludes(text, "fetch(", "pet-renderer.js");
  assertNotIncludes(text, "fetch('/chat'", "pet-renderer.js");
  assertNotIncludes(text, 'fetch("/chat"', "pet-renderer.js");
}

function run() {
  const tests = [
    testMainHasPetWindowPrototype,
    testPetWindowOptionsAreSafeAndPetSpecific,
    testFullAppWindowStillExists,
    testPetWindowDoesNotReplaceFullAppByDefault,
    testNoRendererDirectOllamaAccess,
    testPetRendererDoesNotCallChat,
  ];

  for (const test of tests) {
    test();
    console.log(`[PASS] ${test.name}`);
  }

  console.log(`[PASS] pet window smoke complete (${tests.length} checks)`);
}

run();
