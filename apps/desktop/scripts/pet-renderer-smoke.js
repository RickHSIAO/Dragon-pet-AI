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
    this.hidden = false;
    this.defaultView = null;
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

class FakeTimerApi {
  constructor() {
    this.now = 0;
    this.nextId = 1;
    this.timers = new Map();
  }

  setTimeout(callback, delayMs) {
    const id = this.nextId;
    this.nextId += 1;
    this.timers.set(id, {
      callback,
      runAt: this.now + delayMs,
    });
    return id;
  }

  clearTimeout(id) {
    this.timers.delete(id);
  }

  advance(delayMs) {
    const target = this.now + delayMs;

    while (true) {
      const nextTimer = [...this.timers.entries()]
        .filter(([, timer]) => timer.runAt <= target)
        .sort((a, b) => a[1].runAt - b[1].runAt)[0];

      if (!nextTimer) break;

      const [id, timer] = nextTimer;
      this.timers.delete(id);
      this.now = timer.runAt;
      timer.callback();
    }

    this.now = target;
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
  assertIncludes(html, 'id="pet-stage-controls"', "pet.html");
  assertIncludes(html, 'id="pet-bubble"', "pet.html");
  assertRegex(html, /id="pet-bubble"[^>]*class="[^"]*\bpet-speech-bubble\b/, "pet.html");
  assertIncludes(html, 'data-state="collapsed"', "pet.html");
  assertIncludes(html, 'hidden', "pet.html");
  assertIncludes(html, 'id="pet-bubble-message"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-status"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-response"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-details"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-open-hook"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-close-hook"', "pet.html");
  assertIncludes(html, 'id="pet-bubble-placeholder"', "pet.html");
  assertIncludes(html, 'id="pet-context-menu-hook"', "pet.html");
  assertIncludes(html, 'id="pet-open-full-app-hook"', "pet.html");
  assertIncludes(html, 'id="pet-menu"', "pet.html");
  assertIncludes(html, 'data-menu-state="closed"', "pet.html");
  assertIncludes(
    html,
    'data-supported-bubble-states="collapsed idle_default expanded handoff speaking thinking composing empty_input pending success backend_offline timeout llm_local_error fallback_mock long_reply"',
    "pet.html"
  );
  assertIncludes(html, 'id="pet-menu-toggle-details"', "pet.html");
  assertIncludes(html, 'id="pet-menu-reset-position"', "pet.html");
  assertIncludes(html, 'id="pet-menu-hide-window"', "pet.html");
  assertRegex(html, /id="pet-bubble-open-hook"(?:(?!>).)*aria-label="Open Full App for chat"/, "pet.html");
  assertRegex(html, /id="pet-bubble-close-hook"(?:(?!>).)*aria-label="Hide Pet Window"/, "pet.html");
  assertRegex(html, /id="pet-open-full-app-hook"(?:(?!>).)*data-hook="open-full-app"/, "pet.html");
  assert.equal(/id="pet-open-full-app-hook"(?:(?!>).)*disabled/.test(html), false);
  assert.equal(/id="pet-context-menu-hook"(?:(?!>).)*disabled/.test(html), false);
  assertRegex(html, /id="pet-drag-handle"[^>]*class="[^"]*\bpet-drag-handle\b/, "pet.html");
  assert.equal(/id="pet-drag-handle"[^>]*class="[^"]*\bpet-no-drag\b/.test(html), false);
  assertRegex(html, /id="pet-drag-region"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assert.equal(/id="pet-drag-region"[^>]*class="[^"]*\bpet-drag-region\b/.test(html), false);
  assertRegex(
    html,
    /id="pet-drag-region"[\s\S]*id="pet-avatar-container"[\s\S]*id="pet-bubble"[\s\S]*id="pet-hint"/,
    "pet.html"
  );
  assertRegex(html, /id="pet-avatar-container"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-avatar"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-stage-controls"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-status"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-response"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-details"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-placeholder"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[^>]*class="[^"]*\bpet-dev-chat-form\b/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[\s\S]*?data-dev-only="true"/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[\s\S]*?aria-hidden="true"/, "pet.html");
  assertRegex(html, /id="pet-chat-form-hook"[\s\S]*?hidden/, "pet.html");
  assertRegex(html, /id="pet-chat-input-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-input-hook"[\s\S]*?tabindex="-1"/, "pet.html");
  assertRegex(html, /id="pet-chat-input-hook"[\s\S]*?hidden/, "pet.html");
  assertRegex(html, /id="pet-chat-send-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-chat-send-hook"[\s\S]*?tabindex="-1"/, "pet.html");
  assertRegex(html, /id="pet-chat-send-hook"[\s\S]*?hidden/, "pet.html");
  assertRegex(html, /id="pet-bubble-open-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-bubble-close-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-context-menu-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-open-full-app-hook"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu-toggle-details"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu-toggle-details"(?:(?!>).)*data-menu-action="toggle-details"/, "pet.html");
  assertRegex(html, /id="pet-menu-reset-position"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assertRegex(html, /id="pet-menu-hide-window"[^>]*class="[^"]*\bpet-no-drag\b/, "pet.html");
  assert.ok(
    html.indexOf('id="pet-bubble-close-hook"') < html.indexOf('id="pet-drag-region"'),
    "close control should be outside the reply bubble flow"
  );
  assertNotIncludes(html, 'id="pet-bubble-details-toggle"', "pet.html");
  assertNotIncludes(html, 'id="pet-menu-open-full-app"', "pet.html");
  assertNotIncludes(html, 'id="pet-menu-close"', "pet.html");
  assertNotIncludes(html, ">speech bubble<", "pet.html");
  assert.equal(html.includes("pet-bubble-header"), false, "pet.html should not keep inline bubble controls");
  assertIncludes(html, "&#x54FC;&#xFF0C;", "pet.html");
  assertIncludes(html, "Display-only speech bubble. Type in Full App.", "pet.html");
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
  assertIncludes(css, "width: 300px", "pet.css");
  assertIncludes(css, "min-height: 400px", "pet.css");
  assertIncludes(css, "background: transparent", "pet.css");
  assertIncludes(css, "-webkit-app-region: drag", "pet.css");
  assertIncludes(css, "-webkit-app-region: no-drag", "pet.css");
  assertIncludes(css, ".pet-drag-handle", "pet.css");
  assertIncludes(css, ".pet-stage-controls", "pet.css");
  assertIncludes(css, ".pet-drag-region", "pet.css");
  assertIncludes(css, ".pet-no-drag", "pet.css");
  assertIncludes(css, ':not([data-bubble-state="collapsed"])', "pet.css");
  assertIncludes(css, '.pet-bubble[data-state="expanded"]', "pet.css");
  assertIncludes(css, ".pet-bubble-message", "pet.css");
  assertIncludes(css, ".pet-bubble-status", "pet.css");
  assertIncludes(css, ".pet-bubble-response", "pet.css");
  assertIncludes(css, ".pet-bubble-details", "pet.css");
  assertIncludes(css, ".pet-speech-bubble::after", "pet.css");
  assertIncludes(css, ".pet-dev-chat-form", "pet.css");
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
  assertRegex(css, /\.pet-stage-controls[\s\S]*position:\s*absolute/, "pet.css");
  assertRegex(css, /\.pet-stage-controls[\s\S]*top:\s*28px/, "pet.css");
  assertRegex(css, /\.pet-stage-controls[\s\S]*right:\s*10px/, "pet.css");
  assertRegex(css, /\.pet-stage-controls[\s\S]*z-index:\s*9/, "pet.css");
  assertRegex(css, /\.pet-shell[\s\S]*height:\s*400px/, "pet.css");
  assertRegex(css, /\.pet-shell[\s\S]*max-height:\s*400px/, "pet.css");
  assertRegex(css, /\.pet-shell[\s\S]*overflow:\s*hidden/, "pet.css");
  assertRegex(css, /\.pet-shell[\s\S]*grid-template-rows:\s*minmax\(0,\s*1fr\) auto/, "pet.css");
  assertRegex(css, /\.pet-stage,\s*\r?\n\.pet-drag-region[\s\S]*overflow:\s*hidden/, "pet.css");
  assertRegex(css, /\.pet-bubble[\s\S]*position:\s*relative/, "pet.css");
  assertRegex(css, /\.pet-bubble[\s\S]*width:\s*100%/, "pet.css");
  assertRegex(css, /\.pet-speech-bubble::after[\s\S]*content:\s*""/, "pet.css");
  assertRegex(css, /\.pet-speech-bubble::after[\s\S]*transform:\s*translateX\(-50%\) rotate\(45deg\)/, "pet.css");
  assertRegex(css, /\.pet-bubble[\s\S]*overflow:\s*hidden/, "pet.css");
  assertRegex(
    css,
    /\.pet-bubble[\s\S]*grid-template-rows:\s*minmax\(0,\s*1fr\) auto/,
    "pet.css"
  );
  assertRegex(css, /\.pet-bubble[\s\S]*gap:\s*6px/, "pet.css");
  assertRegex(css, /\.pet-bubble\[data-state="expanded"\][\s\S]*max-height:\s*122px/, "pet.css");
  assertRegex(css, /\.pet-bubble\[data-state="expanded"\][\s\S]*padding:\s*10px 12px/, "pet.css");
  assertRegex(css, /\.pet-bubble-body[\s\S]*display:\s*none/, "pet.css");
  assert.equal(css.includes(".pet-bubble-header"), false, "pet.css should not reserve inline bubble controls");
  assertRegex(css, /\.pet-dev-chat-form,\s*\r?\n\.pet-dev-chat-form\[hidden\][\s\S]*display:\s*none/, "pet.css");
  assertRegex(css, /\.pet-bubble-message[\s\S]*max-height:\s*16px/, "pet.css");
  assertRegex(css, /\.pet-bubble-message[\s\S]*overflow:\s*hidden/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*max-height:\s*92px/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*min-height:\s*0/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*overflow-y:\s*auto/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*font-size:\s*13px/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*line-height:\s*1\.42/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*overflow-wrap:\s*anywhere/, "pet.css");
  assertRegex(css, /\.pet-bubble-response[\s\S]*white-space:\s*pre-wrap/, "pet.css");
  assertRegex(css, /\.pet-bubble\[data-state="long_reply"\] \.pet-bubble-response[\s\S]*max-height:\s*92px/, "pet.css");
  assertRegex(css, /\.pet-bubble-details[\s\S]*max-height:\s*46px/, "pet.css");
  assertRegex(css, /\.pet-bubble-details[\s\S]*overflow-y:\s*auto/, "pet.css");
  assertRegex(css, /\.pet-bubble-details\[hidden\][\s\S]*display:\s*none/, "pet.css");
  assertRegex(css, /\.pet-bubble\[data-has-details="false"\] \.pet-bubble-details[\s\S]*display:\s*none/, "pet.css");
  assertRegex(css, /\.pet-bubble\[data-details-open="true"\][\s\S]*max-height:\s*158px/, "pet.css");
  assertRegex(css, /\.pet-bubble\[data-details-open="true"\] \.pet-bubble-response[\s\S]*max-height:\s*74px/, "pet.css");
  assertRegex(css, /\.pet-shell:not\(\[data-bubble-state="collapsed"\]\) \.pet-avatar[\s\S]*width:\s*142px/, "pet.css");
  assertRegex(css, /\.pet-shell:not\(\[data-bubble-state="collapsed"\]\) \.pet-avatar[\s\S]*height:\s*142px/, "pet.css");
  assertRegex(css, /\.pet-menu[\s\S]*max-height:\s*144px/, "pet.css");
  assertRegex(css, /\.pet-menu[\s\S]*overflow-y:\s*auto/, "pet.css");
  assertRegex(css, /\.pet-stage,\s*\r?\n\.pet-drag-region[\s\S]*-webkit-app-region:\s*no-drag\b/, "pet.css");
  assertRegex(css, /\.pet-avatar[\s\S]*-webkit-app-region:\s*no-drag\b/, "pet.css");
  assertRegex(css, /button,\s*\r?\ninput[\s\S]*-webkit-app-region:\s*no-drag/, "pet.css");
  assertRegex(css, /textarea[\s\S]*-webkit-app-region:\s*no-drag/, "pet.css");
}

