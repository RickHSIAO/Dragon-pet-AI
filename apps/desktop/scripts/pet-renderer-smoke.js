const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const desktopRoot = path.resolve(__dirname, "..");
const petRoot = path.join(desktopRoot, "src", "pet");
const petHtmlPath = path.join(petRoot, "pet.html");
const petCssPath = path.join(petRoot, "pet.css");
const petRendererPath = path.join(petRoot, "pet-renderer.js");

class FakeElement {
  constructor(id) {
    this.id = id;
    this.dataset = {};
    this.textContent = "";
    this.attributes = {};
  }

  getAttribute(name) {
    return this.attributes[name] || "";
  }

  setAttribute(name, value) {
    this.attributes[name] = String(value);
  }
}

class FakeDocument {
  constructor(ids) {
    this.elements = new Map(ids.map((id) => [id, new FakeElement(id)]));
  }

  getElementById(id) {
    return this.elements.get(id) || null;
  }
}

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function assertFileExists(filePath) {
  assert.equal(fs.existsSync(filePath), true, `${filePath} should exist`);
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

function testPetFilesExist() {
  assertFileExists(petHtmlPath);
  assertFileExists(petCssPath);
  assertFileExists(petRendererPath);
}

function testPetHtmlReferencesStaticAssets() {
  const html = readText(petHtmlPath);
  assertIncludes(html, 'href="pet.css"', "pet.html");
  assertIncludes(html, 'src="pet-renderer.js"', "pet.html");
  assertIncludes(html, 'id="pet-avatar-container"', "pet.html");
  assertIncludes(html, 'id="pet-avatar"', "pet.html");
  assertIncludes(html, 'id="pet-hint"', "pet.html");
  assertIncludes(html, 'id="pet-bubble"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-placeholder"', "pet.html");
  assertIncludes(html, 'id="pet-context-menu-hook"', "pet.html");
  assertIncludes(html, 'id="pet-open-full-app-hook"', "pet.html");
  assertRegex(html, /id="pet-drag-region"[^>]*class="[^"]*\bpet-drag-region\b/, "pet.html");
  assertRegex(html, /id="pet-bubble"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-context-menu-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-open-full-app-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertIncludes(html, "&#x54FC;&#xFF0C;", "pet.html");
  assertIncludes(
    html,
    "../renderer/assets/pet/christina/expressions/christina_neutral.png",
    "pet.html"
  );
}

function testPetCssUsesStaticPetDimensions() {
  const css = readText(petCssPath);
  assertIncludes(css, "width: 220px", "pet.css");
  assertIncludes(css, "min-height: 280px", "pet.css");
  assertIncludes(css, "background: transparent", "pet.css");
  assertIncludes(css, "-webkit-app-region: drag", "pet.css");
  assertIncludes(css, "-webkit-app-region: no-drag", "pet.css");
  assertIncludes(css, ".pet-drag-region", "pet.css");
  assertIncludes(css, ".pet-no-drag", "pet.css");
  assertRegex(css, /button,\s*\r?\ninput[\s\S]*-webkit-app-region:\s*no-drag/, "pet.css");
  assertRegex(css, /textarea[\s\S]*-webkit-app-region:\s*no-drag/, "pet.css");
}

function testPetRendererHasNoBackendOrOllamaCalls() {
  const renderer = readText(petRendererPath);
  assertNotIncludes(renderer, "fetch(", "pet-renderer.js");
  assertNotIncludes(renderer, "fetch('/chat'", "pet-renderer.js");
  assertNotIncludes(renderer, 'fetch("/chat"', "pet-renderer.js");
  assertNotIncludes(renderer, "localhost:11434", "pet-renderer.js");
  assertNotIncludes(renderer, "127.0.0.1:11434", "pet-renderer.js");
  assertNotIncludes(renderer, "11434", "pet-renderer.js");
}

function testPetRendererInitializesStaticDom() {
  const { initializePetMode, PET_MODE_DEFAULTS } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-avatar-container",
    "pet-avatar",
    "pet-hint",
    "pet-bubble",
    "pet-bubble-placeholder",
  ]);

  initializePetMode(fakeDocument);

  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.initialized, "true");
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.mode, "pet");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.equal(fakeDocument.getElementById("pet-hint").textContent, PET_MODE_DEFAULTS.hint);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "placeholder");
  assert.equal(fakeDocument.getElementById("pet-bubble").getAttribute("aria-expanded"), "false");
  assert.match(fakeDocument.getElementById("pet-bubble-placeholder").textContent, /TASK-115/);
}

function run() {
  const tests = [
    testPetFilesExist,
    testPetHtmlReferencesStaticAssets,
    testPetCssUsesStaticPetDimensions,
    testPetRendererHasNoBackendOrOllamaCalls,
    testPetRendererInitializesStaticDom,
  ];

  for (const test of tests) {
    test();
    console.log(`[PASS] ${test.name}`);
  }

  console.log(`[PASS] pet renderer smoke complete (${tests.length} checks)`);
}

run();
