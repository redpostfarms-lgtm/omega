#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LED Matrix Panel Controller for Speech Visualization
Integrates with AZZ voice profile for visual feedback during speech
"""

import asyncio
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("⚠ pyserial not installed. Install: pip install pyserial")


@dataclass
class RGBColor:
    """RGB color representation"""
    r: int  # 0-255
    g: int  # 0-255
    b: int  # 0-255

    def to_hex(self) -> str:
        """Convert to hex color string"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_tuple(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple"""
        return (self.r, self.g, self.b)


class LEDMatrixController:
    """
    Controller for 16×32 RGB LED Matrix Panel
    Provides visual feedback during speech synthesis
    """

    # Predefined colors
    COLORS = {
        "red": RGBColor(255, 0, 0),
        "green": RGBColor(0, 255, 0),
        "blue": RGBColor(0, 0, 255),
        "yellow": RGBColor(255, 255, 0),
        "cyan": RGBColor(0, 255, 255),
        "magenta": RGBColor(255, 0, 255),
        "white": RGBColor(255, 255, 255),
        "orange": RGBColor(255, 165, 0),
        "purple": RGBColor(128, 0, 128),
        "pink": RGBColor(255, 192, 203),
        "off": RGBColor(0, 0, 0),
    }

    def __init__(self, port: Optional[str] = None, baud_rate: int = 9600):
        """
        Initialize LED Matrix Controller

        Args:
            port: Serial port (auto-detect if None)
            baud_rate: Serial baud rate (default 9600)
        """
        self.config_dir = Path(__file__).parent / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "led_matrix_config.json"

        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.is_connected = False

        # Matrix properties
        self.width = 32
        self.height = 16
        self.current_color = self.COLORS["red"]  # Default: red
        self.brightness = 100  # 0-100%

        # Load configuration
        self.config = self.load_config()

        # Speech visualization state
        self.visualizing = False
        self.visualization_mode = "spectrum"  # spectrum, wave, pulse

        self.log("LED Matrix Controller initialized")

    def log(self, message: str):
        """Log message"""
        print(f"[LED Matrix] {message}")

    def load_config(self) -> Dict:
        """Load configuration"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)

        # Default configuration
        return {
            "device": {
                "type": "16x32 LED Matrix",
                "dimensions": "173x70mm",
                "power": "5V/2A USB",
                "control": "APP/Serial"
            },
            "default_color": "red",
            "default_brightness": 100,
            "visualization_mode": "spectrum",
            "speech_sync": True,
            "auto_connect": True
        }

    def save_config(self):
        """Save configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
        self.log(f"✓ Configuration saved: {self.config_file}")

    def find_led_matrix_port(self) -> Optional[str]:
        """Auto-detect LED Matrix USB port"""
        if not SERIAL_AVAILABLE:
            return None

        self.log("Scanning for LED Matrix USB device...")

        ports = list(serial.tools.list_ports.comports())
        for port in ports:
            # Common USB serial identifiers
            if any(x in port.description.lower() for x in ["usb", "serial", "ch340", "cp210"]):
                self.log(f"Found potential device: {port.device} - {port.description}")
                return port.device

        self.log("⚠ No LED Matrix device found")
        return None

    def connect(self, port: Optional[str] = None) -> bool:
        """
        Connect to LED Matrix via serial

        Args:
            port: Serial port (auto-detect if None)

        Returns:
            True if connected successfully
        """
        if not SERIAL_AVAILABLE:
            self.log("✗ pyserial not available")
            return False

        # Auto-detect port if not specified
        if port is None:
            port = self.find_led_matrix_port()

        if port is None:
            self.log("✗ No serial port found")
            return False

        try:
            self.serial_conn = serial.Serial(
                port=port,
                baudrate=self.baud_rate,
                timeout=1
            )
            self.is_connected = True
            self.port = port
            self.log(f"✓ Connected to {port}")
            return True

        except Exception as e:
            self.log(f"✗ Connection failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from LED Matrix"""
        if self.serial_conn:
            self.serial_conn.close()
            self.is_connected = False
            self.log("Disconnected")

    def send_command(self, command: str) -> bool:
        """
        Send command to LED Matrix

        Args:
            command: Command string

        Returns:
            True if command sent successfully
        """
        if not self.is_connected:
            self.log("⚠ Not connected - simulating command")
            self.log(f"  Command: {command}")
            return True

        try:
            self.serial_conn.write(f"{command}\n".encode())
            return True
        except Exception as e:
            self.log(f"✗ Command failed: {e}")
            return False

    def set_color(self, color: RGBColor):
        """
        Set LED matrix color

        Args:
            color: RGB color
        """
        self.current_color = color
        command = f"COLOR:{color.r},{color.g},{color.b}"
        self.send_command(command)
        self.log(f"Color set: RGB({color.r}, {color.g}, {color.b})")

    def set_color_by_name(self, color_name: str):
        """
        Set color by name

        Args:
            color_name: Color name (red, green, blue, etc.)
        """
        if color_name.lower() in self.COLORS:
            self.set_color(self.COLORS[color_name.lower()])
        else:
            self.log(f"⚠ Unknown color: {color_name}")

    def set_brightness(self, brightness: int):
        """
        Set LED brightness

        Args:
            brightness: Brightness level (0-100)
        """
        self.brightness = max(0, min(100, brightness))
        command = f"BRIGHTNESS:{self.brightness}"
        self.send_command(command)
        self.log(f"Brightness: {self.brightness}%")

    def display_text(self, text: str, color: Optional[RGBColor] = None):
        """
        Display text on LED matrix

        Args:
            text: Text to display
            color: RGB color (uses current color if None)
        """
        if color:
            self.set_color(color)

        command = f"TEXT:{text}"
        self.send_command(command)
        self.log(f"Displaying: {text}")

    def clear(self):
        """Clear LED matrix display"""
        self.send_command("CLEAR")
        self.log("Display cleared")

    def visualize_spectrum(self, frequencies: List[float]):
        """
        Visualize audio frequency spectrum

        Args:
            frequencies: List of frequency magnitudes (0-1)
        """
        # Create bar graph from frequencies
        num_bars = min(len(frequencies), self.width)
        bar_data = []

        for i in range(num_bars):
            bar_height = int(frequencies[i] * self.height)
            bar_data.append(bar_height)

        command = f"SPECTRUM:{','.join(map(str, bar_data))}"
        self.send_command(command)

    def visualize_waveform(self, samples: List[float]):
        """
        Visualize audio waveform

        Args:
            samples: Audio samples (-1 to 1)
        """
        # Convert samples to display coordinates
        num_points = min(len(samples), self.width)
        points = []

        for i in range(num_points):
            y = int((samples[i] + 1) * self.height / 2)
            points.append(y)

        command = f"WAVE:{','.join(map(str, points))}"
        self.send_command(command)

    def pulse_effect(self, duration: float = 1.0):
        """
        Create pulsing effect

        Args:
            duration: Pulse duration in seconds
        """
        command = f"PULSE:{duration}"
        self.send_command(command)

    async def sync_with_speech(self, audio_path: Path):
        """
        Synchronize LED visualization with speech audio

        Args:
            audio_path: Path to audio file
        """
        self.log(f"Syncing with audio: {audio_path}")

        try:
            import librosa
            import numpy as np

            # Load audio
            y, sr = librosa.load(str(audio_path), sr=None)

            # Extract features for visualization
            hop_length = 512
            duration = len(y) / sr

            # Calculate spectrum
            S = np.abs(librosa.stft(y, hop_length=hop_length))

            # Get frames
            num_frames = S.shape[1]
            frame_duration = hop_length / sr

            self.visualizing = True

            # Visualize each frame
            for i in range(num_frames):
                if not self.visualizing:
                    break

                # Get frequency bins for this frame
                frame = S[:, i]

                # Normalize and take top frequencies
                frame_norm = frame / (np.max(frame) + 1e-10)

                # Downsample to matrix width
                bins = np.interp(
                    np.linspace(0, len(frame_norm)-1, self.width),
                    np.arange(len(frame_norm)),
                    frame_norm
                )

                # Visualize
                if self.visualization_mode == "spectrum":
                    self.visualize_spectrum(bins.tolist())
                elif self.visualization_mode == "wave":
                    # Use amplitude envelope for waveform
                    start_idx = i * hop_length
                    end_idx = min(start_idx + hop_length, len(y))
                    samples = y[start_idx:end_idx]
                    if len(samples) > 0:
                        downsampled = np.interp(
                            np.linspace(0, len(samples)-1, self.width),
                            np.arange(len(samples)),
                            samples
                        )
                        self.visualize_waveform(downsampled.tolist())

                # Wait for frame duration
                await asyncio.sleep(frame_duration)

            self.visualizing = False
            self.log("✓ Speech visualization complete")

        except ImportError:
            self.log("✗ librosa not installed for audio analysis")
        except Exception as e:
            self.log(f"✗ Visualization error: {e}")

    def stop_visualization(self):
        """Stop current visualization"""
        self.visualizing = False
        self.clear()

    def get_status(self) -> Dict:
        """Get controller status"""
        return {
            "connected": self.is_connected,
            "port": self.port,
            "color": {
                "rgb": self.current_color.to_tuple(),
                "hex": self.current_color.to_hex()
            },
            "brightness": self.brightness,
            "visualization_mode": self.visualization_mode,
            "visualizing": self.visualizing,
            "matrix_size": f"{self.width}x{self.height}"
        }


# Global controller instance
led_matrix = LEDMatrixController()


async def main():
    """Main entry point for testing"""
    print("\n" + "=" * 70)
    print("  LED MATRIX CONTROLLER - SPEECH VISUALIZATION")
    print("=" * 70 + "\n")

    controller = LEDMatrixController()

    # Auto-connect
    if controller.config.get("auto_connect", True):
        print("Attempting auto-connect...")
        controller.connect()

    print("\nAvailable Colors:")
    for name, color in controller.COLORS.items():
        print(f"  • {name}: RGB{color.to_tuple()} - {color.to_hex()}")

    # Set default color to red
    print("\nSetting color to RED...")
    controller.set_color_by_name("red")

    print("\nController Status:")
    status = controller.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    # Demo: Display text
    print("\nDisplaying 'OMEGA' on matrix...")
    controller.display_text("OMEGA")

    # Save configuration
    controller.save_config()

    print("\n" + "=" * 70)
    print("  READY FOR SPEECH VISUALIZATION")
    print("=" * 70)
    print("\nIntegration:")
    print("  from omega_visual_feedback.led_matrix_controller import led_matrix")
    print("  led_matrix.set_color_by_name('red')")
    print("  await led_matrix.sync_with_speech(audio_path)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