function testPetRendererUsesBackendChatWithoutDirectOllama() {
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "sendPetChatMessage", "pet-renderer.js");
  assertIncludes(renderer, "PET_CHAT_TIMEOUT_MS = 100000", "pet-renderer.js");
  assertIncludes(renderer, "PET_REPLY_LONG_THRESHOLD = 160", "pet-renderer.js");
  assertIncludes(renderer, "PET_REPLY_PREVIEW_LIMIT = 120", "pet-renderer.js");
  assertIncludes(renderer, "PET_LONG_REPLY_HINT", "pet-renderer.js");
  assertIncludes(renderer, "function isLongReply", "pet-renderer.js");
  assertIncludes(renderer, "function truncatePetReply", "pet-renderer.js");
  assertIncludes(renderer, "function toggleBubbleDetails", "pet-renderer.js");
  assertIncludes(renderer, "function toggleDetailsFromMenu", "pet-renderer.js");
  assertIncludes(renderer, "function handleChatHandoff", "pet-renderer.js");
  assertIncludes(renderer, "PET_HANDOFF_REPLY", "pet-renderer.js");
  assertIncludes(renderer, "const PET_BUBBLE_STATE_EXPRESSIONS = Object.freeze", "pet-renderer.js");
  assertIncludes(renderer, "function normalizePetMood", "pet-renderer.js");
  assertIncludes(renderer, "function setPetExpressionForBubbleState", "pet-renderer.js");
  assertIncludes(renderer, "function expressionForBubbleState", "pet-renderer.js");
  assertIncludes(renderer, "fetchWithTimeout", "pet-renderer.js");
  assertIncludes(renderer, "PetChatTimeoutError", "pet-renderer.js");
  assertIncludes(renderer, "buildChatPayload", "pet-renderer.js");
  assertIncludes(renderer, 'use_memory: false', "pet-renderer.js");
  assertIncludes(renderer, 'if (!data || typeof data.reply !== "string")', "pet-renderer.js");
  assertIncludes(renderer, "throw new PetChatResponseError()", "pet-renderer.js");
  assertIncludes(renderer, "reply: data.reply", "pet-renderer.js");
  assertIncludes(renderer, 'mood: data && typeof data.mood === "string"', "pet-renderer.js");
  assertIncludes(renderer, 'source: data && typeof data.source === "string"', "pet-renderer.js");
  assertIncludes(renderer, '`${backendUrl}/chat`', "pet-renderer.js");
  assertIncludes(renderer, 'if (isLongReply(reply)) return "long_reply"', "pet-renderer.js");
  for (const mood of ["neutral", "focused", "happy", "proud", "annoyed", "worried", "sleepy"]) {
    assertIncludes(renderer, `christina_${mood}.png`, "pet-renderer.js");
  }
  assertNotIncludes(renderer, "fetch('/chat'", "pet-renderer.js");
  assertNotIncludes(renderer, 'fetch("/chat"', "pet-renderer.js");
  assertNotIncludes(renderer, "localhost:11434", "pet-renderer.js");
  assertNotIncludes(renderer, "127.0.0.1:11434", "pet-renderer.js");
  assertNotIncludes(renderer, "11434", "pet-renderer.js");
  assertNotIncludes(renderer, "error.stack", "pet-renderer.js");
}

