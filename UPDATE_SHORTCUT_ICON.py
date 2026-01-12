#!/usr/bin/env python3
"""
Update Desktop Shortcut Icon
============================
Updates the Omega desktop shortcut to use the Omega logo icon.
"""

import sys
import os
from pathlib import Path
import subprocess

def update_shortcut_icon():
    """Update desktop shortcut icon to Omega logo"""
    
    print("\n" + "=" * 80)
    print(" " * 25 + "UPDATE SHORTCUT ICON")
    print("=" * 80)
    print()
    
    # Get paths
    script_dir = Path(__file__).parent.absolute()
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        desktop = Path(os.environ.get('USERPROFILE', '')) / "Desktop"
    
    shortcut_path = desktop / "Omega.lnk"
    icon_path = script_dir / "omega_icon.ico"
    
    if not shortcut_path.exists():
        print("[ERROR] Desktop shortcut not found!")
        print(f"Expected: {shortcut_path}")
        print()
        print("Please create the shortcut first:")
        print("  python CREATE_DESKTOP_SHORTCUT.py")
        return False
    
    if not icon_path.exists():
        print("[ERROR] Icon file not found!")
        print(f"Expected: {icon_path}")
        print()
        print("Please create the icon first:")
        print("  python CREATE_OMEGA_ICON.py")
        return False
    
    print(f"Shortcut: {shortcut_path}")
    print(f"Icon: {icon_path}")
    print()
    
    # Update shortcut icon using PowerShell
    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.IconLocation = "{icon_path},0"
$Shortcut.Save()
Write-Host "Icon updated successfully"
"""
    
    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] Shortcut icon updated successfully!")
            print(f"     Icon: {icon_path.name} (Omega logo)")
            return True
        else:
            print(f"[ERROR] Failed to update icon:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to update icon: {e}")
        return False

if __name__ == "__main__":
    if sys.platform != 'win32':
        print("[ERROR] This script is for Windows only")
        return
    
    success = update_shortcut_icon()
    
    if success:
        print()
        print("=" * 80)
        print(" " * 25 + "ICON UPDATE COMPLETE")
        print("=" * 80)
        print()
        print("The desktop shortcut now uses the Omega logo icon.")
        print("=" * 80)
    else:
        print()
        print("=" * 80)
        print(" " * 25 + "ICON UPDATE FAILED")
        print("=" * 80)
