# FTS5 - OpenClaw 對話歷史搜尋系統

> 🤖 讓你的 AI 助理記住一切 — 內建 Self-Improving 智慧學習。

[![授權：MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![版本](https://img.shields.io/badge/Version-1.2.0-green.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)

**FTS5** 索引所有對話歷史並生成 LLM 摘要。內建 **Self-Improving** 整合，自動從修正和模式中學習。

[English](README.md) · [繁體中文](README_ZH.md) · [更新日誌](CHANGELOG.md)

---

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| 🔍 **全文搜尋** | 跨所有對話即時搜尋 |
| 🤖 **LLM 摘要** | 自動生成你語言的摘要 |
| 🌐 **多語言** | zh-TW, zh-CN, en, ja |
| 🧠 **自我改進** | 從修正中學習，追蹤模式 |
| 🔄 **自動索引** | Cron 增量更新 |
| ⚡ **頻率限制** | 每分鐘 30 次 |
| 🛡️ **錯誤恢復** | 三層 fallback |
| 🔒 **安全** | 無硬編碼 Key，資料自動遮罩 |

---

## 🚀 快速開始

```bash
# 1. 複製
git clone https://github.com/ZCrystalC33/fts5-openclaw-skill.git ~/.openclaw/skills/fts5

# 2. 設定
cp ~/.openclaw/skills/fts5/config.env.example ~/.openclaw/fts5.env
nano ~/.openclaw/fts5.env  # 填入 MINIMAX_API_KEY

# 3. 安裝精靈
python3 ~/.openclaw/skills/fts5/setup.py

# 4. 重啟
openclaw gateway restart
```

---

## 📦 包含模組

### FTS5 核心

| 檔案 | 功能 |
|------|------|
| `__init__.py` | 主 API：`search()`, `summarize()`, `get_stats()` |
| `llm_summary.py` | LLM + 多語言 Prompt |
| `rate_limiter.py` | 每分鐘 30 次（滑動窗口）|
| `error_handling.py` | 三層 Fallback 系統 |
| `indexer.py` | 對話索引器（狀態追蹤）|
| `sensitive_filter.py` | API Key / Token 遮罩 |
| `setup.py` | 互動式安裝精靈 |
| `install.py` | Cron 鉤子安裝腳本 |

### Self-Improving 整合

| 檔案 | 等級 | 功能 |
|------|------|------|
| `context_predictor.py` | P1 | 分析文字 → 預測 topics/intents |
| `reindex.py` | P1 | 自動更新 `index.md` |
| `exchange_engine.py` | P2 | 冷/熱層自動交換 |
| `exchange-cron.sh` | P2 | Cron 鉤子（每天 3 AM）|
| `fts5_integration.py` | P3 | 雙向 FTS5 ↔ 記憶同步 |

### 記憶檔案

```
self_improving/
├── memory.md            # 熱層（≤100 行）
├── corrections.md       # 修正日誌
├── index.md            # 自動生成索引
├── heartbeat-state.md  # 心跳狀態
└── domains/
    └── openclaw-fts5.md
```

---

## 💬 使用方式

### FTS5 搜尋

```python
from skills.fts5 import search, summarize, get_stats

# 搜尋
results = search("FTS5", limit=5)
for r in results:
    print(f"{r['timestamp']}: {r['content'][:80]}...")

# LLM 摘要
result = summarize("上次討論的內容")
print(result['summary'])

# 統計
print(get_stats())
# {'total': 8257, 'channels': 2, 'senders': 3, ...}
```

### Self-Improving 上下文預測

```python
from skills.fts5.self_improving.scripts.context_predictor import analyze_text

analysis = analyze_text("上次我們談的 FTS5")
print(analysis['topics'])       # [{'topic': 'fts5', 'hint': '...'}]
print(analysis['intents'])      # [{'intent': 'history', 'memory_type': 'context_recall'}]
print(analysis['suggested_memory_load'])  # ['fts5:recent_conversations', 'domains/fts5']
```

### FTS5 整合

```python
from skills.fts5.self_improving.scripts.fts5_integration import index_correction

# 將修正記錄到 FTS5 以便未來搜尋
index_correction("User corrected my understanding of API key format")
```

---

## 🧠 Self-Improving 層級規則

| 層級 | 位置 | 條件 |
|------|------|------|
| **熱** | `memory.md` | 7 天內引用 |
| **溫** | `domains/` | 3+ 引用 |
| **冷** | `archive/` | 30+ 天未引用 |

---

## 📍 安裝位置優先權

腳本自動偵測並使用**現有的** Self-Improving 安裝位置，保留你的學習資料。

| 優先 | 位置 | 情境 |
|------|------|------|
| 1st | `~/self-improving/` | 已安裝過 |
| 2nd | `~/.openclaw/skills/fts5/self_improving/` | 全新安裝 |

---

## ⚙️ Cron 鉤子

兩個自動化任務維持系統運作：

### FTS5 索引器（每 5 分鐘）

```
~/.openclaw/scripts/fts5-indexer.sh
*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh
```

### Self-Improving 交換（每天 3 AM）

```
~/.openclaw/skills/fts5/self_improving/scripts/exchange-cron.sh
0 3 * * * ~/.openclaw/skills/fts5/self_improving/scripts/exchange-cron.sh
```

---

## 🔧 設定

| 方式 | 方法 |
|------|------|
| 環境變數 | `export MINIMAX_API_KEY=sk-cp-xxx` |
| 設定檔 | `~/.openclaw/fts5.env` |

優先順序：環境變數 → `~/.openclaw/fts5.env` → `~/.openclaw/config.json`

---

## 🛡️ 安全

- ✅ 無硬編碼 API Key
- ✅ 只使用使用者提供的憑證
- ✅ 敏感資料自動遮罩（API Key、Token、密碼）
- ✅ 私人設定檔（600 權限）

---

## 📄 文件

| 檔案 | 語言 | 說明 |
|------|------|------|
| `README.md` | English | 英文說明 |
| `README_ZH.md` | 繁體中文 | 本檔案 |
| `SKILL.md` | English | OpenClaw 技能定義 |
| `CHANGELOG.md` | English | 版本記錄 |

---

## 📄 授權

MIT License — 詳見 [LICENSE](LICENSE)

---

**由 Ophelia Prime 製作**

[GitHub](https://github.com/ZCrystalC33/fts5-openclaw-skill) · [回報問題](https://github.com/ZCrystalC33/fts5-openclaw-skill/issues)