function testPetRendererDefinesBubbleStates() {
  const renderer = readText(petRendererPath);
  assertIncludes(renderer, "const BUBBLE_STATES = Object.freeze", "pet-renderer.js");
  assertIncludes(renderer, "function setBubbleState", "pet-renderer.js");

  for (const state of [
    "collapsed",
    "idle_default",
    "expanded",
    "handoff",
    "speaking",
    "thinking",
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
    "\\u5f8c\\u7aef\\u4f3c\\u4e4e\\u4e0d\\u5728\\uff0c\\u6c5d\\u5148\\u53bb Full App \\u628a\\u5b83\\u53eb\\u9192\\u3002",
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
    "\\u56de\\u8986\\u8f03\\u9577\\uff0c\\u53ef\\u958b Full App \\u67e5\\u770b\\u5b8c\\u6574\\u5167\\u5bb9\\u3002",
    "pet-renderer.js"
  );
  assertIncludes(renderer, "const PET_RECENT_REPLY_VISIBLE_MS = 90000", "pet-renderer.js");
  assertIncludes(renderer, "const PET_HANDOFF_HINT_MS = 6000", "pet-renderer.js");
  assertIncludes(
    renderer,
    "\\u543e\\u5728\\u3002\\u8981\\u627e\\u543e\\u5c31\\u53bb Full App \\u8aaa\\u8a71\\u3002",
    "pet-renderer.js"
  );
  assertIncludes(
    renderer,
    "\\u53bb Full App \\u8aaa\\uff0c\\u543e\\u6703\\u807d\\u3002",
    "pet-renderer.js"
  );
}

function testPetRendererInitializesBubbleIdleDefault() {
  const { initializePetMode, PET_IDLE_REPLY, PET_MODE_DEFAULTS } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-drag-region",
    "pet-avatar-container",
    "pet-avatar",
    "pet-hint",
    "pet-bubble",
    "pet-bubble-details",
    "pet-bubble-details-toggle",
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
    "pet-menu-toggle-details",
  ]);

  initializePetMode(fakeDocument);

  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.initialized, "true");
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.mode, "pet");
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.bubbleState, "idle_default");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.equal(fakeDocument.getElementById("pet-hint").textContent, PET_MODE_DEFAULTS.hint);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "idle_default");
  assert.equal(fakeDocument.getElementById("pet-bubble").getAttribute("aria-expanded"), "true");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.menuState, "closed");
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");
  assert.equal(fakeDocument.getElementById("pet-menu").getAttribute("aria-hidden"), "true");
  assert.equal(fakeDocument.getElementById("pet-menu").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, PET_MODE_DEFAULTS.bubbleMessage);
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "idle");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_IDLE_REPLY);
  assert.match(fakeDocument.getElementById("pet-bubble-placeholder").textContent, /Display-only speech bubble/);
}

