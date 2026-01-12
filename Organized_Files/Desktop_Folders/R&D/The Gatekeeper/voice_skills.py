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
Voice Skills System
Register and execute voice-activated skills.

Red Post Farms, LLC - 2026
"""

import json
import importlib
from pathlib import Path
from typing import Dict, List, Callable, Optional

BRAIN = Path(r'D:\RPF_BRAIN')
SKILLS_DIR = BRAIN / 'Archived' / 'voice_skills'
SKILLS_DIR.mkdir(parents=True, exist_ok=True)

class VoiceSkills:
    def __init__(self):
        self.skills = {}
        self._load_skills()
    
    def _load_skills(self):
        """Load registered skills."""
        skills_file = SKILLS_DIR / "skills.json"
        if skills_file.exists():
            try:
                with open(skills_file, 'r', encoding='utf-8') as f:
                    self.skills = json.load(f)
            except: pass
    
    def _save_skills(self):
        """Save skills to disk."""
        skills_file = SKILLS_DIR / "skills.json"
        with open(skills_file, 'w', encoding='utf-8') as f:
            json.dump(self.skills, f, indent=2)
    
    def register_skill(self, name: str, trigger_words: List[str], module: str, function: str):
        """Register a voice skill."""
        self.skills[name] = {
            "trigger_words": trigger_words,
            "module": module,
            "function": function,
            "usage_count": 0
        }
        self._save_skills()
    
    def execute_skill(self, text: str) -> Optional[str]:
        """Execute skill based on text."""
        text_lower = text.lower()
        for skill_name, skill_data in self.skills.items():
            for trigger in skill_data["trigger_words"]:
                if trigger in text_lower:
                    try:
                        module = importlib.import_module(skill_data["module"])
                        func = getattr(module, skill_data["function"])
                        result = func(text)
                        skill_data["usage_count"] = skill_data.get("usage_count", 0) + 1
                        self._save_skills()
                        return result
                    except Exception as e:
                        return f"Error executing skill {skill_name}: {e}"
        return None
    
    def list_skills(self) -> List[str]:
        """List all registered skills."""
        return list(self.skills.keys())

def main():
    skills = VoiceSkills()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python voice_skills.py <command> [args...]")
        print("Commands: register <name> <trigger> <module> <function>, execute <text>, list")
        return
    cmd = sys.argv[1].lower()
    if cmd == "register":
        if len(sys.argv) < 6: print("Error: register requires name, trigger, module, function"); return
        triggers = sys.argv[3].split(',')
        skills.register_skill(sys.argv[2], triggers, sys.argv[4], sys.argv[5])
        print("OK Skill registered")
    elif cmd == "execute":
        if len(sys.argv) < 3: print("Error: execute requires text"); return
        result = skills.execute_skill(" ".join(sys.argv[2:]))
        print(result if result else "No skill matched")
    elif cmd == "list":
        skill_list = skills.list_skills()
        print("Registered Skills:")
        for name in skill_list: print(f"  {name}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

