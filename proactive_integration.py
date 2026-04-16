"""
Proactive Integration Engine
===========================
Connects PFSI + Self-Improving + Proactivity into a unified closed loop.

Flow:
  User Message → Proactivity Hook → PFSI Search → Self-Improving Analysis → Action
                      ↑                                        ↓
                      └──────────── Learning ←────────────────┘

Design: Agentic Harness Patterns
- Compress: Truncation needs recovery pointer
- Select: Just-in-time loading, not eager
- Tool & Safety: Canonical check before writing
- Task Decomposition: Typed IDs, disk output
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── Path Detection ──────────────────────────────────────────────

def _find_self_improving() -> Path:
    """Find Self-Improving directory with priority: original > merged."""
    original = Path.home() / "self-improving"
    merged = Path(__file__).parent.parent / "self_improving"
    
    if original.exists() and (original / "corrections.md").exists():
        return original
    return merged

SELF_IMPROVING_DIR = _find_self_improving()

# ── Trigger Detection ────────────────────────────────────────────

PROACTIVE_TRIGGERS = [
    r"上次", r"之前", r"以前", r"曾經", r"那個",
    r"什麼時候", r"我們談過", r"記得嗎",
    r"繼續", r"還有", r"後來",
    r"上次談", r"之前設定", r"那個專案",
]

def detect_proactive_need(query: str) -> bool:
    """Detect if user's message suggests proactive history review."""
    for pattern in PROACTIVE_TRIGGERS:
        if re.search(pattern, query, re.IGNORECASE):
            return True
    return False


def extract_topic(query: str) -> str:
    """Extract the topic from query for PFSI search.
    
    Removes trigger words but keeps natural phrase structure.
    """
    # Patterns to remove (keep the rest of the phrase)
    trigger_patterns = [
        r'^上次[,，]?', r'^之前[,，]?', r'^以前[,，]?', r'^曾經[,，]?',
        r'^那個[,，]?', r'^我們[,，]?',
    ]
    
    cleaned = query
    for pattern in trigger_patterns:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Also remove trailing trigger words
    for t in ['上次', '之前', '以前', '曾經', '那個', '我們', '談到', '設定']:
        if cleaned.endswith(t):
            cleaned = cleaned[:-len(t)].strip()
    
    cleaned = re.sub(r'[^\w\s]', ' ', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Collapse whitespace
    
    # Fallback: if cleaned is empty, use original query
    if len(cleaned) < 3:
        cleaned = query[:30]
    
    return cleaned


# ── PFSI Search ──────────────────────────────────────────────────

def proactive_search(topic: str, limit: int = 3) -> List[Dict]:
    """Search PFSI for relevant history. Uses just-in-time loading."""
    try:
        from skills.fts5 import search
        return search(topic, limit=limit)
    except ImportError:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "fts5_module",
                Path(__file__).parent / "__init__.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.search(topic, limit=limit)
        except Exception:
            return []


def proactive_summarize(topic: str, history: List[Dict], limit: int = 3) -> Dict:
    """Summarize PFSI search results using LLM."""
    try:
        from skills.fts5 import summarize
        return summarize(topic, history, limit=limit)
    except ImportError:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "fts5_module",
                Path(__file__).parent / "__init__.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.summarize(topic, history, limit=limit)
        except Exception:
            return {"success": False, "error": "import failed"}


# ── Self-Improving Analysis ──────────────────────────────────────

def check_correction_pattern(topic: str, history: List[Dict]) -> Tuple[bool, str]:
    """
    Check if this topic has been corrected before.
    Returns (has_correction, summary).
    """
    corrections_file = SELF_IMPROVING_DIR / "corrections.md"
    if not corrections_file.exists():
        return False, ""
    
    content = corrections_file.read_text()
    
    topic_words = [w for w in topic.lower().split() if len(w) > 3]
    if not topic_words:
        return False, ""
    
    matches = sum(1 for w in topic_words if w in content.lower() and len(w) > 3)
    
    if matches >= 2:
        return True, f"「{topic}」曾在 corrections 中記錄"
    
    return False, ""


def write_learning(topic: str, insight: str, source: str = "proactive"):
    """Write new learning to Self-Improving. Uses canonical check."""
    memory_file = SELF_IMPROVING_DIR / "memory.md"
    
    if memory_file.exists():
        content = memory_file.read_text()
        if insight in content:
            return  # Already recorded
    
    timestamp = "2026-04-17"
    entry = f"\n## [{timestamp}] Proactive Learning ({source})\n"
    entry += f"- Topic: {topic}\n"
    entry += f"- Insight: {insight}\n"
    
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)


# ── Proactive State Update ────────────────────────────────────────

PROACTIVITY_DIR = Path.home() / "proactivity"
SESSION_STATE_FILE = PROACTIVITY_DIR / "session-state.md"


def update_proactive_state(topic: str, action: str, result: str):
    """Update Proactivity session state with current work."""
    SESSION_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    timestamp = "2026-04-17 04:02"
    entry = f"\n[{timestamp}] {action}\n"
    entry += f"  Topic: {topic}\n"
    entry += f"  Result: {result}\n"
    
    with open(SESSION_STATE_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


# ── Main Integration Loop ─────────────────────────────────────────

def run_proactive_check(query: str) -> Optional[str]:
    """
    Main entry point for proactive integration.
    
    Returns None if no action needed, otherwise returns proactive response.
    
    Implements:
    - Select: Just-in-time loading
    - Tool & Safety: Canonical check before action
    - Memory Persistence: State written to disk
    """
    # Step 1: Proactivity Hook - detect need
    if not detect_proactive_need(query):
        return None
    
    # Step 2: Extract topic and search PFSI
    topic = extract_topic(query)
    history = proactive_search(topic, limit=3)
    
    if not history:
        return None
    
    # Step 3: Self-Improving - check correction pattern
    has_correction, correction_note = check_correction_pattern(topic, history)
    
    # Step 4: Decide action based on findings
    result = None
    
    if has_correction:
        result = f"{correction_note}\n"
        result += f"找到了 {len(history)} 條相關歷史"
        write_learning(topic, correction_note, "proactive-reminder")
    elif history:
        try:
            summary_result = proactive_summarize(topic, history, limit=3)
            if summary_result.get("success"):
                result = f"📋 相關歷史：\n{summary_result['summary'][:200]}"
            else:
                result = f"找到 {len(history)} 條相關記錄"
        except Exception as e:
            result = f"找到 {len(history)} 條相關記錄"
    
    if result:
        update_proactive_state(topic, "proactive-check", result)
        return result
    
    return None


# ── CLI Interface ────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = run_proactive_check(query)
        if result:
            print(result)
        else:
            print("No proactive action needed")
    else:
        print("Proactive Integration Engine")
        print("Usage: python proactive_integration.py <query>")