function testPetRendererRendersAllLocalBubbleStates() {
  const { BUBBLE_STATES, sanitizeBubbleDetailText, setBubbleState } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-bubble",
    "pet-bubble-title",
    "pet-bubble-details",
    "pet-bubble-details-toggle",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
    "pet-menu-toggle-details",
  ]);

  for (const [state, config] of Object.entries(BUBBLE_STATES)) {
    const renderedState = setBubbleState(fakeDocument, state);
    assert.equal(renderedState, state);
    assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.bubbleState, state);
    assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, state);
    assert.equal(
      fakeDocument.getElementById("pet-bubble-status").textContent,
      sanitizeBubbleDetailText(config.statusText)
    );
    assert.equal(
      fakeDocument.getElementById("pet-bubble-message").textContent,
      sanitizeBubbleDetailText(config.message)
    );
    assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, config.response);
    assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, config.inputDisabled);
    assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, config.sendDisabled);
    assert.equal(fakeDocument.getElementById("pet-bubble").hidden, !config.expanded);
    assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
    assert.equal(fakeDocument.getElementById("pet-bubble-details-toggle").getAttribute("aria-expanded"), "false");
  }
}

function assertDevComposerHidden(fakeDocument, expectedDisabled) {
  const form = fakeDocument.getElementById("pet-chat-form-hook");
  const input = fakeDocument.getElementById("pet-chat-input-hook");
  const send = fakeDocument.getElementById("pet-chat-send-hook");

  assert.ok(form, "dev chat form should exist");
  assert.ok(input, "dev chat input should exist");
  assert.ok(send, "dev chat send button should exist");
  assert.equal(form.hidden, true, "dev chat form should stay hidden");
  assert.equal(input.hidden, true, "dev chat input should stay hidden");
  assert.equal(send.hidden, true, "dev chat send button should stay hidden");
  assert.equal(form.getAttribute("aria-hidden"), "true");
  assert.equal(form.dataset.devOnly, "true");
  assert.equal(input.disabled, expectedDisabled, "dev chat input disabled state should match");
  assert.equal(send.disabled, expectedDisabled, "dev chat send disabled state should match");
}

function createPetBubbleStateDocument() {
  return new FakeDocument([
    "pet-mode-root",
    "pet-avatar-container",
    "pet-avatar",
    "pet-bubble",
    "pet-bubble-title",
    "pet-bubble-details",
    "pet-bubble-details-toggle",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-form-hook",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
    "pet-menu-toggle-details",
  ]);
}

function testPetSpeechBubbleKeepsDevComposerHiddenAcrossDisplayStates() {
  const { setBubbleState } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const enabledStates = [
    "idle_default",
    "expanded",
    "handoff",
    "speaking",
    "composing",
    "empty_input",
    "success",
    "backend_offline",
    "timeout",
    "llm_local_error",
    "fallback_mock",
    "long_reply",
  ];

  for (const state of enabledStates) {
    setBubbleState(fakeDocument, state);
    assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);
    assertDevComposerHidden(fakeDocument, false);
  }

  setBubbleState(fakeDocument, "thinking");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);
  assertDevComposerHidden(fakeDocument, true);

  setBubbleState(fakeDocument, "pending");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);
  assertDevComposerHidden(fakeDocument, true);
}

function testFullAppStatusDoesNotRemoveComposer() {
  const { handleOpenFullApp, setBubbleState } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();

  setBubbleState(fakeDocument, "expanded");
  assertDevComposerHidden(fakeDocument, false);

  handleOpenFullApp(fakeDocument, {
    openFullApp() {
      return Promise.resolve({ ok: true });
    },
  });

  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, "Opening Full App...");
  assertDevComposerHidden(fakeDocument, false);
}

function testPetRendererAppliesSpeechUpdateToSpeechBubble() {
  const { renderPetSpeechUpdate } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();

  const renderedState = renderPetSpeechUpdate(fakeDocument, {
    reply: "Speech from Full App.",
    mood: "happy",
    source: "llm_local",
  });

  assert.equal(renderedState, "speaking");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Speech from Full App.");
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, "打字請開 Full App。");
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.detailsOpen, "false");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "happy");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_happy\.png$/);
}

function testPetRendererSpeechUpdateUsesReplyOnlyWhenDiagnosticsExist() {
  const { renderPetSpeechUpdate, toggleBubbleDetails, visibleReplyForSpeechPayload } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const payload = {
    reply: "Character-facing reply only.",
    mood: "happy",
    source: "llm_local",
    status: "provider_debug_status",
    helper: "Open the diagnostics panel.",
    details: "raw provider latency=123ms",
    thinking: "THINKING_FIELD_SHOULD_NOT_RENDER",
    reasoning: "REASONING_TRACE_SHOULD_NOT_RENDER",
    diagnostics: {
      provider: "ollama",
      raw: "localhost:11434 returned debug JSON",
      thinking: "MESSAGE_THINKING_SHOULD_NOT_RENDER",
    },
    explanation: "This should never be visible in the main Pet bubble.",
  };

  assert.equal(visibleReplyForSpeechPayload(payload), "Character-facing reply only.");

  const renderedState = renderPetSpeechUpdate(fakeDocument, payload);
  const visibleText = fakeDocument.getElementById("pet-bubble-response").textContent;

  assert.equal(renderedState, "speaking");
  assert.equal(visibleText, "Character-facing reply only.");
  assert.doesNotMatch(
    visibleText,
    /provider_debug_status|diagnostics|latency|localhost|11434|helper|explanation|thinking|reasoning|llm_local|source|mood|raw/i
  );
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.hasDetails, "true");
  assert.equal(fakeDocument.getElementById("pet-menu-toggle-details").hidden, false);

  toggleBubbleDetails(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, false);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Character-facing reply only.");
  assert.match(fakeDocument.getElementById("pet-bubble-status").textContent, /provider_debug_status|local/);
  assert.match(
    fakeDocument.getElementById("pet-bubble-message").textContent,
    /Open the diagnostics panel|provider_debug_status|latency/
  );
  assert.doesNotMatch(
    `${fakeDocument.getElementById("pet-bubble-status").textContent} ${fakeDocument.getElementById("pet-bubble-message").textContent}`,
    /THINKING_FIELD|REASONING_TRACE|MESSAGE_THINKING|localhost|11434|<think|done thinking|\{|\}/i
  );
}

function testPetRendererSpeechUpdateHandlesLongReply() {
  const {
    PET_LONG_REPLY_HINT,
    PET_REPLY_LONG_THRESHOLD,
    PET_REPLY_PREVIEW_LIMIT,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const longReply = "x".repeat(PET_REPLY_LONG_THRESHOLD + 1);

  const renderedState = renderPetSpeechUpdate(fakeDocument, {
    reply: longReply,
    mood: "focused",
    source: "llm_local",
  });

  assert.equal(renderedState, "long_reply");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);
  assert.ok(fakeDocument.getElementById("pet-bubble-response").textContent.length <= PET_REPLY_PREVIEW_LIMIT + 1);
  assert.match(fakeDocument.getElementById("pet-bubble-response").textContent, /\u2026$/);
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, PET_LONG_REPLY_HINT);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.hasDetails, "true");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "focused");
}

