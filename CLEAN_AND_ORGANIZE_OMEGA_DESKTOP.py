#!/usr/bin/env python3
"""
Clean and Organize Omega Desktop
=================================
Removes old desktop icons, organizes files, and creates new Omega UI launcher.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime

class OmegaDesktopOrganizer:
    """Organizes desktop icons and creates Omega UI launcher"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.desktop_dir = Path.home() / "Desktop"
        self.options_dir = self.base_dir / "Options"
        self.omega_ui_launcher = "OMEGA_UI_LAUNCHER.py"
        
        # Files to organize (old shortcuts and related files)
        self.old_shortcuts = [
            "Omega.lnk",
            "OMEGA.lnk",
            "omega.lnk",
            "Omega Voice AI.lnk",
            "Omega Control Panel.lnk",
            "Control Panel.lnk",
            "START_OMEGA.lnk",
            "START_CONTROL_PANEL.lnk",
            "OMEGA_START.lnk"
        ]
        
        # Storage directories for file organization
        self.storage_dirs = {
            "scripts": self.base_dir / "Scripts",
            "launchers": self.base_dir / "Launchers",
            "icons": self.options_dir,
            "config": self.base_dir / "Config",
            "logs": self.base_dir / "Logs"
        }
        
        # Create storage directories
        for dir_path in self.storage_dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def remove_old_desktop_icons(self) -> List[str]:
        """Remove all old desktop icons"""
        print("\n[1/4] Removing old desktop icons...")
        
        removed = []
        for shortcut_name in self.old_shortcuts:
            shortcut_path = self.desktop_dir / shortcut_name
            if shortcut_path.exists():
                try:
                    shortcut_path.unlink()
                    removed.append(shortcut_name)
                    print(f"[OK] Removed: {shortcut_name}")
                except Exception as e:
                    print(f"[ERROR] Failed to remove {shortcut_name}: {e}")
        
        # Also search for any other Omega-related shortcuts
        try:
            for item in self.desktop_dir.iterdir():
                if item.suffix == '.lnk' and 'omega' in item.name.lower():
                    if item.name not in removed:
                        try:
                            item.unlink()
                            removed.append(item.name)
                            print(f"[OK] Removed: {item.name}")
                        except Exception as e:
                            print(f"[ERROR] Failed to remove {item.name}: {e}")
        except Exception as e:
            print(f"[ERROR] Error scanning desktop: {e}")
        
        print(f"[OK] Removed {len(removed)} old desktop icons")
        return removed
    
    def organize_files(self) -> Dict[str, List[str]]:
        """Organize files into proper storage locations"""
        print("\n[2/4] Organizing files...")
        
        organized = {
            "scripts": [],
            "launchers": [],
            "icons": [],
            "config": [],
            "logs": []
        }
        
        # Find and organize launcher scripts
        launcher_patterns = [
            "START_*.py",
            "*_LAUNCHER.py",
            "*_START.py",
            "RUN_*.py"
        ]
        
        launchers_dir = self.storage_dirs["launchers"]
        for pattern in launcher_patterns:
            for file_path in self.base_dir.glob(pattern):
                if file_path.is_file() and file_path.name != self.omega_ui_launcher:
                    try:
                        target = launchers_dir / file_path.name
                        if target.exists():
                            target.unlink()
                        file_path.rename(target)
                        organized["launchers"].append(file_path.name)
                        print(f"[OK] Moved to Launchers: {file_path.name}")
                    except Exception as e:
                        print(f"[ERROR] Failed to move {file_path.name}: {e}")
        
        # Find and organize icon files
        icon_patterns = ["*.ico", "*.png", "*.bmp"]
        icons_dir = self.storage_dirs["icons"]
        for pattern in icon_patterns:
            for file_path in self.base_dir.glob(pattern):
                if file_path.is_file() and file_path.parent != icons_dir:
                    # Check if it's an Omega-related icon
                    if 'omega' in file_path.stem.lower() or 'logo' in file_path.stem.lower():
                        try:
                            target = icons_dir / file_path.name
                            if target.exists():
                                target.unlink()
                            file_path.rename(target)
                            organized["icons"].append(file_path.name)
                            print(f"[OK] Moved to Options: {file_path.name}")
                        except Exception as e:
                            print(f"[ERROR] Failed to move {file_path.name}: {e}")
        
        # Find and organize config files
        config_patterns = ["*_config.json", "*.env", "*_settings.json"]
        config_dir = self.storage_dirs["config"]
        for pattern in config_patterns:
            for file_path in self.base_dir.glob(pattern):
                if file_path.is_file() and file_path.parent != config_dir:
                    try:
                        target = config_dir / file_path.name
                        if target.exists():
                            target.unlink()
                        file_path.rename(target)
                        organized["config"].append(file_path.name)
                        print(f"[OK] Moved to Config: {file_path.name}")
                    except Exception as e:
                        print(f"[ERROR] Failed to move {file_path.name}: {e}")
        
        print(f"[OK] Organized {sum(len(files) for files in organized.values())} files")
        return organized
    
    def create_omega_ui_launcher(self) -> Path:
        """Create Omega UI launcher script"""
        print("\n[3/4] Creating Omega UI launcher...")
        
        launcher_file = self.base_dir / self.omega_ui_launcher
        
        launcher_content = f'''#!/usr/bin/env python3
"""
Omega UI Launcher
=================
Main launcher for Omega User Interface and system connection.
"""

import sys
import os
from pathlib import Path

# Add base directory to path
base_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(base_dir))

def launch_omega_ui():
    """Launch Omega Control Panel UI"""
    try:
        print("=" * 80)
        print(" " * 25 + "OMEGA UI LAUNCHER")
        print("=" * 80)
        print()
        print("Starting Omega Control Panel...")
        print()
        
        # Import and run control panel
        from omega_control_panel import ControlPanel
        
        panel = ControlPanel()
        panel.run()
        
    except ImportError as e:
        print(f"[ERROR] Failed to import control panel: {e}")
        print("Make sure omega_control_panel.py is in the base directory")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to start Omega UI: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    launch_omega_ui()
'''
        
        with open(launcher_file, 'w', encoding='utf-8') as f:
            f.write(launcher_content)
        
        print(f"[OK] Created Omega UI launcher: {launcher_file.name}")
        return launcher_file
    
    def create_desktop_shortcut(self) -> Path:
        """Create desktop shortcut with Omega logo"""
        print("\n[4/4] Creating desktop shortcut with Omega logo...")
        
        # Find Omega logo
        logo_path = self.options_dir / "omega_logo.ico"
        if not logo_path.exists():
            # Try other formats
            for ext in ['.png', '.bmp']:
                alt_logo = self.options_dir / f"omega_logo{ext}"
                if alt_logo.exists():
                    # Convert to ICO if needed
                    try:
                        from PIL import Image
                        img = Image.open(alt_logo)
                        logo_path = self.options_dir / "omega_logo.ico"
                        img.save(logo_path, format='ICO')
                        print(f"[OK] Converted logo to ICO format")
                        break
                    except ImportError:
                        print("[WARNING] PIL/Pillow not available, using default icon")
                        logo_path = None
                        break
                    except Exception as e:
                        print(f"[WARNING] Logo conversion failed: {e}")
                        logo_path = None
                        break
        
        launcher_path = self.base_dir / self.omega_ui_launcher
        shortcut_path = self.desktop_dir / "Omega.lnk"
        
        # Create VBScript to create shortcut
        vbs_script = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{sys.executable}"
