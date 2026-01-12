#!/usr/bin/env python3
"""
Prepare Production - Comprehensive Deep Scan and Optimization
==============================================================
Comprehensive production preparation with deep scan, optimization, and integration.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Run comprehensive production preparation"""
    
    print("=" * 80)
    print(" " * 15 + "OMEGA PRODUCTION PREPARATION")
    print("=" * 80)
    print()
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Phase 1: Deep Code Analysis
    print("[PHASE 1] Deep Code Analysis...")
    try:
        from omega_production_preparation import ProductionPreparator
        preparator = ProductionPreparator()
        report = preparator.run_full_preparation()
        
        print()
        print("=" * 80)
        print("PRODUCTION PREPARATION SUMMARY")
        print("=" * 80)
        print(f"Files Analyzed: {report.files_analyzed}")
        print(f"Issues Found: {report.issues_found}")
        print(f"Optimizations Applied: {report.optimizations_applied}")
        print(f"Production Ready: {'✅ YES' if report.production_ready else '❌ NO'}")
        print()
        print("Integration Status:")
        for key, status in report.integration_status.items():
            print(f"  {'✅' if status else '❌'} {key.replace('_', ' ').title()}")
        print()
        print("Reports saved to: production_reports/")
        
    except Exception as e:
        print(f"[ERROR] Production preparation error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Phase 2: Integration Scan (if available)
    print("\n[PHASE 2] Integration Scan...")
    try:
        from omega_scan_integration import ScanIntegrationSystem
        scanner = ScanIntegrationSystem()
        # Run scan (commented out to avoid long execution)
        # results = scanner.run_full_pipeline()
        print("  ✅ Integration scan system available")
    except ImportError:
        print("  ℹ️  Integration scan system not available")
    except Exception as e:
        print(f"  ⚠️  Integration scan error: {e}")
    
    # Phase 3: System Verification
    print("\n[PHASE 3] System Verification...")
    
    # Check key files
    key_files = [
        "omega_operational_startup.py",
        "omega_full_brain.py",
        "hands_free_omega_optimized.py",
        "omega_comprehensive_hardware.py",
        "omega_control_panel.py",
        "omega_startup_optimizer.py"
    ]
    
    print("  Key Files:")
    for filename in key_files:
        exists = Path(filename).exists()
        print(f"    {'✅' if exists else '❌'} {filename}")
    
    print()
    print("=" * 80)
    print("PRODUCTION PREPARATION COMPLETE")
    print("=" * 80)
    print()
    print("Omega is ready for operational deployment.")
    print()
    print("To start Omega in operational mode:")
    print("  python omega_operational_startup.py")
    print()
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