function testPetBubbleDetailsDisclosureHiddenWhenNoMeaningfulDetails() {
  const { renderPetSpeechUpdate, toggleBubbleDetails, toggleDetailsFromMenu } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();

  renderPetSpeechUpdate(fakeDocument, {
    reply: "Only the reply is meaningful.",
  });

  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Only the reply is meaningful.");
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.hasDetails, "false");
  assert.equal(fakeDocument.getElementById("pet-mode-root").dataset.bubbleHasDetails, "false");
  assert.equal(fakeDocument.getElementById("pet-bubble-details-toggle").disabled, true);
  assert.equal(fakeDocument.getElementById("pet-menu-toggle-details").hidden, true);

  assert.equal(toggleBubbleDetails(fakeDocument), false);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(toggleDetailsFromMenu(fakeDocument), false);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
}

function testPetBubbleDetailsDisclosureTogglesSourceAndHelperText() {
  const { renderPetSpeechUpdate, toggleBubbleDetails } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();

  renderPetSpeechUpdate(fakeDocument, {
    reply: "Clean visible reply.",
    mood: "happy",
    source: "llm_local",
  });

  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Clean visible reply.");
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local");
  assert.doesNotMatch(
    fakeDocument.getElementById("pet-bubble-response").textContent,
    /source|status|helper|mood|local|llm_local|Full App/i
  );
  assert.equal(fakeDocument.getElementById("pet-menu-toggle-details").hidden, false);
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, "打字請開 Full App。");

  toggleBubbleDetails(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, false);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.detailsOpen, "true");
  assert.equal(fakeDocument.getElementById("pet-bubble-details-toggle").getAttribute("aria-expanded"), "true");

  toggleBubbleDetails(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.detailsOpen, "false");
  assert.equal(fakeDocument.getElementById("pet-bubble-details-toggle").getAttribute("aria-expanded"), "false");
}

function testPetBubbleDetailsSanitizesThinkingAndRawDiagnostics() {
  const { detailOptionsForSpeechPayload, renderPetSpeechUpdate, toggleBubbleDetails } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const payload = {
    reply: "Clean final answer.",
    source: "llm_local",
    status: "Thinking... done thinking.",
    helper: "<think>hidden reasoning</think>",
    details: '{"provider":"ollama","thinking":"secret"}',
    debug: "Traceback stack trace localhost:11434",
  };

  assert.deepEqual(detailOptionsForSpeechPayload(payload, "speaking", "llm_local"), {
    statusText: "local",
    message: "\u6253\u5b57\u8acb\u958b Full App\u3002",
    detailsAvailable: true,
  });

  renderPetSpeechUpdate(fakeDocument, payload);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Clean final answer.");
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);

  toggleBubbleDetails(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, false);
  assert.doesNotMatch(
    `${fakeDocument.getElementById("pet-bubble-status").textContent} ${fakeDocument.getElementById("pet-bubble-message").textContent}`,
    /thinking|done thinking|reasoning|<think|provider.*ollama|Traceback|stack trace|localhost|11434|\{|\}/i
  );
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Clean final answer.");
}

function testPetPresenceIdleDefaultStaticHint() {
  const { PET_IDLE_REPLY, setPetIdleDefault } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();

  const renderedState = setPetIdleDefault(fakeDocument, { timerApi: new FakeTimerApi() });

  assert.equal(renderedState, "idle_default");
  assert.equal(fakeDocument.getElementById("pet-bubble").hidden, false);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_IDLE_REPLY);
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "idle");
  assert.doesNotMatch(fakeDocument.getElementById("pet-bubble-response").textContent, /source|status|mood|llm_local|local/);
  assertDevComposerHidden(fakeDocument, false);
}

function testPetPresenceRecentReplyReplacesIdleAndExpires() {
  const {
    PET_IDLE_REPLY,
    PET_RECENT_REPLY_VISIBLE_MS,
    renderPetSpeechUpdate,
    setPetIdleDefault,
  } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(fakeDocument, { timerApi });
  renderPetSpeechUpdate(
    fakeDocument,
    {
      reply: "Recent clean reply.",
      mood: "happy",
      source: "llm_local",
    },
    { timerApi }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Recent clean reply.");

  timerApi.advance(PET_RECENT_REPLY_VISIBLE_MS - 1);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Recent clean reply.");

  timerApi.advance(1);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "idle_default");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_IDLE_REPLY);
}

function testPetPresenceRecentReplyTimerResetsOnNewReply() {
  const { PET_IDLE_REPLY, PET_RECENT_REPLY_VISIBLE_MS, renderPetSpeechUpdate } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  renderPetSpeechUpdate(fakeDocument, { reply: "First reply.", source: "llm_local" }, { timerApi });
  timerApi.advance(50000);
  renderPetSpeechUpdate(fakeDocument, { reply: "Second reply.", source: "llm_local" }, { timerApi });

  timerApi.advance(PET_RECENT_REPLY_VISIBLE_MS - 1);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Second reply.");

  timerApi.advance(1);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_IDLE_REPLY);
}

function testPetPresenceHandoffHintRestoresRecentReplyOrIdle() {
  const {
    PET_HANDOFF_HINT_MS,
    PET_HANDOFF_REPLY,
    PET_IDLE_REPLY,
    handleChatHandoff,
    renderPetSpeechUpdate,
    showPetHandoffHint,
  } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();
  let opened = false;

  renderPetSpeechUpdate(fakeDocument, { reply: "Still recent.", source: "llm_local" }, { timerApi });
  const result = handleChatHandoff(
    fakeDocument,
    {
      openFullApp() {
        opened = true;
        return Promise.resolve({ ok: true });
      },
    },
    { timerApi }
  );

  assert.equal(opened, true);
  assert.equal(typeof result.then, "function");
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "handoff");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_HANDOFF_REPLY);
  assertDevComposerHidden(fakeDocument, false);

  timerApi.advance(PET_HANDOFF_HINT_MS);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Still recent.");

  showPetHandoffHint(fakeDocument, { timerApi });
  timerApi.advance(PET_HANDOFF_HINT_MS);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Still recent.");

  timerApi.advance(90000);
  showPetHandoffHint(fakeDocument, { timerApi });
  timerApi.advance(PET_HANDOFF_HINT_MS);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_IDLE_REPLY);
}

