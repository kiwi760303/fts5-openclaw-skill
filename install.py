#!/usr/bin/env python3
"""
FTS5 Installer Script
Installs FTS5 skill and sets up cron hooks for automatic indexing

Handles existing Self-Improving installations gracefully:
- If ~/self-improving/ exists: offer to use existing location
- If no existing installation: use merged location in FTS5 repo
"""

import os
import sys
import subprocess
from pathlib import Path

FTS5_DIR = os.path.expanduser("~/.openclaw/skills/fts5")
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")
CRON_HOOK = os.path.expanduser("~/.openclaw/scripts/fts5-indexer.sh")
ORIGINAL_SELF_IMPROVING = os.path.expanduser("~/self-improving")
MERGED_SELF_IMPROVING = os.path.join(FTS5_DIR, "self_improving")

def print_step(msg):
    print(f"\n📦 {msg}")

def print_success(msg):
    print(f"   ✅ {msg}")

def print_error(msg):
    print(f"   ❌ {msg}")

def print_info(msg):
    print(f"   ℹ️  {msg}")

def check_already_installed():
    """Check if FTS5 is already installed."""
    return os.path.exists(FTS5_DIR)

def check_openclaw_installed():
    """Check if OpenClaw is installed."""
    return os.path.exists(OPENCLAW_DIR)

def create_cron_hook():
    """Create the FTS5 indexer cron hook script."""
    print_step("Creating cron hook...")

    # Create scripts directory if not exists
    scripts_dir = os.path.dirname(CRON_HOOK)
    os.makedirs(scripts_dir, exist_ok=True)

    hook_content = """#!/bin/bash
# FTS5 Indexer Cron Hook
# This script is triggered by OpenClaw heartbeat to index new messages

FTS5_DIR="$HOME/.openclaw/skills/fts5"
LOG_FILE="$HOME/.openclaw/logs/fts5-indexer.log"

# Run indexer if FTS5 is installed
if [ -f "$FTS5_DIR/indexer.py" ]; then
    python3 "$FTS5_DIR/indexer.py" >> "$LOG_FILE" 2>&1
fi
"""

    with open(CRON_HOOK, 'w') as f:
        f.write(hook_content)

    os.chmod(CRON_HOOK, 0o755)
    print_success(f"Cron hook created: {CRON_HOOK}")

