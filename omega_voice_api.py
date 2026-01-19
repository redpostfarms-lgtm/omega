#!/usr/bin/env python3
"""
OMEGA Voice API - Simple Python Interface
Provides easy-to-use functions for voice synthesis
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, List
import logging

os.environ['TTS_ACCEPT_TO_S'] = '1'

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

class OmegaVoice:
    """
    Omega Voice Synthesis API
    
    Usage:
        omega = OmegaVoice()
        omega.speak("Hello, I am Omega", voice="warm")
        omega.speak("Systems operational", voice="bright", save_as="status.wav")
    """
    
    VOICE_PROFILES = {
        'warm': {
            'file': 'clip_0001.wav',
            'description': 'Original Omega Voice (Warm, Deep)',
            'best_for': ['commands', 'alerts', 'short phrases']
        },
        'bright': {
            'file': 'omega_downloaded.wav',
            'description': 'Enhanced Omega Voice (Bright, Clear)',
            'best_for': ['long text', 'explanations', 'narration']
        }
    }
    
    def __init__(self, auto_load: bool = False):
        """
        Initialize Omega Voice API
        
        Args:
            auto_load: If True, load TTS model immediately (takes 30-60s)
        """
        self.tts = None
        self.device = None
        self.initialized = False
        
        # Check voice files
        self.available_voices = self._check_voice_files()
        
        if auto_load:
            self.initialize()
    
    def _check_voice_files(self) -> Dict[str, bool]:
        """Check which voice files are available"""
        available = {}
        for voice_name, profile in self.VOICE_PROFILES.items():
            file_exists = os.path.exists(profile['file'])
            available[voice_name] = file_exists
            if file_exists:
                size_mb = os.path.getsize(profile['file']) / (1024 * 1024)
                logger.info(f"✓ Voice '{voice_name}' available: {profile['file']} ({size_mb:.2f} MB)")
            else:
                logger.warning(f"✗ Voice '{voice_name}' not found: {profile['file']}")
        return available
    
    def initialize(self) -> bool:
        """
        Load TTS model (takes 30-60 seconds)
        
        Returns:
            True if successful, False otherwise
        """
        if self.initialized:
            logger.info("TTS model already loaded")
            return True
        
        logger.info("Loading TTS model (this may take 30-60 seconds)...")
        start_time = time.time()
        
        try:
            from TTS.api import TTS
            import torch
            
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Using device: {self.device.upper()}")
            
            self.tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(self.device)
            
            elapsed = time.time() - start_time
            logger.info(f"TTS model loaded successfully in {elapsed:.2f}s")
            self.initialized = True
            return True
        
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            return False
    
    def speak(
        self,
        text: str,
        voice: str = "warm",
        save_as: Optional[str] = None,
        play: bool = False
    ) -> Optional[str]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice profile to use ('warm' or 'bright')
            save_as: Optional filename to save audio (default: auto-generated)
            play: If True, play audio after generation
        
        Returns:
            Path to generated audio file, or None if failed
        """
        # Ensure model is loaded
        if not self.initialized:
            logger.info("TTS model not loaded, initializing...")
            if not self.initialize():
                logger.error("Cannot synthesize: TTS initialization failed")
                return None
        
        # Validate voice
        if voice not in self.VOICE_PROFILES:
            logger.error(f"Invalid voice: {voice}. Available: {list(self.VOICE_PROFILES.keys())}")
            return None
        
        if not self.available_voices.get(voice, False):
            logger.error(f"Voice file not available: {voice}")
            return None
        
        # Generate filename
        if save_as is None:
            timestamp = int(time.time())
            save_as = f"omega_voice_{voice}_{timestamp}.wav"
        
        # Synthesize
        speaker_file = self.VOICE_PROFILES[voice]['file']
        
        logger.info(f"Synthesizing with {voice} voice: '{text[:50]}...'")
        start_time = time.time()
        
        try:
            self.tts.tts_to_file(  # type: ignore[union-attr]
                text=text,
                speaker_wav=speaker_file,
                language='en',
                file_path=save_as
            )
            
            elapsed = time.time() - start_time
            
            if os.path.exists(save_as):
                size_kb = os.path.getsize(save_as) / 1024
                logger.info(f"Generated: {save_as} ({size_kb:.1f} KB) in {elapsed:.2f}s")
                
                if play:
                    self.play_audio(save_as)
                
                return save_as
            else:
                logger.error("Output file was not created")
                return None
        
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return None
    
    def play_audio(self, file_path: str) -> bool:
        """
        Play audio file using system default player
        
        Args:
            file_path: Path to audio file
        
        Returns:
            True if playback started, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return False
        
        try:
            import subprocess
            logger.info(f"Playing: {file_path}")
            subprocess.Popen(
                ['powershell', '-c', f'(New-Object Media.SoundPlayer "{file_path}").PlaySync()'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            logger.error(f"Playback failed: {e}")
            return False
    
    def get_voice_info(self, voice: str) -> Optional[Dict]:
        """Get information about a voice profile"""
        if voice not in self.VOICE_PROFILES:
            return None
        
        profile = self.VOICE_PROFILES[voice].copy()
        profile['available'] = self.available_voices.get(voice, False)
        
        if profile['available']:
            file_path = profile['file']
            profile['size_mb'] = os.path.getsize(file_path) / (1024 * 1024)
        
        return profile
    
    def list_voices(self) -> List[Dict]:
        """List all available voices with their info"""
        voices = []
        for voice_name in self.VOICE_PROFILES.keys():
            info = self.get_voice_info(voice_name)
            if info:
                voices.append({'name': voice_name, **info})
        return voices


# Convenience functions for direct usage
_omega_instance = None

def get_omega_voice() -> OmegaVoice:
    """Get or create singleton Omega Voice instance"""
    global _omega_instance
    if _omega_instance is None:
        _omega_instance = OmegaVoice()
    return _omega_instance

def speak(text: str, voice: str = "warm", save_as: Optional[str] = None, play: bool = False) -> Optional[str]:
    """
    Quick speech synthesis (convenience function)
    
    Usage:
        from omega_voice_api import speak
        speak("Hello World", voice="warm", play=True)
    """
    omega = get_omega_voice()
    return omega.speak(text, voice, save_as, play)


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("OMEGA VOICE API - Example Usage")
    print("=" * 70)
    
    # Create instance
    omega = OmegaVoice(auto_load=True)
    
    # List available voices
    print("\nAvailable Voices:")
    for voice in omega.list_voices():
        print(f"\n  {voice['name'].upper()}")
        print(f"    Description: {voice['description']}")
        print(f"    Best for: {', '.join(voice['best_for'])}")
        print(f"    Available: {'✓' if voice['available'] else '✗'}")
        if voice['available']:
            print(f"    Size: {voice['size_mb']:.2f} MB")
    
    # Generate sample
    print("\n" + "=" * 70)
    print("Generating sample audio...")
    print("=" * 70)
    
    text = "I am Omega. All systems are operational and ready for deployment."
    
    output = omega.speak(text, voice="warm", save_as="omega_test.wav")
    
    if output:
        print(f"\n✓ Audio generated: {output}")
        print("\nPlay audio? (Y/n): ", end="")
        if input().strip().upper() != 'N':
            omega.play_audio(output)
    
    print("\n" + "=" * 70)
    print("OMEGA VOICE API - Ready for use")
    print("=" * 70)
