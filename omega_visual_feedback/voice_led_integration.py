#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AZZ Voice + LED Matrix Integration
Synchronizes visual feedback with speech synthesis
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

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "omega_voice_profiles"))

from led_matrix_controller import LEDMatrixController, RGBColor
from rgb_control_interface import RGBControlInterface


class VoiceLEDIntegration:
    """
    Integration between AZZ voice system and LED Matrix
    Provides synchronized visual feedback during speech
    """

    def __init__(self):
        """Initialize voice-LED integration"""
        self.led = LEDMatrixController()
        self.rgb_control = RGBControlInterface(self.led)

        # Auto-connect on init
        if self.led.config.get("auto_connect", True):
            self.led.connect()

        # Set default speaking color (RED)
        self.rgb_control.set_state_color("speaking")

        self.log("Voice-LED integration initialized")

    def log(self, message: str):
        """Log message"""
        print(f"[Voice-LED] {message}")

    async def synthesize_with_visualization(
        self,
        text: str,
        output_path: Path,
        voice_system: str = "azure"
    ):
        """
        Synthesize speech with synchronized LED visualization

        Args:
            text: Text to synthesize
            output_path: Output audio file path
            voice_system: Voice synthesis system (azure/coqui)
        """
        self.log(f"Synthesizing with visualization: {text}")

        # Import voice system
        try:
            from azz_voice_system import AZZVoiceSystem
            azz = AZZVoiceSystem()
        except ImportError:
            self.log("✗ AZZ Voice System not available")
            return False

        # Set LED to processing state (orange)
        self.rgb_control.set_state_color("processing")
        self.led.display_text("...")

        # Synthesize speech
        try:
            if voice_system == "azure":
                success = azz.synthesize_with_azure(text, output_path)
            elif voice_system == "coqui":
                success = azz.synthesize_with_coqui(text, output_path)
            else:
                self.log(f"✗ Unknown voice system: {voice_system}")
                return False

            if not success:
                # Set error state (magenta)
                self.rgb_control.set_state_color("error")
                self.led.display_text("ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Synthesis error: {e}")
            self.rgb_control.set_state_color("error")
            return False

        # Set speaking state (red) and visualize
        self.rgb_control.set_state_color("speaking")

        # Display text snippet
        display_text = text[:16]  # First 16 chars for 16x32 display
        self.led.display_text(display_text)

        # Sync visualization with audio
        if output_path.exists():
            await self.led.sync_with_speech(output_path)

        # Set success state (cyan-green)
        self.rgb_control.set_state_color("success")

        self.log("✓ Synthesis and visualization complete")
        return True

    async def speak_with_led(
        self,
        text: str,
        color: str = "red",
        show_text: bool = True
    ):
        """
        Quick speak function with LED feedback

        Args:
            text: Text to speak
            color: LED color during speech
            show_text: Display text on LED matrix
        """
        # Set color
        self.led.set_color_by_name(color)

        # Display text
        if show_text:
            display_text = text[:16]
            self.led.display_text(display_text)

        # Generate speech
        output_path = Path("temp_speech.wav")

        try:
            from azz_voice_system import AZZVoiceSystem
            azz = AZZVoiceSystem()

            success = azz.synthesize_with_azure(text, output_path)

            if success and output_path.exists():
                # Visualize
                await self.led.sync_with_speech(output_path)

                # Cleanup
                output_path.unlink()

        except Exception as e:
            self.log(f"✗ Error: {e}")

    async def demo_modes(self):
        """Demonstrate different visualization modes"""
        self.log("Running demo of all modes...")

        modes = {
            "idle": "System ready",
            "listening": "Listening for input",
            "processing": "Processing request",
            "speaking": "AZZ is speaking",
            "success": "Task complete",
            "error": "Error occurred"
        }

        for state, description in modes.items():
            print(f"\n[{state.upper()}] {description}")

            # Set state color
            self.rgb_control.set_state_color(state)

            # Display text
            self.led.display_text(state.upper())

            # Wait
            await asyncio.sleep(2)

            # Breathing effect for speaking state
            if state == "speaking":
                await self.rgb_control.breathing_effect(
                    self.rgb_control.presets[state],
                    cycles=2
                )

        self.log("✓ Demo complete")


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  AZZ VOICE + LED MATRIX INTEGRATION")
    print("=" * 70 + "\n")

    # Initialize integration
    integration = VoiceLEDIntegration()

    # Show status
    print("LED Matrix Status:")
    status = integration.led.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\nRGB Color Info:")
    color_info = integration.rgb_control.get_color_info()
    print(f"  Current State: {color_info['current_state']}")
    print(f"  Color: {color_info['hex']} RGB{color_info['rgb']}")
    print(f"  Brightness: {color_info['brightness']}%")

    print("\n" + "=" * 70)
    print("  INTEGRATION READY")
    print("=" * 70)

    # Menu
    print("\nOptions:")
    print("  1. Demo all visualization modes")
    print("  2. Test speech synthesis with LED")
    print("  3. Interactive RGB control")
    print("  4. Exit")

    choice = input("\nChoice (1-4): ").strip()

    if choice == "1":
        await integration.demo_modes()

    elif choice == "2":
        text = input("\nEnter text to synthesize: ").strip()
        if text:
            output = Path("test_speech_led.wav")
            await integration.synthesize_with_visualization(text, output)
        else:
            print("✗ No text entered")

    elif choice == "3":
        await integration.rgb_control.interactive_control()

    elif choice == "4":
        print("\nExiting...")

    # Cleanup
    integration.led.clear()
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
