const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const desktopRoot = path.resolve(__dirname, "..");
const rendererPath = path.join(desktopRoot, "src", "renderer", "renderer.js");
const indexPath = path.join(desktopRoot, "src", "renderer", "index.html");

class FakeResponse {
  constructor(status, data) {
    this.status = status;
    this.ok = status >= 200 && status < 300;
    this._data = data;
  }

  async json() {
    return this._data;
  }
}

class FakeElement {
  constructor(tagName = "div", id = "") {
    this.tagName = tagName.toUpperCase();
    this.id = id;
    this.children = [];
    this.parentNode = null;
    this.style = {};
    this.listeners = {};
    this.className = "";
    this.textContent = "";
    this.value = "";
    this.checked = false;
    this.disabled = false;
    this.placeholder = "";
    this.title = "";
    this.scrollTop = 0;
    this.scrollHeight = 0;
    this.rows = 0;
    this.options = [];
    // TASK-083: support innerHTML and data attributes for pet expression checks
    this._innerHTML = "";
    this._attributes = {};
    // TASK-098: support element.dataset.xxx assignments (used for data-bool badges)
    this.dataset = {};
  }

  set innerHTML(value) {
    this._innerHTML = String(value);
    this.children = [];
    this.lastChild = null;
  }

  get innerHTML() {
    return this._innerHTML;
  }

  setAttribute(name, value) {
    this._attributes[name] = String(value);
  }

  getAttribute(name) {
    return Object.prototype.hasOwnProperty.call(this._attributes, name)
      ? this._attributes[name]
      : null;
  }

  appendChild(child) {
    this._innerHTML = "";
    child.parentNode = this;
    this.children.push(child);
    this.lastChild = child;
    this.scrollHeight = this.children.length;
    return child;
  }

  replaceChildren(...children) {
    this.children = [];
    this.lastChild = null;
    for (const child of children) {
      this.appendChild(child);
    }
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

  click() {
    this.dispatchEvent({
      type: "click",
      preventDefault() {},
    });
  }

  focus() {
    this.focused = true;
  }

  remove() {
    if (!this.parentNode) return;
    this.parentNode.children = this.parentNode.children.filter((child) => child !== this);
    this.parentNode.lastChild = this.parentNode.children.at(-1) || null;
    this.parentNode = null;
  }
}

// TASK-086: FakeImage — simulates browser Image() probe for PNG asset fallback tests.
// availableImages is closed over per loadRenderer() call so each test is isolated.
// set src() schedules onload (if path in availableImages) or onerror asynchronously,
// matching real browser behaviour where image callbacks are never synchronous.
class FakeImageBase {
  constructor() {
    this.onload = null;
    this.onerror = null;
    this._src = "";
  }

  get src() {
    return this._src;
  }
}

class FakeDocument {
  constructor() {
    this.elements = new Map();
    // TASK-108: support document.addEventListener (used by idle timer pointerdown guard)
    this._docListeners = {};
  }

  // TASK-108: document-level event listener registration (idle timer guard)
  addEventListener(type, fn) {
    if (!this._docListeners[type]) this._docListeners[type] = [];
    this._docListeners[type].push(fn);
  }

  getElementById(id) {
    if (!this.elements.has(id)) {
      const element = new FakeElement("div", id);
      if (id === "provider-settings-provider") {
        element.options = [
          { value: "mock", textContent: "mock" },
          { value: "anthropic", textContent: "anthropic" },
          { value: "ollama", textContent: "ollama - local, no key" },
        ];
        element.value = "mock";
      }
      if (id === "audit-limit") element.value = "20";
      if (id === "audit-offset") element.value = "0";
      if (id === "provider-fallback-to-mock") element.checked = true;
      this.elements.set(id, element);
    }
    return this.elements.get(id);
  }

