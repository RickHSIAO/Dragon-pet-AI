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
  // TASK-166B: shell is now fluid (100% of Electron window); fixed 300/400 removed from shell
  const css = readText(petCssPath);
  assertIncludes(css, "width: 100%", "pet.css");     // fluid shell width
  assertIncludes(css, "height: 100%", "pet.css");    // fluid shell height
  assertIncludes(css, "min-width: 225px", "pet.css");   // Small preset minimum
  assertIncludes(css, "min-height: 300px", "pet.css");  // Small preset minimum
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
  assertRegex(css, /\.pet-shell[\s\S]*height:\s*100%/, "pet.css");  // TASK-166B: fluid
  assertRegex(css, /\.pet-shell[\s\S]*max-height:\s*100%/, "pet.css");  // TASK-166B: fluid
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
  assertRegex(css, /\.pet-avatar[\s\S]*object-fit:\s*contain/, "pet.css");
  // TASK-166A: drop-shadow is allowed on .pet-avatar for wallpaper contrast;
  // destructive filter types (blur, brightness, invert, etc.) remain prohibited
  assertRegex(css, /\.pet-avatar[\s\S]*filter:\s*drop-shadow/, "pet.css");
  assertNotIncludes(css, "filter: blur", "pet.css");
  assertNotIncludes(css, "filter: brightness", "pet.css");
  assertNotIncludes(css, "filter: invert", "pet.css");
  assertNotIncludes(css, "filter: grayscale", "pet.css");
  assertNotIncludes(css, "filter: opacity", "pet.css");
  assertNotIncludes(css, "mix-blend-mode", "pet.css");
  assertNotIncludes(css, "background-image", "pet.css");
  assertNotIncludes(css, "mask-image", "pet.css");
  assertNotIncludes(css, "-webkit-mask", "pet.css");
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
    "pet-hint",          // TASK-166C: needed for quiet-mode hint suppression tests
    "pet-menu-quiet-mode",  // TASK-166C: needed for quiet-mode data-attribute tests
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
    PET_MOOD_EXPRESSION_MAP,
    PET_BUBBLE_STATE_EXPRESSIONS,
    expressionAssetForMood,
    expressionForBubbleState,
    normalizePetMood,
    renderPetSpeechUpdate,
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

  assert.equal(PET_MOOD_EXPRESSION_MAP.error, "worried");
  assert.equal(PET_MOOD_EXPRESSION_MAP.offline, "worried");
  assert.equal(PET_MOOD_EXPRESSION_MAP.sad, "worried");
  assert.equal(PET_MOOD_EXPRESSION_MAP.pending, "focused");

  assert.equal(normalizePetMood("happy"), "happy");
  assert.equal(normalizePetMood("focused"), "focused");
  assert.equal(normalizePetMood("FOCUSED"), "focused");
  assert.equal(normalizePetMood(" proud "), "proud");
  assert.equal(normalizePetMood("worried"), "worried");
  assert.equal(normalizePetMood("error"), "worried");
  assert.equal(normalizePetMood("offline"), "worried");
  assert.equal(normalizePetMood("sad"), "worried");
  assert.equal(normalizePetMood("not_a_mood"), "neutral");
  assert.equal(normalizePetMood(""), "neutral");
  assert.equal(normalizePetMood(null), "neutral");
  assert.equal(normalizePetMood("__proto__"), "neutral");
  assert.equal(normalizePetMood("toString"), "neutral");
  assert.deepEqual(expressionAssetForMood("focused"), {
    mood: "focused",
    assetPath: CHRISTINA_EXPRESSION_ASSETS.focused,
  });
  assert.deepEqual(expressionAssetForMood("missing"), {
    mood: "neutral",
    assetPath: CHRISTINA_EXPRESSION_ASSETS.neutral,
  });
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

  setPetExpression(fakeDocument, "proud");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "proud");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_proud\.png$/);

  setPetExpression(fakeDocument, "worried");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "worried");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_worried\.png$/);

  setPetExpression(fakeDocument, "unknown");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_neutral\.png$/);

  setPetExpression(fakeDocument, "sleepy");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "sleepy");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_sleepy\.png$/);
  fakeDocument.getElementById("pet-avatar").onerror();
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_neutral\.png$/);

  setPetExpressionForBubbleState(fakeDocument, "empty_input");
  assert.equal(fakeDocument.getElementById("pet-avatar-container").dataset.expression, "annoyed");
  assert.match(fakeDocument.getElementById("pet-avatar").getAttribute("src"), /christina_annoyed\.png$/);

  const speechDocument = createPetBubbleStateDocument();
  renderPetSpeechUpdate(speechDocument, {
    reply: "Mood should not alter this reply.",
    mood: "toString",
    source: "llm_local",
  });
  assert.equal(
    speechDocument.getElementById("pet-bubble-response").textContent,
    "Mood should not alter this reply."
  );
  assert.equal(speechDocument.getElementById("pet-avatar-container").dataset.expression, "neutral");
  assert.doesNotMatch(
    speechDocument.getElementById("pet-bubble-response").textContent,
    /mood|source|debug|details|thinking|toString/
  );
  assert.equal(speechDocument.getElementById("pet-bubble-details").hidden, true);
}

function testPetMoodExpressionManualSmokeHookUsesRealSpeechPath() {
  const {
    PET_MOOD_SMOKE_API_NAME,
    PET_MOOD_SMOKE_REPLY,
    installPetMoodExpressionSmokeHook,
  } = require(petRendererPath);
  const fakeDocument = createPetBubbleStateDocument();
  const fakeWindow = {};

  const smokeApi = installPetMoodExpressionSmokeHook(fakeDocument, fakeWindow);
  assert.equal(fakeWindow[PET_MOOD_SMOKE_API_NAME], smokeApi);
  assert.deepEqual([...smokeApi.supportedMoods].sort(), [
    "annoyed",
    "focused",
    "happy",
    "neutral",
    "proud",
    "sleepy",
    "worried",
  ]);

  const focused = smokeApi.apply("focused");
  const proud = smokeApi.apply("proud");
  const worried = smokeApi.apply("worried");
  const neutral = smokeApi.apply("neutral");
  const unknown = smokeApi.apply("missing");

  assert.deepEqual(
    [focused.expression, proud.expression, worried.expression, neutral.expression, unknown.expression],
    ["focused", "proud", "worried", "neutral", "neutral"]
  );
  assert.match(focused.src, /christina_focused\.png$/);
  assert.match(proud.src, /christina_proud\.png$/);
  assert.match(worried.src, /christina_worried\.png$/);
  assert.match(neutral.src, /christina_neutral\.png$/);
  assert.notEqual(focused.src, proud.src);
  assert.notEqual(proud.src, worried.src);
  assert.notEqual(worried.src, neutral.src);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.state, "speaking");
  assert.equal(fakeDocument.getElementById("pet-bubble-response").textContent, PET_MOOD_SMOKE_REPLY);
  assert.doesNotMatch(
    fakeDocument.getElementById("pet-bubble-response").textContent,
    /focused|proud|worried|neutral|mood|source|debug|details|thinking/
  );
  assert.equal(fakeDocument.getElementById("pet-bubble-details").hidden, true);
  assert.equal(fakeDocument.getElementById("pet-bubble").dataset.hasDetails, "false");
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

// ---------------------------------------------------------------------------
// TASK-157 — Pet Bubble Thinking / Typing State
// ---------------------------------------------------------------------------

