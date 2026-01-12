# Voice Improvement System - Complete Guide

## Overview
This system helps improve Omega's TTS voice quality by:
1. Finding free audio resources
2. Recording conversations
3. Analyzing voice characteristics (pitch, spectral features, wavelengths)
4. Comparing with reference voices
5. Improving TTS based on analysis

## Free Audio Resources Found

### Sound Effects (6 sources)
- **Freesound.org** - 500,000+ sounds (CC0/CC-BY)
- **Zapsplat** - Professional library (Free with attribution)
- **BBC Sound Effects** - 16,000+ archive sounds
- **OpenGameArt** - Free game assets
- **Incompetech** - Royalty-free music/sounds
- **Mixkit** - Free sound effects

### Voice Samples (6 datasets)
- **Common Voice (Mozilla)** - Massive multilingual dataset (CC0)
- **LibriSpeech** - 1000 hours of audiobook speech (CC BY 4.0)
- **LJSpeech** - 24 hours, single speaker, high quality (Public Domain) ⭐ **Best for voice cloning**
- **CMU ARCTIC** - Phonetically balanced US English
- **TED-LIUM** - TED talks dataset
- **VoxCeleb** - Speaker recognition dataset

### Recommended for Voice Improvement
- **Voice Cloning**: LJSpeech, Common Voice, CMU ARCTIC
- **Voice Characteristics**: LibriSpeech, TED-LIUM
- **Sound Effects**: Freesound, BBC Sound Effects

## Tools Created

### 1. `audio_resource_finder.py`
Finds and catalogs free audio resources.
```batch
py -3.11 audio_resource_finder.py
```

### 2. `conversation_recorder.py`
Records conversation segments and analyzes them.
```batch
py -3.11 conversation_recorder.py
```

### 3. `voice_improvement_analyzer.py`
Analyzes voice characteristics:
- Pitch (fundamental frequency)
- Spectral centroid
- Spectral rolloff
- Zero-crossing rate
- MFCCs (Mel-frequency cepstral coefficients)
- Chroma features
- Harmonic ratios
- Tempo/rhythm

```batch
py -3.11 voice_improvement_analyzer.py
```

### 4. `interactive_omega.py`
Interactive conversation mode with:
- Speech recognition
- Voice recording
- Emotion detection
- Automatic responses
- Background audio playback

```batch
py -3.11 interactive_omega.py
```

## Quick Start

### Option 1: Quick Conversation
```batch
TALK_WITH_OMEGA.bat
```

### Option 2: Full System
```batch
START_VOICE_IMPROVEMENT.bat
```

## What Gets Analyzed

### Voice Characteristics Extracted:
1. **Pitch** (Fundamental Frequency)
   - Mean, std, min, max
   - Helps match voice pitch

2. **Spectral Features**
   - Centroid: "Brightness" of voice
   - Rolloff: Frequency content
   - Zero-crossing rate: Voice quality

3. **MFCCs** (13 coefficients)
   - Voice timbre characteristics
   - Unique voice fingerprint

4. **Chroma Features**
   - Harmonic content
   - Musical quality of voice

5. **Energy & Dynamics**
   - RMS energy
   - Volume patterns
   - Tempo/rhythm

6. **Harmonic Ratio**
   - Voice vs noise ratio
   - Voice clarity

## How It Improves Voice Quality

1. **Records Your Voice**
   - Every conversation is saved
   - Multiple samples analyzed

2. **Extracts Features**
   - Analyzes pitch, spectral features, MFCCs
   - Creates voice fingerprint

3. **Compares with References**
   - Compares with clip_0001.wav
   - Compares with reference datasets
   - Finds optimal characteristics

4. **Improves TTS**
   - Uses voice clone (clip_0001.wav) always
   - Adjusts based on analysis
   - Better voice matching

## File Structure

```
conversations/          # Recorded conversation segments
  ├── conv_YYYYMMDD_HHMMSS.wav
  └── conv_YYYYMMDD_HHMMSS.json  # Metadata

audio_resources.json    # Catalog of free resources
clip_0001.wav          # Your voice reference sample
```

## Next Steps

1. **Start Conversation**: Run `TALK_WITH_OMEGA.bat`
2. **Answer Questions**: Omega will ask questions to gather voice samples
3. **Analyze**: Run `voice_improvement_analyzer.py` after recording
4. **Compare**: Compare your voice with reference samples
5. **Improve**: TTS automatically uses voice clone and learns from patterns

## Tips

- **Speak Naturally**: Don't overthink, just talk normally
- **Variety**: Talk about different topics for diverse samples
- **Duration**: Longer conversations = better analysis
- **Quality**: Use good microphone for better results
- **Reference**: Keep clip_0001.wav as your main voice reference

## Technical Details

### Audio Analysis Stack:
- `librosa` - Audio analysis and feature extraction
- `sounddevice` - Audio recording
- `scipy` - Signal processing
- `numpy` - Numerical computation

### TTS Stack:
- `TTS` (Coqui) - Text-to-speech
- `xtts_v2` model - Voice cloning model
- Voice clone always enabled via `clip_0001.wav`

### Recording Settings:
- Sample Rate: 16 kHz
- Format: 16-bit WAV
- Channels: Mono
- Duration: 5-10 seconds per segment

---

**Ready to improve Omega's voice? Start with `TALK_WITH_OMEGA.bat`!**
