#!/usr/bin/env python3
"""
Trace Activation Sequence
=========================
This script adds detailed tracing to the activation sequence to identify issues.
"""

import sys
import os
import traceback
from pathlib import Path

# Add base directory to path
base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

# Set matplotlib backend before importing
try:
    import matplotlib
    print(f"[TRACE] Setting matplotlib backend to TkAgg...")
    matplotlib.use('TkAgg', force=True)
    print(f"[TRACE] Backend set to: {matplotlib.get_backend()}")
except Exception as e:
    print(f"[TRACE] Failed to set backend: {e}")

def trace_launch():
    """Trace the launch sequence with detailed logging"""
    print("=" * 80)
    print(" " * 20 + "TRACING ACTIVATION SEQUENCE")
    print("=" * 80)
    print()
    
    try:
        print("[TRACE] Step 1: Importing ControlPanel...")
        from omega_control_panel import ControlPanel
        print("[TRACE] ✓ ControlPanel imported successfully")
        print()
        
        print("[TRACE] Step 2: Creating ControlPanel instance...")
        panel = ControlPanel()
        print("[TRACE] ✓ ControlPanel instance created")
        print(f"[TRACE]   panel.running = {panel.running}")
        print(f"[TRACE]   MATPLOTLIB_AVAILABLE = {hasattr(panel, '_create_gui_panel')}")
        print()
        
        print("[TRACE] Step 3: Calling panel.run()...")
        print("[TRACE]   This should create the GUI and call plt.show(block=True)")
        print("[TRACE]   plt.show(block=True) should block until window is closed")
        print()
        
        # Check if matplotlib is available
        try:
            import matplotlib.pyplot as plt
            print(f"[TRACE]   matplotlib.pyplot imported")
            print(f"[TRACE]   Current backend: {matplotlib.get_backend()}")
            print(f"[TRACE]   Interactive mode: {plt.isinteractive()}")
        except Exception as e:
            print(f"[TRACE]   ERROR checking matplotlib: {e}")
        
        print()
        print("[TRACE] Starting panel.run() now...")
        print("[TRACE] If window doesn't appear or closes immediately, we'll catch it")
        print()
        
        # Call run() - this should block
        panel.run()
        
        print()
        print("[TRACE] panel.run() has returned")
        print("[TRACE] This means plt.show(block=True) returned")
        print("[TRACE] Window should have been closed by user")
        print()
        
    except ImportError as e:
        print(f"[TRACE] ERROR: ImportError - {e}")
        traceback.print_exc()
        return False
    except KeyboardInterrupt:
        print("\n[TRACE] KeyboardInterrupt caught - user pressed Ctrl+C")
        return True
    except Exception as e:
        print(f"[TRACE] ERROR: Exception - {type(e).__name__}: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    try:
        success = trace_launch()
        if success:
            print("\n[TRACE] Activation sequence completed")
        else:
            print("\n[TRACE] Activation sequence failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n[TRACE] Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[TRACE] Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)
