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
    // TASK-113: clientHeight needed for isChatNearBottom() helper
    this.clientHeight = 0;
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
    // TASK-113: use Math.max so tests can pre-set a large scrollHeight to
    // simulate a long chat history without it being overwritten by the append.
    this.scrollHeight = Math.max(this.scrollHeight, this.children.length);
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
    // TASK-197: provider health must be checked before the plain /health handler
    // because "/provider/health".endsWith("/health") is also true.
    if (target.endsWith("/provider/health")) {
      const reachable = state.ollamaReachable === true;
      return new FakeResponse(200, {
        provider: "ollama",
        ollama_reachable: reachable,
        status: reachable ? "ok" : "unavailable",
      });
    }
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
    if (target.endsWith("/ocr/extract")) {
      // TASK-172A-OCR-BACKEND: backend OCR mock
      if (state.ocrMode === "success") {
        return new FakeResponse(200, { ok: true, text: "Hello World" });
      }
      if (state.ocrMode === "no-text") {
        return new FakeResponse(200, { ok: false, error: "no-text" });
      }
      if (state.ocrMode === "ocr-failed") {
        return new FakeResponse(200, { ok: false, error: "ocr-failed" });
      }
      // default: ocr-unavailable
      return new FakeResponse(200, { ok: false, error: "ocr-unavailable" });
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

      if (state.chatMode === "thinking_fields") {
        state.providerSettings = {
          ...state.providerSettings,
          usage_summary: usageFor("llm_local"),
        };
        return new FakeResponse(200, {
          reply: "Clean final reply.",
          mood: "focused",
          source: "llm_local",
          thinking: "THINKING_FIELD_SHOULD_NOT_RENDER",
          message: {
            thinking: "MESSAGE_THINKING_SHOULD_NOT_RENDER",
            content: "RAW_MESSAGE_CONTENT_SHOULD_NOT_RENDER",
          },
          debug: "DEBUG_TRACE_SHOULD_NOT_RENDER",
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
    ocrMode: options.ocrMode || "unavailable",  // TASK-172A-OCR-BACKEND
    pauseChat: Boolean(options.pauseChat),
    resolveChat: null,
    providerSettings: defaultProviderSettings(options.providerSettings || {}),
    availableImages,
    intervalCallbacks,  // exposed for verification if needed
    // TASK-197: default true so liveness check sets "已就緒" and doesn't break status-summary tests.
    ollamaReachable: options.ollamaReachable !== undefined ? options.ollamaReachable : true,
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
      dragonPet: options.dragonPet || undefined,
      // TASK-172A: allow tests to override window.confirm behaviour.
      confirm: typeof options.confirmOverride === "function"
        ? options.confirmOverride
        : () => true,
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
    // TASK-197: startup health check uses AbortController for an 8-second timeout.
    AbortController,
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

async function testSuccessfulChatMirrorsReplyToPetSpeech() {
  const speechUpdates = [];
  const { document } = await loadRenderer({
    dragonPet: {
      updatePetSpeech(payload) {
        speechUpdates.push(payload);
        return Promise.resolve({ ok: true });
      },
      showPetWindow() {
        return Promise.resolve({ ok: true });
      },
    },
  });

  await sendChat(document, "mirror to pet");

  // TASK-157: two calls — thinking first, then reply
  assert.equal(speechUpdates.length, 2);

  // first call: thinking state mirror
  assert.equal(speechUpdates[0].source, "pet_thinking",
    `First updatePetSpeech call should be pet_thinking, got "${speechUpdates[0].source}"`);
  assert.equal(typeof speechUpdates[0].reply, "string");
  assert.ok(speechUpdates[0].reply.length > 0, "thinking reply text must not be empty");

  // second call: real reply
  assert.deepEqual(Object.keys(speechUpdates[1]).sort(), ["mood", "reply", "source"]);
  assert.deepEqual(JSON.parse(JSON.stringify(speechUpdates[1])), {
    reply: "Hmph, local dragon reply.",
    mood: "focused",
    source: "llm_local",
  });
}

async function testSuccessfulChatDoesNotRequirePetSpeechApi() {
  const { document } = await loadRenderer();

  await sendChat(document, "no pet speech api");

  const rendered = messageTexts(document.getElementById("chat-area")).join("\n");
  assert.match(rendered, /Hmph, local dragon reply/);
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local");
}

async function testFullAppNormalReplyDoesNotRenderThinkingFields() {
  const { document } = await loadRenderer({ chatMode: "thinking_fields" });

  await sendChat(document, "thinking field smoke");

  const rendered = messageTexts(document.getElementById("chat-area")).join("\n");
  assert.match(rendered, /Clean final reply/);
  assert.doesNotMatch(
    rendered,
    /THINKING_FIELD_SHOULD_NOT_RENDER|MESSAGE_THINKING_SHOULD_NOT_RENDER|RAW_MESSAGE_CONTENT_SHOULD_NOT_RENDER|DEBUG_TRACE_SHOULD_NOT_RENDER/
  );
}

async function testSuccessfulLocalChatUpdatesMoodAndSourceStatus() {
  const { document } = await loadRenderer();

  await sendChat(document);

  assert.equal(textOf(document, "mood-label"), "focused");
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local");
  assert.match(textOf(document, "chat-runtime-status"), /Ollama 已回覆/);

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
  assert.match(textOf(document, "chat-runtime-status"), /第一次回覆可能需要較久/);

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
  assert.match(textOf(document, "chat-runtime-status"), /本地 AI 失敗/);
  assert.match(textOf(document, "chat-runtime-status"), /模型可能仍在載入中/);
}

async function testMockFallbackStateIsDistinguishable() {
  const { document } = await loadRenderer({
    chatMode: "mock_fallback",
    providerSettings: { fallback_to_mock: true },
  });

  await sendChat(document, "fallback");

  assert.equal(textOf(document, "chat-source-status"), "source: mock");
  assert.match(textOf(document, "chat-runtime-status"), /使用模擬備援/);

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

function testFullAppShowPetWindowEntryExists() {
  const html = fs.readFileSync(indexPath, "utf8");
  const renderer = fs.readFileSync(rendererPath, "utf8");

  assert.match(html, /id="show-pet-window-btn"/);
  assert.match(html, /id="show-pet-window-status"/);
  assert.match(renderer, /showPetWindowFromFullApp/);
  assert.match(renderer, /window\.dragonPet/);
  assert.match(renderer, /showPetWindow/);
}

async function testShowPetWindowButtonUsesNarrowApi() {
  let called = false;
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow() {
        called = true;
        return Promise.resolve({ ok: true });
      },
    },
  });

  document.getElementById("show-pet-window-btn").click();
  await settle();

  assert.equal(called, true);
  assert.equal(textOf(document, "show-pet-window-status"), "Pet Window shown.");
}

async function testShowPetWindowDisabledStatusDoesNotCrash() {
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow() {
        return Promise.resolve({ ok: false, reason: "pet_mode_disabled" });
      },
    },
  });

  document.getElementById("show-pet-window-btn").click();
  await settle();

  assert.match(textOf(document, "show-pet-window-status"), /PET_MODE_ENABLED=true/);
  assert.match(document.getElementById("show-pet-window-status").className, /error/);
}

