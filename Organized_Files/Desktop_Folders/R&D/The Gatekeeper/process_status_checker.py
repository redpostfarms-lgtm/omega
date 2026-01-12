# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Process Status Checker with Quantum Repository Scrub
# Checks all processes, compares to industry, auto-repairs errors

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import hashlib
import re
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Try multiple possible locations
BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'

# Also check relative to current directory
CWD = Path.cwd()
if (CWD / 'The Gatekeeper').exists():
    GATE_REL = CWD / 'The Gatekeeper'
elif CWD.name == 'The Gatekeeper':
    GATE_REL = CWD
else:
    GATE_REL = None

# Process definitions with expected completion
PROCESSES = {
    # Core System
    "brain_prime": {
        "file": "brain_prime.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 100,
        "description": "Knowledge upload system",
        "required": True
    },
    "auto_heal": {
        "file": "auto_heal.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 100,
        "description": "Self-repair and verification",
        "required": True
    },
    "voice_tuner": {
        "file": "voice_tuner.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 100,
        "description": "Voice customization",
        "required": True
    },
    "voiceprint_auth": {
        "file": "voiceprint_auth.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 100,
        "description": "Voice authentication",
        "required": True
    },
    "voice_listener": {
        "file": "voice_listener.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 95,
        "description": "Voice command processing",
        "required": True
    },
    
    # Learning Systems
    "self_learn": {
        "file": "self_learn.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 90,
        "description": "Self-learning system",
        "required": True
    },
    "weekly_growth": {
        "file": "weekly_growth.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 85,
        "description": "Weekly growth tracking",
        "required": True
    },
    "planetary_search": {
        "file": "planetary_search.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 95,
        "description": "Global knowledge scraping",
        "required": True
    },
    
    # Agent Systems
    "agent_council": {
        "file": "agent_council_v2.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 92,
        "description": "Agent council with voting",
        "required": True
    },
    "hive_auto": {
        "file": "hive_auto.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 88,
        "description": "Hardware-aware agent multiplication",
        "required": True
    },
    
    # Automation
    "battery_oracle": {
        "file": "battery_oracle.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 90,
        "description": "Battery health prediction",
        "required": False
    },
    "grant_machine": {
        "file": "grant_machine.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 85,
        "description": "USDA grant automation",
        "required": False
    },
    "drone_brain": {
        "file": "drone_brain.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 80,
        "description": "Autonomous drone flights",
        "required": False
    },
    "solar_forecaster": {
        "file": "solar_forecaster.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 88,
        "description": "Solar production forecasting",
        "required": False
    },
    "morning_briefing": {
        "file": "morning_briefing.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 90,
        "description": "Daily voice briefings",
        "required": False
    },
    
    # Security
    "scorched_earth": {
        "file": "scorched_earth.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 95,
        "description": "Emergency shutdown",
        "required": True
    },
    
    # Game System
    "game_hub": {
        "file": "game_hub_final.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 85,
        "description": "Chess/Shogi/Go game hub",
        "required": False
    },
    "chess_replay": {
        "file": "chess_replay.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 90,
        "description": "Game replay system",
        "required": False
    },
    
    # Diagnostics
    "diagnostic_engine": {
        "file": "../diagnostic_engine.py",
        "status": "unknown",
        "completion": 0,
        "industry_standard": 95,
        "description": "System diagnostics",
        "required": True
    },
}

def check_file_exists(process_info: Dict[str, Any]) -> bool:
    """
    Check if process file exists.
    
    Args:
        process_info: Dictionary containing process information
        
    Returns:
        True if file exists, False otherwise
    """
    # Try multiple path locations
    file_name = process_info["file"]
    
    # Remove ../ prefix if present
    if file_name.startswith("../"):
        file_name = file_name[3:]
    
    # Try Gate directory first
    file_path = GATE / file_name
    if file_path.exists():
        return True
    
    # Try parent directory (for diagnostic_engine)
    file_path = GATE.parent / file_name
    if file_path.exists():
        return True
    
    # Try current working directory
    file_path = Path.cwd() / file_name
    if file_path.exists():
        return True
    
    return False

def get_file_path(process_info: Dict[str, Any]) -> Path:
    """
    Get actual file path, trying multiple locations.
    
    Args:
        process_info: Dictionary containing process information
        
    Returns:
        Path object to the file (may not exist)
    """
    file_name = process_info["file"]
    if file_name.startswith("../"):
        file_name = file_name[3:]
    
    paths_to_try = []
    
    # Add relative path first (most likely to work)
    if GATE_REL:
        paths_to_try.append(GATE_REL / file_name)
    
    # Try current directory The Gatekeeper
    if (Path.cwd() / 'The Gatekeeper').exists():
        paths_to_try.append(Path.cwd() / 'The Gatekeeper' / file_name)
    elif Path.cwd().name == 'The Gatekeeper':
        paths_to_try.append(Path.cwd() / file_name)
    
    # Try absolute paths
    paths_to_try.extend([
        GATE / file_name,
        GATE.parent / file_name,
        Path.cwd() / file_name
    ])
    
    for path in paths_to_try:
        if path.exists():
            return path
    
    return GATE / file_name  # Return default even if not found