  createElement(tagName) {
    return new FakeElement(tagName);
  }
}

function defaultProviderSettings(overrides = {}) {
  return {
    provider: "ollama",
    model: "qwen3:8b",
    real_provider_enabled: true,
    llm_chat_enabled: true,
    fallback_to_mock: false,
    key_status: "not_required",
    resolved_provider: "ollama",
    last_test_status: "not_tested",
    usage_summary: {
      request_count: 0,
      source_counts: {},
      provider_counts: {},
      model_counts: {},
      estimated_input_tokens: 0,
      estimated_output_tokens: 0,
      estimated_total_tokens: 0,
      fallback_count: 0,
      memory_used_count: 0,
      error_counts: {},
    },
    ...overrides,
  };
}

function usageFor(source, overrides = {}) {
  return {
    request_count: 1,
    source_counts: { [source]: 1 },
    provider_counts: { ollama: 1 },
    model_counts: { "qwen3:8b": 1 },
    estimated_input_tokens: 1,
    estimated_output_tokens: 1,
    estimated_total_tokens: 2,
    fallback_count: 0,
    memory_used_count: 0,
    error_counts: {},
    ...overrides,
  };
}

function createFetchStub(state) {
  return async function fetchStub(url, options = {}) {
    state.calls.push({
      url: String(url),
      method: options.method || "GET",
      body: options.body || null,
    });

    const target = String(url);
    if (target.endsWith("/health")) {
      return new FakeResponse(200, { status: "ok" });
    }
    if (target.endsWith("/memory")) {
      return new FakeResponse(200, []);
    }
    if (target.includes("/memory/context-preview")) {
      return new FakeResponse(200, {
        count: 0,
        source: "manual_memory_preview",
        context: "Memory Context Preview:\n\nNo active memories.",
      });
    }
    if (target.includes("/memory/audit")) {
      return new FakeResponse(200, {
        items: [],
        count: 0,
        limit: 20,
        offset: 0,
      });
    }
    if (target.endsWith("/provider/settings") && (options.method || "GET") === "GET") {
      return new FakeResponse(200, state.providerSettings);
    }
    if (target.endsWith("/provider/settings") && options.method === "PATCH") {
      state.providerSettings = {
        ...state.providerSettings,
        ...JSON.parse(options.body),
        key_status: "not_required",
        resolved_provider: "ollama",
      };
      return new FakeResponse(200, state.providerSettings);
    }
    if (target.endsWith("/provider/settings/test")) {
      return new FakeResponse(200, {
        status: "success",
        provider: "ollama",
        model: "qwen3:8b",
        source: "llm_local",
        safe_message: "Local Ollama connection successful.",
        error_category: null,
        usage_estimate: { input_tokens: 1, output_tokens: 1, total_tokens: 2 },
      });
    }
    if (target.endsWith("/chat")) {
      if (state.pauseChat) {
        await new Promise((resolve) => {
          state.resolveChat = resolve;
        });
      }
      if (state.chatMode === "network_error") {
        throw new TypeError("fetch failed");
      }
      if (state.chatMode === "provider_timeout") {
        return new FakeResponse(504, { detail: "provider_timeout" });
      }
      if (state.chatMode === "local_error") {
        state.providerSettings = {
          ...state.providerSettings,
          usage_summary: usageFor("llm_local_error", {
            error_counts: { provider_timeout: 1 },
          }),
        };
        return new FakeResponse(200, {
          reply: "Provider failed safely.",
          mood: "focused",
          source: "llm_local_error",
        });
      }
      if (state.chatMode === "mock_fallback") {
        state.providerSettings = {
          ...state.providerSettings,
          fallback_to_mock: true,
          usage_summary: usageFor("mock", {
            fallback_count: 1,
            error_counts: { provider_timeout: 1 },
          }),
        };
        return new FakeResponse(200, {
          reply: "Mock fallback reply.",
          mood: "focused",
          source: "mock",
        });
      }

      if (state.chatMode === "unknown_mood") {
        state.providerSettings = {
          ...state.providerSettings,
          usage_summary: usageFor("llm_local"),
        };
        return new FakeResponse(200, {
          reply: "Some reply.",
          mood: "legendary",   // unknown mood — not in PET_EXPRESSIONS
          source: "llm_local",
        });
      }

      state.providerSettings = {
        ...state.providerSettings,
        usage_summary: usageFor("llm_local"),
      };
      return new FakeResponse(200, {
        reply: "Hmph, local dragon reply.",
        mood: "focused",
        source: "llm_local",
      });
    }
    return new FakeResponse(404, { detail: "not found" });
  };
}

async function settle() {
  for (let i = 0; i < 8; i += 1) {
    await new Promise((resolve) => setTimeout(resolve, 0));
  }
}

async function loadRenderer(options = {}) {
  const document = new FakeDocument();

  // TASK-086: per-test set of PNG paths that "exist" for FakeImage probes.
  // Default is empty — all probes fire onerror, SVG fallback stays active,
  // and all pre-TASK-086 tests remain unaffected.
  const availableImages = new Set(options.availableImages || []);

  // TASK-108: fake setInterval — stores callbacks without firing them.
  // Tests call sandbox.idleTick() directly to avoid real-time waits.
  const intervalCallbacks = [];

  const state = {
    calls: [],
    chatMode: options.chatMode || "success",
    pauseChat: Boolean(options.pauseChat),
    resolveChat: null,
    providerSettings: defaultProviderSettings(options.providerSettings || {}),
    availableImages,
    intervalCallbacks,  // exposed for verification if needed
  };

  // FakeImage closes over availableImages so each test run is isolated.
  class FakeImage extends FakeImageBase {
    set src(val) {
      this._src = val;
      const cb = availableImages.has(val) ? this.onload : this.onerror;
      if (typeof cb === "function") setTimeout(cb, 0);
    }
  }

  const sandbox = {
    console,
    document,
    window: {
      location: {
        search: "?backend=http%3A%2F%2Flocalhost%3A8000",
      },
      confirm: () => true,
      // TASK-108: idle timer registers window.addEventListener("focus", ...) — stub it
      addEventListener() {},
    },
    URLSearchParams,
    fetch: createFetchStub(state),
    setTimeout,
    clearTimeout,
    // TASK-108: fake setInterval/clearInterval — stores callbacks, never fires them.
    // Tests invoke sandbox.idleTick() directly.
    setInterval(fn, ms) {
      intervalCallbacks.push({ fn, ms });
      return intervalCallbacks.length; // fake numeric ID
    },
    clearInterval() {},
    Image: FakeImage,
    Event: class Event {
      constructor(type, init = {}) {
        this.type = type;
        this.bubbles = Boolean(init.bubbles);
      }
    },
  };

  const code = fs.readFileSync(rendererPath, "utf8");
  vm.runInNewContext(code, sandbox, { filename: rendererPath });
  await settle();
  return { document, state, sandbox };
}

function messageTexts(chatArea) {
  return chatArea.children.map((message) =>
    message.children.map((child) => child.textContent).join("\n")
  );
}

function textOf(document, id) {
  return document.getElementById(id).textContent;
}

async function sendChat(document, message = "hello") {
  document.getElementById("message-input").value = message;
  document.getElementById("send-btn").click();
  await settle();
}

async function testChatSendCallsBackendAndRendersReply() {
  const { document, state } = await loadRenderer();

  await sendChat(document, "local chat smoke");

  const chatCalls = state.calls.filter((call) => call.url.endsWith("/chat"));
  assert.equal(chatCalls.length, 1);
  assert.equal(chatCalls[0].method, "POST");
  assert.deepEqual(JSON.parse(chatCalls[0].body), {
    message: "local chat smoke",
    use_memory: false,
  });

  const rendered = messageTexts(document.getElementById("chat-area")).join("\n");
  assert.match(rendered, /You/);
  assert.match(rendered, /local chat smoke/);
  assert.match(rendered, /Hmph, local dragon reply/);
}

async function testSuccessfulLocalChatUpdatesMoodAndSourceStatus() {
  const { document } = await loadRenderer();

  await sendChat(document);

  assert.equal(textOf(document, "mood-label"), "focused");
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local");
  assert.match(textOf(document, "chat-runtime-status"), /source=llm_local/);

  const usageText = document
    .getElementById("provider-usage-summary")
    .children
    .map((child) => child.textContent)
    .join("\n");
  assert.match(usageText, /llm_local: 1/);
}

async function testLoadingColdStartStatusIsVisible() {
  const { document, state } = await loadRenderer({ pauseChat: true });

  document.getElementById("message-input").value = "slow local chat";
  document.getElementById("send-btn").click();
  await new Promise((resolve) => setTimeout(resolve, 0));

  assert.equal(document.getElementById("send-btn").disabled, true);
  assert.equal(textOf(document, "send-btn"), "Sending...");
  assert.equal(textOf(document, "chat-source-status"), "source: pending");
  assert.match(textOf(document, "chat-runtime-status"), /first response can take longer/i);

  state.resolveChat();
  await settle();
  assert.equal(document.getElementById("send-btn").disabled, false);
}

async function testEnterKeySendsChat() {
  const { document, state } = await loadRenderer();
  const input = document.getElementById("message-input");

  input.value = "send from enter";
  input.dispatchEvent({
    type: "keydown",
    key: "Enter",
    shiftKey: false,
    preventDefault() {
      this.prevented = true;
    },
  });
  await settle();

  const chatCalls = state.calls.filter((call) => call.url.endsWith("/chat"));
  assert.equal(chatCalls.length, 1);
  assert.equal(JSON.parse(chatCalls[0].body).message, "send from enter");
}

async function testBackendOfflineShowsSafeUiError() {
  const { document } = await loadRenderer({ chatMode: "network_error" });

  await sendChat(document, "offline");

  const rendered = messageTexts(document.getElementById("chat-area")).join("\n");
  assert.match(rendered, /Cannot reach backend/);
  assert.equal(textOf(document, "chat-source-status"), "source: backend_offline");
  assert.equal(document.getElementById("send-btn").disabled, false);
}

async function testProviderTimeoutShowsSafeUiError() {
  const { document } = await loadRenderer({ chatMode: "provider_timeout" });

  await sendChat(document, "timeout");

  const rendered = messageTexts(document.getElementById("chat-area")).join("\n");
  assert.match(rendered, /Provider timed out/);
  assert.doesNotMatch(rendered, /RAW_PROVIDER_BODY/);
  assert.equal(textOf(document, "chat-source-status"), "source: error");
}

async function testLocalProviderFailureWithoutFallbackIsVisible() {
  const { document } = await loadRenderer({ chatMode: "local_error" });

  await sendChat(document, "local fail");

  assert.equal(textOf(document, "chat-source-status"), "source: llm_local_error");
  assert.match(textOf(document, "chat-runtime-status"), /local provider failed safely/i);
  assert.match(textOf(document, "chat-runtime-status"), /model may still be loading/i);
}

async function testMockFallbackStateIsDistinguishable() {
  const { document } = await loadRenderer({
    chatMode: "mock_fallback",
    providerSettings: { fallback_to_mock: true },
  });

  await sendChat(document, "fallback");

  assert.equal(textOf(document, "chat-source-status"), "source: mock");
  assert.match(textOf(document, "chat-runtime-status"), /fallback_to_mock is enabled/i);

  const usageText = document
    .getElementById("provider-usage-summary")
    .children
    .map((child) => child.textContent)
    .join("\n");
  assert.match(usageText, /Fallbacks\s+1/);
  assert.match(usageText, /provider_timeout: 1/);
}

async function testProviderSettingsStatusAndTestConnectionSuccess() {
  const { document, state } = await loadRenderer();

  assert.equal(textOf(document, "provider-current-provider"), "ollama");
  assert.equal(textOf(document, "provider-current-model"), "qwen3:8b");
  assert.equal(textOf(document, "provider-key-status"), "not_required");
  assert.equal(textOf(document, "provider-resolved-provider"), "ollama");
  assert.equal(textOf(document, "provider-real-enabled-status"), "true");
  assert.equal(textOf(document, "provider-llm-chat-enabled-status"), "true");
  assert.equal(textOf(document, "provider-fallback-status"), "false");

  document.getElementById("test-provider-connection-btn").click();
  await settle();

  const testCalls = state.calls.filter((call) => call.url.endsWith("/provider/settings/test"));
  const patchCalls = state.calls.filter(
    (call) => call.url.endsWith("/provider/settings") && call.method === "PATCH"
  );
  assert.equal(testCalls.length, 1);
  assert.equal(patchCalls.length, 0);
  assert.equal(state.providerSettings.model, "qwen3:8b");
  assert.equal(state.providerSettings.fallback_to_mock, false);
  assert.match(textOf(document, "provider-test-msg"), /Local Ollama connection successful/);
  assert.match(textOf(document, "provider-test-msg"), /source: llm_local/);
}

async function testSaveProviderSettingsOmitsBlankModelAndKeepsFallbackFalse() {
  const { document, state } = await loadRenderer();

  document.getElementById("provider-settings-model").value = "";
  document.getElementById("provider-fallback-to-mock").checked = false;
  document.getElementById("provider-settings-form").dispatchEvent({
    type: "submit",
    preventDefault() {},
  });
  await settle();

  const patchCalls = state.calls.filter(
    (call) => call.url.endsWith("/provider/settings") && call.method === "PATCH"
  );
  assert.equal(patchCalls.length, 1);
  const body = JSON.parse(patchCalls[0].body);
  assert.equal(Object.prototype.hasOwnProperty.call(body, "model"), false);
  assert.equal(body.fallback_to_mock, false);
  assert.equal(state.providerSettings.model, "qwen3:8b");
  assert.equal(state.providerSettings.fallback_to_mock, false);
}

// ---------------------------------------------------------------------------
// TASK-083: Pet expression tests
// ---------------------------------------------------------------------------

async function testSuccessfulChatWithFocusedMoodSetsFocusedExpression() {
  const { document } = await loadRenderer();

  await sendChat(document, "focus test");

  // mood label updated from response
  assert.equal(textOf(document, "mood-label"), "focused");
  // pet expression set to focused (known mood)
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "focused");
  // innerHTML contains SVG content
  assert.match(document.getElementById("pet-face").innerHTML, /<svg/);
}

