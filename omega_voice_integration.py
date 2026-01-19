"""
OMEGA Voice Integration System
Comprehensive voice system integrating Kit voice with LED controls,
voice variations, and full Omega system connectivity
"""

import os
import sys
import json
import subprocess
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"


class VoiceProfile:
    """Voice profile with personality and LED patterns"""

    def __init__(self, name: str, file: str, style: str, color: str, led_pattern: str):
        self.name = name
        self.file = file
        self.style = style
        self.color = color
        self.led_pattern = led_pattern
        self.play_count = 0
        self.last_played = None

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "file": self.file,
            "style": self.style,
            "color": self.color,
            "led_pattern": self.led_pattern,
            "play_count": self.play_count,
            "last_played": self.last_played,
        }


class OmegaVoiceSystem:
    """Integrated Omega Voice System with Kit voice and variations"""

    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config_file = self.base_path / "omega_voice_config.json"
        self.log_file = self.base_path / "system_monitor_reports" / "voice_system.log"

        # Voice profiles
        self.voices = {
            "kit": VoiceProfile(
                name="Kit",
                file="clip_0001.wav",
                style="Precise, Technical, Efficient",
                color=CYAN,
                led_pattern="sweep",
            ),
            "warm": VoiceProfile(
                name="Omega Warm",
                file="omega_downloaded.wav",
                style="Deep, Commanding, Authoritative",
                color=RED,
                led_pattern="pulse",
            ),
            "tactical": VoiceProfile(
                name="Tactical",
                file="clip_0001.wav",  # Pitch shifted version
                style="Strategic, Military, Direct",
                color=GREEN,
                led_pattern="strobe",
            ),
            "sentinel": VoiceProfile(
                name="Sentinel",
                file="clip_0001.wav",  # Speed adjusted version
                style="Watchful, Protective, Alert",
                color=BLUE,
                led_pattern="wave",
            ),
        }

        self.current_voice = "kit"
        self.led_bars = 30
        self.led_enabled = True

        # Load or create config
        self.load_config()

    def load_config(self):
        """Load voice system configuration"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                config = json.load(f)
                self.current_voice = config.get("current_voice", "kit")
                self.led_enabled = config.get("led_enabled", True)

                # Load play counts
                for voice_name, data in config.get("voices", {}).items():
                    if voice_name in self.voices:
                        self.voices[voice_name].play_count = data.get("play_count", 0)
                        self.voices[voice_name].last_played = data.get("last_played")

    def save_config(self):
        """Save voice system configuration"""
        config = {
            "current_voice": self.current_voice,
            "led_enabled": self.led_enabled,
            "voices": {name: voice.to_dict() for name, voice in self.voices.items()},
            "last_updated": datetime.now().isoformat(),
        }

        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def log(self, message: str):
        """Log voice system activity"""
        self.log_file.parent.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.log_file, "a") as f:
            f.write(log_entry)

    def print_header(self):
        """Display system header"""
        print(f"\n{CYAN}{BOLD}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}{'🎙️  OMEGA VOICE INTEGRATION SYSTEM  🎙️':^70}{RESET}")
        print(f"{CYAN}{BOLD}{'Multi-Voice Neural Interface':^70}{RESET}")
        print(f"{CYAN}{BOLD}{'=' * 70}{RESET}\n")

    def led_sweep(self, duration: float = 2.0, description: str = "Processing"):
        """KITT-style LED sweep animation"""
        if not self.led_enabled:
            return

        voice = self.voices[self.current_voice]
        print(f"\n{YELLOW}[{description}]{RESET}")

        start_time = time.time()
        position = 0
        direction = 1

        while time.time() - start_time < duration:
            bars = ["░"] * self.led_bars

            # Active LED with trail
            if 0 <= position < self.led_bars:
                bars[position] = f"{voice.color}█{RESET}"
                if position - 1 >= 0:
                    bars[position - 1] = f"{MAGENTA}▓{RESET}"
                if position - 2 >= 0:
                    bars[position - 2] = f"{DIM}▒{RESET}"
                if position + 1 < self.led_bars:
                    bars[position + 1] = f"{MAGENTA}▓{RESET}"
                if position + 2 < self.led_bars:
                    bars[position + 2] = f"{DIM}▒{RESET}"

            print(
                f"\r{voice.color}║{RESET}{''.join(bars)}{voice.color}║{RESET}", end="", flush=True
            )

            position += direction
            if position >= self.led_bars - 1:
                direction = -1
            elif position <= 0:
                direction = 1

            time.sleep(0.04)

        print(f"\n{GREEN}✓ Ready{RESET}\n")

    def led_pulse(self, count: int = 3):
        """Pulsing LED effect"""
        if not self.led_enabled:
            return

        voice = self.voices[self.current_voice]
        print(f"\n{voice.color}[Pulse Pattern]{RESET}")

        for _ in range(count):
            # Pulse out
            for intensity in range(0, self.led_bars, 3):
                bar = f"{voice.color}{'█' * intensity}{'░' * (self.led_bars - intensity)}{RESET}"
                print(f"\r{bar}", end="", flush=True)
                time.sleep(0.02)

            # Pulse in
            for intensity in range(self.led_bars, 0, -3):
                bar = f"{voice.color}{'█' * intensity}{'░' * (self.led_bars - intensity)}{RESET}"
                print(f"\r{bar}", end="", flush=True)
                time.sleep(0.02)

        print(f"\n")

    def led_wave(self, duration: float = 3.0):
        """Wave pattern LED effect"""
        if not self.led_enabled:
            return

        voice = self.voices[self.current_voice]
        print(f"\n{voice.color}[Wave Pattern]{RESET}")

        start_time = time.time()
        offset = 0

        while time.time() - start_time < duration:
            bars = []
            for i in range(self.led_bars):
                # Sine wave pattern
                intensity = int((1 + __import__("math").sin((i + offset) * 0.3)) * 5)
                if intensity > 7:
                    bars.append(f"{voice.color}█{RESET}")
                elif intensity > 5:
                    bars.append(f"{MAGENTA}▓{RESET}")
                elif intensity > 3:
                    bars.append(f"{DIM}▒{RESET}")
                else:
                    bars.append("░")

            print(
                f"\r{voice.color}║{RESET}{''.join(bars)}{voice.color}║{RESET}", end="", flush=True
            )
            offset += 1
            time.sleep(0.05)

        print(f"\n")

    def led_strobe(self, count: int = 5):
        """Strobe/flash effect"""
        if not self.led_enabled:
            return

        voice = self.voices[self.current_voice]
        print(f"\n{voice.color}[Strobe Pattern]{RESET}")

        for _ in range(count):
            # Flash on
            print(f"\r{voice.color}{'█' * self.led_bars}{RESET}", end="", flush=True)
            time.sleep(0.1)
            # Flash off
            print(f"\r{'░' * self.led_bars}", end="", flush=True)
            time.sleep(0.1)

        print(f"\n")

    def play_led_pattern(self, duration: float = 3.0):
        """Play LED pattern based on current voice"""
        voice = self.voices[self.current_voice]
        pattern = voice.led_pattern

        if pattern == "sweep":
            self.led_sweep(duration, f"{voice.name} Voice Active")
        elif pattern == "pulse":
            self.led_pulse(int(duration))
        elif pattern == "wave":
            self.led_wave(duration)
        elif pattern == "strobe":
            self.led_strobe(int(duration * 2))

    def check_voice_file(self, voice_name: str) -> bool:
        """Check if voice file exists"""
        voice = self.voices[voice_name]
        file_path = self.base_path / voice.file

        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"{GREEN}✓ {voice.name} Voice Available{RESET}")
            print(f"  File: {voice.file}")
            print(f"  Size: {size_mb:.2f} MB")
            print(f"  Style: {voice.style}")
            print(f"  Play Count: {voice.play_count}\n")
            return True
        else:
            print(f"{RED}✗ {voice.name} voice file not found: {voice.file}{RESET}\n")
            return False

    def play_voice(self, text: Optional[str] = None, voice_name: Optional[str] = None):
        """Play voice with LED animation"""
        if voice_name:
            self.current_voice = voice_name

        voice = self.voices[self.current_voice]

        if not self.check_voice_file(self.current_voice):
            return False

        # LED intro animation
        self.play_led_pattern(2.0)

        # Display text
        print(f"\n{voice.color}{BOLD}[{voice.name.upper()} SPEAKING]{RESET}")
        if text:
            print(f"{voice.color}► {text}{RESET}\n")
        else:
            print(f"{voice.color}► Playing {voice.name} voice sample...{RESET}\n")

        # Play audio
        try:
            file_path = str((self.base_path / voice.file).absolute())
            result = subprocess.run(
                [
                    "powershell",
                    "-c",
                    f'$player = New-Object System.Media.SoundPlayer("{file_path}"); $player.PlaySync()',
                ],
                timeout=120,
                capture_output=True,
            )

            if result.returncode == 0:
                # Update stats
                voice.play_count += 1
                voice.last_played = datetime.now().isoformat()
                self.save_config()
                self.log(f"Played {voice.name} voice successfully")

                print(f"{GREEN}✓ Playback complete{RESET}\n")

                # LED outro animation
                self.play_led_pattern(1.5)
                return True
            else:
                print(f"{RED}✗ Playback failed{RESET}")
                return False

        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")
            self.log(f"Error playing {voice.name}: {e}")
            return False

    def switch_voice(self, voice_name: str):
        """Switch to different voice profile"""
        if voice_name not in self.voices:
            print(f"{RED}✗ Unknown voice: {voice_name}{RESET}")
            print(f"{CYAN}Available voices: {', '.join(self.voices.keys())}{RESET}")
            return False

        self.current_voice = voice_name
        voice = self.voices[voice_name]

        print(f"\n{voice.color}{'=' * 70}{RESET}")
        print(f"{voice.color}{BOLD}[VOICE SWITCH] Now using {voice.name}{RESET}")
        print(f"{voice.color}{voice.style:^70}{RESET}")
        print(f"{voice.color}{'=' * 70}{RESET}\n")

        self.save_config()
        return True

    def list_voices(self):
        """Display all available voices"""
        print(f"\n{CYAN}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}Available Voice Profiles{RESET}")
        print(f"{CYAN}{'=' * 70}{RESET}\n")

        for name, voice in self.voices.items():
            marker = "●" if name == self.current_voice else "○"
            print(f"{voice.color}{marker} {voice.name}{RESET}")
            print(f"  {DIM}Style: {voice.style}{RESET}")
            print(f"  {DIM}Pattern: {voice.led_pattern} | Plays: {voice.play_count}{RESET}\n")

    def demo_all_voices(self):
        """Demonstrate all voice profiles"""
        self.print_header()

        print(f"{YELLOW}Running complete voice demonstration...{RESET}\n")

        for name in self.voices.keys():
            self.switch_voice(name)
            time.sleep(0.5)
            self.play_voice(f"This is {self.voices[name].name}. {self.voices[name].style}.")
            time.sleep(1)

        print(f"\n{GREEN}{'=' * 70}{RESET}")
        print(f"{GREEN}{BOLD}Demonstration Complete{RESET}")
        print(f"{GREEN}{'=' * 70}{RESET}\n")

    def interactive_mode(self):
        """Interactive voice control"""
        self.print_header()
        self.list_voices()

        print(f"{CYAN}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}Commands:{RESET}")
        print(f"  {GREEN}play{RESET} - Play current voice")
        print(f"  {GREEN}switch <voice>{RESET} - Switch voice (kit/warm/tactical/sentinel)")
        print(f"  {GREEN}list{RESET} - List all voices")
        print(f"  {GREEN}demo{RESET} - Demonstrate all voices")
        print(f"  {GREEN}led <on|off>{RESET} - Toggle LED animations")
        print(f"  {GREEN}sweep/pulse/wave/strobe{RESET} - Test LED patterns")
        print(f"  {GREEN}status{RESET} - Show system status")
        print(f"  {GREEN}quit{RESET} - Exit")
        print(f"{CYAN}{'=' * 70}{RESET}\n")

        while True:
            try:
                voice = self.voices[self.current_voice]
                cmd = input(f"{voice.color}{voice.name} > {RESET}").strip().lower()

                if cmd in ["quit", "exit", "q"]:
                    print(f"{YELLOW}Shutting down voice system...{RESET}")
                    self.led_sweep(1.0, "Shutdown Sequence")
                    break

                elif cmd == "play":
                    self.play_voice()

                elif cmd.startswith("switch "):
                    voice_name = cmd.split(" ", 1)[1]
                    self.switch_voice(voice_name)

                elif cmd == "list":
                    self.list_voices()

                elif cmd == "demo":
                    self.demo_all_voices()

                elif cmd == "led on":
                    self.led_enabled = True
                    print(f"{GREEN}✓ LED animations enabled{RESET}")
                    self.save_config()

                elif cmd == "led off":
                    self.led_enabled = False
                    print(f"{YELLOW}LED animations disabled{RESET}")
                    self.save_config()

                elif cmd == "sweep":
                    self.led_sweep(5.0, "LED Sweep Test")

                elif cmd == "pulse":
                    self.led_pulse(5)

                elif cmd == "wave":
                    self.led_wave(5.0)

                elif cmd == "strobe":
                    self.led_strobe(10)

                elif cmd == "status":
                    self.show_status()

                elif cmd in ["help", "?"]:
                    print(
                        f"{CYAN}Commands: play, switch, list, demo, led, sweep, pulse, wave, strobe, status, quit{RESET}"
                    )

                elif cmd == "":
                    continue

                else:
                    print(f"{YELLOW}Unknown command. Type 'help' for commands.{RESET}")

            except KeyboardInterrupt:
                print(f"\n{YELLOW}Interrupted{RESET}")
                break
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")

    def show_status(self):
        """Display system status"""
        print(f"\n{CYAN}{'=' * 70}{RESET}")
        print(f"{CYAN}{BOLD}Omega Voice System Status{RESET}")
        print(f"{CYAN}{'=' * 70}{RESET}\n")

        print(f"{BOLD}Current Voice:{RESET} {self.voices[self.current_voice].name}")
        print(f"{BOLD}LED Animations:{RESET} {'Enabled' if self.led_enabled else 'Disabled'}")
        print(f"{BOLD}Voice Profiles:{RESET} {len(self.voices)}")
        print(f"{BOLD}Total Plays:{RESET} {sum(v.play_count for v in self.voices.values())}\n")

        print(f"{BOLD}Most Used Voice:{RESET}")
        most_used = max(self.voices.values(), key=lambda v: v.play_count)
        print(f"  {most_used.name} ({most_used.play_count} plays)\n")


def main():
    """Main entry point"""
    system = OmegaVoiceSystem()

    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()

        if cmd == "play":
            voice = sys.argv[2] if len(sys.argv) > 2 else None
            system.play_voice(voice_name=voice)

        elif cmd == "demo":
            system.demo_all_voices()

        elif cmd == "list":
            system.print_header()
            system.list_voices()

        elif cmd == "status":
            system.print_header()
            system.show_status()

        elif cmd in ["interactive", "i"]:
            system.interactive_mode()

        else:
            print(
                f"{YELLOW}Usage: python omega_voice_integration.py [play|demo|list|status|interactive]{RESET}"
            )
    else:
        # Default: interactive mode
        system.interactive_mode()


if __name__ == "__main__":
    main()
