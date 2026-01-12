"""
Farm Crop Planning System
Plan and schedule crop planting.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
FARM_DIR = BRAIN_DIR / "Archived" / "farm_data"
FARM_DIR.mkdir(parents=True, exist_ok=True)

class CropPlanning:
    def __init__(self):
        self.plans = {}
        self._load_plans()
    
    def _load_plans(self):
        """Load crop plans."""
        plans_file = FARM_DIR / "crop_plans.json"
        if plans_file.exists():
            try:
                with open(plans_file, 'r', encoding='utf-8') as f:
                    self.plans = json.load(f)
            except: pass
    
    def _save_plans(self):
        """Save crop plans."""
        plans_file = FARM_DIR / "crop_plans.json"
        with open(plans_file, 'w', encoding='utf-8') as f:
            json.dump(self.plans, f, indent=2)
    
    def create_plan(self, crop: str, planting_date: str, area: float, notes: str = ""):
        """Create a crop plan."""
        plan_id = f"{crop}_{planting_date}"
        self.plans[plan_id] = {
            "crop": crop,
            "planting_date": planting_date,
            "area": area,
            "notes": notes,
            "status": "planned"
        }
        self._save_plans()
    
    def get_plans(self) -> Dict:
        """Get all crop plans."""
        return self.plans

def main():
    cp = CropPlanning()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python farm_crop_planning.py <command> [args...]")
        print("Commands: create <crop> <date> <area> [notes], list")
        return
    cmd = sys.argv[1].lower()
    if cmd == "create":
        if len(sys.argv) < 5: print("Error: create requires crop, date, area"); return
        notes = " ".join(sys.argv[5:]) if len(sys.argv) > 5 else ""
        cp.create_plan(sys.argv[2], sys.argv[3], float(sys.argv[4]), notes)
        print("OK Plan created")
    elif cmd == "list":
        plans = cp.get_plans()
        print(f"Crop Plans ({len(plans)}):")
        for plan_id, plan in plans.items():
            print(f"  {plan['crop']} - {plan['planting_date']} - {plan['area']} acres")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

