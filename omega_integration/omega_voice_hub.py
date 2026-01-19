#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Voice Hub - Universal Voice Integration
Routes voice synthesis through all Omega systems with LED visualization
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "omega_voice_profiles"))
sys.path.insert(0, str(Path(__file__).parent.parent / "omega_visual_feedback"))


class OmegaVoiceHub:
    """
    Central hub for all Omega voice operations
    Integrates AZZ voice, LED Matrix, and all system components
    """

    def __init__(self):
        """Initialize Omega Voice Hub"""
        self.config_dir = Path(__file__).parent / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "omega_voice_hub.json"

        # Initialize components
        self.azz_voice = None
        self.led_matrix = None
        self.voice_led = None

        # Load configuration
        self.config = self.load_config()

        # Initialize if auto-start enabled
        if self.config.get("auto_initialize", True):
            self.initialize_components()

        self.log("Omega Voice Hub initialized")

    def log(self, message: str):
        """Log message"""
        print(f"[Omega Voice Hub] {message}")

    def load_config(self) -> Dict:
        """Load hub configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)

        # Default configuration
        return {
            "version": "1.0.0",
            "auto_initialize": True,
            "default_voice": "azz",
            "default_backend": "azure",
            "led_enabled": True,
            "led_default_color": "red",
            "components": {
                "azz_voice": {
                    "enabled": True,
                    "path": "omega_voice_profiles/azz_voice_system.py"
                },
                "led_matrix": {
                    "enabled": True,
                    "path": "omega_visual_feedback/led_matrix_controller.py"
                },
                "voice_led_integration": {
                    "enabled": True,
                    "path": "omega_visual_feedback/voice_led_integration.py"
                }
            },
            "routing": {
                "default": "azz",
                "omega": "azz",
                "azure": "azz",
                "system": "azz",
                "user": "azz"
            }
        }

    def save_config(self):
        """Save hub configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
        self.log(f"✓ Configuration saved: {self.config_file}")

    def initialize_components(self):
        """Initialize all voice components"""
        self.log("Initializing voice components...")

        # Initialize AZZ Voice
        if self.config["components"]["azz_voice"]["enabled"]:
            try:
                from azz_voice_system import AZZVoiceSystem
                self.azz_voice = AZZVoiceSystem()
                self.log("  ✓ AZZ Voice System loaded")
            except ImportError as e:
                self.log(f"  ✗ AZZ Voice System failed: {e}")

        # Initialize LED Matrix
        if self.config["components"]["led_matrix"]["enabled"]:
            try:
                from led_matrix_controller import LEDMatrixController
                self.led_matrix = LEDMatrixController()
                if self.config.get("led_enabled", True):
                    self.led_matrix.connect()
                    self.led_matrix.set_color_by_name(
                        self.config.get("led_default_color", "red")
                    )
                self.log("  ✓ LED Matrix loaded")
            except ImportError as e:
                self.log(f"  ✗ LED Matrix failed: {e}")

        # Initialize Voice-LED Integration
        if self.config["components"]["voice_led_integration"]["enabled"]:
            try:
                from voice_led_integration import VoiceLEDIntegration
                self.voice_led = VoiceLEDIntegration()
                self.log("  ✓ Voice-LED Integration loaded")
            except ImportError as e:
                self.log(f"  ✗ Voice-LED Integration failed: {e}")

    async def speak(
        self,
        text: str,
        voice: Optional[str] = None,
        backend: Optional[str] = None,
        output_path: Optional[Path] = None,
        led_enabled: bool = True,
        led_color: Optional[str] = None,
        show_text: bool = True,
        visualize: bool = True
    ) -> bool:
        """
        Universal speak function - routes through all Omega systems

        Args:
            text: Text to synthesize
            voice: Voice profile (default: azz)
            backend: Synthesis backend (azure/coqui, default: azure)
            output_path: Output audio file path
            led_enabled: Enable LED visualization
            led_color: LED color during speech
            show_text: Display text on LED matrix
            visualize: Enable audio visualization

        Returns:
            True if successful
        """
        voice = voice or self.config.get("default_voice", "azz")
        backend = backend or self.config.get("default_backend", "azure")
        led_color = led_color or self.config.get("led_default_color", "red")

        self.log(f"Speaking: {text[:50]}...")
        self.log(f"  Voice: {voice}, Backend: {backend}")

        # Use Voice-LED integration if available
        if self.voice_led and led_enabled:
            try:
                if output_path is None:
                    output_path = Path(f"omega_speech_{hash(text)}.wav")

                success = await self.voice_led.synthesize_with_visualization(
                    text=text,
                    output_path=output_path,
                    voice_system=backend
                )

                if success:
                    self.log("✓ Speech synthesis complete (with LED)")
                    return True

            except Exception as e:
                self.log(f"✗ Voice-LED synthesis failed: {e}")

        # Fallback to AZZ Voice only
        if self.azz_voice:
            try:
                if output_path is None:
                    output_path = Path(f"omega_speech_{hash(text)}.wav")

                # Set LED color if enabled
                if self.led_matrix and led_enabled:
                    self.led_matrix.set_color_by_name(led_color)
                    if show_text:
                        self.led_matrix.display_text(text[:16])

                # Synthesize
                if backend == "azure":
                    success = self.azz_voice.synthesize_with_azure(text, output_path)
                elif backend == "coqui":
                    success = self.azz_voice.synthesize_with_coqui(text, output_path)
                else:
                    self.log(f"✗ Unknown backend: {backend}")
                    return False

                # Visualize if enabled
                if success and visualize and self.led_matrix and output_path.exists():
                    await self.led_matrix.sync_with_speech(output_path)

                if success:
                    self.log("✓ Speech synthesis complete")
                    return True

            except Exception as e:
                self.log(f"✗ Synthesis failed: {e}")

        self.log("✗ No voice systems available")
        return False

    async def quick_speak(self, text: str, color: str = "red") -> bool:
        """
        Quick speak with default settings

        Args:
            text: Text to speak
            color: LED color

        Returns:
            True if successful
        """
        return await self.speak(
            text=text,
            led_color=color,
            show_text=True,
            visualize=True
        )

    async def system_announce(self, message: str, priority: str = "normal"):
        """
        System announcement with priority-based LED colors

        Args:
            message: Announcement message
            priority: Priority level (low/normal/high/critical)
        """
        color_map = {
            "low": "blue",
            "normal": "green",
            "high": "orange",
            "critical": "red"
        }

        color = color_map.get(priority, "green")

        self.log(f"System announcement [{priority.upper()}]: {message}")

        return await self.speak(
            text=message,
            led_color=color,
            show_text=True,
            visualize=False  # No visualization for system messages
        )

    def set_led_state(self, state: str):
        """
        Set LED state (idle/listening/processing/speaking/error/success)

        Args:
            state: State name
        """
        if self.voice_led:
            self.voice_led.rgb_control.set_state_color(state)
            self.log(f"LED state: {state}")

    def get_status(self) -> Dict:
        """Get hub status"""
        return {
            "version": self.config["version"],
            "components": {
                "azz_voice": self.azz_voice is not None,
                "led_matrix": self.led_matrix is not None,
                "voice_led": self.voice_led is not None
            },
            "default_voice": self.config["default_voice"],
            "default_backend": self.config["default_backend"],
            "led_enabled": self.config["led_enabled"],
            "led_default_color": self.config["led_default_color"],
            "led_connected": self.led_matrix.is_connected if self.led_matrix else False
        }

    async def test_all_systems(self):
        """Test all voice systems"""
        self.log("\n" + "=" * 70)
        self.log("TESTING ALL OMEGA VOICE SYSTEMS")
        self.log("=" * 70)

        tests = [
            ("System idle", "idle", "System ready"),
            ("Processing request", "processing", "Processing your request"),
            ("Speaking test", "speaking", "This is a voice system test"),
            ("Success message", "success", "All systems operational"),
        ]

        for test_name, state, text in tests:
            self.log(f"\n[{test_name}]")
            self.set_led_state(state)
            await asyncio.sleep(1)

            if text:
                await self.quick_speak(text)
                await asyncio.sleep(2)

        self.set_led_state("idle")
        self.log("\n✓ All systems tested")


