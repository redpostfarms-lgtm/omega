"""
Auto-generated voice configuration
DO NOT EDIT MANUALLY - Generated from voice_registry.py
"""

from pathlib import Path
from typing import Dict, Optional

# Voice paths
AZZ_VOICE_PATH = Path("H:/The Gatekeeper/voices/azz")
AZZ_VOICE_SAMPLE = Path("H:/The Gatekeeper/voices/azz/azz.wav")

# Voice profiles
VOICE_PROFILES: Dict[str, dict] = {
    "azz": {
        "name": "AZZ",
        "description": "Primary voice profile for Omega system",
        "path": "H:\\The Gatekeeper\\voices\\azz",
        "sample": "H:\\The Gatekeeper\\voices\\azz\\azz.wav",
        "enabled": true,
        "backend": "azure",
        "azure_voice": "en-US-AvaMultilingualNeural",
        "features": {
            "pitch": "medium",
            "rate": 1.0,
            "volume": 1.0,
            "emotion": "neutral"
        },
        "use_cases": [
            "azure",
            "omega",
            "general"
        ]
    }
}

# Routing rules
VOICE_ROUTING: Dict[str, str] = {
    "azure": "azz",
    "omega": "azz",
    "default": "azz"
}

# Default voice
DEFAULT_VOICE = "azz"


def get_voice_for_context(context: str) -> str:
    """Get appropriate voice for context"""
    return VOICE_ROUTING.get(context, DEFAULT_VOICE)


def get_voice_profile(name: str) -> Optional[dict]:
    """Get voice profile by name"""
    return VOICE_PROFILES.get(name)


def get_voice_sample_path(name: str) -> Optional[Path]:
    """Get voice sample path"""
    profile = get_voice_profile(name)
    if profile:
        return Path(profile["sample"])
    return None
