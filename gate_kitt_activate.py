"""
GATE - KITT Voice Activation
Gate speaks with the KITT voice (clip_0001.wav)
"""
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gate_kit_voice import GateKitVoice

def main():
    """Activate Gate with KITT voice"""
    
    print("\n" + "="*70)
    print("🚪 GATE - GATEKEEPER AUTONOMOUS TECHNICAL ENGINEER")
    print("🎤 Voice System: KITT (clip_0001.wav)")
    print("="*70 + "\n")
    
    # Initialize Gate's Kit voice
    gate = GateKitVoice()
    
    # Gate's introduction with KITT voice
    gate_intro = """Hello. I am Gate, the Gatekeeper Autonomous Technical Engineer.
    
My primary function is system security and access control.
I work alongside Omega to protect and manage this system.

My voice signature is based on the Knight Industries Two Thousand interface.
All systems are secured. Standing by for commands."""
    
    print("\n🔊 Activating Gate's KITT voice system...\n")
    
    # Check voice availability
    if gate.check_kit_voice():
        # Play Gate's voice with KITT style
        success = gate.play_kit_voice(gate_intro)
        
        if success:
            print("\n✅ Gate voice system online")
            print("🔒 Security protocols active")
            print("🎯 Ready for duty\n")
        else:
            print("\n⚠️ Voice playback encountered an issue\n")
    else:
        print("\n❌ KITT voice file not found\n")
        print("Expected location: clip_0001.wav")
        print("Please ensure the voice file is in the current directory.\n")

if __name__ == "__main__":
    main()
