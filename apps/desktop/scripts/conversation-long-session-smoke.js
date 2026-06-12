const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const desktopRoot = path.resolve(__dirname, "..");
const rendererPath = path.join(desktopRoot, "src", "renderer", "renderer.js");

const CONVERSATION_QUEUE_MAX = 4;

function readText(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function makeTurn({
  turnId,
  status = "sent",
  reason = "none",
  pendingCount = 0,
  activeTurnId = 0,
  sttStatus = "success",
  chatStatus = "sent",
  ownerVoiceDryRunStatus = "ok",
  ownerVoiceAccepted = null,
  candidateWavTemporary = true,
  candidateWavDeleted = true,
  durationMs = 1800,
  blobSizeBytes = 64000,
  audioClass = "usable_audio",
  dropStage = "none",
  stopMode = "none",
  backpressurePaused = false,
  backpressureReason = "none",
  backpressureResumeReason = "none",
}) {
  return {
    turnId,
    status,
    reason,
    pendingCount,
    activeTurnId,
    sttStatus,
    chatStatus,
    ownerVoiceDryRunStatus,
    ownerVoiceAccepted,
    candidateWavTemporary,
    candidateWavDeleted,
    durationMs,
    blobSizeBytes,
    audioClass,
    dropStage,
    stopMode,
    backpressurePaused,
    backpressureReason,
    backpressureResumeReason,
  };
}

function makeLongSessionFixture() {
  return {
    queueLimit: CONVERSATION_QUEUE_MAX,
    pendingCount: 0,
    activeTurnId: 0,
    stopMode: "drain_complete",
    backpressurePaused: false,
    backpressureReason: "none",
    backpressureResumeReason: "queue_available",
    turns: [
      makeTurn({ turnId: 1, ownerVoiceAccepted: true }),
      makeTurn({ turnId: 2, ownerVoiceAccepted: false }),
      makeTurn({ turnId: 3, pendingCount: 1, ownerVoiceAccepted: true }),
      makeTurn({ turnId: 4, pendingCount: 2, ownerVoiceAccepted: null, ownerVoiceDryRunStatus: "not_computed", candidateWavTemporary: false, candidateWavDeleted: false }),
      makeTurn({ turnId: 5, sttStatus: "no_speech", chatStatus: "skipped", reason: "no_speech", ownerVoiceDryRunStatus: "disabled", ownerVoiceAccepted: null, candidateWavTemporary: false, candidateWavDeleted: false, durationMs: 950, blobSizeBytes: 12000 }),
      makeTurn({ turnId: 6, pendingCount: 3, ownerVoiceAccepted: true }),
      makeTurn({ turnId: 7, pendingCount: 4, ownerVoiceAccepted: true }),
      makeTurn({ turnId: 8, status: "backpressure_paused", reason: "queue_high_watermark", pendingCount: 3, activeTurnId: 7, sttStatus: "not_started", chatStatus: "not_sent", ownerVoiceDryRunStatus: "none", ownerVoiceAccepted: null, candidateWavTemporary: false, candidateWavDeleted: false, audioClass: "not_recorded", dropStage: "before_recording", durationMs: 0, blobSizeBytes: 0, backpressurePaused: true, backpressureReason: "queue_high_watermark" }),
      makeTurn({ turnId: 9, status: "backpressure_resumed", reason: "queue_available", pendingCount: 2, activeTurnId: 7, sttStatus: "not_started", chatStatus: "not_sent", ownerVoiceDryRunStatus: "none", ownerVoiceAccepted: null, candidateWavTemporary: false, candidateWavDeleted: false, audioClass: "not_recorded", dropStage: "none", durationMs: 0, blobSizeBytes: 0, backpressureResumeReason: "queue_available" }),
      makeTurn({ turnId: 10, status: "dropped", reason: "empty_artifact", pendingCount: 2, sttStatus: "none", chatStatus: "none", ownerVoiceDryRunStatus: "none", ownerVoiceAccepted: null, candidateWavTemporary: false, candidateWavDeleted: false, audioClass: "empty_artifact", dropStage: "before_queue", durationMs: 0, blobSizeBytes: 0 }),
      makeTurn({ turnId: 11, chatStatus: "error", reason: "chat_error", ownerVoiceAccepted: false }),
      makeTurn({ turnId: 12, ownerVoiceAccepted: true }),
      makeTurn({ turnId: 13, status: "drain_complete", reason: "drain_complete", sttStatus: "success", chatStatus: "sent", ownerVoiceAccepted: true, stopMode: "drain_complete" }),
    ],
    hardFallbackTurns: [
      makeTurn({ turnId: 99, status: "dropped", reason: "queue_full", pendingCount: 4, sttStatus: "none", chatStatus: "none", ownerVoiceDryRunStatus: "none", ownerVoiceAccepted: null, candidateWavTemporary: false, candidateWavDeleted: false, audioClass: "usable_audio", dropStage: "at_queue", durationMs: 2100, blobSizeBytes: 72000 }),
    ],
  };
}

function summarizeLongSession(session) {
  const summary = {
    totalTurns: session.turns.length,
    completedTurns: 0,
    noSpeechTurns: 0,
    droppedByReason: {},
    queueFullCount: 0,
    emptyArtifactCount: 0,
    chatErrorCount: 0,
    backpressurePausedCount: 0,
    backpressureResumedCount: 0,
    hardFallbackQueueFullCount: 0,
    ownerVoiceAcceptedCount: 0,
    ownerVoiceRejectedCount: 0,
    ownerVoiceUnknownCount: 0,
    candidateWavDeletedTrueCount: 0,
    candidateWavDeletedFalseCount: 0,
    finalPendingCount: session.pendingCount,
    finalActiveTurnId: session.activeTurnId,
    finalStopMode: session.stopMode,
  };

  for (const turn of session.turns) {
    if (turn.sttStatus === "success" && turn.chatStatus === "sent") {
      summary.completedTurns += 1;
    }
    if (turn.sttStatus === "no_speech") {
      summary.noSpeechTurns += 1;
    }
    if (turn.status === "dropped") {
      summary.droppedByReason[turn.reason] = (summary.droppedByReason[turn.reason] || 0) + 1;
    }
    if (turn.reason === "queue_full") {
      summary.queueFullCount += 1;
    }
    if (turn.reason === "empty_artifact") {
      summary.emptyArtifactCount += 1;
    }
    if (turn.chatStatus === "error") {
      summary.chatErrorCount += 1;
    }
    if (turn.backpressurePaused) {
      summary.backpressurePausedCount += 1;
    }
    if (turn.backpressureResumeReason && turn.backpressureResumeReason !== "none") {
      summary.backpressureResumedCount += 1;
    }
    if (turn.ownerVoiceAccepted === true) {
      summary.ownerVoiceAcceptedCount += 1;
    } else if (turn.ownerVoiceAccepted === false) {
      summary.ownerVoiceRejectedCount += 1;
    } else {
      summary.ownerVoiceUnknownCount += 1;
    }
    if (turn.candidateWavDeleted === true) {
      summary.candidateWavDeletedTrueCount += 1;
    } else {
      summary.candidateWavDeletedFalseCount += 1;
    }
  }

  for (const turn of session.hardFallbackTurns || []) {
    if (turn.reason === "queue_full") {
      summary.hardFallbackQueueFullCount += 1;
    }
  }

  return summary;
}

function formatCopyableSummary(summary) {
  return [
    `total=${summary.totalTurns}`,
    `completed=${summary.completedTurns}`,
    `no_speech=${summary.noSpeechTurns}`,
    `queue_full=${summary.queueFullCount}`,
    `empty_artifact=${summary.emptyArtifactCount}`,
    `chat_error=${summary.chatErrorCount}`,
    `backpressure.paused=${summary.backpressurePausedCount}`,
    `backpressure.resumed=${summary.backpressureResumedCount}`,
    `hardFallback.queue_full=${summary.hardFallbackQueueFullCount}`,
    `ownerVoice.accepted=${summary.ownerVoiceAcceptedCount}`,
    `ownerVoice.rejected=${summary.ownerVoiceRejectedCount}`,
    `ownerVoice.unknown=${summary.ownerVoiceUnknownCount}`,
    `candidateWavDeleted.true=${summary.candidateWavDeletedTrueCount}`,
    `candidateWavDeleted.false=${summary.candidateWavDeletedFalseCount}`,
    `finalPending=${summary.finalPendingCount}/${CONVERSATION_QUEUE_MAX}`,
    `finalActive=${summary.finalActiveTurnId}`,
    `stopMode=${summary.finalStopMode}`,
  ].join(" ");
}

function validateLongSessionDiagnostics(session) {
  assert.equal(session.queueLimit, CONVERSATION_QUEUE_MAX, "queue max must remain 4");
  assert.ok(session.turns.length >= 10, "fixture should represent a long session");
  assert.ok(session.pendingCount <= session.queueLimit, "final pending must not exceed max");
  assert.equal(session.activeTurnId, 0, "active turn must clear after drain");
  assert.equal(session.stopMode, "drain_complete", "final stop mode should show drain_complete");
  assert.equal(session.backpressurePaused, false, "final backpressure pause must clear");
  assert.equal(session.backpressureReason, "none", "final backpressure reason must clear");

  for (const turn of session.turns) {
    assert.ok(turn.pendingCount <= session.queueLimit, `turn#${turn.turnId} pending exceeds max`);
    if (turn.reason === "queue_full") {
      assert.fail("normal backpressure path should not produce queue_full");
    }
    if (turn.reason === "empty_artifact") {
      assert.equal(turn.audioClass, "empty_artifact", "empty artifact must stay distinguishable");
      assert.equal(turn.dropStage, "before_queue", "empty artifact must drop before queue");
      assert.equal(turn.blobSizeBytes, 0, "empty artifact should keep zero-byte evidence");
    }
    if (turn.ownerVoiceDryRunStatus === "ok") {
      assert.notEqual(turn.sttStatus, "blocked", "Owner Voice dry-run must not hard-block STT");
      assert.notEqual(turn.chatStatus, "blocked", "Owner Voice dry-run must not hard-block chat");
    }
    if (turn.candidateWavTemporary) {
      assert.equal(turn.candidateWavDeleted, true, "temporary candidate WAV should be deleted");
    }
  }

  for (const turn of session.hardFallbackTurns || []) {
    assert.equal(turn.reason, "queue_full", "hard fallback should preserve queue_full reason");
    assert.equal(turn.audioClass, "usable_audio", "hard fallback queue_full must preserve usable audio class");
    assert.equal(turn.dropStage, "at_queue", "hard fallback queue_full must be at queue admission");
    assert.ok(turn.blobSizeBytes > 0, "hard fallback usable queue_full turn should keep blob bytes");
  }

  const summary = summarizeLongSession(session);
  assert.ok(summary.completedTurns >= 8, "should represent multiple completed turns");
  assert.equal(summary.noSpeechTurns, 1, "should represent a silence/no_speech turn");
  assert.equal(summary.queueFullCount, 0, "normal backpressure path should avoid usable queue_full");
  assert.equal(summary.emptyArtifactCount, 1, "should keep empty artifact distinct");
  assert.equal(summary.chatErrorCount, 1, "should count chat errors separately");
  assert.equal(summary.backpressurePausedCount, 1, "should count backpressure pause");
  assert.equal(summary.backpressureResumedCount, 1, "should count backpressure resume");
  assert.equal(summary.hardFallbackQueueFullCount, 1, "should keep hard fallback queue_full visible");
  assert.equal(summary.finalPendingCount, 0, "final pending should be drained");
  assert.equal(summary.finalActiveTurnId, 0, "final active should be clear");
  assert.equal(summary.finalStopMode, "drain_complete", "summary should include final stop mode");
  return summary;
}

function validateRendererSourceShape() {
  const src = readText(rendererPath);
  assert.ok(src.includes("FULL_APP_CONVERSATION_PENDING_MAX      = 4"), "renderer queue max must remain 4");
  assert.ok(src.includes("conversationQueuePressure"), "renderer must expose queue pressure diagnostics");
  assert.ok(src.includes("conversationQueueFull"), "renderer must expose queue-full diagnostics");
  assert.ok(src.includes("FULL_APP_CONVERSATION_BACKPRESSURE_PAUSE_PENDING"), "renderer must define backpressure pause threshold");
  assert.ok(src.includes("FULL_APP_CONVERSATION_BACKPRESSURE_RESUME_PENDING"), "renderer must define backpressure resume threshold");
  assert.ok(src.includes("conversationBackpressurePaused"), "renderer must expose backpressure pause diagnostics");
  assert.ok(src.includes("conversationBackpressureReason"), "renderer must expose backpressure reason diagnostics");
  assert.ok(src.includes("conversationBackpressureResumeReason"), "renderer must expose backpressure resume diagnostics");
  assert.ok(src.includes("_conversationShouldPauseForBackpressure"), "renderer must evaluate backpressure before recording");
  assert.ok(src.includes("conversationTurnLifecycleCount"), "renderer must expose lifecycle count");
  assert.ok(src.includes("drain_complete"), "renderer must preserve drain_complete state");
  assert.ok(src.includes("queue_full"), "renderer must preserve queue_full reason");
  assert.ok(src.includes("empty_artifact"), "renderer must preserve empty artifact reason");
  assert.ok(src.includes("audioClass"), "diagnostics should carry lifecycle audio class");
  assert.ok(src.includes("\" audio=\" +"), "diagnostics should render lifecycle audio class");
  assert.ok(src.includes("dropStage="), "diagnostics should render drop stage");
  assert.ok(src.includes("ownerVoice="), "diagnostics should render owner voice per-turn state");
  assert.ok(src.includes("candidateWavTemporary"), "diagnostics should include candidate WAV temporary field");
  assert.ok(src.includes("candidateWavDeleted"), "diagnostics should include candidate WAV deleted field");
  assert.ok(!src.includes("ownerVoiceDryRunStatus = \"blocked\""), "Owner Voice dry-run must not become a hard block");
}

function main() {
  validateRendererSourceShape();
  const session = makeLongSessionFixture();
  const summary = validateLongSessionDiagnostics(session);
  const copyable = formatCopyableSummary(summary);

  assert.ok(copyable.includes("total=13"), "copyable summary should include total turns");
  assert.ok(copyable.includes("completed=8"), "copyable summary should include completed turns");
  assert.ok(copyable.includes("queue_full=0"), "copyable summary should show no normal queue_full drops");
  assert.ok(copyable.includes("empty_artifact=1"), "copyable summary should include empty artifact count");
  assert.ok(copyable.includes("backpressure.paused=1"), "copyable summary should include backpressure pause count");
  assert.ok(copyable.includes("backpressure.resumed=1"), "copyable summary should include backpressure resume count");
  assert.ok(copyable.includes("hardFallback.queue_full=1"), "copyable summary should include hard fallback queue_full count");
  assert.ok(copyable.includes("finalPending=0/4"), "copyable summary should include final pending/max");
  assert.ok(copyable.includes("stopMode=drain_complete"), "copyable summary should include stop mode");

  console.log("[PASS] renderer conversation diagnostics source shape");
  console.log("[PASS] synthetic long-session lifecycle invariants");
  console.log("[PASS] copyable runtime summary format");
  console.log(`conversation long-session smoke: PASS ${copyable}`);
}

main();
