#!/usr/bin/env python3
"""
Auto Optimize Applications
==========================
Automatically detects and optimizes application priorities without user input.
Selects and optimizes apps intelligently based on system usage.
"""

import sys
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

class AutoAppOptimizer:
    """Automatically optimize applications without user input"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.optimized_apps = []
        self.priority_map = {
            'high': psutil.HIGH_PRIORITY_CLASS if PSUTIL_AVAILABLE else None,
            'normal': psutil.NORMAL_PRIORITY_CLASS if PSUTIL_AVAILABLE else None,
            'low': psutil.BELOW_NORMAL_PRIORITY_CLASS if PSUTIL_AVAILABLE else None
        }
        
        # Apps that should be high priority (Omega-related)
        self.high_priority_apps = [
            'omega',
            'python',
            'cursor',
            'code',
            'powershell',
            'cmd'
        ]
        
        # Apps that can be low priority (background/browser)
        self.low_priority_apps = [
            'chrome',
            'firefox',
            'edge',
            'spotify',
            'discord',
            'steam',
            'battle.net'
        ]
    
    def detect_running_apps(self) -> List[Dict]:
        """Detect all running applications"""
        if not PSUTIL_AVAILABLE:
            return []
        
        apps = []
        current_pid = os.getpid()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'memory_info', 'cpu_percent']):
                try:
                    pinfo = proc.info
                    
                    # Skip system processes and current process
                    if pinfo['pid'] == current_pid or pinfo['pid'] == 0:
                        continue
                    
                    # Skip processes without name
                    if not pinfo['name']:
                        continue
                    
                    app_name = pinfo['name'].lower()
                    exe_path = pinfo['exe'] if pinfo['exe'] else ""
                    
                    # Get memory usage
                    memory_mb = 0
                    if pinfo['memory_info']:
                        memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                    
                    apps.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'],
                        'exe': exe_path,
                        'memory_mb': memory_mb,
                        'cpu_percent': pinfo['cpu_percent'] if pinfo['cpu_percent'] else 0,
                        'app_name': app_name
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"[WARNING] Error detecting apps: {e}")
        
        return apps
    
    def determine_priority(self, app: Dict) -> str:
        """Automatically determine priority for an app (no user input)"""
        app_name = app['app_name']
        
        # Check for high priority apps
        for high_priority in self.high_priority_apps:
            if high_priority in app_name:
                return 'high'
        
        # Check for low priority apps
        for low_priority in self.low_priority_apps:
            if low_priority in app_name:
                return 'low'
        
        # Default to normal priority
        return 'normal'
    
    def optimize_app_priority(self, app: Dict, priority: str) -> bool:
        """Set application priority"""
        if not PSUTIL_AVAILABLE:
            return False
        
        try:
            proc = psutil.Process(app['pid'])
            priority_class = self.priority_map.get(priority)
            
            if priority_class is None:
                return False
            
            # Set priority (Windows)
            if sys.platform == 'win32':
                proc.nice(priority_class)
            else:
                # Unix-like systems
                if priority == 'high':
                    proc.nice(-5)
                elif priority == 'low':
                    proc.nice(5)
                else:
                    proc.nice(0)
            
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            return False
        except Exception as e:
            return False
    
    def auto_optimize_all_apps(self) -> Dict[str, int]:
        """Automatically optimize all detected apps (no user input)"""
        print("\n" + "=" * 80)
        print(" " * 25 + "AUTO APP OPTIMIZATION")
        print("=" * 80)
        print()
        print("Detecting running applications...")
        
        apps = self.detect_running_apps()
        print(f"[OK] Found {len(apps)} running applications")
        print()
        
        stats = {
            'total': len(apps),
            'high': 0,
            'normal': 0,
            'low': 0,
            'failed': 0
        }
        
        print("Optimizing applications automatically...")
        print()
        
        for app in apps:
            # Automatically determine priority (no user input)
            priority = self.determine_priority(app)
            
            # Optimize app
            success = self.optimize_app_priority(app, priority)
            
            if success:
                stats[priority] += 1
                self.optimized_apps.append({
                    'name': app['name'],
                    'pid': app['pid'],
                    'priority': priority
                })
                print(f"  [{priority.upper():6}] {app['name']:30} (PID: {app['pid']})")
            else:
                stats['failed'] += 1
        
        print()
        print("=" * 80)
        print(" " * 25 + "OPTIMIZATION COMPLETE")
        print("=" * 80)
        print()
        print(f"Total apps detected: {stats['total']}")
        print(f"High priority:       {stats['high']}")
        print(f"Normal priority:     {stats['normal']}")
        print(f"Low priority:        {stats['low']}")
        print(f"Failed:              {stats['failed']}")
        print()
        print("All applications optimized automatically!")
        print("=" * 80)
        print()
        
        return stats
    
    def optimize_specific_apps(self, app_names: List[str], priority: str = 'high') -> int:
        """Optimize specific apps by name"""
        if not PSUTIL_AVAILABLE:
            return 0
        
        apps = self.detect_running_apps()
        optimized_count = 0
        
        for app in apps:
            app_name = app['app_name']
            
            # Check if this app matches any in the list
            for target_name in app_names:
                if target_name.lower() in app_name:
                    success = self.optimize_app_priority(app, priority)
                    if success:
                        optimized_count += 1
                        print(f"  [{priority.upper()}] {app['name']} (PID: {app['pid']})")
                    break
        
        return optimized_count
    
    def get_optimization_status(self) -> Dict:
        """Get current optimization status"""
        return {
            'optimized_count': len(self.optimized_apps),
            'optimized_apps': self.optimized_apps
        }


def main():
    """Main function - automatically optimizes all apps"""
    if not PSUTIL_AVAILABLE:
        print("[ERROR] psutil not available")
        print("Install with: pip install psutil")
        return 1
    
    optimizer = AutoAppOptimizer()
    
    # Automatically optimize all apps (no user input required)
    stats = optimizer.auto_optimize_all_apps()
    
    # Save optimization log
    log_path = optimizer.base_dir / "app_optimization_log.json"
    try:
        import json
        from datetime import datetime
        
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'stats': stats,
            'optimized_apps': optimizer.optimized_apps
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"Optimization log saved: {log_path.name}")
    except Exception as e:
        print(f"[WARNING] Failed to save log: {e}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
