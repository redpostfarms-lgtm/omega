"""
Farm Data Export System
Export farm data to various formats.

Red Post Farms, LLC - 2026
"""

import json
import csv
from pathlib import Path
from typing import Dict, List
from datetime import datetime

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
FARM_DIR = BRAIN_DIR / "Archived" / "farm_data"
EXPORT_DIR = FARM_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

class FarmDataExport:
    def __init__(self):
        self.exports = []
    
    def export_to_json(self, data: Dict, filename: str) -> str:
        """Export data to JSON."""
        filepath = EXPORT_DIR / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return str(filepath)
    
    def export_to_csv(self, data: List[Dict], filename: str) -> str:
        """Export data to CSV."""
        filepath = EXPORT_DIR / f"{filename}.csv"
        if not data:
            return ""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        return str(filepath)
    
    def export_to_txt(self, data: str, filename: str) -> str:
        """Export data to text."""
        filepath = EXPORT_DIR / f"{filename}.txt"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        return str(filepath)

def main():
    fde = FarmDataExport()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python farm_data_export.py <command> [args...]")
        print("Commands: json <data_json> <filename>, csv <data_json> <filename>, txt <data> <filename>")
        return
    cmd = sys.argv[1].lower()
    if cmd == "json":
        if len(sys.argv) < 4: print("Error: json requires data and filename"); return
        data = json.loads(sys.argv[2])
        filepath = fde.export_to_json(data, sys.argv[3])
        print(f"OK Exported to {filepath}")
    elif cmd == "csv":
        if len(sys.argv) < 4: print("Error: csv requires data and filename"); return
        data = json.loads(sys.argv[2])
        filepath = fde.export_to_csv(data, sys.argv[3])
        print(f"OK Exported to {filepath}")
    elif cmd == "txt":
        if len(sys.argv) < 4: print("Error: txt requires data and filename"); return
        filepath = fde.export_to_txt(sys.argv[2], sys.argv[3])
        print(f"OK Exported to {filepath}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

