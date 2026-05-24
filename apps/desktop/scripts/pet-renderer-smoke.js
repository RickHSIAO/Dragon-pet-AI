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
    this.disabled = false;
    this.value = "";
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
    this.listeners = {};
  }

  getElementById(id) {
    return this.elements.get(id) || null;
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
  assertIncludes(html, 'id="pet-drag-handle"', "pet.html");
  assertIncludes(html, 'id="pet-avatar-container"', "pet.html");
  assertIncludes(html, 'id="pet-avatar"', "pet.html");
  assertIncludes(html, 'id="pet-hint"', "pet.html");
  assertIncludes(html, 'id="pet-bubble"', "pet.html");
  assertIncludes(html, 'data-state="collapsed"', "pet.html");
  assertIncludes(html, 'hidden', "pet.html");
  assertIncludes(html, 'id="pet-bubble-message"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-status"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-response"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-open-hook"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-close-hook"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-placeholder"', "pet.html");
  assertIncludes(html, 'id="pet-context-menu-hook"', "pet.html");
  assertIncludes(html, 'id="pet-open-full-app-hook"', "pet.html");
  assertIncludes(html, 'id="pet-menu"', "pet.html");
  assertIncludes(html, 'data-menu-state="closed"', "pet.html");
  assertIncludes(
    html,
    'data-supported-bubble-states="collapsed expanded composing empty_input pending success backend_offline timeout llm_local_error fallback_mock long_reply"',
    "pet.html"
  );
  assertIncludes(html, 'id="pet-menu-open-full-app"', "pet.html");
  assertIncludes(html, 'id="pet-menu-reset-position"', "pet.html");
  assertIncludes(html, 'id="pet-menu-hide-window"', "pet.html");
  assertIncludes(html, 'id="pet-menu-close"', "pet.html");
  assertRegex(html, /id="pet-open-full-app-hook"(?:(?!>).)*data-hook="open-full-app"/, "pet.html");
  assert.equal(/id="pet-open-full-app-hook"(?:(?!>).)*disabled/.test(html), false);
  assert.equal(/id="pet-context-menu-hook"(?:(?!>).)*disabled/.test(html), false);
  assertRegex(html, /id="pet-drag-handle"[^>]*class="[^"]*\bpet-drag-handle\b/, "pet.html");
  assert.equal(/id="pet-drag-handle"[^>]*class="[^"]*\bpet-no-drag\b/.test(html), false);
  assertRegex(html, /id="pet-drag-region"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assert.equal(/id="pet-drag-region"[^>]*class="[^"]*\bpet-drag-region\b/.test(html), false);
  assertRegex(html, /id="pet-avatar-container"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-avatar"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-status"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-response"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-placeholder"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-input-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-send-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-open-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-close-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-context-menu-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-open-full-app-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu-open-full-app"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu-reset-position"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu-hide-window"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu-close"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertIncludes(html, "&#x54FC;&#xFF0C;", "pet.html");
  assertNotIncludes(html, 'id="pet-menu-hotspot"', "pet.html");
  assertNotIncludes(html, 'data-hook="menu-hotspot"', "pet.html");
  assertIncludes(
    html,
    "../renderer/assets/pet/christina/expressions/christina_neutral.png",
    "pet.html"
  );
  assertIncludes(html, "connect-src 'self' http://localhost:8000 http://127.0.0.1:8000", "pet.html");
  assertNotIncludes(html, "https://", "pet.html");
  assertNotIncludes(html, "localhost:11434", "pet.html");
  assertNotIncludes(html, "127.0.0.1:11434", "pet.html");
}

