#!/usr/bin/env python3
"""
FTS5 Linter - Architectural Enforcement Tool
Enforces harness engineering principles mechanically.

Rules:
1. __init__.py only exports public API
2. Path dependency direction (no cross-layer calls)
3. exchange_engine.py layer rules validated
4. exchange-cron.sh has correct permissions (755)
5. No hardcoded paths (use Path/home())
6. Scripts must have executable permission
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict

# Colors for output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

FTS5_DIR = Path(__file__).parent
ERRORS = []
WARNINGS = []

# Layer definitions
PUBLIC_API = ['search', 'summarize', 'get_stats', 'add_message']


def error(msg: str, file: str = None):
    prefix = f"{RED}❌ ERROR{RESET}"
    location = f" [{file}]" if file else ""
    print(f"{prefix}{location} {msg}")
    ERRORS.append((msg, file))


def warn(msg: str, file: str = None):
    prefix = f"{YELLOW}⚠️  WARN{RESET}"
    location = f" [{file}]" if file else ""
    print(f"{prefix}{location} {msg}")
    WARNINGS.append((msg, file))


def info(msg: str):
    print(f"{BLUE}ℹ️  INFO{RESET} {msg}")


def success(msg: str):
    print(f"{GREEN}✅ {msg}{RESET}")


def check_init_exports():
    """Rule 1: __init__.py only exports public API."""
    init_file = FTS5_DIR / '__init__.py'
    
    if not init_file.exists():
        error("__init__.py not found", "__init__.py")
        return False
    
    content = init_file.read_text()
    
    # Find all __all__ definitions
    all_matches = re.findall(r'__all__\s*=\s*\[(.*?)\]', content, re.DOTALL)
    
    # Find all function definitions
    func_matches = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
    
    # Check if any non-public function is exported
    for func in func_matches:
        if not func.startswith('_') and func not in PUBLIC_API:
            # Check if it's actually exported
            for all_list in all_matches:
                if func in all_list:
                    warn(f"Non-public API '{func}' is exported", "__init__.py")
    
    success("__init__.py export check passed")
    return True


def check_hardcoded_paths():
    """Rule 5: No hardcoded paths (except intentional constants)."""
    
    issues_found = False
    
    for py_file in FTS5_DIR.rglob('*.py'):
        if '.git' in str(py_file) or '__pycache__' in str(py_file) or 'linter.py' in str(py_file):
            continue
            
        content = py_file.read_text()
        rel_path = py_file.relative_to(FTS5_DIR)
        
        # Check for expanduser with hardcoded paths
        # Allow ORIGINAL_SELF_IMPROVING = os.path.expanduser("~/self-improving")
        # Allow _ORIGINAL_DIR = Path.home() / "self-improving"
        
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Skip comments
            if '#' in line:
                code_part = line.split('#')[0]
            else:
                code_part = line
                
            # Skip lines that define constants properly
            if 'ORIGINAL_SELF_IMPROVING' in line and '=' in line and 'expanduser' in line:
                continue
            if 'MERGED_SELF_IMPROVING' in line and '=' in line:
                continue
            if '_ORIGINAL_DIR' in line and 'Path.home()' in line:
                continue
            if '_MERGED_DIR' in line and '.parent' in line:
                continue
                
            # Check for forbidden patterns
            if 'expanduser' in code_part and 'self-improving' in code_part.lower():
                error(f"Hardcoded self-improving path found", f"{rel_path}:{i}")
                issues_found = True
    
    if not issues_found:
        success("No hardcoded paths found")
    
    return not issues_found


def check_script_permissions():
    """Rule 4 & 6: Scripts have correct permissions."""
    scripts = [
        FTS5_DIR / 'self_improving' / 'scripts' / 'exchange-cron.sh',
        FTS5_DIR.parent / 'scripts' / 'fts5-indexer.sh',
    ]
    
    all_ok = True
    for script in scripts:
        if not script.exists():
            continue
            
        mode = script.stat().st_mode & 0o777
        rel_path = script.relative_to(FTS5_DIR)
        
        if mode & 0o111 == 0:  # No execute permission
            error(f"Script not executable: {script.name} (mode: {oct(mode)})", str(rel_path))
            all_ok = False
        elif mode != 0o755:
            warn(f"Script permission not 755: {script.name} (mode: {oct(mode)})", str(rel_path))
    
    if all_ok:
        success("Script permissions correct")
    
    return all_ok


def check_path_detection_consistency():
    """All scripts must use consistent path detection logic."""
    scripts = [
        FTS5_DIR / 'self_improving' / 'scripts' / 'exchange_engine.py',
        FTS5_DIR / 'self_improving' / 'scripts' / 'reindex.py',
        FTS5_DIR / 'self_improving' / 'scripts' / 'fts5_integration.py',
        FTS5_DIR / 'self_improving' / 'scripts' / 'context_predictor.py',
    ]
    
    required_pattern = '_ORIGINAL_DIR.exists()'
    fallback_pattern = '_MERGED_DIR'
    
    all_ok = True
    for script in scripts:
        if not script.exists():
            continue
            
        content = script.read_text()
        rel_path = script.relative_to(FTS5_DIR)
        
        if required_pattern not in content:
            error(f"Missing path detection pattern in {script.name}", str(rel_path))
            all_ok = False
        elif fallback_pattern not in content:
            warn(f"Missing fallback to merged dir in {script.name}", str(rel_path))
    
    if all_ok:
        success("Path detection consistent across all scripts")
    
    return all_ok


def check_layer_dependencies():
    """Check that layers don't call across improperly."""
    
    # Allowed: fts5_integration.py can import from skills.fts5
    # context_predictor.py can import fts5_integration
    # Other scripts should not import directly
    
    allowed_imports = {
        'fts5_integration.py': ['from skills.fts5 import', 'from __init__ import'],
        'context_predictor.py': ['fts5_integration'],
    }
    
    script_files = list((FTS5_DIR / 'self_improving' / 'scripts').glob('*.py'))
    issues = []
    
    for script in script_files:
        content = script.read_text()
        script_name = script.name
        
        if script_name in allowed_imports:
            continue
        else:
            if 'from skills.fts5 import' in content or 'from __init__ import' in content:
                issues.append(script_name)
                warn(f"Script {script_name} imports directly from fts5 core", script_name)
    
    if not issues:
        success("Layer dependency check passed")
        return True
    return False


