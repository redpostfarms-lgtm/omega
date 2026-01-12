#!/usr/bin/env python3
"""
Create Desktop Shortcut for Omega
==================================
Creates a Windows desktop shortcut to launch Omega outside of Cursor.
"""

import sys
import os
from pathlib import Path
import subprocess

def create_desktop_shortcut():
    """Create a desktop shortcut for Omega"""
    
    print("\n" + "=" * 80)
    print(" " * 25 + "OMEGA - DESKTOP SHORTCUT CREATOR")
    print("=" * 80)
    print()
    
    # Get paths
    script_dir = Path(__file__).parent.absolute()
    # Use START_CONTROL_PANEL.bat if it exists, otherwise OMEGA_OPERATIONAL_STARTUP.bat
    omega_bat = script_dir / "START_CONTROL_PANEL.bat"
    if not omega_bat.exists():
        omega_bat = script_dir / "OMEGA_OPERATIONAL_STARTUP.bat"
    
    # Get icon path
    icon_path = script_dir / "omega_icon.ico"
    
    # Get desktop path
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        # Try alternative desktop paths
        desktop = Path(os.environ.get('PUBLIC', '')) / "Desktop"
        if not desktop.exists():
            desktop = Path(os.environ.get('USERPROFILE', '')) / "Desktop"
    
    if not desktop.exists():
        print("[ERROR] Could not find Desktop folder")
        print("Please create shortcut manually:")
        print(f"  1. Right-click on: {omega_bat}")
        print("  2. Select 'Create shortcut'")
        print("  3. Move shortcut to Desktop")
        return False
    
    shortcut_path = desktop / "Omega.lnk"
    
    print(f"Script directory: {script_dir}")
    print(f"Omega batch file: {omega_bat}")
    print(f"Desktop path: {desktop}")
    print(f"Shortcut will be: {shortcut_path}")
    print()
    
    # Check if batch file exists
    if not omega_bat.exists():
        print(f"[ERROR] Omega batch file not found: {omega_bat}")
        return False
    
    # Create shortcut using PowerShell
    print("[Creating desktop shortcut...]")
    
    # PowerShell script to create shortcut with icon
    icon_location_line = f'$Shortcut.IconLocation = "{icon_path},0"\n' if icon_path.exists() else ""
    ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{omega_bat}"
$Shortcut.WorkingDirectory = "{script_dir}"
$Shortcut.Description = "Launch Omega - Standalone Operational System"
$Shortcut.WindowStyle = 1
{icon_location_line}$Shortcut.Save()
Write-Host "Shortcut created successfully"
"""
    
    try:
        # Run PowerShell script
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("[OK] Desktop shortcut created successfully!")
            print(f"     Location: {shortcut_path}")
            print()
            print("You can now:")
            print("  1. Find 'Omega.lnk' on your Desktop")
            print("  2. Double-click to launch Omega")
            print("  3. Right-click → Properties to customize icon (optional)")
            return True
        else:
            print(f"[ERROR] PowerShell script failed:")
            print(result.stderr)
            
            # Fallback: Create using VBScript
            print("\n[Trying alternative method with VBScript...]")
            return create_shortcut_vbs(shortcut_path, omega_bat, script_dir, str(icon_path) if icon_path.exists() else None)
            
    except Exception as e:
        print(f"[ERROR] Failed to create shortcut: {e}")
        print("\n[Trying alternative method with VBScript...]")
        return create_shortcut_vbs(shortcut_path, omega_bat, script_dir, str(icon_path) if icon_path.exists() else None)

def create_shortcut_vbs(shortcut_path, target_path, working_dir, icon_path=None):
    """Create shortcut using VBScript (fallback method)"""
    try:
        icon_line = f'oLink.IconLocation = "{icon_path},0"\n' if icon_path and Path(icon_path).exists() else ""
        vbs_script = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_path}"
oLink.WorkingDirectory = "{working_dir}"
oLink.Description = "Launch Omega - Standalone Operational System"
oLink.WindowStyle = 1
{icon_line}oLink.Save
'''
        vbs_file = Path(__file__).parent / "create_shortcut_temp.vbs"
        vbs_file.write_text(vbs_script, encoding='utf-8')
        
        result = subprocess.run(
            ["cscript", "//nologo", str(vbs_file)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Clean up temp file
        if vbs_file.exists():
            vbs_file.unlink()
        
        if result.returncode == 0:
            print("[OK] Desktop shortcut created successfully (VBScript method)!")
            print(f"     Location: {shortcut_path}")
            if icon_path and Path(icon_path).exists():
                print(f"     Icon: {Path(icon_path).name} (Omega logo)")
            return True
        else:
            print(f"[ERROR] VBScript method failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERROR] VBScript fallback failed: {e}")
        return False

def create_batch_shortcut_creator():
    """Create a simple batch file alternative"""
    batch_content = f'''@echo off
REM Create Desktop Shortcut for Omega
echo Creating Desktop Shortcut for Omega...
echo.

cd /d "%~dp0"

REM Create shortcut using PowerShell
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Omega.lnk'); $Shortcut.TargetPath = '%CD%\\OMEGA_OPERATIONAL_STARTUP.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Launch Omega - Standalone Operational System'; $Shortcut.WindowStyle = 1; $Shortcut.Save()"

if exist "%USERPROFILE%\\Desktop\\Omega.lnk" (
    echo.
    echo [OK] Desktop shortcut created successfully!
    echo Location: %%USERPROFILE%%\\Desktop\\Omega.lnk
    echo.
    echo You can now double-click "Omega" on your Desktop to launch Omega.
) else (
    echo.
    echo [ERROR] Failed to create shortcut.
    echo Please create manually: Right-click OMEGA_OPERATIONAL_STARTUP.bat ^> Create shortcut ^> Move to Desktop
)

pause
'''
    batch_file = Path(__file__).parent / "CREATE_DESKTOP_SHORTCUT.bat"
    batch_file.write_text(batch_content, encoding='utf-8')
    print(f"\n[OK] Also created batch file: {batch_file.name}")
    print("     You can run this if Python method doesn't work")

def main():
    """Main function"""
    if sys.platform != 'win32':
        print("[ERROR] This script is for Windows only")
        print("On Linux/Mac, create a launcher script manually")
        return
    
    success = create_desktop_shortcut()
    create_batch_shortcut_creator()
    
    if success:
        print("\n" + "=" * 80)
        print(" " * 25 + "SHORTCUT CREATED SUCCESSFULLY")
        print("=" * 80)
        print()
        print("Omega is now accessible from your Desktop!")
        print("Double-click 'Omega.lnk' to launch Omega outside of Cursor.")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print(" " * 25 + "SHORTCUT CREATION FAILED")
        print("=" * 80)
        print()
        print("Alternative: Create shortcut manually")
        print("  1. Navigate to:", Path(__file__).parent)
        print("  2. Right-click: OMEGA_OPERATIONAL_STARTUP.bat")
        print("  3. Select: Create shortcut")
        print("  4. Move shortcut to Desktop")
        print("  5. Rename to: Omega")
        print("=" * 80)

if __name__ == "__main__":
    main()