def add_fts5_cron():
    """Add FTS5 indexer to crontab (tries sudo first, falls back to user)."""
    print_step("Setting up FTS5 cron (every 5 minutes)...")

    cron_entry = "*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh"

    # Try sudo first (for system-wide crontab)
    try:
        result = subprocess.run(['sudo', 'crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""

        if 'fts5-indexer.sh' in current_cron:
            print_success("FTS5 cron already configured")
            return True

        new_cron = current_cron.strip() + '\n' + cron_entry + '\n'
        subprocess.run(['sudo', 'crontab', '-'], input=new_cron, text=True)
        print_success("System crontab updated")
        return True

    except Exception as e:
        print_info(f"Sudo cron failed: {e}")

    # Fallback to user crontab
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""

        if 'fts5-indexer.sh' in current_cron:
            print_success("FTS5 cron already configured")
            return True

        new_cron = current_cron.strip() + '\n' + cron_entry + '\n'
        subprocess.run(['crontab', '-'], input=new_cron, text=True)
        print_success("User crontab updated")
        return True

    except Exception as e:
        print_error(f"User crontab update failed: {e}")
        return False

def check_existing_self_improving():
    """Check if Self-Improving is already installed."""
    return os.path.exists(ORIGINAL_SELF_IMPROVING)

def setup_exchange_cron(use_fts5_scripts=True):
    """Setup cron for Self-Improving exchange engine (3 AM daily)."""
    if use_fts5_scripts:
        script_path = os.path.join(MERGED_SELF_IMPROVING, "scripts", "exchange-cron.sh")
    else:
        script_path = os.path.join(ORIGINAL_SELF_IMPROVING, "scripts", "exchange-cron.sh")

    if not os.path.exists(script_path):
        return False

    cron_entry = f"0 3 * * * {script_path}"

    # Try sudo first
    try:
        result = subprocess.run(['sudo', 'crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""

        if 'exchange-cron.sh' in current_cron:
            print_success("Exchange cron already configured")
            return True

        new_cron = current_cron.strip() + '\n' + cron_entry + '\n'
        subprocess.run(['sudo', 'crontab', '-'], input=new_cron, text=True)
        print_success("Exchange cron configured (3 AM daily)")
        return True

    except Exception:
        pass

    # Fallback to user crontab
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""

        if 'exchange-cron.sh' in current_cron:
            print_success("Exchange cron already configured")
            return True

        new_cron = current_cron.strip() + '\n' + cron_entry + '\n'
        subprocess.run(['crontab', '-'], input=new_cron, text=True)
        print_success("Exchange cron configured (3 AM daily)")
        return True

    except Exception as e:
        print_info(f"Exchange cron setup failed: {e}")
        print_info(f"Manual: {cron_entry}")
        return False

def setup_self_improving_integration():
    """
    Handle Self-Improving integration.
    Priority: existing ~/self-improving/ > merged location
    """
    print_step("Checking Self-Improving integration...")

    has_existing = check_existing_self_improving()
    has_merged = os.path.exists(os.path.join(MERGED_SELF_IMPROVING, "memory.md"))

    if has_existing:
        print_success(f"Found existing Self-Improving: {ORIGINAL_SELF_IMPROVING}")
        print_info("Scripts will auto-detect and use existing installation")
        print_info("Your learning data is preserved and will continue growing")

        # Offer to update cron to use new scripts
        print("\n   Would you like to update your cron to use the new scripts from FTS5?")
        print("   (The new scripts have auto-detection and work with both locations)")
        response = input("   Update cron to FTS5 scripts? [y/N]: ").strip().lower()

        if response == 'y':
            setup_exchange_cron(use_fts5_scripts=True)
        else:
            print_info("Keeping existing cron configuration")
            # Still try to set up exchange cron from original location
            setup_exchange_cron(use_fts5_scripts=False)

    elif has_merged:
        print_success(f"Using merged Self-Improving: {MERGED_SELF_IMPROVING}")
        setup_exchange_cron(use_fts5_scripts=True)

    else:
        print_info("No existing Self-Improving found")
        print_info("Self-Improving is embedded in FTS5 repo and ready to use")

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   FTS5 Installer                                             ║
║   Full-Text Search for OpenClaw                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Check OpenClaw
    if not check_openclaw_installed():
        print("❌ OpenClaw not found at ~/.openclaw/")
        print("   Please install OpenClaw first: https://github.com/openclaw/openclaw")
        sys.exit(1)

    print_success("OpenClaw found")

    # Check FTS5 installed
    if check_already_installed():
        print_info("FTS5 is already installed")
        print_info(f"Location: {FTS5_DIR}")
        response = input("\n   Re-install? [y/N]: ").strip().lower()
        if response != 'y':
            print("Installation cancelled")
            sys.exit(0)

    # Create cron hook
    create_cron_hook()

    # Setup Self-Improving integration
    setup_self_improving_integration()

    # Setup FTS5 cron
    print("\n⚠️  Cron setup requires sudo for system-wide installation")
    response = input("   Setup cron for automatic indexing? [Y/n]: ").strip().lower()
    if response != 'n':
        add_fts5_cron()
    else:
        print_info("Cron skipped - manual indexing only")
        print_info("Run 'python3 $HOME/.openclaw/skills/fts5/indexer.py' manually")

    # Summary
    home = os.path.expanduser("~")
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✅ FTS5 Installation Complete!                              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📋 Next Steps:

   1. Configure API Key
      cp $HOME/.openclaw/skills/fts5/config.env.example $HOME/.openclaw/fts5.env
      nano $HOME/.openclaw/fts5.env

   2. Run Setup Wizard
      python3 $HOME/.openclaw/skills/fts5/setup.py

   3. Index Existing Conversations
      python3 $HOME/.openclaw/skills/fts5/indexer.py

   4. Restart OpenClaw agent
      openclaw gateway restart

📚 Documentation:
   English: $HOME/.openclaw/skills/fts5/README_EN.md
   中文:   $HOME/.openclaw/skills/fts5/README_ZH.md

⚙️  Cron Hooks:
   FTS5 Indexer: $HOME/.openclaw/scripts/fts5-indexer.sh (every 5 min)
   Self-Improving Exchange: $HOME/.openclaw/skills/fts5/self_improving/scripts/exchange-cron.sh (3 AM daily)

🧠 Self-Improving:
   Existing installations are automatically detected and preserved
   Your learning data will continue to grow in the original location
""")

if __name__ == "__main__":
    main()
