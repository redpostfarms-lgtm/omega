"""
C: Drive Cleanup & Monitoring System
Ensures C: drive maintains at least 15GB free space
"""

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


class CDriveManager:
    def __init__(self):
        self.min_free_gb = 15
        self.cleanup_log = Path("H:/The Gatekeeper/logs/c_drive_cleanup.log")
        self.config_file = Path("H:/The Gatekeeper/config/c_drive_config.json")

        # Ensure log directory exists
        self.cleanup_log.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        self.load_config()

    def load_config(self):
        """Load cleanup configuration"""
        default_config = {
            "min_free_gb": 15,
            "auto_cleanup": True,
            "cleanup_targets": [
                "C:\\Windows\\Temp",
                "C:\\Windows\\SoftwareDistribution\\Download",
                "C:\\Windows\\Logs\\CBS",
                "C:\\Windows\\Logs\\DISM",
                "C:\\ProgramData\\Microsoft\\Windows\\WER",
            ],
            "user_cleanup_targets": [
                "AppData\\Local\\Temp",
                "AppData\\Local\\Microsoft\\Windows\\INetCache",
                "AppData\\Local\\Microsoft\\Windows\\WebCache",
                "AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Cache",
                "AppData\\Local\\Google\\Chrome\\User Data\\Default\\Cache",
                "AppData\\Local\\CrashDumps",
            ],
            "exclude_extensions": [".sys", ".dll", ".exe"],
            "max_log_age_days": 30,
            "enable_monitoring": True,
        }

        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Save configuration"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def log(self, message):
        """Log cleanup activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        with open(self.cleanup_log, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(log_entry.strip())

    def get_drive_space(self):
        """Get C: drive space information"""
        total, used, free = shutil.disk_usage("C:\\")
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "free_percent": round((free / total) * 100, 2),
        }

    def needs_cleanup(self):
        """Check if cleanup is needed"""
        space = self.get_drive_space()
        return space["free_gb"] < self.min_free_gb

    def clean_directory(self, path_str, recursive=True):
        """Clean a directory"""
        path = Path(path_str)

        if not path.exists():
            return 0

        freed = 0
        try:
            if recursive:
                items = list(path.rglob("*"))
            else:
                items = list(path.glob("*"))

            for item in items:
                if item.is_file():
                    try:
                        size = item.stat().st_size
                        item.unlink()
                        freed += size
                    except Exception:
                        pass

            freed_mb = round(freed / (1024**2), 2)
            self.log(f"Cleaned {path}: {freed_mb} MB")
            return freed

        except Exception as e:
            self.log(f"Error cleaning {path}: {e}")
            return 0

    def run_disk_cleanup(self):
        """Run Windows Disk Cleanup"""
        self.log("Running Windows Disk Cleanup...")
        try:
            # Run cleanmgr with sageset to configure, then sagerun to execute
            subprocess.run(["cleanmgr", "/sagerun:1"], check=False)
            self.log("Disk Cleanup completed")
        except Exception as e:
            self.log(f"Disk Cleanup error: {e}")

    def clean_temp_files(self):
        """Clean temporary files"""
        self.log("🧹 Starting temp file cleanup...")

        total_freed = 0

        # System temp directories
        for target in self.config["cleanup_targets"]:
            freed = self.clean_directory(target)
            total_freed += freed

        # User temp directories
        user_profile = Path.home()
        for target in self.config["user_cleanup_targets"]:
            user_path = user_profile / target
            freed = self.clean_directory(str(user_path))
            total_freed += freed

        freed_gb = round(total_freed / (1024**3), 2)
        self.log(f"✅ Total freed from temp files: {freed_gb} GB")
        return total_freed

    def clean_old_logs(self):
        """Clean old log files"""
        self.log("Cleaning old log files...")

        log_dirs = [
            Path("C:/Windows/Logs"),
            Path("C:/ProgramData/Microsoft/Windows/WER/ReportQueue"),
        ]

        total_freed = 0
        max_age_days = self.config.get("max_log_age_days", 30)

        for log_dir in log_dirs:
            if not log_dir.exists():
                continue

            try:
                for log_file in log_dir.rglob("*.log"):
                    try:
                        age_days = (
                            datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)
                        ).days
                        if age_days > max_age_days:
                            size = log_file.stat().st_size
                            log_file.unlink()
                            total_freed += size
                    except Exception:
                        pass
            except Exception:
                pass

        freed_mb = round(total_freed / (1024**2), 2)
        self.log(f"Cleaned old logs: {freed_mb} MB")
        return total_freed

    def find_large_files(self, min_size_gb=1):
        """Find large files on C: drive"""
        self.log(f"Searching for files over {min_size_gb}GB...")

        large_files = []
        min_size_bytes = min_size_gb * 1024**3

        search_dirs = [Path("C:/Users"), Path("C:/ProgramData"), Path("C:/Windows/Temp")]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            try:
                for file in search_dir.rglob("*"):
                    if file.is_file():
                        try:
                            size = file.stat().st_size
                            if size > min_size_bytes:
                                large_files.append(
                                    {"path": str(file), "size_gb": round(size / (1024**3), 2)}
                                )
                        except Exception:
                            pass
            except Exception:
                pass

        return sorted(large_files, key=lambda x: x["size_gb"], reverse=True)

    def perform_full_cleanup(self):
        """Perform full cleanup operation"""
        self.log("=" * 60)
        self.log("🧹 STARTING FULL C: DRIVE CLEANUP")
        self.log("=" * 60)

        # Get initial space
        initial_space = self.get_drive_space()
        self.log(f"Initial free space: {initial_space['free_gb']} GB")

        # Clean temp files
        self.clean_temp_files()

        # Clean old logs
        self.clean_old_logs()

        # Get final space
        final_space = self.get_drive_space()
        freed = round(final_space["free_gb"] - initial_space["free_gb"], 2)

        self.log("=" * 60)
        self.log(f"✅ CLEANUP COMPLETE")
        self.log(f"Free space: {initial_space['free_gb']} GB → {final_space['free_gb']} GB")
        self.log(f"Space freed: {freed} GB")
        self.log("=" * 60)

        # Check if more cleanup needed
        if final_space["free_gb"] < self.min_free_gb:
            needed = self.min_free_gb - final_space["free_gb"]
            self.log(f"⚠️  Still need {needed} GB more to reach 15GB target")
            self.log("Finding large files for manual review...")
            large_files = self.find_large_files(0.5)
            if large_files:
                self.log("\n📊 Large files found (over 500MB):")
                for file in large_files[:20]:
                    self.log(f"  {file['size_gb']} GB - {file['path']}")
        else:
            self.log(
                f"✅ Target achieved: {final_space['free_gb']} GB free (target: {self.min_free_gb} GB)"
            )

        return final_space

    def setup_scheduled_task(self):
        """Set up scheduled task for automatic monitoring"""
        self.log("Setting up scheduled monitoring task...")

        # Create PowerShell script for scheduled task
        ps_script = Path("H:/The Gatekeeper/scripts/monitor_c_drive.ps1")
        ps_script.parent.mkdir(parents=True, exist_ok=True)

        script_content = f"""