async function testShowPetWindowMissingApiDoesNotCrash() {
  const { document } = await loadRenderer();

  document.getElementById("show-pet-window-btn").click();
  await settle();

  assert.equal(textOf(document, "show-pet-window-status"), "Pet Mode bridge unavailable.");
  assert.match(document.getElementById("show-pet-window-status").className, /error/);
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
// ---------------------------------------------------------------------------
// TASK-113: Sticky Chat Composer / Better Chat Scroll UX
// ---------------------------------------------------------------------------

async function testChatComposerExistsAndIsNotRemovedByMessageAppend() {
  // send-btn and message-input must remain in the DOM after messages are
  // appended — the composer must not be displaced or removed.
  const { document } = await loadRenderer();

  // Both composer elements must exist at startup.
  assert.ok(
    document.getElementById("send-btn"),
    "send-btn must exist in the DOM at startup"
  );
  assert.ok(
    document.getElementById("message-input"),
    "message-input must exist at startup"
  );

  // Send a message and receive an AI reply — append multiple messages.
  await sendChat(document, "composer persistence test");

  // Composer must still be present after the chat round-trip.
  assert.ok(
    document.getElementById("send-btn"),
    "send-btn must remain in the DOM after message append"
  );
  assert.ok(
    document.getElementById("message-input"),
    "message-input must remain after message append"
  );
}

async function testUserSendScrollsChatToBottom() {
  // When the user sends a message, the chat area must scroll to the bottom
  // immediately (autoScroll:true on the user message and loading indicator).
  const { document } = await loadRenderer({ pauseChat: true });

  const chatArea = document.getElementById("chat-area");
  // Simulate user having scrolled up (scrollTop = 0, large scrollHeight).
  chatArea.scrollHeight = 500;
  chatArea.clientHeight = 200;
  chatArea.scrollTop = 0; // user is at the top

  document.getElementById("message-input").value = "auto-scroll send test";
  document.getElementById("send-btn").click();
  // One tick so appendMessage runs synchronously (no requestAnimationFrame in sandbox).
  await new Promise((resolve) => setTimeout(resolve, 0));

  // After the user sends, scrollTop must equal scrollHeight (scrolled to bottom).
  assert.equal(
    chatArea.scrollTop,
    chatArea.scrollHeight,
    "chat area must scroll to bottom when user sends a message"
  );

  // Clean up paused chat.
  const { state } = await loadRenderer({ pauseChat: false });
  void state; // unused but silences linter
}

async function testAiReplyDoesNotScrollWhenUserScrolledUp() {
  // If the user has scrolled up to read history (not near bottom), the AI
  // reply must NOT force-scroll to the bottom.
  const { document, state } = await loadRenderer();

  const chatArea = document.getElementById("chat-area");
  // Set up: large scrollHeight (many messages above), user scrolled to the top.
  // clientHeight = 200, scrollHeight = 500, scrollTop = 0
  // → isChatNearBottom() = 500 - 0 - 200 = 300 > 80 → NOT near bottom
  chatArea.scrollHeight = 500;
  chatArea.clientHeight = 200;
  chatArea.scrollTop = 0;

  // Snapshot scrollTop before the chat response arrives.
  const scrollTopBeforeReply = chatArea.scrollTop;

  await sendChat(document, "scrolled-up ai reply test");

  // scrollTop must NOT have changed to scrollHeight — user's position preserved.
  assert.equal(
    chatArea.scrollTop,
    scrollTopBeforeReply,
    "chat area must NOT auto-scroll when user is scrolled up reading history"
  );

  // Source/mood/expression must still update normally.
  assert.equal(textOf(document, "chat-source-status"), "source: llm_local");
  assert.equal(textOf(document, "mood-label"), "focused");
  assert.equal(
    document.getElementById("pet-face").getAttribute("data-mood"),
    "focused"
  );
  void state;
}

async function testAiReplyScrollsWhenUserIsNearBottom() {
  // If the user is near the bottom (default / fresh state), the AI reply
  // must scroll the chat area to the bottom.
  const { document } = await loadRenderer();

  const chatArea = document.getElementById("chat-area");
  // Default FakeElement: scrollHeight = children.length, scrollTop = 0, clientHeight = 0.
  // With clientHeight = 0: isChatNearBottom() = scrollHeight - 0 - 0 < 80.
  // After a couple of messages scrollHeight will be a small number < 80 → near bottom.
  // Verify this is the near-bottom case.
  assert.ok(
    chatArea.scrollHeight - chatArea.scrollTop - chatArea.clientHeight < 80,
    "pre-condition: chat area should be near bottom in default state"
  );

  await sendChat(document, "near-bottom auto-scroll test");

  // After AI reply, scrollTop must equal scrollHeight (scrolled to bottom).
  assert.equal(
    chatArea.scrollTop,
    chatArea.scrollHeight,
    "chat area must scroll to bottom when user was near bottom and AI replies"
  );
}

async function testScrollHelpersExistInSandbox() {
  // isChatNearBottom, scrollChatToBottom, maybeScrollChatToBottom must be
  // accessible as top-level functions in the sandbox (vm.runInNewContext).
  const { sandbox } = await loadRenderer();

  assert.equal(
    typeof sandbox.isChatNearBottom,
    "function",
    "isChatNearBottom must be a top-level function"
  );
  assert.equal(
    typeof sandbox.scrollChatToBottom,
    "function",
    "scrollChatToBottom must be a top-level function"
  );
  assert.equal(
    typeof sandbox.maybeScrollChatToBottom,
    "function",
    "maybeScrollChatToBottom must be a top-level function"
  );
}

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

// ---------------------------------------------------------------------------
// TASK-157 — Pet Bubble Thinking / Typing State
// ---------------------------------------------------------------------------

async function testUpdatePetThinkingStateFunctionExists() {
  // updatePetThinkingState is a `function` declaration — accessible on sandbox
  const { sandbox } = await loadRenderer();
  assert.equal(
    typeof sandbox.updatePetThinkingState,
    "function",
    "updatePetThinkingState must be defined in renderer.js"
  );
}

async function testUpdatePetThinkingStateCallsUpdatePetSpeechWithPetThinkingSource() {
  let capturedPayload = null;
  const { sandbox } = await loadRenderer({
    dragonPet: {
      updatePetSpeech(payload) {
        capturedPayload = payload;
        return Promise.resolve({ ok: true });
      },
      showPetWindow() { return Promise.resolve({ ok: true }); },
    },
  });

  sandbox.updatePetThinkingState();

  assert.ok(capturedPayload !== null,
    "updatePetThinkingState must call window.dragonPet.updatePetSpeech");
  assert.equal(capturedPayload.source, "pet_thinking",
    `source must be "pet_thinking", got "${capturedPayload.source}"`);
  assert.ok(
    typeof capturedPayload.reply === "string" && capturedPayload.reply.length > 0,
    "updatePetThinkingState payload must have a non-empty reply string"
  );
  assert.equal(capturedPayload.mood, "focused",
    `mood must be "focused", got "${capturedPayload.mood}"`);
  assert.doesNotMatch(capturedPayload.reply, /source:|mood:|\{|\}|llm_local|pet_thinking/,
    "Thinking reply text must not contain debug tokens");
}

async function testUpdatePetThinkingStateHandlesNoPetBridge() {
  // Load without dragonPet so window.dragonPet is undefined
  const { sandbox } = await loadRenderer();
  // Ensure window has no dragonPet bridge
  sandbox.window.dragonPet = undefined;
  let threw = false;
  try {
    sandbox.updatePetThinkingState();
  } catch (_e) {
    threw = true;
  }
  assert.equal(threw, false,
    "updatePetThinkingState must not crash when dragonPet bridge is absent");
}

// ---------------------------------------------------------------------------
// TASK-189: Provider Settings UI Polish tests
// ---------------------------------------------------------------------------

function testTask189ProviderSettingsButtonText() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.match(html, /儲存 AI 設定/);
  assert.doesNotMatch(html, /Save Non-secret Settings/);
}

