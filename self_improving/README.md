# Self-Improving - Enhanced for OpenClaw

Self-Improving module with P1/P2/P3 enhancements integrated into FTS5.

## 📍 Installation Location

**For existing Self-Improving users:** Scripts automatically detect and use your existing `~/self-improving/` installation to preserve all learning data.

| Priority | Location | When Used |
|----------|----------|-----------|
| 1st | `~/self-improving/` | User already installed before |
| 2nd | `~/.openclaw/skills/fts5/self_improving/` | New installation |

## 📦 What's Included

```
self_improving/
├── memory.md              # Hot layer (≤100 lines)
├── corrections.md         # Corrections log
├── index.md              # Auto-generated index
├── heartbeat-state.md    # Heartbeat tracking
├── domains/              # Domain learnings
│   └── openclaw-fts5.md
└── scripts/              # Enhancement modules
    ├── context_predictor.py   # P1: Context prediction
    ├── reindex.py             # P1: Auto-index
    ├── exchange_engine.py     # P2: Cold/Hot layers
    ├── exchange-cron.sh       # P2: Cron hook
    └── fts5_integration.py   # P3: Bidirectional sync
```

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/ZCrystalC33/openclaw-pfsi.git ~/.openclaw/skills/fts5

# 2. If you already have ~/self-improving/, scripts will auto-detect it

# 3. Run setup
python3 ~/.openclaw/skills/fts5/setup.py

# 4. Set up cron (optional)
echo "0 3 * * * $HOME/.openclaw/skills/fts5/self_improving/scripts/exchange-cron.sh" | crontab -
```

## 🔧 Usage

```python
# Context prediction
from skills.fts5.self_improving.scripts.context_predictor import analyze_text
analysis = analyze_text("上次我們談的 FTS5")

# FTS5 integration
from skills.fts5.self_improving.scripts.fts5_integration import index_correction
index_correction("User corrected my understanding")
```

## 🔄 Layer Exchange Rules

| Layer | Location | Trigger |
|-------|----------|---------|
| HOT | memory.md | < 7 days referenced |
| WARM | domains/ | 3+ references |
| COLD | archive/ | 30+ days unreferenced

## 📄 License

MIT License - See LICENSE file