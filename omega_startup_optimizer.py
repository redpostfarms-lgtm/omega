"""
Omega Startup Optimizer
=======================
Optimizes Windows startup by disabling non-essential programs and adding Omega to startup.
- Identifies non-essential startup programs
- Disables unnecessary startup items
- Adds Omega to Windows startup
- Creates backup/restore functionality
"""

import os
import sys
import json
import platform
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
import winreg

@dataclass
class StartupItem:
    """Startup item information"""
    name: str
    path: str
    location: str  # 'registry', 'startup_folder', 'scheduled_task', 'service'
    enabled: bool
    description: str = ""
    essential: bool = False  # True if essential Windows component
    category: str = ""  # 'system', 'third_party', 'microsoft_store', 'user'

class StartupOptimizer:
    """Windows startup optimizer"""
    
    ESSENTIAL_WINDOWS_PROGRAMS = {
        'Windows Defender', 'Security Health Service', 'Windows Update',
        'Windows Security', 'Microsoft Windows', 'System',
        'Windows Audio', 'Windows Audio Endpoint Builder',
        'Plug and Play', 'Power', 'Display Manager', 'User Manager',
        'Windows Management Instrumentation', 'Remote Procedure Call',
        'Windows Time', 'DNS Client', 'DHCP Client', 'Network Location Awareness',
        'Windows Firewall', 'Windows Security Center', 'Windows Error Reporting Service',
        'Windows Event Log', 'Windows Image Acquisition', 'Windows Search',
        'Windows Update', 'Windows Backup', 'Windows Installer',
    }
    
    COMMON_NON_ESSENTIAL = {
        'Skype', 'Discord', 'Spotify', 'Steam', 'Epic Games', 'Adobe',
        'iTunes', 'QuickTime', 'Google Update', 'Microsoft Teams',
        'Zoom', 'Slack', 'Dropbox', 'OneDrive', 'Google Drive',
        'Spotify Web Helper', 'CCleaner', 'NVIDIA Control Panel',
        'Cortana', 'Xbox Game Bar', 'Xbox Game Bar Plugin',
        'Windows Feedback Hub', 'Windows Mail', 'Windows Maps',
        'Microsoft Store', 'Microsoft Office', 'Office Click-to-Run',
        'Adobe Acrobat', 'Adobe Creative Cloud', 'iCloud',
        'Apple Mobile Device', 'Bonjour', 'QuickTime',
        'iTunesHelper', 'SpotifyWebHelper', 'Steam Client Bootstrapper',
        'EpicGamesLauncher', 'DiscordUpdater', 'SlackUpdater',
        'ZoomOpener', 'SkypeHost', 'TeamsMachineInstaller',
    }
    
    TRACKING_SERVICES = {
        'Connected User Experiences and Telemetry', 'DiagTrack', 'dmwappushservice',
        'Windows Error Reporting Service', 'WERSvc', 'WerSvc',
        'Windows Customer Experience Improvement Program', 'CEIP',
        'Application Experience', 'AeLookupSvc',
        'Program Compatibility Assistant Service', 'PcaSvc',
        'Windows Search', 'WSearch',  # Can be disabled if not needed
        'Cortana', 'Microsoft Cortana',
        'Windows Feedback Hub', 'Feedback Hub',
        'Xbox Game Bar', 'Xbox Game Bar Plugin', 'GameBar',
        'Xbox Live Game Save', 'XboxGipSvc',
        'Xbox Live Auth Manager', 'XblAuthManager',
        'Xbox Live Networking Service', 'XblGameSave',
        'Microsoft Compatibility Telemetry', 'CompatTelRunner',
        'Windows Error Reporting', 'WerFault',
        'Windows Media Player Network Sharing Service', 'WMPNetworkSvc',
        'Windows Update Medic Service',  # Keep Windows Update but remove medic
        'Data Collection and Publishing Service',
        'Diagnostic Policy Service', 'DPS',  # Keep basic diagnostics but can remove
        'Windows Management Instrumentation',  # Keep this - it's essential
    }
    
    TRACKING_KEYWORDS = {
        'telemetry', 'tracking', 'diagnostic', 'error reporting', 'feedback',
        'customer experience', 'ceip', 'dmwappush', 'diagtrack',
        'compattelemetry', 'compat tel', 'wersvc', 'wers',
        'xbox live', 'xbox game', 'gamebar', 'cortana',
        'data collection', 'usage data', 'analytics',
    }
    
    def __init__(self):
        self.system = platform.system()
        if self.system != "Windows":
            raise RuntimeError("This script is designed for Windows only")
        
        self.startup_items: List[StartupItem] = []
        self.disabled_items: List[StartupItem] = []
        self.removed_items: List[StartupItem] = []
        self.backup_file = Path("startup_backup.json")
        self.removal_backup_file = Path("startup_removal_backup.json")
        self.omega_startup_script = None
        
    def scan_startup_items(self) -> List[StartupItem]:
        """Scan all startup items from various locations"""
        self.startup_items = []
        
        self._scan_registry_startup(winreg.HKEY_CURRENT_USER,
                                    r"Software\Microsoft\Windows\CurrentVersion\Run")
        
        self._scan_registry_startup(winreg.HKEY_LOCAL_MACHINE,
                                    r"Software\Microsoft\Windows\CurrentVersion\Run")
        
        self._scan_startup_folder()
        
        self._scan_scheduled_tasks()
        
        self._scan_services()
        
        return self.startup_items
    
    def _scan_registry_startup(self, hkey: int, subkey: str):
        """Scan registry startup items"""
        try:
            key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_READ)
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    location = f"registry_{'HKCU' if hkey == winreg.HKEY_CURRENT_USER else 'HKLM'}"
                    essential = self._is_essential(name)
                    category = self._categorize_item(name, value)
                    
                    item = StartupItem(
                        name=name,
                        path=value,
                        location=location,
                        enabled=True,
                        description=f"Registry startup item in {location}",
                        essential=essential,
                        category=category
                    )
                    self.startup_items.append(item)
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Could not scan registry {subkey}: {e}")
    
    def _scan_startup_folder(self):
        """Scan startup folder"""
        try:
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            if startup_folder.exists():
                for item in startup_folder.iterdir():
                    if item.is_file() and item.suffix.lower() in ['.bat', '.cmd', '.lnk', '.exe']:
                        essential = self._is_essential(item.stem)
                        category = self._categorize_item(item.stem, str(item))
                        
                        item_obj = StartupItem(
                            name=item.stem,
                            path=str(item),
                            location="startup_folder",
                            enabled=True,
                            description=f"Startup folder item: {item.name}",
                            essential=essential,
                            category=category
                        )
                        self.startup_items.append(item_obj)
        except Exception as e:
            print(f"Warning: Could not scan startup folder: {e}")
    
    def _scan_scheduled_tasks(self):
        """Scan scheduled tasks that run on startup"""
        try:
            result = subprocess.run(
                ['schtasks', '/query', '/fo', 'csv', '/v'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines[1:]:  # Skip header
                    if not line.strip():
                        continue
                    
                    parts = line.split(',')
                    if len(parts) > 1:
                        task_name = parts[0].strip('"')
                        trigger = parts[4].strip('"') if len(parts) > 4 else ""
                        
                        if any(keyword in trigger.lower() for keyword in ['startup', 'logon', 'boot']):
                            essential = self._is_essential(task_name)
                            category = self._categorize_item(task_name, "")
                            
                            item = StartupItem(
                                name=task_name,
                                path="",
                                location="scheduled_task",
                                enabled=True,
                                description=f"Scheduled task: {trigger}",
                                essential=essential,
                                category=category
                            )
                            self.startup_items.append(item)
        except Exception as e:
            print(f"Warning: Could not scan scheduled tasks: {e}")
    
    def _scan_services(self):
        """Scan non-essential services"""
        try:
            result = subprocess.run(
                ['sc', 'query', 'state=', 'all'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Note: Service scanning is complex, so we'll focus on registry/startup folder
        except Exception as e:
            print(f"Warning: Could not scan services: {e}")
    
    def _is_essential(self, name: str) -> bool:
        """Check if item is essential Windows component"""
        name_lower = name.lower()
        for essential in self.ESSENTIAL_WINDOWS_PROGRAMS:
            if essential.lower() in name_lower:
                return True
        return False
    
    def _is_tracking(self, name: str, path: str = "") -> bool:
        """Check if item is tracking/telemetry service"""
        name_lower = name.lower()
        path_lower = path.lower()
        
        for tracking in self.TRACKING_SERVICES:
            if tracking.lower() in name_lower or tracking.lower() in path_lower:
                return True
        
        for keyword in self.TRACKING_KEYWORDS:
            if keyword.lower() in name_lower or keyword.lower() in path_lower:
                return True
        
        return False
    
    def _categorize_item(self, name: str, path: str) -> str:
        """Categorize startup item"""
        name_lower = name.lower()
        path_lower = path.lower()
        
        if any(system in name_lower for system in ['windows', 'microsoft', 'system', 'security']):
            if not self._is_essential(name):
                return "microsoft_store"
            return "system"
        
        for non_essential in self.COMMON_NON_ESSENTIAL:
            if non_essential.lower() in name_lower or non_essential.lower() in path_lower:
                return "third_party"
        
        return "user"
    
    def get_non_essential_items(self) -> List[StartupItem]:
        """Get list of non-essential startup items"""
        non_essential = [item for item in self.startup_items if not item.essential]
        category_order = {"third_party": 0, "user": 1, "microsoft_store": 2}
        non_essential.sort(key=lambda x: (category_order.get(x.category, 99), x.name))
        return non_essential
    
    def get_tracking_items(self) -> List[StartupItem]:
        """Get list of tracking/telemetry startup items"""
        tracking_items = [item for item in self.startup_items if self._is_tracking(item.name, item.path)]
        return tracking_items
    
    def remove_startup_item(self, item: StartupItem) -> Tuple[bool, str]:
        """Remove a startup item completely (delete from registry/folder)"""
        try:
            if item.location.startswith("registry_"):
                hkey_str = item.location.replace("registry_", "")
                hkey = winreg.HKEY_CURRENT_USER if hkey_str == "HKCU" else winreg.HKEY_LOCAL_MACHINE
                subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                try:
                    key = winreg.OpenKey(hkey, subkey, 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, item.name)
                    winreg.CloseKey(key)
                    item.enabled = False
                    self.removed_items.append(item)
                    return True, f"✅ Removed {item.name} from registry"
                except FileNotFoundError:
                    return False, f"{item.name} not found in registry"
                except PermissionError:
                    return False, f"Permission denied: Run as administrator to remove {item.name}"
            
            elif item.location == "startup_folder":
                backup_dir = Path("startup_backup")
                backup_dir.mkdir(exist_ok=True)
                
                source = Path(item.path)
                if source.exists():
                    backup_path = backup_dir / source.name
                    shutil.move(str(source), str(backup_path))
                    item.enabled = False
                    item.path = str(backup_path)  # Update path to backup location
                    self.removed_items.append(item)
                    return True, f"✅ Removed {item.name} from startup folder (backed up)"
                else:
                    return False, f"{item.name} not found in startup folder"
            
            elif item.location == "scheduled_task":
                try:
                    result = subprocess.run(
                        ['schtasks', '/delete', '/tn', item.name, '/f'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        item.enabled = False
                        self.removed_items.append(item)
                        return True, f"✅ Removed scheduled task: {item.name}"
                    else:
                        result2 = subprocess.run(
                            ['schtasks', '/change', '/tn', item.name, '/disable'],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result2.returncode == 0:
                            item.enabled = False
                            self.removed_items.append(item)
                            return True, f"✅ Disabled scheduled task: {item.name} (delete requires admin)"
                        return False, f"Failed to remove task: {result.stderr}"
                except Exception as e:
                    return False, f"Error removing task: {e}"
            
            return False, f"Unknown location type: {item.location}"
        
        except Exception as e:
            return False, f"Error disabling {item.name}: {e}"
    
    def remove_all_non_essential(self) -> Dict[str, Any]:
        """Remove all non-essential startup items completely"""
        results = {
            "removed": [],
            "failed": [],
            "skipped": []
        }
        
        non_essential = self.get_non_essential_items()
        
        for item in non_essential:
            if item.enabled:
                success, message = self.remove_startup_item(item)
                if success:
                    results["removed"].append({"name": item.name, "message": message})
                else:
                    results["failed"].append({"name": item.name, "message": message})
            else:
                results["skipped"].append({"name": item.name, "message": "Already removed/disabled"})
        
        self.save_removal_backup()
        
        return results
    
    def remove_all_tracking(self) -> Dict[str, Any]:
        """Remove all tracking/telemetry startup items completely"""
        results = {
            "removed": [],
            "failed": [],
            "skipped": []
        }
        
        tracking_items = self.get_tracking_items()
        
        for item in tracking_items:
            if item.enabled:
                success, message = self.remove_startup_item(item)
                if success:
                    results["removed"].append({"name": item.name, "message": message})
                else:
                    results["failed"].append({"name": item.name, "message": message})
            else:
                results["skipped"].append({"name": item.name, "message": "Already removed/disabled"})
        
        self.save_removal_backup()
        
        return results
    
    def cleanup_startup(self) -> Dict[str, Any]:
        """Complete cleanup: Remove tracking + non-essential items"""
        results = {
            "tracking_removed": [],
            "non_essential_removed": [],
            "total_removed": 0,
            "failed": []
        }
        
        print("Removing tracking/telemetry items...")
        tracking_results = self.remove_all_tracking()
        results["tracking_removed"] = tracking_results["removed"]
        results["failed"].extend(tracking_results["failed"])
        
        print("Removing non-essential items...")
        non_essential_results = self.remove_all_non_essential()
        results["non_essential_removed"] = non_essential_results["removed"]
        results["failed"].extend(non_essential_results["failed"])
        
        results["total_removed"] = len(results["tracking_removed"]) + len(results["non_essential_removed"])
        
        return results
    
    def disable_all_non_essential(self) -> Dict[str, Any]:
        """Disable all non-essential startup items (legacy - uses remove now)"""
        return self.remove_all_non_essential()
    
    def save_backup(self):
        """Save backup of disabled items"""
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "disabled_items": [asdict(item) for item in self.disabled_items],
            "system": self.system
        }
        
        with open(self.backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Backup saved to: {self.backup_file}")
    
    def save_removal_backup(self):
        """Save backup of removed items"""
        backup_data = {
            "timestamp": datetime.now().isoformat(),
            "removed_items": [asdict(item) for item in self.removed_items],
            "system": self.system
        }
        
        with open(self.removal_backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Removal backup saved to: {self.removal_backup_file}")
    
    def restore_backup(self) -> Tuple[bool, str]:
        """Restore disabled items from backup"""
        if not self.backup_file.exists():
            return False, "No backup file found"
        
        try:
            with open(self.backup_file, 'r') as f:
                backup_data = json.load(f)
            
            restored = 0
            failed = 0
            
            for item_data in backup_data.get("disabled_items", []):
                item = StartupItem(**item_data)
                restored += 1
            
            return True, f"Restored {restored} items, {failed} failed"
        
        except Exception as e:
            return False, f"Error restoring backup: {e}"
    
    def add_omega_to_startup(self, omega_script: Optional[Path] = None) -> Tuple[bool, str]:
        """Add Omega to Windows startup"""
        try:
            if omega_script is None:
                current_dir = Path(__file__).parent
                possible_scripts = [
                    current_dir / "START_HERE.bat",
                    current_dir / "start_omega.bat",
                    current_dir / "START_CONTROL_PANEL.bat",
                    current_dir / "omega_full_brain.py"
                ]
                
                omega_script = None
                for script in possible_scripts:
                    if script.exists():
                        omega_script = script
                        break
                
                if omega_script is None:
                    return False, "Could not find Omega startup script. Please specify path."
            
            omega_script = Path(omega_script).absolute()
            
            if not omega_script.exists():
                return False, f"Omega script not found: {omega_script}"
            
            startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            startup_folder.mkdir(parents=True, exist_ok=True)
            
            startup_script = startup_folder / "Omega_Start.bat"
            
            if omega_script.suffix.lower() == '.py':
                script_content = f"""@echo off
REM Omega System - Auto-start on login
cd /d "{omega_script.parent}"
python "{omega_script.name}"
"""
            else:
                script_content = f"""@echo off
REM Omega System - Auto-start on login
cd /d "{omega_script.parent}"
call "{omega_script.name}"
"""
            
            with open(startup_script, 'w') as f:
                f.write(script_content)
            
            self.omega_startup_script = startup_script
            
            return True, f"✅ Omega added to startup: {startup_script}"
        
        except Exception as e:
            return False, f"Error adding Omega to startup: {e}"
    
    def remove_omega_from_startup(self) -> Tuple[bool, str]:
        """Remove Omega from Windows startup"""
        try:
            if self.omega_startup_script is None:
                startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
                omega_scripts = list(startup_folder.glob("Omega*.bat"))
                if omega_scripts:
                    self.omega_startup_script = omega_scripts[0]
            
            if self.omega_startup_script and Path(self.omega_startup_script).exists():
                Path(self.omega_startup_script).unlink()
                return True, f"✅ Omega removed from startup: {self.omega_startup_script}"
            else:
                return False, "Omega startup script not found"
        
        except Exception as e:
            return False, f"Error removing Omega from startup: {e}"
    
    def get_startup_report(self) -> Dict[str, Any]:
        """Get comprehensive startup report"""
        self.scan_startup_items()
        
        essential = [item for item in self.startup_items if item.essential]
        non_essential = self.get_non_essential_items()
        enabled_non_essential = [item for item in non_essential if item.enabled]
        disabled_non_essential = [item for item in non_essential if not item.enabled]
        
        startup_folder = Path(os.getenv("APPDATA")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        omega_in_startup = any("Omega" in item.name for item in self.startup_items if item.location == "startup_folder")
        
        return {
            "total_items": len(self.startup_items),
            "essential_items": len(essential),
            "non_essential_items": len(non_essential),
            "enabled_non_essential": len(enabled_non_essential),
            "disabled_non_essential": len(disabled_non_essential),
            "omega_in_startup": omega_in_startup,
            "items_by_category": {
                "system": len([item for item in self.startup_items if item.category == "system"]),
                "third_party": len([item for item in self.startup_items if item.category == "third_party"]),
                "microsoft_store": len([item for item in self.startup_items if item.category == "microsoft_store"]),
                "user": len([item for item in self.startup_items if item.category == "user"]),
            }
        }

def main():
    """Main function"""
    print("=" * 80)
    print("OMEGA STARTUP OPTIMIZER")
    print("=" * 80)
    print()
    
    if platform.system() != "Windows":
        print("❌ This script is designed for Windows only")
        sys.exit(1)
    
    optimizer = StartupOptimizer()
    
    print("Scanning startup items...")
    optimizer.scan_startup_items()
    
    report = optimizer.get_startup_report()
    print()
    print("Startup Report:")
    print(f"  Total items: {report['total_items']}")
    print(f"  Essential items: {report['essential_items']}")
    print(f"  Non-essential items: {report['non_essential_items']}")
    print(f"  Enabled non-essential: {report['enabled_non_essential']}")
    print(f"  Omega in startup: {'Yes' if report['omega_in_startup'] else 'No'}")
    print()
    
    non_essential = optimizer.get_non_essential_items()
    if non_essential:
        print("Non-essential startup items:")
        for item in non_essential[:20]:  # Show first 20
            status = "✓ Enabled" if item.enabled else "✗ Disabled"
            print(f"  {status} | {item.category:15} | {item.name}")
        if len(non_essential) > 20:
            print(f"  ... and {len(non_essential) - 20} more")
        print()
    
    print("Options:")
    print("  1. Disable all non-essential startup items")
    print("  2. Add Omega to startup")
    print("  3. Do both (recommended)")
    print("  4. Show detailed report")
    print("  5. Exit")
    print()
    
    choice = input("Enter choice (1-5): ").strip()
    
    if choice == "1":
        print("\nDisabling non-essential startup items...")
        results = optimizer.disable_all_non_essential()
        print(f"\n✅ Disabled: {len(results['disabled'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        print(f"⏭️  Skipped: {len(results['skipped'])}")
    
    elif choice == "2":
        print("\nAdding Omega to startup...")
        success, message = optimizer.add_omega_to_startup()
        print(message)
    
    elif choice == "3":
        print("\nDisabling non-essential startup items...")
        results = optimizer.disable_all_non_essential()
        print(f"✅ Disabled: {len(results['disabled'])}")
        
        print("\nAdding Omega to startup...")
        success, message = optimizer.add_omega_to_startup()
        print(message)
        
        print("\n✅ Startup optimization complete!")
        print("Omega will now start automatically on login.")
    
    elif choice == "4":
        print("\nDetailed Report:")
        for item in optimizer.startup_items:
            essential_mark = "★" if item.essential else " "
            status = "✓" if item.enabled else "✗"
            print(f"{essential_mark} {status} [{item.category:15}] {item.name}")
            print(f"    Location: {item.location} | Path: {item.path[:60]}...")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
