#!/usr/bin/env python3
"""
Test Security System
====================
Quick test of network security system
"""

from omega_network_security import get_security_manager, SecurityLevel

def main():
    print("=" * 80)
    print("OMEGA NETWORK SECURITY SYSTEM - TEST")
    print("=" * 80)
    print()
    
    try:
        security = get_security_manager()
        print("✅ Security Manager Loaded")
        print()
        
        # Get security status
        print("Security Status:")
        status = security.get_security_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
        print()
        
        # Test VPN manager
        print("VPN Status:")
        vpn_status = security.vpn.get_vpn_status()
        print(f"  Available Protocols: {vpn_status['available_protocols']}")
        print(f"  Connected: {vpn_status['connected']}")
        print()
        
        # Test firewall
        print("Firewall Status:")
        print(f"  Available: {security.firewall.available}")
        if security.firewall.available:
            print(f"  Backend: {getattr(security.firewall, 'backend', 'Windows Firewall')}")
        print()
        
        # Test air-gap
        print("Air-Gap Status:")
        print(f"  Active: {security.air_gap.is_air_gapped()}")
        print()
        
        # Security levels
        print("Security Levels Available:")
        for level in SecurityLevel:
            print(f"  - {level.value}")
        print()
        
        print("=" * 80)
        print("TEST COMPLETE - System is operational")
        print("=" * 80)
        print()
        print("Note: Actual operations (VPN connect, firewall enable, air-gap)")
        print("require administrator/root permissions and should be tested carefully.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
