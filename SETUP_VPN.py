#!/usr/bin/env python3
"""
Setup VPN System
================
Interactive VPN setup and testing
"""

import sys
from pathlib import Path
from omega_vpn_system import get_vpn_manager, VPNProvider, VPNStatus

def print_header():
    """Print header"""
    print("=" * 80)
    print("OMEGA VPN SYSTEM - SETUP AND TESTING")
    print("=" * 80)
    print()

def print_status(manager):
    """Print VPN status"""
    status = manager.get_status()
    print("=" * 80)
    print("VPN STATUS")
    print("=" * 80)
    print(f"Connected: {'✅ Yes' if status['connected'] else '❌ No'}")
    print(f"Provider: {status['provider'] or 'None'}")
    print(f"Status: {status['status']}")
    if status['connection_time']:
        print(f"Connected Since: {status['connection_time']}")
    if status['ip_address']:
        print(f"IP Address: {status['ip_address']}")
    print("=" * 80)
    print()

def main():
    print_header()
    
    manager = get_vpn_manager()
    
    print("Available VPN Providers:")
    print("-" * 80)
    print("1. OpenVPN (Open-source, configurable)")
    print("2. WireGuard (Modern, fast)")
    print("3. Cloudflare WARP (Free tier, easy)")
    print()
    
    while True:
        print("=" * 80)
        print("OPTIONS")
        print("=" * 80)
        print("1. Connect to VPN")
        print("2. Disconnect from VPN")
        print("3. Check VPN Status")
        print("4. Test Connection")
        print("5. Setup Browser Integration")
        print("6. Exit")
        print()
        
        try:
            choice = input("Enter option (1-6): ").strip()
            
            if choice == "1":
                print("\n" + "=" * 80)
                print("CONNECT TO VPN")
                print("=" * 80)
                print()
                print("Select provider:")
                print("1. OpenVPN")
                print("2. WireGuard")
                print("3. Cloudflare WARP")
                print()
                
                provider_choice = input("Enter provider (1-3): ").strip()
                
                provider_map = {
                    "1": VPNProvider.OPENVPN,
                    "2": VPNProvider.WIREGUARD,
                    "3": VPNProvider.CLOUDFLARE_WARP
                }
                
                if provider_choice in provider_map:
                    provider = provider_map[provider_choice]
                    
                    config_path = None
                    if provider in [VPNProvider.OPENVPN, VPNProvider.WIREGUARD]:
                        config_path = input(f"Enter config file path (or press Enter for default): ").strip()
                        if not config_path:
                            config_path = None
                    
                    print(f"\nConnecting to {provider.value}...")
                    success, message = manager.connect(provider, config_path)
                    
                    if success:
                        print(f"✅ {message}")
                        print_status(manager)
                    else:
                        print(f"❌ Connection failed: {message}")
                        print()
                        print("Troubleshooting:")
                        if provider == VPNProvider.OPENVPN:
                            print("- Ensure OpenVPN is installed")
                            print("- Check config file path and format")
                            print("- Run as administrator if needed")
                        elif provider == VPNProvider.WIREGUARD:
                            print("- Ensure WireGuard is installed")
                            print("- Check config file path and format")
                            print("- Run as administrator/sudo if needed")
                        elif provider == VPNProvider.CLOUDFLARE_WARP:
                            print("- Install Cloudflare WARP client")
                            print("- Windows: Download from cloudflare.com/warp")
                            print("- Linux: Install warp-cli package")
                else:
                    print("Invalid provider choice")
            
            elif choice == "2":
                print("\n⚠️ Warning: VPN is set to always stay on.")
                print("Disconnecting is not recommended.")
                confirm = input("Are you sure you want to disable always-on mode? (yes/no): ").strip().lower()
                if confirm == "yes":
                    manager.always_on = False
                    manager.save_config()
                    print("\nDisconnecting VPN...")
                    success = manager.disconnect()
                    if success:
                        print("✅ Disconnected successfully")
                    else:
                        print("❌ Disconnect failed or already disconnected")
                else:
                    print("Disconnect cancelled - VPN remains on")
                print_status(manager)
            
            elif choice == "3":
                print()
                print_status(manager)
            
            elif choice == "4":
                print("\nTesting VPN connection...")
                success, test_result = manager.test_connection()
                if success:
                    print("✅ Connection test successful")
                    print(f"   IP Address: {test_result.get('ip', 'Unknown')}")
                    print(f"   Status: {test_result.get('status', 'Unknown')}")
                else:
                    print("❌ Connection test failed")
                    print("   VPN may not be connected or connection is slow")
                print()
            
            elif choice == "5":
                print("\n" + "=" * 80)
                print("BROWSER INTEGRATION SETUP")
                print("=" * 80)
                print()
                print("Browser integration will be configured to:")
                print("1. Check VPN status when browser starts")
                print("2. Connect VPN automatically if disconnected")
                print("3. Route browser traffic through VPN")
                print()
                
                enabled = manager.browser_integrator.enable_vpn_on_browser_start()
                if enabled:
                    print("✅ Browser integration enabled")
                    print()
                    print("Note: Browser integration is active.")
                    print("VPN will be checked when browsers are launched.")
                else:
                    print("⚠️ Browser integration setup completed")
                print()
            
            elif choice == "6":
                print("\nExiting VPN setup.")
                break
            
            else:
                print("Invalid option. Please enter 1-6.\n")
        
        except KeyboardInterrupt:
            print("\n\nExiting VPN setup.")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