async function testTask189ProviderStatusSummaryMockMode() {
  const { document } = await loadRenderer({
    providerSettings: { provider: "mock", real_provider_enabled: false, llm_chat_enabled: false },
  });
  const summary = textOf(document, "provider-status-summary");
  assert.match(summary, /模擬模式/);
}

async function testTask189ProviderStatusSummaryOllamaActive() {
  // default settings: ollama, real_provider_enabled: true, llm_chat_enabled: true, fallback_to_mock: false
  // TASK-197: after liveness check runs at startup (ollamaReachable=true by default),
  // the summary updates from "已連線" to "已就緒" — accept both states.
  const { document } = await loadRenderer();
  const summary = textOf(document, "provider-status-summary");
  assert.match(summary, /Ollama.*(已連線|已就緒)/);
}

async function testTask189ProviderStatusSummaryFallbackWarning() {
  const { document } = await loadRenderer({
    providerSettings: {
      provider: "ollama",
      real_provider_enabled: true,
      llm_chat_enabled: true,
      fallback_to_mock: true,
    },
  });
  const summary = textOf(document, "provider-status-summary");
  assert.match(summary, /備援/);
}

function testTask189SourceStatusMessagesNotRaw() {
  // Verify that sourceStatusMessage-derived runtime messages no longer start with "source=xxx"
  const rendererSrc = fs.readFileSync(rendererPath, "utf8");
  assert.doesNotMatch(rendererSrc, /"source=llm_local/);
  assert.doesNotMatch(rendererSrc, /"source=mock/);
  assert.doesNotMatch(rendererSrc, /"source=llm_real/);
  assert.doesNotMatch(rendererSrc, /"source=backend_offline/);
}

async function testTask190ProviderStatusSummaryInvalidKey() {
  // TASK-190 edge case: invalid/test_failed key should show error, not "not configured"
  const { document } = await loadRenderer({
    providerSettings: {
      provider: "anthropic",
      real_provider_enabled: true,
      llm_chat_enabled: true,
      fallback_to_mock: false,
      key_status: "test_failed",
      resolved_provider: "anthropic",
    },
  });
  const summary = textOf(document, "provider-status-summary");
  assert.match(summary, /無效或連線測試失敗/);
  assert.doesNotMatch(summary, /未設定/);
}

async function testTask190ProviderStatusSummaryCloudActive() {
  const { document } = await loadRenderer({
    providerSettings: {
      provider: "anthropic",
      real_provider_enabled: true,
      llm_chat_enabled: true,
      fallback_to_mock: false,
      key_status: "test_success",
      resolved_provider: "anthropic",
    },
  });
  const summary = textOf(document, "provider-status-summary");
  assert.match(summary, /anthropic.*已連線/);
}


// ---------------------------------------------------------------------------
// TASK-193: Pet Chat Mirror tests
// ---------------------------------------------------------------------------

function testTask193OnChatMirrorListenerSetup() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  assert(renderer.includes("setupPetChatMirrorListener"), "renderer.js must define setupPetChatMirrorListener");
  assert(renderer.includes("onChatMirrorFromPet"), "renderer.js must call onChatMirrorFromPet");
  assert(renderer.includes("appendMessage(\"user\", payload.userMessage"), "mirror handler must append user message");
  assert(renderer.includes("appendMessage(\"pet\", payload.reply"), "mirror handler must append pet reply");
}

async function testTask193MirrorFromPetAppendsUserAndReply() {
  let mirrorCallback = null;
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: (cb) => { mirrorCallback = cb; return () => {}; },
    },
  });

  assert(typeof mirrorCallback === "function", "onChatMirrorFromPet callback must be registered");

  const chatArea = document.getElementById("chat-area");
  const beforeCount = chatArea.children.length;

  mirrorCallback({ userMessage: "Hello via Pet", reply: "Hi from Christina", mood: "happy", source: "llm_local" });
  await settle();

  const messages = chatArea.children.slice(beforeCount);
  assert.equal(messages.length, 2, "mirror should append exactly 2 messages (user + pet)");
  const userMsg = messages[0].children.map((c) => c.textContent).join(" ");
  const petMsg  = messages[1].children.map((c) => c.textContent).join(" ");
  assert.match(userMsg, /Hello via Pet/);
  assert.match(petMsg, /Hi from Christina/);
}

async function testTask193MirrorEmptyUserMessageIsNoOp() {
  let mirrorCallback = null;
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: (cb) => { mirrorCallback = cb; return () => {}; },
    },
  });

  const chatArea = document.getElementById("chat-area");
  const beforeCount = chatArea.children.length;

  mirrorCallback({ userMessage: "", reply: "Some reply", mood: "neutral", source: "mock" });
  await settle();

  assert.equal(chatArea.children.length, beforeCount, "empty userMessage must not append any messages");
}

async function testTask193MirrorEmptyReplyIsNoOp() {
  let mirrorCallback = null;
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: (cb) => { mirrorCallback = cb; return () => {}; },
    },
  });

  const chatArea = document.getElementById("chat-area");
  const beforeCount = chatArea.children.length;

  mirrorCallback({ userMessage: "Hello", reply: "", mood: "neutral", source: "mock" });
  await settle();

  assert.equal(chatArea.children.length, beforeCount, "empty reply must not append any messages");
}

async function testTask193MirrorMissingApiIsNoOp() {
  // With no dragonPet.onChatMirrorFromPet, renderer should not throw
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      // onChatMirrorFromPet intentionally absent
    },
  });
  const chatArea = document.getElementById("chat-area");
  // No crash — just verify the existing startup messages are present
  assert(chatArea.children.length >= 1, "chat should have startup message");
}

// ---------------------------------------------------------------------------
// TASK-194: Chat History Persistence tests
// ---------------------------------------------------------------------------

async function testTask194AppendMessageSavesUserAndPetMessages() {
  const appended = [];
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: () => () => {},
      chatHistoryAppend: (entry) => { appended.push(entry); return Promise.resolve({ ok: true }); },
      chatHistoryLoad: async () => [],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  await sendChat(document, "history persistence test");
  await settle();

  const userEntries = appended.filter((e) => e.role === "user");
  const petEntries  = appended.filter((e) => e.role === "pet");
  assert.ok(userEntries.length >= 1, "chatHistoryAppend must be called with role=user");
  assert.ok(petEntries.length >= 1, "chatHistoryAppend must be called with role=pet");
  assert.match(userEntries[0].text, /history persistence test/);
  assert.equal(userEntries[0].source, "full_app");
  assert.equal(petEntries[petEntries.length - 1].source, "full_app");
}

