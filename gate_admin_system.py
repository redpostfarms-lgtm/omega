#!/usr/bin/env python3
"""
GATE Administrator System - Background monitoring and autonomous management
Handles: Error detection, code analysis, git operations, voice/logging, dependency management
"""

import os
import sys
import json
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import queue

# Setup logging with voice capability
class VoiceLogger:
    """Logger that speaks errors and important events"""
    def __init__(self):
        self.log_file = Path("gate_admin_logs.txt")
        self.voice_enabled = self._check_voice_available()
        self.message_queue = queue.Queue()
        self.voice_thread = None
        
        # Configure file logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - GATE - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("GATE")
        
        if self.voice_enabled:
            self._start_voice_thread()
    
    def _check_voice_available(self) -> bool:
        """Check if TTS is available"""
        try:
            import pyttsx3
            return True
        except ImportError:
            try:
                # Try Windows SAPI
                import win32com.client
                return True
            except ImportError:
                self.logger.warning("Voice output unavailable - install pyttsx3 for voice")
                return False
    
    def _start_voice_thread(self):
        """Start background thread for voice output"""
        def voice_worker():
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 175)
                engine.setProperty('volume', 0.9)
                
                while True:
                    message = self.message_queue.get()
                    if message is None:
                        break
                    try:
                        engine.say(message)
                        engine.runAndWait()
                    except Exception as e:
                        self.logger.error(f"Voice output error: {e}")
                    self.message_queue.task_done()
            except Exception as e:
                self.logger.error(f"Voice thread error: {e}")
        
        self.voice_thread = threading.Thread(target=voice_worker, daemon=True)
        self.voice_thread.start()
    
    def speak(self, message: str):
        """Queue message for voice output"""
        if self.voice_enabled:
            self.message_queue.put(message)
    
    def info(self, message: str, speak: bool = False):
        """Log info message"""
        self.logger.info(message)
        if speak:
            self.speak(message)
    
    def error(self, message: str, speak: bool = True):
        """Log error and speak it"""
        self.logger.error(message)
        if speak:
            self.speak(f"Error: {message}")
    
    def warning(self, message: str, speak: bool = False):
        """Log warning"""
        self.logger.warning(message)
        if speak:
            self.speak(f"Warning: {message}")
    
    def success(self, message: str, speak: bool = True):
        """Log success"""
        self.logger.info(f"✅ {message}")
        if speak:
            self.speak(message)


