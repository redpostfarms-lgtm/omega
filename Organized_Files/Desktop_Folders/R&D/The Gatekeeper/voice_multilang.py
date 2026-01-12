# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# TRADEMARK NOTICE: "Omega" and "Ω" are trademarks of Red Post Farms, LLC.
#
"""
Multi-Language Voice System
Support for multiple languages in voice commands.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, Optional

BRAIN = Path(r'D:\RPF_BRAIN')
LANG_DIR = BRAIN / 'Archived' / 'voice_languages'
LANG_DIR.mkdir(parents=True, exist_ok=True)

class MultiLanguage:
    def __init__(self):
        self.current_language = "en"
        self.languages = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German"
        }
        self.translations = {}
        self._load_settings()
    
    def _load_settings(self):
        """Load language settings."""
        settings_file = LANG_DIR / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_language = data.get("language", "en")
                    self.translations = data.get("translations", {})
            except: pass
    
    def _save_settings(self):
        """Save language settings."""
        settings_file = LANG_DIR / "settings.json"
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump({
                "language": self.current_language,
                "translations": self.translations
            }, f, indent=2)
    
    def set_language(self, lang_code: str) -> bool:
        """Set current language."""
        if lang_code in self.languages:
            self.current_language = lang_code
            self._save_settings()
            return True
        return False
    
    def detect_language(self, text: str) -> str:
        """Detect language from text (simple heuristic)."""
        # Simple detection based on common words
        text_lower = text.lower()
        if any(word in text_lower for word in ['el', 'la', 'de', 'que', 'es']):
            return "es"
        elif any(word in text_lower for word in ['le', 'la', 'de', 'et', 'est']):
            return "fr"
        elif any(word in text_lower for word in ['der', 'die', 'das', 'und', 'ist']):
            return "de"
        return "en"
    
    def translate_command(self, text: str, target_lang: Optional[str] = None) -> str:
        """Translate command to target language."""
        target = target_lang or self.current_language
        if target == "en":
            return text
        # Simple translation lookup
        return self.translations.get(text, text)

def main():
    ml = MultiLanguage()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python voice_multilang.py <command> [args...]")
        print("Commands: set <lang_code>, detect <text>, translate <text> [target_lang]")
        return
    cmd = sys.argv[1].lower()
    if cmd == "set":
        if len(sys.argv) < 3: print("Error: set requires lang_code"); return
        print(f"OK Language set to {ml.languages.get(sys.argv[2], sys.argv[2])}" if ml.set_language(sys.argv[2]) else "FAILED Invalid language")
    elif cmd == "detect":
        if len(sys.argv) < 3: print("Error: detect requires text"); return
        lang = ml.detect_language(" ".join(sys.argv[2:]))
        print(f"Detected: {ml.languages.get(lang, lang)}")
    elif cmd == "translate":
        if len(sys.argv) < 3: print("Error: translate requires text"); return
        target = sys.argv[3] if len(sys.argv) > 3 else None
        result = ml.translate_command(" ".join(sys.argv[2:]), target)
        print(f"Translated: {result}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

