"""
Farm Mobile Access System
Provide mobile-friendly access to farm data.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
FARM_DIR = BRAIN_DIR / "Archived" / "farm_data"
MOBILE_DIR = FARM_DIR / "mobile"
MOBILE_DIR.mkdir(parents=True, exist_ok=True)

class FarmMobileAccess:
    def __init__(self):
        self.mobile_data = {}
        self._load_mobile_data()
    
    def _load_mobile_data(self):
        """Load mobile data."""
        mobile_file = MOBILE_DIR / "mobile_data.json"
        if mobile_file.exists():
            try:
                with open(mobile_file, 'r', encoding='utf-8') as f:
                    self.mobile_data = json.load(f)
            except: pass
    
    def _save_mobile_data(self):
        """Save mobile data."""
        mobile_file = MOBILE_DIR / "mobile_data.json"
        with open(mobile_file, 'w', encoding='utf-8') as f:
            json.dump(self.mobile_data, f, indent=2)
    
    def create_mobile_view(self, view_name: str, data: Dict):
        """Create a mobile-optimized view."""
        self.mobile_data[view_name] = {
            "data": data,
            "optimized": True,
            "mobile_friendly": True
        }
        self._save_mobile_data()
    
    def get_mobile_view(self, view_name: str) -> Dict:
        """Get mobile view."""
        return self.mobile_data.get(view_name, {})

def main():
    fma = FarmMobileAccess()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python farm_mobile_access.py <command> [args...]")
        print("Commands: create <view_name> <data_json>, get <view_name>")
        return
    cmd = sys.argv[1].lower()
    if cmd == "create":
        if len(sys.argv) < 4: print("Error: create requires view_name and data"); return
        data = json.loads(sys.argv[3])
        fma.create_mobile_view(sys.argv[2], data)
        print("OK Mobile view created")
    elif cmd == "get":
        if len(sys.argv) < 3: print("Error: get requires view_name"); return
        view = fma.get_mobile_view(sys.argv[2])
        print(json.dumps(view, indent=2) if view else "View not found")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

