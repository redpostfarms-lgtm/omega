#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FARMHUB 2026 - WORKSPACE SYSTEM SCAN
# Scans current workspace directory structure

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import glob

print("=" * 70)
print("FARMHUB 2026 - WORKSPACE SYSTEM SCAN")
print(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Workspace: {Path.cwd()}")
print("=" * 70)
print()

results = {
    'scan_date': datetime.now().isoformat(),
    'workspace': str(Path.cwd()),
    'modules': {},
    'quantum': {},
    'files_found': []
}

# Scan for FarmHub files
print("[1/5] Scanning for FarmHub Files...")
print("-" * 70)

farmhub_files = list(Path('.').rglob('FarmHub*.py'))
if farmhub_files:
    for f in farmhub_files:
        size = f.stat().st_size
        print(f"  [OK] {f.name:30} {str(f.parent)} ({size/1024:.1f} KB)")
        results['files_found'].append({
            'name': f.name,
            'path': str(f),
            'size_kb': round(size/1024, 2)
        })
        if 'Final' in f.name:
            results['modules']['FarmHub Core'] = {
                'status': 'OK',
                'path': str(f)
            }
else:
    print("  [WARN] FarmHub files not found in workspace")

print()

# Scan for quantum files
print("[2/5] Scanning for Quantum Files...")
print("-" * 70)

quantum_files = list(Path('.').rglob('*quantum*.py'))
if quantum_files:
    for f in quantum_files[:10]:  # Limit to first 10
        size = f.stat().st_size
        print(f"  [OK] {f.name:40} {str(f.parent)[:30]}")
        if 'agent_quantum_optimizer' in f.name:
            results['quantum']['Quantum Optimizer'] = {
                'status': 'OK',
                'path': str(f)
            }
        elif 'quantum_optimization' in f.name:
            results['quantum']['Quantum Optimization'] = {
                'status': 'OK',
                'path': str(f)
            }
else:
    print("  [WARN] Quantum files not found")

print()

# Scan Gatekeeper directory
print("[3/5] Scanning Gatekeeper Structure...")
print("-" * 70)

gatekeeper = Path('The Gatekeeper')
if gatekeeper.exists():
    subdirs = [d for d in gatekeeper.iterdir() if d.is_dir()]
    py_files = list(gatekeeper.rglob('*.py'))
    
    print(f"  [OK] Gatekeeper directory found")
    print(f"       Subdirectories: {len(subdirs)}")
    print(f"       Python files: {len(py_files)}")
    
    # Check for key modules
    key_modules = {
        'FarmHub': gatekeeper / 'FarmHub' / 'FarmHub_2026_Final.py',
        'Sales': gatekeeper / 'Sales' / 'QuantumSalesBot.py',
        'Fusion': gatekeeper / 'gatekeeper_fusion.py'
    }
    
    for name, path in key_modules.items():
        if path.exists():
            print(f"       [OK] {name} module found")
            results['modules'][name] = {'status': 'OK', 'path': str(path)}
        else:
            print(f"       [WARN] {name} module not found")
else:
    print("  [WARN] Gatekeeper directory not found")

print()

# Scan for test files
print("[4/5] Scanning Test Files...")
print("-" * 70)

test_files = list(Path('.').rglob('test*.py')) + list(Path('.').rglob('*test*.py'))
test_files = [f for f in test_files if 'quantum' in f.name.lower() or 'farmhub' in f.name.lower()][:5]

if test_files:
    for f in test_files:
        print(f"  [OK] {f.name}")
else:
    print("  [INFO] No test files found")

print()

# Summary
print("[5/5] Summary...")
print("-" * 70)

total_py_files = len(list(Path('.').rglob('*.py')))
total_size = sum(f.stat().st_size for f in Path('.').rglob('*.py'))

print(f"  Total Python files in workspace: {total_py_files}")
print(f"  Total size: {total_size/(1024*1024):.1f} MB")
print(f"  FarmHub modules found: {len([m for m in results['modules'].values() if m.get('status') == 'OK'])}")
print(f"  Quantum modules found: {len([m for m in results['quantum'].values() if m.get('status') == 'OK'])}")

print()
print("=" * 70)
print("WORKSPACE SCAN COMPLETE")
print("=" * 70)

# Save results
with open('workspace_scan_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: workspace_scan_results.json")
