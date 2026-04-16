#!/usr/bin/env python3
"""
FTS5 Installer Script
Installs FTS5 skill and sets up cron hooks for automatic indexing
"""

import os
import sys
import subprocess

FTS5_DIR = os.path.expanduser("~/.openclaw/skills/fts5")
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")
CRON_HOOK = os.path.expanduser("~/.openclaw/scripts/fts5-indexer.sh")

def print_step(msg):
    print(f"\n📦 {msg}")

def print_success(msg):
    print(f"   ✅ {msg}")

def print_error(msg):
    print(f"   ❌ {msg}")

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

def add_to_cron():
    """Add FTS5 indexer to crontab."""
    print_step("Adding to crontab...")
    
    cron_entry = "*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh"
    
    try:
        # Get current crontab
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""
        
        # Check if FTS5 entry already exists
        if 'fts5-indexer.sh' in current_cron:
            print_success("Cron entry already exists")
            return True
        
        # Add new entry
        new_cron = current_cron.strip() + '\n' + cron_entry + '\n'
        
        # Write new crontab
        process = subprocess.run(['crontab', '-'], input=new_cron, text=True)
        
        if process.returncode == 0:
            print_success("Crontab updated with FTS5 indexer")
            return True
        else:
            print_error(f"Crontab update failed: {process.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Cron setup failed: {e}")
        print_info("Note: Cron requires sudo if running as system service")
        return False

def print_info(msg):
    print(f"   ℹ️  {msg}")

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
    
    # Setup cron (requires sudo for system-wide)
    print("\n⚠️  Cron setup requires sudo for system-wide installation")
    response = input("   Setup cron for automatic indexing? [Y/n]: ").strip().lower()
    if response != 'n':
        try:
            import subprocess
            result = subprocess.run(['sudo', 'crontab', '-l'], capture_output=True, text=True)
            current_cron = result.stdout if result.returncode == 0 else ""
            
            if 'fts5-indexer.sh' in current_cron:
                print_success("Cron entry already exists")
            else:
                cron_entry = "*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh"
                new_cron = current_cron.strip() + '\n' + cron_entry + '\n'
                subprocess.run(['sudo', 'crontab', '-'], input=new_cron, text=True)
                print_success("System crontab updated")
        except Exception as e:
            print_error(f"Cron setup failed: {e}")
            print_info("You can manually add to crontab:")
            print_info("*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh")
    else:
        print_info("Cron skipped - manual indexing only")
        print_info("Run 'python3 ~/.openclaw/skills/fts5/indexer.py' manually")
    
    # Summary
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✅ FTS5 Installation Complete!                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

📋 Next Steps:

   1. Configure API Key
      cp ~/.openclaw/skills/fts5/config.env.example ~/.openclaw/fts5.env
      nano ~/.openclaw/fts5.env

   2. Run Setup Wizard
      python3 ~/.openclaw/skills/fts5/setup.py

   3. Index Existing Conversations
      python3 ~/.openclaw/skills/fts5/indexer.py

   4. Restart OpenClaw agent
      openclaw gateway restart

📚 Documentation:
   English: ~/.openclaw/skills/fts5/README_EN.md
   中文:   ~/.openclaw/skills/fts5/README_ZH.md

⚙️  Cron Hook:
   /home/snow/.openclaw/scripts/fts5-indexer.sh (created)
   Auto-run every 5 minutes for incremental indexing

""")

if __name__ == "__main__":
    main()