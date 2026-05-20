# Dragon Pet AI

AI 驅動的桌面螢幕寵物 — 有個性、有記憶的桌面同伴。

---

## 目前狀態

**Phase 3 完成 — Memory-Aware Chat and Audit Inspection**
**Phase 4 進行中 — LLM Adapter Integration（TASK-049 Secure Key Storage Design 進行中）**

Backend（FastAPI）和 Desktop（Electron）均可運行。Mock chat、Manual Memory、Memory-Aware Chat（two-layer gate）、Audit Inspection API 和 Audit Logs UI 全部完成並通過 runtime smoke check。pytest 最新結果：356 passed。Real provider adapter 已在 TASK-035 behind feature flags；Anthropic contract 已用 mocked HTTP 驗證（TASK-037）。`/chat` wiring 已放在 `LLM_CHAT_ENABLED` 後面，default false；mock runtime smoke passed（TASK-041）；live provider 仍預設停用。

BYOK 已設計完成（TASK-045）：推薦方向 BYOK desktop app / personal companion，使用者自帶 API key 並承擔 provider billing。Usage meter 設計完成（TASK-046）：14 個追蹤欄位、token 估算規則、privacy 邊界。Provider Settings UI 設計完成（TASK-047）：UI sections、9-step settings flow、security boundaries、error UX。Backend Provider Settings API 設計完成（TASK-048）：5 個 endpoints、write-only key handling、safe status model、test connection safety。Secure Key Storage 設計進行中（TASK-049）：4 個 storage options 比較、MVP 推薦 env var only、future desktop 推薦 OS keychain、plain SQLite 明確禁止。尚未實作 settings API、settings UI、或 persistent key storage；API key 目前仍為 env-only（dev phase）；real provider 預設關閉。manual live smoke 暫緩，直到使用者明確接受成本風險。詳見 `docs/BYOK_PRODUCT_AND_SETTINGS.md`、`docs/USAGE_METER_DESIGN.md`、`docs/PROVIDER_SETTINGS_UI_DESIGN.md`、`docs/PROVIDER_SETTINGS_API_DESIGN.md`、`docs/COST_AND_MONETIZATION.md`。

---

## 快速啟動

### 1. Backend（FastAPI）

```bash
cd backend

# 建立虛擬環境（Windows）
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 啟動開發伺服器
uvicorn app.main:app --reload --port 8000
```

啟動後可驗證：
```bash
# Health check
curl http://localhost:8000/health

# Mock chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!"}'
```

### 2. Desktop（Electron）

> 需要先確認 backend 已在 localhost:8000 執行。

```bash
cd apps/desktop
npm install
npm start
```

桌面視窗啟動後：
- 自動呼叫 `/health` 確認 backend 連線
- 在輸入框輸入訊息，按 Send 或 Enter 送出
- 顯示 mock 回應（`source: "mock"`，無真實 AI）

---

## 目前功能

| 功能 | 狀態 |
|---|---|
| `GET /health` — liveness check | ✅ 可用 |
| `POST /chat` — mock 角色回應 | ✅ 可用（無 AI） |
| Desktop 視窗 | ✅ 可用 |
| Desktop ↔ Backend 通訊 | ✅ 可用 |
| SQLite 資料庫初始化 | ✅ 可用 |
| Manual Memory API (`POST/GET/DELETE /memory`) | ✅ 可用 |
| Memory Context Preview (`GET /memory/context-preview`) | ✅ 可用 |
| Memory-aware chat toggle (`use_memory`, two-layer gate) | ✅ 可用 |
| `GET /memory/audit` — read-only audit inspection API | ✅ 可用（TASK-026） |
| Desktop Audit Logs UI | ✅ 可用（TASK-027） |

---

## 目前限制（TASK-003）

以下功能尚未實作：

