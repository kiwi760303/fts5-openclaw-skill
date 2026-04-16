"""
FTS5 Indexer - Automatic message indexing for OpenClaw sessions

This module handles automatic indexing of new messages from OpenClaw session files.
It tracks what's been indexed and only imports new messages on each run.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.fts5 import init_db, add_message, get_stats, search

# State file to track indexed sessions
STATE_FILE = os.path.expanduser("~/.openclaw/fts5/indexer_state.json")

# Session directory - use ~/.openclaw/agents/main/sessions
SESSIONS_DIR = os.path.expanduser("~/.openclaw/agents/main/sessions")


def load_state() -> Dict:
    """Load the indexer state."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "indexed_sessions": {},  # {filename: {"last_mtime": ..., "last_size": ..., "last_indexed_id": ...}}
        "last_run": None,
        "total_indexed": 0
    }


def save_state(state: Dict):
    """Save the indexer state."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def get_session_info(filepath: str) -> Dict:
    """Get current session file info."""
    stat = os.stat(filepath)
    return {
        "size": stat.st_size,
        "mtime": stat.st_mtime,
        "mtime_iso": datetime.fromtimestamp(stat.st_mtime).isoformat()
    }


def count_messages_in_file(filepath: str) -> int:
    """Count message events in a session file."""
    count = 0
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    event = json.loads(line.strip())
                    if event.get('type') == 'message':
                        msg = event.get('message', {})
                        if msg.get('role') in ('user', 'assistant'):
                            count += 1
                except (json.JSONDecodeError, KeyError):
                    continue
    except (IOError, UnicodeDecodeError):
        pass
    return count


def index_session(filepath: str, force: bool = False) -> Tuple[int, bool]:
    """
    Index new messages from a session file.
    
    Returns:
        (count of new messages indexed, whether file was updated)
    """
    filename = os.path.basename(filepath)
    state = load_state()
    session_info = get_session_info(filepath)
    
    # Check if file is new or updated
    if filename in state["indexed_sessions"]:
        last_info = state["indexed_sessions"][filename]
        if (last_info["size"] == session_info["size"] and 
            last_info["mtime"] == session_info["mtime"]):
            # No changes
            return 0, False
    
    # Import messages from this file
    from skills.fts5 import import_from_session_file
    count = import_from_session_file(filepath)
    
    # Update state
    state["indexed_sessions"][filename] = {
        **session_info,
        "indexed_at": datetime.now().isoformat(),
        "messages_indexed": count
    }
    
    save_state(state)
    
    return count, True


def run_indexer() -> Dict:
    """
    Run the FTS5 indexer - checks all sessions and indexes new messages.
    
    Returns:
        Dict with indexing results
    """
    init_db()
    state = load_state()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "sessions_checked": 0,
        "sessions_updated": 0,
        "new_messages": 0,
        "errors": []
    }
    
    if not os.path.exists(SESSIONS_DIR):
        results["errors"].append(f"Sessions directory not found: {SESSIONS_DIR}")
        return results
    
    # Check all session files
    for filename in os.listdir(SESSIONS_DIR):
        if not filename.endswith('.jsonl') or '.reset.' in filename:
            continue
        
        # Skip reset files
        if '.reset.' in filename:
            continue
        
        filepath = os.path.join(SESSIONS_DIR, filename)
        results["sessions_checked"] += 1
        
        try:
            count, updated = index_session(filepath)
            if updated:
                results["sessions_updated"] += 1
                results["new_messages"] += count
        except Exception as e:
            results["errors"].append(f"{filename}: {str(e)}")
    
    # Update last run time
    state["last_run"] = datetime.now().isoformat()
    state["total_indexed"] = get_stats()["total"]
    save_state(state)
    
    return results


def get_indexer_status() -> Dict:
    """Get current indexer status."""
    state = load_state()
    stats = get_stats()
    
    return {
        "state_file": STATE_FILE,
        "sessions_tracked": len(state["indexed_sessions"]),
        "last_run": state["last_run"],
        "total_messages_indexed": stats["total"],
        "total_sessions_in_dir": len([f for f in os.listdir(SESSIONS_DIR) 
                                      if f.endswith('.jsonl') and '.reset.' not in f])
        if os.path.exists(SESSIONS_DIR) else 0,
        "sessions": {
            fname: info
            for fname, info in state["indexed_sessions"].items()
        }
    }


if __name__ == "__main__":
    print("🔍 FTS5 Indexer Running...")
    print()
    
    # Show status
    status = get_indexer_status()
    print(f"📊 Current Status:")
    print(f"   Sessions tracked: {status['sessions_tracked']}")
    print(f"   Total messages: {status['total_messages_indexed']}")
    print(f"   Last run: {status['last_run'] or 'Never'}")
    print()
    
    # Run indexer
    print("🚀 Running indexer...")
    results = run_indexer()
    
    print(f"   Sessions checked: {results['sessions_checked']}")
    print(f"   Sessions updated: {results['sessions_updated']}")
    print(f"   New messages: {results['new_messages']}")
    
    if results['errors']:
        print(f"   Errors: {results['errors']}")
    
    print()
    print("✅ Indexer complete!")
