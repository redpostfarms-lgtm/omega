#!/usr/bin/env python3
"""
Gatekeeper Admin Helper
=======================
Ensures Gatekeeper system has admin privileges and can save critical files.
Run this to verify and set up admin permissions.
"""

import os
import sys
import json
from pathlib import Path
import ctypes
import subprocess
from datetime import datetime

# Platform detection
IS_WINDOWS = sys.platform.startswith('win')
IS_ADMIN = False

if IS_WINDOWS:
    try:
        IS_ADMIN = ctypes.windll.shell.IsUserAnAdmin()
    except:
        IS_ADMIN = False

class AdminHelper:
    """Helper for admin operations and file permissions"""
    
    def __init__(self):
        self.workspace = Path(".")
        self.critical_files = [
            "gatekeeper_integration_module.py",
            "gatekeeper_integration_config.json",
            "logs/gatekeeper_system.log",
            "system_diagnostics.json",
            "gatekeeper_final_diagnostics.json"
        ]
        self.admin_status = IS_ADMIN
    
    def check_admin_status(self):
        """Check if running as admin"""
        print("\n" + "="*70)
        print("GATEKEEPER ADMIN STATUS CHECK")
        print("="*70)
        print(f"\nPlatform: {sys.platform}")
        print(f"Running as Admin: {'YES' if self.admin_status else 'NO'}")
        print(f"Current User: {os.getenv('USERNAME', 'Unknown')}")
        print(f"Working Directory: {self.workspace.absolute()}")
        
        return self.admin_status
    
    def check_file_permissions(self):
        """Check permissions on critical files"""
        print("\n" + "-"*70)
        print("CRITICAL FILE PERMISSIONS:")
        print("-"*70)
        
        for file_path in self.critical_files:
            full_path = self.workspace / file_path
            parent_dir = full_path.parent
            
            # Create directory if needed
            if not parent_dir.exists():
                try:
                    parent_dir.mkdir(parents=True, exist_ok=True)
                    status = "CREATED"
                except PermissionError:
                    status = "PERMISSION DENIED"
                except Exception as e:
                    status = f"ERROR: {e}"
            else:
                status = "EXISTS"
            
            # Check write permission
            if full_path.exists():
                writable = os.access(full_path, os.W_OK)
                write_status = "WRITABLE" if writable else "READ-ONLY"
            elif parent_dir.exists():
                writable = os.access(parent_dir, os.W_OK)
                write_status = "DIR WRITABLE" if writable else "DIR READ-ONLY"
            else:
                write_status = "UNKNOWN"
            
            print(f"  {file_path}")
            print(f"    Status: {status}")
            print(f"    Write: {write_status}")
    
    def setup_critical_directories(self):
        """Ensure critical directories exist with proper permissions"""
        print("\n" + "-"*70)
        print("SETTING UP CRITICAL DIRECTORIES:")
        print("-"*70)
        
        dirs_needed = [
            "logs",
            "data",
            "reports",
            "backups"
        ]
        
        for dir_name in dirs_needed:
            dir_path = self.workspace / dir_name
            try:
                dir_path.mkdir(exist_ok=True)
                print(f"  ✓ {dir_name}/ - Ready")
            except PermissionError:
                print(f"  ✗ {dir_name}/ - Permission Denied (admin needed)")
            except Exception as e:
                print(f"  ✗ {dir_name}/ - Error: {e}")
    
    def create_admin_batch_scripts(self):
        """Create batch scripts for admin operations"""
        print("\n" + "-"*70)
        print("CREATING ADMIN SCRIPTS:")
        print("-"*70)
        
        # Windows batch script for admin launch
        if IS_WINDOWS:
            batch_content = """@echo off
REM Gatekeeper Admin Launcher
REM Run Gatekeeper with admin privileges

echo Gatekeeper Admin Launcher
echo =========================

REM Check for admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Admin Status: Running as ADMIN
) else (
    echo Admin Status: NOT RUNNING AS ADMIN
    echo Attempting to elevate...
    powershell -Command "Start-Process cmd -ArgumentList '/c %~0' -Verb RunAs"
    exit /b
)

REM Run Python script
cd /d "%~dp0"
python gatekeeper_integration_module.py
pause
"""
            
            batch_file = self.workspace / "run_gatekeeper_admin.bat"
            try:
                with open(batch_file, 'w') as f:
                    f.write(batch_content)
                print(f"  ✓ Created: run_gatekeeper_admin.bat")
            except PermissionError:
                print(f"  ✗ Cannot create admin batch (permission denied)")
            except Exception as e:
                print(f"  ✗ Error creating batch: {e}")
        
        # PowerShell script for admin launch
        ps_content = """# Gatekeeper Admin Launcher (PowerShell)
# Run Gatekeeper with admin privileges

Write-Host "Gatekeeper Admin Launcher" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if ($isAdmin) {
    Write-Host "Status: Running as ADMIN" -ForegroundColor Green
    
    # Run the system
    Write-Host "Initializing Gatekeeper..." -ForegroundColor Yellow
    python gatekeeper_integration_module.py
} else {
    Write-Host "Status: NOT RUNNING AS ADMIN" -ForegroundColor Red
    Write-Host "Attempting to elevate..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\\$($MyInvocation.MyCommand.Name)`"" -Verb RunAs
}
"""
        
        ps_file = self.workspace / "run_gatekeeper_admin.ps1"
        try:
            with open(ps_file, 'w') as f:
                f.write(ps_content)
            print(f"  ✓ Created: run_gatekeeper_admin.ps1")
        except PermissionError:
            print(f"  ✗ Cannot create admin PowerShell script (permission denied)")
        except Exception as e:
            print(f"  ✗ Error creating PowerShell script: {e}")
    
    def create_admin_config(self):
        """Create admin configuration file"""
        print("\n" + "-"*70)
        print("ADMIN CONFIGURATION:")
        print("-"*70)
        
        admin_config = {
            "admin_required": True,
            "admin_enforced": True,
            "critical_files": self.critical_files,
            "log_directory": "logs",
            "backup_directory": "backups",
            "permissions": {
                "logs": "rwx",
                "data": "rwx",
                "reports": "rwx",
                "backups": "rwx",
                "gatekeeper_integration_module.py": "rw",
                "gatekeeper_integration_config.json": "rw"
            },
            "auto_elevate": IS_WINDOWS,
            "setup_date": datetime.now().isoformat(),
            "platform": sys.platform
        }
        
        config_file = self.workspace / "admin_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(admin_config, f, indent=2)
            print(f"  ✓ Created: admin_config.json")
        except PermissionError:
            print(f"  ✗ Cannot create config (permission denied)")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def verify_critical_files(self):
        """Verify all critical files are accessible"""
        print("\n" + "-"*70)
        print("CRITICAL FILES VERIFICATION:")
        print("-"*70)
        
        critical_files_check = [
            "gatekeeper_integration_module.py",
            "omega_control_panel_web.py",
            "CONSOLIDATION_STATUS.txt"
        ]
        
        all_good = True
        for fname in critical_files_check:
            fpath = self.workspace / fname
            if fpath.exists():
                size = fpath.stat().st_size / 1024
                readable = os.access(fpath, os.R_OK)
                status = "OK" if readable else "NOT READABLE"
                print(f"  ✓ {fname:40s} {size:8.1f} KB - {status}")
            else:
                print(f"  ✗ {fname:40s} NOT FOUND")
                all_good = False
        
        return all_good
    
    def generate_report(self):
        """Generate admin status report"""
        print("\n" + "="*70)
        print("ADMIN SETUP SUMMARY")
        print("="*70)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "admin_status": self.admin_status,
            "platform": sys.platform,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "workspace": str(self.workspace.absolute()),
            "critical_files_count": len(self.critical_files),
            "setup_complete": True
        }
        
        for key, value in report.items():
            print(f"  {key:25s}: {value}")
        
        # Save report
        report_file = self.workspace / "admin_setup_report.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n  Report saved to: admin_setup_report.json")
        except:
            pass
        
        return report
    
    def run_full_setup(self):
        """Run complete admin setup"""
        self.check_admin_status()
        self.check_file_permissions()
        self.setup_critical_directories()
        self.create_admin_batch_scripts()
        self.create_admin_config()
        verified = self.verify_critical_files()
        self.generate_report()
        
        print("\n" + "="*70)
        if self.admin_status:
            print("✓ ADMIN SETUP COMPLETE - Full privileges available")
        else:
            print("⚠ RUNNING WITHOUT ADMIN - Some operations may fail")
            print("  Recommendation: Run as Administrator for full functionality")
        print("="*70 + "\n")
        
        return self.admin_status


def main():
    """Main entry point"""
    helper = AdminHelper()
    admin_status = helper.run_full_setup()
    
    return 0 if admin_status else 1


if __name__ == "__main__":
    sys.exit(main())
