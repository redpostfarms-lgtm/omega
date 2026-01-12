#!/usr/bin/env python3
"""
Auto-Launch Omega Control Panel Web Interface
=============================================
Launches the web interface and opens it in the default browser
"""

import sys
import time
import webbrowser
import threading
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def open_browser_delayed(url, delay=2):
    """Open browser after a delay to allow server to start"""
    time.sleep(delay)
    webbrowser.open(url)
    print(f"✅ Browser opened: {url}")

def main():
    """Main entry point"""
    print("=" * 80)
    print(" " * 20 + "OMEGA CONTROL PANEL - AUTO LAUNCH")
    print("=" * 80)
    print()
    print("Starting web interface...")
    print("Browser will open automatically in 2 seconds...")
    print()
    
    # Start browser opening in background thread
    url = "http://localhost:5000"
    browser_thread = threading.Thread(target=open_browser_delayed, args=(url, 2))
    browser_thread.daemon = True
    browser_thread.start()
    
    # Import and run the web interface
    try:
        from omega_control_panel_web import OmegaControlPanelWeb
        
        web_interface = OmegaControlPanelWeb(host='127.0.0.1', port=5000, debug=False)
        web_interface.run()
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Failed to start web interface: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
