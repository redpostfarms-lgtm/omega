#!/usr/bin/env python3
"""
Start Omega Control Panel
==========================
Quick launcher for the Omega Control Panel
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from omega_control_panel import ControlPanel
    
    print("=" * 80)
    print("OMEGA CONTROL PANEL - LAUNCHER")
    print("=" * 80)
    print()
    print("Starting control panel...")
    print("Press Ctrl+C to exit")
    print()
    
    panel = ControlPanel()
    panel.run()
    
except KeyboardInterrupt:
    print("\n\nControl panel stopped.")
    sys.exit(0)
except Exception as e:
    print(f"Error starting control panel: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