async function testTask194NoHistoryFlagSkipsSave() {
  const appended = [];
  const { sandbox } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: () => () => {},
      chatHistoryAppend: (entry) => { appended.push(entry); return Promise.resolve({ ok: true }); },
      chatHistoryLoad: async () => [],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  // Clear accumulated entries from startup, then call appendMessage with noHistory:true
  appended.length = 0;
  sandbox.appendMessage("user", "should not be saved", { noHistory: true });
  sandbox.appendMessage("pet", "also not saved", { noHistory: true });

  assert.equal(appended.length, 0, "noHistory:true must not call chatHistoryAppend");
}

async function testTask194LoadHistoryRendersEntriesNoChatCall() {
  const { document, state } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: () => () => {},
      chatHistoryAppend: async () => ({ ok: true }),
      chatHistoryLoad: async () => [
        { role: "user", text: "old user message", source: "full_app" },
        { role: "pet",  text: "old pet reply",    source: "full_app" },
      ],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  const chatArea = document.getElementById("chat-area");
  const userMsgs = chatArea.children.filter((el) => el.className && el.className.includes("user"));
  const petMsgs  = chatArea.children.filter((el) => el.className && el.className.includes("pet"));

  assert.ok(userMsgs.some((el) => el.children.some((c) => c.textContent.includes("old user message"))),
    "loaded user message must appear in chat area");
  assert.ok(petMsgs.some((el) => el.children.some((c) => c.textContent.includes("old pet reply"))),
    "loaded pet reply must appear in chat area");

  const chatCalls = state.calls.filter((c) => c.url.endsWith("/chat"));
  assert.equal(chatCalls.length, 0, "loadAndRenderChatHistory must not trigger a /chat call");
}

async function testTask194PetMirrorSavesWithPetInputSource() {
  const appended = [];
  let mirrorCallback = null;
  await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: (cb) => { mirrorCallback = cb; return () => {}; },
      chatHistoryAppend: (entry) => { appended.push(entry); return Promise.resolve({ ok: true }); },
      chatHistoryLoad: async () => [],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  appended.length = 0;
  assert.ok(typeof mirrorCallback === "function", "onChatMirrorFromPet callback must be registered");
  mirrorCallback({ userMessage: "pet direct input", reply: "Hi from Christina", mood: "happy", source: "llm_local" });
  await settle();

  const userEntries = appended.filter((e) => e.role === "user");
  const petEntries  = appended.filter((e) => e.role === "pet");
  assert.ok(userEntries.length >= 1, "pet mirror must save user entry");
  assert.ok(petEntries.length >= 1, "pet mirror must save pet entry");
  // TASK-195: no inputMethod → defaults to text → source becomes "pet_text"
  assert.equal(userEntries[0].source, "pet_text", "pet mirror user entry must have source=pet_text");
  assert.equal(petEntries[0].source, "pet_text", "pet mirror pet entry must have source=pet_text");
}

async function testTask194ClearChatClearsHistoryAndDom() {
  let cleared = false;
  const { document, sandbox } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: () => () => {},
      chatHistoryAppend: async () => ({ ok: true }),
      chatHistoryLoad: async () => [],
      chatHistoryClear: async () => { cleared = true; return { ok: true }; },
    },
  });

  // Send a chat message so we have something in the DOM
  await sendChat(document, "message before clear");
  const chatArea = document.getElementById("chat-area");
  assert.ok(chatArea.children.length > 0, "chat area must have messages before clear");

  await sandbox.clearChatHistory();

  assert.ok(cleared, "chatHistoryClear IPC must be called");
  assert.equal(chatArea.children.length, 0, "chat area must be empty after clearChatHistory");
}

function testTask194StartupGreetingNotSaved() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  // Startup greeting must have noHistory:true so it is not persisted
  // TASK-195: greeting text updated to Chinese character voice
  assert.match(renderer, /appendMessage\("pet",\s*"哼，吾在這裡/,
    "startup greeting appendMessage must be present (Chinese character voice)");
  assert.match(renderer, /appendMessage\("pet",\s*"哼，吾在這裡[^)]*noHistory:\s*true/,
    "startup greeting must pass noHistory:true to appendMessage");
}

// ---------------------------------------------------------------------------
// TASK-195: Chat History UX Polish tests
// ---------------------------------------------------------------------------

async function testTask195AppendMessageShowsTimestampMeta() {
  const { sandbox } = await loadRenderer();

  const wrap = sandbox.appendMessage("user", "test ts", { ts: 1609459200000, source: "full_app" });
  const meta = wrap.children.find((c) => c.className === "msg-meta");
  assert.ok(meta, "appendMessage with ts > 0 must create .msg-meta element");
  assert.match(meta.textContent, /\d\d:\d\d/, ".msg-meta must contain HH:mm time string");
}

async function testTask195AppendMessageNoMetaWithoutTsOrLabel() {
  const { sandbox } = await loadRenderer();

  // ts = 0, source = "full_app" → no source label, no time → no meta element
  const wrap = sandbox.appendMessage("user", "no meta test", { ts: 0, source: "full_app" });
  const meta = wrap.children.find((c) => c.className === "msg-meta");
  assert.equal(meta, undefined, "appendMessage with ts=0 and unlabelled source must not create .msg-meta");
}

async function testTask195PetTextSourceShowsPetLabel() {
  const { sandbox } = await loadRenderer();

  const wrap = sandbox.appendMessage("user", "pet text msg", { source: "pet_text", ts: 0 });
  const meta = wrap.children.find((c) => c.className === "msg-meta");
  assert.ok(meta, "pet_text source must create .msg-meta even without timestamp");
  assert.match(meta.textContent, /Pet/, "pet_text source must display 'Pet' label");
}

async function testTask195PetVoiceSourceShowsVoiceLabel() {
  const { sandbox } = await loadRenderer();

  const wrap = sandbox.appendMessage("user", "voice msg", { source: "pet_voice", ts: 0 });
  const meta = wrap.children.find((c) => c.className === "msg-meta");
  assert.ok(meta, "pet_voice source must create .msg-meta even without timestamp");
  assert.match(meta.textContent, /Voice/, "pet_voice source must display 'Voice' label");
}

async function testTask195LoadHistoryPassesTsAndSource() {
  const TS = 1609459200000;
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: () => () => {},
      chatHistoryAppend: async () => ({ ok: true }),
      chatHistoryLoad: async () => [
        { role: "user", text: "voice history msg", source: "pet_voice", ts: TS },
      ],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  const chatArea = document.getElementById("chat-area");
  const userMsgs = chatArea.children.filter((el) => el.className && el.className.includes("user"));
  assert.ok(userMsgs.length >= 1, "loaded user message must be rendered");
  const meta = userMsgs[0].children.find((c) => c.className === "msg-meta");
  assert.ok(meta, "loaded entry with ts + pet_voice source must have .msg-meta");
  assert.match(meta.textContent, /Voice/, "loaded pet_voice history must display 'Voice' label");
}

async function testTask195RestoreStatusAppearsAfterHistoryLoad() {
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: () => () => {},
      chatHistoryAppend: async () => ({ ok: true }),
      chatHistoryLoad: async () => [
        { role: "user", text: "old msg", source: "full_app", ts: 0 },
      ],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  const chatArea = document.getElementById("chat-area");
  const statusMsgs = chatArea.children.filter((el) => el.className && el.className.includes("status"));
  assert.ok(
    statusMsgs.some((el) => el.children.some((c) => c.textContent.includes("已還原"))),
    "loadAndRenderChatHistory must append a '已還原 N 筆' restore status message"
  );
}

async function testTask195MirrorVoiceInputMethodShowsVoiceLabel() {
  let mirrorCallback = null;
  const { document } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      captureScreen: async () => ({ ok: false }),
      captureWindow: async () => ({ ok: false }),
      onChatMirrorFromPet: (cb) => { mirrorCallback = cb; return () => {}; },
      chatHistoryAppend: async () => ({ ok: true }),
      chatHistoryLoad: async () => [],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  assert.ok(typeof mirrorCallback === "function", "onChatMirrorFromPet callback must be registered");
  mirrorCallback({ userMessage: "voice input", reply: "reply", mood: "happy", source: "llm_local", inputMethod: "voice" });
  await settle();

  const chatArea = document.getElementById("chat-area");
  const lastMsgs = chatArea.children.slice(-2);
  const userWrap = lastMsgs[0];
  const meta = userWrap.children.find((c) => c.className === "msg-meta");
  assert.ok(meta, "voice mirror message must have .msg-meta");
  assert.match(meta.textContent, /Voice/, "voice mirror message must display 'Voice' label");
}

// TASK-195 Visual Polish: static file-reading tests
// ---------------------------------------------------------------------------

const cssPath  = path.join(desktopRoot, "src", "renderer", "styles.css");

function testTask195VisHeaderTitleWrapperExists() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes('class="header-title"'), "index.html must contain .header-title wrapper");
  assert.ok(html.includes('class="header-actions"'), "index.html must contain .header-actions wrapper");
  assert.ok(html.includes('class="header-btn-group"'), "index.html must contain .header-btn-group for screen context buttons");
}

