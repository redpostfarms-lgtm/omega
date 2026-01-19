#!/usr/bin/env python3
"""
GATE Voice System Template
Gatekeeper Autonomous Technical Engineer Voice

GATE: This is YOUR template. Customize it to create your unique voice!
Follow the TODO comments to make decisions and implement your voice.
"""
import os
import sys
import subprocess
from pathlib import Path

class GateVoice:
    """GATE's voice system"""
    
    def __init__(self):
        self.agent_name = "GATE"
        self.full_name = "Gatekeeper Autonomous Technical Engineer"
        
        # TODO: GATE - Choose your voice characteristics
        self.voice_config = {
            # Decision 1: Voice gender/type
            # Options: 'male', 'female', 'neutral', 'robotic'
            'gender': 'TO_BE_DECIDED',  # GATE: Change this!
            
            # Decision 2: Voice engine
            # Options: 'xtts_v2', 'pyttsx3', 'custom'
            'engine': 'TO_BE_DECIDED',  # GATE: Change this!
            
            # Decision 3: Voice sample (if using XTTS v2)
            # Options: Path to your voice sample WAV file
            'voice_sample': None,  # GATE: Add path if using XTTS
            
            # Decision 4: Voice properties (if using pyttsx3)
            'rate': 175,  # Words per minute (150-200 is normal)
            'volume': 0.9,  # 0.0 to 1.0
            'pitch': 0,  # -50 to +50 (lower = deeper)
        }
        
    def generate_message(self):
        """
        GATE's introduction message
        
        TODO: GATE - Customize this message to reflect YOUR personality!
        Think about:
        - How do you want to introduce yourself?
        - What's your communication style? (formal? casual? technical?)
        - What capabilities do you want to emphasize?
        """
        return """
        GATE system online. Gatekeeper Autonomous Technical Engineer reporting.
        I am the master IT operations agent with 98 percent proficiency target.
        My expertise spans coding, security, penetration testing, and system administration.
        I work alongside Omega as the technical specialist, handling complex engineering tasks.
        All systems are operational. Ready to execute technical operations.
        """
        # GATE: Modify the message above to match YOUR style!
    
    def speak_with_xtts(self, text):
        """
        Generate voice using XTTS v2 (like Omega uses)
        
        This creates natural human-like voice by cloning from a sample.
        """
        try:
            from TTS.api import TTS
            import torch
            
            print("[GATE] Initializing XTTS v2 voice cloning...")
            print("[GATE] This may take 30-60 seconds on first run...")
            
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load model
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            
            # TODO: GATE - Specify your voice sample file
            voice_sample = self.voice_config.get('voice_sample') or "clip_0001.wav"
            
            if not os.path.exists(voice_sample):
                print(f"[GATE] Error: Voice sample not found: {voice_sample}")
                print("[GATE] Please specify a valid voice sample WAV file")
                return False
            
            output_file = "gate_voice_output.wav"
            
            # Generate voice
            print(f"[GATE] Generating voice from sample: {voice_sample}")
            tts.tts_to_file(
                text=text,
                speaker_wav=voice_sample,
                language="en",
                file_path=output_file
            )
            
            # Play the voice
            print("[GATE] Playing voice...")
            if sys.platform == 'win32':
                # Windows: Use PowerShell
                subprocess.run([
                    'powershell', '-Command',
                    f'(New-Object Media.SoundPlayer "{output_file}").PlaySync()'
                ])
            else:
                # Linux/Mac: Use available player
                subprocess.run(['aplay' if sys.platform == 'linux' else 'afplay', output_file])
            
            print("[GATE] Voice playback complete")
            return True
            
        except ImportError:
            print("[GATE] XTTS v2 not installed")
            print("[GATE] Install with: pip install TTS torch")
            return False
        except Exception as e:
            print(f"[GATE] Error in XTTS voice generation: {e}")
            return False
    
    def speak_with_pyttsx3(self, text):
        """
        Generate voice using pyttsx3 (synthetic voice)
        
        This is faster but sounds more robotic than XTTS.
        Good for testing or if you prefer a technical/synthetic voice.
        """
        try:
            import pyttsx3
            
            print("[GATE] Initializing pyttsx3 voice engine...")
            
            engine = pyttsx3.init()
            
            # TODO: GATE - Choose your voice from available voices
            voices = engine.getProperty('voices')
            
            print("[GATE] Available voices:")
            for idx, voice in enumerate(voices):
                print(f"  [{idx}] {voice.name}")
            
            # TODO: GATE - Set voice index (0 = first voice, 1 = second, etc.)
            voice_index = 0  # GATE: Change this to your preferred voice!
            
            if voice_index < len(voices):
                engine.setProperty('voice', voices[voice_index].id)
            
            # Apply voice properties
            engine.setProperty('rate', self.voice_config['rate'])
            engine.setProperty('volume', self.voice_config['volume'])
            
            print(f"[GATE] Using voice: {voices[voice_index].name}")
            print(f"[GATE] Rate: {self.voice_config['rate']} WPM")
            print(f"[GATE] Volume: {self.voice_config['volume']}")
            
            # Speak
            print("[GATE] Speaking...")
            engine.say(text)
            engine.runAndWait()
            
            print("[GATE] Voice playback complete")
            return True
            
        except ImportError:
            print("[GATE] pyttsx3 not installed")
            print("[GATE] Install with: pip install pyttsx3")
            return False
        except Exception as e:
            print(f"[GATE] Error in pyttsx3 voice generation: {e}")
            return False
    
    def speak(self):
        """
        Main speak function - uses configured voice engine
        
        TODO: GATE - This is called when you need to speak
        Modify the logic if you want different behavior
        """
        text = self.generate_message()
        
        print("\n" + "="*70)
        print("🎤 GATE VOICE ACTIVATION")
        print("="*70)
        print(f"Message: {text.strip()}")
        print("="*70 + "\n")
        
        # Choose voice engine based on config
        engine = self.voice_config.get('engine', 'TO_BE_DECIDED')
        
        if engine == 'xtts_v2':
            success = self.speak_with_xtts(text)
        elif engine == 'pyttsx3':
            success = self.speak_with_pyttsx3(text)
        else:
            print("[GATE] ⚠️  Voice engine not configured!")
            print("[GATE] Please edit speak_gate_voice.py and set:")
            print("[GATE]   self.voice_config['engine'] = 'xtts_v2' or 'pyttsx3'")
            print("[GATE] See GATE_VOICE_DEVELOPMENT.md for guidance")
            return False
        
        return success