function testPetPresenceHiddenRestoreUsesRecentWindow() {
  const {
    PET_IDLE_REPLY,
    PET_RECENT_REPLY_VISIBLE_MS,
    renderPetSpeechUpdate,
    restorePetPresenceAfterShow,
  } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  renderPetSpeechUpdate(fakeDocument, { reply: "Restore me.", source: "llm_local" }, { timerApi });
  fakeDocument.getElementById("pet-bubble-response").textContent = "Hidden stale text.";
  restorePetPresenceAfterShow(fakeDocument, { timerApi });
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Restore me.");

  timerApi.advance(PET_RECENT_REPLY_VISIBLE_MS);
  restorePetPresenceAfterShow(fakeDocument, { timerApi });
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_IDLE_REPLY);
}

function testPetPresenceErrorMessageStaysClean() {
  const { renderPetSpeechUpdate, toggleBubbleDetails } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();

  renderPetSpeechUpdate(fakeDocument, {
    reply: "raw provider diagnostic: localhost:11434 failed",
    mood: "worried",
    source: "llm_local_error",
  });

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "llm_local_error");
  assert.equal(
    fakeDocument.getElementById("pet-bubble-response").textContent,
    "\u543e\u7684\u9b54\u529b\u66ab\u6642\u5361\u4f4f\u4e86\u3002"
  );
  assert.doesNotMatch(
    fakeDocument.getElementById("pet-bubble-response").textContent,
    /provider|diagnostic|localhost|11434|llm_local_error/
  );
  assert.match(fakeDocument.getElementById("pet-bubble-message").textContent, /Full App|provider/);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);

  toggleBubbleDetails(fakeDocument);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, false);
  assert.doesNotMatch(
    `${fakeDocument.getElementById("pet-bubble-status").textContent} ${fakeDocument.getElementById("pet-bubble-message").textContent}`,
    /raw provider diagnostic|localhost|11434|stack trace|<think|thinking/i
  );
}

function testPetRendererRegistersFixedSpeechUpdateListener() {
  const { initializePetMode } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-drag-region",
    "pet-avatar-container",
    "pet-avatar",
    "pet-hint",
    "pet-bubble",
    "pet-bubble-title",
    "pet-bubble-details",
    "pet-bubble-details-toggle",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-form-hook",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
    "pet-bubble-open-hook",
    "pet-bubble-close-hook",
    "pet-open-full-app-hook",
    "pet-context-menu-hook",
    "pet-menu",
  ]);
  const originalWindow = global.window;
  let registeredCallback = null;

  global.window = {
    dragonPet: {
      onSpeechUpdate(callback) {
        registeredCallback = callback;
        return () => {};
      },
    },
  };

  initializePetMode(fakeDocument);
  global.window = originalWindow;

  assert.equal(typeof registeredCallback, "function");
  registeredCallback({
    reply: "Mirrored reply.",
    mood: "proud",
    source: "llm_local",
  });

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Mirrored reply.");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "proud");
}

function testPetExpressionMappingHelpersUseExistingAssets() {
  const {
    CHRISTINA_EXPRESSION_ASSETS,
    PET_BUBBLE_STATE_EXPRESSIONS,
    expressionForBubbleState,
    normalizePetMood,
    setPetExpression,
    setPetExpressionForBubbleState,
  } = require(petRendererPath);
  const fakeDocument = new FakeDocument(["pet-avatar-container", "pet-avatar"]);

  assert.deepEqual(Object.keys(CHRISTINA_EXPRESSION_ASSETS).sort(), [
    "annoyed",
    "focused",
    "happy",
    "neutral",
    "proud",
    "sleepy",
    "worried",
  ]);

  for (const [mood, assetPath] of Object.entries(CHRISTINA_EXPRESSION_ASSETS)) {
    assert.match(assetPath, new RegExp(`christina_${mood}\\.png$`));
  }

  assert.equal(normalizePetMood("happy"), "happy");
  assert.equal(normalizePetMood("focused"), "focused");
  assert.equal(normalizePetMood("not_a_mood"), "neutral");
  assert.equal(expressionForBubbleState("pending"), "focused");
  assert.equal(expressionForBubbleState("thinking"), "focused");
  assert.equal(expressionForBubbleState("backend_offline"), "worried");
  assert.equal(expressionForBubbleState("timeout"), "sleepy");
  assert.equal(expressionForBubbleState("llm_local_error"), "worried");
  assert.equal(expressionForBubbleState("fallback_mock"), "proud");
  assert.equal(expressionForBubbleState("empty_input"), "annoyed");
  assert.equal(expressionForBubbleState("long_reply"), "focused");
  assert.equal(expressionForBubbleState("idle_default"), "neutral");
  assert.equal(expressionForBubbleState("handoff"), "neutral");
  assert.equal(expressionForBubbleState("speaking", "happy"), "happy");
  assert.equal(expressionForBubbleState("success", "happy"), "happy");
  assert.equal(expressionForBubbleState("success", "unknown"), "neutral");
  assert.equal(PET_BUBBLE_STATE_EXPRESSIONS.composing, "neutral");

  setPetExpression(fakeDocument, "focused");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "focused");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_focused\.png$/);

  setPetExpression(fakeDocument, "unknown");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_neutral\.png$/);

  setPetExpressionForBubbleState(fakeDocument, "empty_input");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "annoyed");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_annoyed\.png$/);
}

