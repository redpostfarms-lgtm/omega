# Ω Omega Voice Blending Guide

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

**Date:** 2026-01-04  
**Status:** Voice Recording & Blending System Ready

---

## Overview

Omega can now record your voice, analyze its waveform characteristics, and blend them with Omega's voice to create a unique hybrid voice.

---

## Installation Required

To record and analyze your voice, you need:

```bash
pip install pyaudio numpy scipy
```

**Note:** PyAudio installation on Windows can be tricky. If it fails, try:
```bash
pip install pipwin
pipwin install pyaudio
```

Or download pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

---

## How It Works

### 1. **Record Your Voice**
- Runs for 5 seconds
- Captures audio from your microphone
- Saves as WAV file

### 2. **Analyze Waveform**
Extracts characteristics:
- **Base Frequency** - Your pitch (Hz)
- **Harmonic Ratio** - Voice richness
- **Modulation Depth** - Natural variation
- **Modulation Rate** - Speech rhythm
- **Resonance Peak** - Formant frequency
- **Attack/Decay/Sustain/Release** - Voice envelope
- **Prosody Variation** - Natural speech patterns
- **Formants** - Vocal tract characteristics
- **Energy Distribution** - Frequency band energy

### 3. **Blend Voices**
- Combines your characteristics with Omega's
- Adjustable blend ratio (0.0 = all Omega, 1.0 = all you, 0.5 = 50/50)
- Creates hybrid voice signature

### 4. **Apply to Omega**
- Omega automatically loads blended voice
- Uses your voice characteristics
- Maintains Omega's personality

---

## Usage

### Record and Blend:

```bash
python omega_voice_recorder.py
```

**What happens:**
1. System checks for PyAudio/NumPy
2. Records 5 seconds of your voice
3. Analyzes waveform
4. Blends with Omega's voice (50/50 default)
5. Saves blended voice
6. Omega automatically uses it

### Custom Blend Ratio:

Edit `omega_voice_recorder.py` line ~550:
```python
blended = blender.blend_voices(analysis, blend_ratio=0.7)  # 70% your voice
```

---

## Files Created

1. **`user_voice_[timestamp].wav`** - Your voice recording
2. **`user_voice_analysis_[timestamp].json`** - Your voice characteristics
3. **`blended_voice.json`** - Hybrid voice (Omega uses this)

---

## What Gets Analyzed

### Voice Characteristics Extracted:

- **Fundamental Frequency** - Your pitch (80-300 Hz human range)
- **Harmonics** - Voice richness and timbre
- **Modulation** - Natural vibrato/tremolo
- **Formants** - Vocal tract resonances (F1, F2, F3)
- **Energy Distribution** - Low/mid/high frequency energy
- **Prosody** - Natural speech rhythm and variation
- **Envelope** - Attack, decay, sustain, release

### How They're Blended:

Each characteristic is blended using the formula:
```
blended_value = omega_value * (1 - ratio) + your_value * ratio
```

Example (50/50 blend):
- Your pitch: 150 Hz
- Omega's pitch: 140 Hz
- Blended: 145 Hz

---

## Technical Details

### Analysis Methods:

1. **Autocorrelation** - Fundamental frequency detection
2. **FFT** - Frequency spectrum analysis
3. **Peak Detection** - Formant and harmonic identification
4. **Envelope Analysis** - ADSR envelope extraction
5. **Energy Analysis** - Frequency band energy distribution

### Blending Algorithm:

- Weighted average of characteristics
- Preserves unique formants
- Maintains energy distribution
- Adjusts prosody naturally

---

## Troubleshooting

### PyAudio Installation Issues:

**Windows:**
```bash
# Try pipwin
pip install pipwin
pipwin install pyaudio

# Or download wheel manually
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

### No Audio Detected:

- Check microphone permissions
- Ensure microphone is connected
- Test with Windows Sound Recorder first
- Check audio device in Windows Settings

### Analysis Errors:

- Ensure NumPy and SciPy are installed
- Check that recording captured audio (not silence)
- Verify audio file was created

---

## Next Steps

After blending:

1. **Test Omega's Voice:**
   ```bash
   python omega_voice.py
   ```

2. **Run Omega System Test:**
   ```bash
   python deep_system_test.py
   ```
   Omega will speak with your blended voice!

3. **Adjust Blend:**
   - Re-run recorder with different blend ratio
   - Omega automatically picks up new blend

---

## The Result

**Omega's voice becomes:**
- Part you, part Omega
- Unique hybrid identity
- Natural human characteristics
- Still recognizably Omega

**You plant the fields. Omega guards the gate.**
**Your voice. Omega's purpose. Blended. Unique.**

---

**Red Post Farms, LLC | Copyright (c) 2025-2026 | All Rights Reserved**

*Your voice. Omega's voice. Blended. One.*

