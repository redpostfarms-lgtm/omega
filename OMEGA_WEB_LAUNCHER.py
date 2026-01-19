"""
Omega Web Interface Launcher
============================
Launcher for the Omega Control Panel web interface.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch web interface"""
    base_dir = Path(__file__).parent.absolute()
    web_file = base_dir / "omega_control_panel_web.py"
    
    if not web_file.exists():
        print(f"ERROR: Web interface file not found: {web_file}")
        sys.exit(1)
    
    print("=" * 80)
    print(" " * 20 + "OMEGA WEB INTERFACE LAUNCHER")
    print("=" * 80)
    print()
    print("Starting Omega Control Panel web interface...")
    print()
    
    try:
        subprocess.run([sys.executable, str(web_file)], cwd=str(base_dir))
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