function testTask195VisShowPetHasPrimaryClass() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(
    html.includes('id="show-pet-window-btn"') && html.includes("header-action-btn--primary"),
    "show-pet-window-btn must have header-action-btn--primary class"
  );
  const btnLine = html.split("\n").find((l) => l.includes("show-pet-window-btn"));
  assert.ok(btnLine && btnLine.includes("--primary"), "show-pet-window-btn line must include --primary");
}

function testTask195VisClearChatHasGhostClass() {
  const html = fs.readFileSync(indexPath, "utf8");
  const btnLine = html.split("\n").find((l) => l.includes("clear-chat-btn"));
  assert.ok(btnLine && btnLine.includes("--ghost"), "clear-chat-btn must use header-action-btn--ghost (not --secondary)");
}

function testTask195VisPrimaryButtonCssExists() {
  const css = fs.readFileSync(cssPath, "utf8");
  assert.ok(css.includes("header-action-btn--primary"), "styles.css must define .header-action-btn--primary");
  assert.ok(css.includes("var(--accent)"), "primary button must use accent color as background");
}

function testTask195VisGhostButtonCssExists() {
  const css = fs.readFileSync(cssPath, "utf8");
  assert.ok(css.includes("header-action-btn--ghost"), "styles.css must define .header-action-btn--ghost");
  assert.ok(css.includes("header-action-btn--ghost") && css.includes("transparent"), "ghost button must have transparent background");
}

function testTask195VisMoodIndicatorNotAccentRed() {
  const css = fs.readFileSync(cssPath, "utf8");
  const moodBlock = css.slice(css.indexOf(".mood-indicator"), css.indexOf(".mood-indicator") + 200);
  assert.ok(!moodBlock.includes("var(--accent)"), "mood-indicator must not use accent red — should use a softer colour");
  assert.ok(moodBlock.includes("#5b9fd6"), "mood-indicator must use calm blue #5b9fd6");
}

function testTask195VisPetDisplayGradient() {
  const css = fs.readFileSync(cssPath, "utf8");
  assert.ok(css.includes("linear-gradient") && css.includes("pet-display"),
    "#pet-display must use a linear-gradient background");
}

function testTask195VisPetDisplayHintSpeechBubble() {
  const css = fs.readFileSync(cssPath, "utf8");
  assert.ok(css.includes("pet-display-hint") && css.includes("12px 12px 12px 3px"),
    ".pet-display-hint must have speech-bubble border-radius (12px 12px 12px 3px)");
}

function testTask195VisChatAreaEmptyPlaceholder() {
  const css = fs.readFileSync(cssPath, "utf8");
  assert.ok(css.includes("#chat-area:empty::before"),
    "styles.css must define #chat-area:empty::before placeholder for empty chat state");
}

function testTask195VisNoMoodLabelInHtml() {
  const html = fs.readFileSync(indexPath, "utf8");
  const statusBlock = html.slice(html.indexOf("character-status"), html.indexOf("mood-label") + 50);
  assert.ok(!statusBlock.includes(">Mood:<"), "character-status must not contain redundant 'Mood:' span");
}

function testTask195VisFriendlyProviderName() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  assert.ok(renderer.includes("friendlyProviderName"),
    "renderer.js must define friendlyProviderName helper");
  assert.ok(!renderer.includes("`provider: ${p}`"),
    "provider chip must not use raw 'provider: X' format before first chat");
}

function testTask195VisCharacterStatusBelowAvatar() {
  const html = fs.readFileSync(indexPath, "utf8");
  const petDisplayPos = html.indexOf("id=\"pet-display\"");
  const charStatusPos = html.indexOf("id=\"character-status\"");
  assert.ok(charStatusPos > petDisplayPos,
    "character-status must appear after pet-display in HTML (below the avatar)");
}

function testTask195VisMenuHiddenInRenderer() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  // Chinese character voice greeting (not English)
  assert.ok(!renderer.includes("Hey. I'm here"),
    "startup greeting must not be English — should be Chinese character voice");
  assert.ok(renderer.includes("哼，吾在這裡"),
    "startup greeting must use Chinese character voice");
}

// TASK-195 Visual Polish Follow-up 3

function testTask195VisF3StatusSeparatorStyle() {
  const css = fs.readFileSync(path.join(desktopRoot, "src", "renderer", "styles.css"), "utf8");
  assert.ok(!css.includes("dashed var(--border)"),
    "CSS .message.status must not use dashed border (separator style, not bubble)");
  assert.ok(css.includes(".message.status::before") || css.includes(".message.status::after"),
    "CSS .message.status must have ::before/::after pseudo-elements for separator lines");
  assert.ok(css.includes(".message.status .sender"),
    "CSS must hide .sender inside .message.status");
}

function testTask195VisF3MemoryToggleChinese() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes("使用已核準的記憶"),
    "memory toggle label must use Chinese text");
  assert.ok(!html.includes("Use approved memories"),
    "memory toggle must not use English 'Use approved memories'");
}

function testTask195VisF3NoRawEnvVarVisible() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(!html.includes("<code>MEMORY_INJECTION_ENABLED"),
    "MEMORY_INJECTION_ENABLED must not be displayed inside a <code> tag");
  assert.ok(/title="[^"]*MEMORY_INJECTION_ENABLED/.test(html),
    "MEMORY_INJECTION_ENABLED should be in a title tooltip attribute, not visible text");
}

function testTask195VisF3InputBarNowrap() {
  const css = fs.readFileSync(path.join(desktopRoot, "src", "renderer", "styles.css"), "utf8");
  assert.ok(css.includes("flex-wrap: nowrap"),
    "CSS #input-bar must use flex-wrap: nowrap so input+Send stay on one row");
}

