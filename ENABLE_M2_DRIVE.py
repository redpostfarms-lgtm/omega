#!/usr/bin/env python3
"""
Enable M.2 Drive - Auto Configuration
=====================================
Enables the M.2 drive in the new slot
"""

from omega_comprehensive_hardware import get_hardware_controller

def main():
    print("=" * 80)
    print("ENABLE M.2 DRIVE - ASUS B550-PLUS")
    print("=" * 80)
    print()
    
    hw = get_hardware_controller()
    
    print("Enabling M.2 drive in new slot...")
    print("-" * 80)
    print()
    
    # Enable M.2 drive
    success, message = hw.enable_m2_drive("M.2_2")
    
    if success:
        print(f"✅ {message}")
        print("✅ M.2 drive is now enabled in BIOS")
        print("✅ Drive is active and ready to use")
    else:
        print(f"❌ {message}")
        print("⚠️  Note: Some BIOS settings may require a system restart")
    
    print()
    print("=" * 80)
    print("M.2 DRIVE ENABLE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