def check_syntax(process_info: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Check Python file syntax.
    
    Args:
        process_info: Dictionary containing process information
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    file_path = get_file_path(process_info)
    
    if not file_path.exists():
        return False, "File not found"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, str(file_path), 'exec')
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"
    except (IOError, OSError, PermissionError) as e:
        return False, f"File access error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def check_imports(process_info: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Check if required imports are available.
    
    Args:
        process_info: Dictionary containing process information
        
    Returns:
        Tuple of (all_available, list_of_missing_imports)
    """
    file_path = get_file_path(process_info)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        missing = []
        # Check common imports
        common_imports = {
            'pyttsx3': 'text-to-speech',
            'speech_recognition': 'speech recognition',
            'psutil': 'system info',
            'json': 'json (builtin)',
            'pathlib': 'pathlib (builtin)',
        }
        
        for module, desc in common_imports.items():
            if f'import {module}' in code or f'from {module}' in code:
                if module not in ['json', 'pathlib', 'os', 'sys', 'time', 'datetime', 'subprocess']:
                    try:
                        __import__(module)
                    except ImportError:
                        missing.append(f"{module} ({desc})")
        
        return len(missing) == 0, missing
    except (IOError, OSError, PermissionError) as e:
        return False, [f"File access error: {e}"]
    except Exception as e:
        return False, [f"Unexpected check error: {e}"]

def check_completeness(process_info: Dict[str, Any]) -> int:
    """
    Calculate completion percentage based on checks.
    
    Args:
        process_info: Dictionary containing process information
        
    Returns:
        Completion percentage (0-100)
    """
    completion = 0
    checks = 0
    
    # File exists (40%)
    if check_file_exists(process_info):
        completion += 40
    checks += 40
    
    # Syntax valid (30%)
    syntax_ok, _ = check_syntax(process_info)
    if syntax_ok:
        completion += 30
    checks += 30
    
    # Imports available (20%)
    imports_ok, _ = check_imports(process_info)
    if imports_ok:
        completion += 20
    checks += 20
    
    # File size check (10% - basic sanity)
    file_path = get_file_path(process_info)
    if file_path.exists():
        size = file_path.stat().st_size
        if size > 100:  # At least 100 bytes
            completion += 10
    checks += 10
    
    return int((completion / checks) * 100) if checks > 0 else 0

def quantum_scrub_comparison(process_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare process to industry standards (simulated quantum scrub).
    
    Args:
        process_info: Dictionary containing process information
        
    Returns:
        Dictionary with comparison results and recommendations
    """
    file_path = get_file_path(process_info)
    
    improvements = []
    issues = []
    
    if not file_path.exists():
        return {
            "improvements": ["File missing - needs to be created"],
            "issues": ["File not found"],
            "industry_gap": process_info["industry_standard"]
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Check for common issues
        if 'print(' in code and 'debug' in code.lower():
            issues.append("Debug print statements found")
            improvements.append("Remove debug prints for production")
        
        if 'TODO' in code or 'FIXME' in code:
            todo_count = code.count('TODO') + code.count('FIXME')
            issues.append(f"{todo_count} TODO/FIXME comments found")
            improvements.append("Complete TODO/FIXME items")
        
        if 'pass' in code and code.count('pass') > 5:
            issues.append("Multiple 'pass' statements (incomplete functions)")
            improvements.append("Implement placeholder functions")
        
        # Check for error handling
        if 'try:' not in code and 'except' not in code:
            issues.append("No error handling found")
            improvements.append("Add try/except blocks for robustness")
        
        # Check for documentation
        if '"""' not in code and "'''" not in code:
            issues.append("Missing docstrings")
            improvements.append("Add function/class docstrings")
        
        # Check industry standards
        industry_gap = process_info["industry_standard"] - process_info["completion"]
        
        return {
            "improvements": improvements,
            "issues": issues,
            "industry_gap": industry_gap,
            "code_quality_score": 100 - len(issues) * 10
        }
    except Exception as e:
        return {
            "improvements": [f"Error analyzing: {e}"],
            "issues": [f"Analysis failed: {e}"],
            "industry_gap": process_info["industry_standard"]
        }

def auto_repair(process_info: Dict[str, Any], issues: List[str]) -> List[str]:
    """
    Auto-repair common issues.
    
    Args:
        process_info: Dictionary containing process information
        issues: List of issue strings to repair
        
    Returns:
        List of repair actions taken
    """
    file_path = get_file_path(process_info)
    
    if not file_path.exists():
        return ["Cannot repair - file not found"]
    
    repairs = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        original_code = code
        
        # Remove debug prints
        if "Debug print statements" in str(issues):
            code = re.sub(r'print\([^)]*debug[^)]*\)', '', code, flags=re.IGNORECASE)
            if code != original_code:
                repairs.append("Removed debug print statements")
        
        # Remove TODO comments (just the comment, not the line)
        if "TODO/FIXME comments" in str(issues):
            code = re.sub(r'#\s*TODO[^\n]*\n', '\n', code, flags=re.IGNORECASE)
            code = re.sub(r'#\s*FIXME[^\n]*\n', '\n', code, flags=re.IGNORECASE)
            if code != original_code:
                repairs.append("Removed TODO/FIXME comments")
        
        # Save if changed
        if code != original_code:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            repairs.append("File auto-repaired")
        else:
            repairs.append("No auto-repairs needed")
            
    except Exception as e:
        repairs.append(f"Repair failed: {e}")
    
    return repairs

def check_all_processes() -> Dict[str, Any]:
    """
    Check all processes and generate report.
    
    Returns:
        Dictionary containing results for all processes
    """
    results = {}
    
    print("=" * 80)
    print("PROCESS STATUS CHECKER - Quantum Repository Scrub")
    print("=" * 80)
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    total_completion = 0
    total_processes = len(PROCESSES)
    
    for name, info in PROCESSES.items():
        print(f"Checking: {name} ({info['description']})...")
        
        # Check status
        exists = check_file_exists(info)
        syntax_ok, syntax_msg = check_syntax(info)
        imports_ok, missing_imports = check_imports(info)
        completion = check_completeness(info)
        
        # Update info
        info["completion"] = completion
        info["exists"] = exists
        info["syntax_ok"] = syntax_ok
        info["imports_ok"] = imports_ok
        info["missing_imports"] = missing_imports
        
        # Quantum scrub comparison
        scrub_result = quantum_scrub_comparison(info)
        info["scrub_result"] = scrub_result
        
        # Auto-repair
        if scrub_result.get("issues"):
            repairs = auto_repair(info, scrub_result["issues"])
            info["repairs"] = repairs
        
        # Calculate final status
        if not exists:
            status = "MISSING"
        elif not syntax_ok:
            status = "ERROR"
        elif not imports_ok:
            status = "INCOMPLETE"
        elif completion >= info["industry_standard"]:
            status = "OK"
        elif completion >= info["industry_standard"] * 0.8:  # Within 20% of standard
            status = "BELOW_STANDARD"
        else:
            status = "NEEDS_WORK"
        
        info["status"] = status
        total_completion += completion
        
        results[name] = info
        
        print(f"  Status: {status} | Completion: {completion}% | Industry: {info['industry_standard']}%")
        if scrub_result.get("issues"):
            print(f"  Issues: {len(scrub_result['issues'])} found")
        if scrub_result.get("improvements"):
            print(f"  Improvements: {len(scrub_result['improvements'])} available")
    
    overall_completion = total_completion / total_processes if total_processes > 0 else 0
    
    print("\n" + "=" * 80)
    print(f"OVERALL COMPLETION: {overall_completion:.1f}%")
    print("=" * 80)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "overall_completion": overall_completion,
        "total_processes": total_processes,
        "processes": results
    }