async function testPendingExpressionSetBeforeResponse() {
  const { document, state } = await loadRenderer({ pauseChat: true });

  document.getElementById("message-input").value = "pending test";
  document.getElementById("send-btn").click();
  // Advance one tick — startup settled but chat not yet resolved
  await new Promise((resolve) => setTimeout(resolve, 0));

  // While waiting, pet must show pending
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "pending");
  assert.match(document.getElementById("pet-face").innerHTML, /<svg/);

  state.resolveChat();
  await settle();
  // After response arrives, mood updates to focused (from mock response)
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "focused");
}

async function testUnknownMoodFallsBackToNeutralExpression() {
  const { document } = await loadRenderer({ chatMode: "unknown_mood" });

  await sendChat(document, "unknown mood test");

  // mood label shows raw backend mood value
  assert.equal(textOf(document, "mood-label"), "legendary");
  // expression falls back to neutral (unknown mood → safe default)
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "neutral");
}

async function testBackendOfflineSetsOfflineExpression() {
  const { document } = await loadRenderer({ chatMode: "network_error" });

  await sendChat(document, "offline test");

  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "offline");
  assert.match(document.getElementById("pet-face").innerHTML, /<svg/);
  // source status also shows offline
  assert.equal(textOf(document, "chat-source-status"), "source: backend_offline");
}

async function testLocalErrorSetsErrorExpression() {
  const { document } = await loadRenderer({ chatMode: "local_error" });

  await sendChat(document, "error test");

  // llm_local_error source must override mood expression to error
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "error");
  assert.match(document.getElementById("pet-face").innerHTML, /<svg/);
  // source status still shows llm_local_error
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local_error");
}

async function testMockFallbackExpressionFollowsMoodNotSource() {
  const { document } = await loadRenderer({
    chatMode: "mock_fallback",
    providerSettings: { fallback_to_mock: true },
  });

  await sendChat(document, "fallback expression test");

  // source=mock, mood=focused — source status shows mock (not llm_local)
  assert.equal(textOf(document, "chat-source-status"), "source: mock");
  // mock fallback is not an error source, so expression follows the mood
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "focused");
}