function testPetCssUsesStaticPetDimensions() {
  const css = readText(petCssPath);
  assertIncludes(css, "width: 220px", "pet.css");
  assertIncludes(css, "min-height: 280px", "pet.css");
  assertIncludes(css, "background: transparent", "pet.css");
  assertIncludes(css, "-webkit-app-region: drag", "pet.css");
  assertIncludes(css, "-webkit-app-region: no-drag", "pet.css");
  assertIncludes(css, ".pet-drag-handle", "pet.css");
  assertIncludes(css, ".pet-drag-region", "pet.css");
  assertIncludes(css, ".pet-no-drag", "pet.css");
  assertIncludes(css, '[data-bubble-state="expanded"]', "pet.css");
  assertIncludes(css, '.pet-bubble[data-state="expanded"]', "pet.css");
  assertIncludes(css, ".pet-bubble-message", "pet.css");
  assertIncludes(css, ".pet-bubble-status", "pet.css");
  assertIncludes(css, ".pet-bubble-response", "pet.css");
  assertIncludes(css, ".pet-menu", "pet.css");
  assertIncludes(css, '.pet-menu[hidden]', "pet.css");
  assertIncludes(css, ".pet-menu-item", "pet.css");
  assertIncludes(css, "position: relative", "pet.css");
  assertIncludes(css, "grid-template-columns: 1fr auto", "pet.css");
  assertNotIncludes(css, ".pet-menu-hotspot", "pet.css");
  assert.equal((css.match(/-webkit-app-region:\s*drag\b/g) || []).length, 1);
  assertRegex(css, /\.pet-drag-handle[\s\S]*-webkit-app-region:\s*drag\b/, "pet.css");
  assertRegex(css, /\.pet-drag-handle[\s\S]*height:\s*24px/, "pet.css");
  assertRegex(css, /\.pet-drag-handle[\s\S]*width:\s*156px/, "pet.css");
  assertRegex(css, /\.pet-drag-handle[\s\S]*z-index:\s*8/, "pet.css");
  assertRegex(css, /\.pet-drag-handle[\s\S]*pointer-events:\s*auto/, "pet.css");
  assertRegex(css, /\.pet-drag-handle::before/, "pet.css");
  assertRegex(css, /\.pet-shell[\s\S]*height:\s*280px/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*max-height:\s*30px/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*overflow-y:\s*auto/, "pet.css");
  assertRegex(css, /\.pet-bubble\[data-state="long_reply"\] \.pet-bubble-response[\s\S]*max-height:\s*36px/, "pet.css");
  assertRegex(css, /\.pet-stage,\s*\r?\n\.pet-drag-region[\s\S]*-webkit-app-region:\s*no-drag\b/, "pet.css");
  assertRegex(css, /\.pet-avatar[\s\S]*-webkit-app-region:\s*no-drag\b/, "pet.css");
  assertRegex(css, /button,\s*\r?\ninput[\s\S]*-webkit-app-region:\s*no-drag/, "pet.css");
  assertRegex(css, /textarea[\s\S]*-webkit-app-region:\s*no-drag/, "pet.css");
}

function testPetRendererUsesBackendChatWithoutDirectOllama() {
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "sendPetChatMessage", "pet-renderer.js");
  assertIncludes(renderer, "buildChatPayload", "pet-renderer.js");
  assertIncludes(renderer, 'use_memory: false', "pet-renderer.js");
  assertIncludes(renderer, 'reply: data && typeof data.reply === "string"', "pet-renderer.js");
  assertIncludes(renderer, 'mood: data && typeof data.mood === "string"', "pet-renderer.js");
  assertIncludes(renderer, 'source: data && typeof data.source === "string"', "pet-renderer.js");
  assertIncludes(renderer, '`${backendUrl}/chat`', "pet-renderer.js");
  assertNotIncludes(renderer, "fetch('/chat'", "pet-renderer.js");
  assertNotIncludes(renderer, 'fetch("/chat"', "pet-renderer.js");
  assertNotIncludes(renderer, "localhost:11434", "pet-renderer.js");
  assertNotIncludes(renderer, "127.0.0.1:11434", "pet-renderer.js");
  assertNotIncludes(renderer, "11434", "pet-renderer.js");
}

