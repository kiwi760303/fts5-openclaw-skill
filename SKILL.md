---
name: FTS5 Full-Text Search
slug: fts5
version: 1.2.0
description: "SQLite FTS5 full-text search with LLM summarization for OpenClaw. No hardcoded credentials, includes auto-indexing cron hook."
metadata: {
  "clawdbot": {
    "emoji": "🔍",
    "requires": {
      "bins": ["sqlite3"],
      "python": ["json", "re", "datetime", "urllib"]
    },
    "os": ["linux", "darwin", "win32"],
    "configPaths": ["~/.openclaw/fts5.env"]
  }
}
---

## Overview

FTS5 provides instant full-text search across all OpenClaw conversation history, combined with LLM-powered summarization to give meaningful answers instead of raw search results.

**Features:**
- 🔍 SQLite FTS5 full-text search
- 🤖 LLM summarization (MiniMax)
- 🌐 Multi-language (zh-TW, zh-CN, en, ja)
- 🔒 Sensitive data auto-masking
- ⚡ Rate limiting (30 calls/min)
- 🛡️ 3-layer error recovery
- 📊 Smart context management
- 🔄 Incremental auto-indexing

## Prerequisites

| Requirement | Status | Notes |
|-------------|--------|-------|
| Python 3.7+ | ✅ Built-in | Required |
| SQLite3 | ✅ Built-in | Required for FTS5 |
| OpenClaw | ⚠️ Required | Must be installed first |
| MiniMax API Key | ⚠️ Required | User provides |
| Internet | ✅ Required | For MiniMax API |

## Installation

### Step 1: Install OpenClaw (if not installed)

```bash
# Follow OpenClaw installation guide
# https://docs.openclaw.ai/
```

### Step 2: Clone FTS5

```bash
git clone https://github.com/kiwi760303/fts5-openclaw-skill.git ~/.openclaw/skills/fts5
```

### Step 3: Run Installer (Optional)

```bash
python3 ~/.openclaw/skills/fts5/install.py
```

This creates:
- Cron hook at `~/.openclaw/scripts/fts5-indexer.sh`
- Optional system crontab entry

### Step 4: Configure API Key

```bash
# Option A: Environment variable
export MINIMAX_API_KEY=sk-cp-your-key-here

# Option B: Config file (recommended)
cp ~/.openclaw/skills/fts5/config.env.example ~/.openclaw/fts5.env
nano ~/.openclaw/fts5.env  # Add your key
```

### Step 5: Setup Wizard (Interactive)

```bash
python3 ~/.openclaw/skills/fts5/setup.py
```

This will:
- ✅ Check system prerequisites
- ✅ Guide you to get API key
- ✅ Save configuration
- ✅ Test API connection
- ✅ Optionally index existing conversations

### Step 6: Restart OpenClaw

```bash
openclaw gateway restart
```

## Cron Hook Setup (Auto-Indexing)

FTS5 includes automatic indexing via cron hook:

### Automatic (via install.py)

```bash
python3 ~/.openclaw/skills/fts5/install.py
# Select Y to setup cron
```

### Manual Setup

Add to crontab (`crontab -e`):

```cron
*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh
```

The hook script at `~/.openclaw/scripts/fts5-indexer.sh` runs indexer every 5 minutes.

## File Structure

```
~/.openclaw/
├── skills/fts5/                    # FTS5 Skill
│   ├── __init__.py                # Main module
│   ├── llm_summary.py              # LLM + prompts
│   ├── rate_limiter.py             # 30 calls/min
│   ├── error_handling.py           # 3-layer fallback
│   ├── indexer.py                  # Session indexer
│   ├── sensitive_filter.py         # Data masking
│   ├── setup.py                    # Interactive wizard
│   ├── install.py                  # Installer script
│   ├── config.env.example           # Config template
│   ├── SKILL.md                    # This file
│   └── README_*.md                 # Documentation
├── scripts/
│   └── fts5-indexer.sh             # Cron hook (auto-created)
├── fts5.db                         # SQLite database
└── fts5/
    └── indexer_state.json          # Indexer state
```

## Dependencies

| Module | Python Stdlib | Notes |
|--------|--------------|-------|
| sqlite3 | ✅ | Built-in |
| json | ✅ | Built-in |
| re | ✅ | Built-in |
| datetime | ✅ | Built-in |
| urllib | ✅ | Built-in |
| os, sys, time | ✅ | Built-in |

**No external dependencies!** FTS5 uses only Python standard library.

## Configuration Priority

1. `MINIMAX_API_KEY` environment variable (highest)
2. `~/.openclaw/fts5.env` config file
3. `~/.openclaw/config.json` (fts5.api_key)

## Usage

```python
from skills.fts5 import search, summarize, get_stats

# Search
results = search("Discord Bot", limit=5)

# LLM Summary
result = summarize("上次討論的內容")
print(result['summary'])

# Statistics
stats = get_stats()
print(f"Total: {stats['total']} messages")
```

## OpenClaw Integration

### Proactivity Integration

Add to `~/.openclaw/workspace/HEARTBEAT.md`:

```markdown
## FTS5 Triggers

When user says:
- "上次" / "之前" / "以前" → use summarize()
- "什麼時候討論過" → use summarize()
- "怎麼樣了" / "進度" → use summarize() with status
```

### Session Indexing

Indexer reads from:
```
~/.openclaw/agents/main/sessions/*.jsonl
```

## Troubleshooting

### "Module not found"

```bash
# Ensure FTS5 is in correct location
ls ~/.openclaw/skills/fts5/

# Add to Python path if needed
export PYTHONPATH=$PYTHONPATH:~/.openclaw/skills
```

### "API connection failed"

1. Check API key is correct in `~/.openclaw/fts5.env`
2. Verify internet connection
3. Run setup: `python3 ~/.openclaw/skills/fts5/setup.py`

### "No messages indexed"

1. Check sessions directory exists:
   ```bash
   ls ~/.openclaw/agents/main/sessions/
   ```
2. Run indexer manually:
   ```bash
   python3 ~/.openclaw/skills/fts5/indexer.py
   ```
3. Check state file:
   ```bash
   cat ~/.openclaw/fts5/indexer_state.json
   ```

## Version History

- **v1.2.0** (2026-04-16): Onboarding wizard, 30 calls/min, EN/ZH docs
- **v1.1.0** (2026-04-15): LLM summarization, rate limiting
- **v1.0.0** (2026-04-14): Initial release

## License

MIT License - See LICENSE file