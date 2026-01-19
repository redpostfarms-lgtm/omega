"""
OmegaVPN Setup - Complete VPN System
======================================
Privacy-focused VPN with all security features
"""

import sys
from pathlib import Path
from omega_vpn_enhanced import get_optimized_vpn, VPNProvider
from omega_vpn_system import ComprehensiveVPNManager

def print_header():
    """Print header"""
    print("=" * 80)
    print("OMEGAVPN - ULTIMATE PRIVACY PROTECTION")
    print("=" * 80)
    print()
    print("OmegaVPN: Complete Privacy, Always On")
    print()

def print_features():
    """Print VPN features"""
    print("Privacy Features:")
    print("-" * 80)
    print("✅ No Logging - Zero logs, complete privacy")
    print("✅ DNS Leak Protection - Secure DNS routing")
    print("✅ Kill Switch - Blocks all traffic if VPN disconnects")
    print("✅ DNS over HTTPS (DoH) - Encrypted DNS queries")
    print("✅ IPv6 Leak Protection - Prevents IPv6 leaks")
    print("✅ WebRTC Leak Protection - Browser privacy")
    print("✅ Always-On Mode - VPN stays connected permanently")
    print("✅ Auto-Reconnect - Automatic reconnection")
    print("✅ Browser Integration - Automatic activation")
    print("-" * 80)
    print()

def main():
    print_header()
    print_features()
    
    omegavpn = get_optimized_vpn("OmegaVPN")
    
    print("OmegaVPN Status:")
    print("-" * 80)
    status = omegavpn.get_status()
    print(f"VPN Name: {status.get('vpn_name', 'OmegaVPN')}")
    print(f"Connected: {'✅ Yes' if status.get('connected') else '❌ No'}")
    print(f"Provider: {status.get('provider') or 'None'}")
    print(f"Status: {status.get('status')}")
    
    privacy = status.get('privacy_features', {})
    print()
    print("Privacy Features Status:")
    print(f"  DNS Leak Protection: {'✅' if privacy.get('dns_leak_protection') else '❌'}")
    print(f"  DNS Leak Detected: {'❌ Yes' if privacy.get('dns_leak_detected') else '✅ No'}")
    print(f"  Kill Switch: {'✅ Enabled' if privacy.get('kill_switch') else '❌ Disabled'}")
    print(f"  IPv6 Protection: {'✅' if privacy.get('ipv6_leak_protection') else '❌'}")
    print(f"  WebRTC Protection: {'✅' if privacy.get('webrtc_leak_protection') else '❌'}")
    print(f"  No Logging: {'✅' if privacy.get('no_logging') else '❌'}")
    print("-" * 80)
    print()
    
    print("Options:")
    print("1. Connect OmegaVPN")
    print("2. Check Status")
    print("3. Optimize Connection")
    print("4. Test DNS Leak")
    print("5. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter option (1-5): ").strip()
            
            if choice == "1":
                print("\n" + "=" * 80)
                print("CONNECT OMEGAVPN")
                print("=" * 80)
                print()
                print("Available providers:")
                print("1. Cloudflare WARP (Recommended - free, fast, secure)")
                print("2. OpenVPN (Requires config file)")
                print("3. WireGuard (Requires config file)")
                print()
                
                provider_choice = input("Select provider (1-3): ").strip()
                provider_map = {
                    "1": VPNProvider.CLOUDFLARE_WARP,
                    "2": VPNProvider.OPENVPN,
                    "3": VPNProvider.WIREGUARD
                }
                
                if provider_choice in provider_map:
                    provider = provider_map[provider_choice]
                    config_path = None
                    
                    if provider in [VPNProvider.OPENVPN, VPNProvider.WIREGUARD]:
                        config_path = input("Enter config file path (or Enter for default): ").strip()
                        if not config_path:
                            config_path = None
                    
                    print(f"\nConnecting OmegaVPN ({provider.value})...")
                    success, message = omegavpn.connect(provider, config_path)
                    
                    if success:
                        print(f"✅ {message}")
                        print("✅ OmegaVPN connected with all privacy protections enabled")
                        print("✅ VPN will stay on permanently (always-on mode)")
                    else:
                        print(f"❌ Connection failed: {message}")
                else:
                    print("Invalid provider choice")
            
            elif choice == "2":
                print()
                status = omegavpn.get_status()
                print("=" * 80)
                print("OMEGAVPN STATUS")
                print("=" * 80)
                print(f"VPN Name: {status.get('vpn_name')}")
                print(f"Connected: {'✅ Yes' if status.get('connected') else '❌ No'}")
                print(f"Provider: {status.get('provider')}")
                print(f"Status: {status.get('status')}")
                print(f"Always-On: {'✅ Yes' if status.get('always_on') else '❌ No'}")
                print()
                privacy = status.get('privacy_features', {})
                print("Privacy Features:")
                for key, value in privacy.items():
                    print(f"  {key.replace('_', ' ').title()}: {'✅' if value else '❌'}")
                print()
            
            elif choice == "3":
                print("\nOptimizing OmegaVPN connection...")
                result = omegavpn.optimize_connection()
                print("✅ Optimization complete")
                if result.get('optimizations_applied'):
                    print("Optimizations applied:")
                    for opt in result['optimizations_applied']:
                        print(f"  - {opt}")
                print()
            
            elif choice == "4":
                print("\nTesting DNS leak protection...")
                no_leak, result = omegavpn.dns_leak_protection.test_dns_leak()
                if no_leak:
                    print("✅ No DNS leak detected - Protection working")
                else:
                    print("❌ DNS leak detected!")
                    print(f"Details: {result}")
                print()
            
            elif choice == "5":
                print("\nExiting OmegaVPN setup.")
                print("Remember: OmegaVPN stays connected in always-on mode!")
                break
            
            else:
                print("Invalid option. Please enter 1-5.\n")
        
        except KeyboardInterrupt:
            print("\n\nExiting OmegaVPN setup.")
            print("OmegaVPN remains connected in always-on mode!")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