function testPetRendererDefinesBubbleStates() {
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "const BUBBLE_STATES = Object.freeze", "pet-renderer.js");
  assertIncludes(renderer, "function setBubbleState", "pet-renderer.js");

  for (const state of [
    "collapsed",
    "expanded",
    "composing",
    "empty_input",
    "pending",
    "success",
    "backend_offline",
    "timeout",
    "llm_local_error",
    "fallback_mock",
    "long_reply",
  ]) {
    assertIncludes(renderer, `${state}:`, "pet-renderer.js");
  }

  assertIncludes(renderer, "\\u543e\\u6b63\\u5728\\u60f3\\uff0c\\u5225\\u50ac\\u3002", "pet-renderer.js");
  assertIncludes(
    renderer,
    "\\u5f8c\\u7aef\\u4f3c\\u4e4e\\u4e0d\\u5728\\uff0c\\u6c5d\\u5148\\u53bb\\u628a\\u5b83\\u53eb\\u9192\\u3002",
    "pet-renderer.js"
  );
  assertIncludes(
    renderer,
    "\\u672c\\u5730\\u6a21\\u578b\\u53ef\\u80fd\\u9084\\u5728\\u9192\\u4f86\\u3002",
    "pet-renderer.js"
  );
  assertIncludes(
    renderer,
    "\\u543e\\u7684\\u9b54\\u529b\\u66ab\\u6642\\u5361\\u4f4f\\u4e86\\u3002",
    "pet-renderer.js"
  );
  assertIncludes(
    renderer,
    "\\u9019\\u662f\\u66ab\\u6642\\u56de\\u61c9\\uff0c\\u5225\\u592a\\u5f97\\u610f\\u3002",
    "pet-renderer.js"
  );
  assertIncludes(
    renderer,
    "\\u56de\\u8986\\u592a\\u9577\\uff0c\\u4e4b\\u5f8c\\u53ef\\u5230 Full App \\u67e5\\u770b\\u5b8c\\u6574\\u5167\\u5bb9\\u3002",
    "pet-renderer.js"
  );
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
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
    "pet-chat-form-hook",
    "pet-menu",
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
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.menuState, "closed");
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");
  assert.equal(fakeDocument.getElementById("pet-menu").getAttribute("aria-hidden"), "true");
  assert.equal(fakeDocument.getElementById("pet-menu").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, PET_MODE_DEFAULTS.bubbleMessage);
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local placeholder");
  assert.match(fakeDocument.getElementById("pet-bubble-placeholder").textContent, /TASK-133/);
}

function testPetRendererRendersAllLocalBubbleStates() {
  const { BUBBLE_STATES, setBubbleState } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-bubble",
    "pet-bubble-title",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
  ]);

  for (const [state, config] of Object.entries(BUBBLE_STATES)) {
    const renderedState = setBubbleState(fakeDocument, state);
    assert.equal(renderedState, state);
    assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.bubbleState, state);
    assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, state);
    assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, config.statusText);
    assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, config.message);
    assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, config.response);
    assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, config.inputDisabled);
    assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, config.sendDisabled);
    assert.equal(fakeDocument.getElementById("pet-bubble").hidden, !config.expanded);
  }
}

