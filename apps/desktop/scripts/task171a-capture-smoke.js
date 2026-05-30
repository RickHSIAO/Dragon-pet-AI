"use strict";
/**
 * TASK-171A — screenshot capture regression + scope tests.
 *
 * Loaded as a sub-module by renderer-chat-smoke.js so it shares the FakeDocument
 * harness. Kept in a separate file to avoid touching the (much larger) main
 * smoke script during NTFS-padding-sensitive writes.
 *
 * The tests assert the safety envelope, not the OS-level capture:
 *  - capture only fires on explicit click
 *  - the preload surface is narrow (captureScreen only)
 *  - no /chat call is triggered by capture
 *  - no disk save, OCR, vision, or background monitoring code was added
 *  - the Full App chat path is unaffected (typing regression)
 */

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const desktopRoot = path.resolve(__dirname, "..");
const rendererPath = path.join(desktopRoot, "src", "renderer", "renderer.js");
const indexPath = path.join(desktopRoot, "src", "renderer", "index.html");
const preloadPath = path.join(desktopRoot, "src", "renderer", "preload.js");
const mainPath = path.join(desktopRoot, "src", "main.js");

function testStaticSourceScopeChecks() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  const preload = fs.readFileSync(preloadPath, "utf8");
  const main = fs.readFileSync(mainPath, "utf8");

  assert.ok(!/require\(['"]fs['"]\)/.test(renderer),
    "renderer.js must not require('fs')");
  assert.ok(!/writeFileSync|writeFile\(|fs\.write/.test(renderer),
    "renderer.js must not write files");
  // TASK-172A-OCR: tesseract.js is now intentionally required (Option A).
  // The prohibition was lifted when OCR was implemented. Cloud vision is still banned.
  assert.ok(!/gpt-4-vision|claude-vision|imageAnalysis/i.test(renderer),
    "renderer.js must not contain vision/image-analysis code");
  assert.ok(!/setInterval\([^)]*captureScreen/.test(renderer),
    "renderer.js must not background-poll captureScreen");

  assert.ok(/screen:capture-once/.test(main),
    "main.js must declare screen:capture-once channel");
  assert.ok(!/setInterval\([^)]*desktopCapturer/.test(main),
    "main.js must not background-poll desktopCapturer");
  assert.ok(!/writeFileSync.*thumbnail|fs\.write.*toDataURL/.test(main),
    "main.js must not write screenshots to disk");
  // TASK-171A multi-monitor scope: must match by display_id, not blindly use sources[0]
  assert.ok(/display_id/.test(main),
    "main.js must attempt display_id matching for primary display");
  assert.ok(/primaryId/.test(main),
    "main.js must derive primaryId from screen.getPrimaryDisplay()");
  assert.ok(/primary-display-ambiguous/.test(main),
    "main.js must return primary-display-ambiguous when multi-monitor match fails");
  assert.ok(/primary-display-ambiguous/.test(
    fs.readFileSync(rendererPath,"utf8")),
    "renderer.js must map primary-display-ambiguous to a clean zh-TW message");

  assert.match(preload,
    /captureScreen\s*:\s*\(\s*\)\s*=>\s*ipcRenderer\.invoke\(\s*SCREEN_CAPTURE_ONCE_CHANNEL\s*\)/,
    "preload.js must expose captureScreen() with zero args");
  assert.ok(!/exposeInMainWorld\([^)]*['"]ipcRenderer['"]/.test(preload),
    "preload.js must not expose raw ipcRenderer");
  assert.ok(!/desktopCapturer/.test(preload),
    "preload.js must not expose desktopCapturer directly");
}

function testCaptureButtonExistsInHtml() {
  const html = fs.readFileSync(indexPath, "utf8");
  assert.match(html, /id="capture-screen-btn"/);
  assert.match(html, /id="capture-screen-status"/);
  const chineseLabel = "擷取螢幕";
  assert.ok(html.includes(chineseLabel),
    "Button label must be the Chinese label per design §1");
}

async function testCaptureDoesNotRunOnLoad(ctx) {
  let captureCalls = 0;
  await ctx.loadRenderer({
    dragonPet: {
      captureScreen() {
        captureCalls += 1;
        return Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" });
      },
    },
  });
  assert.equal(captureCalls, 0, "capture must not run on renderer load");
}

async function testTypingStillWorksAfterCaptureWiring(ctx) {
  const { document, state } = await ctx.loadRenderer();
  await ctx.sendChat(document, "regression after capture wiring");
  const chatCalls = state.calls.filter((call) => call.url.endsWith("/chat"));
  assert.equal(chatCalls.length, 1,
    "Full App chat send must still POST exactly once to /chat");
}

async function testCaptureClickInvokesNarrowPreloadApi(ctx) {
  let captureArgs = null;
  let captureCalls = 0;
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen(...args) {
        captureCalls += 1;
        captureArgs = args;
        return Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" });
      },
    },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  assert.equal(captureCalls, 1);
  assert.deepEqual(captureArgs, [],
    "captureScreen must be called with zero arguments");
}

async function testCaptureSuccessUpdatesStatusWithSafeMessage(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const status = ctx.textOf(document, "capture-screen-status");
  const successMarker = "螢幕截圖完成";
  assert.ok(status.includes(successMarker),
    "status must contain the Chinese success marker");
  assert.ok(!status.includes("base64"), "status must not show raw base64");
  assert.ok(!status.includes("data:image"), "status must not show data URL");
}

async function testCaptureFailureUsesSafeMappedMessage(ctx) {
  const cases = [
    ["permission-denied", "權限"],
    ["no-source", "找不到"],
    ["capture-failed", "稍後再試"],
    ["unknown-error-code", "稍後再試"],
  ];
  for (const pair of cases) {
    const reason = pair[0];
    const needle = pair[1];
    const { document } = await ctx.loadRenderer({
      dragonPet: {
        captureScreen: () => Promise.resolve({ ok: false, error: reason }),
      },
    });
    document.getElementById("capture-screen-btn").click();
    await ctx.settle();
    const status = ctx.textOf(document, "capture-screen-status");
    assert.ok(status.includes(needle),
      "reason=" + reason + " expected needle " + needle + " got: " + status);
    assert.ok(!status.includes(reason) || reason === "capture-failed",
      "status must not echo raw reason code " + reason);
    assert.ok(/error/.test(
      document.getElementById("capture-screen-status").className
    ));
  }
}

async function testCaptureMissingBridgeDoesNotCrash(ctx) {
  const { document } = await ctx.loadRenderer();
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const status = ctx.textOf(document, "capture-screen-status");
  // Should produce a user-visible status without throwing.
  assert.ok(status && status.length > 0,
    "missing bridge must still set a user-visible status");
  assert.ok(/error/.test(
    document.getElementById("capture-screen-status").className
  ));
}

async function testCaptureNeverPostsToChat(ctx) {
  const { document, state } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
  });
  const before = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const after = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  assert.equal(after, before, "capture must not POST to /chat");
}