async function testPetThinkingSourceMapsToThinkingState() {
  const { stateForChatSource, PET_THINKING_SOURCE } = require(petRendererPath);
  const state = stateForChatSource(PET_THINKING_SOURCE, "any reply text");
  assert.equal(state, "thinking",
    `Expected stateForChatSource("${PET_THINKING_SOURCE}", ...) to return "thinking", got "${state}"`);
}

async function testPetThinkingRenderShowsReplyInBubble() {
  const { renderPetSpeechUpdate, PET_THINKING_SOURCE } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const reply = "\u543e\u3001\u543e\u624d\u4e0d\u662f\u5728\u8a8d\u771f\u601d\u8003\u5462\u2026\u2026\u7b49\u4e00\u4e0b\uff01";
  const state = renderPetSpeechUpdate(doc, { reply, mood: "focused", source: PET_THINKING_SOURCE });
  assert.equal(state, "thinking",
    `Expected renderPetSpeechUpdate with pet_thinking source to return "thinking", got "${state}"`);
  const responseEl = doc.getElementById("pet-bubble-response");
  assert.ok(responseEl && responseEl.textContent === reply,
    `Expected bubble response to show thinking text, got "${responseEl && responseEl.textContent}"`);
}

async function testPetThinkingRenderBubbleIsClean() {
  const { renderPetSpeechUpdate, PET_THINKING_SOURCE } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  renderPetSpeechUpdate(doc, {
    reply: "\u543e\u6b63\u5728\u60f3\u3002",
    mood: "focused",
    source: PET_THINKING_SOURCE,
  });
  const responseEl = doc.getElementById("pet-bubble-response");
  const text = responseEl ? responseEl.textContent : "";
  assert.doesNotMatch(text, /pet_thinking|source:|mood:|\{|\}/,
    `Thinking bubble must not contain debug tokens, got: "${text}"`);
}

async function testPetThinkingSourceConstantIsExported() {
  const { PET_THINKING_SOURCE } = require(petRendererPath);
  assert.equal(typeof PET_THINKING_SOURCE, "string",
    `PET_THINKING_SOURCE must be a string, got ${typeof PET_THINKING_SOURCE}`);
  assert.ok(PET_THINKING_SOURCE.length > 0,
    `PET_THINKING_SOURCE must be a non-empty string`);
  assert.equal(PET_THINKING_SOURCE, "pet_thinking",
    `PET_THINKING_SOURCE must equal "pet_thinking", got "${PET_THINKING_SOURCE}"`);
}


// ---------------------------------------------------------------------------
// TASK-158 — Pet Idle Presence Line Rotation
// ---------------------------------------------------------------------------

function testPetIdleLineConstantsAreExported() {
  const { PET_IDLE_LINES, PET_IDLE_ROTATION_MS, PET_IDLE_REPLY } = require(petRendererPath);
  assert.ok(Array.isArray(PET_IDLE_LINES) || (PET_IDLE_LINES && typeof PET_IDLE_LINES[Symbol.iterator] === "function"),
    "PET_IDLE_LINES must be iterable");
  const lines = [...PET_IDLE_LINES];
  assert.ok(lines.length >= 2, "PET_IDLE_LINES must have at least 2 lines");
  for (const line of lines) {
    assert.equal(typeof line, "string");
    assert.ok(line.length > 0, "idle line must be non-empty");
    assert.doesNotMatch(line, /source:|mood:|\{|\}|llm_local|pet_thinking|debug|provider/i,
      `idle line must not contain debug tokens: "${line}"`);
    assert.notEqual(line, PET_IDLE_REPLY,
      "idle rotation line should differ from PET_IDLE_REPLY");
  }
  assert.ok(typeof PET_IDLE_ROTATION_MS === "number" && PET_IDLE_ROTATION_MS >= 30000,
    "PET_IDLE_ROTATION_MS must be >= 30000 ms");
}

function testPickNextIdleLineCyclesDeterministically() {
  const { PET_IDLE_LINES, pickNextIdleLine } = require(petRendererPath);
  const lines = [...PET_IDLE_LINES];
  const len = lines.length;
  const fakeState = { lastIdleLineIdx: -1 };
  const seen = [];
  // cycle through more than one full rotation to verify wrap
  for (let i = 0; i < len * 2; i++) {
    seen.push(pickNextIdleLine(fakeState));
  }
  // first pass should equal the array in order
  assert.deepEqual(seen.slice(0, len), lines);
  // second pass should repeat the same order
  assert.deepEqual(seen.slice(len), lines);
}

function testIdleRotationFiresAfterInterval() {
  const { PET_IDLE_LINES, PET_IDLE_LAUNCH_QUIET_MS, PET_IDLE_ROTATION_MS, PET_IDLE_REPLY, setPetIdleDefault } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  // Before rotation fires
  assert.equal(doc.getElementById("pet-bubble-response").textContent, PET_IDLE_REPLY);

  // Fire the rotation — must wait for launch quiet period (TASK-159)
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS);
  const afterRotation = doc.getElementById("pet-bubble-response").textContent;
  const idleLines = [...PET_IDLE_LINES];
  assert.ok(idleLines.includes(afterRotation),
    `After one rotation, response should be an idle line, got: "${afterRotation}"`);
  assert.notEqual(afterRotation, PET_IDLE_REPLY,
    "Rotated idle line should differ from PET_IDLE_REPLY");

  // Second rotation should advance to next line
  timerApi.advance(PET_IDLE_ROTATION_MS);
  const afterSecond = doc.getElementById("pet-bubble-response").textContent;
  assert.ok(idleLines.includes(afterSecond),
    `After second rotation, response should be an idle line, got: "${afterSecond}"`);
  assert.notEqual(afterSecond, afterRotation, "consecutive idle lines should differ");
}

function testIdleRotationSuppressedDuringRecentReply() {
  const {
    PET_IDLE_COOLDOWN_MS,
    PET_IDLE_ROTATION_MS,
    PET_RECENT_REPLY_VISIBLE_MS,
    PET_IDLE_LINES,
    PET_IDLE_REPLY,
    setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  renderPetSpeechUpdate(doc, { reply: "Real reply.", source: "llm_local" }, { timerApi });

  // Advance past rotation interval — should NOT show idle line
  timerApi.advance(PET_IDLE_ROTATION_MS + 1);
  assert.equal(doc.getElementById("pet-bubble-response").textContent, "Real reply.",
    "Idle rotation must not overwrite an active recent reply");

  // Advance past recent reply expiry — now idle_default
  timerApi.advance(PET_RECENT_REPLY_VISIBLE_MS);
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "idle_default");
  // After cooldown expires, idle line should appear (TASK-159: cooldown after activity)
  timerApi.advance(PET_IDLE_COOLDOWN_MS);
  const idleLines = [...PET_IDLE_LINES];
  const text = doc.getElementById("pet-bubble-response").textContent;
  assert.ok(idleLines.includes(text),
    `After recent reply expires and cooldown passes, idle rotation should resume; got: "${text}"`);
}