async function testSourceStatusRemainsVisibleAlongsidePetExpression() {
  const { document } = await loadRenderer();

  await sendChat(document, "source visibility test");

  // Both pet expression and source status must be visible simultaneously
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "focused");
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local");
  assert.equal(textOf(document, "mood-label"), "focused");
}

async function testProviderTimeoutSetsErrorExpression() {
  const { document } = await loadRenderer({ chatMode: "provider_timeout" });

  await sendChat(document, "timeout expression test");

  // Backend returns 504, which is a non-ok error response
  const petMood = document.getElementById("pet-face").getAttribute("data-mood");
  assert.equal(petMood, "error");
}

// ---------------------------------------------------------------------------
// TASK-086: Image asset fallback tests
// ---------------------------------------------------------------------------
async function testNeutralMoodUsesPngImageWhenAvailable() {
  // TASK-109: startup now ends with setPetExpression("proud"), so we explicitly
  // call setMood("neutral") after startup to test the neutral PNG load path.
  // With neutral PNG marked available, FakeImage fires onload → petFace gets <img>.
  const NEUTRAL_PATH = "assets/pet/christina/expressions/christina_neutral.png";
  const { document, sandbox } = await loadRenderer({
    availableImages: [NEUTRAL_PATH],
  });

  // Explicitly set neutral mood to trigger the neutral PNG probe.
  sandbox.setMood("neutral");
  await settle();

  const petFace = document.getElementById("pet-face");
  assert.equal(petFace.getAttribute("data-mood"), "neutral");
  // After settle(), onload has fired and SVG was replaced by <img>
  assert.equal(petFace.children.length, 1);
  assert.equal(petFace.children[0].tagName, "IMG");
  assert.match(petFace.children[0].src, /christina_neutral\.png/);
  // innerHTML cleared when <img> was appended
  assert.equal(petFace.innerHTML, "");
}

async function testIntegratedMoodPngAssetsLoadWhenAvailable() {
  const moods = ["neutral", "focused", "happy", "proud", "annoyed"];
  const paths = moods.map((mood) => `assets/pet/christina/expressions/christina_${mood}.png`);
  const { document, sandbox } = await loadRenderer({
    availableImages: paths,
  });

  for (const mood of moods) {
    sandbox.setMood(mood);
    await settle();

    const petFace = document.getElementById("pet-face");
    assert.equal(petFace.getAttribute("data-mood"), mood);
    assert.equal(petFace.children.length, 1);
    assert.equal(petFace.children[0].tagName, "IMG");
    assert.match(petFace.children[0].src, new RegExp(`christina_${mood}\\.png`));
    assert.equal(petFace.innerHTML, "");
  }
}

async function testPngLoadFailureFallsBackToSvg() {
  // No PNG available (default) → FakeImage fires onerror → SVG placeholder stays.
  // TASK-109: startup ends with setPetExpression("proud"), so data-mood is now "proud".
  const { document } = await loadRenderer();

  const petFace = document.getElementById("pet-face");
  assert.equal(petFace.getAttribute("data-mood"), "proud",
    "startup greeting sets proud expression; PNG fallback must still show SVG");
  // SVG string remains in innerHTML; no IMG child was added (no proud PNG available)
  assert.match(petFace.innerHTML, /<svg/);
  assert.equal(petFace.children.length, 0);
}

async function testFocusedMoodFallsBackToSvgWhenNoPng() {
  // chat returns mood=focused; no PNG available → SVG fallback for focused.
  const { document } = await loadRenderer();

  await sendChat(document, "focused fallback test");

  const petFace = document.getElementById("pet-face");
  assert.equal(petFace.getAttribute("data-mood"), "focused");
  assert.match(petFace.innerHTML, /<svg/);
  assert.equal(petFace.children.length, 0);
}

async function testMissingExpressionPngsStillFallBackToSvg() {
  const availableImages = [
    "assets/pet/christina/expressions/christina_neutral.png",
    "assets/pet/christina/expressions/christina_focused.png",
    "assets/pet/christina/expressions/christina_happy.png",
    "assets/pet/christina/expressions/christina_proud.png",
    "assets/pet/christina/expressions/christina_annoyed.png",
  ];
  const missingMoods = ["worried", "sleepy", "pending", "error", "offline"];
  const { document, sandbox } = await loadRenderer({ availableImages });

  for (const mood of missingMoods) {
    sandbox.setMood(mood);
    await settle();

    const petFace = document.getElementById("pet-face");
    assert.equal(petFace.getAttribute("data-mood"), mood);
    assert.match(petFace.innerHTML, /<svg/);
    assert.equal(petFace.children.length, 0);
  }
}

async function testImageAssetDoesNotBreakSourceOrMoodLabel() {
  // With neutral PNG available, source status and mood label must still update normally.
  const NEUTRAL_PATH = "assets/pet/christina/expressions/christina_neutral.png";
  const { document } = await loadRenderer({
    availableImages: [NEUTRAL_PATH],
  });

  await sendChat(document, "image + label test");

  // After a focused-response chat: focused PNG not available → SVG for focused.
  // Source label and mood label must still update correctly.
  assert.equal(textOf(document, "mood-label"), "focused");
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local");
  // pet-face updated to focused mood
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "focused");
}

// TASK-098: UI polish tests

async function testChatAreaAccumulatesMultipleMessages() {
  // Verify that sending multiple messages grows the chat area correctly
  // (tests scrollback accumulation — pixel scroll is layout-engine-dependent,
  //  but DOM accumulation must be correct for scroll to be meaningful).
  // Note: uses children.filter() because FakeElement does not implement querySelectorAll.
  const { document } = await loadRenderer({ chatMode: "mock" });

  await sendChat(document, "first message");
  await sendChat(document, "second message");
  await sendChat(document, "third message");

  const chatArea = document.getElementById("chat-area");
  const userMsgs = chatArea.children.filter(
    (el) => el.className && el.className.includes("user")
  );
  assert.equal(userMsgs.length, 3, "Three user messages accumulated in chat area");

  const petMsgs = chatArea.children.filter(
    (el) => el.className && el.className.includes("pet")
  );
  // 1 greeting on startup + 3 replies
  assert.ok(petMsgs.length >= 3, "At least three pet replies accumulated");
}

async function testFriendlySourceLabelShownAfterLocalChat() {
  // Verify TASK-098: user-facing friendly label is shown alongside the technical source pill
  const { document } = await loadRenderer();  // default: llm_local mode

  await sendChat(document);

  // Technical source pill: unchanged format required by smoke tests
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local");
  // TASK-098: friendly label displayed in provider status pill
  assert.equal(textOf(document, "chat-provider-status"), "Local Ollama");
}

