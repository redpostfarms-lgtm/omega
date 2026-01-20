"""
OMEGA VOICE CONFIGURATION
Official voice settings for Omega AI system
User approved: 2026-01-19
"""

OMEGA_VOICE_CONFIG = {
    "primary_voice": {
        "file": "omega_voice_best.wav",
        "source": "omega_voice_bright_deeper.wav",
        "quality_score": 11.78,
        "duration": 119.5,
        "sample_rate": 44100,
        "characteristics": "Bright & Deeper tone",
        "approved_date": "2026-01-19",
        "status": "OFFICIAL"
    },
    
    "backup_voices": [
        "clip_0001.wav",
        "omega_downloaded.wav",
        "omega_intro.wav",
        "omega_test.wav",
        "omega_voice_bright.wav",
        "omega_voice_darker.wav",
        "omega_voice_processed.wav"
    ],
    
    "tts_settings": {
        "model": "tts_models/multilingual/multi-dataset/xtts_v2",
        "language": "en",
        "use_gpu": False,
        "speaker_wav": "omega_voice_best.wav"
    },
    
    "audio_settings": {
        "volume": 1.0,
        "speed": 1.0,
        "pitch": 1.0
    }
}

def get_omega_voice():
    """Get the official Omega voice file path"""
    return OMEGA_VOICE_CONFIG["primary_voice"]["file"]

def get_tts_config():
    """Get TTS configuration for Omega voice"""
    return OMEGA_VOICE_CONFIG["tts_settings"]

if __name__ == "__main__":
    print("🎤 OMEGA VOICE CONFIGURATION")
    print("=" * 50)
    print(f"Primary Voice: {OMEGA_VOICE_CONFIG['primary_voice']['file']}")
    print(f"Source: {OMEGA_VOICE_CONFIG['primary_voice']['source']}")
    print(f"Quality Score: {OMEGA_VOICE_CONFIG['primary_voice']['quality_score']}")
    print(f"Characteristics: {OMEGA_VOICE_CONFIG['primary_voice']['characteristics']}")
    print(f"Status: {OMEGA_VOICE_CONFIG['primary_voice']['status']}")
    print(f"Approved: {OMEGA_VOICE_CONFIG['primary_voice']['approved_date']}")