function testIdleRotationSuppressedDuringThinking() {
  const {
    PET_IDLE_ROTATION_MS,
    PET_IDLE_REPLY,
    PET_THINKING_SOURCE,
    setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });

  // Mirror thinking state (as Full App does before fetch)
  renderPetSpeechUpdate(doc,
    { reply: "\u543e\u3001\u543e\u624d\u4e0d\u662f\u5728\u8a8d\u771f\u601d\u8003\u5462\u2026\u2026", mood: "focused", source: PET_THINKING_SOURCE },
    { timerApi }
  );
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "thinking");

  // Advance past rotation interval — must NOT overwrite thinking bubble
  timerApi.advance(PET_IDLE_ROTATION_MS + 1);
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "thinking",
    "Idle rotation must not overwrite thinking state");
}

function testIdleRotationSuppressedDuringErrorState() {
  const {
    PET_IDLE_ROTATION_MS,
    setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  renderPetSpeechUpdate(doc,
    { reply: "", mood: "worried", source: "llm_local_error" },
    { timerApi }
  );
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "llm_local_error");

  // Advance past rotation interval — must NOT overwrite error state
  timerApi.advance(PET_IDLE_ROTATION_MS + 1);
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "llm_local_error",
    "Idle rotation must not overwrite an active error state");
}

function testIdleLineNotRecordedAsRecentReply() {
  const {
    PET_IDLE_LINES,
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_ROTATION_MS,
    PET_IDLE_REPLY,
    setPetIdleDefault,
    restorePetPresenceAfterShow,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });

  // Trigger an idle rotation — must wait for launch quiet period (TASK-159)
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS);
  const idleLines = [...PET_IDLE_LINES];
  const rotatedText = doc.getElementById("pet-bubble-response").textContent;
  assert.ok(idleLines.includes(rotatedText),
    `Expected an idle line after launch quiet + rotation, got: "${rotatedText}"`);

  // Simulate hide/show — restorePetPresenceAfterShow must NOT restore the idle line
  doc.getElementById("pet-bubble-response").textContent = "stale display text";
  restorePetPresenceAfterShow(doc, { timerApi });
  const restoredText = doc.getElementById("pet-bubble-response").textContent;
  assert.notEqual(restoredText, rotatedText,
    "restorePetPresenceAfterShow must not restore a stale idle rotation line");
  assert.equal(restoredText, PET_IDLE_REPLY,
    `restore must fall back to PET_IDLE_REPLY, got: "${restoredText}"`);
}

function testIdleRotationBubbleIsClean() {
  const {
    PET_IDLE_LINES,
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_ROTATION_MS,
    setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS);  // TASK-159: must wait for launch quiet

  const text = doc.getElementById("pet-bubble-response").textContent;
  assert.doesNotMatch(text, /source:|mood:|\{|\}|llm_local|pet_thinking|debug|provider/i,
    `Idle rotation bubble must not contain debug tokens: "${text}"`);
  // state must still be idle_default
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "idle_default",
    "Bubble state must stay idle_default during rotation");
  // details must stay hidden (no spurious details)
  assert.equal(doc.getElementById("pet-bubble-details").hidden, true,
    "Details must stay hidden during idle rotation");
}

function testIdleRotationDoesNotAffectDetailsDisclosure() {
  const {
    PET_IDLE_LINES,
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_ROTATION_MS,
    setPetIdleDefault,
    renderPetSpeechUpdate,
    toggleBubbleDetails,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  renderPetSpeechUpdate(doc, {
    reply: "Test reply.",
    mood: "happy",
    source: "llm_local",
    status: "provider_status",
    helper: "some helper text",
  }, { timerApi });

  toggleBubbleDetails(doc);
  assert.equal(doc.getElementById("pet-bubble-details").hidden, false,
    "Details should be open after toggle");

  // Simulate recent reply expiry returning to idle, then rotation
  // (details must not be affected by idle rotation because idle state shows no details)
  // Start fresh idle state
  setPetIdleDefault(doc, { timerApi });
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS);  // TASK-159: wait for launch quiet period

  const idleLines = [...PET_IDLE_LINES];
  const text = doc.getElementById("pet-bubble-response").textContent;
  assert.ok(idleLines.includes(text), `Expected idle line after launch quiet + rotation, got "${text}"`);
  assert.equal(doc.getElementById("pet-bubble-details").hidden, true,
    "Details panel must be hidden during idle rotation");
  assert.equal(doc.getElementById("pet-bubble").dataset.detailsOpen, "false",
    "Details must not be open during idle rotation");
}


// ---------------------------------------------------------------------------
// TASK-159 — Pet Idle Presence Timing / Noise Control
// ---------------------------------------------------------------------------

function testIdleTimingConstantsAreExported() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_COOLDOWN_MS,
    setIdleCooldown,
  } = require(petRendererPath);
  assert.ok(
    typeof PET_IDLE_LAUNCH_QUIET_MS === "number" && PET_IDLE_LAUNCH_QUIET_MS >= 60000,
    "PET_IDLE_LAUNCH_QUIET_MS must be a number >= 60000"
  );
  assert.ok(
    typeof PET_IDLE_COOLDOWN_MS === "number" && PET_IDLE_COOLDOWN_MS >= 30000,
    "PET_IDLE_COOLDOWN_MS must be a number >= 30000"
  );
  assert.equal(typeof setIdleCooldown, "function", "setIdleCooldown must be exported");
}

function testIdleLaunchQuietPeriodSuppressesFirstTick() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_REPLY,
    setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "Immediately after init, response must be PET_IDLE_REPLY"
  );

  // Advance just under the launch quiet period — no idle line should appear
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS - 1);
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    `Idle rotation must not fire before launch quiet period (${PET_IDLE_LAUNCH_QUIET_MS}ms)`
  );
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "idle_default");
}

function testIdleFirstTickFiresAfterLaunchQuiet() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_LINES,
    PET_IDLE_REPLY,
    setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS);

  const text = doc.getElementById("pet-bubble-response").textContent;
  const idleLines = [...PET_IDLE_LINES];
  assert.ok(
    idleLines.includes(text),
    `First idle line must appear after launch quiet period, got: "${text}"`
  );
  assert.notEqual(text, PET_IDLE_REPLY, "Rotated line must differ from PET_IDLE_REPLY");
}

function testIdleCooldownSuppressesRotationAfterActivity() {
  const {
    PET_IDLE_COOLDOWN_MS,
    PET_IDLE_REPLY,
    PET_RECENT_REPLY_VISIBLE_MS,
    setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  renderPetSpeechUpdate(doc, { reply: "Activity reply.", source: "llm_local" }, { timerApi });

  // Let recent reply expire — returns to idle with post-activity cooldown
  timerApi.advance(PET_RECENT_REPLY_VISIBLE_MS);
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "idle_default");

  // Advance just under cooldown — no idle rotation line should appear yet
  timerApi.advance(PET_IDLE_COOLDOWN_MS - 1);
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "Idle rotation must not fire before post-activity cooldown expires"
  );
}