function testPetRendererTogglesMenuState() {
  const { closeMenu, openMenu, setMenuState, toggleMenu } = require(petRendererPath);
  const fakeDocument = new FakeDocument(["pet-mode-root", "pet-menu"]);

  openMenu(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.menuState, "open");
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");
  assert.equal(fakeDocument.getElementById("pet-menu").getAttribute("aria-hidden"), "false");
  assert.equal(fakeDocument.getElementById("pet-menu").hidden, false);

  closeMenu(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");
  assert.equal(fakeDocument.getElementById("pet-menu").hidden, true);

  setMenuState(fakeDocument, true);
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  toggleMenu(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");

  toggleMenu(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");
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
  const { initializePetMode } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-drag-region",
    "pet-avatar-container",
    "pet-avatar",
    "pet-hint",
    "pet-bubble",
    "pet-bubble-open-hook",
    "pet-bubble-close-hook",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
    "pet-chat-form-hook",
    "pet-open-full-app-hook",
    "pet-context-menu-hook",
    "pet-menu",
    "pet-menu-open-full-app",
    "pet-menu-reset-position",
    "pet-menu-hide-window",
    "pet-menu-close",
  ]);

  initializePetMode(fakeDocument);
  fakeDocument.getElementById("pet-drag-region").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "expanded");

  fakeDocument.getElementById("pet-bubble-close-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "collapsed");

  fakeDocument.getElementById("pet-bubble-open-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "expanded");

  const input = fakeDocument.getElementById("pet-chat-input-hook");
  input.value = "hello";
  input.dispatchEvent({ type: "input", target: input });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "composing");

  let prevented = false;
  input.value = "";
  fakeDocument.getElementById("pet-chat-form-hook").dispatchEvent({
    type: "submit",
    preventDefault() {
      prevented = true;
    },
  });
  assert.equal(prevented, true);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "empty_input");
}

function createPetChatDocument() {
  return new FakeDocument([
    "pet-mode-root",
    "pet-avatar-container",
    "pet-avatar",
    "pet-bubble",
    "pet-bubble-title",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
  ]);
}

async function testPetChatEmptyInputDoesNotFetch() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  const input = fakeDocument.getElementById("pet-chat-input-hook");
  let fetchCalled = false;

  input.value = "   ";
  const result = await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      fetchImpl() {
        fetchCalled = true;
      },
    }
  );

  assert.equal(result, null);
  assert.equal(fetchCalled, false);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "empty_input");
}

async function testPetChatSubmitUsesBackendChatAndRendersSuccess() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  const input = fakeDocument.getElementById("pet-chat-input-hook");
  let capturedUrl = "";
  let capturedOptions = null;
  let resolveFetch;

  input.value = "hello";
  const pendingFetch = new Promise((resolve) => {
    resolveFetch = resolve;
  });

  const submitPromise = handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl(url, options) {
        capturedUrl = url;
        capturedOptions = options;
        return pendingFetch;
      },
    }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "pending");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, true);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, true);

  resolveFetch({
    ok: true,
    json: async () => ({
      reply: "Pet reply",
      mood: "happy",
      source: "llm_local",
    }),
  });

  const result = await submitPromise;
  assert.deepEqual(result, { reply: "Pet reply", mood: "happy", source: "llm_local" });
  assert.equal(capturedUrl, "http://localhost:8000/chat");
  assert.deepEqual(JSON.parse(capturedOptions.body), { message: "hello", use_memory: false });
  assert.equal(capturedOptions.method, "POST");
  assert.equal(capturedOptions.headers["Content-Type"], "application/json");
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "success");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Pet reply");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "happy");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_happy\.png$/);
  assert.equal(input.value, "");
}

async function testPetChatSourceMockUsesFallbackState() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "mock please";

  await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => ({
        ok: true,
        json: async () => ({
          reply: "Mock reply",
          mood: "proud",
          source: "mock",
        }),
      }),
    }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "fallback_mock");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "mock fallback");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Mock reply");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "proud");
}

async function testPetChatSourceLocalErrorUsesErrorState() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "error please";

  await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => ({
        ok: true,
        json: async () => ({
          reply: "Safe fallback reply",
          mood: "worried",
          source: "llm_local_error",
        }),
      }),
    }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "llm_local_error");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local model error");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Safe fallback reply");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
}

async function testPetChatNetworkFailureUsesBackendOfflineState() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "network please";

  const result = await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => {
        throw new TypeError("Failed to fetch");
      },
    }
  );

  assert.equal(result, null);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "backend_offline");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "backend offline");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
}

async function testPetChatLongReplyUsesLongReplyState() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  const longReply = "Long reply. ".repeat(30);
  fakeDocument.getElementById("pet-chat-input-hook").value = "long please";

  await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => ({
        ok: true,
        json: async () => ({
          reply: longReply,
          mood: "focused",
          source: "llm_local",
        }),
      }),
    }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "long_reply");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, longReply);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "focused");
}

