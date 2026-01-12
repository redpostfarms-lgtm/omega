#!/usr/bin/env python3
"""
Optimize Scripts and Consolidate
=================================
Consolidates and optimizes redundant scripts.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Set
import json
from datetime import datetime
import re

class ScriptOptimizer:
    """Optimizes and consolidates scripts"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.optimizations = []
        self.consolidations = []
        
    def analyze_script_redundancy(self) -> List[Dict[str, Any]]:
        """Analyze redundant scripts"""
        redundancies = []
        
        # Find similar script patterns
        config_scripts = list(self.base_dir.glob("*CONFIG*.py"))
        optimize_scripts = list(self.base_dir.glob("*OPTIMIZE*.py"))
        scan_scripts = list(self.base_dir.glob("*SCAN*.py"))
        
        # Check for similar functionality
        if len(config_scripts) > 1:
            redundancies.append({
                "type": "multiple_config_scripts",
                "files": [f.name for f in config_scripts],
                "suggestion": "Consider consolidating into OMEGA_CONFIG_OPTIMIZED.py"
            })
        
        if len(optimize_scripts) > 1:
            redundancies.append({
                "type": "multiple_optimize_scripts",
                "files": [f.name for f in optimize_scripts],
                "suggestion": "Consider consolidating optimize functionality"
            })
        
        if len(scan_scripts) > 1:
            redundancies.append({
                "type": "multiple_scan_scripts",
                "files": [f.name for f in scan_scripts],
                "suggestion": "Consider consolidating scan functionality"
            })
        
        return redundancies
    
    def consolidate_config_scripts(self):
        """Consolidate configuration scripts"""
        # OMEGA_CONFIG_OPTIMIZED.py should be the main config system
        # OMEGA_AUTOMATIC_DEEP_SEARCH.py can use it
        
        config_optimized = self.base_dir / "OMEGA_CONFIG_OPTIMIZED.py"
        auto_search = self.base_dir / "OMEGA_AUTOMATIC_DEEP_SEARCH.py"
        
        if config_optimized.exists() and auto_search.exists():
            # Update auto_search to use optimized config
            with open(auto_search, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it already uses OMEGA_CONFIG_OPTIMIZED
            if 'OMEGA_CONFIG_OPTIMIZED' not in content:
                self.consolidations.append({
                    "file": "OMEGA_AUTOMATIC_DEEP_SEARCH.py",
                    "action": "Update to use OMEGA_CONFIG_OPTIMIZED",
                    "status": "recommended"
                })
        
        return self.consolidations

def main():
    """Main function"""
    base_dir = Path(__file__).parent.absolute()
    
    print("\n" + "=" * 80)
    print(" " * 20 + "SCRIPT OPTIMIZATION AND CONSOLIDATION")
    print("=" * 80)
    print()
    
    optimizer = ScriptOptimizer(base_dir)
    
    # Analyze redundancies
    print("[1/2] Analyzing script redundancies...")
    redundancies = optimizer.analyze_script_redundancy()
    print(f"[OK] Found {len(redundancies)} redundancy patterns")
    
    for red in redundancies:
        print(f"  - {red['type']}: {len(red['files'])} files")
        print(f"    Suggestion: {red['suggestion']}")
    
    # Consolidate config scripts
    print("[2/2] Consolidating configuration scripts...")
    consolidations = optimizer.consolidate_config_scripts()
    print(f"[OK] Found {len(consolidations)} consolidation opportunities")
    
    print()
    print("=" * 80)
    print(" " * 25 + "ANALYSIS COMPLETE")
    print("=" * 80)
    print()
    print("Recommendations:")
    print("  1. Use OMEGA_CONFIG_OPTIMIZED.py as main config system")
    print("  2. Update other scripts to use consolidated config")
    print("  3. Consider consolidating similar scripts")
    print()

if __name__ == "__main__":
    main()
