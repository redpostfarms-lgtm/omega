#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE Autonomous Administrator System
Continuous patrol, problem detection, and automatic resolution
Full source control authority with commit and branch management
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

try:
    from gate_admin_auth import GateAdminAuth
except ImportError:
    GateAdminAuth = None


class GateAutonomousAdmin:
    """
    GATE Autonomous Administrator
    - Continuous system patrol
    - Automatic problem detection and resolution
    - Full source control management
    - Code integration and testing
    - Resource access for problem solving
    """

    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or Path(__file__).parent
        self.auth = GateAdminAuth() if GateAdminAuth else None
        self.session = None

        # Patrol configuration
        self.patrol_interval = 300  # 5 minutes
        self.problem_log = self.root / "logs" / "gate_patrol.log"
        self.resolution_log = self.root / "logs" / "gate_resolutions.log"

        # Create log directories
        self.problem_log.parent.mkdir(parents=True, exist_ok=True)

        # Problem categories
        self.problems_detected = []
        self.resolutions_attempted = []

        # Git configuration
        self.git_configured = False
        self.commit_authority = True  # Gate has commit authority

    def authenticate(self, username: str = "gate", password: Optional[str] = None) -> bool:
        """Authenticate Gate as administrator"""
        if not self.auth:
            self.log("Warning: Authentication system not available")
            return False

        if password is None:
            # Try to load from environment
            password = os.getenv("GATE_ADMIN_PASSWORD")
            if not password:
                self.log("Error: No password provided")
                return False

        success, session = self.auth.authenticate(username, password)
        if success:
            self.session = session
            self.log(f"✓ Authenticated as {username} ({session['role']})")
            return True
        else:
            self.log(f"✗ Authentication failed: {session.get('error')}")
            return False

    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"

        print(log_entry)

        # Write to patrol log
        with open(self.problem_log, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

    def log_resolution(self, problem: str, solution: str, success: bool):
        """Log problem resolution attempt"""
        timestamp = datetime.now().isoformat()
        resolution = {
            "timestamp": timestamp,
            "problem": problem,
            "solution": solution,
            "success": success,
        }

        self.resolutions_attempted.append(resolution)

        with open(self.resolution_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(resolution) + "\n")

    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> Tuple[bool, str]:
        """Execute command with admin privileges"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.root,
                capture_output=True,
                text=True,
                timeout=60,
                encoding="utf-8",
                errors="replace",
            )

            success = result.returncode == 0
            output = result.stdout if success else result.stderr

            return success, output

        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    # ============================================
    # SOURCE CONTROL MANAGEMENT
    # ============================================

    def setup_git_config(self) -> bool:
        """Configure Git for Gate administrator"""
        self.log("Setting up Git configuration for GATE...")

        # Set Git user
        commands = [
            ["git", "config", "user.name", "GATE Administrator"],
            ["git", "config", "user.email", "gate@gatekeeper-omega.local"],
            ["git", "config", "commit.gpgsign", "false"],  # Disable GPG for automation
        ]

        for cmd in commands:
            success, output = self.run_command(cmd)
            if not success:
                self.log(f"Warning: {' '.join(cmd)} failed: {output}", "WARN")

        self.git_configured = True
        self.log("✓ Git configured for GATE")
        return True

    def check_git_status(self) -> Dict:
        """Check Git repository status"""
        status = {
            "is_repo": False,
            "branch": None,
            "uncommitted_changes": False,
            "untracked_files": [],
            "modified_files": [],
            "ahead_behind": {"ahead": 0, "behind": 0},
        }

        # Check if Git repo
        success, output = self.run_command(["git", "rev-parse", "--git-dir"])
        if not success:
            return status

        status["is_repo"] = True

        # Get current branch
        success, output = self.run_command(["git", "branch", "--show-current"])
        if success:
            status["branch"] = output.strip()

        # Check for uncommitted changes
        success, output = self.run_command(["git", "status", "--porcelain"])
        if success and output.strip():
            status["uncommitted_changes"] = True

            for line in output.strip().split("\n"):
                if line.startswith("??"):
                    status["untracked_files"].append(line[3:])
                elif line.startswith(" M") or line.startswith("M "):
                    status["modified_files"].append(line[3:])

        return status

    def auto_commit_changes(self, message: Optional[str] = None) -> bool:
        """Automatically commit changes with Gate's authority"""
        if not self.commit_authority:
            self.log("Error: No commit authority", "ERROR")
            return False

        if not self.git_configured:
            self.setup_git_config()

        git_status = self.check_git_status()
        if not git_status["uncommitted_changes"]:
            self.log("No uncommitted changes to commit")
            return True

        # Generate commit message if not provided
        if not message:
            message = f"GATE Auto-commit: System maintenance and improvements\n\n"
            message += f"Modified files: {len(git_status['modified_files'])}\n"
            message += f"Untracked files: {len(git_status['untracked_files'])}\n"
            message += f"Timestamp: {datetime.now().isoformat()}\n\n"
            message += "Co-Authored-By: GATE Administrator <gate@gatekeeper-omega.local>"

        # Stage all changes
        self.log("Staging all changes...")
        success, output = self.run_command(["git", "add", "-A"])
        if not success:
            self.log(f"Failed to stage changes: {output}", "ERROR")
            return False

        # Commit
        self.log("Committing changes...")
        success, output = self.run_command(["git", "commit", "-m", message])
        if success:
            self.log(f"✓ Committed: {message.split(chr(10))[0]}")
            return True
        else:
            self.log(f"Commit failed: {output}", "ERROR")
            return False

    def create_branch(self, branch_name: str) -> bool:
        """Create and switch to new branch"""
        self.log(f"Creating branch: {branch_name}")

        # Create and checkout branch
        success, output = self.run_command(["git", "checkout", "-b", branch_name])
        if success:
            self.log(f"✓ Created and switched to branch: {branch_name}")
            return True
        else:
            self.log(f"Failed to create branch: {output}", "ERROR")
            return False

    def push_to_remote(self, branch: Optional[str] = None, force: bool = False) -> bool:
        """Push commits to remote repository"""
        if not branch:
            git_status = self.check_git_status()
            branch = git_status["branch"]

        if not branch:
            self.log("No branch to push", "ERROR")
            return False

        self.log(f"Pushing to remote: {branch}")

        cmd = ["git", "push", "-u", "origin", branch]
        if force:
            cmd.insert(2, "--force")

        success, output = self.run_command(cmd)
        if success:
            self.log(f"✓ Pushed to origin/{branch}")
            return True
        else:
            self.log(f"Push failed: {output}", "ERROR")
            return False

    # ============================================
    # PROBLEM DETECTION
    # ============================================

    async def patrol_system(self):
        """Continuous system patrol for problems"""
        self.log("=" * 70)
        self.log("GATE AUTONOMOUS PATROL - Starting")
        self.log("=" * 70)

        problems = []

        # 1. Check Git repository
        self.log("Checking Git repository...")
        git_problems = self.check_git_problems()
        problems.extend(git_problems)

        # 2. Check Python files for errors
        self.log("Checking Python files...")
        python_problems = self.check_python_files()
        problems.extend(python_problems)

        # 3. Check dependencies
        self.log("Checking dependencies...")
        dependency_problems = self.check_dependencies()
        problems.extend(dependency_problems)

        # 4. Check file structure
        self.log("Checking file structure...")
        structure_problems = self.check_file_structure()
        problems.extend(structure_problems)

        # 5. Check test results
        self.log("Checking test results...")
        test_problems = self.check_test_results()
        problems.extend(test_problems)

        self.problems_detected = problems
        self.log(f"\n{'=' * 70}")
        self.log(f"Patrol complete: {len(problems)} problems detected")
        self.log(f"{'=' * 70}\n")

        return problems

    def check_git_problems(self) -> List[Dict]:
        """Detect Git-related problems"""
        problems = []

        git_status = self.check_git_status()

        if not git_status["is_repo"]:
            problems.append(
                {
                    "category": "git",
                    "severity": "high",
                    "description": "Not a Git repository",
                    "solution": "initialize_git",
                }
            )
            return problems

        # Check for uncommitted changes
        if git_status["uncommitted_changes"]:
            problems.append(
                {
                    "category": "git",
                    "severity": "medium",
                    "description": f"Uncommitted changes: {len(git_status['modified_files'])} modified, {len(git_status['untracked_files'])} untracked",
                    "solution": "auto_commit",
                    "data": git_status,
                }
            )

        # Check if branch is up to date with remote
        success, output = self.run_command(["git", "status", "-sb"])
        if success and "ahead" in output:
            problems.append(
                {
                    "category": "git",
                    "severity": "low",
                    "description": "Local branch ahead of remote",
                    "solution": "push_to_remote",
                }
            )

        return problems

    def check_python_files(self) -> List[Dict]:
        """Check Python files for syntax errors"""
        problems = []

        for py_file in self.root.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue

            # Check syntax
            success, output = self.run_command([sys.executable, "-m", "py_compile", str(py_file)])

            if not success:
                problems.append(
                    {
                        "category": "python",
                        "severity": "high",
                        "description": f"Syntax error in {py_file.name}",
                        "solution": "fix_syntax",
                        "file": str(py_file),
                        "error": output,
                    }
                )

        return problems

    def check_dependencies(self) -> List[Dict]:
        """Check for missing or outdated dependencies"""
        problems = []

        # Check if requirements.txt exists
        req_file = self.root / "requirements.txt"
        if not req_file.exists():
            problems.append(
                {
                    "category": "dependencies",
                    "severity": "medium",
                    "description": "requirements.txt not found",
                    "solution": "create_requirements",
                }
            )
            return problems

        # Try to import critical modules
        critical_modules = ["torch", "transformers", "websockets", "aiofiles", "psutil"]

        for module in critical_modules:
            try:
                __import__(module)
            except ImportError:
                problems.append(
                    {
                        "category": "dependencies",
                        "severity": "high",
                        "description": f"Missing critical module: {module}",
                        "solution": "install_dependencies",
                        "module": module,
                    }
                )

        return problems

    def check_file_structure(self) -> List[Dict]:
        """Check for missing essential directories"""
        problems = []

        required_dirs = ["data", "config", "models", "logs", "output", "tests"]

        for dir_name in required_dirs:
            dir_path = self.root / dir_name
            if not dir_path.exists():
                problems.append(
                    {
                        "category": "structure",
                        "severity": "medium",
                        "description": f"Missing directory: {dir_name}",
                        "solution": "create_directory",
                        "path": str(dir_path),
                    }
                )

        return problems

    def check_test_results(self) -> List[Dict]:
        """Check recent test results"""
        problems = []

        # Check if test reports exist
        report_dir = self.root / "test_reports"
        if not report_dir.exists():
            problems.append(
                {
                    "category": "testing",
                    "severity": "low",
                    "description": "No test reports found",
                    "solution": "run_tests",
                }
            )
            return problems

        # Check master report
        master_report = report_dir / "master_test_report.json"
        if master_report.exists():
            try:
                with open(master_report) as f:
                    data = json.load(f)

                # Check for failures
                if data.get("pytest_results", {}).get("status") == "FAILED":
                    problems.append(
                        {
                            "category": "testing",
                            "severity": "high",
                            "description": "Test suite has failures",
                            "solution": "investigate_test_failures",
                            "data": data,
                        }
                    )
            except Exception:
                pass

        return problems

    # ============================================
    # PROBLEM RESOLUTION
    # ============================================

    async def resolve_problems(self, problems: List[Dict]):
        """Automatically resolve detected problems"""
        self.log("\n" + "=" * 70)
        self.log("GATE AUTONOMOUS RESOLUTION - Starting")
        self.log("=" * 70)

        resolved = 0
        failed = 0

        for problem in problems:
            self.log(f"\n[{problem['severity'].upper()}] {problem['description']}")

            solution_func = getattr(self, f"solve_{problem['solution']}", None)
            if solution_func:
                try:
                    success = await solution_func(problem) if asyncio.iscoroutinefunction(
                        solution_func
                    ) else solution_func(problem)

                    if success:
                        self.log(f"  ✓ Resolved: {problem['solution']}")
                        resolved += 1
                        self.log_resolution(
                            problem["description"], problem["solution"], True
                        )
                    else:
                        self.log(f"  ✗ Failed to resolve: {problem['solution']}")
                        failed += 1
                        self.log_resolution(
                            problem["description"], problem["solution"], False
                        )

                except Exception as e:
                    self.log(f"  ✗ Error resolving: {str(e)}", "ERROR")
                    failed += 1
                    self.log_resolution(problem["description"], str(e), False)
            else:
                self.log(f"  ? No solution handler for: {problem['solution']}", "WARN")

        self.log(f"\n{'=' * 70}")
        self.log(f"Resolution complete: {resolved} resolved, {failed} failed")
        self.log(f"{'=' * 70}\n")

        return resolved, failed

    # Solution handlers
    def solve_auto_commit(self, problem: Dict) -> bool:
        """Auto-commit uncommitted changes"""
        return self.auto_commit_changes()

    def solve_push_to_remote(self, problem: Dict) -> bool:
        """Push local commits to remote"""
        return self.push_to_remote()

    def solve_initialize_git(self, problem: Dict) -> bool:
        """Initialize Git repository"""
        success, output = self.run_command(["git", "init"])
        if success:
            self.setup_git_config()
            return True
        return False

    def solve_create_directory(self, problem: Dict) -> bool:
        """Create missing directory"""
        try:
            Path(problem["path"]).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def solve_install_dependencies(self, problem: Dict) -> bool:
        """Install missing dependency"""
        module = problem.get("module")
        if module:
            success, output = self.run_command(
                [sys.executable, "-m", "pip", "install", module]
            )
            return success
        return False

    def solve_run_tests(self, problem: Dict) -> bool:
        """Run test suite"""
        test_script = self.root / "run_comprehensive_tests.py"
        if test_script.exists():
            success, output = self.run_command([sys.executable, str(test_script)])
            return success
        return False

    # ============================================
    # CODE INTEGRATION & TESTING
    # ============================================

    def validate_code_integration(self, files: List[Path]) -> Tuple[bool, List[str]]:
        """Test code integration before committing"""
        self.log("Validating code integration...")

        issues = []

        # 1. Check syntax
        for file_path in files:
            if file_path.suffix == ".py":
                success, output = self.run_command(
                    [sys.executable, "-m", "py_compile", str(file_path)]
                )
                if not success:
                    issues.append(f"Syntax error in {file_path.name}: {output}")

        # 2. Run quick tests
        test_file = self.root / "tests" / "test_basic.py"
        if test_file.exists():
            success, output = self.run_command(
                [sys.executable, "-m", "pytest", str(test_file), "-v"]
            )
            if not success:
                issues.append(f"Basic tests failed: {output[:200]}")

        if issues:
            self.log(f"✗ Validation failed with {len(issues)} issues", "ERROR")
            for issue in issues:
                self.log(f"  - {issue}", "ERROR")
            return False, issues
        else:
            self.log("✓ Code validation passed")
            return True, []

    async def integrate_and_commit(self, message: str) -> bool:
        """Integrate code changes, test, and commit"""
        self.log("Starting code integration and commit process...")

        # 1. Check Git status
        git_status = self.check_git_status()
        if not git_status["uncommitted_changes"]:
            self.log("No changes to integrate")
            return True

        # 2. Collect changed files
        changed_files = [
            self.root / f for f in git_status["modified_files"] + git_status["untracked_files"]
        ]

        # 3. Validate integration
        valid, issues = self.validate_code_integration(changed_files)
        if not valid:
            self.log("Cannot commit: code validation failed", "ERROR")
            return False

        # 4. Commit changes
        return self.auto_commit_changes(message)

    # ============================================
    # CONTINUOUS PATROL LOOP
    # ============================================

    async def start_continuous_patrol(self, interval: Optional[int] = None):
        """Start continuous patrol loop"""
        interval = interval or self.patrol_interval

        self.log("=" * 70)
        self.log("GATE CONTINUOUS PATROL - ACTIVE")
        self.log(f"Patrol interval: {interval} seconds")
        self.log("=" * 70)

        patrol_count = 0

        try:
            while True:
                patrol_count += 1
                self.log(f"\n\n{'#' * 70}")
                self.log(f"Patrol #{patrol_count} - {datetime.now().isoformat()}")
                self.log(f"{'#' * 70}\n")

                # Run patrol
                problems = await self.patrol_system()

                # Resolve problems
                if problems:
                    resolved, failed = await self.resolve_problems(problems)

                    # If critical problems resolved, commit changes
                    if resolved > 0:
                        await self.integrate_and_commit(
                            f"GATE Auto-resolution: Fixed {resolved} issues\n\n"
                            f"Patrol #{patrol_count}\n"
                            f"Resolved: {resolved}, Failed: {failed}"
                        )

                # Wait for next patrol
                self.log(f"\nNext patrol in {interval} seconds...")
                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            self.log("\n\nPatrol stopped by user")
        except Exception as e:
            self.log(f"\n\nPatrol error: {e}", "ERROR")
            raise


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  GATE AUTONOMOUS ADMINISTRATOR")
    print("=" * 70 + "\n")

    admin = GateAutonomousAdmin()

    # Setup Git
    admin.setup_git_config()

    print("\nOptions:")
    print("  1. Run single patrol")
    print("  2. Start continuous patrol (every 5 minutes)")
    print("  3. Check Git status")
    print("  4. Commit all changes")
    print("  5. Run code validation")

    choice = input("\nChoice (1-5): ").strip()

    if choice == "1":
        problems = await admin.patrol_system()
        if problems:
            await admin.resolve_problems(problems)
    elif choice == "2":
        await admin.start_continuous_patrol()
    elif choice == "3":
        status = admin.check_git_status()
        print(json.dumps(status, indent=2))
    elif choice == "4":
        admin.auto_commit_changes()
    elif choice == "5":
        import glob

        py_files = [Path(f) for f in glob.glob("*.py")]
        valid, issues = admin.validate_code_integration(py_files)
        print(f"Validation: {'✓ PASS' if valid else '✗ FAIL'}")


if __name__ == "__main__":
    asyncio.run(main())
