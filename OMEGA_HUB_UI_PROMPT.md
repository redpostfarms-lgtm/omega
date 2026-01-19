# Omega Hub UI Design Prompt

## Overview
Floating, resizable overlay window for Red Post Farms & Omega AI integration with KITT-inspired voice visualizer.

---

## Static Image Prompt (for UI mockup)

```
Photorealistic compact UI window called 'Omega Hub' - sleek black chrome bezel with subtle metallic sheen, 2x2 inch square default size, floating overlay design with semi-transparent edges. 

Top bar: 'RED POST FARMS' text in matte crimson (hex #8B0000) lettering, bold sans-serif font, slightly embossed.

Center: Three vertical white LED bars (KITT Knight Rider season 2 style) - clean simple design, bars arranged in subtle V shape, glowing softly white/cyan when idle, no side buttons or extra LEDs, pure minimalist voice visualizer against black background.

Bottom left: Small pixel-art style goat icon (16x16px), white outline, gentle idle animation blinking every 3 seconds.

Bottom right: Tiny status indicator showing "SOIL: 68%" in green monospace font.

Overall aesthetic: 1980s retro-futuristic meets modern minimal UI, dark cockpit vibe, sharp details, 4K resolution, PNG with transparency for overlay capability.
```

---

## Animated Clip Prompt (5-second loop)

```
Seamless five-second animation loop of Omega Hub voice visualizer responding to speech:

Three vertical white LED bars in center pulse and sweep rhythmically like classic KITT equalizer - bars rise and fall in smooth waves (center bar leads, outer bars follow with slight delay), glowing cyan-white with soft bloom effect.

Red Post Farms text stays static at top.

Goat icon blinks once at 2-second mark.

Soil percentage updates from 68% to 67% smoothly.

Black chrome bezel reflects subtle ambient light.

Perfect loop for real-time voice response visualization, 60fps smooth motion, retro synth aesthetic, dark background with transparency edges.
```

---

## Interactive Features & Controls

### Toggle Controls
- **ESC**: Minimize to system tray / Hide window
- **CTRL + R**: Restore window from hidden state
- **CTRL + SHIFT + O**: Open Omega Hub (global hotkey)

### Resize Options
- **Default**: 2x2 inches (minimal mode)
- **Medium**: 4x4 inches (monitoring mode)
- **Large**: 6x6 inches (detailed mode)
- **Fullscreen**: Entire screen (dashboard mode)
- **Drag corners**: Free-form resize with aspect ratio lock toggle

### Right-Click Context Menu
```
┌─────────────────────────┐
│ Omega Hub               │
├─────────────────────────┤
│ ► Size Presets          │
│   • Minimal (2x2")      │
│   • Monitoring (4x4")   │
│   • Detailed (6x6")     │
│   • Fullscreen          │
├─────────────────────────┤
│ ► Voice Visualizer      │
│   • Match Voice Pitch   │
│   • Classic White       │
│   • KITT Red Mode       │
│   • Custom Color...     │
├─────────────────────────┤
│ ► Farm Icon             │
│   • Goat (default)      │
│   • Sheep               │
│   • Chicken             │
│   • Tractor             │
│   • Custom Image...     │
├─────────────────────────┤
│ ► Display Mode          │
│   • Farm Mode           │
│   • Omega Mode          │
│   • Gaming HUD          │
│   • Minimal Status      │
├─────────────────────────┤
│ ⚙ Settings              │
│ 💾 Save Current Preset   │
│ 🔄 Reset to Default     │
│ ❌ Close                │
└─────────────────────────┘
```

---

## Mode Presets

### Farm Mode
- Shows: Soil moisture, weather, livestock health
- Visualizer: Green spectrum (farm health indicator)
- Icon: Rotating farm animals
- Update frequency: 30 seconds

### Omega Mode
- Shows: AI status, processing load, voice activity
- Visualizer: White/cyan KITT style (matches voice)
- Icon: Omega logo pulsing
- Update frequency: Real-time