- `/chat` 回傳的是 hardcoded mock 回應，**未串接任何 AI API**
- 無資料庫資料表（SQLite 檔案建立但為空）
- 無記憶系統、無角色狀態持久化
- 無語音（TTS / STT）
- 無 Live2D 動畫
- 無 shell 指令執行能力
- 無使用者檔案存取能力

---

## 如何閱讀 docs/

| 文件 | 說明 |
|---|---|
| `docs/TASKS.md` | 目前任務狀態與進度追蹤 |
| `docs/PHASE3_DEMO_SUMMARY.md` | Phase 3 demo summary、safety model、demo flow |
| `docs/PHASE4_PLAN.md` | Phase 4 規劃：候選方向、建議路徑、安全約束、任務序列 |
| `docs/LLM_ADAPTER_DESIGN.md` | LLM Adapter 架構設計：provider interface、feature flags、API key 安全規則、error handling（含 TASK-034R Opus 審查結果與 TASK-034F 修補） |
| `docs/LLM_PROVIDER_CONTRACT.md` | TASK-036 vendor contract：Anthropic request / response / error mapping、mocked fixtures、manual smoke checklist |
| `docs/CHAT_LLM_WIRING_DESIGN.md` | TASK-039 chat wiring design：`LLM_CHAT_ENABLED`、/chat adapter flow、fallback、memory interaction、logging/test plan |
| `docs/CHAT_LLM_REAL_PROVIDER_WIRING_DESIGN.md` | TASK-042 real-provider /chat wiring design：flag matrix、source behavior、fallback、memory independence、manual live smoke prerequisites |
| `docs/COST_AND_MONETIZATION.md` | TASK-044 cost control and go/no-go design：BYOK-first direction、live smoke criteria、monetization options |
| `docs/BYOK_PRODUCT_AND_SETTINGS.md` | TASK-045 BYOK product/settings design：key ownership、storage options、settings UX、安全邊界、usage visibility |
| `docs/USAGE_METER_DESIGN.md` | TASK-046 usage meter design：token/cost tracking、estimation rules、privacy boundaries、storage options、UI requirements |
| `docs/PROVIDER_SETTINGS_UI_DESIGN.md` | TASK-047 provider settings UI design：UI sections、settings flow（9 steps）、security boundaries、error UX（7 types）、memory interaction、non-goals、implementation sequence |
| `docs/PROVIDER_SETTINGS_API_DESIGN.md` | TASK-048 backend provider settings API design：5 endpoints、write-only key handling、safe status model、test connection safety rules、usage meter integration、security boundaries、error categories |
| `docs/SECURE_KEY_STORAGE_DESIGN.md` | TASK-049 secure key storage design：4 storage options、MVP recommendation（env var）、future desktop recommendation（OS keychain）、key lifecycle、redaction rules、threat model、testing requirements |
| `docs/PRD.md` | 產品需求文件（MVP 定義） |
| `docs/ARCHITECTURE.md` | 系統架構設計 |
| `docs/MEMORY_SYSTEM.md` | 記憶系統設計 |
| `docs/CHARACTER_SPEC.md` | 角色設定與人格規格 |
| `docs/ROADMAP.md` | 開發路線圖 |
| `docs/STREAMER_COMPANION_MODE.md` | Future side track（未排入 roadmap）：直播 companion 模式設計探索 |

建議閱讀順序：`TASKS.md` → `PRD.md` → `ARCHITECTURE.md` → 其他文件

> **Future Side Track（未排入 roadmap）：** Streamer Companion Mode — 未來可能的直播應用方向，讓 dragon-pet 成為 OBS overlay 角色、回應 Twitch/YouTube 事件與 chat 指令。此方向需要 Phase 4 LLM adapter 穩定、TTS 完成、以及專屬安全設計，目前不在實作計畫內。詳見 `docs/STREAMER_COMPANION_MODE.md`。

---

## 目錄結構

