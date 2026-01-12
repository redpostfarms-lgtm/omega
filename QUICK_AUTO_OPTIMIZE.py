#!/usr/bin/env python3
"""
Quick Auto Optimize - Simplified version that prints output immediately
"""
import sys
import os

print("\n" + "=" * 80)
print(" " * 25 + "AUTO APP OPTIMIZATION")
print("=" * 80)
print()

# Check for psutil
try:
    import psutil
    print("[OK] psutil is available")
    PSUTIL_AVAILABLE = True
except ImportError:
    print("[ERROR] psutil not available")
    print("Install with: pip install psutil")
    PSUTIL_AVAILABLE = False
    sys.exit(1)

if PSUTIL_AVAILABLE:
    print("[OK] Starting auto-optimization...")
    print()
    # Import and run the main script
    try:
        from AUTO_SELECT_AND_OPTIMIZE import AutoSelectOptimizer
        optimizer = AutoSelectOptimizer()
        stats = optimizer.run_auto_optimization()
        print("\n[OK] Optimization complete!")
        print(f"Total apps optimized: {stats.get('total', 0)}")
    except Exception as e:
        print(f"[ERROR] Optimization failed: {e}")
        import traceback
        traceback.print_exc()

print("=" * 80)