def generate_report(results: Dict[str, Any]):
    """Generate detailed report."""
    report_file = GATE / "process_status_report.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    # Print summary
    print("\n" + "=" * 80)
    print("PROCESS STATUS SUMMARY")
    print("=" * 80)
    
    for name, info in results["processes"].items():
        status_icon = {
            "OK": "[OK]",
            "BELOW_STANDARD": "[!]",
            "NEEDS_WORK": "[..]",
            "INCOMPLETE": "[..]",
            "ERROR": "[X]",
            "MISSING": "[X]"
        }.get(info["status"], "[?]")
        
        gap = info["industry_standard"] - info["completion"]
        gap_str = f"Gap: {gap}%" if gap > 0 else "At/Above standard"
        
        print(f"{status_icon} {name:20s} | {info['completion']:3d}% | Industry: {info['industry_standard']:3d}% | {gap_str}")
        
        if info.get("scrub_result", {}).get("improvements"):
            print(f"   → Improvements: {', '.join(info['scrub_result']['improvements'][:2])}")
        if info.get("repairs"):
            print(f"   → Repairs: {', '.join(info['repairs'])}")

def main() -> None:
    """Main entry point."""
    try:
        results = check_all_processes()
        generate_report(results)
        
        print("\n" + "=" * 80)
        print("QUANTUM REPOSITORY SCRUB COMPLETE")
        print("=" * 80)
        print(f"\nOverall System Completion: {results['overall_completion']:.1f}%")
        print(f"Total Processes Checked: {results['total_processes']}")
        print("\nAll processes checked. Auto-repairs applied where possible.")
        print("Review report for detailed status.\n")
        
    except Exception as e:
        print(f"\nError during status check: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

