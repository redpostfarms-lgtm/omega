"""
Omega UI Launcher
=================
Main launcher for Omega User Interface and system connection.
Uses visible display method to ensure window shows.
"""

import sys
import os
from pathlib import Path

base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

try:
    import matplotlib
    matplotlib.use('TkAgg', force=True)
except (ImportError, ValueError):
    pass

def launch_omega_ui():
    """Launch Omega Control Panel UI"""
    try:
        print("=" * 80)
        print(" " * 25 + "OMEGA UI LAUNCHER")
        print("=" * 80)
        print()
        print("Starting Omega Control Panel...")
        print("Loading cached data for fast startup...")
        print()
        
        from omega_control_panel import ControlPanel
        
        panel = ControlPanel()
        
        print("[OK] Control Panel initialized")
        print("[OK] Starting GUI...")
        print()
        print("The Omega Control Panel window should appear shortly.")
        print("Keep this window open - the UI will stay visible and interactive.")
        print("Press Ctrl+C to exit")
        print()
        
        panel.run()
        
    except ImportError as e:
        print(f"[ERROR] Failed to import control panel: {e}")
        print("Make sure omega_control_panel.py is in the base directory")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nStopping control panel...")
        if 'panel' in locals():
            panel.stop()
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Failed to start Omega UI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    launch_omega_ui()
