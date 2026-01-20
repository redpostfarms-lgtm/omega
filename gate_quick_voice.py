"""
GATE - Quick KITT Voice Test
Just play the KITT voice directly, then switch to conversation mode
"""
import subprocess
from pathlib import Path

kitt_voice = Path("H:/The Gatekeeper/static/audio/kitt_voice.wav")

print("\n" + "="*70)
print("🚪 GATE - Quick Voice Test")
print("="*70 + "\n")

if kitt_voice.exists():
    print(f"✅ KITT voice found: {kitt_voice}")
    print(f"📢 Playing KITT voice sample...\n")
    
    # Play the voice file directly
    subprocess.run([
        "powershell", "-c",
        f'$player = New-Object System.Media.SoundPlayer("{kitt_voice}"); $player.PlaySync()'
    ])
    
    print("\n✅ Playback complete!")
    print("\nTo enable full conversation mode with voice cloning,")
    print("run: gate_voice_system.py\n")
else:
    print(f"❌ KITT voice not found at: {kitt_voice}\n")
