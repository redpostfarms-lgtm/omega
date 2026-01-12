#!/usr/bin/env python3
# Manage Authorized Voices - Add/remove authorized speakers
from voice_security_system import voice_security
from pathlib import Path
import sys

def list_authorized_voices():
    """List all authorized voices."""
    voices = voice_security.authorized_voices
    if not voices:
        print("\n[No authorized voices registered]")
        return
    
    print("\n" + "=" * 70)
    print("  AUTHORIZED VOICES")
    print("=" * 70)
    for voice_id, voice_data in voices.items():
        print(f"\nVoice ID: {voice_id[:16]}...")
        print(f"  Name: {voice_data.get('name', 'Unknown')}")
        print(f"  Created: {voice_data.get('created', 'Unknown')}")
        print(f"  Pitch: {voice_data['features'].get('pitch', {}).get('mean', 0):.1f} Hz")

def add_authorized_voice(audio_file, name):
    """Add a new authorized voice."""
    if not Path(audio_file).exists():
        print(f"[ERROR] Audio file not found: {audio_file}")
        return False
    
    print(f"\n[Registering authorized voice: {name}]")
    print(f"Source: {audio_file}")
    
    if voice_security.register_authorized_voice(audio_file, name):
        print(f"[SUCCESS] Voice registered successfully!")
        return True
    else:
        print(f"[ERROR] Failed to register voice")
        return False

def remove_authorized_voice(voice_id):
    """Remove an authorized voice."""
    if voice_id in voice_security.authorized_voices:
        name = voice_security.authorized_voices[voice_id].get('name', 'Unknown')
        del voice_security.authorized_voices[voice_id]
        voice_security.save_authorized_voices()
        print(f"[SUCCESS] Removed authorized voice: {name}")
        return True
    else:
        print(f"[ERROR] Voice ID not found: {voice_id}")
        return False

def update_threshold(new_threshold):
    """Update the lock-on threshold (0.0 to 1.0)."""
    if 0.0 <= new_threshold <= 1.0:
        voice_security.lock_on_threshold = new_threshold
        print(f"[SUCCESS] Lock-on threshold updated to {new_threshold*100:.0f}%")
        return True
    else:
        print(f"[ERROR] Threshold must be between 0.0 and 1.0")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("  AUTHORIZED VOICE MANAGER")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_authorized_voices()
        elif command == 'add' and len(sys.argv) >= 4:
            add_authorized_voice(sys.argv[2], sys.argv[3])
        elif command == 'remove' and len(sys.argv) >= 3:
            remove_authorized_voice(sys.argv[2])
        elif command == 'threshold' and len(sys.argv) >= 3:
            update_threshold(float(sys.argv[2]))
        else:
            print("\nUsage:")
            print("  python manage_authorized_voices.py list")
            print("  python manage_authorized_voices.py add <audio_file.wav> <name>")
            print("  python manage_authorized_voices.py remove <voice_id>")
            print("  python manage_authorized_voices.py threshold <0.0-1.0>")
    else:
        # Interactive mode
        list_authorized_voices()
        print("\n[SECURITY STATUS]")
        status = voice_security.get_security_status()
        for key, value in status.items():
            print(f"  {key}: {value}")