# C: Drive Monitoring Script
$freeSpace = (Get-PSDrive C).Free / 1GB
$minFree = {self.min_free_gb}

if ($freeSpace -lt $minFree) {{
    Write-Host "⚠️  C: drive low on space: $([math]::Round($freeSpace, 2)) GB free"
    python "H:\\The Gatekeeper\\c_drive_manager.py" --auto-cleanup
}}
"""

        with open(ps_script, "w") as f:
            f.write(script_content)

        self.log(f"Created monitoring script: {ps_script}")
        self.log("Run as administrator to create scheduled task:")
        self.log(
            f'  schtasks /create /tn "Omega C Drive Monitor" /tr "powershell -File {ps_script}" /sc daily /st 02:00'
        )


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="C: Drive Cleanup Manager")
    parser.add_argument("--auto-cleanup", action="store_true", help="Run automatic cleanup")
    parser.add_argument("--check", action="store_true", help="Check drive space only")
    parser.add_argument("--find-large", action="store_true", help="Find large files")
    parser.add_argument("--setup-monitor", action="store_true", help="Setup monitoring")

    args = parser.parse_args()

    manager = CDriveManager()

    if args.check:
        space = manager.get_drive_space()
        print(f"\n💾 C: DRIVE STATUS")
        print("=" * 60)
        print(f"Total: {space['total_gb']} GB")
        print(f"Used: {space['used_gb']} GB")
        print(f"Free: {space['free_gb']} GB ({space['free_percent']}%)")
        print("=" * 60)

        if space["free_gb"] < manager.min_free_gb:
            print(f"⚠️  WARNING: Below {manager.min_free_gb} GB threshold!")
        else:
            print(f"✅ OK: Above {manager.min_free_gb} GB threshold")

    elif args.find_large:
        large_files = manager.find_large_files(0.5)
        print("\n📊 LARGE FILES (over 500MB):")
        print("=" * 60)
        for file in large_files[:30]:
            print(f"{file['size_gb']:6.2f} GB - {file['path']}")
        print("=" * 60)
        print(f"Total large files: {len(large_files)}")

    elif args.setup_monitor:
        manager.setup_scheduled_task()

    else:
        # Full cleanup
        space_before = manager.get_drive_space()

        print("\n💾 C: DRIVE CLEANUP")
        print("=" * 60)
        print(f"Current free space: {space_before['free_gb']} GB")
        print(f"Target: {manager.min_free_gb} GB")
        print("=" * 60)

        if manager.needs_cleanup() or args.auto_cleanup:
            print("\n🧹 Starting cleanup...")
            manager.perform_full_cleanup()
        else:
            print(f"\n✅ No cleanup needed ({space_before['free_gb']} GB free)")


if __name__ == "__main__":
    main()