# Global hub instance
omega_voice_hub = OmegaVoiceHub()


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  OMEGA VOICE HUB - UNIVERSAL VOICE INTEGRATION")
    print("=" * 70 + "\n")

    # Initialize hub
    hub = OmegaVoiceHub()

    # Show status
    print("Hub Status:")
    status = hub.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 70)
    print("  HUB READY")
    print("=" * 70)

    # Menu
    print("\nOptions:")
    print("  1. Test quick speak")
    print("  2. Test system announcement")
    print("  3. Test all systems")
    print("  4. Custom speech")
    print("  5. LED state control")
    print("  6. View configuration")
    print("  7. Exit")

    choice = input("\nChoice (1-7): ").strip()

    if choice == "1":
        text = input("\nEnter text to speak: ").strip()
        if text:
            await hub.quick_speak(text, color="red")
        else:
            print("✗ No text entered")

    elif choice == "2":
        message = input("\nEnter announcement: ").strip()
        priority = input("Priority (low/normal/high/critical): ").strip() or "normal"
        if message:
            await hub.system_announce(message, priority)
        else:
            print("✗ No message entered")

    elif choice == "3":
        await hub.test_all_systems()

    elif choice == "4":
        text = input("\nEnter text: ").strip()
        color = input("LED color (red/green/blue/etc.): ").strip() or "red"
        backend = input("Backend (azure/coqui): ").strip() or "azure"

        if text:
            await hub.speak(
                text=text,
                backend=backend,
                led_color=color,
                visualize=True
            )
        else:
            print("✗ No text entered")

    elif choice == "5":
        print("\nStates: idle, listening, processing, speaking, error, success")
        state = input("Select state: ").strip()
        if state:
            hub.set_led_state(state)
            await asyncio.sleep(2)

    elif choice == "6":
        print("\nConfiguration:")
        print(json.dumps(hub.config, indent=2))

    elif choice == "7":
        print("\nExiting...")

    # Save config
    hub.save_config()

    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
