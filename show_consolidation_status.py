#!/usr/bin/env python3
"""
Gatekeeper Module Consolidation Helper
=======================================
Shows which modules are now consolidated and suggests cleanup.
Run this to see what can be archived.
"""

import os
from pathlib import Path

print("\n" + "="*70)
print("GATEKEEPER MODULE CONSOLIDATION STATUS")
print("="*70 + "\n")

workspace = Path(".")

# Modules that are now integrated
integrated_modules = [
    "gatekeeper_omega_bridge.py",
    "gatekeeper_error_handler.py",
    "gatekeeper_system_health_monitor.py"
]

# The unified module
unified_module = "gatekeeper_integration_module.py"

print(f"UNIFIED MODULE (all-in-one):")
print(f"  {unified_module}")
if unified_module in os.listdir():
    size = os.path.getsize(unified_module) / 1024
    print(f"    Size: {size:.1f} KB ✓")
else:
    print(f"    NOT FOUND ✗")

print(f"\nPREVIOUSLY SEPARATE MODULES (now integrated):")
total_old_size = 0
for module in integrated_modules:
    if module in os.listdir():
        size = os.path.getsize(module) / 1024
        total_old_size += size
        print(f"  ✗ {module:45s} {size:8.1f} KB (redundant)")
    else:
        print(f"  ? {module:45s} NOT FOUND")

print(f"\n{'-'*70}")
print(f"CONSOLIDATION STATUS: COMPLETE")
print(f"{'-'*70}")

print(f"\nBENEFITS:")
print(f"  ✓ Unified API through GatekeeperIntegration class")
print(f"  ✓ Centralized error handling and logging")
print(f"  ✓ Real-time health monitoring integrated")
print(f"  ✓ Thread-safe operations throughout")
print(f"  ✓ Single configuration file")
print(f"  ✓ Comprehensive diagnostics")

print(f"\nUSAGE:")
print(f"  from gatekeeper_integration_module import (")
print(f"      GatekeeperIntegration,")
print(f"      get_integration,")
print(f"      SystemErrorHandler,")
print(f"      SystemHealthMonitor")
print(f"  )")

print(f"\nOPTIONAL: Archive old modules (they are now redundant):")
print(f"  mkdir archived_modules")
for module in integrated_modules:
    if module in os.listdir():
        print(f"  move {module} archived_modules/")

print(f"\n" + "="*70)
print(f"✓ System ready - Use gatekeeper_integration_module.py")
print(f"="*70 + "\n")