function testPetRendererMenuHooksAreLocalAndNarrow() {
  const { initializePetMode } = require(petRendererPath);
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
    "pet-context-menu-hook",
    "pet-menu",
    "pet-menu-open-full-app",
    "pet-menu-reset-position",
    "pet-menu-hide-window",
    "pet-menu-close",
  ]);

  initializePetMode(fakeDocument);

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.getElementById("pet-menu-close").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");

  let contextPrevented = false;
  fakeDocument.getElementById("pet-mode-root").dispatchEvent({
    type: "contextmenu",
    preventDefault() {
      contextPrevented = true;
    },
  });
  assert.equal(contextPrevented, true);
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.getElementById("pet-mode-root").dispatchEvent({
    type: "contextmenu",
    preventDefault() {},
  });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.dispatchEvent({ type: "keydown", key: "Escape" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.getElementById("pet-menu-close").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");
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

function testPetRendererMenuActionsUseNarrowApis() {
  const { handleHidePetWindow, handleResetPetPosition } = require(petRendererPath);
  const fakeDocument = new FakeDocument(["pet-bubble-message"]);
  const originalWindow = global.window;
  const calls = [];

  global.window = {
    dragonPet: {
      resetPetPosition() {
        calls.push("reset");
        return Promise.resolve({ ok: true });
      },
      hidePetWindow() {
        calls.push("hide");
        return Promise.resolve({ ok: true });
      },
    },
  };

  const resetResult = handleResetPetPosition(fakeDocument);
  const hideResult = handleHidePetWindow(fakeDocument);

  global.window = originalWindow;

  assert.deepEqual(calls, ["reset", "hide"]);
  assert.equal(typeof resetResult.then, "function");
  assert.equal(typeof hideResult.then, "function");
}

function testPetRendererMenuActionFallbacksDoNotCrash() {
  const { handleHidePetWindow, handleResetPetPosition } = require(petRendererPath);
  const fakeDocument = new FakeDocument(["pet-bubble-message"]);
  const originalWindow = global.window;

  global.window = {};
  assert.equal(handleResetPetPosition(fakeDocument), null);
  assert.equal(
    fakeDocument.getElementById("pet-bubble-message").textContent,
    "Reset Pet Position is not available in this preview."
  );

  assert.equal(handleHidePetWindow(fakeDocument), null);
  assert.equal(
    fakeDocument.getElementById("pet-bubble-message").textContent,
    "Hide Pet Window is not available in this preview."
  );
  global.window = originalWindow;
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

async function run() {
  const tests = [
    testPetFilesExist,
    testPetHtmlReferencesStaticAssets,
    testPetCssUsesStaticPetDimensions,
    testPetRendererUsesBackendChatWithoutDirectOllama,
    testPetRendererDefinesBubbleStates,
    testPetRendererInitializesBubbleCollapsed,
    testPetRendererRendersAllLocalBubbleStates,
    testPetRendererTogglesBubbleState,
    testPetRendererTogglesMenuState,
    testPetRendererClickAndSubmitHandlersAreLocalOnly,
    testPetChatEmptyInputDoesNotFetch,
    testPetChatSubmitUsesBackendChatAndRendersSuccess,
    testPetChatSourceMockUsesFallbackState,
    testPetChatSourceLocalErrorUsesErrorState,
    testPetChatNetworkFailureUsesBackendOfflineState,
    testPetChatLongReplyUsesLongReplyState,
    testPetRendererMenuHooksAreLocalAndNarrow,
    testPetRendererOpenFullAppUsesNarrowApi,
    testPetRendererMenuActionsUseNarrowApis,
    testPetRendererMenuActionFallbacksDoNotCrash,
    testPetRendererOpenFullAppFallbackDoesNotCrash,
  ];

  for (const test of tests) {
    await test();
    console.log(`[PASS] ${test.name}`);
  }

  console.log(`[PASS] pet renderer smoke complete (${tests.length} checks)`);
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
