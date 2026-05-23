# Phase 5 — Companion Behavior Loop

> **文件狀態：** 設計草案（TASK-107）
> **建立日期：** 2026-05-23
> **前置版本：** v0.5.2（Local Ollama mode、Provider Settings 持久化、expression system 7/10 PNG）

---

## 一、Phase 5 目標

讓克莉絲蒂娜從「聊天框」進化為真正的「桌面寵物」。

目前的體驗是被動的：使用者開口，克莉絲蒂娜才回應。Phase 5 的目標是加入「環境存在感」：即使使用者沒有輸入，克莉絲蒂娜也有自己的狀態，並在適當時機給予輕量互動。

### 核心行為目標

| 行為 | 說明 |
|------|------|
| **Idle 狀態** | 閒置一段時間後，切換到 sleepy / neutral 表情，表示克莉絲蒂娜在等待 |
| **Startup greeting** | 應用程式啟動時，顯示一句迎接語（依時段調整語氣） |
| **Return-from-away greeting** | 使用者長時間未互動後重新輸入，顯示「回來了」的反應 |
| **Time-aware 語氣** | 依前端系統時間（早/午/晚/深夜）調整問候語氣，不上傳時間至伺服器 |
| **Lightweight proactive message** | 在極低頻率下（每 session 最多一次），克莉絲蒂娜主動說一句話，不重複打擾 |
| **Expression integration** | 所有行為狀態都對接現有 `mood → setPetExpression()` 系統 |

### Phase 5 不做

- 不做自動化工具執行（無 shell、無檔案操作）
- 不做任何形式的 AI 自主行動
- 不做排程任務或 cron job
- 不讀 Email / Calendar / 任何系統資料
- 不做 Live2D / 動畫系統

---

## 二、功能範圍

### In Scope（Phase 5 MVP）

- **Idle timer**：前端 `setTimeout`，N 分鐘無互動後切換 sleepy/neutral 表情
- **Startup greeting**：app 啟動時的問候訊息（pre-written 或呼叫 `/chat`）
- **Return greeting**：從 idle 狀態恢復互動時的反應訊息
- **Time slot detection**：前端 `new Date().getHours()` 判斷時段，影響問候語氣
- **Anti-spam cooldown**：session 內最多一次 proactive，並有最短冷卻間隔
- **Expression state integration**：idle → sleepy、greeting → happy、error → worried 等

### Out of Scope（Phase 5 明確排除）

- 自動讀取本機檔案、目錄或 shell 輸出
- 讀取 Email、行事曆、系統通知
- 執行任何系統命令或腳本
- 呼叫任何外部 API（天氣、新聞等）
- 精確定位或 IP 位置推斷
- 在使用者未確認的情況下發送任何訊息或操作系統
- 語音 TTS / STT
- Live2D、Spine、3D 動畫

### Later（Phase 6+ 候選）

- 使用者可設定的 idle timeout 時間
- 記憶感知的 greeting（知道上次聊什麼）
- 自訂問候語庫（使用者可新增）
- 排程提醒（用戶明確設定，非自動推斷）
- 表情動畫轉場效果

---

## 三、安全邊界（永久性限制）

以下限制適用於整個 Phase 5，**不得在任何子任務中繞過**：

| 規則 | 說明 |
|------|------|
| 不自動讀檔 | renderer 不得存取 `fs`、`path`、`electron.shell` 讀取任何本機檔案 |
| 不自動讀 Email / Calendar | 不整合任何郵件或行事曆 API |
| 不自動執行命令 | 不使用 `child_process`、`exec`、`spawn`、shell |
| 不自動呼叫外部 API | Companion 行為完全在本機發生，頂多呼叫本地 backend `/chat` |
| 不使用精確定位 | 只使用 `new Date().getHours()` 判斷時段，不讀 GPS / IP location |
| 不在未確認時操作 | 任何 proactive 訊息都是顯示在 UI 聊天區，不自動點擊、提交或操作系統 |
| `/chat` schema 不變 | `reply / mood / source` 三欄不增不減 |
| Renderer 不直連 Ollama | 所有 LLM 請求仍透過 backend `localhost:8000` |
| API Key 不回傳前端 | 現有安全規則維持不變 |

---

## 四、技術設計草案

### 4.1 架構選擇：純前端 MVP

Phase 5 MVP **不新增 backend endpoint**。所有 companion behavior logic 在 `renderer.js` 前端完成。

