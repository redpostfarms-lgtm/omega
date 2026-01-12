#!/usr/bin/env python3
"""
Optimize and Fix Redundancies
==============================
Comprehensive script to identify and fix redundancies, errors, and optimization issues.
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
from collections import defaultdict

class RedundancyFixer:
    """Identifies and fixes redundancies"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.issues_found = []
        self.fixes_applied = []
        
    def analyze_config_redundancy(self) -> List[Dict[str, Any]]:
        """Analyze configuration file redundancies"""
        issues = []
        
        # Check for duplicate search configs
        search_configs = []
        if (self.base_dir / "omega_search_config.json").exists():
            with open(self.base_dir / "omega_search_config.json", 'r') as f:
                search_configs.append(("omega_search_config.json", json.load(f)))
        
        if (self.base_dir / ".cursor" / "config.json").exists():
            with open(self.base_dir / ".cursor" / "config.json", 'r') as f:
                cursor_config = json.load(f)
                if "deep_search" in cursor_config:
                    search_configs.append((".cursor/config.json", cursor_config["deep_search"]))
        
        if (self.base_dir / ".vscode" / "settings.json").exists():
            with open(self.base_dir / ".vscode" / "settings.json", 'r') as f:
                vs_config = json.load(f)
                if "omega.deepSearch" in vs_config:
                    search_configs.append((".vscode/settings.json", vs_config["omega.deepSearch"]))
        
        if len(search_configs) > 1:
            issues.append({
                "type": "redundant_config",
                "description": "Search configuration duplicated across multiple files",
                "files": [f[0] for f in search_configs],
                "fix": "Consolidate into single config file"
            })
        
        return issues
    
    def consolidate_configs(self) -> Dict[str, Any]:
        """Consolidate configuration files"""
        # Load all configs
        configs = {}
        
        # Load omega_search_config.json
        search_config_path = self.base_dir / "omega_search_config.json"
        if search_config_path.exists():
            with open(search_config_path, 'r') as f:
                configs['search'] = json.load(f)
        
        # Load .cursor/config.json
        cursor_config_path = self.base_dir / ".cursor" / "config.json"
        if cursor_config_path.exists():
            with open(cursor_config_path, 'r') as f:
                cursor_config = json.load(f)
                if 'deep_search' in cursor_config:
                    configs['cursor_search'] = cursor_config['deep_search']
                if 'autonomous_implementation' in cursor_config:
                    configs['cursor_autonomy'] = cursor_config['autonomous_implementation']
                if 'omega_autonomy' in cursor_config:
                    configs['cursor_omega'] = cursor_config['omega_autonomy']
        
        # Load .vscode/settings.json
        vs_config_path = self.base_dir / ".vscode" / "settings.json"
        if vs_config_path.exists():
            with open(vs_config_path, 'r') as f:
                vs_config = json.load(f)
                if 'omega.deepSearch' in vs_config:
                    configs['vs_search'] = vs_config['omega.deepSearch']
                # Extract omega.* settings
                omega_settings = {k.replace('omega.', ''): v for k, v in vs_config.items() if k.startswith('omega.')}
                if omega_settings:
                    configs['vs_omega'] = omega_settings
        
        # Create consolidated config
        consolidated = {
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            "search": configs.get('search', {
                "automatic_deep_search": True,
                "search_depth": "deepest",
                "search_breadth": "widest",
                "use_all_resources": True
            }),
            "autonomy": {
                "enabled": True,
                "auto_create_files": True,
                "auto_edit_files": True,
                "require_confirmation": False
            }
        }
        
        return consolidated
    
    def fix_configs(self):
        """Fix configuration redundancies"""
        consolidated = self.consolidate_configs()
        
        # Save consolidated config
        consolidated_path = self.base_dir / "omega_config_consolidated.json"
        with open(consolidated_path, 'w') as f:
            json.dump(consolidated, f, indent=2)
        
        # Update .cursor/config.json (remove duplicate search config)
        cursor_config_path = self.base_dir / ".cursor" / "config.json"
        if cursor_config_path.exists():
            with open(cursor_config_path, 'r') as f:
                cursor_config = json.load(f)
            
            # Remove duplicate deep_search if omega_search_config.json exists
            if "deep_search" in cursor_config and (self.base_dir / "omega_search_config.json").exists():
                del cursor_config["deep_search"]
                cursor_config["_note"] = "Search config moved to omega_search_config.json"
            
            with open(cursor_config_path, 'w') as f:
                json.dump(cursor_config, f, indent=2)
        
        # Update .vscode/settings.json (remove duplicate search config)
        vs_config_path = self.base_dir / ".vscode" / "settings.json"
        if vs_config_path.exists():
            with open(vs_config_path, 'r') as f:
                vs_config = json.load(f)
            
            # Remove duplicate omega.deepSearch if omega_search_config.json exists
            if "omega.deepSearch" in vs_config and (self.base_dir / "omega_search_config.json").exists():
                del vs_config["omega.deepSearch"]
            
            with open(vs_config_path, 'w') as f:
                json.dump(vs_config, f, indent=2)
        
        self.fixes_applied.append("Consolidated configuration files")
    
    def analyze_duplicate_files(self) -> List[Dict[str, Any]]:
        """Analyze duplicate/obsolete documentation files"""
        issues = []
        
        # Find all *_COMPLETE.md files
        complete_files = list(self.base_dir.glob("*_COMPLETE.md"))
        
        # Group by feature
        features = defaultdict(list)
        for file in complete_files:
            # Extract feature name
            name = file.stem.replace("_COMPLETE", "").replace("_", " ").lower()
            features[name].append(file.name)
        
        # Find duplicates
        for feature, files in features.items():
            if len(files) > 1:
                issues.append({
                    "type": "duplicate_documentation",
                    "feature": feature,
                    "files": files,
                    "fix": f"Consolidate {len(files)} files into one"
                })
        
        return issues
    
    def optimize_scripts(self):
        """Optimize Python scripts"""
        optimizations = []
        
        # Find Python files with redundant imports
        py_files = list(self.base_dir.rglob("*.py"))
        
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Check for duplicate imports
                imports = []
                import_lines = []
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith('import ') or stripped.startswith('from '):
                        if stripped in imports:
                            optimizations.append({
                                "file": str(py_file.relative_to(self.base_dir)),
                                "line": i + 1,
                                "issue": f"Duplicate import: {stripped}",
                                "fix": "Remove duplicate"
                            })
                        else:
                            imports.append(stripped)
                            import_lines.append((i, line))
            except:
                pass
        
        return optimizations