function testRendererDoesNotContainDirectOllamaUrl() {
  const haystack = [
    fs.readFileSync(rendererPath, "utf8"),
    fs.readFileSync(indexPath, "utf8"),
  ].join("\n");
  assert.equal(haystack.includes("localhost:11434"), false);
  assert.equal(haystack.includes("127.0.0.1:11434"), false);
  assert.equal(/\b11434\b/.test(haystack), false);
}

// ---------------------------------------------------------------------------
// TASK-108: Idle State UI Behavior tests
// ---------------------------------------------------------------------------

async function testIdleShortThresholdSetsNeutralExpressionAndHint() {
  // After 3 min of inactivity, idleTick() should set neutral expression and hint.
  const { document, state, sandbox } = await loadRenderer();

  // Advance fake clock by 3 min + 1 ms to cross the short threshold
  sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
  await settle();

  const petFace = document.getElementById("pet-face");
  assert.equal(petFace.getAttribute("data-mood"), "neutral",
    "short idle: expression must be neutral");
  const hint = document.getElementById("pet-display-hint").textContent;
  assert.match(hint, /吾在這裡/, "short idle: hint must contain waiting text");
}

async function testIdleLongThresholdSetsSleepyExpressionAndHint() {
  // After 10 min of inactivity, idleTick() should set sleepy expression and hint.
  const { document, state, sandbox } = await loadRenderer();

  // Advance fake clock by 10 min + 1 ms to cross the long threshold
  sandbox.idleTick(Date.now() + 10 * 60 * 1000 + 1);
  await settle();

  const petFace = document.getElementById("pet-face");
  assert.equal(petFace.getAttribute("data-mood"), "sleepy",
    "long idle: expression must be sleepy");
  const hint = document.getElementById("pet-display-hint").textContent;
  assert.match(hint, /哼/, "long idle: hint must contain sleepy tsundere text");
}

async function testUserInteractionResetsIdleState() {
  // Enter short_idle, then resetActivity() should restore expression and show return hint.
  const { document, state, sandbox } = await loadRenderer();

  // Enter short_idle state
  sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
  await settle();
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "neutral",
    "must be neutral before reset");

  // User interacts — resetActivity() resets the clock
  sandbox.resetActivity();
  await settle();

  // After reset, hint shows return greeting
  const hint = document.getElementById("pet-display-hint").textContent;
  assert.match(hint, /終於回來/, "return from idle: hint must show welcome-back text");
  // Expression should be restored (not sleepy)
  const mood = document.getElementById("pet-face").getAttribute("data-mood");
  assert.notEqual(mood, "sleepy", "return from idle: expression must not be sleepy");
}

async function testIdleTickDoesNotCallChatEndpoint() {
  // idleTick() must never trigger a /chat fetch call.
  const { state, sandbox } = await loadRenderer();
  const chatCallsBefore = state.calls.filter((c) => c.url.endsWith("/chat")).length;

  sandbox.idleTick(Date.now() + 10 * 60 * 1000 + 1);
  await settle();

  const chatCallsAfter = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  assert.equal(chatCallsAfter, chatCallsBefore,
    "idleTick must never call /chat — no new chat requests");
}

async function testIdleTickNotFiredDuringActiveChatRequest() {
  // idleTick() called while isSending must not override the pending/loading expression.
  const { document, state, sandbox } = await loadRenderer({ pauseChat: true });

  // Trigger a chat request (sets isSending=true, expression=pending)
  document.getElementById("message-input").value = "idle during send";
  document.getElementById("send-btn").click();
  await new Promise((resolve) => setTimeout(resolve, 0));

  // Verify we are in loading state
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "pending",
    "must show pending while awaiting response");

  // Advance time past long threshold and tick — must be a no-op since isSending=true
  sandbox.idleTick(Date.now() + 10 * 60 * 1000 + 1);
  await new Promise((resolve) => setTimeout(resolve, 0));

  // Expression must still be pending (not sleepy)
  assert.equal(document.getElementById("pet-face").getAttribute("data-mood"), "pending",
    "idleTick during send must not override pending expression");

  // Resolve the chat
  state.resolveChat();
  await settle();
}

async function testSourceStatusStillVisibleAfterIdleThenChat() {
  // After idle -> resetActivity -> send chat, source status must update normally.
  const { document, state, sandbox } = await loadRenderer();

  // Enter idle state
  sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
  await settle();

  // User returns and sends a chat message
  sandbox.resetActivity();
  await sendChat(document, "post-idle chat");

  // Source status must reflect the chat response, not idle state
  assert.equal(
    document.getElementById("chat-source-status").textContent,
    "source: llm_local",
    "source status must update correctly after returning from idle"
  );
  assert.equal(document.getElementById("mood-label").textContent, "focused",
    "mood label must update from chat response after idle");
}

// ---------------------------------------------------------------------------
// TASK-109: Startup greeting tests
// ---------------------------------------------------------------------------

async function testStartupGreetingHintIsVisible() {
  // After a successful startup, pet-display-hint must show the greeting text.
  // No /chat is called; this is a purely static UI update.
  const { document } = await loadRenderer();

  const hint = document.getElementById("pet-display-hint").textContent;
  assert.match(
    hint,
    /哼，汝終於把吾叫醒/,
    "startup greeting hint must contain character greeting text"
  );
}

async function testStartupGreetingExpressionIsProud() {
  // After startup the pet face must show the "proud" expression.
  const { document } = await loadRenderer();

  const mood = document.getElementById("pet-face").getAttribute("data-mood");
  assert.equal(mood, "proud", "startup greeting expression must be proud");
}

async function testStartupGreetingDoesNotCallChat() {
  // Startup greeting must NEVER trigger a /chat fetch.
  const { state } = await loadRenderer();

  const chatCalls = state.calls.filter((c) => c.url.endsWith("/chat"));
  assert.equal(
    chatCalls.length,
    0,
    "startup greeting must not call /chat — no automatic chat requests"
  );
}

async function testIdleStillWorksAfterStartupGreeting() {
  // After startup greeting, idle timer must still fire normally.
  // 3-min idle → neutral expression + idle hint (overrides greeting).
  const { document, sandbox } = await loadRenderer();

  // Verify greeting is showing first
  const greetingHint = document.getElementById("pet-display-hint").textContent;
  assert.match(greetingHint, /哼，汝終於把吾叫醒/, "greeting must be visible before idle");

  // Advance past short idle threshold
  sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
  await settle();

  const idleHint = document.getElementById("pet-display-hint").textContent;
  assert.match(
    idleHint,
    /吾在這裡/,
    "idle hint must override startup greeting after 3 min"
  );
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "neutral",
    "idle must set neutral expression even after startup greeting"
  );
}

