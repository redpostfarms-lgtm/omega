#!/usr/bin/env python3
"""
Auto Select and Optimize Applications
======================================
Automatically selects and optimizes applications without user input.
Intelligently picks apps based on usage patterns and system requirements.
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class AutoSelectOptimizer:
    """Automatically select and optimize applications"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.selected_apps = []
        
        # Auto-selection rules (Omega decides, no user input)
        self.selection_rules = {
            'essential': [
                'omega', 'python', 'cursor', 'code', 'powershell',
                'explorer', 'dwm', 'winlogon'
            ],
            'productive': [
                'notepad', 'word', 'excel', 'outlook', 'chrome',
                'firefox', 'edge', 'vscode', 'pycharm'
            ],
            'background': [
                'spotify', 'discord', 'steam', 'battle.net',
                'epicgameslauncher', 'origin'
            ]
        }
        
        # Priority mapping
        self.priority_map = {
            'essential': 'high',
            'productive': 'normal',
            'background': 'low'
        }
    
    def auto_select_apps(self) -> Dict[str, List[Dict]]:
        """Automatically select apps based on rules (no user input)"""
        if not PSUTIL_AVAILABLE:
            return {}
        
        selected = {
            'essential': [],
            'productive': [],
            'background': []
        }
        
        current_pid = os.getpid()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info']):
                try:
                    pinfo = proc.info
                    
                    if pinfo['pid'] == current_pid or pinfo['pid'] == 0:
                        continue
                    
                    if not pinfo['name']:
                        continue
                    
                    app_name = pinfo['name'].lower()
                    memory_mb = 0
                    if pinfo['memory_info']:
                        memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    
                    app_info = {
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'exe': pinfo['exe'] if pinfo['exe'] else "",
                        'memory_mb': memory_mb,
                        'app_name': app_name
                    }
                    
                    # Auto-select based on rules
                    for category, patterns in self.selection_rules.items():
                        for pattern in patterns:
                            if pattern.lower() in app_name:
                                selected[category].append(app_info)
                                break
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"[WARNING] Error selecting apps: {e}")
        
        return selected
    
    def optimize_selected_apps(self, selected: Dict[str, List[Dict]]) -> Dict[str, int]:
        """Optimize all selected apps automatically"""
        if not PSUTIL_AVAILABLE:
            return {}
        
        stats = {
            'essential': 0,
            'productive': 0,
            'background': 0,
            'total': 0
        }
        
        for category, apps in selected.items():
            priority = self.priority_map.get(category, 'normal')
            
            for app in apps:
                try:
                    proc = psutil.Process(app['pid'])
                    
                    if sys.platform == 'win32':
                        priority_class = {
                            'high': psutil.HIGH_PRIORITY_CLASS,
                            'normal': psutil.NORMAL_PRIORITY_CLASS,
                            'low': psutil.BELOW_NORMAL_PRIORITY_CLASS
                        }.get(priority, psutil.NORMAL_PRIORITY_CLASS)
                        
                        proc.nice(priority_class)
                    else:
                        nice_value = {'high': -5, 'normal': 0, 'low': 5}.get(priority, 0)
                        proc.nice(nice_value)
                    
                    stats[category] += 1
                    stats['total'] += 1
                    
                    self.selected_apps.append({
                        'name': app['name'],
                        'pid': app['pid'],
                        'category': category,
                        'priority': priority
                    })
                    
                    print(f"  [{priority.upper():6}] {app['name']:30} ({category})")
                
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                except Exception as e:
                    continue
        
        return stats
    
    def run_auto_optimization(self):
        """Run automatic selection and optimization (no user input)"""
        print("\n" + "=" * 80)
        print(" " * 20 + "AUTO SELECT AND OPTIMIZE APPLICATIONS")
        print("=" * 80)
        print()
        print("Automatically selecting applications...")
        print("(No user input required - Omega decides)")
        print()
        
        # Auto-select apps
        selected = self.auto_select_apps()
        
        total_selected = sum(len(apps) for apps in selected.values())
        print(f"[OK] Selected {total_selected} applications automatically")
        print()
        print(f"  Essential:   {len(selected['essential'])}")
        print(f"  Productive:  {len(selected['productive'])}")
        print(f"  Background:  {len(selected['background'])}")
        print()
        
        print("Optimizing selected applications...")
        print()
        
        # Optimize all selected apps
        stats = self.optimize_selected_apps(selected)
        
        print()
        print("=" * 80)
        print(" " * 25 + "OPTIMIZATION COMPLETE")
        print("=" * 80)
        print()
        print(f"Total apps optimized: {stats['total']}")
        print(f"  Essential (High):   {stats['essential']}")
        print(f"  Productive (Normal): {stats['productive']}")
        print(f"  Background (Low):   {stats['background']}")
        print()
        print("All applications automatically selected and optimized!")
        print("=" * 80)
        print()
        
        return stats


def main():
    """Main function"""
    if not PSUTIL_AVAILABLE:
        print("[ERROR] psutil not available")
        print("Install with: pip install psutil")
        return 1
    
    optimizer = AutoSelectOptimizer()
    
    # Automatically select and optimize (no user input)
    stats = optimizer.run_auto_optimization()
    
    # Save optimization log
    log_path = optimizer.base_dir / "auto_optimization_log.json"
    try:
        import json
        from datetime import datetime
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'selected_apps': optimizer.selected_apps
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"Optimization log saved: {log_path.name}")
    except Exception as e:
        print(f"[WARNING] Failed to save log: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
