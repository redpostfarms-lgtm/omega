#!/usr/bin/env python3
"""
VPN Browser Integration
=======================
Automatic VPN activation when browsers start
"""

import os
import sys
import time
import subprocess
import platform
import psutil
from pathlib import Path
from omega_vpn_system import get_vpn_manager, VPNProvider

class BrowserMonitor:
    """Monitor browser processes and activate VPN"""
    
    def __init__(self):
        self.vpn_manager = get_vpn_manager()
        self.browser_processes = [
            "chrome.exe", "firefox.exe", "msedge.exe",  # Windows
            "google-chrome", "firefox", "microsoft-edge",  # Linux
            "Google Chrome", "Firefox", "Microsoft Edge"  # macOS
        ]
        self.monitoring = False
        self.check_interval = 5  # Check every 5 seconds
    
    def is_browser_running(self) -> bool:
        """Check if any browser is running"""
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    proc_name = proc.info['name'].lower()
                    for browser in self.browser_processes:
                        if browser.lower() in proc_name:
                            return True
                except:
                    pass
        except:
            pass
        return False
    
    def wait_for_browser_start(self) -> bool:
        """Wait for browser to start"""
        print("Monitoring for browser startup...")
        print("(Press Ctrl+C to stop)")
        
        browser_was_running = self.is_browser_running()
        
        while True:
            time.sleep(self.check_interval)
            
            browser_is_running = self.is_browser_running()
            
            # Browser just started
            if browser_is_running and not browser_was_running:
                print("✅ Browser detected!")
                return True
            
            browser_was_running = browser_is_running
    
    def ensure_vpn_active(self) -> bool:
        """Ensure VPN is active when browser starts"""
        status = self.vpn_manager.get_status()
        
        if not status['connected']:
            print("⚠️ VPN is not connected")
            print("Connecting VPN...")
            
            # Try to connect with saved provider
            if self.vpn_manager.active_provider:
                provider = self.vpn_manager.active_provider
            else:
                # Default to Cloudflare WARP (easiest)
                provider = VPNProvider.CLOUDFLARE_WARP
            
            success, message = self.vpn_manager.connect(provider)
            
            if success:
                print(f"✅ VPN connected: {message}")
                return True
            else:
                print(f"❌ VPN connection failed: {message}")
                print("Please connect VPN manually using: python SETUP_VPN.py")
                return False
        else:
            print(f"✅ VPN already connected ({status['provider']})")
            return True
    
    def monitor_and_activate(self):
        """Monitor for browser startup and activate VPN"""
        self.monitoring = True
        
        try:
            while self.monitoring:
                if self.is_browser_running():
                    print("\n" + "=" * 80)
                    print("BROWSER DETECTED - CHECKING VPN")
                    print("=" * 80)
                    
                    if self.ensure_vpn_active():
                        print("✅ VPN is active - Browser can use VPN")
                    else:
                        print("❌ VPN is not active - Browser may not be protected")
                    
                    print("=" * 80)
                    print("\nMonitoring for browser restart...")
                    print("(Press Ctrl+C to stop)")
                    
                    # Wait for browser to close
                    while self.is_browser_running():
                        time.sleep(self.check_interval)
                    
                    print("Browser closed. Waiting for next browser start...")
                else:
                    time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            print("\n\nStopping browser monitor...")
            self.monitoring = False

def create_startup_script():
    """Create startup script for automatic VPN activation"""
    script_content = """@echo off
REM VPN Browser Integration - Auto-start
python "{}" --monitor
""".format(Path(__file__).absolute())
    
    if platform.system() == "Windows":
        startup_dir = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        startup_dir.mkdir(parents=True, exist_ok=True)
        script_path = startup_dir / "OmegaVPN_Monitor.bat"
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"✅ Startup script created: {script_path}")
        return True
    
    return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="VPN Browser Integration")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring for browser")
    parser.add_argument("--setup-startup", action="store_true", help="Setup startup script")
    args = parser.parse_args()
    
    if args.setup_startup:
        print("Setting up startup script...")
        create_startup_script()
        return
    
    monitor = BrowserMonitor()
    
    if args.monitor:
        monitor.monitor_and_activate()
    else:
        print("=" * 80)
        print("VPN BROWSER INTEGRATION")
        print("=" * 80)
        print()
        print("Options:")
        print("1. Monitor for browser startup (activate VPN automatically)")
        print("2. Check VPN status now")
        print("3. Setup startup script (auto-start on boot)")
        print()
        
        choice = input("Enter option (1-3): ").strip()
        
        if choice == "1":
            if monitor.ensure_vpn_active():
                print("\nVPN is active. Starting browser monitor...")
                monitor.monitor_and_activate()
            else:
                print("\nPlease connect VPN first using: python SETUP_VPN.py")
        
        elif choice == "2":
            status = monitor.vpn_manager.get_status()
            print("\nVPN Status:")
            print(f"  Connected: {status['connected']}")
            print(f"  Provider: {status['provider'] or 'None'}")
            print(f"  Status: {status['status']}")
        
        elif choice == "3":
            create_startup_script()

if __name__ == "__main__":
    main()
