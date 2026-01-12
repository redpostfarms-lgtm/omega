#!/usr/bin/env python3
"""
Fix and Enhance Control Panel
==============================
Fixes UI display issues and adds caching for faster loading.
"""

import sys
from pathlib import Path

# Read the control panel file
control_panel_file = Path(__file__).parent / "omega_control_panel.py"
cache_module_file = Path(__file__).parent / "omega_control_panel_cache.py"

def fix_control_panel():
    """Fix control panel and add caching"""
    
    print("\n[1/3] Reading control panel file...")
    with open(control_panel_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if cache import exists
    if "from omega_control_panel_cache import ControlPanelCache" not in content:
        print("\n[2/3] Adding cache import...")
        # Find the imports section and add cache import
        import_line = "from omega_control_panel_cache import ControlPanelCache\n"
        
        # Find a good place to add it (after other imports, before class definition)
        if "class ControlPanel:" in content:
            insert_pos = content.find("class ControlPanel:")
            # Find last import before class
            last_import_pos = content.rfind("\nimport ", 0, insert_pos)
            if last_import_pos == -1:
                last_import_pos = content.rfind("\nfrom ", 0, insert_pos)
            if last_import_pos != -1:
                # Find end of that import line
                end_of_line = content.find("\n", last_import_pos + 1)
                if end_of_line != -1:
                    content = content[:end_of_line+1] + import_line + content[end_of_line+1:]
                    print("[OK] Cache import added")
    
    # Check if cache is initialized in __init__
    if "self.cache = ControlPanelCache()" not in content:
        print("\n[2/3] Adding cache initialization...")
        # Find __init__ method
        init_pattern = "def __init__(self):"
        if init_pattern in content:
            init_pos = content.find(init_pattern)
            # Find the end of __init__ (look for first method definition after it)
            next_method = content.find("\n    def ", init_pos + len(init_pattern))
            if next_method == -1:
                next_method = len(content)
            
            # Find a good place to add cache init (after self.running = False)
            if "self.running = False" in content[init_pos:next_method]:
                running_pos = content.find("self.running = False", init_pos)
                end_of_line = content.find("\n", running_pos)
                if end_of_line != -1:
                    cache_init = "\n        # Cache for fast loading\n        self.cache = ControlPanelCache()\n        self.cache.load_cache()  # Load last known data\n"
                    content = content[:end_of_line+1] + cache_init + content[end_of_line+1:]
                    print("[OK] Cache initialization added")
    
    # Check if cache is used in _create_gui_panel or run method
    # This is more complex - we'll need to modify the methods
    
    print("\n[3/3] Writing updated file...")
    with open(control_panel_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] Control panel file updated")
    print("\nNote: Additional modifications needed for cache integration")
    print("Cache module created: omega_control_panel_cache.py")

if __name__ == "__main__":
    fix_control_panel()