// ---------------------------------------------------------------------------
// TASK-110: Return-from-away greeting tests
// ---------------------------------------------------------------------------

async function testReturnFromLongIdleShowsReturnGreeting() {
  // After ≥ 15 min idle, the first resetActivity() call must show the
  // long-away return greeting ("哼，汝終於回來了。吾才沒有一直等汝。")
  // and set annoyed expression. No /chat is called.
  const { document, sandbox } = await loadRenderer();

  // Advance past long-away threshold (15 min + 1 ms)
  sandbox.idleTick(Date.now() + 15 * 60 * 1000 + 1);
  await settle();

  // Verify long_idle state was entered and awayGreetingEligible was set
  // (idleTick crosses 10-min first, then 15-min in one shot here)
  sandbox.resetActivity();
  await settle();

  const hint = document.getElementById("pet-display-hint").textContent;
  assert.match(hint, /吾才沒有/, "long-away return: hint must contain 吾才沒有");
  assert.match(hint, /終於回來了/, "long-away return: hint must contain 終於回來了");

  const mood = document.getElementById("pet-face").getAttribute("data-mood");
  assert.equal(mood, "annoyed", "long-away return: expression must be annoyed");
}

async function testReturnGreetingDoesNotCallChat() {
  // resetActivity() after long idle must NEVER trigger a /chat fetch.
  const { state, sandbox } = await loadRenderer();

  sandbox.idleTick(Date.now() + 15 * 60 * 1000 + 1);
  await settle();

  const chatCallsBefore = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  sandbox.resetActivity();
  await settle();

  const chatCallsAfter = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  assert.equal(
    chatCallsAfter,
    chatCallsBefore,
    "return greeting must not call /chat — no new chat requests"
  );
}

async function testReturnGreetingOnlyFiresOncePerAwaySession() {
  // Within the same away session, the return greeting must appear only once.
  // Subsequent resetActivity() calls (user keeps interacting) must not repeat it.
  const { document, sandbox } = await loadRenderer();

  sandbox.idleTick(Date.now() + 15 * 60 * 1000 + 1);
  await settle();

  // First return — shows greeting
  sandbox.resetActivity();
  await settle();
  const firstHint = document.getElementById("pet-display-hint").textContent;
  assert.match(firstHint, /吾才沒有/, "first return must show long-away greeting");

  // Second interaction immediately after — must NOT repeat the return greeting
  // (wasIdle=false now, awayGreetingFired=true)
  sandbox.resetActivity();
  await settle();
  const secondHint = document.getElementById("pet-display-hint").textContent;
  // Hint should still be the greeting from the first call (no override for short idle)
  assert.match(secondHint, /吾才沒有/,
    "second resetActivity must not clear the greeting (hint unchanged, no wasIdle)");
  // Critically: the second call must NOT have changed the expression to a different mood
  const mood = document.getElementById("pet-face").getAttribute("data-mood");
  assert.equal(mood, "annoyed", "expression must stay annoyed after second reset");
}

async function testShortIdleDoesNotTriggerReturnGreeting() {
  // Only ≥ 15 min idle triggers the long-away greeting.
  // 3-min idle should give the regular short-return hint, not the away greeting.
  const { document, sandbox } = await loadRenderer();

  // Cross only the short_idle threshold (3 min)
  sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
  await settle();

  sandbox.resetActivity();
  await settle();

  const hint = document.getElementById("pet-display-hint").textContent;
  assert.doesNotMatch(
    hint,
    /吾才沒有/,
    "short idle must not show long-away return greeting"
  );
  assert.match(hint, /終於回來了嗎/, "short idle return must show regular return hint");
}

async function testReturnGreetingResetAfterReenteringLongIdle() {
  // After a return greeting fires, the user must be able to get another one
  // on the NEXT long-idle → return cycle.
  const { document, sandbox } = await loadRenderer();

  // ── First away cycle ──
  sandbox.idleTick(Date.now() + 15 * 60 * 1000 + 1);
  await settle();
  sandbox.resetActivity(); // greeting fires, awayGreetingFired=true
  await settle();
  const firstHint = document.getElementById("pet-display-hint").textContent;
  assert.match(firstHint, /吾才沒有/, "first away cycle must show greeting");

  // ── User is now active (resetActivity set lastActivityTime ≈ Date.now()) ──
  // ── Second away cycle: idle again for 15+ min ──
  // idleTick at 10 min → enters long_idle, resets awayGreetingFired=false
  sandbox.idleTick(Date.now() + 10 * 60 * 1000 + 1);
  await settle();
  // idleTick at 15 min → marks awayGreetingEligible=true
  sandbox.idleTick(Date.now() + 15 * 60 * 1000 + 1);
  await settle();

  sandbox.resetActivity(); // should fire greeting again for this new away session
  await settle();
  const secondHint = document.getElementById("pet-display-hint").textContent;
  assert.match(secondHint, /吾才沒有/,
    "second away cycle must also show greeting after re-entering long_idle");
}

// ---------------------------------------------------------------------------
// TASK-111: Companion hint lock tests
// ---------------------------------------------------------------------------

async function testStartupGreetingLocksHintFromIdleTransition() {
  // idleTick must not override the startup greeting while the lock is active.
  // We extend the lock to 10 min via sandbox.lockCompanionHint so it outlasts
  // the synthetic 3-min idle tick.
  const { document, sandbox } = await loadRenderer();

  // Verify startup greeting is showing
  const greetingHint = document.getElementById("pet-display-hint").textContent;
  assert.match(greetingHint, /哼，汝終於把吾叫醒/, "startup greeting must be visible");

  // Extend the lock so it spans the synthetic tick timestamp
  sandbox.lockCompanionHint(10 * 60 * 1000); // 10 min >> 3-min idle threshold

  // Fire idleTick at 3-min threshold — would normally switch hint to idle text
  sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
  await settle();

  // Hint must still show the startup greeting (lock protected it)
  const hintAfter = document.getElementById("pet-display-hint").textContent;
  assert.match(
    hintAfter,
    /哼，汝終於把吾叫醒/,
    "hint lock must protect startup greeting from idle transition"
  );
  // Expression must also be unchanged
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "proud",
    "hint lock must protect proud expression from idle transition"
  );
}