function testIdleCooldownAllowsRotationAfterExpiry() {
  const {
    PET_IDLE_COOLDOWN_MS,
    PET_IDLE_LINES,
    PET_IDLE_REPLY,
    PET_RECENT_REPLY_VISIBLE_MS,
    setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  renderPetSpeechUpdate(doc, { reply: "Activity reply.", source: "llm_local" }, { timerApi });

  // Let recent reply expire — idle with cooldown
  timerApi.advance(PET_RECENT_REPLY_VISIBLE_MS);
  assert.equal(doc.getElementById("pet-bubble").dataset.state, "idle_default");

  // Advance exactly to cooldown expiry — rotation fires
  timerApi.advance(PET_IDLE_COOLDOWN_MS);
  const text = doc.getElementById("pet-bubble-response").textContent;
  const idleLines = [...PET_IDLE_LINES];
  assert.ok(
    idleLines.includes(text),
    `Idle rotation must fire once post-activity cooldown expires, got: "${text}"`
  );
  assert.notEqual(text, PET_IDLE_REPLY);
}

function testIdleRotationResumesAfterRestoreWithCooldown() {
  const {
    PET_IDLE_COOLDOWN_MS,
    PET_IDLE_LINES,
    PET_IDLE_REPLY,
    setPetIdleDefault,
    restorePetPresenceAfterShow,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  // Start idle, let launch quiet and some rotation pass, then simulate show from idle
  setPetIdleDefault(doc, { timerApi });
  timerApi.advance(PET_IDLE_COOLDOWN_MS * 3);  // expire launch quiet + some rotations

  // Simulate hide/show — restore returns to idle with a fresh cooldown
  restorePetPresenceAfterShow(doc, { timerApi });
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "After restore-to-idle, response must be PET_IDLE_REPLY immediately"
  );

  // Advance just under cooldown — no rotation yet
  timerApi.advance(PET_IDLE_COOLDOWN_MS - 1);
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "Idle rotation must not fire immediately after show/restore"
  );

  // Advance exactly to cooldown expiry — rotation fires
  timerApi.advance(1);
  const text = doc.getElementById("pet-bubble-response").textContent;
  const idleLines = [...PET_IDLE_LINES];
  assert.ok(
    idleLines.includes(text),
    `Idle rotation must resume after show cooldown expires, got: "${text}"`
  );
}

function testIdleConsecutiveRotationsNeverRepeatLine() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_ROTATION_MS,
    setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS);
  const first = doc.getElementById("pet-bubble-response").textContent;

  timerApi.advance(PET_IDLE_ROTATION_MS);
  const second = doc.getElementById("pet-bubble-response").textContent;

  timerApi.advance(PET_IDLE_ROTATION_MS);
  const third = doc.getElementById("pet-bubble-response").textContent;

  assert.notEqual(first, second, "Consecutive idle rotations must not repeat the same line (1→2)");
  assert.notEqual(second, third, "Consecutive idle rotations must not repeat the same line (2→3)");
}


// ── TASK-160: Quiet Mode / Idle Presence Toggle ──────────────────────────────

function testQuietModeApiIsExported() {
  const { getPetQuietMode, setPetQuietMode, PET_IDLE_COOLDOWN_MS } = require(petRendererPath);
  assert.equal(typeof getPetQuietMode, "function", "getPetQuietMode must be exported");
  assert.equal(typeof setPetQuietMode, "function", "setPetQuietMode must be exported");
  assert.ok(
    typeof PET_IDLE_COOLDOWN_MS === "number" && PET_IDLE_COOLDOWN_MS >= 30000,
    "PET_IDLE_COOLDOWN_MS must be exported and ≥ 30000"
  );
}

function testQuietModeDefaultsOff() {
  const { getPetQuietMode, setPetIdleDefault } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();
  setPetIdleDefault(doc, { timerApi });
  assert.equal(getPetQuietMode(doc), false, "Quiet Mode must default to OFF after setPetIdleDefault");
}

function testQuietModeOnSuppressesIdleRotation() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_ROTATION_MS,
    PET_IDLE_REPLY,
    getPetQuietMode,
    setPetQuietMode,
    setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  setPetQuietMode(doc, true, timerApi);
  assert.equal(getPetQuietMode(doc), true, "Quiet Mode must be ON after setPetQuietMode(true)");

  // Advance well past launch quiet + several rotation intervals
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS + PET_IDLE_ROTATION_MS * 5);

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(bubble.dataset.state, "collapsed", "Bubble must be collapsed while Quiet Mode is ON");  // TASK-160 fix
  assert.equal(bubble.hidden, true, "Bubble must be hidden while Quiet Mode is ON");  // TASK-160 fix
}

function testQuietModeOnCancelsExistingTimer() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_ROTATION_MS,
    PET_IDLE_REPLY,
    setPetQuietMode,
    setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  // Advance to just before the first tick fires (timer is pending)
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS - 1);
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "No idle line yet (timer still pending)"
  );

  // Turn Quiet Mode ON — should cancel the pending timer
  setPetQuietMode(doc, true, timerApi);

  // Advance far past where the tick would have fired
  timerApi.advance(PET_IDLE_ROTATION_MS * 10);
  const bubble2 = doc.getElementById("pet-bubble");
  assert.equal(bubble2.dataset.state, "collapsed", "Bubble must be collapsed after Quiet Mode ON cancels timer");  // TASK-160 fix
  assert.equal(bubble2.hidden, true, "Bubble must be hidden after Quiet Mode ON cancels timer");  // TASK-160 fix
}

function testQuietModeOffResumesRotationAfterCooldown() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_COOLDOWN_MS,
    PET_IDLE_ROTATION_MS,
    PET_IDLE_LINES,
    PET_IDLE_REPLY,
    getPetQuietMode,
    setPetQuietMode,
    setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  // Let first idle line fire
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS);
  const firstLine = doc.getElementById("pet-bubble-response").textContent;
  assert.ok([...PET_IDLE_LINES].includes(firstLine), "First idle line must be from PET_IDLE_LINES");

  // Turn Quiet Mode ON — stops next timer and collapses idle bubble (TASK-160 fix)
  setPetQuietMode(doc, true, timerApi);
  timerApi.advance(PET_IDLE_ROTATION_MS * 5);
  const bubbleR = doc.getElementById("pet-bubble");
  assert.equal(bubbleR.dataset.state, "collapsed", "Bubble must be collapsed while Quiet Mode is ON");  // TASK-160 fix
  assert.equal(bubbleR.hidden, true, "Bubble must be hidden while Quiet Mode is ON");  // TASK-160 fix

  // Turn Quiet Mode OFF — restores idle_default and restarts rotation with cooldown delay (TASK-160 fix)
  setPetQuietMode(doc, false, timerApi);
  assert.equal(getPetQuietMode(doc), false, "Quiet Mode must be OFF after setPetQuietMode(false)");
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "Quiet Mode OFF must restore idle_default static text"  // TASK-160 fix
  );

  // Just before cooldown expires — no rotation yet, still showing idle_default
  timerApi.advance(PET_IDLE_COOLDOWN_MS - 1);
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "Rotation must not fire before cooldown expires after Quiet Mode OFF"  // TASK-160 fix
  );

  // Exactly at cooldown expiry — rotation fires
  timerApi.advance(1);
  const newLine = doc.getElementById("pet-bubble-response").textContent;
  assert.ok(
    [...PET_IDLE_LINES].includes(newLine),
    `Rotation must resume after cooldown, got: "${newLine}"`
  );
  assert.notEqual(newLine, firstLine, "Rotation must advance to a new idle line");
}

