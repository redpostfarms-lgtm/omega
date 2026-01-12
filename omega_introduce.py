#!/usr/bin/env python3
# Omega Introduction - Quick introduction and start
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from omega_full_brain import get_tts, play_audio_background
from voice_security_system import voice_security

async def omega_introduce():
    print("\n" + "=" * 70)
    print("  OMEGA - INTRODUCTION")
    print("=" * 70 + "\n")
    
    print("[Loading Omega...]")
    tts = get_tts()
    print("[OK] Omega ready!\n")
    
    # Check security status
    security_status = voice_security.get_security_status()
    
    # Simple, natural introduction
    introduction = """Hello, I am Omega. I'm ready to have a conversation with you. Just speak naturally, and I'll listen and respond. Let's begin."""
    
    print("[Omega Introduction]")
    print(introduction.replace('\n    ', ' ').strip() + "\n")
    
    print("[Generating introduction audio...]")
    tts.tts_to_file(
        text=introduction,
        speaker_wav='clip_0001.wav' if Path('clip_0001.wav').exists() else None,
        language='en',
        file_path='omega_intro.wav'
    )
    
    print("[Playing introduction in background...]")
    play_audio_background('omega_intro.wav')
    
    # Wait for audio to play
    await asyncio.sleep(20)
    
    print("\n[OK] Introduction complete!")
    print("\n[Omega is now ready for hands-free conversation]")
    print("[Starting conversation mode...]\n")
    
    # Now start the full conversation
    from hands_free_omega import hands_free_conversation
    await hands_free_conversation()

if __name__ == "__main__":
    try:
        asyncio.run(omega_introduce())
    except KeyboardInterrupt:
        print("\n\n[Omega conversation ended. Thank you!]")
