#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Matrix Panel Setup
Quick setup and test for 16×32 RGB LED Matrix
"""

import asyncio
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Add path
sys.path.insert(0, str(Path(__file__).parent / "omega_visual_feedback"))


async def main():
    """Setup LED Matrix"""
    print("\n" + "=" * 70)
    print("  LED MATRIX PANEL SETUP")
    print("=" * 70 + "\n")

    print("Device: 16×32 RGB LED Matrix (173×70mm)")
    print("Power: 5V/2A USB")
    print("Control: APP (iPixel Color) + Serial\n")

    # Check dependencies
    print("[Step 1/4] Checking dependencies...")
    dependencies = {
        "pyserial": False,
        "librosa": False,
        "numpy": False
    }

    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            dependencies[dep] = True
            print(f"  ✓ {dep}")
        except ImportError:
            print(f"  ✗ {dep} (not installed)")

    missing = [dep for dep, installed in dependencies.items() if not installed]

    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        print(f"  pip install {' '.join(missing)}")
        print()

        install_now = input("Install missing dependencies now? (y/n): ").strip().lower()
        if install_now == 'y':
            import subprocess
            for dep in missing:
                print(f"\nInstalling {dep}...")
                subprocess.run([sys.executable, "-m", "pip", "install", dep])

    # Initialize controller
    print("\n[Step 2/4] Initializing LED Matrix controller...")

    try:
        from led_matrix_controller import LEDMatrixController
        led = LEDMatrixController()
        print("  ✓ Controller initialized")
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return

    # Connect
    print("\n[Step 3/4] Connecting to LED Matrix...")
    print("  Make sure:")
    print("    • LED Matrix is powered on (5V/2A USB)")
    print("    • USB cable is connected")
    print("    • iPixel Color app is closed (if using serial)")

    connect_now = input("\n  Ready to connect? (y/n): ").strip().lower()

    if connect_now == 'y':
        if led.connect():
            print(f"  ✓ Connected to {led.port}")
        else:
            print("  ⚠ Connection failed (will simulate commands)")
    else:
        print("  ⚠ Skipping connection (will simulate commands)")

    # Test RGB control
    print("\n[Step 4/4] Testing RGB control...")

    print("\n  Setting color to RED (default)...")
    led.set_color_by_name("red")

    print("  Setting brightness to 100%...")
    led.set_brightness(100)

    print("  Displaying 'OMEGA'...")
    led.display_text("OMEGA")

    # Test other colors
    print("\n  Testing color changes...")
    colors = ["green", "blue", "yellow", "cyan", "magenta"]

    for color in colors:
        print(f"    • {color.upper()}")
        led.set_color_by_name(color)
        await asyncio.sleep(0.5)

    # Return to red
    print("\n  Returning to RED...")
    led.set_color_by_name("red")

    # Status
    print("\n" + "=" * 70)
    print("  SETUP COMPLETE")
    print("=" * 70)

    print("\nLED Matrix Status:")
    status = led.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\nConfiguration saved to:")
    print(f"  {led.config_file}")

    print("\nNext Steps:")
    print("  1. Test RGB control:")
    print("     python omega_visual_feedback/rgb_control_interface.py")
    print()
    print("  2. Integrate with voice:")
    print("     python omega_visual_feedback/voice_led_integration.py")
    print()
    print("  3. Read documentation:")
    print("     omega_visual_feedback/LED_MATRIX_README.md")

    print("\n" + "=" * 70 + "\n")

    # Save config
    led.save_config()


if __name__ == "__main__":
    asyncio.run(main())