function testQuietModeOnDoesNotSuppressThinkingBubble() {
  const {
    PET_THINKING_SOURCE,
    getPetQuietMode,
    setPetQuietMode,
    setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  setPetQuietMode(doc, true, timerApi);
  assert.equal(getPetQuietMode(doc), true, "Quiet Mode must be ON");

  renderPetSpeechUpdate(
    doc,
    { reply: "思考中…", mood: "focused", source: PET_THINKING_SOURCE },
    { timerApi }
  );

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(
    bubble.dataset.state,
    "thinking",
    "Thinking bubble must still appear with Quiet Mode ON"
  );
}

function testQuietModeOnDoesNotSuppressFinalReply() {
  const {
    getPetQuietMode,
    setPetQuietMode,
    setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  setPetQuietMode(doc, true, timerApi);
  assert.equal(getPetQuietMode(doc), true, "Quiet Mode must be ON");

  const replyText = "好，我知道了。";
  renderPetSpeechUpdate(
    doc,
    { reply: replyText, mood: "neutral", source: "llm_local" },
    { timerApi }
  );

  const bubble = doc.getElementById("pet-bubble");
  const responseEl = doc.getElementById("pet-bubble-response");
  assert.ok(
    bubble.dataset.state === "speaking" || bubble.dataset.state === "success",
    `Final reply must still show while Quiet Mode is ON, got state: "${bubble.dataset.state}"`
  );
  assert.equal(
    responseEl.textContent,
    replyText,
    "Final reply text must appear in bubble with Quiet Mode ON"
  );
}

function testQuietModeOnDoesNotSuppressErrorFallback() {
  const {
    getPetQuietMode,
    setPetQuietMode,
    setPetIdleDefault,
    setBubbleState,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  setPetQuietMode(doc, true, timerApi);
  assert.equal(getPetQuietMode(doc), true, "Quiet Mode must be ON");

  setBubbleState(doc, "llm_local_error");

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(
    bubble.dataset.state,
    "llm_local_error",
    "Error fallback must still appear with Quiet Mode ON"
  );
}

function testQuietModeUnknownValueFallsBackToOff() {
  const { getPetQuietMode, setPetQuietMode, setPetIdleDefault } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();
  setPetIdleDefault(doc, { timerApi });

  for (const badValue of [null, undefined, 0, 1, "yes", "true", [], {}]) {
    setPetQuietMode(doc, badValue, timerApi);
    assert.equal(
      getPetQuietMode(doc),
      false,
      `Quiet Mode must fall back to OFF for non-true value: ${JSON.stringify(badValue)}`
    );
  }
}

function testQuietModeOnCollapsesIdleBubble() {
  // TASK-160 fix: Quiet Mode ON must collapse the idle bubble, not show fixed idle text
  const { getPetQuietMode, setPetQuietMode, setPetIdleDefault, PET_IDLE_REPLY } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  const bubble = doc.getElementById("pet-bubble");
  assert.equal(bubble.dataset.state, "idle_default", "Starts in idle_default");
  assert.equal(bubble.hidden, false, "Bubble visible in idle_default");
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "idle_default shows PET_IDLE_REPLY text"
  );

  // Turn Quiet Mode ON — must collapse the bubble
  setPetQuietMode(doc, true, timerApi);
  assert.equal(getPetQuietMode(doc), true, "Quiet Mode is ON");
  assert.equal(bubble.dataset.state, "collapsed", "Quiet Mode ON must collapse idle bubble");
  assert.equal(bubble.hidden, true, "Bubble must be hidden with Quiet Mode ON");

  // Turn Quiet Mode OFF — must restore idle_default
  setPetQuietMode(doc, false, timerApi);
  assert.equal(getPetQuietMode(doc), false, "Quiet Mode is OFF");
  assert.equal(bubble.dataset.state, "idle_default", "Quiet Mode OFF must restore idle_default");
  assert.equal(bubble.hidden, false, "Bubble must be visible again with Quiet Mode OFF");
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "Quiet Mode OFF must restore PET_IDLE_REPLY text"
  );
}

function testQuietModeHideShowWithQuietOnNoRotation() {
  const {
    PET_IDLE_LAUNCH_QUIET_MS,
    PET_IDLE_COOLDOWN_MS,
    getPetQuietMode,
    setPetQuietMode,
    setPetIdleDefault,
    restorePetPresenceAfterShow,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  setPetQuietMode(doc, true, timerApi);
  assert.equal(getPetQuietMode(doc), true, "Quiet Mode must be ON");

  // Simulate hide/show: restorePetPresenceAfterShow must keep bubble collapsed when quiet ON
  restorePetPresenceAfterShow(doc, { timerApi });

  // Advance far past cooldown and rotation intervals
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS + PET_IDLE_COOLDOWN_MS + 1);

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(bubble.dataset.state, "collapsed", "Bubble must stay collapsed after show/restore with Quiet Mode ON");  // TASK-160 fix
  assert.equal(bubble.hidden, true, "Bubble must stay hidden after show/restore with Quiet Mode ON");  // TASK-160 fix
}


// ── TASK-162: Quiet Mode Persistence ──────────────────────────────────────────

function testQuietModePersistPreAppliedTrueCollapsesBubble() {
  // Simulates: main.js passes ?quietMode=true, renderer applies it before idle init
  const { getPetQuietMode, setPetQuietMode, setPetIdleDefault } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  // Apply persisted quiet=true BEFORE first idle render (mirrors URL-param startup path)
  setPetQuietMode(doc, true, timerApi);
  assert.equal(getPetQuietMode(doc), true, "quietMode must be ON after pre-apply");

  setPetIdleDefault(doc, { timerApi });

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(bubble.dataset.state, "collapsed", "Pre-applied quietMode=true must keep bubble collapsed on startup");
  assert.equal(bubble.hidden, true, "Bubble must be hidden when quietMode pre-applied as true");
}

function testQuietModePersistPreAppliedFalseShowsIdleDefault() {
  // Simulates: no stored preference / stored false → idle_default on startup
  const { getPetQuietMode, setPetIdleDefault, PET_IDLE_REPLY } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  // No pre-apply — quietMode stays at default false
  assert.equal(getPetQuietMode(doc), false, "quietMode must default to OFF");

  setPetIdleDefault(doc, { timerApi });

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(bubble.dataset.state, "idle_default", "No stored pref must show idle_default");
  assert.equal(bubble.hidden, false, "Bubble must be visible with no stored pref");
  assert.equal(
    doc.getElementById("pet-bubble-response").textContent,
    PET_IDLE_REPLY,
    "idle_default must show PET_IDLE_REPLY with no stored pref"
  );
}

function testQuietModePersistCorruptValueFallsBackToOff() {
  // Simulates: corrupt stored value → fail safe to OFF
  const { getPetQuietMode, setPetQuietMode, setPetIdleDefault } = require(petRendererPath);

  for (const badValue of [null, undefined, "true", 1, "yes", {}, []]) {
    const doc = createPetBubbleStateDocument();
    const timerApi = new FakeTimerApi();

    setPetQuietMode(doc, badValue, timerApi);
    assert.equal(
      getPetQuietMode(doc),
      false,
      "Corrupt stored value must fall back to OFF: " + JSON.stringify(badValue)
    );

    // Must show idle_default, not crash
    setPetIdleDefault(doc, { timerApi });
    const bubble = doc.getElementById("pet-bubble");
    assert.equal(
      bubble.dataset.state,
      "idle_default",
      "Corrupt value must leave bubble at idle_default: " + JSON.stringify(badValue)
    );
  }
}

function testQuietModePersistPreAppliedTrueNoRotationAfterCooldown() {
  // Simulates: restored quietMode=true → idle rotation stays suppressed (TASK-159 non-regression)
  const {
    getPetQuietMode, setPetQuietMode, setPetIdleDefault,
    PET_IDLE_LAUNCH_QUIET_MS, PET_IDLE_COOLDOWN_MS, PET_IDLE_ROTATION_MS,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });

  assert.equal(getPetQuietMode(doc), true, "quietMode must stay ON");

  // Advance far past all cooldown + rotation windows
  timerApi.advance(PET_IDLE_LAUNCH_QUIET_MS + PET_IDLE_COOLDOWN_MS + PET_IDLE_ROTATION_MS * 5);

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(
    bubble.dataset.state,
    "collapsed",
    "Bubble must stay collapsed with persisted quietMode=true after cooldown + rotation intervals"
  );
}

