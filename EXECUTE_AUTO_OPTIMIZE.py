#!/usr/bin/env python3
"""Execute auto optimization and show results"""
import subprocess
import sys
from pathlib import Path

base_dir = Path(__file__).parent.absolute()

print("\n" + "=" * 80)
print(" " * 25 + "EXECUTING AUTO OPTIMIZATION")
print("=" * 80)
print()

try:
    # Run the optimization script
    result = subprocess.run(
        [sys.executable, str(base_dir / "AUTO_SELECT_AND_OPTIMIZE.py")],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Print output
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print(f"Return code: {result.returncode}")
    
    # Check for log file
    log_file = base_dir / "auto_optimization_log.json"
    if log_file.exists():
        print(f"\n[OK] Optimization log created: {log_file.name}")
        import json
        with open(log_file) as f:
            log_data = json.load(f)
            print(f"Total apps optimized: {log_data.get('stats', {}).get('total', 0)}")
    
except Exception as e:
    print(f"[ERROR] Failed to execute: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
