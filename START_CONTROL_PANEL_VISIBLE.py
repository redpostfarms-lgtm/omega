#!/usr/bin/env python3
"""
Start Omega Control Panel - Visible Version
============================================
Ensures the GUI window displays by using block=True after initialization.
"""

import sys
import os
import threading
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Set matplotlib backend before importing anything
try:
    import matplotlib
    # Try TkAgg first (most reliable on Windows)
    try:
        matplotlib.use('TkAgg', force=True)
        print("[OK] Using TkAgg backend")
    except:
        try:
            matplotlib.use('Qt5Agg', force=True)
            print("[OK] Using Qt5Agg backend")
        except:
            print("[INFO] Using default matplotlib backend")
except:
    pass

try:
    from omega_control_panel import ControlPanel
    import matplotlib.pyplot as plt
    
    print("=" * 80)
    print("OMEGA CONTROL PANEL - STARTING")
    print("=" * 80)
    print()
    
    print("[OK] Creating control panel...")
    panel = ControlPanel()
    
    print("[OK] Starting GUI...")
    print()
    print("A GUI window should appear NOW.")
    print("If you don't see a window, check:")
    print("  1. Is matplotlib installed? (pip install matplotlib)")
    print("  2. Is tkinter available? (usually comes with Python)")
    print("  3. Check for error messages above")
    print()
    print("Press Ctrl+C to exit")
    print()
    
    # Run the panel - this will display the GUI
    try:
        # Start panel in a way that ensures window shows
        panel.running = True
        
        if hasattr(panel, '_create_gui_panel'):
            panel._create_gui_panel()
            print("[OK] GUI initialized")
            print("[OK] Showing window...")
            
            # Show the window - use block=True to ensure it displays
            plt.show(block=True)  # This will block and show the window
            
        else:
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
    print()
    print("Troubleshooting:")
    print("  1. Install matplotlib: pip install matplotlib")
    print("  2. Check if tkinter is available (usually comes with Python)")
    print("  3. Try running: python TEST_MATPLOTLIB_DISPLAY.py")
    sys.exit(1)
