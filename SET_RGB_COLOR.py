#!/usr/bin/env python3
"""
Set RGB Color - Quick Command
=============================
Quick script to set RGB color (gold for Omega)
"""

import sys
from omega_comprehensive_hardware import get_hardware_controller

def main():
    if len(sys.argv) > 1:
        # Custom color specified
        color_input = sys.argv[1]
        
        hw = get_hardware_controller()
        
        # Try hex code
        if color_input.startswith("#"):
            success, message = hw.set_rgb_color(hex_color=color_input)
        # Try RGB values (R,G,B)
        elif "," in color_input:
            r, g, b = map(int, color_input.split(","))
            success, message = hw.set_rgb_color(r=r, g=g, b=b)
        # Try color name
        else:
            success, message = hw.set_rgb_color(color_name=color_input)
        
        print(message)
    else:
        # Default: Set to gold (Omega color)
        hw = get_hardware_controller()
        success, message = hw.set_rgb_color(r=255, g=215, b=0)  # Gold
        print("Setting RGB to gold (Omega color)...")
        print(message)

if __name__ == "__main__":
    main()
