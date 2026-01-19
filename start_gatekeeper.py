#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The Gatekeeper Omega - Standalone Launcher
Initializes and starts the complete system
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    if sys.version_info < (3, 9):
        print("Error: Python 3.9+ required")
        sys.exit(1)

def check_dependencies():
    try:
        import torch
        import transformers
        import websockets
        import aiofiles
        print("✓ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

def initialize_directories():
    dirs = [
        "data/credentials", "data/sessions", "data/logs", "data/cache",
        "config/profiles", "config/auth",
        "models/tts", "models/speech", "models/llm",
        "output/audio", "output/reports",
        "backups", "logs"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ Directories initialized")

def setup_admin():
    from gate_admin_auth import GateAdminAuth
    auth = GateAdminAuth()
    if not auth.get_status()["admin_configured"]:
        print("Setting up GATE administrator...")
        result = auth.setup_admin()
        print(f"✓ Administrator configured: {result['username']}")

def start_system():
    print("\n" + "="*70)
    print("  THE GATEKEEPER OMEGA - STARTING")
    print("="*70 + "\n")

    check_python_version()
    if not check_dependencies():
        print("\nInstall dependencies with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    initialize_directories()
    setup_admin()

    print("\n✓ System initialized successfully!")
    print("\nNext steps:")
    print("  1. Configure resources: python resource_controller.py")
    print("  2. Run tests: python run_comprehensive_tests.py")
    print("  3. Start main system: python omega_core.py")

if __name__ == "__main__":
    start_system()