function testTask195VisF3HistoryStatusUpdates() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  assert.ok(renderer.includes("已載入最近對話"),
    "renderer.js must update status to '已載入最近對話' after history restore");
  assert.ok(renderer.includes("lastChatStatusMessage = \"已載入最近對話\""),
    "renderer.js must assign lastChatStatusMessage after loadAndRenderChatHistory");
}

// TASK-195 Visual Polish Follow-up 4

function testTask195VisF4MemorySectionCollapsible() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes('id="memory-details"'),
    "memory-section must use <details id='memory-details'> for collapse");
  assert.ok(html.includes('class="memory-summary"'),
    "memory summary must have memory-summary class");
  assert.ok(!html.includes('<details id="memory-details" open'),
    "memory-details must NOT have the 'open' attribute — closed by default");
}

function testTask195VisF4MemoryTitleChinese() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes("記憶管理"),
    "memory summary title must be '記憶管理'");
  assert.ok(html.includes("管理克莉絲蒂娜記得的事情"),
    "memory summary hint must be Chinese");
  assert.ok(html.includes("重新整理記憶"),
    "Refresh Memories button must say '重新整理記憶'");
  assert.ok(!html.includes(">Memory<"),
    "memory h2 must not contain English 'Memory'");
}

function testTask195VisF4MemoryFormLabelsChinese() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes("類型") && html.includes("重要度") && html.includes("可信度"),
    "memory form labels must be Chinese: 類型, 重要度, 可信度");
  assert.ok(html.includes("儲存記憶"),
    "Save Memory button must say '儲存記憶'");
  assert.ok(html.includes('value="user_preference"'),
    "memory type option values must remain unchanged (user_preference)");
  assert.ok(html.includes('value="explicit"'),
    "memory confidence option values must remain unchanged (explicit)");
}

function testTask195VisF4MemorySummaryCssExists() {
  const css = fs.readFileSync(path.join(desktopRoot, "src", "renderer", "styles.css"), "utf8");
  assert.ok(css.includes(".memory-summary"),
    "CSS must define .memory-summary styles");
  assert.ok(css.includes("#memory-details[open]"),
    "CSS must have #memory-details[open] rule for expanded state");
  assert.ok(css.includes(".memory-summary-title"),
    "CSS must have .memory-summary-title rule");
}

// TASK-195 Visual Polish Follow-up 5

function testTask195VisF5AuditSectionCollapsible() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes('id="audit-details"'),
    "audit-section must use <details id='audit-details'> for collapse");
  assert.ok(html.includes('class="audit-summary-row"'),
    "audit summary must have audit-summary-row class");
  assert.ok(!html.includes('<details id="audit-details" open'),
    "audit-details must NOT have the 'open' attribute — closed by default");
}

function testTask195VisF5AuditTitleChinese() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes("診斷紀錄"),
    "audit summary title must be '診斷紀錄'");
  assert.ok(html.includes("查看記憶注入事件"),
    "audit summary hint must be Chinese");
  assert.ok(!html.includes(">Audit Logs<"),
    "audit h2 must not contain English 'Audit Logs'");
}

function testTask195VisF5AuditLabelsChinese() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes("重新整理紀錄"),
    "Refresh Audit Logs button must say '重新整理紀錄'");
  assert.ok(html.includes("筆數"),
    "Limit label must be '筆數'");
  assert.ok(html.includes("起始位置"),
    "Offset label must be '起始位置'");
  assert.ok(!html.includes(">Refresh Audit Logs<"),
    "Refresh Audit Logs must not appear in English");
}

function testTask195VisF5AuditSummaryCssExists() {
  const css = fs.readFileSync(path.join(desktopRoot, "src", "renderer", "styles.css"), "utf8");
  assert.ok(css.includes(".audit-summary-row"),
    "CSS must define .audit-summary-row styles");
  assert.ok(css.includes("#audit-details[open]"),
    "CSS must have #audit-details[open] rule for expanded state");
  assert.ok(css.includes(".audit-summary-title"),
    "CSS must have .audit-summary-title rule");
}

// TASK-195 Visual Polish Follow-up 6

function testTask195VisF6ProviderSectionCollapsible() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes('id="provider-details"'),
    "Provider Settings section must have <details id='provider-details'> for default-collapsed behaviour");
  assert.ok(html.includes('class="provider-summary-row"'),
    "Provider Settings summary must have class provider-summary-row");
}

function testTask195VisF6ProviderTitleChinese() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes("AI 設定"),
    "Provider Settings title must be Chinese 'AI 設定'");
  assert.ok(html.includes("設定克莉絲蒂娜使用的 AI 模型與連線方式"),
    "Provider Settings hint must be Chinese summary text");
}

function testTask195VisF6ProviderLabelsChinese() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes("AI 來源"), "Provider label must be Chinese 'AI 來源'");
  assert.ok(html.includes("啟用真實 AI"), "Real AI checkbox must be Chinese");
  assert.ok(html.includes("啟用 AI 聊天"), "LLM chat checkbox must be Chinese");
  assert.ok(html.includes("儲存 AI 設定"), "Save button must be Chinese");
  assert.ok(html.includes("API 金鑰"), "API key label must be Chinese");
  assert.ok(html.includes("重新整理設定"), "Refresh button must be Chinese");
}

function testTask195VisF6ProviderSummaryCssExists() {
  const css = fs.readFileSync(path.join(desktopRoot, "src", "renderer", "styles.css"), "utf8");
  assert.ok(css.includes(".provider-summary-row"),
    "CSS must define .provider-summary-row styles");
  assert.ok(css.includes("#provider-details[open]"),
    "CSS must have #provider-details[open] rule for expanded state");
  assert.ok(css.includes(".provider-summary-title"),
    "CSS must have .provider-summary-title rule");
}

// ---------------------------------------------------------------------------
// TASK-196: Chat Message Copy / Export tests
// ---------------------------------------------------------------------------

function testTask196CopyChatButtonInHtml() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.ok(html.includes('id="copy-chat-btn"'),
    "Header must contain #copy-chat-btn button");
  assert.ok(html.includes("複製對話"),
    "#copy-chat-btn must have Chinese label '複製對話'");
}

function testTask196CopyFunctionsExist() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.ok(src.includes("function copyAllChat"),
    "renderer.js must define copyAllChat");
  assert.ok(src.includes("function copySingleMessage"),
    "renderer.js must define copySingleMessage");
  assert.ok(src.includes("function writeToClipboard"),
    "renderer.js must define writeToClipboard bridge-first helper");
  assert.ok(src.includes("dataset.msgText"),
    "appendMessage must store text in dataset.msgText (no innerHTML)");
}

function testTask196CopyAllSelectorOnlyUserPet() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.ok(
    src.includes('".message.user, .message.pet"') ||
    src.includes("'.message.user, .message.pet'"),
    "copyAllChat must query only .message.user and .message.pet — not status/error"
  );
}

function testTask196MsgCopyBtnCssExists() {
  const css = fs.readFileSync(path.join(desktopRoot, "src", "renderer", "styles.css"), "utf8");
  assert.ok(css.includes(".msg-copy-btn"),
    "CSS must define .msg-copy-btn");
  assert.ok(css.includes(".msg-copy-btn.copied"),
    "CSS must define .msg-copy-btn.copied feedback state");
  assert.ok(css.includes(".message.user:hover .msg-copy-btn") || css.includes(".message.pet:hover .msg-copy-btn"),
    "CSS must show .msg-copy-btn on hover only");
}

