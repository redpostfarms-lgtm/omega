"""
Knowledge Bidirectional Links System
Create bidirectional links between knowledge entries.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List, Set

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
LINKS_DIR = BRAIN_DIR / "Archived" / "knowledge_links"
LINKS_DIR.mkdir(parents=True, exist_ok=True)

class KnowledgeLinks:
    def __init__(self):
        self.links = {}  # {entry_id: [linked_entry_ids]}
        self.backlinks = {}  # {entry_id: [backlink_entry_ids]}
        self._load_links()
    
    def _load_links(self):
        """Load links from disk."""
        links_file = LINKS_DIR / "links.json"
        if links_file.exists():
            try:
                with open(links_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.links = data.get("links", {})
                    self._rebuild_backlinks()
            except: pass
    
    def _rebuild_backlinks(self):
        """Rebuild backlinks index."""
        self.backlinks = {}
        for entry_id, linked_ids in self.links.items():
            for linked_id in linked_ids:
                if linked_id not in self.backlinks:
                    self.backlinks[linked_id] = []
                if entry_id not in self.backlinks[linked_id]:
                    self.backlinks[linked_id].append(entry_id)
    
    def _save_links(self):
        """Save links to disk."""
        links_file = LINKS_DIR / "links.json"
        with open(links_file, 'w', encoding='utf-8') as f:
            json.dump({"links": self.links}, f, indent=2)
    
    def create_link(self, from_id: str, to_id: str):
        """Create bidirectional link."""
        if from_id not in self.links:
            self.links[from_id] = []
        if to_id not in self.links[from_id]:
            self.links[from_id].append(to_id)
        
        if to_id not in self.backlinks:
            self.backlinks[to_id] = []
        if from_id not in self.backlinks[to_id]:
            self.backlinks[to_id].append(from_id)
        
        self._save_links()
    
    def get_links(self, entry_id: str) -> List[str]:
        """Get forward links from an entry."""
        return self.links.get(entry_id, [])
    
    def get_backlinks(self, entry_id: str) -> List[str]:
        """Get backlinks to an entry."""
        return self.backlinks.get(entry_id, [])
    
    def get_graph_view(self, entry_id: str, depth: int = 2) -> Dict:
        """Get graph view of linked entries."""
        visited = set()
        graph = {"nodes": [], "edges": []}
        
        def traverse(eid: str, current_depth: int):
            if eid in visited or current_depth > depth:
                return
            visited.add(eid)
            graph["nodes"].append(eid)
            
            for linked_id in self.get_links(eid):
                graph["edges"].append((eid, linked_id))
                if current_depth < depth:
                    traverse(linked_id, current_depth + 1)
            
            for backlink_id in self.get_backlinks(eid):
                graph["edges"].append((backlink_id, eid))
                if current_depth < depth:
                    traverse(backlink_id, current_depth + 1)
        
        traverse(entry_id, 0)
        return graph

def main():
    kl = KnowledgeLinks()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python knowledge_links.py <command> [args...]")
        print("Commands: link <from_id> <to_id>, get <entry_id>, backlinks <entry_id>, graph <entry_id> [depth]")
        return
    cmd = sys.argv[1].lower()
    if cmd == "link":
        if len(sys.argv) < 4: print("Error: link requires from_id and to_id"); return
        kl.create_link(sys.argv[2], sys.argv[3])
        print("OK Link created")
    elif cmd == "get":
        if len(sys.argv) < 3: print("Error: get requires entry_id"); return
        links = kl.get_links(sys.argv[2])
        print(f"Links: {', '.join(links)}" if links else "No links")
    elif cmd == "backlinks":
        if len(sys.argv) < 3: print("Error: backlinks requires entry_id"); return
        backlinks = kl.get_backlinks(sys.argv[2])
        print(f"Backlinks: {', '.join(backlinks)}" if backlinks else "No backlinks")
    elif cmd == "graph":
        if len(sys.argv) < 3: print("Error: graph requires entry_id"); return
        depth = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        graph = kl.get_graph_view(sys.argv[2], depth)
        print(f"Graph: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

