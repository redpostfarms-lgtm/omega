"""
Daily Notes System
Create and manage daily notes.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
NOTES_DIR = BRAIN_DIR / "Archived" / "daily_notes"
NOTES_DIR.mkdir(parents=True, exist_ok=True)

class DailyNotes:
    def __init__(self):
        self.notes = {}
        self._load_notes()
    
    def _load_notes(self):
        """Load notes from disk."""
        notes_file = NOTES_DIR / "notes.json"
        if notes_file.exists():
            try:
                with open(notes_file, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            except: pass
    
    def _save_notes(self):
        """Save notes to disk."""
        notes_file = NOTES_DIR / "notes.json"
        with open(notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=2)
    
    def add_note(self, date: str, content: str):
        """Add a daily note."""
        if date not in self.notes:
            self.notes[date] = []
        self.notes[date].append({
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self._save_notes()
    
    def get_notes(self, date: str) -> List[Dict]:
        """Get notes for a date."""
        return self.notes.get(date, [])
    
    def get_today_notes(self) -> List[Dict]:
        """Get today's notes."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.get_notes(today)

def main():
    dn = DailyNotes()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python knowledge_daily_notes.py <command> [args...]")
        print("Commands: add <date> <content>, get <date>, today")
        return
    cmd = sys.argv[1].lower()
    if cmd == "add":
        if len(sys.argv) < 4: print("Error: add requires date and content"); return
        dn.add_note(sys.argv[2], " ".join(sys.argv[3:]))
        print("OK Note added")
    elif cmd == "get":
        if len(sys.argv) < 3: print("Error: get requires date"); return
        notes = dn.get_notes(sys.argv[2])
        print(f"Notes for {sys.argv[2]}:")
        for note in notes: print(f"  {note['content']}")
    elif cmd == "today":
        notes = dn.get_today_notes()
        print(f"Today's notes ({len(notes)}):")
        for note in notes: print(f"  {note['content']}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

