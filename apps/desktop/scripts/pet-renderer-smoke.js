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
    this.hidden = false;
    this.listeners = {};
  }

  getAttribute(name) {
    return this.attributes[name] || "";
  }

  setAttribute(name, value) {
    this.attributes[name] = String(value);
  }

  addEventListener(type, listener) {
    if (!this.listeners[type]) this.listeners[type] = [];
    this.listeners[type].push(listener);
  }

  dispatchEvent(event) {
    const listeners = this.listeners[event.type] || [];
    for (const listener of listeners) {
      listener(event);
    }
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
  assertIncludes(html, 'data-state="collapsed"', "pet.html");
  assertIncludes(html, 'hidden', "pet.html");
  assertIncludes(html, 'id="pet-bubble-message"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-open-hook"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-close-hook"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-placeholder"', "pet.html");
  assertIncludes(html, 'id="pet-context-menu-hook"', "pet.html");
  assertIncludes(html, 'id="pet-open-full-app-hook"', "pet.html");
  assertRegex(html, /id="pet-open-full-app-hook"(?:(?!>).)*data-hook="open-full-app"/, "pet.html");
  assert.equal(/id="pet-open-full-app-hook"(?:(?!>).)*disabled/.test(html), false);
  assertRegex(html, /id="pet-drag-region"[^>]*class="[^"]*\bpet-drag-region\b/, "pet.html");
  assertRegex(html, /id="pet-bubble"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-input-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-send-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-open-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-close-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-context-menu-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-open-full-app-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertIncludes(html, "&#x54FC;&#xFF0C;", "pet.html");
  assertIncludes(
    html,
    "../renderer/assets/pet/christina/expressions/christina_neutral.png",
    "pet.html"
  );
  assertNotIncludes(html, "https://", "pet.html");
  assertNotIncludes(html, "http://", "pet.html");
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
  assertIncludes(css, '[data-bubble-state="expanded"]', "pet.css");
  assertIncludes(css, '.pet-bubble[data-state="expanded"]', "pet.css");
  assertIncludes(css, ".pet-bubble-message", "pet.css");
  assertIncludes(css, "grid-template-columns: 1fr auto", "pet.css");
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

function testPetRendererInitializesBubbleCollapsed() {
  const { initializePetMode, PET_MODE_DEFAULTS } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-drag-region",
    "pet-avatar-container",
    "pet-avatar",
    "pet-hint",
    "pet-bubble",
    "pet-bubble-open-hook",
    "pet-bubble-close-hook",
    "pet-bubble-message",
    "pet-bubble-placeholder",
    "pet-chat-form-hook",
  ]);

  initializePetMode(fakeDocument);

  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.initialized, "true");
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.mode, "pet");
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.bubbleState, "collapsed");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.equal(fakeDocument.getElementById("pet-hint").textContent, PET_MODE_DEFAULTS.hint);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "collapsed");
  assert.equal(fakeDocument.getElementById("pet-bubble").getAttribute("aria-expanded"), "false");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, PET_MODE_DEFAULTS.bubbleMessage);
  assert.match(fakeDocument.getElementById("pet-bubble-placeholder").textContent, /TASK-118/);
}

function testPetRendererTogglesBubbleState() {
  const { collapseBubble, expandBubble, toggleBubble } = require(petRendererPath);
  const fakeDocument = new FakeDocument(["pet-mode-root", "pet-bubble"]);

  expandBubble(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.bubbleState, "expanded");
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "expanded");
  assert.equal(fakeDocument.getElementById("pet-bubble").getAttribute("aria-expanded"), "true");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);

  toggleBubble(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "collapsed");

  toggleBubble(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "expanded");

  collapseBubble(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "collapsed");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, true);
}

function testPetRendererClickAndSubmitHandlersAreLocalOnly() {
  const { initializePetMode, PET_MODE_DEFAULTS } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-drag-region",
    "pet-avatar-container",
    "pet-avatar",
    "pet-hint",
    "pet-bubble",
    "pet-bubble-open-hook",
    "pet-bubble-close-hook",
    "pet-bubble-message",
    "pet-bubble-placeholder",
    "pet-chat-form-hook",
    "pet-open-full-app-hook",
  ]);

  initializePetMode(fakeDocument);
  fakeDocument.getElementById("pet-drag-region").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "expanded");

  fakeDocument.getElementById("pet-bubble-close-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "collapsed");

  fakeDocument.getElementById("pet-bubble-open-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "expanded");

  let prevented = false;
  fakeDocument.getElementById("pet-chat-form-hook").dispatchEvent({
    type: "submit",
    preventDefault() {
      prevented = true;
    },
  });
  assert.equal(prevented, true);
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, PET_MODE_DEFAULTS.bubbleMessage);
}

function testPetRendererOpenFullAppUsesNarrowApi() {
  const { handleOpenFullApp } = require(petRendererPath);
  const fakeDocument = new FakeDocument(["pet-bubble-message"]);
  let called = false;

  const result = handleOpenFullApp(fakeDocument, {
    openFullApp() {
      called = true;
      return Promise.resolve({ ok: true });
    },
  });

  assert.equal(called, true);
  assert.equal(typeof result.then, "function");
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, "Opening Full App...");
}

function testPetRendererOpenFullAppFallbackDoesNotCrash() {
  const { handleOpenFullApp, initializePetMode } = require(petRendererPath);
  const directDocument = new FakeDocument(["pet-bubble-message"]);

  assert.equal(handleOpenFullApp(directDocument, {}), null);
  assert.equal(
    directDocument.getElementById("pet-bubble-message").textContent,
    "Full App switch is not available in this preview."
  );

  const clickDocument = new FakeDocument([
    "pet-mode-root",
    "pet-drag-region",
    "pet-avatar-container",
    "pet-avatar",
    "pet-hint",
    "pet-bubble",
    "pet-bubble-open-hook",
    "pet-bubble-close-hook",
    "pet-bubble-message",
    "pet-bubble-placeholder",
    "pet-chat-form-hook",
    "pet-open-full-app-hook",
  ]);

  initializePetMode(clickDocument);
  clickDocument.getElementById("pet-open-full-app-hook").dispatchEvent({ type: "click" });
  assert.equal(
    clickDocument.getElementById("pet-bubble-message").textContent,
    "Full App switch is not available in this preview."
  );
}

function run() {
  const tests = [
    testPetFilesExist,
    testPetHtmlReferencesStaticAssets,
    testPetCssUsesStaticPetDimensions,
    testPetRendererHasNoBackendOrOllamaCalls,
    testPetRendererInitializesBubbleCollapsed,
    testPetRendererTogglesBubbleState,
    testPetRendererClickAndSubmitHandlersAreLocalOnly,
    testPetRendererOpenFullAppUsesNarrowApi,
    testPetRendererOpenFullAppFallbackDoesNotCrash,
  ];

  for (const test of tests) {
    test();
    console.log(`[PASS] ${test.name}`);
  }

  console.log(`[PASS] pet renderer smoke complete (${tests.length} checks)`);
}

run();