def main():
    """Main function"""
    base_dir = Path(__file__).parent.absolute()
    
    print("\n" + "=" * 80)
    print(" " * 20 + "OPTIMIZE AND FIX REDUNDANCIES")
    print("=" * 80)
    print()
    
    fixer = RedundancyFixer(base_dir)
    
    # Analyze config redundancy
    print("[1/4] Analyzing configuration redundancies...")
    config_issues = fixer.analyze_config_redundancy()
    print(f"[OK] Found {len(config_issues)} config redundancies")
    
    # Analyze duplicate files
    print("[2/4] Analyzing duplicate documentation...")
    doc_issues = fixer.analyze_duplicate_files()
    print(f"[OK] Found {len(doc_issues)} duplicate documentation files")
    
    # Optimize scripts
    print("[3/4] Analyzing script optimizations...")
    script_optimizations = fixer.optimize_scripts()
    print(f"[OK] Found {len(script_optimizations)} script optimizations")
    
    # Fix configs
    print("[4/4] Fixing configuration redundancies...")
    fixer.fix_configs()
    print("[OK] Configuration files consolidated")
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "config_issues": config_issues,
        "doc_issues": doc_issues,
        "script_optimizations": script_optimizations[:50],  # Limit to 50
        "fixes_applied": fixer.fixes_applied
    }
    
    report_path = base_dir / "OPTIMIZATION_REPORT.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print()
    print("=" * 80)
    print(" " * 25 + "OPTIMIZATION COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Config redundancies: {len(config_issues)}")
    print(f"  - Duplicate docs: {len(doc_issues)}")
    print(f"  - Script optimizations: {len(script_optimizations)}")
    print(f"  - Fixes applied: {len(fixer.fixes_applied)}")
    print()
    print(f"Report saved: {report_path.name}")
    print()

if __name__ == "__main__":
    main()
