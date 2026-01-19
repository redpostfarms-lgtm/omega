# LED Matrix Visual Feedback System

Complete integration of 16×32 RGB LED Matrix Panel with AZZ voice profile for synchronized visual speech feedback.

## 🎨 Device Specifications

**LED Matrix Panel:**
- **Size**: 16×32 pixels (173×70mm)
- **Type**: RGB Full Color
- **Power**: 5V/2A USB
- **Control**: APP (iPixel Color) + Serial/USB
- **Communication**: Bluetooth + USB Serial
- **App**: Scan QR code for "iPixel Color" app

## 📁 System Components

```
omega_visual_feedback/
├── led_matrix_controller.py       # Core LED matrix control
├── rgb_control_interface.py       # RGB monitoring & control
├── voice_led_integration.py       # Voice + LED integration
├── LED_MATRIX_README.md           # This file
└── config/
    └── led_matrix_config.json     # Auto-generated config
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Required for serial communication
pip install pyserial

# Required for audio visualization
pip install librosa numpy scipy

# Optional: Azure Speech SDK
pip install azure-cognitiveservices-speech
```

### 2. Connect LED Matrix

1. **Connect USB cable** from LED Matrix to computer
2. **Power on** the device (5V/2A USB power)
3. **Turn on Bluetooth** (optional, for app control)
4. **Enable Location** (required for Bluetooth on some devices)

### 3. Test Connection

```bash
cd omega_visual_feedback
python led_matrix_controller.py
```

This will:
- Auto-detect the LED Matrix USB port
- Set default color to RED
- Display "OMEGA" on the matrix
- Show connection status

### 4. Run RGB Control

```bash
python rgb_control_interface.py
```

Interactive menu for:
- Setting state colors
- Custom RGB values
- Brightness adjustment
- Pulse and breathing effects
- Real-time visualization

### 5. Integrate with Voice

```bash
python voice_led_integration.py
```

Synchronizes LED visualization with AZZ voice synthesis.

## 🎯 Usage Examples

### Example 1: Basic LED Control

```python
from omega_visual_feedback.led_matrix_controller import LEDMatrixController

# Initialize controller
led = LEDMatrixController()
led.connect()  # Auto-detect USB port

# Set color to RED
led.set_color_by_name("red")

# Display text
led.display_text("HELLO")

# Adjust brightness
led.set_brightness(75)  # 75%

# Clear display
led.clear()
```

### Example 2: RGB Color Control

```python
from omega_visual_feedback.rgb_control_interface import RGBControlInterface
from omega_visual_feedback.led_matrix_controller import RGBColor

# Initialize RGB control
rgb = RGBControlInterface()

# Set predefined state
rgb.set_state_color("speaking")  # Red

# Set custom color
rgb.set_custom_color(255, 100, 50)  # Custom RGB

# Pulse effect
await rgb.pulse_color(RGBColor(255, 0, 0), duration=2.0)

# Breathing effect
await rgb.breathing_effect(RGBColor(0, 255, 0), cycles=3)
```

### Example 3: Voice + LED Integration

```python
from omega_visual_feedback.voice_led_integration import VoiceLEDIntegration
from pathlib import Path

# Initialize integration
voice_led = VoiceLEDIntegration()

# Synthesize with visual feedback
await voice_led.synthesize_with_visualization(
    text="Hello from AZZ!",
    output_path=Path("output.wav"),
    voice_system="azure"
)

# Quick speak with LED
await voice_led.speak_with_led(
    text="System ready",
    color="green",
    show_text=True
)
```

### Example 4: Audio Visualization

```python
from omega_visual_feedback.led_matrix_controller import led_matrix
from pathlib import Path

# Visualize audio file
audio_path = Path("speech.wav")
await led_matrix.sync_with_speech(audio_path)

# Real-time spectrum visualization
frequencies = [0.5, 0.8, 1.0, 0.9, 0.6, ...]  # 32 values
led_matrix.visualize_spectrum(frequencies)

# Waveform visualization
samples = [-0.1, 0.2, 0.5, 0.3, -0.2, ...]  # Audio samples
led_matrix.visualize_waveform(samples)
```

## 🎨 Color Presets

The system includes predefined colors for different speech states:

