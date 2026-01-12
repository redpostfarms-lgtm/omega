#!/usr/bin/env python3
"""
Test Control Panel Display
===========================
Tests if control panel can display.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    print("=" * 80)
    print("TESTING CONTROL PANEL DISPLAY")
    print("=" * 80)
    print()
    
    print("[1/4] Importing matplotlib...")
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    print(f"[OK] Matplotlib backend: {matplotlib.get_backend()}")
    
    print("\n[2/4] Importing control panel...")
    from omega_control_panel import ControlPanel
    print("[OK] ControlPanel imported")
    
    print("\n[3/4] Creating control panel instance...")
    panel = ControlPanel()
    print("[OK] ControlPanel instance created")
    
    print("\n[4/4] Testing GUI creation...")
    print("Creating GUI panel (this should open a window)...")
    
    # Enable interactive mode
    plt.ion()
    
    # Try to create GUI
    try:
        panel._create_gui_panel()
        print("[OK] GUI panel created")
        
        # Show window
        print("Showing window...")
        plt.show(block=False)
        plt.pause(0.1)
        
        print("[OK] Window should be visible now")
        print("\nPress Enter to continue...")
        input()
        
        panel.stop()
        print("[OK] Test complete")
        
    except Exception as e:
        print(f"[ERROR] Failed to create GUI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
