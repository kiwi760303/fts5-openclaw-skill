#!/usr/bin/env python3
"""
OpenClaw PFSI Installer
Installs PFSI skill and sets up cron hooks for automatic indexing

Handles existing installations gracefully:
- If ~/self-improving/ exists: use existing location (data preserved)
- If ~/proactivity/ exists: detect and integrate
- Database: auto-created at ~/.openclaw/fts5.db (gitignored, never committed)
"""

import os
import sys
import subprocess
from pathlib import Path

PFSI_DIR = os.path.expanduser("~/.openclaw/skills/fts5")  # Keep path for compatibility
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")
CRON_HOOK = os.path.expanduser("~/.openclaw/scripts/fts5-indexer.sh")
ORIGINAL_SELF_IMPROVING = os.path.expanduser("~/self-improving")
MERGED_SELF_IMPROVING = os.path.join(PFSI_DIR, "self_improving")
PROACTIVITY_DIR = os.path.expanduser("~/proactivity")

# Version info
VERSION = "2.0.0"

def print_step(msg):
    print(f"\n📦 {msg}")

def print_success(msg):
    print(f"   ✅ {msg}")

def print_error(msg):
    print(f"   ❌ {msg}")

def print_info(msg):
    print(f"   ℹ️  {msg}")

def print_warning(msg):
    print(f"   ⚠️  {msg}")

def check_already_installed():
    """Check if PFSI is already installed."""
    return os.path.exists(PFSI_DIR)

def check_openclaw_installed():
    """Check if OpenClaw is installed."""
    return os.path.exists(OPENCLAW_DIR)

# ── Conflict Detection ──────────────────────────────────────────

def check_existing_self_improving():
    """Check if Self-Improving is already installed."""
    return os.path.exists(ORIGINAL_SELF_IMPROVING)

def check_existing_proactivity():
    """Check if Proactivity is already installed."""
    return os.path.exists(PROACTIVITY_DIR)

def check_conflicts():
    """
    Check for potential conflicts with existing installations.
    Returns dict with conflict information.
    """
    conflicts = {
        'self_improving': check_existing_self_improving(),
        'proactivity': check_existing_proactivity(),
        'pfsi': check_already_installed(),
    }
    
    # Check for version mismatches
    if conflicts['self_improving']:
        si_memory = os.path.join(ORIGINAL_SELF_IMPROVING, "memory.md")
        if os.path.exists(si_memory):
            # Check if PFSI-specific patterns exist
            with open(si_memory, 'r') as f:
                content = f.read()
                if "PFSI" in content or "Proactive" in content:
                    conflicts['si_version_mismatch'] = True

    if conflicts['proactivity']:
        pv = os.path.join(PROACTIVITY_DIR, "memory.md")
        if os.path.exists(pv):
            with open(pv, 'r') as f:
                content = f.read()
                if "PFSI" in content:
                    conflicts['pv_version_mismatch'] = True

    return conflicts

def report_conflicts(conflicts):
    """Report detected conflicts to user."""
    print_step("Checking for existing installations...")
    
    if conflicts['pfsi']:
        print_warning(f"PFSI already installed at {PFSI_DIR}")
        response = input("   Re-install? [y/N]: ").strip().lower()
        if response != 'y':
            print_info("Keeping existing installation")
            return False
        print_info("Proceeding with re-installation...")
    
    if conflicts['self_improving']:
        print_success(f"Found existing Self-Improving: {ORIGINAL_SELF_IMPROVING}")
        print_info("Your learning data will be preserved and integrated")
    
    if conflicts['proactivity']:
        print_success(f"Found existing Proactivity: {PROACTIVITY_DIR}")
        print_info("PFSI will integrate with your existing Proactivity setup")
    
    return True

# ── Cron Setup ──────────────────────────────────────────────────

def create_cron_hook():
    """Create the PFSI indexer cron hook script."""
    print_step("Creating cron hook...")

    scripts_dir = os.path.dirname(CRON_HOOK)
    os.makedirs(scripts_dir, exist_ok=True)

    hook_content = """#!/bin/bash
# OpenClaw PFSI Indexer Cron Hook
# This script is triggered by OpenClaw heartbeat to index new messages

PFSI_DIR="$HOME/.openclaw/skills/fts5"
LOG_FILE="$HOME/.openclaw/logs/fts5-indexer.log"

# Run indexer if PFSI is installed
if [ -f "$PFSI_DIR/indexer.py" ]; then
    python3 "$PFSI_DIR/indexer.py" >> "$LOG_FILE" 2>&1
fi
"""

    with open(CRON_HOOK, 'w') as f:
        f.write(hook_content)

    os.chmod(CRON_HOOK, 0o755)
    print_success(f"Cron hook created: {CRON_HOOK}")