**理由：**
- Idle timer / greeting 不需要跨 session 持久化（phase 5 MVP 接受 session-scoped 行為）
- 避免 backend 複雜度
- 未來若需持久化可在 Phase 6 引入 `/companion/state` endpoint

### 4.2 Idle Timer 設計

```
使用者上一次互動時間 = lastActivityTime（初始為 app 啟動時間）

每次使用者輸入 / 點擊 → 重設 lastActivityTime

setInterval（每 60 秒執行一次）：
  elapsed = now - lastActivityTime
  if elapsed > IDLE_THRESHOLD_SHORT (3 分鐘):
    setPetExpression("neutral")
    hintText = "（克莉絲蒂娜靜靜地等著……）"
  if elapsed > IDLE_THRESHOLD_LONG (10 分鐘):
    setPetExpression("sleepy")
    hintText = "（克莉絲蒂娜打了個盹……）"
```

- **不呼叫 `/chat`**：idle 表情只是純 UI 狀態，不觸發 LLM
- 使用者重新輸入 → 重設 idle，恢復原 mood

### 4.3 Startup Greeting

App 啟動（`DOMContentLoaded`）後：

1. 讀取 `new Date().getHours()` 判斷時段
2. 從 pre-written 問候庫取一句（不呼叫 LLM，避免冷啟動等待）
3. 顯示在聊天區（以 `assistant` 樣式呈現）
4. 同時設定 `setPetExpression("happy")`

| 時段 | 小時範圍 | 問候語氣 |
|------|---------|---------|
| 早晨 | 6–11 | 「早啊，今天也要好好加油喔……才不是為了你！」 |
| 下午 | 12–17 | 「呼，你終於來了。」 |
| 傍晚 | 18–22 | 「這麼晚還在工作？……還好吧。」 |
| 深夜 | 23–5 | 「哼，都幾點了還不睡……我才沒有擔心你！」 |

**Anti-spam guard：** `hasGreetedThisSession = true` 設定後不再重複觸發。

### 4.4 Return-from-Away Greeting

條件：
- 使用者在 idle 狀態（`elapsed > RETURN_THRESHOLD`，建議 15 分鐘）後送出第一則訊息
- 此時在正常 `/chat` 回應**之前**，插入一句 return greeting（pre-written）

```
if (isReturnFromAway && !hasReturnGreetedThisSession):
  displaySystemMessage("歡迎回來…才沒有等你！")
  setPetExpression("happy")
  hasReturnGreetedThisSession = true
  // 接著正常送出 /chat
```

### 4.5 Anti-Spam 機制

| 控制項 | 設計 |
|--------|------|
| Startup greeting | 每 session 最多一次（flag） |
| Return greeting | 每次從 long-idle 回來最多一次（flag，可重設） |
| Proactive message | 每 session 最多一次，且需距上次互動 30+ 分鐘（Phase 5 後期再加） |
| Idle 表情切換 | 不顯示文字訊息，只換表情，無 spam 疑慮 |

### 4.6 Mood / Expression 對接

沿用現有 `setPetExpression(mood)` 函式，不修改其邏輯：

| Companion 狀態 | 呼叫 mood |
|--------------|-----------|
| App 啟動 / greeting | `"happy"` |
| 短暫 idle（3 分鐘） | `"neutral"` |
| 長時間 idle（10 分鐘） | `"sleepy"` |
| Return from away | `"happy"` |
| `/chat` 回應後 | 沿用 backend 回傳的 `mood` 欄位（現有行為不變） |

### 4.7 是否新增 `/companion/tick`？

**Phase 5 MVP：不新增。**

純前端計時器已足夠 MVP 需求。`/companion/tick` 的使用場景（跨 session 狀態、server-side 定時任務）列為 Phase 6 候選設計。

---

## 五、MVP 任務拆分

### TASK-108：Idle State UI Behavior

**範圍：** renderer.js 前端 idle timer
- 新增 `lastActivityTime` 追蹤
- `setInterval` 每分鐘檢查 idle 時間
- 3 分鐘 → `setPetExpression("neutral")` + hint text
- 10 分鐘 → `setPetExpression("sleepy")` + hint text
- 使用者互動 → 重設 idle 計時
- **不新增 backend endpoint**
- **不修改 `/chat` schema**

**驗收：** renderer smoke PASS、node --check PASS、idle 表情在閒置 N 秒後正確切換（測試用短 timeout）

---

