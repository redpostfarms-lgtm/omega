#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
#
# QUANTUM SELF-REPAIR SCRIPT
# Auto-generated from quantum_deep_audit_2026.py
# Date: 2026-01-03T17:38:25.464656

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(r'D:\\RPF_BRAIN\\The Gatekeeper')

def repair_system():
    """Auto-repair system based on audit findings."""
    print("=" * 60)
    print("QUANTUM SELF-REPAIR - AUTO-FIXING SYSTEM")
    print("=" * 60)
    print()
    
    repairs_applied = []
    
    # Repair 1: Install missing dependencies
    print("[1] Checking dependencies...")
    try:
        import pdfplumber
    except ImportError:
        print("  Installing pdfplumber...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pdfplumber'], check=True)
        repairs_applied.append("Installed pdfplumber")
    
    try:
        import PyPDF2
    except ImportError:
        print("  Installing PyPDF2...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'PyPDF2'], check=True)
        repairs_applied.append("Installed PyPDF2")
    
    # Repair 2: Verify critical files
    print("[2] Verifying critical files...")
    critical_files = [
        'brain_prime.py',
        'auto_heal.py',
        'voice_listener.py',
    ]
    
    for filename in critical_files:
        filepath = ROOT / filename
        if not filepath.exists():
            print(f"  WARNING: {filename} not found")
        else:
            print(f"  ✓ {filename} exists")
    
    # Repair 3: Run tests
    print("[3] Running system tests...")
    test_dir = ROOT / 'tests'
    if test_dir.exists():
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', str(test_dir), '-v'],
            capture_output=True,
            text=True,
            cwd=str(ROOT)
        )
        if result.returncode == 0:
            print("  ✓ All tests passed")
        else:
            print(f"  ⚠ Some tests failed")
            print(result.stdout)
    
    print()
    print("=" * 60)
    print("SELF-REPAIR COMPLETE")
    print("=" * 60)
    print(f"Repairs applied: {len(repairs_applied)}")
    for repair in repairs_applied:
        print(f"  ✓ {repair}")
    print()

if __name__ == '__main__':
    repair_system()
