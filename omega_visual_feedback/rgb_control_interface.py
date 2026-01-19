#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RGB Control Interface for LED Matrix Panel
Real-time color monitoring and control during speech synthesis
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

from led_matrix_controller import LEDMatrixController, RGBColor


class RGBControlInterface:
    """
    Interactive RGB control interface for LED Matrix
    Provides real-time color adjustment and monitoring
    """

    def __init__(self, controller: Optional[LEDMatrixController] = None):
        """
        Initialize RGB control interface

        Args:
            controller: LED Matrix controller (creates new if None)
        """
        self.controller = controller or LEDMatrixController()

        # Color presets for different speech states
        self.presets = {
            "idle": RGBColor(50, 50, 255),      # Dim blue
            "listening": RGBColor(0, 255, 0),    # Green
            "speaking": RGBColor(255, 0, 0),     # Red (default)
            "processing": RGBColor(255, 165, 0), # Orange
            "error": RGBColor(255, 0, 255),      # Magenta
            "success": RGBColor(0, 255, 128),    # Cyan-green
        }

        self.current_state = "idle"

    def set_state_color(self, state: str):
        """
        Set color based on speech state

        Args:
            state: Speech state (idle, listening, speaking, etc.)
        """
        if state in self.presets:
            self.controller.set_color(self.presets[state])
            self.current_state = state
            print(f"[RGB Control] State: {state} → {self.presets[state].to_hex()}")
        else:
            print(f"[RGB Control] ⚠ Unknown state: {state}")

    def set_custom_color(self, r: int, g: int, b: int):
        """
        Set custom RGB color

        Args:
            r: Red (0-255)
            g: Green (0-255)
            b: Blue (0-255)
        """
        color = RGBColor(r, g, b)
        self.controller.set_color(color)
        print(f"[RGB Control] Custom color: {color.to_hex()}")

    def adjust_brightness(self, delta: int):
        """
        Adjust brightness by delta

        Args:
            delta: Brightness change (-100 to 100)
        """
        new_brightness = self.controller.brightness + delta
        self.controller.set_brightness(new_brightness)

    def create_color_gradient(self, start_color: RGBColor, end_color: RGBColor, steps: int) -> list:
        """
        Create color gradient between two colors

        Args:
            start_color: Starting RGB color
            end_color: Ending RGB color
            steps: Number of gradient steps

        Returns:
            List of RGBColor objects
        """
        gradient = []

        for i in range(steps):
            t = i / (steps - 1) if steps > 1 else 0

            r = int(start_color.r + (end_color.r - start_color.r) * t)
            g = int(start_color.g + (end_color.g - start_color.g) * t)
            b = int(start_color.b + (end_color.b - start_color.b) * t)

            gradient.append(RGBColor(r, g, b))

        return gradient

    async def pulse_color(self, color: RGBColor, duration: float = 2.0, steps: int = 20):
        """
        Pulse effect with color fade

        Args:
            color: Target RGB color
            duration: Pulse duration in seconds
            steps: Number of fade steps
        """
        # Create gradient from black to color and back
        black = RGBColor(0, 0, 0)
        fade_in = self.create_color_gradient(black, color, steps // 2)
        fade_out = self.create_color_gradient(color, black, steps // 2)

        gradient = fade_in + fade_out
        step_duration = duration / len(gradient)

        for step_color in gradient:
            self.controller.set_color(step_color)
            await asyncio.sleep(step_duration)

    async def breathing_effect(self, color: RGBColor, cycles: int = 3):
        """
        Breathing light effect

        Args:
            color: RGB color
            cycles: Number of breathing cycles
        """
        for _ in range(cycles):
            await self.pulse_color(color, duration=1.5)

    def get_color_info(self) -> Dict:
        """Get current color information"""
        return {
            "current_state": self.current_state,
            "rgb": self.controller.current_color.to_tuple(),
            "hex": self.controller.current_color.to_hex(),
            "brightness": self.controller.brightness,
            "presets": {
                state: color.to_hex()
                for state, color in self.presets.items()
            }
        }

    async def interactive_control(self):
        """Interactive RGB control menu"""
        print("\n" + "=" * 70)
        print("  RGB CONTROL INTERFACE - LED MATRIX")
        print("=" * 70 + "\n")

        while True:
            print("\nOptions:")
            print("  1. Set state color")
            print("  2. Set custom RGB color")
            print("  3. Adjust brightness")
            print("  4. Pulse effect")
            print("  5. Breathing effect")
            print("  6. View color info")
            print("  7. Test visualization")
            print("  8. Exit")

            choice = input("\nChoice (1-8): ").strip()

            if choice == "1":
                print("\nAvailable states:")
                for i, state in enumerate(self.presets.keys(), 1):
                    print(f"  {i}. {state} - {self.presets[state].to_hex()}")

                state_choice = input("Select state (name or number): ").strip()

                # Check if input is number
                try:
                    state_idx = int(state_choice) - 1
                    states = list(self.presets.keys())
                    if 0 <= state_idx < len(states):
                        self.set_state_color(states[state_idx])
                except ValueError:
                    # Input is state name
                    self.set_state_color(state_choice)

            elif choice == "2":
                try:
                    r = int(input("Red (0-255): "))
                    g = int(input("Green (0-255): "))
                    b = int(input("Blue (0-255): "))
                    self.set_custom_color(r, g, b)
                except ValueError:
                    print("✗ Invalid RGB values")

            elif choice == "3":
                try:
                    delta = int(input("Brightness change (-100 to 100): "))
                    self.adjust_brightness(delta)
                    print(f"✓ Brightness: {self.controller.brightness}%")
                except ValueError:
                    print("✗ Invalid brightness value")

            elif choice == "4":
                color_name = input("Pulse color (red/green/blue/etc.): ").strip()
                if color_name in LEDMatrixController.COLORS:
                    color = LEDMatrixController.COLORS[color_name]
                    await self.pulse_color(color)
                else:
                    print(f"✗ Unknown color: {color_name}")

            elif choice == "5":
                color_name = input("Breathing color (red/green/blue/etc.): ").strip()
                if color_name in LEDMatrixController.COLORS:
                    color = LEDMatrixController.COLORS[color_name]
                    await self.breathing_effect(color)
                else:
                    print(f"✗ Unknown color: {color_name}")

            elif choice == "6":
                info = self.get_color_info()
                print("\nCurrent Color Info:")
                print(f"  State: {info['current_state']}")
                print(f"  RGB: {info['rgb']}")
                print(f"  Hex: {info['hex']}")
                print(f"  Brightness: {info['brightness']}%")
                print("\nAvailable Presets:")
                for state, hex_color in info['presets'].items():
                    print(f"  {state}: {hex_color}")

            elif choice == "7":
                print("\nTest Visualization:")
                print("  Creating sample audio visualization...")

                # Demo spectrum
                import random
                for _ in range(20):
                    frequencies = [random.random() for _ in range(32)]
                    self.controller.visualize_spectrum(frequencies)
                    await asyncio.sleep(0.05)

                print("  ✓ Test complete")

            elif choice == "8":
                print("\nExiting RGB control...")
                break

            else:
                print("✗ Invalid choice")


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  RGB MONITORING & CONTROL SYSTEM")
    print("=" * 70 + "\n")

    # Initialize controller
    controller = LEDMatrixController()

    # Auto-connect
    print("Connecting to LED Matrix...")
    if controller.config.get("auto_connect", True):
        controller.connect()

    # Create RGB control interface
    rgb_control = RGBControlInterface(controller)

    # Set default color to RED
    print("\nSetting default color: RED")
    rgb_control.set_state_color("speaking")  # Red preset

    # Display status
    print("\nController Status:")
    status = controller.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    # Show color info
    print("\nColor Configuration:")
    info = rgb_control.get_color_info()
    print(f"  Current State: {info['current_state']}")
    print(f"  RGB: {info['rgb']}")
    print(f"  Hex: {info['hex']}")
    print(f"  Brightness: {info['brightness']}%")

    print("\n" + "=" * 70)
    print("  RGB CONTROL READY")
    print("=" * 70)

    # Interactive control
    choice = input("\nLaunch interactive control? (y/n): ").strip().lower()
    if choice == 'y':
        await rgb_control.interactive_control()


if __name__ == "__main__":
    asyncio.run(main())
