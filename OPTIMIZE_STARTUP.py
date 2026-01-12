#!/usr/bin/env python3
"""
Optimize Startup - Quick Script
================================
Quick script to optimize Windows startup and add Omega to startup.
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from omega_startup_optimizer import StartupOptimizer
    import platform
    
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows only")
        sys.exit(1)
    
    print("=" * 80)
    print("OMEGA STARTUP OPTIMIZER - QUICK RUN")
    print("=" * 80)
    print()
    
    optimizer = StartupOptimizer()
    
    # Scan startup items
    print("Scanning startup items...")
    optimizer.scan_startup_items()
    
    report = optimizer.get_startup_report()
    print(f"Found {report['total_items']} startup items")
    print(f"  - Essential: {report['essential_items']}")
    print(f"  - Non-essential: {report['non_essential_items']} ({report['enabled_non_essential']} enabled)")
    print()
    
    # Remove tracking items
    tracking_items = optimizer.get_tracking_items()
    enabled_tracking = [item for item in tracking_items if item.enabled]
    if enabled_tracking:
        print(f"Removing {len(enabled_tracking)} tracking/telemetry items...")
        tracking_results = optimizer.remove_all_tracking()
        print(f"✅ Removed: {len(tracking_results['removed'])}")
        if tracking_results['failed']:
            print(f"⚠️  Failed: {len(tracking_results['failed'])} (may need admin privileges)")
    else:
        print("✅ No tracking items to remove")
    
    print()
    
    # Remove non-essential items
    if report['enabled_non_essential'] > 0:
        print(f"Removing {report['enabled_non_essential']} non-essential startup items...")
        results = optimizer.remove_all_non_essential()
        print(f"✅ Removed: {len(results['removed'])}")
        if results['failed']:
            print(f"⚠️  Failed: {len(results['failed'])} (may need admin privileges)")
    else:
        print("✅ No non-essential startup items to remove")
    
    print()
    
    # Add Omega to startup
    if not report['omega_in_startup']:
        print("Adding Omega to startup...")
        success, message = optimizer.add_omega_to_startup()
        print(message)
        if success:
            print("✅ Omega will now start automatically on login")
    else:
        print("✅ Omega is already in startup")
    
    print()
    print("=" * 80)
    print("Startup optimization complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Restart your computer to see the improvements")
    print("  2. Omega will start automatically on login")
    print("  3. Backup saved to: startup_backup.json")
    print()
    print("To restore disabled items, run:")
    print("  python omega_startup_optimizer.py")
    print("  Then choose restore option")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
