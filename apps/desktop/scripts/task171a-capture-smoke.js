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
  assert.ok(!/require\(['"]tesseract|import\s+.*tesseract|Tesseract\.recognize\s*\(/i.test(renderer),
    "renderer.js must not require/import tesseract or call Tesseract.recognize()");
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

  // Safety: no OCR library imported, no cloud vision, no /chat in runOcrAnalysis
  assert.ok(!/require\(['"]tesseract/.test(renderer),
    "renderer.js must not require tesseract directly");
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
