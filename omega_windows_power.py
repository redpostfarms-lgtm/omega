"""
Omega Windows Power Management
===============================
System power control: restart, shutdown, sleep, hibernate, and scheduled operations.
"""

import os
import sys
import subprocess
import platform
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List

class WindowsPowerManager:
    """Windows power management system"""
    
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
    
    def shutdown(self, delay_seconds: int = 0, reason: str = "Omega system shutdown", force: bool = False, optimize: bool = True):
        """Shutdown Windows system - optimized to 5 seconds or less with process spacing"""
        try:
            if optimize and delay_seconds > 0:
                try:
                    import psutil
                    import time
                    current_pid = os.getpid()
                    processes_to_close = []
                    
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            pinfo = proc.info
                            if pinfo['pid'] == current_pid:
                                continue
                            proc_name = pinfo['name'].lower()
                            if 'python' in proc_name and 'omega' not in proc_name.lower():
                                processes_to_close.append(pinfo['pid'])
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue
                    
                    for pid in processes_to_close[:10]:
                        try:
                            proc = psutil.Process(pid)
                            proc.terminate()
                            time.sleep(0.1)  # Space out process closures
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    if processes_to_close:
                        time.sleep(0.3)  # Brief pause after process cleanup
                except ImportError:
                    pass  # psutil not available - skip optimization
                except Exception:
                    pass  # Continue even if optimization fails
            
            if force or delay_seconds == 0:
                cmd = f'shutdown /s /f /t 0 /c "{reason}"'
            elif delay_seconds <= 5:
                cmd = f'shutdown /s /f /t {delay_seconds} /c "{reason}"'
            else:
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
            subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True, check=True)
            return True, "System entering sleep mode"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def hibernate(self):
        """Hibernate system"""
        try:
            subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 1,1,0', shell=True, check=True)
            return True, "System entering hibernate mode"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def schedule_shutdown(self, shutdown_time: datetime, reason: str = "Scheduled shutdown"):
        """Schedule a shutdown at specific time"""
        try:
            now = datetime.now()
            if shutdown_time <= now:
                return False, "Shutdown time must be in the future"
            
            delta = shutdown_time - now
            seconds = int(delta.total_seconds())
            
            cmd = f'shutdown /s /t {seconds} /c "{reason}"'
            subprocess.run(cmd, shell=True, check=True)
            
            schedule_entry = {
                "type": "shutdown",
                "time": shutdown_time.isoformat(),
                "reason": reason,
                "created": now.isoformat()
            }
            self.config["scheduled_shutdowns"].append(schedule_entry)
            self.save_config()
            
            return True, f"Shutdown scheduled for {shutdown_time.strftime('%Y-%m-%d %H:%M:%S')}"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def schedule_wake(self, wake_time: datetime, description: str = "Scheduled wake"):
        """Schedule system wake-up using Task Scheduler"""
        try:
            now = datetime.now()
            if wake_time <= now:
                return False, "Wake time must be in the future"
            
            task_name = f"Omega_Wake_{wake_time.strftime('%Y%m%d_%H%M%S')}"
            
            wake_cmd = f'schtasks /Create /TN "{task_name}" /TR "cmd /c echo Wake" /SC ONCE /ST {wake_time.strftime("%H:%M")} /SD {wake_time.strftime("%m/%d/%Y")} /F'
            subprocess.run(wake_cmd, shell=True, check=True)
            
            subprocess.run('powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1', shell=True)
            subprocess.run('powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1', shell=True)
            subprocess.run('powercfg /SETACTIVE SCHEME_CURRENT', shell=True)
            
            wake_entry = {
                "type": "wake",
                "time": wake_time.isoformat(),
                "description": description,
                "task_name": task_name,
                "created": now.isoformat()
            }
            self.config["wake_timers"].append(wake_entry)
            self.save_config()
            
            return True, f"Wake scheduled for {wake_time.strftime('%Y-%m-%d %H:%M:%S')}"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def schedule_sleep(self, sleep_time: datetime, description: str = "Scheduled sleep"):
        """Schedule system sleep at specific time"""
        try:
            now = datetime.now()
            if sleep_time <= now:
                return False, "Sleep time must be in the future"
            
            delta = sleep_time - now
            seconds = int(delta.total_seconds())
            
            task_name = f"Omega_Sleep_{sleep_time.strftime('%Y%m%d_%H%M%S')}"
            sleep_script = f'@echo off\ntimeout /t {seconds} /nobreak\nrundll32.exe powrprof.dll,SetSuspendState 0,1,0'
            
            script_file = Path(f"{task_name}.bat")
            with open(script_file, 'w') as f:
                f.write(sleep_script)
            
            cmd = f'schtasks /Create /TN "{task_name}" /TR "{script_file.absolute()}" /SC ONCE /ST {sleep_time.strftime("%H:%M")} /SD {sleep_time.strftime("%m/%d/%Y")} /F'
            subprocess.run(cmd, shell=True, check=True)
            
            sleep_entry = {
                "type": "sleep",
                "time": sleep_time.isoformat(),
                "description": description,
                "task_name": task_name,
                "created": now.isoformat()
            }
            self.config["sleep_timers"].append(sleep_entry)
            self.save_config()
            
            return True, f"Sleep scheduled for {sleep_time.strftime('%Y-%m-%d %H:%M:%S')}"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def get_scheduled_tasks(self) -> Dict:
        """Get all scheduled power tasks"""
        return {
            "shutdowns": self.config.get("scheduled_shutdowns", []),
            "wake_timers": self.config.get("wake_timers", []),
            "sleep_timers": self.config.get("sleep_timers", [])
        }
    
    def cancel_scheduled_shutdown(self):
        """Cancel any pending scheduled shutdown"""
        return self.cancel_shutdown()
    
    def cancel_scheduled_task(self, task_name: str):
        """Cancel a specific scheduled task"""
        try:
            subprocess.run(f'schtasks /Delete /TN "{task_name}" /F', shell=True, check=True)
            
            for task_list in ["wake_timers", "sleep_timers"]:
                self.config[task_list] = [t for t in self.config.get(task_list, []) if t.get("task_name") != task_name]
            self.save_config()
            
            return True, f"Task {task_name} cancelled"
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e}"
    
    def list_scheduled_tasks(self):
        """List all scheduled power tasks"""
        tasks = self.get_scheduled_tasks()
        
        print("\n" + "=" * 80)
        print("SCHEDULED POWER TASKS")
        print("=" * 80)
        
        if tasks["shutdowns"]:
            print("\nScheduled Shutdowns:")
            for shutdown in tasks["shutdowns"]:
                time_str = datetime.fromisoformat(shutdown["time"]).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  - {time_str}: {shutdown.get('reason', 'No reason')}")
        
        if tasks["wake_timers"]:
            print("\nWake Timers:")
            for wake in tasks["wake_timers"]:
                time_str = datetime.fromisoformat(wake["time"]).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  - {time_str}: {wake.get('description', 'No description')}")
        
        if tasks["sleep_timers"]:
            print("\nSleep Timers:")
            for sleep in tasks["sleep_timers"]:
                time_str = datetime.fromisoformat(sleep["time"]).strftime("%Y-%m-%d %H:%M:%S")
                print(f"  - {time_str}: {sleep.get('description', 'No description')}")
        
        if not any(tasks.values()):
            print("\nNo scheduled tasks")
        
        print("=" * 80)


