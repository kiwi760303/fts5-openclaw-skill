# FTS5 - Full-Text Search for OpenClaw

> 🤖 Make your AI assistant remember everything.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.2.0-green.svg)](CHANGELOG.md)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)

**FTS5** indexes all your conversation history and generates smart LLM summaries - so your AI never forgets what you discussed.

[English README](README_EN.md) | [繁體中文說明](README_ZH.md) | [更新日誌](CHANGELOG.md)

## ⚡ Quick Start

```bash
# Install
git clone https://github.com/ZCrystalC33/fts5-openclaw-skill.git ~/.openclaw/skills/fts5

# Configure
cp ~/.openclaw/skills/fts5/config.env.example ~/.openclaw/fts5.env
nano ~/.openclaw/fts5.env  # Add MINIMAX_API_KEY

# Setup wizard
python3 ~/.openclaw/skills/fts5/setup.py

# Restart
openclaw gateway restart
```

## 🎯 Features

| Feature | Description |
|---------|-------------|
| 🔍 **Search** | Full-text search across all conversations |
| 🤖 **Summarize** | LLM-generated summaries in your language |
| 🌐 **Multi-Language** | zh-TW, zh-CN, en, ja |
| 🔒 **Secure** | No hardcoded keys, auto-masks sensitive data |
| ⚡ **Fast** | SQLite FTS5, 30 calls/min |
| 🔄 **Auto-Index** | Cron-based incremental updates |

## 💬 Usage

```python
from skills.fts5 import search, summarize

# Search
results = search("上次討論的 FTS5", limit=5)

# LLM Summary
result = summarize("上次討論的內容")
print(result['summary'])
```

## 📁 Files

- [README_EN.md](README_EN.md) - English documentation
- [README_ZH.md](README_ZH.md) - 繁體中文說明
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [LICENSE](LICENSE) - MIT License

## 🔧 Configuration

```bash
# Environment variable (recommended)
export MINIMAX_API_KEY=sk-cp-your-key

# Or config file
echo "MINIMAX_API_KEY=sk-cp-your-key" > ~/.openclaw/fts5.env
```

## 🛡️ Security

- ✅ No hardcoded API keys
- ✅ User-provided credentials only
- ✅ Sensitive data auto-masked
- ✅ Private config (600 permissions)

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

**Made by Ophelia Prime**

[GitHub](https://github.com/ZCrystalC33/fts5-openclaw-skill) | [Report Issue](https://github.com/ZCrystalC33/fts5-openclaw-skill/issues)