"""
GATE VOICE CONFIGURATION
Official KITT voice for Gate AI system
"""

GATE_VOICE_CONFIG = {
    "primary_voice": {
        "file": "gate_kitt_voice.wav",
        "source": "KIT1.wav (authentic Knight Rider KITT)",
        "approved_date": "2026-01-19",
        "status": "OFFICIAL"
    },

    "voice_characteristics": {
        "source": "Knight Rider KITT (William Daniels)",
        "style": "Precise, technical, authoritative",
        "personality": "Professional security AI"
    },

    "tts_settings": {
        "model": "tts_models/multilingual/multi-dataset/xtts_v2",
        "language": "en",
        "use_gpu": False,
        "speaker_wav": "gate_kitt_voice.wav"
    }
}

def get_gate_voice():
    """Get Gate's official KITT voice file"""
    return GATE_VOICE_CONFIG["primary_voice"]["file"]

if __name__ == "__main__":
    print("\n🚪 GATE VOICE CONFIGURATION")
    print("=" * 50)
    print(f"Voice File: {GATE_VOICE_CONFIG['primary_voice']['file']}")
    print(f"Source: {GATE_VOICE_CONFIG['primary_voice']['source']}")
    print(f"Status: {GATE_VOICE_CONFIG['primary_voice']['status']}")
    print(f"Approved: {GATE_VOICE_CONFIG['primary_voice']['approved_date']}")
    print()
