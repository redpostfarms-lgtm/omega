"""
Knowledge Tags System
Tag and categorize knowledge entries.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List, Set

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
TAGS_DIR = BRAIN_DIR / "Archived" / "knowledge_tags"
TAGS_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgeTags:
    def __init__(self):
        self.tags = {}  # {entry_id: [tags]}
        self.tag_index = {}  # {tag: [entry_ids]}
        self._load_tags()
    
    def _load_tags(self):
        """Load tags from disk."""
        tags_file = TAGS_DIR / "tags.json"
        if tags_file.exists():
            try:
                with open(tags_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tags = data.get("tags", {})
                    self._rebuild_index()
            except: pass
    
    def _rebuild_index(self):
        """Rebuild tag index."""
        self.tag_index = {}
        for entry_id, tags in self.tags.items():
            for tag in tags:
                if tag not in self.tag_index:
                    self.tag_index[tag] = []
                if entry_id not in self.tag_index[tag]:
                    self.tag_index[tag].append(entry_id)
    
    def _save_tags(self):
        """Save tags to disk."""
        tags_file = TAGS_DIR / "tags.json"
        with open(tags_file, 'w', encoding='utf-8') as f:
            json.dump({"tags": self.tags}, f, indent=2)
    
    def add_tags(self, entry_id: str, tags: List[str]):
        """Add tags to an entry."""
        if entry_id not in self.tags:
            self.tags[entry_id] = []
        for tag in tags:
            if tag not in self.tags[entry_id]:
                self.tags[entry_id].append(tag)
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            if entry_id not in self.tag_index[tag]:
                self.tag_index[tag].append(entry_id)
        self._save_tags()
    
    def remove_tags(self, entry_id: str, tags: List[str]):
        """Remove tags from an entry."""
        if entry_id in self.tags:
            for tag in tags:
                if tag in self.tags[entry_id]:
                    self.tags[entry_id].remove(tag)
                if tag in self.tag_index and entry_id in self.tag_index[tag]:
                    self.tag_index[tag].remove(entry_id)
        self._save_tags()
    
    def get_entries_by_tag(self, tag: str) -> List[str]:
        """Get entries with a specific tag."""
        return self.tag_index.get(tag, [])
    
    def get_tags(self, entry_id: str) -> List[str]:
        """Get tags for an entry."""
        return self.tags.get(entry_id, [])
    
    def list_all_tags(self) -> List[str]:
        """List all tags."""
        return sorted(set(tag for tags in self.tags.values() for tag in tags))

def main():
    kt = KnowledgeTags()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python knowledge_tags.py <command> [args...]")
        print("Commands: add <entry_id> <tag1,tag2>, remove <entry_id> <tag1,tag2>, get <entry_id>, search <tag>, list")
        return
    cmd = sys.argv[1].lower()
    if cmd == "add":
        if len(sys.argv) < 4: print("Error: add requires entry_id and tags"); return
        tags = sys.argv[3].split(',')
        kt.add_tags(sys.argv[2], tags)
        print("OK Tags added")
    elif cmd == "remove":
        if len(sys.argv) < 4: print("Error: remove requires entry_id and tags"); return
        tags = sys.argv[3].split(',')
        kt.remove_tags(sys.argv[2], tags)
        print("OK Tags removed")
    elif cmd == "get":
        if len(sys.argv) < 3: print("Error: get requires entry_id"); return
        tags = kt.get_tags(sys.argv[2])
        print(f"Tags: {', '.join(tags)}" if tags else "No tags")
    elif cmd == "search":
        if len(sys.argv) < 3: print("Error: search requires tag"); return
        entries = kt.get_entries_by_tag(sys.argv[2])
        print(f"Found {len(entries)} entries: {', '.join(entries[:10])}")
    elif cmd == "list":
        tags = kt.list_all_tags()
        print(f"All tags ({len(tags)}): {', '.join(tags)}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