// ---------------------------------------------------------------------------
// TASK-171A multi-monitor scope: primary-display-ambiguous failure test
// ---------------------------------------------------------------------------

async function testCaptureAmbiguousDisplayShowsCleanMessage(ctx) {
  // Simulates multi-monitor: captureScreen returns primary-display-ambiguous
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: false, error: "primary-display-ambiguous" }),
    },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const status = ctx.textOf(document, "capture-screen-status");
  assert.ok(status.includes("螢幕") || status.includes("稍後") || status.includes("無法"),
    "primary-display-ambiguous must show clean zh-TW message, got: " + status);
  assert.ok(!status.includes("ambiguous"),
    "status must not echo raw error code primary-display-ambiguous");
  assert.ok(!status.includes("base64"), "status must not show raw base64");
  // Analyze button must still be disabled (no screenshot stored)
  assert.ok(document.getElementById("analyze-screen-btn").disabled,
    "analyze button must remain disabled when capture fails with ambiguous");
}

// ---------------------------------------------------------------------------
// TASK-172A-OCR-BACKEND: backend fetch OCR tests
// ---------------------------------------------------------------------------

async function test172ABackendOcrSuccess(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: { captureScreen: () => Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }) },
    confirmOverride: () => true,
    ocrMode: "success",
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const summary = document.getElementById("analyze-screen-summary").textContent || "";
  const status = ctx.textOf(document, "analyze-screen-status");
  assert.ok(summary.includes("螢幕摘要") || summary.includes("Hello"),
    "OCR success must show summary, got summary=" + summary + " status=" + status);
  assert.ok(!summary.includes("base64"), "summary must not show raw base64");
  assert.ok(!summary.includes("data:image"), "summary must not show data URL");
}

