#!/usr/bin/env python3
"""
Start Omega Control Panel - Fixed Version
==========================================
Fixed launcher that ensures the GUI window displays properly.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Ensure matplotlib uses TkAgg backend before importing anything
try:
    import matplotlib
    matplotlib.use('TkAgg')
except:
    pass

try:
    from omega_control_panel import ControlPanel
    
    print("=" * 80)
    print("OMEGA CONTROL PANEL - STARTING")
    print("=" * 80)
    print()
    
    # Check if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        print("[OK] Matplotlib available")
    except ImportError:
        print("[ERROR] Matplotlib not available!")
        print("Install with: pip install matplotlib")
        sys.exit(1)
    
    print("[OK] Starting control panel...")
    print("A GUI window should appear shortly.")
    print("Press Ctrl+C to exit")
    print()
    
    # Create and run panel
    panel = ControlPanel()
    
    # Run the panel - this will display the GUI
    try:
        panel.run()
    except KeyboardInterrupt:
        print("\n\nStopping control panel...")
        panel.stop()
        print("Control panel stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Control panel error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
except KeyboardInterrupt:
    print("\n\nControl panel stopped.")
    sys.exit(0)
except Exception as e:
    print(f"\n[ERROR] Failed to start control panel: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