| State | Color | RGB | Hex | Use Case |
|-------|-------|-----|-----|----------|
| **speaking** | **Red** | **(255, 0, 0)** | **#ff0000** | **Active speech (default)** |
| idle | Dim Blue | (50, 50, 255) | #3232ff | System waiting |
| listening | Green | (0, 255, 0) | #00ff00 | Input mode |
| processing | Orange | (255, 165, 0) | #ffa500 | Computing |
| error | Magenta | (255, 0, 255) | #ff00ff | Error state |
| success | Cyan-Green | (0, 255, 128) | #00ff80 | Task complete |

### Changing Default Color

```python
# Method 1: Use preset
rgb_control.set_state_color("speaking")  # Red

# Method 2: Custom RGB
rgb_control.set_custom_color(255, 0, 0)  # Red

# Method 3: Direct color name
led_matrix.set_color_by_name("red")
```

## 📊 Visualization Modes

### 1. Spectrum Analyzer

Displays frequency spectrum as vertical bars:

```python
led_matrix.visualization_mode = "spectrum"
await led_matrix.sync_with_speech(audio_path)
```

### 2. Waveform Display

Shows audio waveform:

```python
led_matrix.visualization_mode = "wave"
await led_matrix.sync_with_speech(audio_path)
```

### 3. Pulse Effect

Rhythmic pulsing synchronized with speech:

```python
led_matrix.pulse_effect(duration=1.0)
```

## 🔧 Configuration

Configuration is auto-generated at:
```
omega_visual_feedback/config/led_matrix_config.json
```

**Default Configuration:**
```json
{
  "device": {
    "type": "16x32 LED Matrix",
    "dimensions": "173x70mm",
    "power": "5V/2A USB",
    "control": "APP/Serial"
  },
  "default_color": "red",
  "default_brightness": 100,
  "visualization_mode": "spectrum",
  "speech_sync": true,
  "auto_connect": true
}
```

## 📱 iPixel Color App

The LED Matrix can also be controlled via the official app:

1. **Scan QR code** on box to download "iPixel Color" app
2. **Enable Bluetooth and Location** on your device
3. **Connect** to LED Matrix
4. **Features**:
   - TEXT: Display custom text
   - GALLERY: Show images/GIFs
   - DIY: Draw custom patterns
   - RHYTHM: Music visualization
   - CLOCK/DATE: Display time
   - REMOTE CONTROL: IR remote support

## 🔌 USB Connection

### Auto-Detection

The system automatically detects the LED Matrix USB port:

```python
led = LEDMatrixController()
led.connect()  # Auto-detect
```

### Manual Port Selection

```python
# Windows
led.connect(port="COM3")

# Linux/Mac
led.connect(port="/dev/ttyUSB0")
```

### Find Available Ports

```python
import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for port in ports:
    print(f"{port.device} - {port.description}")
```

## 🎤 Integration with AZZ Voice

### Automatic Synchronization

```python
from omega_visual_feedback.voice_led_integration import VoiceLEDIntegration

# Initialize
integration = VoiceLEDIntegration()

# Speak with visualization
await integration.synthesize_with_visualization(
    text="AZZ voice with LED visualization",
    output_path=Path("output.wav")
)
```

**What happens:**
1. LED turns **orange** (processing)
2. Text synthesized with AZZ voice
3. LED turns **red** (speaking)
4. Text snippet displayed on matrix
5. Audio spectrum visualized in real-time
6. LED turns **cyan-green** (success)

### State Flow

```
IDLE (blue)
  ↓
PROCESSING (orange) → [Text-to-Speech]
  ↓
SPEAKING (red) → [Audio Playback + Visualization]
  ↓
SUCCESS (cyan-green)
```

## 🐛 Troubleshooting

### LED Matrix Not Detected

```bash
# Check USB connection
python -c "import serial.tools.list_ports; [print(p.device, p.description) for p in serial.tools.list_ports.comports()]"

# Install pyserial
pip install pyserial

# Try manual port
python led_matrix_controller.py
# Then modify code: led.connect(port="COM3")
```

### No Visualization

```bash
# Install audio libraries
pip install librosa numpy scipy

# Check audio file exists
ls output.wav

# Test with simple spectrum
python -c "from omega_visual_feedback.led_matrix_controller import led_matrix; led_matrix.visualize_spectrum([0.5]*32)"
```