### Gaming HUD Mode
- Shows: Minimal - just voice visualizer
- Visualizer: Red KITT style (classic)
- Icon: Hidden
- Transparency: 80% (non-intrusive)
- Update frequency: Real-time voice response

### Minimal Status
- Shows: Single status line only
- Visualizer: Thin 1-bar equalizer
- Icon: Static small badge
- Update frequency: 60 seconds

---

## Technical Specifications

### Window Properties
- **Always on top**: Optional toggle
- **Click-through mode**: Available when transparent >70%
- **Snap to edges**: Magnetic snap to screen borders
- **Multi-monitor**: Remembers position per display
- **Opacity**: 20% - 100% adjustable via slider

### Voice Visualizer Behavior
- **Idle**: Slow breathing pulse (0.5 Hz)
- **Listening**: Medium pulse (2 Hz)
- **Speaking**: Dynamic equalizer matching audio input
- **Processing**: Rotating bars animation
- **Error**: Red flash (3 times)

### Data Sources
- **Soil Moisture**: Real-time sensor data from farm IoT
- **Livestock**: Health monitoring system integration
- **Voice Input**: Microphone audio levels (0-100 dB)
- **AI Status**: Omega processing state & confidence

---

## Color Schemes

### Default (Dark Mode)
- Background: `#0A0A0A` (near black)
- Frame: `#1A1A1A` (dark chrome)
- Primary text: `#FFFFFF` (white)
- Accent: `#8B0000` (crimson red)
- Visualizer: `#00FFFF` (cyan)

### KITT Classic
- Visualizer: `#FF0000` (pure red)
- Background: `#000000` (black)
- Frame: `#2A2A2A` (darker chrome)

### Farm Green
- Visualizer: `#00FF00` (bright green)
- Accent: `#228B22` (forest green)
- Background: `#0F1F0F` (dark green tint)

---

## File Integration

### Configuration File
Location: `omega_hub_config.json`

```json
{
  "window": {
    "size": "2x2",
    "position": { "x": 100, "y": 100 },
    "opacity": 0.95,
    "always_on_top": true,
    "current_mode": "Omega Mode"
  },
  "visualizer": {
    "style": "KITT",
    "color": "#00FFFF",
    "match_voice_pitch": true,
    "bar_count": 3
  },
  "farm_icon": {
    "type": "goat",
    "animate": true,
    "blink_interval": 3000
  },
  "presets": {
    "farm_mode": { "enabled": true },
    "omega_mode": { "enabled": true },
    "gaming_hud": { "enabled": true }
  },
  "hotkeys": {
    "toggle": "Ctrl+Shift+O",
    "hide": "Esc",
    "restore": "Ctrl+R"
  }
}
```

---

## Implementation Notes

1. **Voice Visualizer**: Use real-time FFT (Fast Fourier Transform) on microphone input to drive bar heights
2. **Resizing**: Maintain aspect ratio unless Shift is held while dragging
3. **Transparency**: Automatically increase when cursor hovers away (5-second delay)
4. **Persistence**: Save window position and settings on close, restore on launch
5. **Performance**: Use hardware acceleration for smooth 60fps animation
6. **Accessibility**: High contrast mode available, screen reader compatible

---

## Future Enhancements

- [ ] Multi-window support (separate farm/AI/gaming overlays)
- [ ] Custom visualizer patterns (waveform, circular, spectrum)
- [ ] Integration with voice commands ("Omega, show farm stats")
- [ ] Theme marketplace (community-created skins)
- [ ] Streaming overlay mode (OBS compatible)
- [ ] Mobile companion app (view stats on phone)

---

## Credits

- Inspired by: KITT voice box from Knight Rider (Season 2 design)
- For: Red Post Farms farm management system
- AI: Omega voice assistant integration
- Created: January 18, 2026

---

## Quick Start Command

To generate the base UI image:
```bash
# Use with Flux, Midjourney, or DALL-E 3
python omega_control_panel_web.py --generate-ui --style="kitt-minimal"
```

To test the animated visualizer:
```bash
# Run test pattern
python test_voice_visualizer.py --mode="kitt" --bars=3
```
