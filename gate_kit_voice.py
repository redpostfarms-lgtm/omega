"""
Gate - Kit Voice Integration
Using the Kit voice clip with LED KITT-style voice visualization
"""

import os
import sys
import subprocess
import random
import time
from pathlib import Path

# ANSI color codes
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"


class GateKitVoice:
    """Gate's Kit Voice System with LED visualization"""

    def __init__(self):
        self.kit_voice = Path("clip_0001.wav")
        self.personality = {
            "name": "Kit",
            "style": "Precise, technical, efficient",
            "color": CYAN,
            "led_pattern": "sweep",
        }

        # Kitt LED bar simulation patterns
        self.led_bars = 20
        self.sweep_speed = 0.05

    def print_header(self):
        """Display header with Kit branding"""
        print(f"\n{CYAN}{BOLD}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}{'🎙️  GATE - KIT VOICE SYSTEM  🎙️':^70}{RESET}")
        print(f"{CYAN}{BOLD}{'Neural Voice Interface Active':^70}{RESET}")
        print(f"{CYAN}{BOLD}{'=' * 70}{RESET}\n")

    def kitt_led_animation(self, duration=3.0, description="Processing..."):
        """Simulate KITT-style LED sweep animation"""
        print(f"\n{YELLOW}[{description}]{RESET}")

        start_time = time.time()
        direction = 1
        position = 0

        while time.time() - start_time < duration:
            # Build LED bar display
            bars = []
            for i in range(self.led_bars):
                if i == position:
                    bars.append(f"{RED}█{RESET}")  # Active LED
                elif abs(i - position) <= 2:
                    bars.append(f"{MAGENTA}▓{RESET}")  # Dim trail
                else:
                    bars.append(f"░")  # Off LED

            # Print LED bar
            print(f"\r{CYAN}║{RESET} {''.join(bars)} {CYAN}║{RESET}", end="", flush=True)

            # Update position
            position += direction
            if position >= self.led_bars - 1:
                direction = -1
            elif position <= 0:
                direction = 1

            time.sleep(self.sweep_speed)

        print(f"\n{GREEN}✓ Complete{RESET}\n")

    def check_kit_voice(self):
        """Verify Kit voice file exists"""
        if self.kit_voice.exists():
            size_mb = self.kit_voice.stat().st_size / (1024 * 1024)
            print(f"{GREEN}✓ Kit Voice Available{RESET}")
            print(f"  File: {self.kit_voice.name}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Status: Ready to play\n")
            return True
        else:
            print(f"{RED}✗ Kit voice file not found: {self.kit_voice}{RESET}\n")
            return False

    def play_kit_voice(self, intro_text="Hello, I am Kit."):
        """Play Kit voice with LED animation"""
        if not self.check_kit_voice():
            return False

        # LED animation during intro
        self.kitt_led_animation(2.0, "Initializing Kit Voice")

        print(f"\n{CYAN}{BOLD}[KIT SPEAKING]{RESET}")
        print(f"{CYAN}► {intro_text}{RESET}\n")

        # Play the voice
        try:
            abs_path = str(self.kit_voice.absolute())
            result = subprocess.run(
                [
                    "powershell",
                    "-c",
                    f'$player = New-Object System.Media.SoundPlayer("{abs_path}"); $player.PlaySync()',
                ],
                timeout=120,
                capture_output=True,
            )

            if result.returncode == 0:
                print(f"{GREEN}✓ Playback successful{RESET}\n")
                # LED animation after speech
                self.kitt_led_animation(1.5, "Voice Output Complete")
                return True
            else:
                print(f"{RED}✗ Playback failed{RESET}")
                return False

        except subprocess.TimeoutExpired:
            print(f"{YELLOW}⚠ Playback timeout{RESET}")
            return False
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")
            return False

    def kitt_pulse(self, count=3):
        """Pulsing LED effect"""
        print(f"\n{CYAN}[Pulse Pattern]{RESET}")

        for _ in range(count):
            # Pulse out
            for intensity in range(0, self.led_bars, 2):
                bar = "█" * intensity + "░" * (self.led_bars - intensity)
                print(f"\r{RED}{bar}{RESET}", end="", flush=True)
                time.sleep(0.03)

            # Pulse in
            for intensity in range(self.led_bars, 0, -2):
                bar = "█" * intensity + "░" * (self.led_bars - intensity)
                print(f"\r{RED}{bar}{RESET}", end="", flush=True)
                time.sleep(0.03)

        print(f"\n")

    def demo_sequence(self):
        """Run full demonstration sequence"""
        self.print_header()

        # Check voice file
        if not self.check_kit_voice():
            print(f"{YELLOW}Please ensure clip_0001.wav is in the current directory{RESET}")
            return

        print(f"{CYAN}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}Kit Voice Demonstration{RESET}")
        print(f"{CYAN}{'=' * 70}{RESET}\n")

        # Demo sequence
        demos = [
            "Greetings. I am Kit, your neural voice interface.",
            "All systems operational. Voice synthesis online.",
            "LED arrays synchronized. Audio processing active.",
            "Standing by for your command.",
        ]

        for i, text in enumerate(demos, 1):
            print(f"{YELLOW}[Demo {i}/{len(demos)}]{RESET}")
            self.play_kit_voice(text)

            if i < len(demos):
                print(f"{CYAN}Preparing next demo...{RESET}")
                time.sleep(1)

        # Final pulse
        print(f"\n{CYAN}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}Demonstration Complete{RESET}")
        print(f"{CYAN}{'=' * 70}{RESET}")
        self.kitt_pulse(2)

    def interactive_mode(self):
        """Interactive voice playback mode"""
        self.print_header()

        if not self.check_kit_voice():
            return

        print(f"{CYAN}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}Interactive Mode{RESET}")
        print(f"{CYAN}Commands:{RESET}")
        print(f"  {GREEN}play{RESET} - Play Kit voice")
        print(f"  {GREEN}sweep{RESET} - LED sweep animation")
        print(f"  {GREEN}pulse{RESET} - LED pulse animation")
        print(f"  {GREEN}demo{RESET} - Full demonstration")
        print(f"  {GREEN}quit{RESET} - Exit")
        print(f"{CYAN}{'=' * 70}{RESET}\n")

        while True:
            try:
                cmd = input(f"{CYAN}Kit > {RESET}").strip().lower()

                if cmd == "quit" or cmd == "exit":
                    print(f"{YELLOW}Shutting down Kit voice system...{RESET}")
                    self.kitt_led_animation(1.0, "Shutdown Sequence")
                    break

                elif cmd == "play":
                    self.play_kit_voice()

                elif cmd == "sweep":
                    self.kitt_led_animation(5.0, "LED Sweep Pattern")

                elif cmd == "pulse":
                    self.kitt_pulse(5)

                elif cmd == "demo":
                    self.demo_sequence()
                    print(f"\n{CYAN}Returning to interactive mode...{RESET}\n")

                elif cmd == "help" or cmd == "?":
                    print(f"{CYAN}Available commands: play, sweep, pulse, demo, quit{RESET}")

                elif cmd == "":
                    continue

                else:
                    print(f"{YELLOW}Unknown command: {cmd}{RESET}")
                    print(f"{CYAN}Type 'help' for available commands{RESET}")

            except KeyboardInterrupt:
                print(f"\n{YELLOW}Interrupted. Shutting down...{RESET}")
                break
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")


def main():
    """Main entry point"""
    gate = GateKitVoice()

    # Check command line arguments
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "demo":
            gate.demo_sequence()
        elif cmd == "play":
            gate.play_kit_voice()
        elif cmd == "sweep":
            gate.kitt_led_animation(5.0, "LED Sweep Demo")
        elif cmd == "pulse":
            gate.kitt_pulse(5)
        elif cmd == "interactive" or cmd == "i":
            gate.interactive_mode()
        else:
            print(
                f"{YELLOW}Usage: python gate_kit_voice.py [demo|play|sweep|pulse|interactive]{RESET}"
            )
    else:
        # Default: interactive mode
        gate.interactive_mode()


if __name__ == "__main__":
    main()