async function testGreetingLockExpiresAllowingIdleHint() {
  // Once the 8-second lock expires, idleTick should update hint and expression normally.
  // A synthetic timestamp past the lock expiry (8 s) + idle threshold (3 min) must work.
  const { document, sandbox } = await loadRenderer();

  // Verify startup greeting and lock are in place
  const HINT_LOCK_MS = 8 * 1000;
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /哼，汝終於把吾叫醒/,
    "startup greeting must be showing before lock expiry test"
  );

  // Tick past both lock expiry and 3-min idle threshold
  // (now = Date.now() + HINT_LOCK_MS + 1 + 3 min > hintLockedUntil ≈ Date.now() + 8s)
  sandbox.idleTick(Date.now() + HINT_LOCK_MS + 1 + 3 * 60 * 1000);
  await settle();

  // Lock is expired → idle transition applies
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /吾在這裡/,
    "expired lock: idle hint must replace startup greeting"
  );
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "neutral",
    "expired lock: idle neutral expression must be applied"
  );
}

async function testReturnGreetingLocksHintFromIdleTransition() {
  // Return-from-away greeting must also be protected by the hint lock.
  const { document, sandbox } = await loadRenderer();

  // Enter long idle + eligibility
  sandbox.idleTick(Date.now() + 15 * 60 * 1000 + 1);
  await settle();

  // User returns — shows return greeting + sets 8-second lock
  sandbox.resetActivity();
  await settle();
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /吾才沒有/,
    "return greeting must be showing"
  );

  // Extend the lock so it outlasts the synthetic idle tick
  sandbox.lockCompanionHint(10 * 60 * 1000);

  // Idle tick at 3-min threshold — must NOT override return greeting
  sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
  await settle();

  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /吾才沒有/,
    "hint lock must protect return greeting from immediate idle transition"
  );
}

async function testChatResponseMoodOverridesGreetingLock() {
  // A chat response must always update the expression and mood label,
  // regardless of any active greeting lock.
  const { document } = await loadRenderer();

  // Startup greeting is showing with lock active
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /哼，汝終於把吾叫醒/,
    "startup greeting must be showing before chat"
  );

  // Send a chat — response has mood=focused
  await sendChat(document, "chat during greeting lock test");

  // Chat response must override lock — setMood calls setPetExpression directly
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "focused",
    "chat response mood must override greeting lock"
  );
  assert.equal(
    document.getElementById("mood-label").textContent,
    "focused",
    "mood label must update from chat response despite greeting lock"
  );
}

async function testPendingStateOverridesGreetingLock() {
  // The pending expression (set by sendMessage) must show immediately,
  // bypassing any active greeting lock.
  const { document, state } = await loadRenderer({ pauseChat: true });

  // Startup greeting is showing with lock active
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /哼，汝終於把吾叫醒/,
    "startup greeting must be showing before send"
  );

  // Trigger a chat request — sendMessage sets pending expression directly
  document.getElementById("message-input").value = "pending lock override test";
  document.getElementById("send-btn").click();
  await new Promise((resolve) => setTimeout(resolve, 0));

  // Pending expression must override the greeting lock
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "pending",
    "pending expression must override greeting lock"
  );

  // Clean up
  state.resolveChat();
  await settle();
}

// ---------------------------------------------------------------------------
// TASK-112: Phase 5 Companion Behavior Integration Checkpoint
// ---------------------------------------------------------------------------
// Each test below verifies a cross-task integration scenario not covered by
// the individual TASK-108~111 unit tests.  No new behaviour is introduced —
// these are pure checkpoint / coverage-gap tests.

async function testNetworkErrorOverridesGreetingLock() {
  // A network error (backend unreachable) must override the startup greeting
  // lock.  The offline expression must appear even while hintLockedUntil is
  // in the future, because the error path calls setPetExpression() directly
  // rather than through idleTick.
  const { document } = await loadRenderer({ chatMode: "network_error" });

  // Startup greeting and lock are both active at this point.
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /哼，汝終於把吾叫醒/,
    "startup greeting must be showing before network error"
  );
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "proud",
    "expression must be proud before network error"
  );

  // Send a message that results in a network error.
  await sendChat(document, "network error during greeting lock test");

  // Error path calls setPetExpression("offline") directly — must bypass lock.
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "offline",
    "network error must override greeting lock with offline expression"
  );
  assert.equal(
    textOf(document, "chat-source-status"),
    "source: backend_offline",
    "source status must reflect backend_offline after network error"
  );
}

async function testProviderErrorOverridesGreetingLock() {
  // A provider timeout (HTTP 504) must set the error expression even while
  // the startup greeting lock is active.  The error path calls
  // setPetExpression("error") directly, bypassing hintLockedUntil.
  const { document } = await loadRenderer({ chatMode: "provider_timeout" });

  // Startup greeting and lock are both active.
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /哼，汝終於把吾叫醒/,
    "startup greeting must be showing before provider timeout"
  );
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "proud",
    "expression must be proud before provider timeout"
  );

  // Send a message that results in a provider timeout (HTTP 504).
  await sendChat(document, "provider timeout during greeting lock test");

  // Error path calls setPetExpression("error") directly — must bypass lock.
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "error",
    "provider timeout must override greeting lock with error expression"
  );
}

async function testSourceRuntimeStatusNotClearedByStartupGreeting() {
  // Startup greeting sets pet-display-hint and the proud expression.
  // Verify that (a) mood-label is initialised at startup and (b) the
  // source/runtime status area still updates correctly after a subsequent
  // chat — i.e. the startup greeting setup does not break the status pipeline.
  const { document } = await loadRenderer();

  // Startup greeting must be visible.
  assert.match(
    document.getElementById("pet-display-hint").textContent,
    /哼，汝終於把吾叫醒/,
    "startup greeting must be visible"
  );

  // mood-label is set by setMood("neutral") at startup — must not be empty.
  const moodText = textOf(document, "mood-label");
  assert.ok(
    typeof moodText === "string" && moodText.length > 0,
    `mood-label must be non-empty after startup, got: ${JSON.stringify(moodText)}`
  );

  // pet-face data-mood must be proud (startup expression).
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "proud",
    "pet-face must show proud expression at startup"
  );

  // Sending a chat must still update the source/runtime status area, confirming
  // the startup greeting did not break the status pipeline.
  await sendChat(document, "source status integration check");
  assert.equal(
    textOf(document, "chat-source-status"),
    "source: llm_local",
    "source status must update after chat even after startup greeting was shown"
  );
  assert.equal(
    textOf(document, "mood-label"),
    "focused",
    "mood-label must update after chat even after startup greeting was shown"
  );
}