def add_fts5_cron():
    """Add PFSI indexer to crontab (tries sudo first, falls back to user)."""
    print_step("Setting up PFSI cron (every 5 minutes)...")

    cron_entry = "*/5 * * * * $HOME/.openclaw/scripts/fts5-indexer.sh"

    # Try sudo first (for system-wide crontab)
    try:
        result = subprocess.run(['sudo', 'crontab', '-l'], capture_output=True, text=True)
        current_cron = result.stdout if result.returncode == 0 else ""

        if 'fts5-indexer.sh' in current_cron:
            print_success("PFSI cron already configured")
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
            print_success("PFSI cron already configured")
            return True

        new_cron = current_cron.strip() + '\n' + cron_entry + '\n'
        subprocess.run(['crontab', '-'], input=new_cron, text=True)
        print_success("User crontab updated")
        return True

    except Exception as e:
        print_error(f"User crontab update failed: {e}")
        return False

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

# ── Integration Setup ────────────────────────────────────────────

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

        print("\n   Would you like to update your cron to use the new PFSI scripts?")
        response = input("   Update cron to PFSI scripts? [y/N]: ").strip().lower()

        if response == 'y':
            setup_exchange_cron(use_fts5_scripts=True)
        else:
            print_info("Keeping existing cron configuration")
            setup_exchange_cron(use_fts5_scripts=False)

    elif has_merged:
        print_success(f"Using merged Self-Improving: {MERGED_SELF_IMPROVING}")
        setup_exchange_cron(use_fts5_scripts=True)

    else:
        print_info("No existing Self-Improving found")
        print_info("Self-Improving is embedded in PFSI repo and ready to use")

def setup_proactivity_integration():
    """
    Handle Proactivity integration.
    Proactivity is auto-detected and integrated.
    """
    print_step("Checking Proactivity integration...")
    
    has_proactivity = check_existing_proactivity()
    
    if has_proactivity:
        print_success(f"Found existing Proactivity: {PROACTIVITY_DIR}")
        print_info("PFSI will automatically integrate with Proactivity")
        print_info("Proactive checks will use your existing session-state.md")
    else:
        print_info("No existing Proactivity found")
        print_info("PFSI will create its own Proactivity state directory")
        print_info("To install Proactivity separately: clawhub install proactivity")

# ── Main ─────────────────────────────────────────────────────────

def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   OpenClaw PFSI Installer                                    ║
║   Proactive Full-text Self-improving Integration             ║
║   Version {VERSION}                                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Check OpenClaw
    if not check_openclaw_installed():
        print("❌ OpenClaw not found at ~/.openclaw/")
        print("   Please install OpenClaw first: https://github.com/openclaw/openclaw")
        sys.exit(1)

    print_success("OpenClaw found")

    # Check for conflicts
    conflicts = check_conflicts()
    if not report_conflicts(conflicts):
        print("\nInstallation cancelled")
        sys.exit(0)

    # Create cron hook
    create_cron_hook()

    # Setup integrations
    setup_self_improving_integration()
    setup_proactivity_integration()

    # Setup PFSI cron
    print("\n⚠️  Cron setup requires sudo for system-wide installation")
    response = input("   Setup cron for automatic indexing? [Y/n]: ").strip().lower()
    if response != 'n':
        add_fts5_cron()
    else:
        print_info("Cron skipped - manual indexing only")
        print_info("Run 'python3 $HOME/.openclaw/skills/fts5/indexer.py' manually")

    # Summary
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ✅ OpenClaw PFSI Installation Complete!                     ║
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
   Main: $HOME/.openclaw/skills/fts5/README.md

⚙️  Cron Hooks:
   PFSI Indexer: $HOME/.openclaw/scripts/fts5-indexer.sh (every 5 min)
   Self-Improving Exchange: $HOME/.openclaw/skills/fts5/self_improving/scripts/exchange-cron.sh (3 AM daily)

🧠 Integrations:
   Self-Improving: Auto-detected (existing installations preserved)
   Proactivity: Auto-detected (existing installations integrated)
   Database: Auto-created at ~/.openclaw/fts5.db (never committed to repo)
""")

if __name__ == "__main__":
    main()
