"""
Omega System Monitor - Comprehensive Health Check & Auto-Repair
Monitors code errors, dependencies, disk space, Git status, and system resources
Runs every 15-20 minutes and reports to The Gatekeeper
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import shutil
import psutil


class OmegaSystemMonitor:
    """Complete system monitoring and auto-repair for The Gatekeeper"""

    def __init__(self):
        self.base_path = Path(r"H:\The Gatekeeper")
        self.reports_dir = self.base_path / "system_monitor_reports"
        self.reports_dir.mkdir(exist_ok=True)

        self.log_file = self.reports_dir / "monitor_log.txt"
        self.status_file = self.reports_dir / "current_status.json"
        self.dependencies_file = self.base_path / "required_dependencies.json"

        # Critical dependencies for The Gatekeeper
        self.required_dependencies = {
            "python_packages": [
                "openai",
                "anthropic",
                "tiktoken",
                "requests",
                "numpy",
                "psutil",
                "gitpython",
                "pyyaml",
            ],
            "system_tools": ["git", "python", "pip"],
            "critical_paths": [
                self.base_path / "omega_download_manager.py",
                self.base_path / "omega_hf_cloud_jobs.py",
                self.base_path / "c_drive_manager.py",
                self.base_path / "omega_apps_manager.py",
                self.base_path / "omega_forensic_security.py",
            ],
        }

        self.save_dependencies_config()

    def save_dependencies_config(self):
        """Save dependency requirements for reference"""
        config = {
            "last_updated": datetime.now().isoformat(),
            "python_packages": self.required_dependencies["python_packages"],
            "system_tools": self.required_dependencies["system_tools"],
            "critical_paths": [str(p) for p in self.required_dependencies["critical_paths"]],
        }

        with open(self.dependencies_file, "w") as f:
            json.dump(config, f, indent=4)

    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def run_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """Run command and return success status and output"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, shell=False)
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def check_python_packages(self) -> Dict[str, Any]:
        """Check if required Python packages are installed"""
        self.log("🔍 Checking Python packages...")

        missing = []
        installed = []

        for package in self.required_dependencies["python_packages"]:
            success, output = self.run_command([sys.executable, "-m", "pip", "show", package])

            if success:
                installed.append(package)
            else:
                missing.append(package)

        status = {
            "total_required": len(self.required_dependencies["python_packages"]),
            "installed": installed,
            "missing": missing,
            "status": "OK" if not missing else "ISSUES",
        }

        if missing:
            self.log(f"⚠️  Missing packages: {', '.join(missing)}", "WARNING")
        else:
            self.log("✅ All Python packages installed")

        return status

    def install_missing_packages(self, missing: List[str]) -> Dict[str, bool]:
        """Auto-install missing Python packages"""
        self.log(f"📦 Installing missing packages: {', '.join(missing)}")

        results = {}

        for package in missing:
            self.log(f"  Installing {package}...")
            success, output = self.run_command(
                [sys.executable, "-m", "pip", "install", package, "--upgrade"]
            )

            results[package] = success

            if success:
                self.log(f"  ✅ {package} installed successfully")
            else:
                self.log(f"  ❌ {package} installation failed: {output}", "ERROR")

        return results

    def check_system_tools(self) -> Dict[str, Any]:
        """Check if required system tools are available"""
        self.log("🔧 Checking system tools...")

        available = []
        missing = []

        for tool in self.required_dependencies["system_tools"]:
            tool_path = shutil.which(tool)

            if tool_path:
                available.append({"tool": tool, "path": tool_path})
            else:
                missing.append(tool)

        status = {
            "available": available,
            "missing": missing,
            "status": "OK" if not missing else "ISSUES",
        }

        if missing:
            self.log(f"⚠️  Missing system tools: {', '.join(missing)}", "WARNING")
        else:
            self.log("✅ All system tools available")

        return status

    def check_code_errors(self) -> Dict[str, Any]:
        """Check for Python syntax/import errors in critical files"""
        self.log("🐛 Checking code for errors...")

        errors = {}
        total_issues = 0

        for file_path in self.required_dependencies["critical_paths"]:
            if not file_path.exists():
                errors[str(file_path)] = {"status": "MISSING", "error": "File does not exist"}
                total_issues += 1
                continue

            # Check for syntax errors
            success, output = self.run_command([sys.executable, "-m", "py_compile", str(file_path)])

            if success:
                errors[str(file_path)] = {"status": "OK", "issues": 0}
            else:
                errors[str(file_path)] = {
                    "status": "SYNTAX_ERROR",
                    "error": output[:200],  # First 200 chars
                }
                total_issues += 1

        status = {
            "files_checked": len(self.required_dependencies["critical_paths"]),
            "total_issues": total_issues,
            "details": errors,
            "status": "OK" if total_issues == 0 else "ISSUES",
        }

        if total_issues > 0:
            self.log(f"⚠️  Found {total_issues} files with issues", "WARNING")
        else:
            self.log("✅ All code files syntax-valid")

        return status

    def check_git_status(self) -> Dict[str, Any]:
        """Check Git repository status"""
        self.log("📊 Checking Git status...")

        try:
            # Check if we're in a Git repository
            success, output = self.run_command(["git", "rev-parse", "--git-dir"])

            if not success:
                return {"status": "NO_REPO", "message": "Not a git repository"}

            # Get status
            success, status_output = self.run_command(["git", "status", "--porcelain"])

            modified_files = []
            if success:
                for line in status_output.strip().split("\n"):
                    if line:
                        modified_files.append(line.strip())

            # Get current branch
            success, branch = self.run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            current_branch = branch.strip() if success else "unknown"

            # Get uncommitted changes count
            uncommitted_count = len(modified_files)

            result = {
                "status": "OK" if uncommitted_count <= 2 else "TOO_MANY_CHANGES",
                "current_branch": current_branch,
                "uncommitted_changes": uncommitted_count,
                "modified_files": modified_files[:10],  # First 10
                "target": "≤2 uncommitted files",
            }

            if uncommitted_count > 2:
                self.log(f"⚠️  {uncommitted_count} uncommitted changes (target: ≤2)", "WARNING")
            else:
                self.log(f"✅ Git status OK ({uncommitted_count} uncommitted)")

            return result

        except Exception as e:
            self.log(f"❌ Git check failed: {e}", "ERROR")
            return {"status": "ERROR", "error": str(e)}

    def check_disk_space(self) -> Dict[str, Any]:
        """Check C: drive space"""
        self.log("💾 Checking disk space...")

        try:
            c_drive = psutil.disk_usage("C:/")

            free_gb = c_drive.free / (1024**3)
            total_gb = c_drive.total / (1024**3)
            percent_free = (c_drive.free / c_drive.total) * 100

            status = "OK" if free_gb >= 15 else "LOW_SPACE"

            result = {
                "status": status,
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "percent_free": round(percent_free, 2),
                "target": "≥15 GB free",
            }

            if status == "LOW_SPACE":
                self.log(f"⚠️  C: drive low: {free_gb:.2f} GB (target: ≥15 GB)", "WARNING")
            else:
                self.log(f"✅ C: drive OK: {free_gb:.2f} GB free")

            return result

        except Exception as e:
            self.log(f"❌ Disk check failed: {e}", "ERROR")
            return {"status": "ERROR", "error": str(e)}

    def check_system_resources(self) -> Dict[str, Any]:
        """Check CPU, RAM, and system resources"""
        self.log("⚡ Checking system resources...")

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()

            result = {
                "cpu_percent": round(cpu_percent, 2),
                "ram_total_gb": round(memory.total / (1024**3), 2),
                "ram_used_gb": round(memory.used / (1024**3), 2),
                "ram_percent": round(memory.percent, 2),
                "status": "OK" if cpu_percent < 80 and memory.percent < 85 else "HIGH_USAGE",
            }

            if result["status"] == "HIGH_USAGE":
                self.log(
                    f"⚠️  High resource usage - CPU: {cpu_percent}%, RAM: {memory.percent}%",
                    "WARNING",
                )
            else:
                self.log(f"✅ System resources OK - CPU: {cpu_percent}%, RAM: {memory.percent}%")

            return result

        except Exception as e:
            self.log(f"❌ Resource check failed: {e}", "ERROR")
            return {"status": "ERROR", "error": str(e)}

    def auto_repair(self, scan_report: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt automatic repairs for detected issues"""
        self.log("🔧 Starting auto-repair...")

        repairs = []

        # Install missing Python packages
        if scan_report["python_packages"]["status"] == "ISSUES":
            missing = scan_report["python_packages"]["missing"]
            if missing:
                self.log(f"  Repairing: Installing {len(missing)} missing packages")
                install_results = self.install_missing_packages(missing)
                repairs.append(
                    {
                        "type": "package_install",
                        "results": install_results,
                        "success": all(install_results.values()),
                    }
                )

        # Cleanup disk if low
        if scan_report["disk_space"]["status"] == "LOW_SPACE":
            self.log("  Repairing: Running C: drive cleanup")
            try:
                # Import and run c_drive_manager
                c_manager_path = self.base_path / "c_drive_manager.py"
                if c_manager_path.exists():
                    success, output = self.run_command([sys.executable, str(c_manager_path)])
                    repairs.append(
                        {
                            "type": "disk_cleanup",
                            "success": success,
                            "output": output[:200],  # First 200 chars
                        }
                    )
            except Exception as e:
                self.log(f"  Failed disk cleanup: {e}", "ERROR")

        return {
            "repairs_attempted": len(repairs),
            "repairs": repairs,
            "timestamp": datetime.now().isoformat(),
        }

    def run_full_scan(self, auto_repair: bool = True) -> Dict[str, Any]:
        """Run complete system scan"""
        self.log("=" * 70)
        self.log("🔒 OMEGA SYSTEM MONITOR - FULL SCAN")
        self.log("=" * 70)

        scan_start = time.time()

        # Run all checks
        report = {
            "timestamp": datetime.now().isoformat(),
            "scan_duration_seconds": 0,
            "python_packages": self.check_python_packages(),
            "system_tools": self.check_system_tools(),
            "code_errors": self.check_code_errors(),
            "git_status": self.check_git_status(),
            "disk_space": self.check_disk_space(),
            "system_resources": self.check_system_resources(),
        }

        # Calculate overall status
        all_statuses = [
            report["python_packages"]["status"],
            report["system_tools"]["status"],
            report["code_errors"]["status"],
            report["git_status"]["status"],
            report["disk_space"]["status"],
            report["system_resources"]["status"],
        ]

        issues_count = sum(1 for s in all_statuses if s not in ["OK", "NO_REPO"])

        report["overall_status"] = "HEALTHY" if issues_count == 0 else "ISSUES_DETECTED"
        report["issues_count"] = issues_count

        # Auto-repair if requested
        if auto_repair and issues_count > 0:
            report["auto_repair"] = self.auto_repair(report)

        scan_duration = time.time() - scan_start
        report["scan_duration_seconds"] = round(scan_duration, 2)

        # Save report
        self.save_report(report)

        # Log summary
        self.log("=" * 70)
        self.log(f"✅ Scan complete: {report['overall_status']}")
        self.log(f"   Issues detected: {issues_count}")
        self.log(f"   Scan duration: {scan_duration:.2f}s")
        self.log("=" * 70)

        return report

    def save_report(self, report: Dict[str, Any]):
        """Save monitoring report"""
        # Save current status (for quick access)
        with open(self.status_file, "w") as f:
            json.dump(report, f, indent=4)

        # Save timestamped report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"system_scan_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=4)

        self.log(f"📄 Report saved: {report_file.name}")

        # Cleanup old reports (keep last 100)
        self.cleanup_old_reports()

    def cleanup_old_reports(self):
        """Keep only the most recent 100 reports"""
        reports = sorted(self.reports_dir.glob("system_scan_*.json"))

        if len(reports) > 100:
            for old_report in reports[:-100]:
                old_report.unlink()
            self.log(f"🗑️  Cleaned up {len(reports) - 100} old reports")

    def generate_gate_dashboard(self) -> str:
        """Generate human-readable dashboard for The Gatekeeper"""
        if not self.status_file.exists():
            return "No system monitoring data available yet. Run a scan first."

        with open(self.status_file) as f:
            report = json.load(f)

        dashboard = f"""
╔══════════════════════════════════════════════════════════════════════╗
║              🔒 THE GATEKEEPER - SYSTEM MONITOR                      ║
╚══════════════════════════════════════════════════════════════════════╝

📅 Last Scan: {report["timestamp"]}
⏱️  Duration: {report["scan_duration_seconds"]}s
🎯 Overall Status: {report["overall_status"]}
⚠️  Issues Detected: {report["issues_count"]}

─────────────────────────────────────────────────────────────────────

📦 PYTHON PACKAGES: {report["python_packages"]["status"]}
   • Installed: {len(report["python_packages"]["installed"])}/{report["python_packages"]["total_required"]}
"""

        if report["python_packages"]["missing"]:
            dashboard += f"   ⚠️  Missing: {', '.join(report['python_packages']['missing'])}\n"
        else:
            dashboard += "   ✅ All required packages present\n"

        dashboard += f"""
🔧 SYSTEM TOOLS: {report["system_tools"]["status"]}
   • Available: {len(report["system_tools"]["available"])}/{len(report["system_tools"]["available"]) + len(report["system_tools"]["missing"])}
"""

        if report["system_tools"]["missing"]:
            dashboard += f"   ⚠️  Missing: {', '.join(report['system_tools']['missing'])}\n"
        else:
            dashboard += "   ✅ All tools available\n"

        dashboard += f"""
🐛 CODE ERRORS: {report["code_errors"]["status"]}
   • Files Checked: {report["code_errors"]["files_checked"]}
   • Issues: {report["code_errors"]["total_issues"]}
"""

        if report["code_errors"]["total_issues"] > 0:
            for file, details in report["code_errors"]["details"].items():
                if details["status"] != "OK":
                    dashboard += f"   ⚠️  {Path(file).name}: {details['status']}\n"

        dashboard += f"""
📊 GIT STATUS: {report["git_status"]["status"]}
"""

        if report["git_status"].get("current_branch"):
            dashboard += f"   • Branch: {report['git_status']['current_branch']}\n"
            dashboard += f"   • Uncommitted Changes: {report['git_status']['uncommitted_changes']} (target: ≤2)\n"
            if report["git_status"]["uncommitted_changes"] > 2:
                dashboard += f"   ⚠️  Too many uncommitted changes!\n"

        dashboard += f"""
💾 DISK SPACE: {report["disk_space"]["status"]}
   • C: Drive Free: {report["disk_space"]["free_gb"]} GB / {report["disk_space"]["total_gb"]} GB
   • Percent Free: {report["disk_space"]["percent_free"]}%
   • Target: ≥15 GB free
"""

        if report["disk_space"]["status"] == "LOW_SPACE":
            dashboard += "   ⚠️  LOW SPACE WARNING!\n"

        dashboard += f"""
⚡ SYSTEM RESOURCES: {report["system_resources"]["status"]}
   • CPU Usage: {report["system_resources"]["cpu_percent"]}%
   • RAM Usage: {report["system_resources"]["ram_percent"]}%
   • RAM Used: {report["system_resources"]["ram_used_gb"]}/{report["system_resources"]["ram_total_gb"]} GB
"""

        if report["system_resources"]["status"] == "HIGH_USAGE":
            dashboard += "   ⚠️  HIGH RESOURCE USAGE!\n"

        if report.get("auto_repair"):
            dashboard += f"""
─────────────────────────────────────────────────────────────────────

🔧 AUTO-REPAIR ACTIONS:
   • Repairs Attempted: {report["auto_repair"]["repairs_attempted"]}
"""
            for repair in report["auto_repair"]["repairs"]:
                status_icon = "✅" if repair.get("success") else "❌"
                dashboard += f"   {status_icon} {repair['type']}\n"

        dashboard += """
─────────────────────────────────────────────────────────────────────
📍 Next scan: 15-20 minutes
📁 Report location: H:\\The Gatekeeper\\system_monitor_reports\\
═════════════════════════════════════════════════════════════════════
"""

        return dashboard


def main():
    """Main execution - run system monitoring scan"""
    monitor = OmegaSystemMonitor()

    # Run scan with auto-repair
    report = monitor.run_full_scan(auto_repair=True)

    # Generate and display dashboard
    dashboard = monitor.generate_gate_dashboard()
    print("\n" + dashboard)

    # Save dashboard to file for Gate to access
    dashboard_file = monitor.reports_dir / "GATE_DASHBOARD.txt"
    with open(dashboard_file, "w", encoding="utf-8") as f:
        f.write(dashboard)

    print(f"\n📊 Dashboard saved for Gate: {dashboard_file}")
    print(f"📁 Full JSON report: {monitor.status_file}")

    return report


if __name__ == "__main__":
    main()
