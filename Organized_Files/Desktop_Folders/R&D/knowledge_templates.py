"""
Knowledge Templates System
Create and use templates for knowledge entries.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
TEMPLATES_DIR = BRAIN_DIR / "Archived" / "knowledge_templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgeTemplates:
    def __init__(self):
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from disk."""
        templates_file = TEMPLATES_DIR / "templates.json"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except: pass
    
    def _save_templates(self):
        """Save templates to disk."""
        templates_file = TEMPLATES_DIR / "templates.json"
        with open(templates_file, 'w', encoding='utf-8') as f:
            json.dump(self.templates, f, indent=2)
    
    def create_template(self, name: str, template: str, fields: List[str] = None):
        """Create a template."""
        self.templates[name] = {
            "template": template,
            "fields": fields or [],
            "usage_count": 0
        }
        self._save_templates()
    
    def apply_template(self, name: str, values: Dict[str, str]) -> str:
        """Apply template with values."""
        if name not in self.templates:
            return ""
        template = self.templates[name]["template"]
        result = template
        for field, value in values.items():
            result = result.replace(f"{{{field}}}", value)
        self.templates[name]["usage_count"] = self.templates[name].get("usage_count", 0) + 1
        self._save_templates()
        return result
    
    def list_templates(self) -> List[str]:
        """List all templates."""
        return list(self.templates.keys())

def main():
    kt = KnowledgeTemplates()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python knowledge_templates.py <command> [args...]")
        print("Commands: create <name> <template> [fields], apply <name> <field1=value1,field2=value2>, list")
        return
    cmd = sys.argv[1].lower()
    if cmd == "create":
        if len(sys.argv) < 4: print("Error: create requires name and template"); return
        fields = sys.argv[4].split(',') if len(sys.argv) > 4 else []
        kt.create_template(sys.argv[2], " ".join(sys.argv[3:4] if len(sys.argv) > 3 else []), fields)
        print("OK Template created")
    elif cmd == "apply":
        if len(sys.argv) < 4: print("Error: apply requires name and values"); return
        values = {k: v for k, v in [pair.split('=') for pair in sys.argv[3].split(',')]}
        result = kt.apply_template(sys.argv[2], values)
        print(result)
    elif cmd == "list":
        templates = kt.list_templates()
        print(f"Templates: {', '.join(templates)}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