### Colors Not Changing

```python
# Check connection
led = LEDMatrixController()
print(led.is_connected)

# Test color change
led.set_color_by_name("green")
print(led.current_color.to_hex())

# Increase brightness
led.set_brightness(100)
```

### App vs Serial Conflict

- The LED Matrix can only be controlled by **one source** at a time
- Close the iPixel Color app before using serial control
- Or use app for manual control, serial for automated sync

## 📊 Performance

**Visualization Performance:**
- Frame rate: ~20 FPS (50ms per frame)
- Audio analysis: Real-time with librosa
- Latency: <100ms from audio to display
- Spectrum bars: 32 (full width of 16×32 matrix)

**Power Consumption:**
- Typical: 5V @ 1A (5W)
- Maximum: 5V @ 2A (10W) at full brightness white
- USB 2.0/3.0 compatible

## 🔐 Safety

From device specifications:

⚠️ **WARNING:**
- **INGESTION HAZARD**: Contains button/coin battery
- Keep batteries OUT OF REACH of children
- Seek immediate medical attention if battery is swallowed
- Do not disassemble product
- Handle with care, cannot be folded vigorously
- Use only 5V/2A rated USB power supply

## 📚 API Reference

### LEDMatrixController

```python
class LEDMatrixController:
    def __init__(self, port: Optional[str] = None, baud_rate: int = 9600)
    def connect(self, port: Optional[str] = None) -> bool
    def disconnect(self)
    def set_color(self, color: RGBColor)
    def set_color_by_name(self, color_name: str)
    def set_brightness(self, brightness: int)  # 0-100
    def display_text(self, text: str, color: Optional[RGBColor] = None)
    def clear(self)
    def visualize_spectrum(self, frequencies: List[float])
    def visualize_waveform(self, samples: List[float])
    async def sync_with_speech(self, audio_path: Path)
```

### RGBControlInterface

```python
class RGBControlInterface:
    def set_state_color(self, state: str)
    def set_custom_color(self, r: int, g: int, b: int)
    def adjust_brightness(self, delta: int)
    async def pulse_color(self, color: RGBColor, duration: float = 2.0)
    async def breathing_effect(self, color: RGBColor, cycles: int = 3)
    def get_color_info(self) -> Dict
```

### VoiceLEDIntegration

```python
class VoiceLEDIntegration:
    async def synthesize_with_visualization(self, text: str, output_path: Path, voice_system: str = "azure")
    async def speak_with_led(self, text: str, color: str = "red", show_text: bool = True)
    async def demo_modes(self)
```

## 🎯 Complete Workflow Example

```python
import asyncio
from pathlib import Path
from omega_visual_feedback.voice_led_integration import VoiceLEDIntegration

async def omega_speak(text: str):
    """Complete AZZ voice + LED Matrix workflow"""

    # Initialize
    voice_led = VoiceLEDIntegration()

    # Set initial state
    voice_led.rgb_control.set_state_color("idle")
    await asyncio.sleep(1)

    # Processing
    voice_led.rgb_control.set_state_color("processing")
    voice_led.led.display_text("THINKING...")
    await asyncio.sleep(0.5)

    # Synthesize with visualization
    output = Path(f"omega_speech_{int(time.time())}.wav")
    success = await voice_led.synthesize_with_visualization(
        text=text,
        output_path=output,
        voice_system="azure"
    )

    if success:
        # Success state
        voice_led.rgb_control.set_state_color("success")
        await asyncio.sleep(1)
    else:
        # Error state
        voice_led.rgb_control.set_state_color("error")
        voice_led.led.display_text("ERROR")

    # Return to idle
    voice_led.rgb_control.set_state_color("idle")

# Usage
asyncio.run(omega_speak("Hello from Omega with AZZ voice and LED visualization!"))
```

## 📈 Future Enhancements

Planned features:
- [ ] WiFi connectivity for remote control
- [ ] Multiple display patterns for different voices
- [ ] Emotion-based color mapping
- [ ] Beat detection for music visualization
- [ ] Custom animation sequences
- [ ] Multi-matrix chaining support

---

**Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: ✓ Production Ready
**Default Color**: 🔴 Red (RGB 255,0,0)
