# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER - System Verification
# Checks all components are installed and working

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'

def check_file(file_path, name):
    """Check if a file exists."""
    if file_path.exists():
        print(f"  ✅ {name}")
        return True
    else:
        print(f"  ❌ {name} - MISSING")
        return False

def check_directory(dir_path, name):
    """Check if a directory exists."""
    if dir_path.exists():
        print(f"  ✅ {name}")
        return True
    else:
        print(f"  ❌ {name} - MISSING")
        return False

def check_python_module(module, name):
    """Check if a Python module is installed."""
    try:
        __import__(module)
        print(f"  ✅ {name}")
        return True
    except ImportError:
        print(f"  ❌ {name} - NOT INSTALLED")
        return False

def check_command(cmd, name):
    """Check if a command is available."""
    import subprocess
    try:
        result = subprocess.run(
            [cmd, '--version'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✅ {name}")
            return True
        else:
            print(f"  ❌ {name} - NOT WORKING")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"  ❌ {name} - NOT INSTALLED")
        return False

def verify_system():
    """Verify complete Gatekeeper system."""
    print("=" * 60)
    print("GATEKEEPER SYSTEM VERIFICATION")
    print("=" * 60)
    
    all_ok = True
    
    # Core files
    print("\n📁 Core Files:")
    core_files = [
        (GATE / 'brain_prime.py', 'brain_prime.py'),
        (GATE / 'auto_heal.py', 'auto_heal.py'),
        (GATE / 'voice_tuner.py', 'voice_tuner.py'),
        (GATE / 'voiceprint_auth.py', 'voiceprint_auth.py'),
        (GATE / 'voice_listener.py', 'voice_listener.py'),
        (GATE / 'brain_wakeup.bat', 'brain_wakeup.bat'),
    ]
    
    for path, name in core_files:
        if not check_file(path, name):
            all_ok = False
    
    # The 8 hidden pieces
    print("\n🔧 The 8 Hidden Pieces:")
    hidden_files = [
        (GATE / 'battery_oracle.py', 'battery_oracle.py'),
        (GATE / 'grant_machine.py', 'grant_machine.py'),
        (GATE / 'drone_brain.py', 'drone_brain.py'),
        (GATE / 'solar_forecaster.py', 'solar_forecaster.py'),
        (GATE / 'scorched_earth.py', 'scorched_earth.py'),
        (GATE / 'panic_button.ino', 'panic_button.ino'),
        (GATE / 'morning_briefing.py', 'morning_briefing.py'),
        (GATE / 'self_learn.py', 'self_learn.py'),
    ]
    
    for path, name in hidden_files:
        if not check_file(path, name):
            all_ok = False
    
    # Additional features
    print("\n📚 Additional Features:")
    additional_files = [
        (GATE / 'weekly_growth.py', 'weekly_growth.py'),
        (GATE / 'max_out_pipelines.py', 'max_out_pipelines.py'),
        (GATE / 'prompt_bank.py', 'prompt_bank.py'),
    ]
    
    for path, name in additional_files:
        if not check_file(path, name):
            all_ok = False
    
    # Directories
    print("\n📂 Required Directories:")
    dirs = [
        (BRAIN / 'Archived', 'Archived'),
        (BRAIN / 'Archived' / 'voiceprint', 'voiceprint'),
        (BRAIN / 'Archived' / 'learning', 'learning'),
        (BRAIN / 'Archived' / 'voice_log', 'voice_log'),
    ]
    
    for path, name in dirs:
        if not check_directory(path, name):
            all_ok = False
    
    # Python modules
    print("\n🐍 Python Modules:")
    modules = [
        ('pyttsx3', 'pyttsx3 (text-to-speech)'),
        ('numpy', 'numpy (calculations)'),
        ('speech_recognition', 'speech_recognition (voice input)'),
    ]
    
    for module, name in modules:
        if not check_python_module(module, name):
            all_ok = False
    
    # Optional tools
    print("\n🔧 Optional Tools:")
    tools = [
        ('ollama', 'Ollama (self-learning)'),
        ('pdftotext', 'pdftotext (PDF processing)'),
    ]
    
    for cmd, name in tools:
        check_command(cmd, name)
    
    # Configuration files
    print("\n⚙️  Configuration:")
    config_files = [
        (BRAIN / 'Archived' / 'gatekeeper_brain.json', 'gatekeeper_brain.json'),
        (BRAIN / 'Archived' / 'voiceprint' / 'me.npy', 'voiceprint (me.npy)'),
        (BRAIN / 'Archived' / 'voiceprint' / 'tuned' / 'tune.pkl', 'voice tuning'),
    ]
    
    for path, name in config_files:
        if path.exists():
            print(f"  ✅ {name}")
        else:
            print(f"  ⚠️  {name} - Not configured yet")
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ SYSTEM VERIFICATION PASSED")
        print("The Gatekeeper is ready to use.")
    else:
        print("⚠️  SYSTEM VERIFICATION INCOMPLETE")
        print("Some components are missing. Run setup_complete_system.bat")
    print("=" * 60)

if __name__ == '__main__':
    verify_system()

