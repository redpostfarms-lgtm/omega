"""
Agent Prompt Engineering System
Manages prompt templates, versioning, and A/B testing.

Red Post Farms, LLC - 2026
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
PROMPT_DIR = BRAIN_DIR / "Archived" / "prompts"
PROMPT_DIR.mkdir(parents=True, exist_ok=True)

class PromptEngineer:
    def __init__(self):
        self.templates = {}
        self.versions = {}
        self.ab_tests = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load prompt templates."""
        templates_file = PROMPT_DIR / "templates.json"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except: pass
    
    def _save_templates(self):
        """Save templates to disk."""
        templates_file = PROMPT_DIR / "templates.json"
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=2)
    
    def create_template(self, name: str, template: str, version: str = "1.0") -> bool:
        """Create a prompt template."""
        template_hash = hashlib.sha256(template.encode()).hexdigest()[:16]
        if name not in self.templates:
            self.templates[name] = {}
        self.templates[name][version] = {
            "template": template,
            "hash": template_hash,
            "created": int(time.time()),
            "usage_count": 0
        }
        self._save_templates()
        return True
    
    def version_prompt(self, name: str, new_template: str) -> str:
        """Create new version of a prompt."""
        if name not in self.templates:
            self.create_template(name, new_template, "1.0")
            return "1.0"
        
        versions = [v for v in self.templates[name].keys()]
        if not versions:
            self.create_template(name, new_template, "1.0")
            return "1.0"
        
        latest = max(versions, key=lambda v: float(v))
        new_version = str(float(latest) + 0.1)
        self.create_template(name, new_template, new_version)
        return new_version
    
    def ab_test(self, name_a: str, name_b: str, test_name: str) -> Dict:
        """A/B test two prompts."""
        if name_a not in self.templates or name_b not in self.templates:
            return {"error": "Templates not found"}
        
        test_id = hashlib.sha256(f"{test_name}{int(time.time())}".encode()).hexdigest()[:16]
        self.ab_tests[test_id] = {
            "name": test_name,
            "template_a": name_a,
            "template_b": name_b,
            "results_a": {"success": 0, "total": 0},
            "results_b": {"success": 0, "total": 0},
            "created": int(time.time())
        }
        return {"test_id": test_id, "status": "created"}
    
    def get_template(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Get a prompt template."""
        if name not in self.templates:
            return None
        if version:
            return self.templates[name].get(version, {}).get("template")
        latest = max(self.templates[name].keys(), key=lambda v: float(v))
        template_data = self.templates[name][latest]
        template_data["usage_count"] = template_data.get("usage_count", 0) + 1
        self._save_templates()
        return template_data["template"]
    
    def list_templates(self) -> List[str]:
        """List all template names."""
        return list(self.templates.keys())

import time

def main():
    pe = PromptEngineer()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python agent_prompt_engineer.py <command> [args...]")
        print("Commands: create <name> <template>, version <name> <new_template>, get <name> [version], list")
        return
    cmd = sys.argv[1].lower()
    if cmd == "create":
        if len(sys.argv) < 4: print("Error: create requires name and template"); return
        pe.create_template(sys.argv[2], " ".join(sys.argv[3:]))
        print("OK Template created")
    elif cmd == "version":
        if len(sys.argv) < 4: print("Error: version requires name and new template"); return
        v = pe.version_prompt(sys.argv[2], " ".join(sys.argv[3:]))
        print(f"OK New version: {v}")
    elif cmd == "get":
        if len(sys.argv) < 3: print("Error: get requires name"); return
        version = sys.argv[3] if len(sys.argv) > 3 else None
        template = pe.get_template(sys.argv[2], version)
        print(template if template else "Template not found")
    elif cmd == "list":
        templates = pe.list_templates()
        print("Templates:")
        for name in templates: print(f"  {name}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