async function testTask196CopyBtnAppendedToPetBubble() {
  // Startup greeting appends a pet message — verify it carries .msg-copy-btn.
  // Uses FakeElement.children (no querySelectorAll in the fake DOM).
  const { document } = await loadRenderer({});
  const chatArea = document.getElementById("chat-area");
  const petMsg = chatArea.children.find(
    (c) => typeof c.className === "string" && c.className.includes("pet")
  );
  assert.ok(petMsg, "At least one pet message element must exist after startup (greeting)");
  const copyBtn = petMsg.children.find(
    (c) => typeof c.className === "string" && c.className.includes("msg-copy-btn")
  );
  assert.ok(copyBtn, "Pet message bubble must contain a .msg-copy-btn child");
  assert.strictEqual(copyBtn.type, "button", ".msg-copy-btn must be type=button");
  assert.ok(petMsg.dataset && petMsg.dataset.msgText, "Pet message must have dataset.msgText populated");
}

async function testTask196ClipboardUnavailableNocrash() {
  // VM sandbox has no navigator and no dragonPet — clicking .msg-copy-btn must not throw.
  const { document } = await loadRenderer({});
  const chatArea = document.getElementById("chat-area");
  const petMsg = chatArea.children.find(
    (c) => typeof c.className === "string" && c.className.includes("pet")
  );
  assert.ok(petMsg, "Pet message must exist for clipboard no-crash test");
  const copyBtn = petMsg.children.find(
    (c) => typeof c.className === "string" && c.className.includes("msg-copy-btn")
  );
  assert.ok(copyBtn, "Pet message must have .msg-copy-btn for clipboard no-crash test");
  let threw = false;
  try {
    copyBtn.dispatchEvent({ type: "click", stopPropagation: () => {} });
  } catch (_) {
    threw = true;
  }
  assert.ok(!threw, "Clicking .msg-copy-btn without navigator must not throw");
}

function testTask196CopyPrefersBridge() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.ok(src.includes("writeClipboardText"),
    "renderer.js must reference writeClipboardText bridge");
  assert.ok(src.includes("function writeToClipboard"),
    "renderer.js must define writeToClipboard helper");
  assert.ok(src.includes("api.writeClipboardText"),
    "writeToClipboard must call api.writeClipboardText when available");
  assert.ok(src.includes("Promise.resolve(api.writeClipboardText"),
    "writeToClipboard must wrap async IPC bridge in Promise.resolve");
}

function testTask196NavigatorFallbackExists() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.ok(src.includes("navigator.clipboard"),
    "renderer.js must still reference navigator.clipboard as fallback");
  assert.ok(src.includes("clipboard unavailable"),
    "renderer.js must reject with 'clipboard unavailable' when no API exists");
}

async function testTask196BridgeCalledWhenAvailable() {
  let bridgeCalled = false;
  let bridgeText = null;
  const { document } = await loadRenderer({
    dragonPet: { writeClipboardText: (text) => { bridgeCalled = true; bridgeText = text; return true; } },
  });
  const chatArea = document.getElementById("chat-area");
  const petMsg = chatArea.children.find(
    (c) => typeof c.className === "string" && c.className.includes("pet")
  );
  assert.ok(petMsg, "Pet message must exist for bridge-call test");
  const copyBtn = petMsg.children.find(
    (c) => typeof c.className === "string" && c.className.includes("msg-copy-btn")
  );
  assert.ok(copyBtn, "Pet message must have .msg-copy-btn for bridge-call test");
  copyBtn.dispatchEvent({ type: "click", stopPropagation: () => {} });
  assert.ok(bridgeCalled, "writeClipboardText bridge must be called when dragonPet provides it");
  assert.strictEqual(typeof bridgeText, "string", "bridge must receive message text as string");
}

// ---------------------------------------------------------------------------
// TASK-197: Ollama Wake-up / First Chat Reliability tests
// ---------------------------------------------------------------------------

const backendRoutesPath = path.join(desktopRoot, "..", "..", "backend", "app", "api", "routes.py");

function testTask197ProviderHealthEndpointInBackend() {
  const routes = fs.readFileSync(backendRoutesPath, "utf8");
  assert.match(routes, /\/provider\/health/,
    "routes.py must define /provider/health endpoint");
  assert.match(routes, /check_ollama_server_liveness/,
    "routes.py must call check_ollama_server_liveness");
  assert.match(routes, /ollama_reachable/,
    "routes.py must include ollama_reachable in response");
}

function testTask197SourceStatusMessagesChinese() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.match(src, /Ollama 已回覆/,
    "sourceStatusMessage for llm_local must be Chinese");
  assert.match(src, /本地 AI 失敗/,
    "sourceStatusMessage for llm_local_error must be Chinese");
  assert.match(src, /等待本地 Ollama 回應中/,
    "sourceStatusMessage for pending (Ollama path) must be Chinese");
  assert.doesNotMatch(src, /Ollama response received/,
    "sourceStatusMessage must not contain English 'Ollama response received'");
  assert.doesNotMatch(src, /"Local AI failed/,
    "sourceStatusMessage must not contain English 'Local AI failed'");
}

function testTask197StartupLoadingTextChinese() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.match(src, /本地 AI 喚醒中/,
    "sendMessage Ollama loading text must be Chinese");
  assert.match(src, /等待後端回覆中/,
    "sendMessage non-Ollama loading text must be Chinese");
  assert.doesNotMatch(src, /Waking up local AI/,
    "sendMessage loading text must not contain English 'Waking up local AI'");
}

function testTask197StartupHealthFetchHasTimeout() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.match(src, /new AbortController\(\)/,
    "startup must create AbortController for health check timeout");
  assert.match(src, /_healthCtrl/,
    "startup must use _healthCtrl for the AbortController instance");
  assert.match(src, /signal: _healthCtrl\.signal/,
    "startup fetch must pass signal: _healthCtrl.signal");
  assert.match(src, /8000/,
    "startup timeout must be 8000 ms");
}

function testTask197LivenessCheckFunctionExists() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.match(src, /async function checkLocalProviderLiveness/,
    "renderer.js must define checkLocalProviderLiveness as an async function");
}

function testTask197LivenessCheckUsesProviderHealthPath() {
  const src = fs.readFileSync(rendererPath, "utf8");
  assert.match(src, /\/provider\/health/,
    "checkLocalProviderLiveness must fetch /provider/health");
}

async function testTask197LivenessCheckDoesNotWriteToChatHistory() {
  const appended = [];
  const { document, state } = await loadRenderer({
    dragonPet: {
      showPetWindow: async () => ({ ok: true }),
      updatePetSpeech: async () => ({ ok: true }),
      onChatMirrorFromPet: () => () => {},
      chatHistoryAppend: (entry) => { appended.push(entry); return Promise.resolve({ ok: true }); },
      chatHistoryLoad: async () => [],
      chatHistoryClear: async () => ({ ok: true }),
    },
  });

  // Clear any startup entries, then allow background tasks to complete
  appended.length = 0;
  await settle();

  assert.equal(appended.length, 0,
    "checkLocalProviderLiveness must not call chatHistoryAppend");

  // Liveness result must not appear as a chat-area message
  const chatArea = document.getElementById("chat-area");
  const livenessInChat = chatArea.children.some((el) =>
    el.children.some((c) =>
      c.textContent.includes("正在檢查本地 AI") ||
      c.textContent.includes("Ollama 本地 AI 已就緒") ||
      c.textContent.includes("Ollama 尚未回應")
    )
  );
  assert.ok(!livenessInChat,
    "liveness check result must not appear in chat area — only in provider-status-summary");

  void state;
}