async function testPhase5FullCompanionIntegrationFlow() {
  // End-to-end integration across TASK-108~111:
  //   startup -> lock blocks idle -> lock expires -> idle works -> long idle ->
  //   away eligible -> return greeting (annoyed) -> no /chat at any point.
  //
  // Each sub-phase uses a fresh renderer load to keep state isolated.

  const HINT_LOCK_MS = 8 * 1000;

  // --- Phase A: startup greeting, proud expression, no /chat ---------------
  {
    const { document, state } = await loadRenderer();
    assert.match(
      document.getElementById("pet-display-hint").textContent,
      /哼，汝終於把吾叫醒/,
      "phase5[A]: startup greeting must be visible"
    );
    assert.equal(
      document.getElementById("pet-face").getAttribute("data-mood"),
      "proud",
      "phase5[A]: startup expression must be proud"
    );
    const chatCalls = state.calls.filter((c) => c.url.endsWith("/chat"));
    assert.equal(chatCalls.length, 0, "phase5[A]: startup must not call /chat");
  }

  // --- Phase B: lock blocks 3-min idle hint --------------------------------
  {
    const { document, sandbox } = await loadRenderer();
    sandbox.lockCompanionHint(10 * 60 * 1000);
    sandbox.idleTick(Date.now() + 3 * 60 * 1000 + 1);
    await settle();
    assert.match(
      document.getElementById("pet-display-hint").textContent,
      /哼，汝終於把吾叫醒/,
      "phase5[B]: lock must protect startup greeting from 3-min idle"
    );
    assert.equal(
      document.getElementById("pet-face").getAttribute("data-mood"),
      "proud",
      "phase5[B]: expression must remain proud while lock is active"
    );
  }

  // --- Phase C: lock expires -> idle hint applies ---------------------------
  {
    const { document, sandbox } = await loadRenderer();
    sandbox.idleTick(Date.now() + HINT_LOCK_MS + 1 + 3 * 60 * 1000);
    await settle();
    assert.match(
      document.getElementById("pet-display-hint").textContent,
      /吾在這裡/,
      "phase5[C]: expired lock must allow 3-min idle hint"
    );
    assert.equal(
      document.getElementById("pet-face").getAttribute("data-mood"),
      "neutral",
      "phase5[C]: expired lock must allow neutral idle expression"
    );
  }

  // --- Phase D: 10-min idle -> sleepy --------------------------------------
  {
    const { document, sandbox } = await loadRenderer();
    sandbox.idleTick(Date.now() + HINT_LOCK_MS + 1 + 10 * 60 * 1000);
    await settle();
    assert.equal(
      document.getElementById("pet-face").getAttribute("data-mood"),
      "sleepy",
      "phase5[D]: 10-min idle must set sleepy expression after lock expires"
    );
    assert.match(
      document.getElementById("pet-display-hint").textContent,
      /哼……吾才沒有等到想睡/,
      "phase5[D]: 10-min idle must set sleepy hint"
    );
  }

  // --- Phase E: return-from-away greeting (annoyed, no /chat) -------------
  {
    const { document, sandbox, state } = await loadRenderer();
    sandbox.idleTick(Date.now() + 15 * 60 * 1000 + 1);
    await settle();
    sandbox.resetActivity();
    await settle();
    assert.match(
      document.getElementById("pet-display-hint").textContent,
      /吾才沒有/,
      "phase5[E]: return greeting must appear after 15-min away"
    );
    assert.equal(
      document.getElementById("pet-face").getAttribute("data-mood"),
      "annoyed",
      "phase5[E]: return greeting must set annoyed expression"
    );
    const chatCalls = state.calls.filter((c) => c.url.endsWith("/chat"));
    assert.equal(chatCalls.length, 0, "phase5[E]: return greeting must not call /chat");
  }
}

async function main() {
  await testChatSendCallsBackendAndRendersReply();
  await testSuccessfulLocalChatUpdatesMoodAndSourceStatus();
  await testLoadingColdStartStatusIsVisible();
  await testEnterKeySendsChat();
  await testBackendOfflineShowsSafeUiError();
  await testProviderTimeoutShowsSafeUiError();
  await testLocalProviderFailureWithoutFallbackIsVisible();
  await testMockFallbackStateIsDistinguishable();
  await testProviderSettingsStatusAndTestConnectionSuccess();
  await testSaveProviderSettingsOmitsBlankModelAndKeepsFallbackFalse();
  testRendererDoesNotContainDirectOllamaUrl();
  // TASK-083: pet expression tests
  await testSuccessfulChatWithFocusedMoodSetsFocusedExpression();
  await testPendingExpressionSetBeforeResponse();
  await testUnknownMoodFallsBackToNeutralExpression();
  await testBackendOfflineSetsOfflineExpression();
  await testLocalErrorSetsErrorExpression();
  await testMockFallbackExpressionFollowsMoodNotSource();
  await testSourceStatusRemainsVisibleAlongsidePetExpression();
  await testProviderTimeoutSetsErrorExpression();
  // TASK-086: image asset fallback tests
  await testNeutralMoodUsesPngImageWhenAvailable();
  await testIntegratedMoodPngAssetsLoadWhenAvailable();
  await testPngLoadFailureFallsBackToSvg();
  await testFocusedMoodFallsBackToSvgWhenNoPng();
  await testMissingExpressionPngsStillFallBackToSvg();
  await testImageAssetDoesNotBreakSourceOrMoodLabel();
  // TASK-098: UI polish tests
  await testChatAreaAccumulatesMultipleMessages();
  await testFriendlySourceLabelShownAfterLocalChat();
  // TASK-108: idle state behavior tests
  await testIdleShortThresholdSetsNeutralExpressionAndHint();
  await testIdleLongThresholdSetsSleepyExpressionAndHint();
  await testUserInteractionResetsIdleState();
  await testIdleTickDoesNotCallChatEndpoint();
  await testIdleTickNotFiredDuringActiveChatRequest();
  await testSourceStatusStillVisibleAfterIdleThenChat();
  // TASK-109: startup greeting tests
  await testStartupGreetingHintIsVisible();
  await testStartupGreetingExpressionIsProud();
  await testStartupGreetingDoesNotCallChat();
  await testIdleStillWorksAfterStartupGreeting();
  // TASK-110: return-from-away greeting tests
  await testReturnFromLongIdleShowsReturnGreeting();
  await testReturnGreetingDoesNotCallChat();
  await testReturnGreetingOnlyFiresOncePerAwaySession();
  await testShortIdleDoesNotTriggerReturnGreeting();
  await testReturnGreetingResetAfterReenteringLongIdle();
  // TASK-111: companion hint lock tests
  await testStartupGreetingLocksHintFromIdleTransition();
  await testGreetingLockExpiresAllowingIdleHint();
  await testReturnGreetingLocksHintFromIdleTransition();
  await testChatResponseMoodOverridesGreetingLock();
  await testPendingStateOverridesGreetingLock();
  // TASK-112: Phase 5 integration checkpoint tests
  await testNetworkErrorOverridesGreetingLock();
  await testProviderErrorOverridesGreetingLock();
  await testSourceRuntimeStatusNotClearedByStartupGreeting();
  await testPhase5FullCompanionIntegrationFlow();
  console.log("renderer chat smoke: PASS");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