function testQuietModePersistPreAppliedTrueDoesNotSuppressChatReply() {
  // Simulates: restored quietMode=true → chat reply still appears
  const {
    getPetQuietMode, setPetQuietMode, setPetIdleDefault, renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });
  assert.equal(getPetQuietMode(doc), true, "quietMode ON");

  const replyText = "好的，這是回覆。";
  renderPetSpeechUpdate(
    doc,
    { reply: replyText, mood: "neutral", source: "llm_local" },
    { timerApi }
  );

  const bubble = doc.getElementById("pet-bubble");
  const responseEl = doc.getElementById("pet-bubble-response");
  assert.ok(
    bubble.dataset.state === "speaking" || bubble.dataset.state === "success",
    "Chat reply must show despite persisted quietMode=true, got: " + bubble.dataset.state
  );
  assert.equal(responseEl.textContent, replyText, "Reply text must appear with persisted quietMode=true");
}

function testQuietModePersistPreAppliedTrueDoesNotSuppressThinking() {
  // Simulates: restored quietMode=true → TASK-157 thinking bubble still shows
  const {
    PET_THINKING_SOURCE, getPetQuietMode, setPetQuietMode, setPetIdleDefault,
    renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });
  assert.equal(getPetQuietMode(doc), true, "quietMode ON");

  renderPetSpeechUpdate(
    doc,
    { reply: "思考中…", mood: "focused", source: PET_THINKING_SOURCE },
    { timerApi }
  );

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(
    bubble.dataset.state,
    "thinking",
    "TASK-157 thinking bubble must still appear with persisted quietMode=true"
  );
}


// ── TASK-166C Quiet Mode regression tests ────────────────────────────────────

// Regression: isIdleRotationEligible must return false when quietMode ON
function testQuietModeEligibilityReturnsFalseWhenQuiet() {
  const {
    isIdleRotationEligible,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const presenceState = { quietMode: true, recentReply: null, handoffActive: false };
  // quietMode ON → not eligible regardless of other fields
  assert.equal(
    isIdleRotationEligible(doc, presenceState),
    false,
    "isIdleRotationEligible must return false when quietMode=true"
  );
}

// Regression: idle timer firing while quietMode ON must not change bubble from collapsed
function testQuietModeIdleTimerFiresButBubbleStaysCollapsed() {
  const {
    getPetQuietMode, setPetQuietMode, setPetIdleDefault,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });

  const bubbleAfterInit = doc.getElementById("pet-bubble");
  assert.equal(bubbleAfterInit.dataset.state, "collapsed", "bubble collapsed at init with quietMode ON");

  // Fast-forward well past both launch quiet period and rotation interval
  timerApi.advance(3 * 60 * 1000);  // 3 minutes

  const bubbleAfterTimer = doc.getElementById("pet-bubble");
  assert.equal(
    bubbleAfterTimer.dataset.state,
    "collapsed",
    "bubble must remain collapsed after idle timers fire with quietMode ON"
  );
  assert.equal(getPetQuietMode(doc), true, "quietMode must still be ON");
}

// Regression: after recentReply expires with quietMode ON, bubble must stay collapsed
function testQuietModeRecentReplyExpiryKeepsBubbleCollapsed() {
  const {
    getPetQuietMode, setPetQuietMode, setPetIdleDefault, renderPetSpeechUpdate,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });

  // Simulate a real reply arriving (quietMode ON should not suppress replies)
  renderPetSpeechUpdate(doc, { reply: "測試回覆", mood: "neutral" }, { timerApi });
  const bubbleAfterReply = doc.getElementById("pet-bubble");
  assert.ok(
    bubbleAfterReply.dataset.state !== "collapsed",
    "chat reply must show even with quietMode ON"
  );

  // Advance past PET_RECENT_REPLY_VISIBLE_MS (90 s) to expire recent reply
  timerApi.advance(95 * 1000);

  const bubbleAfterExpiry = doc.getElementById("pet-bubble");
  assert.equal(
    bubbleAfterExpiry.dataset.state,
    "collapsed",
    "bubble must collapse back after recentReply expires when quietMode ON"
  );
  assert.equal(getPetQuietMode(doc), true, "quietMode still ON after expiry");
}

// Regression: restorePetPresence with quietMode ON must keep bubble collapsed
function testQuietModeRestoreKeepsBubbleCollapsed() {
  const {
    getPetQuietMode, setPetQuietMode, setPetIdleDefault, restorePetPresenceAfterShow,
  } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });

  // Simulate a window show/restore event while quietMode ON
  restorePetPresenceAfterShow(doc, { timerApi });

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(
    bubble.dataset.state,
    "collapsed",
    "restorePetPresence must keep bubble collapsed when quietMode ON"
  );
  assert.equal(getPetQuietMode(doc), true, "quietMode still ON after restore");
}


// ── TASK-166C Quiet Mode regression fix 2: data-quiet-mode attribute + hint ─────

// setQuietMode ON must set root.dataset.quietMode = "true"
function testQuietModeOnSetsRootDataAttribute() {
  const { setPetQuietMode, getPetQuietMode, setPetIdleDefault } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  setPetQuietMode(doc, true, timerApi);

  const root = doc.getElementById("pet-mode-root");
  assert.equal(
    root.dataset.quietMode,
    "true",
    "root.dataset.quietMode must be 'true' when Quiet Mode is ON"
  );
  assert.equal(getPetQuietMode(doc), true, "getPetQuietMode must return true");
}

// setQuietMode OFF must set root.dataset.quietMode = "false"
function testQuietModeOffClearsRootDataAttribute() {
  const { setPetQuietMode, setPetIdleDefault } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetIdleDefault(doc, { timerApi });
  setPetQuietMode(doc, true, timerApi);
  setPetQuietMode(doc, false, timerApi);

  const root = doc.getElementById("pet-mode-root");
  assert.equal(
    root.dataset.quietMode,
    "false",
    "root.dataset.quietMode must be 'false' when Quiet Mode is OFF"
  );
}

// startup with URL-persisted quietMode=true must set data-quiet-mode attribute
function testQuietModeStartupAttributeSetByPreApply() {
  const { setPetQuietMode, setPetIdleDefault } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  // Simulate initializePetMode ordering: quietMode applied, THEN idle init
  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });

  const root = doc.getElementById("pet-mode-root");
  const bubble = doc.getElementById("pet-bubble");
  assert.equal(root.dataset.quietMode, "true", "data-quiet-mode must be 'true' after startup with pre-applied quiet");
  assert.equal(bubble.dataset.state, "collapsed", "bubble must be collapsed after startup with quietMode=true");
}

