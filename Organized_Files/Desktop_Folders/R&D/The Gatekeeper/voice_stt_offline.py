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
Offline Speech-to-Text System
Uses Vosk for offline speech recognition.

Red Post Farms, LLC - 2026
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
GATE = BRAIN / 'The Gatekeeper'
MODEL_DIR = GATE / 'models' / 'vosk'

try:
    import vosk
    import pyaudio
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

class OfflineSTT:
    def __init__(self, model_name: str = "vosk-model-small-en-us-0.15"):
        self.model = None
        self.recognizer = None
        self.audio = None
        self.stream = None
        self.model_path = MODEL_DIR / model_name
        self._init_offline_stt()
    
    def _init_offline_stt(self):
        """Initialize offline STT."""
        if not VOSK_AVAILABLE:
            return False
        
        if not self.model_path.exists():
            print(f"Model not found: {self.model_path}")
            print("Download from: https://alphacephei.com/vosk/models")
            return False
        
        try:
            self.model = vosk.Model(str(self.model_path))
            self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4000
            )
            return True
        except Exception as e:
            print(f"STT initialization error: {e}")
            return False
    
    def transcribe(self, audio_data: bytes = None, duration: float = 3.0) -> str:
        """Transcribe audio to text."""
        if not self.recognizer:
            return ""
        
        try:
            if audio_data:
                self.recognizer.AcceptWaveform(audio_data)
            else:
                import time
                start = time.time()
                while time.time() - start < duration:
                    data = self.stream.read(4000, exception_on_overflow=False)
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        if result.get('text'):
                            return result['text']
                final = json.loads(self.recognizer.FinalResult())
                return final.get('text', '')
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    def __del__(self):
        """Cleanup."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()

import json

def init_offline_stt(model_name: str = "vosk-model-small-en-us-0.15") -> OfflineSTT:
    """Initialize offline STT system."""
    return OfflineSTT(model_name)

if __name__ == "__main__":
    stt = init_offline_stt()
    if stt.recognizer:
        print("Offline STT ready. Speak for 3 seconds...")
        text = stt.transcribe(duration=3.0)
        print(f"Transcribed: {text}")
    else:
        print("Offline STT not available. Install Vosk and download model.")

