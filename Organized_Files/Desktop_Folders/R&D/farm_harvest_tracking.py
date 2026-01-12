"""
Farm Harvest Tracking System
Track harvest data and yields.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
FARM_DIR = BRAIN_DIR / "Archived" / "farm_data"
FARM_DIR.mkdir(parents=True, exist_ok=True)

class HarvestTracking:
    def __init__(self):
        self.harvests = {}
        self._load_harvests()
    
    def _load_harvests(self):
        """Load harvest data."""
        harvests_file = FARM_DIR / "harvests.json"
        if harvests_file.exists():
            try:
                with open(harvests_file, 'r', encoding='utf-8') as f:
                    self.harvests = json.load(f)
            except: pass
    
    def _save_harvests(self):
        """Save harvest data."""
        harvests_file = FARM_DIR / "harvests.json"
        with open(harvests_file, 'w', encoding='utf-8') as f:
            json.dump(self.harvests, f, indent=2)
    
    def record_harvest(self, crop: str, date: str, yield_amount: float, unit: str = "lbs"):
        """Record a harvest."""
        harvest_id = f"{crop}_{date}"
        self.harvests[harvest_id] = {
            "crop": crop,
            "date": date,
            "yield": yield_amount,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }
        self._save_harvests()
    
    def get_harvests(self, crop: str = None) -> List[Dict]:
        """Get harvest records."""
        if crop:
            return [h for h in self.harvests.values() if h["crop"] == crop]
        return list(self.harvests.values())

def main():
    ht = HarvestTracking()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python farm_harvest_tracking.py <command> [args...]")
        print("Commands: record <crop> <date> <yield> [unit], get [crop]")
        return
    cmd = sys.argv[1].lower()
    if cmd == "record":
        if len(sys.argv) < 5: print("Error: record requires crop, date, yield"); return
        unit = sys.argv[5] if len(sys.argv) > 5 else "lbs"
        ht.record_harvest(sys.argv[2], sys.argv[3], float(sys.argv[4]), unit)
        print("OK Harvest recorded")
    elif cmd == "get":
        crop = sys.argv[2] if len(sys.argv) > 2 else None
        harvests = ht.get_harvests(crop)
        print(f"Harvests ({len(harvests)}):")
        for h in harvests: print(f"  {h['crop']} - {h['date']} - {h['yield']} {h['unit']}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