// toggleDetailsFromMenu must not show idle_default while Quiet Mode is ON
function testQuietModeToggleDetailsMenuGuardWhenQuiet() {
  const { setPetQuietMode, setPetIdleDefault, toggleDetailsFromMenu } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  setPetQuietMode(doc, true, timerApi);
  setPetIdleDefault(doc, { timerApi });

  const bubble = doc.getElementById("pet-bubble");
  assert.equal(bubble.dataset.state, "collapsed", "pre-condition: bubble collapsed with quiet ON");

  const result = toggleDetailsFromMenu(doc);
  assert.equal(result, false, "toggleDetailsFromMenu must return false (no-op) while Quiet Mode ON");
  assert.equal(
    bubble.dataset.state,
    "collapsed",
    "bubble must remain collapsed after toggleDetailsFromMenu with Quiet Mode ON"
  );
}

// setQuietMode ON while bubble is already collapsed (hint visible) → data attribute hides it
function testQuietModeOnWhileCollapsedSetsAttribute() {
  const { setPetQuietMode, setPetIdleDefault, setBubbleState } = require(petRendererPath);
  const doc = createPetBubbleStateDocument();
  const timerApi = new FakeTimerApi();

  // Start with bubble explicitly collapsed (as happens after hide window / after reply fades)
  setPetIdleDefault(doc, { timerApi });
  setBubbleState(doc, "collapsed");

  const root = doc.getElementById("pet-mode-root");
  const bubble = doc.getElementById("pet-bubble");
  assert.equal(bubble.dataset.state, "collapsed", "pre-condition: bubble is collapsed");
  // quiet mode was NOT on — data attribute should not be "true" yet
  assert.notEqual(root.dataset.quietMode, "true", "pre-condition: quiet mode not yet on");

  // NOW turn quiet mode on
  setPetQuietMode(doc, true, timerApi);
  assert.equal(root.dataset.quietMode, "true", "data-quiet-mode must become 'true' after turning Quiet Mode ON");
  assert.equal(bubble.dataset.state, "collapsed", "bubble must stay collapsed");
}


// ── TASK-166B: Scale preset renderer tests ──────────────────────────────────

async function testScaleNormalizeFallsBackToMedium() {
  const { normalizeScale } = require(petRendererPath);
  assert.equal(normalizeScale("small"),   "small");
  assert.equal(normalizeScale("medium"),  "medium");
  assert.equal(normalizeScale("large"),   "large");
  assert.equal(normalizeScale(undefined), "medium");
  assert.equal(normalizeScale(null),      "medium");
  assert.equal(normalizeScale(""),        "medium");
  assert.equal(normalizeScale("XL"),      "medium");
  assert.equal(normalizeScale(42),        "medium");
}

async function testSetActiveScaleButtonUpdatesDataset() {
  const { setActiveScaleButton } = require(petRendererPath);

  // Build plain-object DOM stubs — no makeDocument(), no createElement()
  const nodes = { "pet-mode-root": { dataset: {} } };
  for (const s of ["small", "medium", "large"]) {
    nodes["pet-menu-scale-" + s] = {
      _ariaPressed: s === "medium" ? "true" : "false",
      setAttribute(attr, val) { if (attr === "aria-pressed") this._ariaPressed = val; },
      getAttribute(attr) { return attr === "aria-pressed" ? this._ariaPressed : null; },
    };
  }
  const patchedDoc = { getElementById: (id) => nodes[id] || null };

  setActiveScaleButton(patchedDoc, "small");
  assert.equal(nodes["pet-mode-root"].dataset.scale, "small", "data-scale should be small");
  assert.equal(nodes["pet-menu-scale-small"]._ariaPressed,  "true",  "small btn aria-pressed");
  assert.equal(nodes["pet-menu-scale-medium"]._ariaPressed, "false", "medium btn aria-pressed");
  assert.equal(nodes["pet-menu-scale-large"]._ariaPressed,  "false", "large btn aria-pressed");

  setActiveScaleButton(patchedDoc, "large");
  assert.equal(nodes["pet-mode-root"].dataset.scale, "large");
  assert.equal(nodes["pet-menu-scale-large"]._ariaPressed,  "true");
  assert.equal(nodes["pet-menu-scale-small"]._ariaPressed,  "false");
}

async function testSetActiveScaleButtonUnknownFallsBackToMedium() {
  const { setActiveScaleButton } = require(petRendererPath);
  const nodes = { "pet-mode-root": { dataset: {} } };
  for (const s of ["small", "medium", "large"]) {
    nodes["pet-menu-scale-" + s] = {
      _ap: "false",
      setAttribute(a, v) { if (a === "aria-pressed") this._ap = v; },
    };
  }
  const doc = { getElementById: (id) => nodes[id] || null };
  setActiveScaleButton(doc, "INVALID");
  assert.equal(nodes["pet-mode-root"].dataset.scale, "medium");
  assert.equal(nodes["pet-menu-scale-medium"]._ap, "true");
  assert.equal(nodes["pet-menu-scale-small"]._ap,  "false");
}

async function testApplyScalePresetCallsApiSetScale() {
  const { applyScalePreset } = require(petRendererPath);
  let calledWith = null;
  const fakeApi = { setScale: (v) => { calledWith = v; return Promise.resolve({ ok: true }); } };
  const doc = {
    getElementById: () => ({ dataset: {}, setAttribute() {} }),
  };
  applyScalePreset(doc, "large", fakeApi);
  assert.equal(calledWith, "large", "setScale should be called with 'large'");
  applyScalePreset(doc, "UNKNOWN", fakeApi);
  assert.equal(calledWith, "medium", "setScale should fall back to 'medium'");
}

async function testScaleUrlParamAppliedOnInit() {
  const { initializePetMode } = require(petRendererPath);

  // Full FakeDocument matching the element set initializePetMode touches
  const dom = new FakeDocument([
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
    "pet-menu-scale-small",
    "pet-menu-scale-medium",
    "pet-menu-scale-large",
  ]);
  const root = dom.getElementById("pet-mode-root");

  // Simulate ?scale=small URL param
  const origWindow = global.window;
  global.window = {
    location: { search: "?quietMode=false&scale=small" },
    dragonPet: null,
  };
  global.URLSearchParams = URLSearchParams;

  initializePetMode(dom);

  global.window = origWindow;

  // data-scale should be set to "small" on root
  assert.equal(root.dataset.scale, "small", "data-scale should be 'small' from URL param");
}

async function testScaleExportsPresent() {
  const mod = require(petRendererPath);
  assert.ok(Array.isArray(mod.PET_VALID_SCALES), "PET_VALID_SCALES should be exported");
  assert.ok(mod.PET_VALID_SCALES.includes("small"),  "PET_VALID_SCALES includes small");
  assert.ok(mod.PET_VALID_SCALES.includes("medium"), "PET_VALID_SCALES includes medium");
  assert.ok(mod.PET_VALID_SCALES.includes("large"),  "PET_VALID_SCALES includes large");
  assert.equal(typeof mod.normalizeScale,       "function");
  assert.equal(typeof mod.setActiveScaleButton, "function");
  assert.equal(typeof mod.applyScalePreset,     "function");
}


// ── TASK-166C: Bubble placement / tail polish ─────────────────────────────

function testBubbleTailCssOnlyNoAssets() {
  const css = readText(petCssPath);
  // Tail exists as CSS pseudo-element; no image assets
  assertIncludes(css, ".pet-speech-bubble::after", "pet.css");
  assertRegex(css, /\.pet-speech-bubble::after[\s\S]*content:\s*""/, "pet.css");
  assertNotIncludes(css, "background-image", "pet.css");
  assertNotIncludes(css, "url(", "pet.css");
}

