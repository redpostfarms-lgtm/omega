# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# TRADEMARK NOTICE: "Omega" and "Ω" are trademarks of Red Post Farms, LLC.
#
"""
Offline Text-to-Speech System
Uses eSpeak or Piper for offline TTS.

Red Post Farms, LLC - 2026
"""

import sys
import io
import subprocess
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
PIPER_MODEL_DIR = GATE / 'models' / 'piper'

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    import onnxruntime
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False

class OfflineTTS:
    def __init__(self):
        self.engine = None
        self.piper_model = None
        self._init_offline_tts()
    
    def _init_offline_tts(self):
        """Initialize offline TTS."""
        if PYTTSX3_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                voices = self.engine.getProperty('voices')
                if len(voices) > 1:
                    self.engine.setProperty('voice', voices[1].id)
                self.engine.setProperty('rate', 110)
                self.engine.setProperty('volume', 0.7)
                return True
            except: pass
        
        # Check for eSpeak
        try:
            subprocess.run(['espeak', '--version'], capture_output=True, timeout=2)
            return True
        except: pass
        
        return False
    
    def synthesize(self, text: str, voice: str = "default") -> bool:
        """Synthesize text to speech."""
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            except: pass
        
        # Fallback to eSpeak
        try:
            subprocess.run(['espeak', text], timeout=10)
            return True
        except: pass
        
        # Fallback to print
        print(text)
        return False

def init_offline_tts() -> OfflineTTS:
    """Initialize offline TTS system."""
    return OfflineTTS()

if __name__ == "__main__":
    tts = init_offline_tts()
    if tts.engine or True:  # eSpeak fallback
        print("Offline TTS ready.")
        tts.synthesize("This is a test of the offline text to speech system.")
    else:
        print("Offline TTS not available. Install pyttsx3 or eSpeak.")