def get_power_manager() -> WindowsPowerManager:
    """Get or create power manager instance"""
    return WindowsPowerManager()


if __name__ == "__main__":
    pm = get_power_manager()
    
    print("=" * 80)
    print("OMEGA WINDOWS POWER MANAGEMENT")
    print("=" * 80)
    print()
    print("Commands:")
    print("  shutdown [delay_seconds] - Shutdown system")
    print("  restart [delay_seconds] - Restart system")
    print("  sleep - Put system to sleep")
    print("  hibernate - Hibernate system")
    print("  schedule_shutdown <time> - Schedule shutdown (format: YYYY-MM-DD HH:MM)")
    print("  schedule_wake <time> - Schedule wake (format: YYYY-MM-DD HH:MM)")
    print("  schedule_sleep <time> - Schedule sleep (format: YYYY-MM-DD HH:MM)")
    print("  list - List scheduled tasks")
    print("  cancel - Cancel pending shutdown")
    print("  exit - Exit")
    print()
    
    while True:
        try:
            cmd = input("Power> ").strip().split()
            if not cmd:
                continue
            
            action = cmd[0].lower()
            
            if action == "exit":
                break
            elif action == "shutdown":
                delay = int(cmd[1]) if len(cmd) > 1 else 0
                success, msg = pm.shutdown(delay)
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            elif action == "restart":
                delay = int(cmd[1]) if len(cmd) > 1 else 0
                success, msg = pm.restart(delay)
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            elif action == "sleep":
                success, msg = pm.sleep()
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            elif action == "hibernate":
                success, msg = pm.hibernate()
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            elif action == "schedule_shutdown":
                if len(cmd) < 2:
                    print("Usage: schedule_shutdown YYYY-MM-DD HH:MM")
                    continue
                time_str = " ".join(cmd[1:])
                try:
                    shutdown_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    success, msg = pm.schedule_shutdown(shutdown_time)
                    print(f"[{'OK' if success else 'ERROR'}] {msg}")
                except ValueError:
                    print("Invalid time format. Use: YYYY-MM-DD HH:MM")
            elif action == "schedule_wake":
                if len(cmd) < 2:
                    print("Usage: schedule_wake YYYY-MM-DD HH:MM")
                    continue
                time_str = " ".join(cmd[1:])
                try:
                    wake_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    success, msg = pm.schedule_wake(wake_time)
                    print(f"[{'OK' if success else 'ERROR'}] {msg}")
                except ValueError:
                    print("Invalid time format. Use: YYYY-MM-DD HH:MM")
            elif action == "schedule_sleep":
                if len(cmd) < 2:
                    print("Usage: schedule_sleep YYYY-MM-DD HH:MM")
                    continue
                time_str = " ".join(cmd[1:])
                try:
                    sleep_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    success, msg = pm.schedule_sleep(sleep_time)
                    print(f"[{'OK' if success else 'ERROR'}] {msg}")
                except ValueError:
                    print("Invalid time format. Use: YYYY-MM-DD HH:MM")
            elif action == "list":
                pm.list_scheduled_tasks()
            elif action == "cancel":
                success, msg = pm.cancel_shutdown()
                print(f"[{'OK' if success else 'ERROR'}] {msg}")
            else:
                print(f"Unknown command: {action}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
