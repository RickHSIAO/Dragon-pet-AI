"use strict";
/**
 * TASK-175: region picker preload.
 * Runs in the region-picker BrowserWindow (contextIsolation: true, nodeIntegration: false).
 * User drags a rectangle; on mouseup sends screen-region:selected with
 * { x, y, width, height } in CSS logical pixels relative to this window's top-left,
 * which is the same as the selected display's top-left (main process positions
 * the window at display.bounds).
 * Esc sends screen-region:cancel.
 * Main process owns DPI conversion, crop, and screen capture.
 * This preload never sees raw display IDs or physical pixel values.
 */
const { ipcRenderer } = require("electron");

const SCREEN_REGION_SELECTED_CHANNEL = "screen-region:selected";
const SCREEN_REGION_CANCEL_CHANNEL   = "screen-region:cancel";

window.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("region-canvas");
  if (!canvas) return;

  canvas.width  = window.innerWidth;
  canvas.height = window.innerHeight;
  const ctx = canvas.getContext("2d");

  let dragging = false;
  let startX = 0, startY = 0, endX = 0, endY = 0;

  function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }

  function draw() {
    const W = canvas.width;
    const H = canvas.height;
    ctx.clearRect(0, 0, W, H);

    if (!dragging) {
      ctx.fillStyle = "rgba(0,0,0,0.50)";
      ctx.fillRect(0, 0, W, H);
      ctx.textAlign = "center";
      ctx.fillStyle = "rgba(255,255,255,0.95)";
      ctx.font = "bold 28px system-ui,-apple-system,sans-serif";
      ctx.fillText("拖曳選取螢幕區域", W / 2, H / 2 - 18);
      ctx.font = "16px system-ui,-apple-system,sans-serif";
      ctx.fillStyle = "rgba(255,255,255,0.70)";
      ctx.fillText("Esc 取消", W / 2, H / 2 + 18);
      return;
    }

    const rx = Math.min(startX, endX);
    const ry = Math.min(startY, endY);
    const rw = Math.abs(endX - startX);
    const rh = Math.abs(endY - startY);

    // Dark overlay everywhere, then punch through for the selected region
    ctx.fillStyle = "rgba(0,0,0,0.45)";
    ctx.fillRect(0, 0, W, H);
    ctx.clearRect(rx, ry, rw, rh);

    // Selection border
    ctx.strokeStyle = "#29a8ff";
    ctx.lineWidth = 2;
    ctx.setLineDash([]);
    ctx.strokeRect(rx, ry, rw, rh);

    // Corner grab handles (visual only)
    const hs = 6;
    ctx.fillStyle = "#29a8ff";
    for (const [cx, cy] of [
      [rx, ry], [rx + rw, ry], [rx, ry + rh], [rx + rw, ry + rh],
    ]) {
      ctx.fillRect(cx - hs / 2, cy - hs / 2, hs, hs);
    }

    // Size label (only when large enough to be legible)
    if (rw > 40 && rh > 16) {
      const labelText = `${Math.round(rw)} × ${Math.round(rh)}`;
      ctx.font = "bold 13px system-ui,-apple-system,monospace";
      ctx.textAlign = "left";
      const labelX = rx + 4;
      const labelY = ry > 22 ? ry - 5 : ry + rh + 17;
      const textW = ctx.measureText(labelText).width;
      ctx.fillStyle = "rgba(0,0,0,0.55)";
      ctx.fillRect(labelX - 2, labelY - 13, textW + 8, 17);
      ctx.fillStyle = "#ffffff";
      ctx.fillText(labelText, labelX + 2, labelY);
    }

    // Persistent cancel hint
    ctx.font = "13px system-ui,-apple-system,sans-serif";
    ctx.textAlign = "right";
    ctx.fillStyle = "rgba(255,255,255,0.55)";
    ctx.fillText("Esc 取消", W - 10, H - 10);
  }

  window.addEventListener("mousedown", (e) => {
    dragging = true;
    startX = clamp(e.clientX, 0, canvas.width);
    startY = clamp(e.clientY, 0, canvas.height);
    endX = startX;
    endY = startY;
    draw();
  });

  window.addEventListener("mousemove", (e) => {
    if (!dragging) return;
    endX = clamp(e.clientX, 0, canvas.width);
    endY = clamp(e.clientY, 0, canvas.height);
    draw();
  });

  window.addEventListener("mouseup", (e) => {
    if (!dragging) return;
    dragging = false;
    endX = clamp(e.clientX, 0, canvas.width);
    endY = clamp(e.clientY, 0, canvas.height);
    const rx = Math.min(startX, endX);
    const ry = Math.min(startY, endY);
    const rw = Math.abs(endX - startX);
    const rh = Math.abs(endY - startY);
    ipcRenderer.send(SCREEN_REGION_SELECTED_CHANNEL, { x: rx, y: ry, width: rw, height: rh });
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      ipcRenderer.send(SCREEN_REGION_CANCEL_CHANNEL);
    }
  });

  draw();
});