async function test172ABackendOcrNoText(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: { captureScreen: () => Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }) },
    confirmOverride: () => true,
    ocrMode: "no-text",
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const status = ctx.textOf(document, "analyze-screen-status");
  assert.ok(status.includes("未偵測到"),
    "no-text must show 未偵測到可用文字。 got: " + status);
}

async function test172ABackendOcrUnavailableShowsClean(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: { captureScreen: () => Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }) },
    confirmOverride: () => true,
    ocrMode: "unavailable",
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const status = ctx.textOf(document, "analyze-screen-status");
  assert.ok(status.includes("不可用") || status.includes("失敗") || status.includes("連線"),
    "OCR unavailable must show clean fallback, got: " + status);
  assert.ok(!status.includes("ocr-unavailable"), "must not echo raw reason code");
  assert.ok(!status.includes("base64"), "must not show raw base64");
}

async function test172ABackendOcrNeverPostsToChat(ctx) {
  const { document, state } = await ctx.loadRenderer({
    dragonPet: { captureScreen: () => Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }) },
    confirmOverride: () => true,
    ocrMode: "success",
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const before = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const after = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  assert.equal(after, before, "OCR must never POST to /chat");
  const ocrCalls = state.calls.filter((c) => c.url.endsWith("/ocr/extract"));
  assert.equal(ocrCalls.length, 1, "OCR must call /ocr/extract exactly once");
}

async function runAll(ctx) {
  // TASK-171A tests
  testStaticSourceScopeChecks();
  testCaptureButtonExistsInHtml();
  await testCaptureDoesNotRunOnLoad(ctx);
  await testTypingStillWorksAfterCaptureWiring(ctx);
  await testCaptureClickInvokesNarrowPreloadApi(ctx);
  await testCaptureSuccessUpdatesStatusWithSafeMessage(ctx);
  await testCaptureFailureUsesSafeMappedMessage(ctx);
  await testCaptureMissingBridgeDoesNotCrash(ctx);
  await testCaptureNeverPostsToChat(ctx);
  await testCaptureAmbiguousDisplayShowsCleanMessage(ctx); // TASK-171A multi-monitor
  // TASK-172A tests
  test172AStaticSourceScopeChecks();
  await test172AAnalyzeButtonDisabledBeforeCapture(ctx);
  await test172AAnalyzeButtonEnabledAfterCapture(ctx);
  await test172ACaptureAloneDoesNotAnalyze(ctx);
  await test172AAnalyzeShowsConfirmationDialog(ctx);
  await test172ACancelPreventsAnalysis(ctx);
  await test172AConfirmStartsAnalysisAndShowsFallback(ctx);
  await test172AAnalyzeNeverPostsToChat(ctx);
  await test172AClearResetsState(ctx);
  await test172ASummaryNeverShowsRawBase64(ctx);
  await test172AAnalyzeWithNoScreenshotShowsCleanError(ctx);
  // TASK-172A-OCR static checks
  test172AOcrStaticChecks();
  // TASK-172A-OCR-BACKEND dynamic tests
  await test172ABackendOcrSuccess(ctx);
  await test172ABackendOcrNoText(ctx);
  await test172ABackendOcrUnavailableShowsClean(ctx);
  await test172ABackendOcrNeverPostsToChat(ctx);
  // TASK-172B tests
  test172BStaticSourceScopeChecks();
  await test172BAskButtonHiddenWithoutSummary(ctx);
  await test172BAskButtonVisibleAfterOcr(ctx);
  await test172BCancelConfirmDoesNotPostToChat(ctx);
  await test172BConfirmPostsSummaryToChat(ctx);
  await test172BPayloadNeverContainsDataUrl(ctx);
  await test172BPayloadNeverContainsBase64(ctx);
  await test172BClearHidesAskButton(ctx);
  await test172BAskButtonHiddenOnNoTextOcr(ctx);
  await test172BAskNeverPostsRawScreenshot(ctx);
}

