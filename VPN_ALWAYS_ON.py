#!/usr/bin/env python3
"""
VPN Always On - Persistent VPN Connection
==========================================
Ensures VPN stays connected at all times
"""

import sys
import time
from pathlib import Path
from omega_vpn_system import get_vpn_manager, VPNProvider

def main():
    print("=" * 80)
    print("OMEGA VPN - ALWAYS ON MODE")
    print("=" * 80)
    print()
    print("VPN will stay connected at all times with automatic reconnection.")
    print()
    
    vpn = get_vpn_manager()
    
    # Ensure always_on is enabled
    vpn.always_on = True
    vpn.auto_reconnect = True
    vpn.save_config()
    
    # Check if already connected
    status = vpn.get_status()
    
    if status['connected']:
        print(f"✅ VPN is already connected ({status['provider']})")
        print("✅ Monitoring enabled - will auto-reconnect if disconnected")
        
        # Start monitoring if not already running
        if not status['monitoring']:
            vpn.start_monitoring()
    else:
        print("⚠️ VPN is not connected")
        print()
        print("Available providers:")
        print("1. Cloudflare WARP (Recommended - free, easy)")
        print("2. OpenVPN (Requires config file)")
        print("3. WireGuard (Requires config file)")
        print()
        
        choice = input("Select provider (1-3, or press Enter to skip): ").strip()
        
        provider_map = {
            "1": VPNProvider.CLOUDFLARE_WARP,
            "2": VPNProvider.OPENVPN,
            "3": VPNProvider.WIREGUARD
        }
        
        if choice in provider_map:
            provider = provider_map[choice]
            
            config_path = None
            if provider in [VPNProvider.OPENVPN, VPNProvider.WIREGUARD]:
                config_path = input(f"Enter config file path (or press Enter for default): ").strip()
                if not config_path:
                    config_path = None
            
            print(f"\nConnecting to {provider.value}...")
            success, message = vpn.connect(provider, config_path)
            
            if success:
                print(f"✅ {message}")
                print("✅ VPN is now always-on with auto-reconnect")
                print("✅ Monitoring started - VPN will stay connected")
            else:
                print(f"❌ Connection failed: {message}")
                print("\nPlease check:")
                if provider == VPNProvider.CLOUDFLARE_WARP:
                    print("- Install Cloudflare WARP client")
                    print("- Windows: Download from cloudflare.com/warp")
                elif provider == VPNProvider.OPENVPN:
                    print("- Install OpenVPN")
                    print("- Ensure config file exists")
                elif provider == VPNProvider.WIREGUARD:
                    print("- Install WireGuard")
                    print("- Ensure config file exists")
        else:
            print("No provider selected. Run this script again to connect.")
            return
    
    print()
    print("=" * 80)
    print("VPN ALWAYS-ON MODE ACTIVE")
    print("=" * 80)
    print()
    print("Features:")
    print("✅ VPN stays connected at all times")
    print("✅ Automatic reconnection if disconnected")
    print("✅ Background monitoring (checks every 30 seconds)")
    print("✅ Connection health checking")
    print("✅ Browser integration enabled")
    print()
    print("The VPN will now:")
    print("- Stay connected indefinitely")
    print("- Auto-reconnect if connection drops")
    print("- Maintain connection across browser restarts")
    print("- Keep monitoring in background")
    print()
    print("To stop monitoring, close this script (Ctrl+C)")
    print("Note: VPN will remain connected even after closing")
    print()
    
    try:
        # Keep script running to maintain monitoring
        while True:
            time.sleep(60)
            status = vpn.get_status()
            if not status['connected'] and vpn.always_on:
                print("[Monitor] VPN disconnected - reconnecting...")
                vpn._reconnect()
    except KeyboardInterrupt:
        print("\n\nStopping monitor (VPN will remain connected)...")
        vpn.stop_monitoring()
        print("Monitor stopped. VPN connection remains active.")

if __name__ == "__main__":
    main()