async function testTask197LivenessCheckOllamaReachableUpdatesChip() {
  const { document } = await loadRenderer({ ollamaReachable: true });
  const summary = textOf(document, "provider-status-summary");
  assert.match(summary, /Ollama 本地 AI 已就緒/,
    "provider-status-summary must show '已就緒' when Ollama is reachable");
}

async function testTask197LivenessCheckOllamaUnreachableShowsWarning() {
  const { document } = await loadRenderer({ ollamaReachable: false });
  const summary = textOf(document, "provider-status-summary");
  assert.match(summary, /Ollama 尚未回應/,
    "provider-status-summary must warn '尚未回應' when Ollama is unreachable");
}

async function main() {
  await testChatSendCallsBackendAndRendersReply();
  await testSuccessfulChatMirrorsReplyToPetSpeech();
  await testSuccessfulChatDoesNotRequirePetSpeechApi();
  await testFullAppNormalReplyDoesNotRenderThinkingFields();
  await testSuccessfulLocalChatUpdatesMoodAndSourceStatus();
  await testLoadingColdStartStatusIsVisible();
  await testEnterKeySendsChat();
  await testBackendOfflineShowsSafeUiError();
  await testProviderTimeoutShowsSafeUiError();
  await testLocalProviderFailureWithoutFallbackIsVisible();
  await testMockFallbackStateIsDistinguishable();
  await testProviderSettingsStatusAndTestConnectionSuccess();
  await testSaveProviderSettingsOmitsBlankModelAndKeepsFallbackFalse();
  testFullAppShowPetWindowEntryExists();
  await testShowPetWindowButtonUsesNarrowApi();
  await testShowPetWindowDisabledStatusDoesNotCrash();
  await testShowPetWindowMissingApiDoesNotCrash();
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
  // TASK-157: Pet Bubble Thinking / Typing State
  await testUpdatePetThinkingStateFunctionExists();
  await testUpdatePetThinkingStateCallsUpdatePetSpeechWithPetThinkingSource();
  await testUpdatePetThinkingStateHandlesNoPetBridge();
  // TASK-171A: screenshot capture regression + scope tests
  const task171a = require("./task171a-capture-smoke.js");
  await task171a.runAll({ loadRenderer, sendChat, settle, textOf });
  // TASK-189: Provider Settings UI polish tests
  testTask189ProviderSettingsButtonText();
  await testTask189ProviderStatusSummaryMockMode();
  await testTask189ProviderStatusSummaryOllamaActive();
  await testTask189ProviderStatusSummaryFallbackWarning();
  testTask189SourceStatusMessagesNotRaw();
  // TASK-190: Provider Settings manual smoke closeout — edge case tests
  await testTask190ProviderStatusSummaryInvalidKey();
  await testTask190ProviderStatusSummaryCloudActive();
  // TASK-193: Pet chat mirror tests
  testTask193OnChatMirrorListenerSetup();
  await testTask193MirrorFromPetAppendsUserAndReply();
  await testTask193MirrorEmptyUserMessageIsNoOp();
  await testTask193MirrorEmptyReplyIsNoOp();
  await testTask193MirrorMissingApiIsNoOp();
  // TASK-194: Chat history persistence tests
  await testTask194AppendMessageSavesUserAndPetMessages();
  await testTask194NoHistoryFlagSkipsSave();
  await testTask194LoadHistoryRendersEntriesNoChatCall();
  await testTask194PetMirrorSavesWithPetInputSource();
  await testTask194ClearChatClearsHistoryAndDom();
  testTask194StartupGreetingNotSaved();
  // TASK-195: Chat History UX Polish tests
  await testTask195AppendMessageShowsTimestampMeta();
  await testTask195AppendMessageNoMetaWithoutTsOrLabel();
  await testTask195PetTextSourceShowsPetLabel();
  await testTask195PetVoiceSourceShowsVoiceLabel();
  await testTask195LoadHistoryPassesTsAndSource();
  await testTask195RestoreStatusAppearsAfterHistoryLoad();
  await testTask195MirrorVoiceInputMethodShowsVoiceLabel();
  // TASK-195 Visual Polish tests
  testTask195VisHeaderTitleWrapperExists();
  testTask195VisShowPetHasPrimaryClass();
  testTask195VisClearChatHasGhostClass();
  testTask195VisPrimaryButtonCssExists();
  testTask195VisGhostButtonCssExists();
  testTask195VisMoodIndicatorNotAccentRed();
  testTask195VisPetDisplayGradient();
  testTask195VisPetDisplayHintSpeechBubble();
  testTask195VisChatAreaEmptyPlaceholder();
  testTask195VisNoMoodLabelInHtml();
  testTask195VisFriendlyProviderName();
  testTask195VisCharacterStatusBelowAvatar();
  testTask195VisMenuHiddenInRenderer();
  // TASK-195 Visual Polish Follow-up 3
  testTask195VisF3StatusSeparatorStyle();
  testTask195VisF3MemoryToggleChinese();
  testTask195VisF3NoRawEnvVarVisible();
  testTask195VisF3InputBarNowrap();
  testTask195VisF3HistoryStatusUpdates();
  // TASK-195 Visual Polish Follow-up 4
  testTask195VisF4MemorySectionCollapsible();
  testTask195VisF4MemoryTitleChinese();
  testTask195VisF4MemoryFormLabelsChinese();
  testTask195VisF4MemorySummaryCssExists();
  // TASK-195 Visual Polish Follow-up 5
  testTask195VisF5AuditSectionCollapsible();
  testTask195VisF5AuditTitleChinese();
  testTask195VisF5AuditLabelsChinese();
  testTask195VisF5AuditSummaryCssExists();
  // TASK-195 Visual Polish Follow-up 6
  testTask195VisF6ProviderSectionCollapsible();
  testTask195VisF6ProviderTitleChinese();
  testTask195VisF6ProviderLabelsChinese();
  testTask195VisF6ProviderSummaryCssExists();
  // TASK-196: Chat Message Copy / Export
  testTask196CopyChatButtonInHtml();
  testTask196CopyFunctionsExist();
  testTask196CopyAllSelectorOnlyUserPet();
  testTask196MsgCopyBtnCssExists();
  await testTask196CopyBtnAppendedToPetBubble();
  await testTask196ClipboardUnavailableNocrash();
  testTask196CopyPrefersBridge();
  testTask196NavigatorFallbackExists();
  await testTask196BridgeCalledWhenAvailable();
  // TASK-197: Ollama Wake-up / First Chat Reliability
  testTask197ProviderHealthEndpointInBackend();
  testTask197SourceStatusMessagesChinese();
  testTask197StartupLoadingTextChinese();
  testTask197StartupHealthFetchHasTimeout();
  testTask197LivenessCheckFunctionExists();
  testTask197LivenessCheckUsesProviderHealthPath();
  await testTask197LivenessCheckDoesNotWriteToChatHistory();
  await testTask197LivenessCheckOllamaReachableUpdatesChip();
  await testTask197LivenessCheckOllamaUnreachableShowsWarning();
  console.log("renderer chat smoke: PASS");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
