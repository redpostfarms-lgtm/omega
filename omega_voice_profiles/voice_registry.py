#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Voice Registry System
Multi-voice support with routing and selection logic
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

# Voice profile paths
VOICE_PROFILES_PATH = Path("H:/The Gatekeeper/voices")
AZZ_VOICE_PATH = VOICE_PROFILES_PATH / "azz"
AZZ_VOICE_SAMPLE = AZZ_VOICE_PATH / "azz.wav"


class VoiceRegistry:
    """
    Multi-voice registry and routing system
    Manages all voice profiles for Omega
    """

    def __init__(self):
        self.profiles_path = VOICE_PROFILES_PATH
        self.profiles_path.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.profiles_path / "voice_registry.json"
        self.registry = self.load_registry()

    def load_registry(self) -> Dict:
        """Load voice registry"""
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)

        # Default registry
        return {
            "version": "1.0.0",
            "default_voice": "azz",
            "voices": {
                "azz": {
                    "name": "AZZ",
                    "description": "Primary voice profile for Omega system",
                    "path": str(AZZ_VOICE_PATH),
                    "sample": str(AZZ_VOICE_SAMPLE),
                    "enabled": True,
                    "backend": "azure",
                    "azure_voice": "en-US-AvaMultilingualNeural",
                    "features": {
                        "pitch": "medium",
                        "rate": 1.0,
                        "volume": 1.0,
                        "emotion": "neutral"
                    },
                    "use_cases": ["azure", "omega", "general"]
                }
            },
            "routing_rules": {
                "azure": "azz",
                "omega": "azz",
                "default": "azz"
            }
        }

    def save_registry(self):
        """Save voice registry"""
        with open(self.registry_file, "w") as f:
            json.dump(self.registry, f, indent=2)

    def register_voice(
        self,
        name: str,
        path: Path,
        backend: str = "azure",
        **kwargs
    ) -> bool:
        """Register a new voice profile"""
        if name in self.registry["voices"]:
            print(f"Voice '{name}' already registered")
            return False

        self.registry["voices"][name] = {
            "name": name.upper(),
            "description": kwargs.get("description", f"{name} voice profile"),
            "path": str(path),
            "sample": str(path / f"{name}.wav"),
            "enabled": kwargs.get("enabled", True),
            "backend": backend,
            "azure_voice": kwargs.get("azure_voice", "en-US-AriaNeural"),
            "features": kwargs.get("features", {
                "pitch": "medium",
                "rate": 1.0,
                "volume": 1.0
            }),
            "use_cases": kwargs.get("use_cases", ["general"])
        }

        self.save_registry()
        print(f"✓ Registered voice: {name}")
        return True

    def get_voice(self, name: str) -> Optional[Dict]:
        """Get voice profile by name"""
        return self.registry["voices"].get(name)

    def list_voices(self) -> List[str]:
        """List all registered voices"""
        return list(self.registry["voices"].keys())

    def get_voice_for_context(self, context: str) -> str:
        """Get appropriate voice for context"""
        # Check routing rules
        voice = self.registry["routing_rules"].get(context)

        if voice and voice in self.registry["voices"]:
            return voice

        # Check use cases
        for voice_name, profile in self.registry["voices"].items():
            if context in profile.get("use_cases", []):
                return voice_name

        # Return default
        return self.registry["default_voice"]

    def set_default_voice(self, name: str) -> bool:
        """Set default voice"""
        if name not in self.registry["voices"]:
            print(f"Voice '{name}' not registered")
            return False

        self.registry["default_voice"] = name
        self.save_registry()
        print(f"✓ Default voice set to: {name}")
        return True

    def add_routing_rule(self, context: str, voice: str) -> bool:
        """Add routing rule for context"""
        if voice not in self.registry["voices"]:
            print(f"Voice '{voice}' not registered")
            return False

        self.registry["routing_rules"][context] = voice
        self.save_registry()
        print(f"✓ Routing rule: {context} → {voice}")
        return True

    def get_voice_config_for_omega(self) -> Dict:
        """Get voice configuration for Omega system"""
        return {
            "AZZ_VOICE_PATH": str(AZZ_VOICE_PATH),
            "AZZ_VOICE_SAMPLE": str(AZZ_VOICE_SAMPLE),
            "DEFAULT_VOICE": self.registry["default_voice"],
            "VOICES": self.registry["voices"],
            "ROUTING": self.registry["routing_rules"]
        }

    def export_typescript_config(self, output_path: Path):
        """Export configuration for TypeScript"""
        config = self.get_voice_config_for_omega()

        ts_content = f"""// Auto-generated voice configuration
// DO NOT EDIT MANUALLY - Generated from voice_registry.py

export const AZZ_VOICE_PATH = "{AZZ_VOICE_PATH.as_posix()}";
export const AZZ_VOICE_SAMPLE = "{AZZ_VOICE_SAMPLE.as_posix()}";

export interface VoiceProfile {{
    name: string;
    description: string;
    path: string;
    sample: string;
    enabled: boolean;
    backend: string;
    azureVoice: string;
    features: {{
        pitch: string;
        rate: number;
        volume: number;
    }};
    useCases: string[];
}}

export const VOICE_PROFILES: Record<string, VoiceProfile> = {json.dumps(config['VOICES'], indent=4)};

export const VOICE_ROUTING: Record<string, string> = {json.dumps(config['ROUTING'], indent=4)};

export const DEFAULT_VOICE = "{config['DEFAULT_VOICE']}";

export function getVoiceForContext(context: string): string {{
    return VOICE_ROUTING[context] || DEFAULT_VOICE;
}}

export function getVoiceProfile(name: string): VoiceProfile | null {{
    return VOICE_PROFILES[name] || null;
}}
"""

        with open(output_path, "w") as f:
            f.write(ts_content)

        print(f"✓ TypeScript config exported to: {output_path}")

    def export_python_config(self, output_path: Path):
        """Export configuration for Python"""
        config = self.get_voice_config_for_omega()

        py_content = f'''"""
Auto-generated voice configuration
DO NOT EDIT MANUALLY - Generated from voice_registry.py
"""

from pathlib import Path
from typing import Dict, Optional

# Voice paths
AZZ_VOICE_PATH = Path("{str(AZZ_VOICE_PATH).replace(chr(92), '/')}")
AZZ_VOICE_SAMPLE = Path("{str(AZZ_VOICE_SAMPLE).replace(chr(92), '/')}")

# Voice profiles
VOICE_PROFILES: Dict[str, dict] = {json.dumps(config['VOICES'], indent=4)}

# Routing rules
VOICE_ROUTING: Dict[str, str] = {json.dumps(config['ROUTING'], indent=4)}

# Default voice
DEFAULT_VOICE = "{config['DEFAULT_VOICE']}"


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
'''

        with open(output_path, "w") as f:
            f.write(py_content)

        print(f"✓ Python config exported to: {output_path}")


