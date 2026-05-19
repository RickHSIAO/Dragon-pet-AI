# Dragon Pet AI

AI 驅動的桌面螢幕寵物 — 有個性、有記憶的桌面同伴。

---

## 目前狀態

**TASK-003 - Basic Runtime Skeleton（進行中）**

Phase 1 第一步：最小可跑骨架。
Backend（FastAPI）和 Desktop（Electron）已建立，`/health` 和 `/chat` mock 端點可用。
尚未串接真實 AI API。

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
| SQLite 資料庫初始化 | ✅ 佔位（無資料表） |

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
| `docs/PRD.md` | 產品需求文件（MVP 定義） |
| `docs/ARCHITECTURE.md` | 系統架構設計 |
| `docs/MEMORY_SYSTEM.md` | 記憶系統設計 |
| `docs/CHARACTER_SPEC.md` | 角色設定與人格規格 |
| `docs/ROADMAP.md` | 開發路線圖 |

建議閱讀順序：`TASKS.md` → `PRD.md` → `ARCHITECTURE.md` → 其他文件

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

## 開發規範

- 每個 TASK 有明確 scope，不得自行擴張
- 所有設計決策記錄於 `docs/` 對應文件中
- 功能實作前必須先完成對應規格文件
- 任何可執行系統操作的功能必須先設計安全層
