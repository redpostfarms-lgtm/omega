#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FARMHUB 2026 - FULL SYSTEM SCAN
# Comprehensive health check of all modules, dependencies, and configurations

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace') if hasattr(sys.stdout, 'reconfigure') else None

print("=" * 70)
print("FARMHUB 2026 - FULL SYSTEM SCAN")
print(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()

# Core paths
ROOT = Path(r'D:\RPF_BRAIN')
FARMHUB = ROOT / 'FarmHub'
GATEKEEPER = ROOT / 'The Gatekeeper'
PROJECTS = GATEKEEPER / 'projects' if GATEKEEPER.exists() else Path()

# Results storage
results = {
    'scan_date': datetime.now().isoformat(),
    'modules': {},
    'dependencies': {},
    'files': {},
    'configuration': {},
    'errors': [],
    'warnings': []
}

# ==================== 1. MODULE SCAN ====================
print("[1/7] Scanning Modules...")
print("-" * 70)

modules_to_check = {
    'FarmHub Core': [
        FARMHUB / 'FarmHub_2026_Final.py',
        FARMHUB / 'master_farmhub.py'
    ],
    'Quantum': [
        PROJECTS / 'quantum_optimization.py',
        Path('agent_quantum_optimizer.py')
    ],
    'HR (Harriet)': [
        ROOT / 'HR' / 'Harriet_v2.py',
        GATEKEEPER / 'HR' / 'Harriet_v2.py'
    ],
    'Engineering (Bob)': [
        ROOT / 'Farm_Engineer' / 'Bob.py',
        GATEKEEPER / 'Farm_Engineer' / 'Bob.py'
    ],
    'Medical': [
        FARMHUB / 'medical_core_final_2026.py'
    ],
    'Apothecary': [
        FARMHUB / 'Apothecary.py'
    ],
    'FeedMaster': [
        FARMHUB / 'WormFeedCalc_Pro.py',
        FARMHUB / 'WormFeedCalc.py'
    ],
    'Sales': [
        GATEKEEPER / 'Sales' / 'QuantumSalesBot.py'
    ],
    'Gatekeeper Fusion': [
        GATEKEEPER / 'gatekeeper_fusion.py'
    ]
}

for module_name, paths in modules_to_check.items():
    found = False
    found_path = None
    
    for path in paths:
        if path.exists():
            found = True
            found_path = str(path)
            size = path.stat().st_size
            results['modules'][module_name] = {
                'status': 'OK',
                'path': found_path,
                'size_bytes': size,
                'size_kb': round(size / 1024, 2)
            }
            print(f"  [OK] {module_name:25} {found_path} ({size/1024:.1f} KB)")
            break
    
    if not found:
        results['modules'][module_name] = {'status': 'NOT FOUND'}
        results['warnings'].append(f"{module_name} module not found")
        print(f"  [WARN] {module_name:25} Not found")

print()

# ==================== 2. DEPENDENCY SCAN ====================
print("[2/7] Scanning Dependencies...")
print("-" * 70)

dependencies = {
    'pyttsx3': 'TTS/Speech',
    'cv2': 'OpenCV (Vision)',
    'ultralytics': 'YOLO (Vision)',
    'vosk': 'Speech Recognition',
    'pyaudio': 'Audio Input',
    'qiskit': 'Quantum Computing (Optional)',
    'numpy': 'Numerical Computing',
    'json': 'JSON (Built-in)',
    'pathlib': 'Path handling (Built-in)',
    'threading': 'Threading (Built-in)',
    'subprocess': 'Subprocess (Built-in)'
}

for dep_name, purpose in dependencies.items():
    try:
        if dep_name == 'cv2':
            import cv2
            version = cv2.__version__
        elif dep_name == 'ultralytics':
            import ultralytics
            version = ultralytics.__version__
        elif dep_name == 'pyttsx3':
            import pyttsx3
            version = 'installed'
        elif dep_name == 'vosk':
            import vosk
            version = 'installed'
        elif dep_name == 'pyaudio':
            import pyaudio
            version = pyaudio.__version__
        elif dep_name == 'qiskit':
            import qiskit
            version = qiskit.__version__
        elif dep_name == 'numpy':
            import numpy
            version = numpy.__version__
        else:
            version = 'built-in'
        
        results['dependencies'][dep_name] = {
            'status': 'OK',
            'version': version,
            'purpose': purpose
        }
        print(f"  [OK] {dep_name:20} {purpose:30} v{version}")
    
    except ImportError:
        results['dependencies'][dep_name] = {
            'status': 'NOT INSTALLED',
            'purpose': purpose
        }
        if dep_name not in ['json', 'pathlib', 'threading', 'subprocess']:
            results['warnings'].append(f"{dep_name} not installed ({purpose})")
            print(f"  [WARN] {dep_name:20} {purpose:30} Not installed")

print()

# ==================== 3. QUANTUM MODULE DEEP SCAN ====================
print("[3/7] Deep Scanning Quantum Module...")
print("-" * 70)

# Test quantum optimizer
try:
    sys.path.insert(0, str(PROJECTS))
    sys.path.insert(0, str(Path.cwd()))
    
    from agent_quantum_optimizer import QuantumOptimizer
    opt = QuantumOptimizer(dimensions=5, num_particles=10)
    
    def test_fitness(x):
        return sum(xi**2 for xi in x)
    
    result = opt.optimize(test_fitness, max_iterations=20)
    
    results['modules']['Quantum Optimizer'] = {
        'status': 'OK',
        'best_fitness': opt.global_best_fitness,
        'test_passed': True
    }
    print(f"  [OK] Quantum Optimizer working (fitness: {opt.global_best_fitness:.6f})")
    
except Exception as e:
    results['modules']['Quantum Optimizer'] = {
        'status': 'ERROR',
        'error': str(e)
    }
    results['errors'].append(f"Quantum optimizer error: {e}")
    print(f"  [ERROR] Quantum Optimizer: {e}")

# Test quantum optimization
try:
    from quantum_optimization import QuantumOptimization
    qopt = QuantumOptimization()
    results['modules']['Quantum Optimization'] = {
        'status': 'OK',
        'qiskit_available': qopt.qiskit_available,
        'dwave_available': qopt.dwave_available
    }
    print(f"  [OK] Quantum Optimization module loaded")
    print(f"       Qiskit: {'Available' if qopt.qiskit_available else 'Not installed'}")
    print(f"       D-Wave: {'Available' if qopt.dwave_available else 'Not installed'}")
    
except ImportError:
    results['modules']['Quantum Optimization'] = {
        'status': 'NOT IN PATH',
        'note': 'Using fallback quantum optimizer'
    }
    print(f"  [INFO] Quantum Optimization module not in path (using fallback)")

print()

# ==================== 4. FILE STRUCTURE SCAN ====================
print("[4/7] Scanning File Structure...")
print("-" * 70)

directories_to_check = {
    'FarmHub': FARMHUB,
    'Gatekeeper': GATEKEEPER,
    'Projects': PROJECTS,
    'HR': ROOT / 'HR',
    'Farm Engineer': ROOT / 'Farm_Engineer',
    'Sales': GATEKEEPER / 'Sales' if GATEKEEPER.exists() else None
}

for dir_name, dir_path in directories_to_check.items():
    if dir_path and dir_path.exists():
        file_count = len(list(dir_path.rglob('*.py')))
        total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
        results['files'][dir_name] = {
            'path': str(dir_path),
            'python_files': file_count,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'exists': True
        }
        print(f"  [OK] {dir_name:20} {file_count:3} Python files, {total_size/(1024*1024):.1f} MB")
    else:
        results['files'][dir_name] = {'exists': False}
        print(f"  [WARN] {dir_name:20} Directory not found")

print()

# ==================== 5. CONFIGURATION SCAN ====================
print("[5/7] Scanning Configuration Files...")
print("-" * 70)

config_files = {
    'Knowledge Base': FARMHUB / 'knowledge_2026.json',
    'Voice Key': FARMHUB / 'voiceprint.sha256',
    'FarmHub Brain': FARMHUB / 'farmhub_brain.json',
    'Laws': FARMHUB / 'laws_2026.json'
}

for config_name, config_path in config_files.items():
    if config_path.exists():
        size = config_path.stat().st_size
        results['configuration'][config_name] = {
            'status': 'OK',
            'path': str(config_path),
            'size_bytes': size
        }
        print(f"  [OK] {config_name:20} {str(config_path)} ({size} bytes)")
    else:
        results['configuration'][config_name] = {'status': 'NOT FOUND'}
        print(f"  [INFO] {config_name:20} Not found (will be created on first run)")

print()

# ==================== 6. PYTHON ENVIRONMENT SCAN ====================
print("[6/7] Scanning Python Environment...")
print("-" * 70)

try:
    python_version = sys.version
    python_executable = sys.executable
    platform = sys.platform
    
    results['configuration']['Python'] = {
        'version': python_version.split()[0],
        'executable': python_executable,
        'platform': platform
    }
    print(f"  [OK] Python Version: {python_version.split()[0]}")
    print(f"  [OK] Executable: {python_executable}")
    print(f"  [OK] Platform: {platform}")
except Exception as e:
    results['errors'].append(f"Python environment scan error: {e}")

print()

# ==================== 7. SYSTEM HEALTH SUMMARY ====================
print("[7/7] System Health Summary...")
print("-" * 70)

# Count statuses
modules_ok = sum(1 for m in results['modules'].values() if m.get('status') == 'OK')
modules_total = len(results['modules'])
modules_found = sum(1 for m in results['modules'].values() if m.get('status') != 'NOT FOUND')

deps_ok = sum(1 for d in results['dependencies'].values() if d.get('status') == 'OK')
deps_total = len([d for d in results['dependencies'] if d not in ['json', 'pathlib', 'threading', 'subprocess']])

print(f"  Modules Found:     {modules_found}/{modules_total} ({modules_found*100//modules_total if modules_total > 0 else 0}%)")
print(f"  Dependencies OK:   {deps_ok}/{deps_total} ({deps_ok*100//deps_total if deps_total > 0 else 0}%)")
print(f"  Errors:            {len(results['errors'])}")
print(f"  Warnings:          {len(results['warnings'])}")

print()

# ==================== FINAL REPORT ====================
print("=" * 70)
print("SCAN COMPLETE")
print("=" * 70)
print()

if results['errors']:
    print("ERRORS FOUND:")
    for error in results['errors']:
        print(f"  [ERROR] {error}")
    print()

if results['warnings']:
    print("WARNINGS:")
    for warning in results['warnings'][:10]:  # Limit to first 10
        print(f"  [WARN] {warning}")
    if len(results['warnings']) > 10:
        print(f"  ... and {len(results['warnings']) - 10} more warnings")
    print()

# Save results
results_file = Path('system_scan_results.json')
with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Detailed results saved to: {results_file}")
print()

# Overall status
if len(results['errors']) == 0 and modules_found >= modules_total * 0.7:
    print("[OK] System is HEALTHY - Ready for operation")
elif len(results['errors']) == 0:
    print("[WARN] System is FUNCTIONAL but some modules missing")
else:
    print("[ERROR] System has ERRORS - Review and fix")

print("=" * 70)
