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
  assert.ok(!/\btesseract\b|recognize\s*\(/i.test(renderer),
    "renderer.js must not contain OCR code");
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
  testStaticSourceScopeChecks();
  testCaptureButtonExistsInHtml();
  await testCaptureDoesNotRunOnLoad(ctx);
  await testTypingStillWorksAfterCaptureWiring(ctx);
  await testCaptureClickInvokesNarrowPreloadApi(ctx);
  await testCaptureSuccessUpdatesStatusWithSafeMessage(ctx);
  await testCaptureFailureUsesSafeMappedMessage(ctx);
  await testCaptureMissingBridgeDoesNotCrash(ctx);
  await testCaptureNeverPostsToChat(ctx);
}

module.exports = { runAll };
