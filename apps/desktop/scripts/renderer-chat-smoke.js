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
  }

  appendChild(child) {
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

class FakeDocument {
  constructor() {
    this.elements = new Map();
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
  const state = {
    calls: [],
    chatMode: options.chatMode || "success",
    pauseChat: Boolean(options.pauseChat),
    resolveChat: null,
    providerSettings: defaultProviderSettings(options.providerSettings || {}),
  };
  const sandbox = {
    console,
    document,
    window: {
      location: {
        search: "?backend=http%3A%2F%2Flocalhost%3A8000",
      },
      confirm: () => true,
    },
    URLSearchParams,
    fetch: createFetchStub(state),
    setTimeout,
    clearTimeout,
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
  return { document, state };
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
  assert.equal(testCalls.length, 1);
  assert.match(textOf(document, "provider-test-msg"), /Local Ollama connection successful/);
  assert.match(textOf(document, "provider-test-msg"), /source: llm_local/);
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
  testRendererDoesNotContainDirectOllamaUrl();
  console.log("renderer chat smoke: PASS");
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
