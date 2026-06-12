"use strict";

const { contextBridge, ipcRenderer } = require("electron");

const PET_SHOW_WINDOW_CHANNEL = "pet:show-window";
const PET_SPEECH_UPDATE_CHANNEL = "pet:speech-update";
const PET_CHAT_MIRROR_RECEIVED_CHANNEL = "pet:chat-mirror-received";  // TASK-193
const CHAT_HISTORY_APPEND_CHANNEL = "chat-history:append";  // TASK-194
const CHAT_HISTORY_LOAD_CHANNEL   = "chat-history:load";    // TASK-194
const CHAT_HISTORY_CLEAR_CHANNEL  = "chat-history:clear";   // TASK-194
const SCREEN_CAPTURE_ONCE_CHANNEL   = "screen:capture-once";    // TASK-171A
const SCREEN_CAPTURE_WINDOW_CHANNEL = "screen:capture-window";  // TASK-176
const CLIPBOARD_WRITE_TEXT_CHANNEL  = "clipboard:write-text";   // TASK-196
const PET_UNREAD_DOT_CHANNEL = "pet:unread-dot";                // TASK-204
const CHAT_EXPORT_CHANNEL    = "chat:export-transcript";        // TASK-205
const PET_EXPRESSION_SUGGESTION_CHANNEL = "pet:expression-suggestion"; // TASK-218
const PET_REACTION_BUBBLE_CHANNEL = "pet:reaction-bubble"; // TASK-220
const STT_TRANSCRIBE_CHANNEL = "stt:transcribe";            // TASK-241
const OWNER_VOICE_CANDIDATE_WAV_CREATE_CHANNEL = "owner-voice:candidate-wav-temp:create"; // TASK-270
const OWNER_VOICE_CANDIDATE_WAV_DELETE_CHANNEL = "owner-voice:candidate-wav-temp:delete"; // TASK-270
const EXPRESSION_SUGGESTION_ALLOWLIST = new Set([               // TASK-218: preload-side allowlist
  "neutral", "focused", "happy", "proud", "annoyed", "sleepy",
]);
const REACTION_BUBBLE_TEXT_BY_ID = Object.freeze({              // TASK-220: preload-side fixed text mapping
  user_active: "哼，總算肯理吾了。",
  message_management: "整理好了？手腳還算俐落。",
  correction: "又改？下次可要想清楚。",
  reset: "清空了。重新開始也無妨。",
  attention_returned: "回來了？吾才沒有等汝。",
  none: "",
});
const REACTION_BUBBLE_ALLOWLIST = new Set(Object.keys(REACTION_BUBBLE_TEXT_BY_ID));
const REACTION_BUBBLE_SOURCE = "interaction_reaction_bubble";
const REACTION_BUBBLE_TTL_MS = 3000;

function sanitizePetSpeechPayload(payload = {}) {
  return {
    reply: typeof payload.reply === "string" ? payload.reply : "",
    mood: typeof payload.mood === "string" ? payload.mood : "neutral",
    source: typeof payload.source === "string" ? payload.source : "unknown",
  };
}

// TASK-193: expose listener for Pet chat mirror events forwarded from main.
// Only text payloads are forwarded — main sanitizes before sending to this window.
function onChatMirrorFromPet(callback) {
  if (typeof callback !== "function") return () => {};
  const listener = (_event, payload) => {
    callback({
      userMessage: typeof payload.userMessage === "string" ? payload.userMessage : "",
      reply: typeof payload.reply === "string" ? payload.reply : "",
      mood: typeof payload.mood === "string" ? payload.mood : "neutral",
      source: typeof payload.source === "string" ? payload.source : "unknown",
      inputMethod: payload.inputMethod === "voice" ? "voice" : "text",  // TASK-195
    });
  };
  ipcRenderer.on(PET_CHAT_MIRROR_RECEIVED_CHANNEL, listener);
  return () => ipcRenderer.removeListener(PET_CHAT_MIRROR_RECEIVED_CHANNEL, listener);
}

// TASK-194: validate entry before forwarding to main — only safe text fields accepted.
// TASK-206: ts is now forwarded so stored timestamps match display time.
function sanitizeChatHistoryEntry(entry = {}) {
  return {
    role: entry.role === "user" || entry.role === "pet" ? entry.role : "",
    text: typeof entry.text === "string" ? entry.text.slice(0, 2000) : "",
    source: typeof entry.source === "string" ? entry.source.slice(0, 30) : "unknown",
    ts: typeof entry.ts === "number" && entry.ts > 0 ? entry.ts : 0,
  };
}

function sanitizeReactionBubblePayload(payload = {}) {
  const rawId = typeof payload === "object" && payload !== null &&
    typeof payload.id === "string" ? payload.id : "";
  const safeId = REACTION_BUBBLE_ALLOWLIST.has(rawId) ? rawId : "none";
  return {
    id: safeId,
    text: REACTION_BUBBLE_TEXT_BY_ID[safeId] || "",
    source: REACTION_BUBBLE_SOURCE,
    ts: Date.now(),
    ttlMs: REACTION_BUBBLE_TTL_MS,
  };
}