```
dragon-pet-ai/
  apps/
    desktop/
      package.json
      src/
        main.js               # Electron main process
        renderer/
          index.html          # 主視窗 HTML
          renderer.js         # UI 邏輯、backend 呼叫
          styles.css          # 樣式
  backend/
    app/
      main.py                 # FastAPI 入口
      api/routes.py           # /health, /chat
      db/database.py          # SQLModel engine 佔位
      schemas/chat.py         # Request / Response schema
    requirements.txt
    README.md
  docs/                       # 所有設計文件
  scripts/                    # 工具腳本（待用）
  .env.example
  README.md
```

---

## 開發順序（Roadmap 摘要）

| Phase | 內容 |
|---|---|
| Phase 0 | 專案定義、規格文件（TASK-000 ~ 002） |
| Phase 1 | Runtime Skeleton — FastAPI + Electron（TASK-003） ← 目前 |
| Phase 2 | Chat + Character — 接 LLM、角色 prompt |
| Phase 3 | Memory + State — SQLite 持久化、長期記憶 |
| Phase 4 | Voice + Presence — TTS、情緒表情 |
| Phase 5 | Assistant — Task List、專案輔助、工具執行 |

詳見 `docs/ROADMAP.md`。

---

## Backend Test

```bash
cd backend
python -m pytest
```

---

## Memory Skeleton

- Backend has a local SQLite `Memory` table skeleton for future long-term memory.
- Manual memory API exists:
  - `POST /memory` creates explicit memory.
  - `GET /memory` lists active memory records.
  - `GET /memory/context-preview` previews active memories as context text.
  - `DELETE /memory/{id}` deactivates memory.
- Desktop has a Memory Management placeholder for creating, listing, deactivating, and previewing local memories.
- Memory is local SQLite only and is not used by `/chat` yet.
- Manual memory injection is designed but not implemented.
- Memory injection design was safety-reviewed; implementation remains disabled until future work.
- Future runtime wiring will require `MEMORY_INJECTION_ENABLED`, default `False`.
- Approved memory context builder exists but is not connected to `/chat` yet.
- Approved context building applies type allowlist, confidence filtering, sensitive-content filtering, and 5-memory / 1500-character caps.
- Prompt formatting uses delimiters and a reference-only safety instruction.
- `MemoryInjectionAudit` table records injection events when memory-aware chat runs: selected memory IDs, count, total context chars, and feature flag state.
- Audit rows store selected IDs and aggregate metadata only — raw memory content is never stored in audit rows.
- An audit inspection design exists (TASK-025): a future `GET /memory/audit` endpoint and UI section will surface safe audit metadata. Not yet implemented.
- Future audit inspection will show: id, created_at, selected_memory_ids, selected_count, total_context_chars, feature_flag_enabled. It will never expose raw memory content or prompt text.
- Manual memory is intended to remain inspectable and controllable before any future chat use.
- Context preview does not use semantic retrieval and does not update `last_used_at`.
- No vector database is connected.
- No automatic memory extraction is implemented.
- A **memory-aware chat UI toggle** is implemented (TASK-023) using a two-layer safety model:
  - Backend global gate: `MEMORY_INJECTION_ENABLED` (set before startup, defaults to `false`)
  - Per-request opt-in: `use_memory` field in the POST `/chat` body (defaults to `false`)
  - Only when both are `true` may `/chat` use approved memory context.
  - The desktop UI shows a "Use approved memories" checkbox near the chat input.
  - `/chat` response schema remains `reply / mood / source` regardless of flag or toggle state.
  - Memory content is never returned in the `/chat` response.
  - No `PATCH /config` endpoint. The backend flag is startup-time only.
  - No Electron IPC required. The frontend sends `use_memory` in the POST body directly.

---

## 開發規範

- 每個 TASK 有明確 scope，不得自行擴張
- 所有設計決策記錄於 `docs/` 對應文件中
- 功能實作前必須先完成對應規格文件
- 任何可執行系統操作的功能必須先設計安全層
