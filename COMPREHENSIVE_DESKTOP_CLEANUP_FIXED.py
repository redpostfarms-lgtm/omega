#!/usr/bin/env python3
"""
Comprehensive Desktop Cleanup and Organization
===============================================
Removes all desktop shortcuts and folders, organizes files properly,
and creates a single Omega logo shortcut.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import json
import tempfile
import subprocess

# Desktop paths
DESKTOP = Path.home() / "Desktop"
PUBLIC_DESKTOP = Path("C:/Users/Public/Desktop")

# Gatekeeper base directory
GATEKEEPER_DIR = Path(__file__).parent.absolute()

# Organization directories
ORGANIZED_DIR = GATEKEEPER_DIR / "Organized_Files"
SCRIPTS_DIR = ORGANIZED_DIR / "Scripts"
SHORTCUTS_DIR = ORGANIZED_DIR / "Shortcuts"
FOLDERS_DIR = ORGANIZED_DIR / "Desktop_Folders"

def find_desktop():
    """Find the active desktop directory"""
    if DESKTOP.exists():
        return DESKTOP
    elif PUBLIC_DESKTOP.exists():
        return PUBLIC_DESKTOP
    else:
        return None

def get_shortcut_target(shortcut_path: Path) -> dict:
    """Get shortcut target information using PowerShell"""
    target_info = {
        "exists": False,
        "target": None,
        "working_dir": None,
        "icon": None,
        "arguments": None
    }
    
    try:
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath
$Shortcut.WorkingDirectory
$Shortcut.Arguments
'''
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            lines = [l.strip() for l in result.stdout.strip().split('\n') if l.strip()]
            if len(lines) >= 3:
                target_info["target"] = lines[0] if lines[0] else None
                target_info["working_dir"] = lines[1] if lines[1] else None
                target_info["arguments"] = lines[2] if lines[2] else None
                if target_info["target"]:
                    target_info["exists"] = Path(target_info["target"]).exists()
    except Exception as e:
        pass  # Silent fail, return default
    
    return target_info

def organize_shortcut(shortcut_path: Path, desktop: Path):
    """Organize a desktop shortcut and log its target"""
    shortcut_name = shortcut_path.stem
    target_info = get_shortcut_target(shortcut_path)
    
    # Create shortcuts directory
    SHORTCUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Move shortcut to organized location
    dest_path = SHORTCUTS_DIR / shortcut_path.name
    try:
        shutil.move(str(shortcut_path), str(dest_path))
        print(f"  [OK] Moved shortcut: {shortcut_name}")
        
        # Log shortcut information
        shortcut_log = {
            "shortcut_name": shortcut_name,
            "original_location": str(shortcut_path),
            "organized_location": str(dest_path),
            "target": target_info.get("target"),
            "working_dir": target_info.get("working_dir"),
            "arguments": target_info.get("arguments"),
            "moved_date": datetime.now().isoformat()
        }
        return shortcut_log
    except Exception as e:
        print(f"  [ERROR] Failed to move shortcut {shortcut_name}: {e}")
        return None

def organize_folder(folder_path: Path, desktop: Path):
    """Organize a desktop folder"""
    folder_name = folder_path.name
    
    # Create folders directory
    FOLDERS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Move folder to organized location
    dest_path = FOLDERS_DIR / folder_name
    try:
        if dest_path.exists():
            dest_path = FOLDERS_DIR / f"{folder_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.move(str(folder_path), str(dest_path))
        print(f"  [OK] Moved folder: {folder_name}")
        
        folder_log = {
            "folder_name": folder_name,
            "original_location": str(folder_path),
            "organized_location": str(dest_path),
            "moved_date": datetime.now().isoformat()
        }
        return folder_log
    except Exception as e:
        print(f"  [ERROR] Failed to move folder {folder_name}: {e}")
        return None

def remove_all_desktop_shortcuts(desktop: Path):
    """Remove all desktop shortcuts"""
    print("\n[Step 1] Removing desktop shortcuts...")
    print("-" * 80)
    
    shortcuts_removed = []
    shortcut_files = list(desktop.glob("*.lnk"))
    
    print(f"Found {len(shortcut_files)} shortcut(s) on desktop")
    
    for shortcut in shortcut_files:
        shortcut_log = organize_shortcut(shortcut, desktop)
        if shortcut_log:
            shortcuts_removed.append(shortcut_log)
    
    return shortcuts_removed

def remove_specific_folders(desktop: Path):
    """Remove specific folders from desktop"""
    print("\n[Step 2] Removing specific desktop folders...")
    print("-" * 80)
    
    folders_to_remove = ["R&D", "AutoCAD Designs", "Cursor Brain"]
    folders_removed = []
    
    for folder_name in folders_to_remove:
        folder_path = desktop / folder_name
        if folder_path.exists() and folder_path.is_dir():
            folder_log = organize_folder(folder_path, desktop)
            if folder_log:
                folders_removed.append(folder_log)
        else:
            print(f"  [INFO] Folder not found: {folder_name}")
    
    return folders_removed

def create_omega_shortcut(desktop: Path):
    """Create Omega logo shortcut on desktop"""
    print("\n[Step 3] Creating Omega logo shortcut...")
    print("-" * 80)
    
    # Remove existing Omega shortcut if it exists
    existing_shortcut = desktop / "Omega.lnk"
    if existing_shortcut.exists():
        try:
            existing_shortcut.unlink()
            print(f"  [INFO] Removed existing Omega shortcut")
        except:
            pass
    
    # Find Omega logo icon (check multiple locations)
    icon_paths = [
        GATEKEEPER_DIR / "Options" / "omega_logo.ico",
        GATEKEEPER_DIR / "omega_logo.ico",
        GATEKEEPER_DIR / "Options" / "omega_logo.png",
        GATEKEEPER_DIR / "omega_logo.png",
        GATEKEEPER_DIR / "images" / "omega_logo_red_gold_wreath.png",
        GATEKEEPER_DIR / "images" / "omega_logo.ico",
        GATEKEEPER_DIR / "images" / "omega_logo.png",
    ]
    
    # Also check Options and images directories
    for check_dir in [GATEKEEPER_DIR / "Options", GATEKEEPER_DIR / "images"]:
        if check_dir.exists():
            for icon_file in check_dir.glob("*.ico"):
                if icon_file not in icon_paths:
                    icon_paths.append(icon_file)
            for icon_file in check_dir.glob("*omega*.png"):
                if icon_file not in icon_paths:
                    icon_paths.append(icon_file)
    
    icon_path = None
    for path in icon_paths:
        if path.exists():
            icon_path = path
            print(f"  [OK] Found Omega logo: {path.name}")
            break
    
    if not icon_path:
        print("  [WARN] Omega logo not found, shortcut will use default icon")
        print("  [INFO] To add logo, save as: Options/omega_logo.ico or images/omega_logo_red_gold_wreath.png")
    
    # Target: OMEGA_UI_LAUNCHER.py
    target_file = GATEKEEPER_DIR / "OMEGA_UI_LAUNCHER.py"
    
    if not target_file.exists():
        print(f"  [ERROR] Target file not found: {target_file}")
        return None
    
    shortcut_path = desktop / "Omega.lnk"
    python_exe = sys.executable
    abs_target = str(target_file.absolute())
    abs_gatekeeper = str(GATEKEEPER_DIR.absolute())
    
    try:
        # Create shortcut using PowerShell
        ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{python_exe}"
$Shortcut.Arguments = '"{abs_target}"'
$Shortcut.WorkingDirectory = "{abs_gatekeeper}"
$Shortcut.WindowStyle = 1
$Shortcut.Description = "Omega Control Panel"
'''
        if icon_path:
            abs_icon = str(icon_path.absolute())
            # Try to convert PNG to ICO if needed
            if icon_path.suffix.lower() == ".png":
                ico_path = icon_path.parent / f"{icon_path.stem}.ico"
                if not ico_path.exists():
                    try:
                        from PIL import Image
                        img = Image.open(icon_path)
                        img.save(ico_path, format='ICO')
                        abs_icon = str(ico_path.absolute())
                        print(f"  [OK] Converted PNG to ICO: {ico_path.name}")
                    except:
                        pass  # Use PNG directly
            ps_script += f'$Shortcut.IconLocation = "{abs_icon},0"\n'
        ps_script += "$Shortcut.Save()\n"
        
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 or shortcut_path.exists():
            print(f"  [OK] Created Omega shortcut: {shortcut_path.name}")
            if icon_path:
                print(f"  [OK] Using icon: {icon_path.name}")
            return str(shortcut_path)
        else:
            # Fallback to VBScript
            print(f"  [WARN] PowerShell failed, trying VBScript...")
            return create_shortcut_vbscript(shortcut_path, target_file, icon_path, GATEKEEPER_DIR)
            
    except Exception as e:
        print(f"  [WARN] Error creating shortcut: {e}")
        print(f"  [INFO] Trying VBScript fallback...")
        return create_shortcut_vbscript(shortcut_path, target_file, icon_path, GATEKEEPER_DIR)

def create_shortcut_vbscript(shortcut_path: Path, target_file: Path, icon_path: Path, working_dir: Path):
    """Create shortcut using VBScript (fallback method)"""
    try:
        python_exe = sys.executable
        abs_target = str(target_file.absolute())
        abs_working = str(working_dir.absolute())
        
        vbscript = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{python_exe}"
oLink.Arguments = "{abs_target}"
oLink.WorkingDirectory = "{abs_working}"
oLink.Description = "Omega Control Panel"
'''
        if icon_path:
            abs_icon = str(icon_path.absolute())
            if icon_path.suffix.lower() == ".png":
                ico_path = icon_path.parent / f"{icon_path.stem}.ico"
                if not ico_path.exists():
                    try:
                        from PIL import Image
                        img = Image.open(icon_path)
                        img.save(ico_path, format='ICO')
                        abs_icon = str(ico_path.absolute())
                    except:
                        pass
            vbscript += f'oLink.IconLocation = "{abs_icon},0"\n'
        vbscript += "oLink.Save\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vbs', delete=False, encoding='utf-8') as f:
            f.write(vbscript)
            vbs_file = f.name
        
        result = subprocess.run(["cscript", "//nologo", vbs_file], capture_output=True, text=True)
        try:
            os.unlink(vbs_file)
        except:
            pass
        
        if shortcut_path.exists():
            print(f"  [OK] Created Omega shortcut: {shortcut_path.name}")
            if icon_path:
                print(f"  [OK] Using icon: {icon_path.name}")
            return str(shortcut_path)
        else:
            print(f"  [ERROR] Failed to create shortcut")
            return None
    except Exception as e:
        print(f"  [ERROR] VBScript fallback failed: {e}")
        return None

def save_cleanup_log(shortcuts_removed: list, folders_removed: list, omega_shortcut: str):
    """Save cleanup log"""
    log_file = ORGANIZED_DIR / "desktop_cleanup_log.json"
    ORGANIZED_DIR.mkdir(parents=True, exist_ok=True)
    
    log_data = {
        "cleanup_date": datetime.now().isoformat(),
        "shortcuts_removed": shortcuts_removed,
        "folders_removed": folders_removed,
        "omega_shortcut_created": omega_shortcut,
        "total_shortcuts_removed": len(shortcuts_removed),
        "total_folders_removed": len(folders_removed)
    }
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2)
    
    print(f"\n[OK] Cleanup log saved: {log_file.name}")

def main():
    """Main cleanup function"""
    print("=" * 80)
    print(" " * 20 + "COMPREHENSIVE DESKTOP CLEANUP")
    print("=" * 80)
    print()
    
    # Find desktop
    desktop = find_desktop()
    if not desktop:
        print("[ERROR] Cannot find desktop directory")
        return
    
    print(f"Desktop location: {desktop}")
    print()
    
    # Step 1: Remove all desktop shortcuts
    shortcuts_removed = remove_all_desktop_shortcuts(desktop)
    
    # Step 2: Remove specific folders
    folders_removed = remove_specific_folders(desktop)
    
    # Step 3: Create Omega shortcut
    omega_shortcut = create_omega_shortcut(desktop)
    
    # Step 4: Save cleanup log
    save_cleanup_log(shortcuts_removed, folders_removed, omega_shortcut)
    
    print()
    print("=" * 80)
    print(" " * 25 + "CLEANUP COMPLETE")
    print("=" * 80)
    print()
    print(f"Shortcuts removed: {len(shortcuts_removed)}")
    print(f"Folders removed: {len(folders_removed)}")
    print(f"Omega shortcut created: {'Yes' if omega_shortcut else 'No'}")
    print()
    print(f"Files organized in: {ORGANIZED_DIR.name}/")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