module.exports = { runAll };

// ---------------------------------------------------------------------------
// TASK-172A: Screenshot OCR Summary — smoke tests
// ---------------------------------------------------------------------------

function test172AStaticSourceScopeChecks() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  const html = fs.readFileSync(indexPath, "utf8");

  // Analyze button exists and starts disabled
  assert.match(html, /id="analyze-screen-btn"/,
    "index.html must have analyze-screen-btn");
  assert.match(html, /id="analyze-screen-btn"[^>]*disabled/,
    "analyze-screen-btn must start disabled");
  assert.match(html, /id="analyze-screen-status"/,
    "index.html must have analyze-screen-status");
  assert.match(html, /id="clear-screen-btn"/,
    "index.html must have clear-screen-btn");
  assert.match(html, /id="analyze-screen-summary"/,
    "index.html must have analyze-screen-summary panel");

  // Key functions exist in renderer
  assert.ok(/function analyzeScreenFromFullApp/.test(renderer),
    "renderer.js must define analyzeScreenFromFullApp");
  assert.ok(/function updateAnalyzeButtonState/.test(renderer),
    "renderer.js must define updateAnalyzeButtonState");
  assert.ok(/function clearScreenshot/.test(renderer),
    "renderer.js must define clearScreenshot");
  assert.ok(/function runOcrAnalysis/.test(renderer),
    "renderer.js must define runOcrAnalysis");
  assert.ok(/function cleanOcrText/.test(renderer),
    "renderer.js must define cleanOcrText");

  // Confirmation text present
  assert.ok(/ANALYZE_CONFIRM_MSG/.test(renderer),
    "renderer.js must define ANALYZE_CONFIRM_MSG");
  assert.ok(/window\.confirm/.test(renderer),
    "renderer.js must use window.confirm for sensitive-content warning");

  // Safety: no cloud vision, no /chat in runOcrAnalysis
  assert.ok(!/gpt-4-vision|claude-vision|imageAnalysis/i.test(renderer),
    "renderer.js must not contain cloud vision code");
  assert.ok(!/writeFileSync|writeFile\(|fs\.write/.test(renderer),
    "renderer.js must not write files");
}

async function test172AAnalyzeButtonDisabledBeforeCapture(ctx) {
  const { document } = await ctx.loadRenderer();
  const btn = document.getElementById("analyze-screen-btn");
  assert.ok(btn.disabled, "analyze button must be disabled before any capture");
}

async function test172AAnalyzeButtonEnabledAfterCapture(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const btn = document.getElementById("analyze-screen-btn");
  assert.ok(!btn.disabled, "analyze button must be enabled after successful capture");
}

async function test172ACaptureAloneDoesNotAnalyze(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const analyzeStatus = ctx.textOf(document, "analyze-screen-status");
  assert.ok(!analyzeStatus.includes("正在分析"),
    "capture alone must not start analysis");
  assert.ok(!analyzeStatus.includes("螢幕摘要"),
    "capture alone must not produce a summary");
}

