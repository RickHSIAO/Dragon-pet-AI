/**
 * dragon-pet-ai — renderer process (TASK-003 skeleton)
 *
 * Responsibilities:
 * - Read user message from input
 * - POST to backend /chat
 * - Display user message and pet reply in chat area
 * - Show clear error if backend is unreachable
 *
 * Safety: no shell execution, no file access, no AI API calls here.
 * Backend URL is read from the URL query param set by main.js.
 */

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const params = new URLSearchParams(window.location.search);
const BACKEND_URL = params.get("backend") || "http://localhost:8000";

// ---------------------------------------------------------------------------
// DOM refs
// ---------------------------------------------------------------------------
const chatArea    = document.getElementById("chat-area");
const msgInput    = document.getElementById("message-input");
const sendBtn     = document.getElementById("send-btn");
const moodLabel   = document.getElementById("mood-label");

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
let currentMood = "neutral";
let isSending   = false;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function appendMessage(role, text) {
  const wrap = document.createElement("div");
  wrap.className = `message ${role}`;

  const sender = document.createElement("div");
  sender.className = "sender";
  sender.textContent =
    role === "user"   ? "You" :
    role === "pet"    ? "Dragon Pet" :
    role === "error"  ? "Error" :
    "System";

  const body = document.createElement("div");
  body.textContent = text;

  wrap.appendChild(sender);
  wrap.appendChild(body);
  chatArea.appendChild(wrap);
  chatArea.scrollTop = chatArea.scrollHeight;
  return wrap;
}

function setMood(mood) {
  currentMood = mood || "neutral";
  moodLabel.textContent = currentMood;
}

function setSending(state) {
  isSending = state;
  sendBtn.disabled = state;
  msgInput.disabled = state;
  sendBtn.textContent = state ? "..." : "Send";
}

// ---------------------------------------------------------------------------
// Backend call
// ---------------------------------------------------------------------------
async function sendMessage(text) {
  if (isSending || !text.trim()) return;
  setSending(true);

  // Show user message immediately
  appendMessage("user", text);
  msgInput.value = "";
  msgInput.style.height = "auto";

  try {
    const res = await fetch(`${BACKEND_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    if (!res.ok) {
      throw new Error(`Backend returned HTTP ${res.status}`);
    }

    const data = await res.json();
    appendMessage("pet", data.reply);
    setMood(data.mood);

  } catch (err) {
    const isNetworkError = err instanceof TypeError && err.message.includes("fetch");
    const errText = isNetworkError
      ? `Cannot reach backend at ${BACKEND_URL}.\nMake sure the backend is running:\n  cd backend && uvicorn app.main:app --reload`
      : `Something went wrong: ${err.message}`;

    appendMessage("error", errText);
  } finally {
    setSending(false);
    msgInput.focus();
  }
}

// ---------------------------------------------------------------------------
// Event listeners
// ---------------------------------------------------------------------------
sendBtn.addEventListener("click", () => {
  sendMessage(msgInput.value);
});

msgInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage(msgInput.value);
  }
});

// Auto-grow textarea
msgInput.addEventListener("input", () => {
  msgInput.style.height = "auto";
  msgInput.style.height = Math.min(msgInput.scrollHeight, 100) + "px";
});

// ---------------------------------------------------------------------------
// Startup
// ---------------------------------------------------------------------------
(async function startup() {
  appendMessage("status", "Connecting to backend...");

  try {
    const res = await fetch(`${BACKEND_URL}/health`);
    const data = await res.json();
    if (data.status === "ok") {
      // Remove the connecting status
      chatArea.lastChild.remove();
      appendMessage("pet", "Hey. I'm here. What's on your mind?");
      setMood("neutral");
    } else {
      throw new Error("Unexpected health response");
    }
  } catch {
    chatArea.lastChild.remove();
    appendMessage(
      "error",
      `Backend not reachable at ${BACKEND_URL}.\nStart the backend first:\n  cd backend\n  uvicorn app.main:app --reload`
    );
  }

  msgInput.focus();
})();