contextBridge.exposeInMainWorld(
  "dragonPet",
  Object.freeze({
    showPetWindow: () => ipcRenderer.invoke(PET_SHOW_WINDOW_CHANNEL),
    updatePetSpeech: (payload) =>
      ipcRenderer.invoke(PET_SPEECH_UPDATE_CHANNEL, sanitizePetSpeechPayload(payload)),
    // TASK-171A: narrow Full App screenshot capture surface.
    captureScreen: () => ipcRenderer.invoke(SCREEN_CAPTURE_ONCE_CHANNEL),
    // TASK-176: explicit window picker capture surface.
    captureWindow: () => ipcRenderer.invoke(SCREEN_CAPTURE_WINDOW_CHANNEL),
    // TASK-193: register listener for Pet chat mirror events.
    onChatMirrorFromPet,
    // TASK-194: chat history persistence IPC.
    chatHistoryAppend: (entry) => ipcRenderer.invoke(CHAT_HISTORY_APPEND_CHANNEL, sanitizeChatHistoryEntry(entry)),
    chatHistoryLoad:   () => ipcRenderer.invoke(CHAT_HISTORY_LOAD_CHANNEL),
    chatHistoryClear:  () => ipcRenderer.invoke(CHAT_HISTORY_CLEAR_CHANNEL),
    // TASK-196: narrow clipboard IPC bridge — routes via main IPC to avoid file:// secure-context restriction.
    writeClipboardText: (text) => {
      if (typeof text !== "string") return Promise.resolve(false);
      const safe = text.slice(0, 20000);
      if (!safe) return Promise.resolve(false);
      return ipcRenderer.invoke(CLIPBOARD_WRITE_TEXT_CHANNEL, safe);
    },
    // TASK-204: forward unread count to Pet Window via main. Payload is count-only — no message content.
    notifyUnreadDot: (count) => {
      const safe = typeof count === "number" && count >= 0 ? count : 0;
      return ipcRenderer.invoke(PET_UNREAD_DOT_CHANNEL, { unreadCount: safe });
    },
    // TASK-218: narrow expression suggestion IPC — expression-only, no speech, no bubble, no TTS.
    sendPetExpressionSuggestion: (payload) => {
      const rawExpression = typeof payload === "object" && payload !== null &&
        typeof payload.expression === "string" ? payload.expression : "";
      const safeExpression = EXPRESSION_SUGGESTION_ALLOWLIST.has(rawExpression)
        ? rawExpression : "neutral";
      return ipcRenderer.invoke(PET_EXPRESSION_SUGGESTION_CHANNEL, {
        expression: safeExpression,
        source: "interaction_expression_suggestion",
        ts: Date.now(),
      });
    },
    // TASK-220: narrow reaction bubble IPC — fixed allowlist text only, no raw user text.
    sendPetReactionBubble: (payload) =>
      ipcRenderer.invoke(PET_REACTION_BUBBLE_CHANNEL, sanitizeReactionBubblePayload(payload)),
    // TASK-241: narrow STT IPC bridge for Full App voice input.
    // Accepts ArrayBuffer only — no file paths, no audio storage, no path traversal.
    // Returns { transcript, status } from backend /stt/transcribe via existing handler.
    transcribeAudio: (arrayBuffer, options = {}) => {
      if (!(arrayBuffer instanceof ArrayBuffer)) {
        return Promise.resolve({ status: "error", transcript: "" });
      }
      const model = options && typeof options.model === "string" &&
        ["tiny", "base", "small"].includes(options.model) ? options.model : "";
      return ipcRenderer.invoke(STT_TRANSCRIBE_CHANNEL, model ? { audio: arrayBuffer, model } : arrayBuffer);
    },
    // TASK-270: narrow Owner Voice candidate WAV temp-file bridge.
    // Accepts already-prepared WAV bytes only; no paths, transcripts, embeddings,
    // centroid, or generic filesystem methods are exposed to renderer code.
    createOwnerVoiceCandidateWavTemp: (arrayBuffer) => {
      if (!(arrayBuffer instanceof ArrayBuffer)) {
        return Promise.resolve({ ok: false, reason: "candidate_wav_temp_unavailable" });
      }
      return ipcRenderer.invoke(OWNER_VOICE_CANDIDATE_WAV_CREATE_CHANNEL, arrayBuffer);
    },
    deleteOwnerVoiceCandidateWavTemp: (filePath) => {
      if (typeof filePath !== "string" || !filePath) {
        return Promise.resolve({ ok: false, deleted: false, reason: "invalid_candidate_path" });
      }
      return ipcRenderer.invoke(OWNER_VOICE_CANDIDATE_WAV_DELETE_CHANNEL, filePath);
    },
    // TASK-205: narrow file save IPC — opens Save Dialog via main, writes plain text only.
    // Content capped at 200000 chars; defaultPath capped at 255 chars.
    saveTextFile: ({ defaultPath, content } = {}) => {
      if (typeof content !== "string") return Promise.resolve({ ok: false, error: "invalid_content" });
      const safeContent  = content.slice(0, 200000);
      const safePath     = typeof defaultPath === "string" ? defaultPath.slice(0, 255) : "dragon-pet-chat.txt";
      return ipcRenderer.invoke(CHAT_EXPORT_CHANNEL, { defaultPath: safePath, content: safeContent });
    },
  })
);
