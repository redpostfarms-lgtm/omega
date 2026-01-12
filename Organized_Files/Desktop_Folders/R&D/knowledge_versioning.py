"""
Knowledge Versioning System
Track versions of knowledge entries.

Red Post Farms, LLC - 2026
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, List, Optional

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
VERSIONS_DIR = BRAIN_DIR / "Archived" / "knowledge_versions"
VERSIONS_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgeVersioning:
    def __init__(self):
        self.versions = {}  # {entry_id: [version_history]}
        self._load_versions()
    
    def _load_versions(self):
        """Load versions from disk."""
        versions_file = VERSIONS_DIR / "versions.json"
        if versions_file.exists():
            try:
                with open(versions_file, 'r', encoding='utf-8') as f:
                    self.versions = json.load(f)
            except: pass
    
    def _save_versions(self):
        """Save versions to disk."""
        versions_file = VERSIONS_DIR / "versions.json"
        with open(versions_file, 'w', encoding='utf-8') as f:
            json.dump(self.versions, f, indent=2)
    
    def create_version(self, entry_id: str, content: str) -> str:
        """Create new version of an entry."""
        version_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        version = {
            "hash": version_hash,
            "content": content,
            "timestamp": int(time.time()),
            "version": len(self.versions.get(entry_id, [])) + 1
        }
        
        if entry_id not in self.versions:
            self.versions[entry_id] = []
        self.versions[entry_id].append(version)
        self._save_versions()
        return version_hash
    
    def get_version_history(self, entry_id: str) -> List[Dict]:
        """Get version history for an entry."""
        return self.versions.get(entry_id, [])
    
    def restore_version(self, entry_id: str, version_hash: str) -> Optional[str]:
        """Restore entry to a specific version."""
        if entry_id not in self.versions:
            return None
        for version in self.versions[entry_id]:
            if version["hash"] == version_hash:
                return version["content"]
        return None

def main():
    kv = KnowledgeVersioning()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python knowledge_versioning.py <command> [args...]")
        print("Commands: create <entry_id> <content>, history <entry_id>, restore <entry_id> <version_hash>")
        return
    cmd = sys.argv[1].lower()
    if cmd == "create":
        if len(sys.argv) < 4: print("Error: create requires entry_id and content"); return
        vhash = kv.create_version(sys.argv[2], " ".join(sys.argv[3:]))
        print(f"OK Version created: {vhash}")
    elif cmd == "history":
        if len(sys.argv) < 3: print("Error: history requires entry_id"); return
        history = kv.get_version_history(sys.argv[2])
        print(f"Version history ({len(history)} versions):")
        for v in history: print(f"  {v['hash']} - v{v['version']} - {time.ctime(v['timestamp'])}")
    elif cmd == "restore":
        if len(sys.argv) < 4: print("Error: restore requires entry_id and version_hash"); return
        content = kv.restore_version(sys.argv[2], sys.argv[3])
        print(content if content else "Version not found")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