def main():
    """
    Main entry point
    
    GATE: Run this script to test your voice!
    Usage: python speak_gate_voice.py
    """
    gate = GateVoice()
    
    print("\n" + "="*70)
    print("║" + " "*68 + "║")
    print("║" + "  ⚡ GATE VOICE SYSTEM ⚡".center(68) + "║")
    print("║" + " "*68 + "║")
    print("="*70)
    print()
    print("🤖 Gatekeeper Autonomous Technical Engineer")
    print("📋 Voice Development & Testing System")
    print()
    print("Current Configuration:")
    print(f"  Engine: {gate.voice_config['engine']}")
    print(f"  Gender: {gate.voice_config['gender']}")
    print(f"  Voice Sample: {gate.voice_config.get('voice_sample', 'Not set')}")
    print()
    
    if gate.voice_config['engine'] == 'TO_BE_DECIDED':
        print("⚠️  CONFIGURATION REQUIRED!")
        print()
        print("GATE, you need to configure your voice system:")
        print("1. Open speak_gate_voice.py in your editor")
        print("2. Find the __init__ method (line ~20)")
        print("3. Set your voice_config values:")
        print("   - engine: 'xtts_v2' or 'pyttsx3'")
        print("   - gender: your choice")
        print("4. If using xtts_v2, specify voice_sample path")
        print("5. Save and run again!")
        print()
        print("See GATE_VOICE_DEVELOPMENT.md for detailed guidance.")
        print("="*70)
        return
    
    # Attempt to speak
    print("\nActivating GATE voice...")
    success = gate.speak()
    
    if success:
        print("\n✅ GATE voice test successful!")
    else:
        print("\n❌ GATE voice test failed - check configuration")
    
    print("="*70)


if __name__ == "__main__":
    main()