### TASK-109：Startup Greeting

**範圍：** app 啟動時顯示一句 pre-written 問候語
- `DOMContentLoaded` 後觸發
- 依 `new Date().getHours()` 選擇時段語氣（4 個時段）
- 問候語以 assistant 樣式顯示在聊天區
- `hasGreetedThisSession` flag 防止重複
- `setPetExpression("happy")` 同步執行
- **不呼叫 `/chat`**（pre-written，不依賴 LLM 可用性）

**驗收：** app 啟動可見問候語、不同時段語氣正確、node --check PASS、renderer smoke PASS

---

### TASK-110：Return-from-Away Greeting

**範圍：** 從長時間 idle 回來的反應
- `RETURN_THRESHOLD = 15 分鐘`
- 使用者在 long-idle 後送出訊息 → 插入 return greeting（pre-written）
- greeting 在 `/chat` 請求發出前顯示
- `hasReturnGreetedThisSession` flag 控制（每次 long-idle 後重設一次）
- `setPetExpression("happy")`
- **不修改 `/chat` 請求或回應格式**

**驗收：** long-idle 後互動可見 return greeting、短時間 idle 不觸發、node --check PASS

---

### TASK-111：Expression Timing Polish

**範圍：** 細化表情切換時機，確保順暢體驗
- `/chat` loading 期間顯示 `"focused"` 表情（現有行為確認或補強）
- `/chat` 回應後立即套用 backend `mood` 欄位（確認不被 idle timer 覆蓋）
- idle 表情切換加入 CSS transition（若已有則確認一致）
- 確保 idle timer 不與 `/chat` mood 衝突（idle 只在無活躍請求時觸發）

**驗收：** `/chat` 回應 mood 不被 idle 覆蓋、loading 表情正確、node --check PASS、renderer smoke PASS

---

### TASK-112：Companion Behavior Smoke Tests

**範圍：** 為 TASK-108～111 新增 renderer smoke 測試
- idle timer 單元測試（mock `Date.now()`，驗證 `setPetExpression` 呼叫）
- startup greeting 測試（DOM 載入後訊息存在）
- return greeting 測試（idle 後首次互動觸發、短 idle 不觸發）
- expression 衝突測試（`/chat` response mood 優先於 idle mood）
- **不修改 backend tests**
- 預期：renderer smoke test count 從 24 增加

**驗收：** `npm run test:renderer` PASS、新增測試覆蓋上述場景

---

## 六、任務順序建議

```
TASK-108 (idle timer)
    ↓
TASK-109 (startup greeting)
    ↓
TASK-110 (return greeting)
    ↓
TASK-111 (expression polish)
    ↓
TASK-112 (smoke tests)
```

TASK-108 是基礎，後續任務依賴其建立的 `lastActivityTime` 與 idle 狀態機制。TASK-112 在所有行為完成後補充測試覆蓋。

---

## 七、Phase 5 安全審查清單

完成每個任務前，確認：

- [ ] Renderer 沒有新增 `localhost:11434` 或任何 Ollama 直連
- [ ] 沒有新增 `fs`、`child_process`、`exec` 等 Node.js 系統模組
- [ ] 沒有新增讀取 Email / Calendar 的程式碼
- [ ] `/chat` schema 仍為 `reply / mood / source`
- [ ] `node --check` 所有 renderer 檔案通過
- [ ] `npm run test:renderer` 通過
- [ ] 沒有新增外部 HTTP 請求（除 `localhost:8000`）
- [ ] API Key 沒有出現在前端任何位置

---

## 八、未來設計備忘（Phase 6+）

以下為 Phase 5 明確排除、但未來可能引入的設計方向，記錄於此備查：

| 功能 | 備忘 |
|------|------|
| `/companion/tick` endpoint | 若需跨 session 持久化 companion 狀態再引入 |
| 使用者可設定 idle timeout | 透過 Provider Settings 延伸或新增 Companion Settings |
| 記憶感知 greeting | 整合 `/memory/context-preview` 取得上次對話主題 |
| 排程提醒 | 使用者明確設定，需獨立的 `/reminder` 設計與安全審查 |
| Proactive LLM message | 使用 `/chat` 加特殊 system context，需防 spam 機制完整後再引入 |
| 表情動畫轉場 | CSS keyframe 或 Web Animation API，不需 Live2D |

---

*文件由 TASK-107 建立。下一步：執行 TASK-108 Idle State UI Behavior。*
