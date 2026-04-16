---
name: FTS5 Full-Text Search
slug: fts5
version: 1.2.0
description: "SQLite FTS5 full-text search with LLM summarization for OpenClaw conversations. Self-contained with no hardcoded credentials."
metadata: {
  "clawdbot": {
    "emoji": "🔍",
    "requires": {
      "bins": ["sqlite3"],
      "python": ["json", "re", "datetime"]
    },
    "os": ["linux", "darwin", "win32"],
    "configPaths": ["~/.openclaw/fts5.env"]
  }
}
---

## Overview

FTS5 provides instant full-text search across all OpenClaw conversation history, combined with LLM-powered summarization to give you meaningful answers instead of raw search results.

**No hardcoded API keys** - users provide their own.

## Features

- 🔍 **FTS5 Full-Text Search** - SQLite-based instant search
- 🤖 **LLM Summarization** - Automatic summary generation
- 🌐 **Multi-Language** - Supports zh-TW, zh-CN, en, ja
- 🔒 **Sensitive Data Filter** - Auto-masks API keys, tokens
- ⚡ **Rate Limiting** - Protects API from overuse
- 🛡️ **Error Recovery** - 3-layer fallback on API failure
- 📊 **Context Management** - Auto-adjusts based on query complexity
- 🔄 **Incremental Indexing** - Only processes changed files

## Installation

### 1. Clone / Download

```bash
# Option A: Git clone
git clone https://github.com/YOUR_USERNAME/fts5-openclaw-skill.git ~/.openclaw/skills/fts5

# Option B: Download tarball
curl -L https://github.com/YOUR_USERNAME/fts5-openclaw-skill/archive/main.tar.gz | tar xz
mv fts5-openclaw-skill ~/.openclaw/skills/fts5
```

### 2. Setup Configuration

```bash
# Copy example config
cp ~/.openclaw/skills/fts5/config.env.example ~/.openclaw/fts5.env

# Edit and add your API key
nano ~/.openclaw/fts5.env
# MINIMAX_API_KEY=sk-cp-your-actual-key-here
```

### 3. Run Onboarding (Interactive Setup)

```bash
python3 ~/.openclaw/skills/fts5/setup.py
```

This will:
- Check for existing configuration
- Guide you through API key setup
- Verify connectivity

### 4. Index Existing Conversations (Optional)

```bash
python3 ~/.openclaw/skills/fts5/indexer.py
```

## Configuration

### Environment Variable (Recommended)

```bash
export MINIMAX_API_KEY=sk-cp-your-key-here
```

### Config File

Create `~/.openclaw/fts5.env`:

```bash
MINIMAX_API_KEY=sk-cp-your-key-here
```

### Priority Order

1. `MINIMAX_API_KEY` environment variable (highest)
2. `~/.openclaw/fts5.env` config file
3. `~/.openclaw/config.json` (fts5.api_key)

## Usage

### Simple Search

```python
from skills.fts5 import search

results = search("Discord Bot", limit=5)
for r in results:
    print(f"{r['timestamp']}: {r['content'][:100]}")
```

### Search with LLM Summary

```python
from skills.fts5 import summarize

result = summarize("Discord Bot")
print(result['summary'])  # LLM-generated summary
print(f"Found: {result['total_found']} total matches")
```

### Statistics

```python
from skills.fts5 import get_stats

stats = get_stats()
print(f"Total messages: {stats['total']}")
```

## Workflow Integration

When user asks about past conversations, use `summarize()` instead of `search()`:

1. User: "我們上次討論的 Discord Bot 怎麼樣了？"
2. Agent: `result = summarize("Discord Bot")`
3. Agent: Display `result['summary']` + relevant references

### Proactivity Integration

Add to `proactivity/memory.md`:

```markdown
## FTS5 Search Triggers

- "上次" / "之前" / "以前" → trigger summarize()
- "什麼時候討論過" → trigger summarize()
- "怎麼樣了" / "進度" → trigger summarize() with status query type
```

## Database Schema

```sql
-- Main conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    sender TEXT,
    sender_label TEXT,
    content TEXT,
    channel TEXT,
    session_key TEXT,
    message_id TEXT,
    is_sensitive BOOLEAN DEFAULT 0
);

-- FTS5 virtual table
CREATE VIRTUAL TABLE conversations_fts USING fts5(
    content, sender, sender_label, channel,
    tokenize='unicode61 remove_diacritics 2'
);
```

## File Structure

```
fts5/
├── __init__.py           # Main module (search, summarize, add_message)
├── llm_summary.py        # LLM summarization with multi-language
├── rate_limiter.py       # Rate limiting
├── error_handling.py     # 3-layer error recovery
├── indexer.py            # Incremental indexer
├── sensitive_filter.py   # Sensitive data masking
├── setup.py              # Onboarding setup
├── config.env.example    # Example configuration
├── SKILL.md             # This file
└── README.md            # Full documentation
```

## Status

- ✅ No hardcoded credentials
- ✅ User-provided API key required
- ✅ Incremental indexing
- ✅ Sensitive data filtering
- ✅ Error recovery with fallback
- ✅ Multi-language support (zh-TW, zh-CN, en, ja)

## Requirements

- Python 3.7+
- SQLite3 (built-in)
- Internet connection (for MiniMax API)

## Troubleshooting

### "MINIMAX_API_KEY not found"

```bash
# Run setup
python3 ~/.openclaw/skills/fts5/setup.py

# Or manually set environment variable
export MINIMAX_API_KEY=sk-cp-your-key
```

### "API connection failed"

1. Check API key is correct
2. Verify internet connection
3. Run `python3 ~/.openclaw/skills/fts5/setup.py` to test

### "No search results found"

- Ensure sessions are being indexed
- Check `~/.openclaw/fts5/indexer_state.json`
- Run indexer manually: `python3 ~/.openclaw/skills/fts5/indexer.py`