def check_exchange_engine_rules():
    """Rule 3: exchange_engine.py validates layer rules."""
    engine_file = FTS5_DIR / 'self_improving' / 'scripts' / 'exchange_engine.py'
    
    if not engine_file.exists():
        error("exchange_engine.py not found")
        return False
    
    content = engine_file.read_text()
    
    required_rules = [
        ('HOT_THRESHOLD_DAYS', '7'),  # Hot: < 7 days
        ('COLD_THRESHOLD_DAYS', '30'),  # Cold: 30+ days
        ('promote', 'promotion logic'),
        ('demote', 'demotion logic'),
    ]
    
    all_found = True
    for rule, desc in required_rules:
        if rule not in content:
            error(f"Missing {rule} ({desc})", "exchange_engine.py")
            all_found = False
    
    if all_found:
        success("exchange_engine.py layer rules validated")
    
    return all_found


def check_no_yolo_patterns():
    """Check for common 'YOLO' anti-patterns."""
    anti_patterns = [
        (r'# TODO.*YOLO', 'YOLO comment found'),
        (r'# FIXME.*ignore', 'FIXME ignore comment'),
    ]
    
    issues = []
    for py_file in FTS5_DIR.rglob('*.py'):
        # Skip linter.py itself and cache directories
        if '.git' in str(py_file) or '__pycache__' in str(py_file) or 'linter.py' in str(py_file):
            continue
            
        content = py_file.read_text()
        rel_path = py_file.relative_to(FTS5_DIR)
        
        for pattern, msg in anti_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warn(f"{msg}", str(rel_path))
                issues.append(rel_path)
    
    if not issues:
        success("No YOLO anti-patterns found")
    
    return len(issues) == 0


def run_all_checks() -> bool:
    """Run all linter checks."""
    print(f"""
{BLUE}{'='*60}
FTS5 Linter - Architectural Enforcement Tool
{'='*60}{RESET}
""")
    
    info(f"FTS5 Directory: {FTS5_DIR}")
    print()
    
    checks = [
        ("Export Check", check_init_exports),
        ("Hardcoded Paths", check_hardcoded_paths),
        ("Script Permissions", check_script_permissions),
        ("Path Detection Consistency", check_path_detection_consistency),
        ("Layer Dependencies", check_layer_dependencies),
        ("Exchange Engine Rules", check_exchange_engine_rules),
        ("YOLO Anti-Patterns", check_no_yolo_patterns),
    ]
    
    results = []
    for name, check_fn in checks:
        print(f"\n{BLUE}--- {name} ---{RESET}")
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            error(f"Check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print(f"""
{BLUE}{'='*60}
Summary
{'='*60}{RESET}
""")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"  {status}  {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if ERRORS:
        print(f"\n{RED}❌ {len(ERRORS)} ERROR(S){RESET}:")
        for msg, file in ERRORS:
            location = f" [{file}]" if file else ""
            print(f"  • {msg}{location}")
    
    if WARNINGS:
        print(f"\n{YELLOW}⚠️  {len(WARNINGS)} WARNING(S){RESET}:")
        for msg, file in WARNINGS:
            location = f" [{file}]" if file else ""
            print(f"  • {msg}{location}")
    
    return passed == total


if __name__ == "__main__":
    success_flag = run_all_checks()
    sys.exit(0 if success_flag else 1)
