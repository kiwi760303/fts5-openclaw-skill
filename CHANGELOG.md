# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.3.0] - 2026-04-16

### 🎉 Major Improvements

#### Self-Improving Integration (Merged)
- **Combined installation** - FTS5 + Self-Improving in one repo
- **Automatic path detection** - Scripts detect existing ~/self-improving/ and preserve data
- **Bidirectional sync** - FTS5 ↔ memory synchronization

#### Harness Engineering Principles
- **FTS5 Linter** - Mechanical architectural enforcement (7 checks)
- **Pattern Registry** - Anti-patterns documented for automatic detection
- **Simplified AGENTS.md** - ~100 lines as table of contents

### ✅ Added

- `linter.py` - Architectural enforcement tool
  - Export validation
  - Hardcoded path detection
  - Script permission checks (755)
  - Path detection consistency
  - Layer dependencies check
  - Exchange engine rules validation
  - YOLO anti-pattern detection
- `self_improving/domains/patterns.md` - Pattern registry
- Bilingual README (Chinese primary, English secondary)

### 🔧 Improved

- **install.py** - Handles existing Self-Improving gracefully
- **exchange-cron.sh** - Proper permissions (755)
- **Path detection** - Consistent across all scripts
- **Documentation** - SKILL.md updated with full structure

## [1.2.0] - 2026-04-16

### 🎉 Major Improvements

#### Onboarding System
- **No hardcoded API keys** - All credentials are user-provided
- Interactive `setup.py` onboarding wizard
- `config.env.example` template for easy setup
- API key validation and connectivity test

#### Multi-Language Support
- Automatic language detection (zh-TW, zh-CN, en, ja)
- Language-specific prompts for LLM summarization
- Traditional vs Simplified Chinese differentiation

### ✅ Added

- `setup.py` - Interactive onboarding wizard
- `config.env.example` - Example configuration file
- `README_zh.md` - Traditional Chinese documentation
- `_get_api_key()` / `load_api_key()` - Centralized API key loading
- Sensitive data filter with masking
- 3-layer error recovery with fallback
- Rate limiting (10 calls/min)
- Incremental indexing with state tracking

### 🔒 Security

- Removed all hardcoded API keys
- All API keys user-provided via environment or config file
- Sensitive data auto-masking (API keys, tokens, private keys)

## [1.1.0] - 2026-04-15

### 🎉 Major Features

#### LLM Summarization
- MiniMax M2.7 integration
- Automatic summary generation
- Query-type detection (technical, status, preference, default)

#### Smart Prompts
- Technical query prompts (English terms preserved)
- Status query prompts (project progress)
- Preference query prompts (user preferences)
- Default prompts (general topics)

### ✅ Added

- `llm_summary.py` - LLM summarization module
- `rate_limiter.py` - Sliding window rate limiter
- Context length management based on query complexity

## [1.0.0] - 2026-04-14

### 🎉 Initial Release

#### Core Features
- SQLite FTS5 full-text search
- Conversation history indexing
- Basic search functionality
- Session file parsing (JSONL)

### ✅ Added

- `__init__.py` - Main module with search/summarize
- `indexer.py` - Session file indexer
- `SKILL.md` - OpenClaw skill definition
- Database schema with FTS5 virtual table

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 1.3.0 | 2026-04-16 | ✅ Current |
| 1.2.0 | 2026-04-16 | ✅ Previous |
| 1.1.0 | 2026-04-15 | ✅ Previous |
| 1.0.0 | 2026-04-14 | ✅ Initial |

## Upgrade Notes

### Upgrading from v1.1.0 to v1.2.0

1. **API Key Required** - v1.2.0 requires user-provided API key
   - Set `MINIMAX_API_KEY` environment variable, or
   - Create `~/.openclaw/fts5.env` with your key

2. **Run setup** - Recommended after upgrade:
   ```bash
   python3 ~/.openclaw/skills/fts5/setup.py
   ```

### Upgrading from v1.0.0 to v1.1.0

- No special upgrade steps needed
- Just `git pull` and enjoy LLM summarization

---

## Statistics (as of v1.3.0)

- **Files**: 14
- **Lines of Code**: ~3,500
- **Dependencies**: Python stdlib only (urllib, sqlite3, json, re)
- **Supported Languages**: 4 (zh-TW, zh-CN, en, ja)
- **Error Recovery Layers**: 3
- **Linter Checks**: 7 (all passing)
- **Self-Improving Scripts**: 5

## Future Plans

- [ ] ClawHub integration for one-command install
- [ ] Web dashboard for search analytics
- [ ] Additional LLM provider support (OpenAI, Anthropic)
- [ ] Conversation threading for context continuity
- [ ] Scheduled summarization reports