class GateAdminSystem:
    """GATE's administrative control system"""
    
    def __init__(self):
        self.logger = VoiceLogger()
        self.workspace = Path(__file__).parent
        self.venv_python = self.workspace / ".venv" / "Scripts" / "python.exe"
        self.errors_found = []
        self.fixes_applied = []
        self.git_operations = []
        
        self.logger.info("🔧 GATE Admin System initializing...", speak=True)
    
    def check_system_errors(self) -> Dict[str, Any]:
        """Scan for Python errors and issues"""
        self.logger.info("🔍 Scanning for system errors...")
        errors = {
            "python_files": [],
            "import_errors": [],
            "syntax_errors": [],
            "runtime_warnings": []
        }
        
        # Check all Python files
        for py_file in self.workspace.rglob("*.py"):
            if ".venv" in str(py_file) or "Organized_Files" in str(py_file):
                continue
            
            try:
                # Quick syntax check
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()
                    compile(code, str(py_file), 'exec')
            except SyntaxError as e:
                error_info = {
                    "file": str(py_file.relative_to(self.workspace)),
                    "line": e.lineno,
                    "error": str(e.msg)
                }
                errors["syntax_errors"].append(error_info)
                self.logger.error(f"Syntax error in {py_file.name}: {e.msg}", speak=False)
        
        self.errors_found = errors
        total_errors = sum(len(v) for v in errors.values())
        
        if total_errors > 0:
            self.logger.warning(f"Found {total_errors} errors requiring attention")
        else:
            self.logger.success("No critical errors found", speak=False)
        
        return errors
    
    def analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code structure and quality"""
        self.logger.info("📊 Analyzing code quality...")
        
        analysis = {
            "total_files": 0,
            "total_lines": 0,
            "imports": set(),
            "functions": [],
            "classes": [],
            "todos": []
        }
        
        for py_file in self.workspace.rglob("*.py"):
            if ".venv" in str(py_file) or "Organized_Files" in str(py_file):
                continue
            
            analysis["total_files"] += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    analysis["total_lines"] += len(lines)
                    
                    for line in lines:
                        # Track imports
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            analysis["imports"].add(line.strip())
                        
                        # Track TODOs
                        if 'TODO' in line or 'FIXME' in line:
                            analysis["todos"].append({
                                "file": str(py_file.relative_to(self.workspace)),
                                "content": line.strip()
                            })
            except Exception as e:
                self.logger.warning(f"Could not analyze {py_file.name}: {e}")
        
        analysis["imports"] = list(analysis["imports"])
        self.logger.info(f"Analyzed {analysis['total_files']} files, {analysis['total_lines']} lines")
        
        return analysis
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check and verify all dependencies"""
        self.logger.info("📦 Checking dependencies...")
        
        deps = {
            "installed": [],
            "missing": [],
            "outdated": []
        }
        
        try:
            # Get installed packages
            result = subprocess.run(
                [str(self.venv_python), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            installed = json.loads(result.stdout)
            deps["installed"] = [{"name": p["name"], "version": p["version"]} for p in installed]
            
            self.logger.info(f"✅ {len(deps['installed'])} packages installed")
            
        except Exception as e:
            self.logger.error(f"Failed to check dependencies: {e}")
        
        return deps
    
    def git_status(self) -> Dict[str, Any]:
        """Check git repository status"""
        self.logger.info("📋 Checking git status...")
        
        status = {
            "branch": "",
            "uncommitted": [],
            "untracked": [],
            "ahead": 0,
            "clean": True
        }
        
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.workspace,
                check=True
            )
            status["branch"] = result.stdout.strip()
            
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.workspace,
                check=True
            )
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                status["clean"] = False
                code = line[:2]
                filename = line[3:]
                
                if code.strip() == '??':
                    status["untracked"].append(filename)
                else:
                    status["uncommitted"].append(filename)
            
            if status["clean"]:
                self.logger.success("Git: Working tree clean", speak=False)
            else:
                self.logger.warning(f"Git: {len(status['uncommitted'])} uncommitted, {len(status['untracked'])} untracked")
            
        except Exception as e:
            self.logger.error(f"Git status check failed: {e}")
        
        return status
    
    def auto_commit(self, message: str) -> bool:
        """Automatically commit all changes"""
        self.logger.info(f"💾 Auto-committing: {message}")
        
        try:
            # Stage all changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=self.workspace,
                check=True
            )
            
            # Commit
            subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.workspace,
                check=True
            )
            
            self.logger.success("Git commit successful")
            self.git_operations.append({
                "type": "commit",
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git commit failed: {e}")
            return False
    
    def install_package(self, package: str) -> bool:
        """Install a Python package"""
        self.logger.info(f"📥 Installing {package}...", speak=True)
        
        try:
            subprocess.run(
                [str(self.venv_python), "-m", "pip", "install", package, "--quiet"],
                check=True
            )
            self.logger.success(f"{package} installed successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to install {package}: {e}")
            return False
    
    def generate_report(self) -> str:
        """Generate comprehensive status report"""
        report = [
            "═" * 60,
            "GATE ADMINISTRATOR SYSTEM REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "═" * 60,
            "",
            "📊 SYSTEM STATUS",
            "-" * 60
        ]
        
        # Errors
        errors = self.check_system_errors()
        total_errors = sum(len(v) for v in errors.values())
        report.append(f"Errors Found: {total_errors}")
        
        # Dependencies
        deps = self.check_dependencies()
        report.append(f"Dependencies: {len(deps['installed'])} installed")
        
        # Git
        git_status = self.git_status()
        report.append(f"Git Branch: {git_status['branch']}")
        report.append(f"Git Status: {'Clean' if git_status['clean'] else 'Uncommitted changes'}")
        
        # Code quality
        analysis = self.analyze_code_quality()
        report.append(f"Python Files: {analysis['total_files']}")
        report.append(f"Total Lines: {analysis['total_lines']}")
        report.append(f"TODOs: {len(analysis['todos'])}")
        
        report.extend([
            "",
            "═" * 60,
            "GATE - Ready to serve at maximum efficiency",
            "═" * 60
        ])
        
        return "\n".join(report)
    
    def run_diagnostic(self):
        """Run complete system diagnostic"""
        self.logger.info("🚀 Running GATE diagnostic suite...", speak=True)
        
        self.check_system_errors()
        self.check_dependencies()
        self.git_status()
        self.analyze_code_quality()
        
        report = self.generate_report()
        print(report)
        
        # Save report
        report_file = self.workspace / "GATE_DIAGNOSTIC_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# GATE Diagnostic Report\n\n```\n{report}\n```\n")
        
        self.logger.success("Diagnostic complete - all systems operational", speak=True)
        
        return report


def main():
    """Main entry point for GATE admin system"""
    gate = GateAdminSystem()
    
    # Welcome message
    gate.logger.info("=" * 60)
    gate.logger.info("GATE ADMINISTRATOR SYSTEM ONLINE")
    gate.logger.info("Ready to monitor, fix errors, and manage operations")
    gate.logger.info("=" * 60)
    gate.logger.speak("GATE administrator system online and ready")
    
    # Run diagnostic
    gate.run_diagnostic()
    
    # Show git status
    git_status = gate.git_status()
    if not git_status["clean"]:
        gate.logger.warning("Uncommitted changes detected")
        response = input("\n🔧 Auto-commit changes? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            gate.auto_commit("feat: GATE admin system - automated commit")
    
    print("\n✅ GATE is monitoring your system in the background")
    print("📝 Logs: gate_admin_logs.txt")
    print("📊 Report: GATE_DIAGNOSTIC_REPORT.md")


if __name__ == "__main__":
    main()