# Global registry instance
voice_registry = VoiceRegistry()


def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  OMEGA VOICE REGISTRY")
    print("=" * 70 + "\n")

    registry = VoiceRegistry()

    print("Current Voice Registry:")
    print(f"  Default voice: {registry.registry['default_voice']}")
    print(f"  Registered voices: {len(registry.registry['voices'])}")

    for name, profile in registry.registry["voices"].items():
        status = "✓" if profile["enabled"] else "✗"
        print(f"\n  {status} {profile['name']}")
        print(f"     Path: {profile['path']}")
        print(f"     Backend: {profile['backend']}")
        print(f"     Use cases: {', '.join(profile['use_cases'])}")

    print("\nRouting Rules:")
    for context, voice in registry.registry["routing_rules"].items():
        print(f"  {context} → {voice}")

    # Save registry
    registry.save_registry()

    # Export configs
    print("\nExporting configurations...")

    # Python config
    py_config_path = Path(__file__).parent / "omega_voice_config.py"
    registry.export_python_config(py_config_path)

    # TypeScript config
    ts_config_path = Path(__file__).parent / "omega_voice_config.ts"
    registry.export_typescript_config(ts_config_path)

    print("\n" + "=" * 70)
    print("  VOICE REGISTRY SAVED")
    print("=" * 70)
    print(f"\nRegistry file: {registry.registry_file}")
    print(f"Python config: {py_config_path}")
    print(f"TypeScript config: {ts_config_path}")
    print("\nAll voice operations will now use the AZZ profile.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