function testPetLongReplyThresholdHelper() {
  const { PET_REPLY_LONG_THRESHOLD, isLongReply, stateForChatSource } = require(petRendererPath);
  const shortReply = "x".repeat(PET_REPLY_LONG_THRESHOLD);
  const longReply = "x".repeat(PET_REPLY_LONG_THRESHOLD + 1);

  assert.equal(PET_REPLY_LONG_THRESHOLD, 160);
  assert.equal(isLongReply(shortReply), false);
  assert.equal(isLongReply(longReply), true);
  assert.equal(stateForChatSource("llm_local", shortReply), "speaking");
  assert.equal(stateForChatSource("llm_local", longReply), "long_reply");
  assert.equal(stateForChatSource("mock", longReply), "fallback_mock");
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
    "pet-bubble-details",
    "pet-bubble-details-toggle",
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
    "pet-menu-toggle-details",
    "pet-menu-reset-position",
    "pet-menu-hide-window",
  ]);
  const originalWindow = global.window;
  const calls = [];

  global.window = {
    dragonPet: {
      openFullApp() {
        calls.push("open");
        return Promise.resolve({ ok: true });
      },
      hidePetWindow() {
        calls.push("hide");
        return Promise.resolve({ ok: true });
      },
    },
  };

  initializePetMode(fakeDocument);
  fakeDocument.getElementById("pet-drag-region").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "idle_default");

  fakeDocument.getElementById("pet-bubble-close-hook").dispatchEvent({ type: "click" });
  assert.deepEqual(calls, ["hide"]);

  fakeDocument.getElementById("pet-bubble-open-hook").dispatchEvent({ type: "click" });
  assert.deepEqual(calls, ["hide", "open"]);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "handoff");
  assert.doesNotMatch(fakeDocument.getElementById("pet-bubble-response").textContent, /source|status|mood|llm_local|local/);

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
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "annoyed");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_annoyed\.png$/);
  global.window = originalWindow;
}

function createPetChatDocument() {
  return new FakeDocument([
    "pet-mode-root",
    "pet-avatar-container",
    "pet-avatar",
    "pet-bubble",
    "pet-bubble-title",
    "pet-bubble-details",
    "pet-bubble-details-toggle",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-form-hook",
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
  assertDevComposerHidden(fakeDocument, false);
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

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "thinking");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, true);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, true);
  assertDevComposerHidden(fakeDocument, true);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "focused");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_focused\.png$/);

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
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Pet reply");
  assert.doesNotMatch(fakeDocument.getElementById("pet-bubble-response").textContent, /Full App/);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, false);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, false);
  assertDevComposerHidden(fakeDocument, false);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "happy");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_happy\.png$/);
  assert.equal(input.value, "");
}

async function testPetChatFocusedMoodUpdatesFocusedExpression() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "focus please";

  await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => ({
        ok: true,
        json: async () => ({
          reply: "Focused reply",
          mood: "focused",
          source: "llm_local",
        }),
      }),
    }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "focused");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_focused\.png$/);
}

async function testPetChatProudMoodUpdatesProudExpression() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "proud please";

  await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => ({
        ok: true,
        json: async () => ({
          reply: "Proud reply",
          mood: "proud",
          source: "llm_local",
        }),
      }),
    }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "proud");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_proud\.png$/);
}

async function testPetChatUnknownMoodFallsBackToNeutralExpression() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "unknown mood please";

  await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => ({
        ok: true,
        json: async () => ({
          reply: "Unknown mood reply",
          mood: "mysterious",
          source: "llm_local",
        }),
      }),
    }
  );

  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_neutral\.png$/);
}

async function testPetChatDoubleSubmitDuringPendingDoesNotDuplicateFetch() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  const input = fakeDocument.getElementById("pet-chat-input-hook");
  let fetchCalls = 0;
  let resolveFetch;

  input.value = "do not duplicate";
  const pendingFetch = new Promise((resolve) => {
    resolveFetch = resolve;
  });

  const firstSubmit = handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl() {
        fetchCalls += 1;
        return pendingFetch;
      },
    }
  );

  const secondSubmit = await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl() {
        fetchCalls += 1;
        return pendingFetch;
      },
    }
  );

  assert.equal(secondSubmit, null);
  assert.equal(fetchCalls, 1);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "thinking");

  resolveFetch({
    ok: true,
    json: async () => ({
      reply: "Done",
      mood: "neutral",
      source: "llm_local",
    }),
  });

  await firstSubmit;
  assert.equal(fetchCalls, 1);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");

  input.value = "send after pending";
  const nextSubmit = await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl() {
        fetchCalls += 1;
        return Promise.resolve({
          ok: true,
          json: async () => ({
            reply: "Second done",
            mood: "happy",
            source: "llm_local",
          }),
        });
      },
    }
  );

  assert.deepEqual(nextSubmit, { reply: "Second done", mood: "happy", source: "llm_local" });
  assert.equal(fetchCalls, 2);
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "Second done");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, false);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, false);
  assertDevComposerHidden(fakeDocument, false);
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
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "proud");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_proud\.png$/);
  assertDevComposerHidden(fakeDocument, false);
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
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "吾的魔力暫時卡住了。");
  assert.doesNotMatch(fakeDocument.getElementById("pet-bubble-response").textContent, /Safe fallback reply/);
  assert.match(fakeDocument.getElementById("pet-bubble-message").textContent, /Full App/);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "worried");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_worried\.png$/);
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").value, "error please");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, false);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, false);
  assertDevComposerHidden(fakeDocument, false);
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
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "吾的魔力暫時卡住了。");
  assert.match(fakeDocument.getElementById("pet-bubble-message").textContent, /Full App/);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "worried");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_worried\.png$/);
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").value, "network please");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, false);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, false);
  assertDevComposerHidden(fakeDocument, false);
}

async function testPetChatTimeoutUsesTimeoutStateAndKeepsInput() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "timeout please";

  const result = await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      timeoutMs: 1,
      fetchImpl: async () => new Promise(() => {}),
    }
  );

  assert.equal(result, null);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "timeout");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local timeout");
  assert.match(fakeDocument.getElementById("pet-bubble-response").textContent, /\u9192\u4f86/);
  assert.doesNotMatch(fakeDocument.getElementById("pet-bubble-response").textContent, /Full App/);
  assert.match(fakeDocument.getElementById("pet-bubble-message").textContent, /Full App/);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "sleepy");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_sleepy\.png$/);
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").value, "timeout please");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, false);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, false);
  assertDevComposerHidden(fakeDocument, false);
}