oLink.Arguments = """{launcher_path}"""
oLink.WorkingDirectory = "{self.base_dir}"
oLink.Description = "Omega User Interface - Control Panel"
{('oLink.IconLocation = "' + str(logo_path) + ',0"' if logo_path else '')}
oLink.Save
'''
        
        # Save VBScript temporarily
        vbs_file = self.base_dir / "create_shortcut_temp.vbs"
        with open(vbs_file, 'w', encoding='utf-8') as f:
            f.write(vbs_script)
        
        try:
            # Run VBScript to create shortcut
            result = subprocess.run(
                ['cscript', '//nologo', str(vbs_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Clean up temp file
            vbs_file.unlink()
            
            print(f"[OK] Created desktop shortcut: {shortcut_path.name}")
            print(f"     Target: {self.omega_ui_launcher}")
            if logo_path:
                print(f"     Icon: {logo_path.name}")
            else:
                print(f"     Icon: Default Python icon")
            return shortcut_path
            
        except Exception as e:
            # Clean up temp file
            if vbs_file.exists():
                vbs_file.unlink()
            print(f"[ERROR] Failed to create shortcut: {e}")
            print("[INFO] You may need to create the shortcut manually")
            return None
    
    def organize_all(self) -> Dict[str, Any]:
        """Organize everything"""
        print("\n" + "=" * 80)
        print(" " * 20 + "CLEAN AND ORGANIZE OMEGA DESKTOP")
        print("=" * 80)
        print()
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "removed_icons": self.remove_old_desktop_icons(),
            "organized_files": self.organize_files(),
            "launcher_created": str(self.create_omega_ui_launcher()),
            "shortcut_created": None
        }
        
        shortcut = self.create_desktop_shortcut()
        if shortcut:
            result["shortcut_created"] = str(shortcut)
        
        return result

def main():
    """Main function"""
    organizer = OmegaDesktopOrganizer()
    result = organizer.organize_all()
    
    # Save result
    result_file = organizer.base_dir / "DESKTOP_ORGANIZATION_RESULT.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print()
    print("=" * 80)
    print(" " * 25 + "ORGANIZATION COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Old icons removed: {len(result['removed_icons'])}")
    print(f"  - Files organized: {sum(len(files) for files in result['organized_files'].values())}")
    print(f"  - Launcher created: {Path(result['launcher_created']).name}")
    if result['shortcut_created']:
        print(f"  - Desktop shortcut created: {Path(result['shortcut_created']).name}")
    else:
        print(f"  - Desktop shortcut: Failed (may need manual creation)")
    print()
    print("Next Steps:")
    print("  1. Double-click 'Omega' icon on desktop to launch UI")
    print("  2. Omega UI will connect to the system")
    print("  3. Control Panel will open")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
