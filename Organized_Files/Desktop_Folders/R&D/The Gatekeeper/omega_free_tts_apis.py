# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Free TTS APIs - Integration with Free Voice Synthesis Services
# Quantum Worldwide Scrub Enhanced

"""
Ω Omega Free TTS APIs

Integrates with free TTS services:
- Edge TTS (Microsoft) - FREE, no API key
- Coqui TTS - Open source, FREE
- Piper TTS - FREE, offline
- eSpeakNG - FREE, open source
"""

import sys
import io
from pathlib import Path
from typing import Optional, Dict, Any, List
import subprocess

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

GATE = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if not GATE.exists():
    GATE = Path.cwd() / 'The Gatekeeper'
if not GATE.exists() and Path.cwd().name == 'The Gatekeeper':
    GATE = Path.cwd()

OMEGA_VOICE_DIR = GATE / 'omega_voice'
OMEGA_VOICE_DIR.mkdir(parents=True, exist_ok=True)

# Edge TTS (Microsoft) - FREE, no API key needed
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Coqui TTS
try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False

# Piper TTS
try:
    import piper
    PIPER_TTS_AVAILABLE = True
except ImportError:
    PIPER_TTS_AVAILABLE = False

# eSpeakNG (via subprocess)
ESPEAK_AVAILABLE = False
try:
    result = subprocess.run(['espeak', '--version'], capture_output=True, timeout=2)
    if result.returncode == 0:
        ESPEAK_AVAILABLE = True
except (FileNotFoundError, subprocess.TimeoutExpired):
    pass


class EdgeTTSWrapper:
    """Wrapper for Edge TTS (Microsoft) - FREE, no API key."""
    
    def __init__(self):
        self.available = EDGE_TTS_AVAILABLE
        self.voices = []
        if self.available:
            self._load_voices()
    
    def _load_voices(self):
        """Load available voices."""
        try:
            import asyncio
            async def get_voices():
                voices = await edge_tts.list_voices()
                return voices
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.voices = loop.run_until_complete(get_voices())
            loop.close()
        except Exception:
            self.voices = []
    
    def speak(self, text: str, voice: str = None, output_file: Path = None) -> bool:
        """Synthesize speech using Edge TTS."""
        if not self.available:
            return False
        
        try:
            import asyncio
            
            async def synthesize():
                if voice:
                    tts = edge_tts.Communicate(text=text, voice=voice)
                else:
                    # Use default voice (usually en-US)
                    tts = edge_tts.Communicate(text=text)
                
                if output_file:
                    await tts.save(str(output_file))
                    return True
                else:
                    # Play directly
                    await tts.save(str(OMEGA_VOICE_DIR / 'temp_edge.wav'))
                    # Play using system player
                    import platform
                    if platform.system() == 'Windows':
                        import os
                        os.system(f'start {OMEGA_VOICE_DIR / "temp_edge.wav"}')
                    return True
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(synthesize())
            loop.close()
            return result
        except Exception as e:
            print(f"Edge TTS error: {e}")
            return False
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """List available voices."""
        return self.voices


class CoquiTTSWrapper:
    """Wrapper for Coqui TTS - Open source, FREE."""
    
    def __init__(self):
        self.available = COQUI_TTS_AVAILABLE
        self.tts = None
        if self.available:
            self._init_tts()
    
    def _init_tts(self):
        """Initialize Coqui TTS."""
        try:
            # Use a fast, high-quality model
            self.tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
        except Exception:
            try:
                # Fallback to simpler model
                self.tts = TTS(model_name="tts_models/en/ljspeech/glow-tts", progress_bar=False)
            except Exception:
                self.tts = None
    
    def speak(self, text: str, output_file: Path = None) -> bool:
        """Synthesize speech using Coqui TTS."""
        if not self.available or not self.tts:
            return False
        
        try:
            if output_file is None:
                output_file = OMEGA_VOICE_DIR / 'temp_coqui.wav'
            
            self.tts.tts_to_file(text=text, file_path=str(output_file))
            
            # Play if no output file specified
            if output_file == OMEGA_VOICE_DIR / 'temp_coqui.wav':
                import platform
                if platform.system() == 'Windows':
                    import os
                    os.system(f'start {output_file}')
            
            return True
        except Exception as e:
            print(f"Coqui TTS error: {e}")
            return False


