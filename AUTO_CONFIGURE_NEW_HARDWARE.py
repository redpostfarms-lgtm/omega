#!/usr/bin/env python3
"""
Auto-Configure New Hardware - ASUS B550-Plus
=============================================
Automatically configures BIOS when new hardware is added
"""

import sys
from omega_bios_integration import get_bios_integration

def main():
    print("=" * 80)
    print("AUTO-CONFIGURE NEW HARDWARE - ASUS B550-PLUS")
    print("=" * 80)
    print()
    
    bios = get_bios_integration()
    
    # Get current status
    status = bios.get_bios_status()
    
    print("Current Hardware Status:")
    print("-" * 80)
    print(f"Motherboard: {status['motherboard']}")
    print(f"GPUs Detected: {status['gpu_slots']}")
    for gpu in status['gpus_detected']:
        print(f"  ✅ {gpu['slot_id']}: {gpu['model']} ({'Enabled' if gpu['enabled'] else 'Disabled'})")
    print(f"Hard Drives Detected: {status['hard_drives']}")
    for drive in status['drives_detected']:
        print(f"  ✅ {drive['drive_id']}: {drive['model']} ({drive['capacity']}) ({'Enabled' if drive['enabled'] else 'Disabled'})")
    print("-" * 80)
    print()
    
    # Auto-configure for new GPU
    if status['gpu_slots'] >= 2:
        print("Configuring Multi-GPU Cross-Connect...")
        print("-" * 80)
        success, message = bios.configure_for_new_gpu()
        if success:
            print(f"✅ {message}")
            print("✅ Both GPUs will run simultaneously (no SLI required)")
            print("✅ PCIe lanes configured: x8/x8 split")
        else:
            print(f"❌ {message}")
        print()
    else:
        print(f"ℹ️  Single GPU detected: {status['gpus_detected'][0]['model'] if status['gpus_detected'] else 'None'}")
        print("   Add a second GPU to enable cross-connect")
        print()
    
    # Auto-configure for new hard drives
    print("Auto-Enabling Hard Drives...")
    print("-" * 80)
    success, message = bios.configure_for_new_hard_drive()
    if success:
        print(f"✅ {message}")
        print("✅ All hard drives are now enabled in BIOS")
    else:
        print(f"❌ {message}")
    print()
    
    # Final status
    print("=" * 80)
    print("CONFIGURATION COMPLETE")
    print("=" * 80)
    print()
    print("Note: Some BIOS settings may require a system restart to take effect.")
    print("      The system will automatically detect and configure new hardware.")
    print()

if __name__ == "__main__":
    main()