async function test172AAnalyzeShowsConfirmationDialog(ctx) {
  let confirmCalled = false;
  let confirmMsg = null;
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
    confirmOverride(msg) {
      confirmCalled = true;
      confirmMsg = msg;
      return false;
    },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  assert.ok(confirmCalled, "clicking Analyze must call window.confirm");
  assert.ok(confirmMsg && confirmMsg.includes("密碼"),
    "confirm message must mention passwords");
  assert.ok(confirmMsg && confirmMsg.includes("API 金鑰"),
    "confirm message must mention API keys");
  assert.ok(confirmMsg && confirmMsg.includes("私密訊息"),
    "confirm message must mention private messages");
}

async function test172ACancelPreventsAnalysis(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
    confirmOverride: () => false,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const analyzeStatus = ctx.textOf(document, "analyze-screen-status");
  assert.ok(!analyzeStatus.includes("正在分析"),
    "cancel must not show analyzing status");
  assert.ok(!analyzeStatus.includes("失敗"),
    "cancel must not show error");
  assert.ok(!document.getElementById("analyze-screen-btn").disabled,
    "analyze button must be re-enabled after cancel");
}

async function test172AConfirmStartsAnalysisAndShowsFallback(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const analyzeStatus = ctx.textOf(document, "analyze-screen-status");
  assert.ok(
    analyzeStatus.includes("分析功能目前不可用") ||
    analyzeStatus.includes("失敗") ||
    analyzeStatus.includes("未偵測到"),
    "analysis must show a clean fallback message, got: " + analyzeStatus
  );
  assert.ok(!analyzeStatus.includes("ocr-unavailable"),
    "status must not echo raw error code");
  assert.ok(!analyzeStatus.includes("base64"),
    "status must not show raw base64");
  assert.ok(!analyzeStatus.includes("data:image"),
    "status must not show data URL");
}

async function test172AAnalyzeNeverPostsToChat(ctx) {
  const { document, state } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  const before = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const after = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  assert.equal(after, before, "analyze must never POST to /chat");
}

async function test172AClearResetsState(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
    },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  assert.ok(!document.getElementById("analyze-screen-btn").disabled,
    "analyze button must be enabled before clear");
  document.getElementById("clear-screen-btn").click();
  await ctx.settle();
  assert.ok(document.getElementById("analyze-screen-btn").disabled,
    "analyze button must be disabled after clear");
  const summary = document.getElementById("analyze-screen-summary");
  assert.ok(summary.hidden || !summary.textContent,
    "summary panel must be hidden/empty after clear");
}