function testBubbleTailHiddenWhenCollapsed() {
  const css = readText(petCssPath);
  // Collapsed data-state: tail hidden via explicit rule
  assertRegex(css, /\.pet-bubble\[data-state="collapsed"\]::after[\s\S]*display:\s*none/, "pet.css");
  // Hidden attribute: tail hidden via existing rule
  assertRegex(css, /\.pet-bubble\[hidden\]::after[\s\S]*display:\s*none/, "pet.css");
}

function testBubbleTailScaleSmall() {
  const css = readText(petCssPath);
  // Small preset: 10×10 tail with -5px top offset
  assertRegex(css, /\[data-scale="small"\] \.pet-speech-bubble::after[\s\S]*width:\s*10px/, "pet.css");
  assertRegex(css, /\[data-scale="small"\] \.pet-speech-bubble::after[\s\S]*height:\s*10px/, "pet.css");
  assertRegex(css, /\[data-scale="small"\] \.pet-speech-bubble::after[\s\S]*top:\s*-5px/, "pet.css");
}

function testBubbleTailScaleLarge() {
  const css = readText(petCssPath);
  // Large preset: 18×18 tail with -9px top offset
  assertRegex(css, /\[data-scale="large"\] \.pet-speech-bubble::after[\s\S]*width:\s*18px/, "pet.css");
  assertRegex(css, /\[data-scale="large"\] \.pet-speech-bubble::after[\s\S]*height:\s*18px/, "pet.css");
  assertRegex(css, /\[data-scale="large"\] \.pet-speech-bubble::after[\s\S]*top:\s*-9px/, "pet.css");
}

function testBubbleMaxHeightScalePresets() {
  const css = readText(petCssPath);
  // Small: 96px bubble max-height (fits 300px window)
  assertRegex(
    css,
    /\[data-scale="small"\] \.pet-bubble\[data-state\]:not\(\[data-state="collapsed"\]\)[\s\S]*max-height:\s*96px/,
    "pet.css"
  );
  // Large: 148px bubble max-height (uses 500px window depth)
  assertRegex(
    css,
    /\[data-scale="large"\] \.pet-bubble\[data-state\]:not\(\[data-state="collapsed"\]\)[\s\S]*max-height:\s*148px/,
    "pet.css"
  );
}

function testBubbleTailVisibleOverflowFix() {
  const css = readText(petCssPath);
  // Root-cause fix: .pet-bubble base rule must use overflow: visible so the
  // ::after tail at top:-8px is not clipped by the bubble's own overflow box.
  assertRegex(
    css,
    /\.pet-bubble\s*\{[^}]*overflow:\s*visible/,
    "pet.css — .pet-bubble base rule must have overflow: visible (TASK-166C tail-fix)"
  );
  // Inner content elements must still self-constrain their overflow
  assertRegex(css, /\.pet-bubble-response[\s\S]*overflow-y:\s*auto/, "pet.css");
  assertRegex(css, /\.pet-bubble-details[\s\S]*overflow-y:\s*auto/, "pet.css");
  // Tail has box-shadow for contrast on light/dark/complex wallpapers
  assertRegex(css, /\.pet-speech-bubble::after[\s\S]*box-shadow:/, "pet.css");
  // Tail border is visible (opacity >= 0.2)
  assertRegex(
    css,
    /\.pet-speech-bubble::after[\s\S]*border-left:\s*1px solid rgba\(72,\s*45,\s*34,\s*0\.2/,
    "pet.css — tail border should be at least 0.2 opacity"
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
    testPetMoodExpressionManualSmokeHookUsesRealSpeechPath,
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
    testPetThinkingSourceMapsToThinkingState,
    testPetThinkingRenderShowsReplyInBubble,
    testPetThinkingRenderBubbleIsClean,
    testPetThinkingSourceConstantIsExported,
    // TASK-158
    testPetIdleLineConstantsAreExported,
    testPickNextIdleLineCyclesDeterministically,
    testIdleRotationFiresAfterInterval,
    testIdleRotationSuppressedDuringRecentReply,
    testIdleRotationSuppressedDuringThinking,
    testIdleRotationSuppressedDuringErrorState,
    testIdleLineNotRecordedAsRecentReply,
    testIdleRotationBubbleIsClean,
    testIdleRotationDoesNotAffectDetailsDisclosure,
    // TASK-159
    testIdleTimingConstantsAreExported,
    testIdleLaunchQuietPeriodSuppressesFirstTick,
    testIdleFirstTickFiresAfterLaunchQuiet,
    testIdleCooldownSuppressesRotationAfterActivity,
    testIdleCooldownAllowsRotationAfterExpiry,
    testIdleRotationResumesAfterRestoreWithCooldown,
    testIdleConsecutiveRotationsNeverRepeatLine,
    // TASK-160
    testQuietModeApiIsExported,
    testQuietModeDefaultsOff,
    testQuietModeOnSuppressesIdleRotation,
    testQuietModeOnCancelsExistingTimer,
    testQuietModeOffResumesRotationAfterCooldown,
    testQuietModeOnDoesNotSuppressThinkingBubble,
    testQuietModeOnDoesNotSuppressFinalReply,
    testQuietModeOnDoesNotSuppressErrorFallback,
    testQuietModeUnknownValueFallsBackToOff,
    testQuietModeOnCollapsesIdleBubble,
    testQuietModeHideShowWithQuietOnNoRotation,
    // TASK-162
    testQuietModePersistPreAppliedTrueCollapsesBubble,
    testQuietModePersistPreAppliedFalseShowsIdleDefault,
    testQuietModePersistCorruptValueFallsBackToOff,
    testQuietModePersistPreAppliedTrueNoRotationAfterCooldown,
    testQuietModePersistPreAppliedTrueDoesNotSuppressChatReply,
    testQuietModePersistPreAppliedTrueDoesNotSuppressThinking,
    // TASK-166C quiet mode regression fix 2: data-quiet-mode attribute
    testQuietModeOnSetsRootDataAttribute,
    testQuietModeOffClearsRootDataAttribute,
    testQuietModeStartupAttributeSetByPreApply,
    testQuietModeToggleDetailsMenuGuardWhenQuiet,
    testQuietModeOnWhileCollapsedSetsAttribute,
    // TASK-166C quiet mode regression fix 1: eligibility + timer guards
    testQuietModeEligibilityReturnsFalseWhenQuiet,
    testQuietModeIdleTimerFiresButBubbleStaysCollapsed,
    testQuietModeRecentReplyExpiryKeepsBubbleCollapsed,
    testQuietModeRestoreKeepsBubbleCollapsed,
    // TASK-166B
    testScaleNormalizeFallsBackToMedium,
    testSetActiveScaleButtonUpdatesDataset,
    testSetActiveScaleButtonUnknownFallsBackToMedium,
    testApplyScalePresetCallsApiSetScale,
    testScaleUrlParamAppliedOnInit,
    testScaleExportsPresent,
    // TASK-166C
    testBubbleTailCssOnlyNoAssets,
    testBubbleTailHiddenWhenCollapsed,
    testBubbleTailScaleSmall,
    testBubbleTailScaleLarge,
    testBubbleMaxHeightScalePresets,
    testBubbleTailVisibleOverflowFix,
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