class PiperTTSWrapper:
    """Wrapper for Piper TTS - FREE, offline."""
    
    def __init__(self):
        self.available = PIPER_TTS_AVAILABLE
    
    def speak(self, text: str, output_file: Path = None) -> bool:
        """Synthesize speech using Piper TTS."""
        if not self.available:
            return False
        
        try:
            if output_file is None:
                output_file = OMEGA_VOICE_DIR / 'temp_piper.wav'
            
            # Piper TTS usage
            # Note: Requires model download
            # piper-tts --model en_US-lessac-medium --output_file output.wav --text "Hello"
            
            import subprocess
            cmd = [
                'piper-tts',
                '--model', 'en_US-lessac-medium',
                '--output_file', str(output_file),
                '--text', text
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode == 0 and output_file.exists():
                # Play if temp file
                if output_file == OMEGA_VOICE_DIR / 'temp_piper.wav':
                    import platform
                    if platform.system() == 'Windows':
                        import os
                        os.system(f'start {output_file}')
                return True
            
            return False
        except Exception as e:
            print(f"Piper TTS error: {e}")
            return False


class FreeTTSManager:
    """Manager for all free TTS APIs."""
    
    def __init__(self):
        self.edge_tts = EdgeTTSWrapper()
        self.coqui_tts = CoquiTTSWrapper()
        self.piper_tts = PiperTTSWrapper()
        self.espeak_available = ESPEAK_AVAILABLE
        
        self.available_engines = []
        if self.edge_tts.available:
            self.available_engines.append("Edge TTS (Microsoft)")
        if self.coqui_tts.available:
            self.available_engines.append("Coqui TTS")
        if self.piper_tts.available:
            self.available_engines.append("Piper TTS")
        if self.espeak_available:
            self.available_engines.append("eSpeakNG")
    
    def speak(self, text: str, engine: str = "auto", **kwargs) -> bool:
        """Synthesize speech using best available engine."""
        if engine == "auto":
            # Try engines in order of quality
            if self.edge_tts.available:
                return self.edge_tts.speak(text, **kwargs)
            elif self.coqui_tts.available:
                return self.coqui_tts.speak(text, **kwargs)
            elif self.piper_tts.available:
                return self.piper_tts.speak(text, **kwargs)
            elif self.espeak_available:
                return self._speak_espeak(text, **kwargs)
            else:
                print("No TTS engines available")
                return False
        elif engine == "edge":
            return self.edge_tts.speak(text, **kwargs)
        elif engine == "coqui":
            return self.coqui_tts.speak(text, **kwargs)
        elif engine == "piper":
            return self.piper_tts.speak(text, **kwargs)
        elif engine == "espeak":
            return self._speak_espeak(text, **kwargs)
        else:
            print(f"Unknown engine: {engine}")
            return False
    
    def _speak_espeak(self, text: str, output_file: Path = None) -> bool:
        """Synthesize using eSpeakNG."""
        try:
            if output_file is None:
                output_file = OMEGA_VOICE_DIR / 'temp_espeak.wav'
            
            cmd = ['espeak', '-s', '150', '-w', str(output_file), text]
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0 and output_file.exists():
                import platform
                if platform.system() == 'Windows':
                    import os
                    os.system(f'start {output_file}')
                return True
            
            return False
        except Exception as e:
            print(f"eSpeak error: {e}")
            return False
    
    def list_available_engines(self) -> List[str]:
        """List available TTS engines."""
        return self.available_engines


def main():
    """Test free TTS APIs."""
    print("=" * 80)
    print("Ω OMEGA FREE TTS APIs")
    print("=" * 80)
    print()
    
    manager = FreeTTSManager()
    
    print("Available TTS Engines:")
    for engine in manager.list_available_engines():
        print(f"  ✓ {engine}")
    
    if not manager.available_engines:
        print("\n⚠️  No TTS engines available")
        print("\nInstall with:")
        print("  pip install edge-tts          # Edge TTS (Microsoft)")
        print("  pip install TTS               # Coqui TTS")
        print("  pip install piper-tts         # Piper TTS")
        print("  # eSpeakNG: Download from https://github.com/espeak-ng/espeak-ng")
    
    print("\n" + "=" * 80)
    print("Testing TTS...")
    print("=" * 80)
    
    test_text = "Hello. I am Omega. Gate guarded. System monitored."
    
    if manager.available_engines:
        print(f"\nSpeaking: {test_text}")
        manager.speak(test_text)
        print("\n✓ TTS test complete!")
    else:
        print("\nInstall TTS engines to test.")


if __name__ == '__main__':
    main()

