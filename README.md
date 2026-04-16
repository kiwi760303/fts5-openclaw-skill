# FTS5 - Full-Text Search for OpenClaw

> 🤖 Make your AI assistant remember everything — with built-in Self-Improving intelligence.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.2.0-green.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)

**FTS5** indexes all your conversation history and generates LLM-powered summaries. Includes built-in **Self-Improving** integration for automatic learning from corrections and patterns.

[English](README.md) · [繁體中文](README_ZH.md) · [Changelog](CHANGELOG.md)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Full-Text Search** | Instant search across all conversations |
| 🤖 **LLM Summaries** | Auto-generated in your language |
| 🌐 **Multi-Language** | zh-TW, zh-CN, en, ja |
| 🧠 **Self-Improving** | Learn from corrections, track patterns |
| 🔄 **Auto-Index** | Cron-based incremental updates |
| ⚡ **Rate Limiting** | 30 calls/min |
| 🛡️ **Error Recovery** | 3-layer fallback |
| 🔒 **Secure** | No hardcoded keys, data auto-masked |

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/ZCrystalC33/fts5-openclaw-skill.git ~/.openclaw/skills/fts5

# 2. Configure
cp ~/.openclaw/skills/fts5/config.env.example ~/.openclaw/fts5.env
nano ~/.openclaw/fts5.env  # Add MINIMAX_API_KEY

# 3. Setup
python3 ~/.openclaw/skills/fts5/setup.py

# 4. Restart
openclaw gateway restart
```

---

## 📦 What's Included

### FTS5 Core

| File | Purpose |
|------|---------|
| `__init__.py` | Main API: `search()`, `summarize()`, `get_stats()` |
| `llm_summary.py` | LLM + multi-language prompts |
| `rate_limiter.py` | 30 calls/min sliding window |
| `error_handling.py` | 3-layer fallback system |
| `indexer.py` | Session indexer with state tracking |
| `sensitive_filter.py` | API key / token masking |
| `setup.py` | Interactive setup wizard |
| `install.py` | Cron hook installer |

### Self-Improving Integration

| File | Level | Purpose |
|------|-------|---------|
| `context_predictor.py` | P1 | Analyze text → predict topics/intents |
| `reindex.py` | P1 | Auto-update `index.md` |
| `exchange_engine.py` | P2 | Cold/Hot layer auto-exchange |
| `exchange-cron.sh` | P2 | Cron hook (3 AM daily) |
| `fts5_integration.py` | P3 | Bidirectional FTS5 ↔ memory sync |

### Memory Files

```
self_improving/
├── memory.md            # Hot layer (≤100 lines)
├── corrections.md       # Corrections log
├── index.md            # Auto-generated index
├── heartbeat-state.md  # Heartbeat tracking
└── domains/
    └── openclaw-fts5.md
```

---

## 💬 Usage

### FTS5 Search

```python
from skills.fts5 import search, summarize, get_stats

# Search
results = search("FTS5", limit=5)
for r in results:
    print(f"{r['timestamp']}: {r['content'][:80]}...")

# LLM Summary
result = summarize("上次討論的內容")
print(result['summary'])

# Stats
print(get_stats())
# {'total': 8257, 'channels': 2, 'senders': 3, ...}
```

### Self-Improving Context Prediction

```python
from skills.fts5.self_improving.scripts.context_predictor import analyze_text

analysis = analyze_text("上次我們談的 FTS5")
print(analysis['topics'])       # [{'topic': 'fts5', 'hint': '...'}]
print(analysis['intents'])      # [{'intent': 'history', 'memory_type': 'context_recall'}]
print(analysis['suggested_memory_load'])  # ['fts5:recent_conversations', 'domains/fts5']
```

### FTS5 Integration

```python
from skills.fts5.self_improving.scripts.fts5_integration import index_correction

# Log a correction to FTS5 for future search
index_correction("User corrected my understanding of API key format")
```

---

## 🧠 Self-Improving Layer Rules

| Layer | Location | Trigger |
|-------|----------|---------|
| **HOT** | `memory.md` | Referenced < 7 days |
| **WARM** | `domains/` | 3+ references |
| **COLD** | `archive/` | 30+ days unreferenced |

---

## 📍 Installation Location Priority

Scripts automatically detect and use the **existing** Self-Improving installation to preserve your learning data.

| Priority | Location | When Used |
|----------|----------|-----------|
| 1st | `~/self-improving/` | Already installed |
| 2nd | `~/.openclaw/skills/fts5/self_improving/` | New installation |

---

## ⚙️ Cron Hooks

Two automated tasks keep your system running:

### FTS5 Indexer (Every 5 minutes)

```
~/.openclaw/scripts/fts5-indexer.sh
*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh
```

### Self-Improving Exchange (3 AM daily)

```
~/.openclaw/skills/fts5/self_improving/scripts/exchange-cron.sh
0 3 * * * ~/.openclaw/skills/fts5/self_improving/scripts/exchange-cron.sh
```

---

## 🔧 Configuration

| Method | How |
|--------|-----|
| Environment | `export MINIMAX_API_KEY=sk-cp-xxx` |
| Config file | `~/.openclaw/fts5.env` |

Priority: Environment variable → `~/.openclaw/fts5.env` → `~/.openclaw/config.json`

---

## 🛡️ Security

- ✅ No hardcoded API keys
- ✅ User-provided credentials only
- ✅ Sensitive data auto-masked (API keys, tokens, passwords)
- ✅ Private config (600 permissions)

---

## 📄 Documentation

| File | Language | Description |
|------|----------|-------------|
| `README.md` | English | This file |
| `README_ZH.md` | 繁體中文 | 中文說明 |
| `SKILL.md` | English | OpenClaw skill definition |
| `CHANGELOG.md` | English | Version history |

---

## 📄 License

MIT License — See [LICENSE](LICENSE)

---

**Made by Ophelia Prime**

[GitHub](https://github.com/ZCrystalC33/fts5-openclaw-skill) · [Report Issue](https://github.com/ZCrystalC33/fts5-openclaw-skill/issues)
