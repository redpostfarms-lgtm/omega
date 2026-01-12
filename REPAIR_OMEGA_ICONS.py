#!/usr/bin/env python3
"""
Repair Omega Icons - Fix and Set All Icon Files
================================================
Repairs and sets Omega logo icons for desktop shortcut and applications.
"""

import sys
import os
import subprocess
from pathlib import Path

def repair_omega_icons():
    """Repair and set Omega icons"""
    
    print("\n" + "=" * 80)
    print(" " * 25 + "OMEGA ICON REPAIR")
    print("=" * 80)
    print()
    
    base_dir = Path(__file__).parent.absolute()
    options_dir = base_dir / "Options"
    images_dir = base_dir / "images"
    
    # Step 1: Ensure icon file exists
    print("[1/4] Checking icon file...")
    icon_file = base_dir / "omega_icon.ico"
    options_icon = options_dir / "omega_icon.ico"
    
    if not icon_file.exists():
        # Try to create icon
        print("  Creating icon file...")
        try:
            sys.path.insert(0, str(base_dir))
            from CREATE_OMEGA_ICON import create_icon_from_logo
            icon_created = create_icon_from_logo()
            if icon_created:
                print("  [OK] Icon file created")
            else:
                print("  [ERROR] Failed to create icon file")
                return False
        except Exception as e:
            print(f"  [ERROR] Failed to create icon: {e}")
            return False
    else:
        print(f"  [OK] Icon file exists: {icon_file.name}")
    
    # Copy to Options folder
    if icon_file.exists():
        options_dir.mkdir(exist_ok=True)
        import shutil
        try:
            shutil.copy2(icon_file, options_icon)
            print(f"  [OK] Icon copied to Options folder")
        except Exception as e:
            print(f"  [WARNING] Failed to copy to Options: {e}")
    
    print()
    
    # Step 2: Update desktop shortcut icon
    print("[2/4] Updating desktop shortcut icon...")
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path(os.environ.get('PUBLIC', '')) / "Desktop"
        if not desktop.exists():
            desktop = Path(os.environ.get('USERPROFILE', '')) / "Desktop"
    
    shortcut_path = desktop / "Omega.lnk"
    
    if shortcut_path.exists():
        try:
            # Use PowerShell to update icon
            ps_script = f'''
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut("{shortcut_path}")
$Shortcut.IconLocation = "{icon_file},0"
$Shortcut.Save()
Write-Host "Icon updated successfully"
'''
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  [OK] Desktop shortcut icon updated")
            else:
                print("  [WARNING] PowerShell method failed, trying alternative...")
                # Try win32com alternative
                try:
                    import win32com.client
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortcut(str(shortcut_path))
                    shortcut.IconLocation = f"{icon_file},0"
                    shortcut.Save()
                    print("  [OK] Desktop shortcut icon updated (win32com)")
                except ImportError:
                    print("  [WARNING] win32com not available, icon update skipped")
                except Exception as e:
                    print(f"  [WARNING] Icon update failed: {e}")
        except Exception as e:
            print(f"  [WARNING] Failed to update shortcut icon: {e}")
    else:
        print("  [INFO] Desktop shortcut not found, creating new one...")
        try:
            sys.path.insert(0, str(base_dir))
            from CREATE_DESKTOP_SHORTCUT import create_desktop_shortcut
            if create_desktop_shortcut():
                print("  [OK] Desktop shortcut created with icon")
        except Exception as e:
            print(f"  [WARNING] Failed to create shortcut: {e}")
    
    print()
    
    # Step 3: Create icon manifest for Options folder
    print("[3/4] Creating icon manifest...")
    manifest_content = f"""OMEGA ICONS MANIFEST
====================

Location: {options_dir}
Created: {Path(__file__).stat().st_mtime}

ICON FILES:
  - omega_icon.ico
    Purpose: Desktop shortcut icon
    Location: {icon_file if icon_file.exists() else 'NOT FOUND'}
    Status: {'OK' if icon_file.exists() else 'MISSING'}

  - omega_logo_red_gold_wreath.png
    Purpose: Source logo image
    Location: {images_dir / 'omega_logo_red_gold_wreath.png'}
    Status: {'OK' if (images_dir / 'omega_logo_red_gold_wreath.png').exists() else 'MISSING'}

USAGE:
  Desktop Shortcut: omega_icon.ico
  Application Icons: Use omega_icon.ico
  BIOS Logo: Use PREPARE_BIOS_LOGO.py to create BMP version

NOTES:
  - All icon files should be in Options folder for centralized management
  - Use CREATE_OMEGA_ICON.py to regenerate icons from logo
  - Use this script (REPAIR_OMEGA_ICONS.py) to repair icon issues
"""
    
    manifest_path = options_dir / "ICONS_MANIFEST.txt"
    options_dir.mkdir(exist_ok=True)
    manifest_path.write_text(manifest_content, encoding='utf-8')
    print("  [OK] Icon manifest created")
    print()
    
    # Step 4: Verify icon files
    print("[4/4] Verifying icon files...")
    icon_status = {
        "Desktop Icon": icon_file.exists(),
        "Options Icon": options_icon.exists() if options_dir.exists() else False,
        "Logo Source": (images_dir / "omega_logo_red_gold_wreath.png").exists(),
        "Desktop Shortcut": shortcut_path.exists() if 'shortcut_path' in locals() else False
    }
    
    all_ok = all(icon_status.values())
    for name, status in icon_status.items():
        status_str = "OK" if status else "MISSING"
        print(f"  {name}: {status_str}")
    
    print()
    
    print("=" * 80)
    print(" " * 25 + "ICON REPAIR COMPLETE")
    print("=" * 80)
    print()
    
    if all_ok:
        print("All icon files are properly set up!")
    else:
        print("Some icon files are missing. Please check the manifest for details.")
    
    print()
    print(f"Icons location: {options_dir}")
    print(f"Desktop shortcut: {shortcut_path if 'shortcut_path' in locals() and shortcut_path.exists() else 'NOT FOUND'}")
    print("=" * 80)
    print()
    
    return all_ok

if __name__ == "__main__":
    success = repair_omega_icons()
    sys.exit(0 if success else 1)
