"""
GATE Voice System with KITT Voice Integration
Uses kitt_voice.wav for voice cloning and conversational speech
"""
import os
import sys
from pathlib import Path
from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import numpy as np
from scipy import signal

class GateVoiceSystem:
    """Gate's conversational voice system using KITT voice"""
    
    def __init__(self):
        self.agent_name = "GATE"
        self.full_name = "Gatekeeper Autonomous Technical Engineer"
        
        # KITT voice file path
        self.kitt_voice_path = Path("H:/The Gatekeeper/static/audio/kitt_voice.wav")
        
        # TTS model for voice cloning
        self.tts = None
        self.model_loaded = False

        # Voice settings
        self.pitch_shift = 0.25  # Semitones higher

        print(f"\n{'='*70}")
        print(f"🚪 {self.agent_name} - {self.full_name}")
        print(f"🎤 Voice: KITT (kitt_voice.wav)")
        print(f"{'='*70}\n")
        
    def initialize_tts(self):
        """Initialize TTS model for voice cloning"""
        if self.model_loaded:
            return True
            
        print("🔄 Loading TTS model for KITT voice cloning...")
        
        try:
            # Load XTTS v2 model for voice cloning
            self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False)
            self.model_loaded = True
            print("✅ TTS model loaded successfully\n")
            return True
        except Exception as e:
            print(f"❌ Error loading TTS model: {e}\n")
            return False
    
    def check_kitt_voice(self):
        """Verify KITT voice file exists"""
        if self.kitt_voice_path.exists():
            size_mb = self.kitt_voice_path.stat().st_size / (1024 * 1024)
            print(f"✅ KITT Voice Available")
            print(f"   File: {self.kitt_voice_path}")
            print(f"   Size: {size_mb:.2f} MB\n")
            return True
        else:
            print(f"❌ KITT voice file not found!")
            print(f"   Expected: {self.kitt_voice_path}\n")
            return False
    
    def speak(self, text, save_to=None):
        """
        Generate speech using KITT voice and speak it
        
        Args:
            text: Text to speak
            save_to: Optional path to save audio file
        """
        if not self.check_kitt_voice():
            print("⚠️ Cannot speak without KITT voice file\n")
            return False
        
        if not self.model_loaded:
            if not self.initialize_tts():
                return False
        
        print(f"\n🔊 Gate speaking: \"{text[:50]}{'...' if len(text) > 50 else ''}\"\n")
        
        try:
            # Generate speech using KITT voice
            output_path = save_to or "gate_speech_output.wav"
            
            self.tts.tts_to_file(
                text=text,
                speaker_wav=str(self.kitt_voice_path),
                language="en",
                file_path=output_path
            )

            # Load and adjust pitch
            data, samplerate = sf.read(output_path)

            # Apply pitch shift (+0.25 semitones = slightly higher pitch)
            pitch_factor = 2 ** (self.pitch_shift / 12.0)
            new_length = int(len(data) / pitch_factor)

            # Resample to shift pitch
            if len(data.shape) == 1:  # Mono
                data_shifted = signal.resample(data, new_length)
            else:  # Stereo
                data_shifted = np.zeros((new_length, data.shape[1]))
                for channel in range(data.shape[1]):
                    data_shifted[:, channel] = signal.resample(data[:, channel], new_length)

            # Time-stretch back to original duration to maintain speed
            data_final = signal.resample(data_shifted, len(data))

            # Play the adjusted speech
            print("▶️ Playing audio (pitch +0.25)...")
            sd.play(data_final, samplerate)
            sd.wait()
            
            print("✅ Speech completed\n")
            return True
            
        except Exception as e:
            print(f"❌ Error generating speech: {e}\n")
            return False
    
    def interactive_mode(self):
        """Interactive conversation mode with Gate"""
        print("\n" + "="*70)
        print("🗣️  GATE INTERACTIVE MODE")
        print("Type your message and Gate will respond with KITT voice")
        print("Commands: 'exit' or 'quit' to stop")
        print("="*70 + "\n")
        
        # Initialize TTS
        if not self.initialize_tts():
            print("Cannot start interactive mode without TTS\n")
            return

        # Initial greeting (shorter for faster processing)
        greeting = "Hello. I am Gate. All systems online. How may I assist you?"
        
        self.speak(greeting)
        
        # Conversation loop
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'goodbye']:
                    farewell = "Understood. GATE signing off. All systems secured."
                    self.speak(farewell)
                    print("\n🔒 Gate has been deactivated\n")
                    break
                
                # Gate's response (you can customize responses here)
                response = self.generate_response(user_input)
                self.speak(response)
                
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                break
    
    def generate_response(self, user_input):
        """
        Generate Gate's response based on user input
        You can customize this for different conversation patterns
        """
        # Simple response logic (can be enhanced with AI/LLM later)
        user_lower = user_input.lower()
        
        if "status" in user_lower or "report" in user_lower:
            return "All systems operational. Security protocols active. No threats detected."
        
        elif "hello" in user_lower or "hi" in user_lower:
            return "Greetings. I am Gate. How may I assist you with system security?"
        
        elif "who are you" in user_lower:
            return f"I am {self.agent_name}, the {self.full_name}. I work alongside Omega to secure and protect this system."
        
        elif "thank" in user_lower:
            return "You are welcome. I am here to serve and protect."
        
        elif "help" in user_lower:
            return "I can assist with system security, access control, and threat monitoring. What do you need?"
        
        else:
            return f"Acknowledged. Processing your request: {user_input[:30]}"


def main():
    """Main entry point for Gate voice system"""
    gate = GateVoiceSystem()
    
    # Check KITT voice availability
    if not gate.check_kitt_voice():
        print("⚠️ Cannot proceed without KITT voice file\n")
        return
    
    # Automatically start interactive conversation mode
    print("🚀 Starting interactive conversation mode...\n")
    gate.interactive_mode()


if __name__ == "__main__":
    main()
