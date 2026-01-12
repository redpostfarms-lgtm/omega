"""
Farm Inventory System
Track farm inventory and supplies.

Red Post Farms, LLC - 2026
"""

import json
from pathlib import Path
from typing import Dict, List

BRAIN_DIR = Path(r"D:\RPF_BRAIN")
FARM_DIR = BRAIN_DIR / "Archived" / "farm_data"
FARM_DIR.mkdir(parents=True, exist_ok=True)

class FarmInventory:
    def __init__(self):
        self.inventory = {}
        self._load_inventory()
    
    def _load_inventory(self):
        """Load inventory."""
        inventory_file = FARM_DIR / "inventory.json"
        if inventory_file.exists():
            try:
                with open(inventory_file, 'r', encoding='utf-8') as f:
                    self.inventory = json.load(f)
            except: pass
    
    def _save_inventory(self):
        """Save inventory."""
        inventory_file = FARM_DIR / "inventory.json"
        with open(inventory_file, 'w', encoding='utf-8') as f:
            json.dump(self.inventory, f, indent=2)
    
    def add_item(self, item: str, quantity: float, unit: str = "units"):
        """Add inventory item."""
        if item not in self.inventory:
            self.inventory[item] = {"quantity": 0, "unit": unit}
        self.inventory[item]["quantity"] += quantity
        self._save_inventory()
    
    def remove_item(self, item: str, quantity: float):
        """Remove inventory item."""
        if item in self.inventory:
            self.inventory[item]["quantity"] = max(0, self.inventory[item]["quantity"] - quantity)
            self._save_inventory()
    
    def get_inventory(self) -> Dict:
        """Get all inventory."""
        return self.inventory

def main():
    fi = FarmInventory()
    import sys
    if len(sys.argv) < 2:
        print("Usage: python farm_inventory.py <command> [args...]")
        print("Commands: add <item> <quantity> [unit], remove <item> <quantity>, list")
        return
    cmd = sys.argv[1].lower()
    if cmd == "add":
        if len(sys.argv) < 4: print("Error: add requires item and quantity"); return
        unit = sys.argv[4] if len(sys.argv) > 4 else "units"
        fi.add_item(sys.argv[2], float(sys.argv[3]), unit)
        print("OK Item added")
    elif cmd == "remove":
        if len(sys.argv) < 4: print("Error: remove requires item and quantity"); return
        fi.remove_item(sys.argv[2], float(sys.argv[3]))
        print("OK Item removed")
    elif cmd == "list":
        inventory = fi.get_inventory()
        print("Inventory:")
        for item, data in inventory.items():
            print(f"  {item}: {data['quantity']} {data['unit']}")
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()

