// Auto-generated voice configuration
// DO NOT EDIT MANUALLY - Generated from voice_registry.py

export const AZZ_VOICE_PATH = "H:/The Gatekeeper/voices/azz";
export const AZZ_VOICE_SAMPLE = "H:/The Gatekeeper/voices/azz/azz.wav";

export interface VoiceProfile {
    name: string;
    description: string;
    path: string;
    sample: string;
    enabled: boolean;
    backend: string;
    azureVoice: string;
    features: {
        pitch: string;
        rate: number;
        volume: number;
    };
    useCases: string[];
}

export const VOICE_PROFILES: Record<string, VoiceProfile> = {
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
};

export const VOICE_ROUTING: Record<string, string> = {
    "azure": "azz",
    "omega": "azz",
    "default": "azz"
};

export const DEFAULT_VOICE = "azz";

export function getVoiceForContext(context: string): string {
    return VOICE_ROUTING[context] || DEFAULT_VOICE;
}

export function getVoiceProfile(name: string): VoiceProfile | null {
    return VOICE_PROFILES[name] || null;
}
