#!/usr/bin/env python3
"""
Create Omega Boot Logo - ASUS B550-Plus
========================================
Creates black and gold Omega symbol boot logo
"""

from omega_boot_logo import BootLogoManager

def main():
    print("=" * 80)
    print("CREATE OMEGA BOOT LOGO")
    print("=" * 80)
    print()
    
    logo_manager = BootLogoManager()
    
    print("Creating black and gold Omega symbol logo...")
    print("-" * 80)
    print()
    
    # Create logo
    logo_path = logo_manager.create_omega_logo()
    
    if logo_path:
        print(f"✅ Logo created: {logo_path}")
        print()
        print("Logo Specifications:")
        print(f"  Format: {logo_manager.logo_format}")
        print(f"  Size: {logo_manager.logo_size[0]}x{logo_manager.logo_size[1]} pixels")
        print(f"  Colors: {logo_manager.logo_colors}")
        print()
        print("Next Steps:")
        print("  1. Install ASUS AI Suite (includes MyLogo utility)")
        print("  2. Launch AI Suite and select 'MyLogo'")
        print("  3. Select the logo file:", logo_path)
        print("  4. Follow instructions to flash BIOS with new logo")
        print("  5. System will restart with Omega logo")
        print()
        print("⚠️  Note: BIOS flashing carries risks. Backup BIOS first!")
    else:
        print("❌ Failed to create logo")
        print("   Install Pillow: pip install Pillow")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