async function testPetChatMalformedResponseUsesSafeErrorState() {
  const { handleChatSubmit } = require(petRendererPath);
  const fakeDocument = createPetChatDocument();
  fakeDocument.getElementById("pet-chat-input-hook").value = "malformed please";

  const result = await handleChatSubmit(
    { preventDefault() {} },
    fakeDocument,
    {
      backendUrl: "http://localhost:8000",
      fetchImpl: async () => ({
        ok: true,
        json: async () => ({
          mood: "happy",
          source: "llm_local",
        }),
      }),
    }
  );

  assert.equal(result, null);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "llm_local_error");
  assert.equal(fakeDocument.getElementById("pet-bubble-status").textContent, "local model error");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, "吾的魔力暫時卡住了。");
  assert.match(fakeDocument.getElementById("pet-bubble-message").textContent, /Full App/);
  assert.doesNotMatch(fakeDocument.getElementById("pet-bubble-response").textContent, /PetChatResponseError/);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "worried");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_worried\.png$/);
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").value, "malformed please");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, false);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, false);
  assertDevComposerHidden(fakeDocument, false);
}

async function testPetChatLongReplyUsesLongReplyState() {
  const { PET_LONG_REPLY_HINT, PET_REPLY_PREVIEW_LIMIT, handleChatSubmit } = require(petRendererPath);
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
  assert.equal(fakeDocument.getElementById("pet-bubble-message").textContent, PET_LONG_REPLY_HINT);
  assert.ok(fakeDocument.getElementById("pet-bubble-response").textContent.length <= PET_REPLY_PREVIEW_LIMIT + 1);
  assert.match(fakeDocument.getElementById("pet-bubble-response").textContent, /\u2026$/);
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "focused");
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").disabled, false);
  assert.equal(fakeDocument.getElementById("pet-chat-send-hook").disabled, false);
  assertDevComposerHidden(fakeDocument, false);
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
    "pet-menu-toggle-details",
    "pet-bubble-details",
    "pet-bubble-details-toggle",
    "pet-bubble-status",
    "pet-bubble-response",
    "pet-menu-reset-position",
    "pet-menu-hide-window",
  ]);

  initializePetMode(fakeDocument);

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.dispatchEvent({
    type: "click",
    target: fakeDocument.getElementById("pet-menu"),
  });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.dispatchEvent({
    type: "click",
    target: fakeDocument.getElementById("pet-context-menu-hook"),
  });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");

  fakeDocument.dispatchEvent({
    type: "click",
    target: new FakeElement("outside"),
  });
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

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");

  fakeDocument.getElementById("pet-context-menu-hook").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "open");
  fakeDocument.getElementById("pet-menu-toggle-details").dispatchEvent({ type: "click" });
  assert.equal(fakeDocument.getElementById("pet-menu").dataset.state, "closed");
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.detailsOpen, "true");
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, false);
  assert.equal(fakeDocument.getElementById("pet-menu-toggle-details").getAttribute("aria-expanded"), "true");
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

function testPetRendererChatHandoffUsesFullAppWithoutPetInput() {
  const { PET_HANDOFF_REPLY, handleChatHandoff } = require(petRendererPath);
  const fakeDocument = new FakeDocument([
    "pet-mode-root",
    "pet-bubble",
    "pet-bubble-title",
    "pet-bubble-details",
    "pet-bubble-details-toggle",
    "pet-menu-toggle-details",
    "pet-bubble-status",
    "pet-bubble-message",
    "pet-bubble-response",
    "pet-bubble-placeholder",
    "pet-chat-form-hook",
    "pet-chat-input-hook",
    "pet-chat-send-hook",
  ]);
  let called = false;
  const timerApi = new FakeTimerApi();

  const result = handleChatHandoff(fakeDocument, {
    openFullApp() {
      called = true;
      return Promise.resolve({ ok: true });
    },
  }, { timerApi });

  assert.equal(called, true);
  assert.equal(typeof result.then, "function");
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "handoff");
  assert.equal(fakeDocument.getElementById("pet-chat-form-hook").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-chat-input-hook").getAttribute("tabindex"), "-1");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_HANDOFF_REPLY);
  assert.doesNotMatch(fakeDocument.getElementById("pet-bubble-response").textContent, /source|status|mood|llm_local|local/);
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
    testPetRendererInitializesBubbleIdleDefault,
    testPetRendererRendersAllLocalBubbleStates,
    testPetSpeechBubbleKeepsDevComposerHiddenAcrossDisplayStates,
    testFullAppStatusDoesNotRemoveComposer,
    testPetRendererAppliesSpeechUpdateToSpeechBubble,
    testPetRendererSpeechUpdateUsesReplyOnlyWhenDiagnosticsExist,
    testPetRendererSpeechUpdateHandlesLongReply,
    testPetBubbleDetailsDisclosureHiddenWhenNoMeaningfulDetails,
    testPetBubbleDetailsDisclosureTogglesSourceAndHelperText,
    testPetBubbleDetailsSanitizesThinkingAndRawDiagnostics,
    testPetPresenceIdleDefaultStaticHint,
    testPetPresenceRecentReplyReplacesIdleAndExpires,
    testPetPresenceRecentReplyTimerResetsOnNewReply,
    testPetPresenceHandoffHintRestoresRecentReplyOrIdle,
    testPetPresenceHiddenRestoreUsesRecentWindow,
    testPetPresenceErrorMessageStaysClean,
    testPetRendererRegistersFixedSpeechUpdateListener,
    testPetExpressionMappingHelpersUseExistingAssets,
    testPetLongReplyThresholdHelper,
    testPetRendererTogglesBubbleState,
    testPetRendererTogglesMenuState,
    testPetRendererClickAndSubmitHandlersAreLocalOnly,
    testPetChatEmptyInputDoesNotFetch,
    testPetChatSubmitUsesBackendChatAndRendersSuccess,
    testPetChatFocusedMoodUpdatesFocusedExpression,
    testPetChatProudMoodUpdatesProudExpression,
    testPetChatUnknownMoodFallsBackToNeutralExpression,
    testPetChatDoubleSubmitDuringPendingDoesNotDuplicateFetch,
    testPetChatSourceMockUsesFallbackState,
    testPetChatSourceLocalErrorUsesErrorState,
    testPetChatNetworkFailureUsesBackendOfflineState,
    testPetChatTimeoutUsesTimeoutStateAndKeepsInput,
    testPetChatMalformedResponseUsesSafeErrorState,
    testPetChatLongReplyUsesLongReplyState,
    testPetRendererMenuHooksAreLocalAndNarrow,
    testPetRendererOpenFullAppUsesNarrowApi,
    testPetRendererChatHandoffUsesFullAppWithoutPetInput,
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
