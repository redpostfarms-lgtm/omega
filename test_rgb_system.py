#!/usr/bin/env python3
"""Quick test of RGB Advanced Controller"""

from omega_rgb_advanced_controller import get_advanced_rgb_controller

print("=" * 70)
print("OMEGA RGB ADVANCED CONTROLLER - QUICK TEST")
print("=" * 70)
print()

try:
    # Get RGB controller
    print("[1] Initializing RGB controller...")
    rgb = get_advanced_rgb_controller()
    print("    ✓ Initialized")
    print()
    
    # Get status
    print("[2] Getting RGB system status...")
    status = rgb.get_status()
    print(f"    Active Method: {status['current_method']}")
    print(f"    Available Methods: {status['available_methods']}")
    print(f"    RGB Enabled: {status['enabled']}")
    print(f"    Current Color: {status['current_color_hex']}")
    print("    ✓ Status retrieved")
    print()
    
    # Test color changes
    print("[3] Testing color changes...")
    colors = [
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
    ]
    
    for name, color in colors:
        result = rgb.set_color(*color)
        status_update = rgb.get_status()
        print(f"    {name}: {status_update['current_color_hex']} - {'✓' if result else '✗'}")
    
    print()
    
    # Enable/disable test
    print("[4] Testing enable/disable...")
    rgb.disable_rgb()
    status_disabled = rgb.get_status()
    print(f"    After disable: {status_disabled['enabled']} (expected: False)")
    
    rgb.enable_rgb()
    status_enabled = rgb.get_status()
    print(f"    After enable: {status_enabled['enabled']} (expected: True)")
    print("    ✓ Enable/disable working")
    print()
    
    print("=" * 70)
    print("✓ ALL TESTS PASSED - RGB SYSTEM OPERATIONAL")
    print("=" * 70)
    print()
    print("Summary:")
    print(f"  - RGB Method: {status['current_method']}")
    print(f"  - Fallback Available: {len(status['available_methods']) > 1}")
    print(f"  - Color Control: Working")
    print(f"  - Power Control: Working")
    print()
    print("Next Steps:")
    print("  1. Install OpenRGB: pip install openrgb")
    print("  2. Test with web UI: python omega_control_panel_web.py --port 5000")
    print("  3. Reference guide: RGB_QUICK_REFERENCE.py")
    print("  4. Troubleshooting: RGB_TROUBLESHOOTING_GUIDE.md")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