async function test172ASummaryNeverShowsRawBase64(ctx) {
  const { document } = await ctx.loadRenderer({
    dragonPet: {
      captureScreen: () =>
        Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,LONGBASE64DATA" }),
    },
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const summaryText = document.getElementById("analyze-screen-summary").textContent || "";
  const statusText = ctx.textOf(document, "analyze-screen-status");
  assert.ok(!summaryText.includes("LONGBASE64DATA"),
    "summary panel must not contain raw base64 data");
  assert.ok(!statusText.includes("LONGBASE64DATA"),
    "status must not contain raw base64 data");
  assert.ok(!summaryText.includes("data:image"),
    "summary panel must not contain data URL");
}

async function test172AAnalyzeWithNoScreenshotShowsCleanError(ctx) {
  const { document } = await ctx.loadRenderer({
    confirmOverride: () => true,
  });
  const btn = document.getElementById("analyze-screen-btn");
  btn.disabled = false;
  btn.click();
  await ctx.settle();
  const analyzeStatus = ctx.textOf(document, "analyze-screen-status");
  assert.ok(
    analyzeStatus.includes("請先擷取") || analyzeStatus.length === 0,
    "clicking analyze with no screenshot must show clean error or be guarded"
  );
}

// ---------------------------------------------------------------------------
// TASK-172A-OCR: static source checks (Option A rejected — DevTools diagnostic present)
// ---------------------------------------------------------------------------

function test172AOcrStaticChecks() {
  const renderer = fs.readFileSync(rendererPath, "utf8");

  // TASK-172A-OCR-BACKEND: runOcrAnalysis uses fetch to /ocr/extract (Option B)
  assert.ok(/\/ocr\/extract/.test(renderer),
    "renderer.js runOcrAnalysis must call /ocr/extract");
  assert.ok(/OCR_TIMEOUT_MS/.test(renderer),
    "renderer.js must define OCR_TIMEOUT_MS");
  assert.ok(/OCR_DATAURL_MAX_LEN/.test(renderer),
    "renderer.js must define OCR_DATAURL_MAX_LEN");
  assert.ok(/ocr-timeout/.test(renderer),
    "renderer.js must handle ocr-timeout error");
  assert.ok(/backend-offline/.test(renderer),
    "renderer.js must handle backend-offline error");
  assert.ok(/invalid-dataurl/.test(renderer),
    "renderer.js must handle invalid-dataurl error");

  // Safety: dataUrl guard before fetch
  assert.ok(/startsWith\("data:image\/"/.test(renderer),
    "renderer.js runOcrAnalysis must guard for data:image/ prefix");

  // No cloud vision; no nodeIntegration weakening; no /chat in OCR path
  assert.ok(!/gpt-4-vision|claude-vision|google.*vision|azure.*vision/i.test(renderer),
    "renderer.js must not reference cloud vision APIs");
  assert.ok(!/nodeIntegration.*true/.test(renderer),
    "renderer.js must not enable nodeIntegration");
}

// ---------------------------------------------------------------------------
// TASK-172B: User-Confirmed Screenshot Summary to Chat Handoff — smoke tests
// ---------------------------------------------------------------------------

const fakeCapture = {
  dragonPet: {
    captureScreen: () =>
      Promise.resolve({ ok: true, dataUrl: "data:image/png;base64,AAA" }),
  },
};

function test172BStaticSourceScopeChecks() {
  const renderer = fs.readFileSync(rendererPath, "utf8");
  const html = fs.readFileSync(indexPath, "utf8");

  // HTML: ask button and status span exist; button starts hidden
  assert.match(html, /id="ask-screen-btn"/,
    "index.html must have ask-screen-btn");
  assert.match(html, /id="ask-screen-btn"[^>]*hidden/,
    "ask-screen-btn must start hidden");
  assert.match(html, /id="ask-screen-status"/,
    "index.html must have ask-screen-status");

  // Renderer: required functions and constants
  assert.ok(/function askScreenFromFullApp/.test(renderer),
    "renderer.js must define askScreenFromFullApp");
  assert.ok(/function updateAskButtonState/.test(renderer),
    "renderer.js must define updateAskButtonState");
  assert.ok(/ASK_SCREEN_CONFIRM_MSG/.test(renderer),
    "renderer.js must define ASK_SCREEN_CONFIRM_MSG");
  assert.ok(/CHAT_SUMMARY_PREFIX/.test(renderer),
    "renderer.js must define CHAT_SUMMARY_PREFIX");

  // Privacy: CHAT_SUMMARY_PREFIX must not embed data:image
  assert.ok(!/data:image/.test(renderer.match(/CHAT_SUMMARY_PREFIX\s*=\s*"([^"]+)"/)?.[1] || ""),
    "CHAT_SUMMARY_PREFIX must not contain data:image");

  // Safety: askScreenFromFullApp uses window.confirm
  assert.ok(/ASK_SCREEN_CONFIRM_MSG/.test(renderer) && /window\.confirm/.test(renderer),
    "renderer.js must use window.confirm for ask handoff");

  // updateAskButtonState called in clearScreenshot
  assert.ok(/function clearScreenshot[\s\S]{0,300}updateAskButtonState/.test(renderer),
    "clearScreenshot must call updateAskButtonState");
}

async function test172BAskButtonHiddenWithoutSummary(ctx) {
  const { document } = await ctx.loadRenderer({ ...fakeCapture, ocrMode: "no-text" });
  const btn = document.getElementById("ask-screen-btn");
  assert.ok(btn.hidden, "ask button must be hidden on load (no OCR summary)");
}

async function test172BAskButtonVisibleAfterOcr(ctx) {
  const { document } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "success",
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const btn = document.getElementById("ask-screen-btn");
  assert.ok(!btn.hidden, "ask button must be visible after successful OCR");
}

async function test172BCancelConfirmDoesNotPostToChat(ctx) {
  // OCR confirm (call 1) = true; ask confirm (call 2) = false.
  let confirmCount = 0;
  const { document, state } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "success",
    confirmOverride: () => { confirmCount++; return confirmCount === 1; },
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const chatBefore = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  document.getElementById("ask-screen-btn").click();
  await ctx.settle();
  const chatAfter = state.calls.filter((c) => c.url.endsWith("/chat")).length;
  assert.equal(chatAfter, chatBefore, "cancelling ask confirmation must not POST to /chat");
}

async function test172BConfirmPostsSummaryToChat(ctx) {
  const { document, state } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "success",
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  document.getElementById("ask-screen-btn").click();
  await ctx.settle();
  const chatCalls = state.calls.filter((c) => c.url.endsWith("/chat"));
  assert.ok(chatCalls.length >= 1, "confirming ask must POST to /chat");
  const body = JSON.parse(chatCalls[chatCalls.length - 1].body);
  assert.ok(
    typeof body.message === "string" && body.message.includes("Hello World"),
    "chat payload must contain OCR summary text"
  );
}

async function test172BPayloadNeverContainsDataUrl(ctx) {
  const { document, state } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "success",
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  document.getElementById("ask-screen-btn").click();
  await ctx.settle();
  for (const call of state.calls.filter((c) => c.url.endsWith("/chat"))) {
    assert.ok(!call.body.includes("data:image/"), "chat payload must never contain raw dataUrl");
  }
}

async function test172BPayloadNeverContainsBase64(ctx) {
  const { document, state } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "success",
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  document.getElementById("ask-screen-btn").click();
  await ctx.settle();
  for (const call of state.calls.filter((c) => c.url.endsWith("/chat"))) {
    const body = JSON.parse(call.body);
    const msg = typeof body.message === "string" ? body.message : "";
    assert.ok(msg.length < 2000, "chat message must be bounded summary, not raw base64");
  }
}

async function test172BClearHidesAskButton(ctx) {
  const { document } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "success",
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const askBtn = document.getElementById("ask-screen-btn");
  assert.ok(!askBtn.hidden, "ask button must be visible after OCR succeeds");
  document.getElementById("clear-screen-btn").click();
  await ctx.settle();
  assert.ok(askBtn.hidden, "ask button must be hidden after clear");
}

async function test172BAskButtonHiddenOnNoTextOcr(ctx) {
  const { document } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "no-text",
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  const askBtn = document.getElementById("ask-screen-btn");
  assert.ok(askBtn.hidden, "ask button must remain hidden when OCR finds no text");
}

async function test172BAskNeverPostsRawScreenshot(ctx) {
  const { document, state } = await ctx.loadRenderer({
    ...fakeCapture,
    ocrMode: "success",
    confirmOverride: () => true,
  });
  document.getElementById("capture-screen-btn").click();
  await ctx.settle();
  document.getElementById("analyze-screen-btn").click();
  await ctx.settle();
  document.getElementById("ask-screen-btn").click();
  await ctx.settle();
  // /ocr/extract legitimately sends the dataUrl; only /chat must never contain it.
  for (const call of state.calls.filter((c) => c.url.endsWith("/chat"))) {
    const body = call.body || "";
    assert.ok(
      !body.includes("data:image/png;base64") &&
      !body.includes("data:image/jpeg;base64"),
      "chat payload must never contain raw screenshot base64"
    );
  }
}
