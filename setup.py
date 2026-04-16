#!/usr/bin/env python3
"""
FTS5 Onboarding Wizard
Step-by-step setup guide for FTS5 skill
"""

import os
import sys
import json
import urllib.request
import urllib.error

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

SETUP_FILE = os.path.expanduser("~/.openclaw/fts5.env")
CONFIG_FILE = os.path.expanduser("~/.openclaw/config.json")
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")


def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_banner():
    """Display welcome banner."""
    clear_screen()
    print(f"""
{BOLD}{CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   {YELLOW}FTS5 Full-Text Search for OpenClaw{ CYAN}                      ║
║   {BLUE}Version 1.2.0 - Onboarding Wizard{ CYAN}                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")


def print_step(current: int, total: int, title: str):
    """Display step header."""
    print(f"\n{BOLD}{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{CYAN}  Step {current}/{total}: {title}{RESET}")
    print(f"{YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}\n")


def print_success(msg: str):
    print(f"  {GREEN}✅ {msg}{RESET}")


def print_error(msg: str):
    print(f"  {RED}❌ {msg}{RESET}")


def print_info(msg: str):
    print(f"  {BLUE}ℹ️  {msg}{RESET}")


def print_warning(msg: str):
    print(f"  {YELLOW}⚠️  {msg}{RESET}")


def input_with_default(prompt: str, default: str) -> str:
    """Get input with default value."""
    result = input(f"  {prompt} [{default}]: ").strip()
    return result if result else default


def check_prerequisites() -> bool:
    """Step 1: Check system prerequisites."""
    print_step(1, 6, "System Prerequisites Check")
    
    all_ok = True
    
    # Check Python version
    print("  Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    else:
        print_error(f"Python {version.major}.{version.minor} - requires 3.7+")
        all_ok = False
    
    # Check SQLite
    print("\n  Checking SQLite...")
    try:
        import sqlite3
        version = sqlite3.sqlite_version
        print_success(f"SQLite {version} ✓")
    except ImportError:
        print_error("SQLite3 not available")
        all_ok = False
    
    # Check OpenClaw directory
    print("\n  Checking OpenClaw directory...")
    if os.path.exists(OPENCLAW_DIR):
        print_success(f"OpenClaw directory found: {OPENCLAW_DIR}")
    else:
        print_warning(f"OpenClaw directory not found: {OPENCLAW_DIR}")
        print_info("Will create on first run")
    
    # Check internet connectivity
    print("\n  Checking internet connectivity...")
    try:
        urllib.request.urlopen("https://api.minimax.io/", timeout=5)
        print_success("Internet connection OK")
    except:
        print_error("Cannot reach api.minimax.io")
        all_ok = False
    
    if not all_ok:
        print(f"\n  {YELLOW}Some prerequisites failed. You may still proceed, but functionality may be limited.{RESET}")
        input("\n  Press Enter to continue...")
    
    return True


def get_api_key_guide() -> str:
    """Step 2: Guide user to get MiniMax API key."""
    print_step(2, 6, "Get MiniMax API Key")
    
    print(f"""  {BOLD}To use FTS5, you need a MiniMax API Key.{RESET}
  
  {CYAN}How to get your API Key:{RESET}
  
  1. Visit {BLUE}https://platform.minimax.io/{RESET}
  2. Create an account or log in
  3. Go to API Keys section
  4. Create a new API Key
  5. Copy the key (starts with 'sk-cp-' or 'sk-')
  
  {YELLOW}Your key will only be stored locally and never shared.{RESET}
""")
    
    input("  Press Enter when you have your API Key ready...")
    
    while True:
        print("\n  Paste your API Key below:")
        api_key = input(f"  {CYAN}Key (sk-cp-...): {RESET}").strip()
        
        if not api_key:
            print_error("Key cannot be empty")
            continue
        
        if len(api_key) < 20:
            print_warning("Key seems too short, please double-check")
            confirm = input("  Continue anyway? [y/N]: ").strip().lower()
            if confirm != 'y':
                continue
        
        return api_key


def save_api_key(api_key: str) -> bool:
    """Step 3: Save API key to config."""
    print_step(3, 6, "Save Configuration")
    
    os.makedirs(os.path.dirname(SETUP_FILE), exist_ok=True)
    
    print(f"\n  Saving to: {SETUP_FILE}")
    
    try:
        with open(SETUP_FILE, 'w') as f:
            f.write(f"# FTS5 Configuration\n")
            f.write(f"# Generated by FTS5 Onboarding Wizard\n")
            f.write(f"# Created: {__import__('datetime').datetime.now().isoformat()}\n")
            f.write(f"\n")
            f.write(f"# MiniMax API Key\n")
            f.write(f"MINIMAX_API_KEY={api_key}\n")
        
        print_success("Configuration saved!")
        print_info(f"File: {SETUP_FILE}")
        
        # Set file permissions to be private
        os.chmod(SETUP_FILE, 0o600)
        print_info("File permissions set to 600 (private)")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to save: {e}")
        return False


def test_connection(api_key: str) -> bool:
    """Step 4: Test API connection."""
    print_step(4, 6, "Test API Connection")
    
    print(f"\n  Testing MiniMax API connection...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": "MiniMax-M2.7",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }
    
    try:
        req = urllib.request.Request(
            "https://api.minimax.io/anthropic/v1/messages",
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read())
            content = result.get('content', [])
            for item in content:
                if item.get('type') == 'text':
                    print_success(f"API responded: '{item['text'][:50]}...'")
                    return True
        
        print_error("No response content")
        return False
        
    except urllib.error.HTTPError as e:
        print_error(f"HTTP Error: {e.code}")
        if e.code == 401:
            print_info("Invalid API key - please check and try again")
        elif e.code == 429:
            print_info("Rate limited - please wait and try again")
        return False
        
    except urllib.error.URLError as e:
        print_error(f"Connection failed: {e.reason}")
        return False
        
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def index_existing_conversations() -> bool:
    """Step 5: Index existing conversations."""
    print_step(5, 6, "Index Existing Conversations")
    
    print(f"""
  {BOLD}This step indexes your existing OpenClaw conversations{RESET}
  {YELLOW}(This is optional and may take a few minutes){RESET}
  
  Indexed data is stored locally in:
  {BLUE}~/.openclaw/fts5.db{RESET}
""")
    
    choice = input("  Index existing conversations? [Y/n]: ").strip().lower()
    
    if choice == 'n':
        print_info("Skipped - you can run this later with:")
        print(f"    {CYAN}python3 ~/.openclaw/skills/fts5/indexer.py{RESET}")
        return False
    
    print("\n  Running indexer...")
    print_info("This may take a few minutes for large conversation histories...")
    
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from indexer import import_all_sessions
        
        sessions_dir = os.path.expanduser("~/.openclaw/agents/main/sessions")
        
        if not os.path.exists(sessions_dir):
            print_warning(f"Sessions directory not found: {sessions_dir}")
            print_info("Skipping indexing - run indexer.py later when you have sessions")
            return False
        
        results = import_all_sessions(sessions_dir)
        
        if results:
            total = sum(results.values())
            print_success(f"Indexed {total} messages from {len(results)} session files!")
        else:
            print_info("No new messages to index (or sessions directory empty)")
        
        return True
        
    except Exception as e:
        print_error(f"Indexing failed: {e}")
        print_info("You can run the indexer manually later:")
        print(f"    {CYAN}python3 ~/.openclaw/skills/fts5/indexer.py{RESET}")
        return False


def show_summary(api_key: str, indexed: bool):
    """Step 6: Show setup summary."""
    print_step(6, 6, "Setup Complete!")
    
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
    
    print(f"""
{BOLD}{GREEN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🎉 FTS5 Setup Complete!                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{RESET}

  {BOLD}Configuration:{RESET}
    API Key: {CYAN}{masked_key}{RESET}
    Config:  {CYAN}~/.openclaw/fts5.env{RESET}
    Database: {CYAN}~/.openclaw/fts5.db{RESET}

  {BOLD}Quick Start:{RESET}
    from skills.fts5 import search, summarize
    
    # Simple search
    results = search("your query", limit=5)
    
    # LLM summary
    result = summarize("your query")
    print(result['summary'])

  {BOLD}Useful Commands:{RESET}
    # Re-run setup
    python3 ~/.openclaw/skills/fts5/setup.py
    
    # Index conversations
    python3 ~/.openclaw/skills/fts5/indexer.py
    
    # Check stats
    python3 -c "from skills.fts5 import get_stats; print(get_stats())"

  {BOLD}Next Steps:{RESET}
    1. Restart your OpenClaw agent
    2. Try: "上次我們談的 FTS5 系統"
    3. Enjoy smart conversation history!

{YELLOW}═══════════════════════════════════════════════════════════════════{RESET}
""")


def run_full_setup():
    """Run the complete onboarding wizard."""
    print_banner()
    
    print(f"""
  {BOLD}Welcome to FTS5 Onboarding!{RESET}
  
  This wizard will guide you through setting up FTS5:
  {CYAN}• Check system requirements{RESET}
  {CYAN}• Configure your API key{RESET}
  {CYAN}• Test the connection{RESET}
  {CYAN}• Optionally index existing conversations{RESET}
  
  Let's get started!
""")
    
    input("  Press Enter to begin...")
    
    # Step 1: Prerequisites
    check_prerequisites()
    
    # Step 2: Get API key
    api_key = get_api_key_guide()
    
    # Step 3: Save config
    if not save_api_key(api_key):
        print_error("Failed to save configuration")
        input("\n  Press Enter to exit...")
        sys.exit(1)
    
    # Step 4: Test connection
    if not test_connection(api_key):
        print_warning("API connection failed, but configuration is saved")
        print_info("You can re-test with: python3 ~/.openclaw/skills/fts5/setup.py")
        retry = input("\n  Continue anyway? [y/N]: ").strip().lower()
        if retry != 'y':
            print_info("Setup incomplete - please try again later")
            sys.exit(0)
    
    # Step 5: Index (optional)
    indexed = index_existing_conversations()
    
    # Step 6: Summary
    print_banner()
    show_summary(api_key, indexed)
    
    input("\n  Press Enter to exit setup...")


def check_existing():
    """Check if already configured."""
    print_banner()
    
    # Check for existing config
    api_key = None
    source = None
    
    env_key = os.environ.get("MINIMAX_API_KEY")
    if env_key:
        api_key = env_key
        source = "environment variable (MINIMAX_API_KEY)"
    
    if not api_key and os.path.exists(SETUP_FILE):
        with open(SETUP_FILE, 'r') as f:
            for line in f:
                if line.startswith("MINIMAX_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    if key and key != "sk-cp-YOUR_KEY_HERE":
                        api_key = key
                        source = f"config file ({SETUP_FILE})"
                        break
    
    if api_key:
        masked = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"""
  {BOLD}✅ FTS5 is already configured!{RESET}
  
  API Key: {CYAN}{masked}{RESET}
  Source: {source}
  
  Config file: {SETUP_FILE}
  
  {YELLOW}What would you like to do?{RESET}
  
    [1] Re-run full setup wizard
    [2] Test API connection only
    [3] Re-index conversations
    [4] Exit
  
""")
        choice = input("  Select option [1-4]: ").strip()
        
        if choice == "1":
            run_full_setup()
        elif choice == "2":
            test_connection(api_key)
            input("\n  Press Enter to exit...")
        elif choice == "3":
            index_existing_conversations()
            input("\n  Press Enter to exit...")
        else:
            print_info("Goodbye!")
            sys.exit(0)
    else:
        print(f"""
  {YELLOW}FTS5 is not configured yet.{RESET}
  
  This wizard will help you set it up.
""")
        input("  Press Enter to begin setup...")
        run_full_setup()


def main():
    """Main entry point."""
    try:
        check_existing()
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Setup interrupted.{RESET}")
        print_info("Run setup.py again anytime to reconfigure.")
        sys.exit(0)


if __name__ == "__main__":
    main()