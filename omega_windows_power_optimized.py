#!/usr/bin/env python3
"""
Omega Windows Power Management - Optimized
===========================================
System power control with optimized process management for smooth shutdown.
"""

import os
import sys
import subprocess
import platform
import json
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List

class WindowsPowerManagerOptimized:
    """Windows power management system with optimized process handling"""
    
    def __init__(self, config_file: str = "omega_power_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        
        if platform.system() != "Windows":
            raise RuntimeError("This module is for Windows only")
    
    def load_config(self) -> Dict:
        """Load power configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            "scheduled_shutdowns": [],
            "wake_timers": [],
            "sleep_timers": []
        }
    
    def save_config(self):
        """Save power configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _close_processes_gracefully(self, delay_between: float = 0.1):
        """Close non-essential processes gracefully with spacing"""
        try:
            current_pid = os.getpid()
            processes_to_close = []
            
            # Get list of non-essential processes
            for proc in psutil.process_iter(['pid', 'name', 'ppid']):
                try:
                    pinfo = proc.info
                    # Skip system processes and current process
                    if pinfo['pid'] == current_pid or pinfo['ppid'] == 0:
                        continue
                    
                    proc_name = pinfo['name'].lower()
                    # Skip critical system processes
                    critical = ['csrss.exe', 'winlogon.exe', 'services.exe', 'lsass.exe', 
                               'smss.exe', 'svchost.exe', 'dwm.exe', 'explorer.exe']
                    if proc_name in critical:
                        continue
                    
                    # Add non-essential processes (Python scripts, etc.)
                    if 'python' in proc_name or proc_name.endswith('.exe'):
                        processes_to_close.append(pinfo['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Close processes with spacing to prevent system bogging
            closed_count = 0
            for pid in processes_to_close[:20]:  # Limit to 20 to avoid overwhelming
                try:
                    proc = psutil.Process(pid)
                    proc.terminate()  # Graceful termination
                    closed_count += 1
                    time.sleep(delay_between)  # Space out process closures
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Give processes time to close
            if closed_count > 0:
                time.sleep(0.5)
            
            return closed_count
            
        except ImportError:
            # psutil not available - skip process management
            return 0
        except Exception as e:
            print(f"Warning: Process cleanup failed: {e}")
            return 0
    
    def shutdown(self, delay_seconds: int = 0, reason: str = "Omega system shutdown", force: bool = False, optimize: bool = True):
        """Shutdown Windows system - optimized to prevent system bogging"""
        try:
            # Optimize by closing processes gracefully first (if requested)
            if optimize and delay_seconds > 0:
                print("[Shutdown] Optimizing processes...")
                self._close_processes_gracefully(delay_between=0.1)
                time.sleep(0.5)  # Brief pause after process cleanup
            
            # Force immediate shutdown if requested (5 seconds max)
            if force or delay_seconds == 0:
                # Use /f to force close applications without waiting
                # Use /t 0 for immediate shutdown (minimum Windows allows)
                cmd = f'shutdown /s /f /t 0 /c "{reason}"'
            elif delay_seconds <= 5:
                # If delay is 5 seconds or less, use force close
                cmd = f'shutdown /s /f /t {delay_seconds} /c "{reason}"'
            else:
                # Longer delays don't force close (allows saves)
                cmd = f'shutdown /s /t {delay_seconds} /c "{reason}"'
            
            subprocess.run(cmd, shell=True, check=True)
            actual_delay = 0 if force else delay_seconds
            return True, f"System will shutdown in {actual_delay} seconds"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def restart(self, delay_seconds: int = 0, reason: str = "Omega system restart"):
        """Restart Windows system"""
        try:
            if delay_seconds > 0:
                cmd = f'shutdown /r /t {delay_seconds} /c "{reason}"'
            else:
                cmd = f'shutdown /r /t 0 /c "{reason}"'
            subprocess.run(cmd, shell=True, check=True)
            return True, f"System will restart in {delay_seconds} seconds"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def cancel_shutdown(self):
        """Cancel pending shutdown/restart"""
        try:
            subprocess.run('shutdown /a', shell=True, check=True)
            return True, "Shutdown cancelled"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def sleep(self):
        """Put system to sleep"""
        try:
            # Windows sleep command
            subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True, check=True)
            return True, "System entering sleep mode"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def hibernate(self):
        """Hibernate system"""
        try:
            # Windows hibernate command
            subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 1,1,0', shell=True, check=True)
            return True, "System entering hibernate mode"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"


def get_power_manager_optimized() -> WindowsPowerManagerOptimized:
    """Get or create optimized power manager instance"""
    return WindowsPowerManagerOptimized()


if __name__ == "__main__":
    pm = get_power_manager_optimized()
    
    print("=" * 80)
    print("OMEGA WINDOWS POWER MANAGEMENT - OPTIMIZED")
    print("=" * 80)
    print()
    print("Optimized shutdown with process spacing to prevent system bogging.")
    print()
    
    # Test shutdown with optimization
    print("Testing optimized shutdown...")
    success, msg = pm.shutdown(force=True, optimize=True)
    print(f"[{'OK' if success else 'ERROR'}] {msg}")
