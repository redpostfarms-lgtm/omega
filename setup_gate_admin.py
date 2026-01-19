#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE Administrator Setup and Control Center
Complete setup for Gate's autonomous administration
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

try:
    from gate_admin_auth import GateAdminAuth
    from gate_autonomous_admin import GateAutonomousAdmin
    from gate_problem_solver import GateProblemSolver
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


class GateSetup:
    """Complete setup and control for GATE administrator"""

    def __init__(self):
        self.root = Path(__file__).parent
        self.auth = GateAdminAuth()
        self.admin = GateAutonomousAdmin()
        self.solver = GateProblemSolver()

    def print_banner(self):
        """Print setup banner"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  GATE ADMINISTRATOR SETUP & CONTROL CENTER".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70 + "\n")

    def check_system_status(self) -> Dict:
        """Check current system status"""
        status = {
            "admin_configured": False,
            "admin_authenticated": False,
            "git_configured": False,
            "git_status": None,
            "dependencies_installed": True,
            "test_status": "unknown",
        }

        # Check admin
        auth_status = self.auth.get_status()
        status["admin_configured"] = auth_status["admin_configured"]
        status["admin_authenticated"] = auth_status["session_active"]

        # Check Git
        git_status = self.admin.check_git_status()
        status["git_configured"] = git_status["is_repo"]
        status["git_status"] = git_status

        # Check dependencies
        critical_modules = ["torch", "transformers", "websockets", "aiofiles"]
        for module in critical_modules:
            try:
                __import__(module)
            except ImportError:
                status["dependencies_installed"] = False
                break

        return status

    def display_status(self, status: Dict):
        """Display system status"""
        print("\n" + "=" * 70)
        print("  SYSTEM STATUS")
        print("=" * 70)

        # Admin status
        admin_icon = "✓" if status["admin_configured"] else "✗"
        auth_icon = "✓" if status["admin_authenticated"] else "✗"
        print(f"\nAdministrator:")
        print(f"  {admin_icon} Configured: {status['admin_configured']}")
        print(f"  {auth_icon} Authenticated: {status['admin_authenticated']}")

        # Git status
        git_icon = "✓" if status["git_configured"] else "✗"
        print(f"\nSource Control:")
        print(f"  {git_icon} Git repository: {status['git_configured']}")
        if status["git_status"]:
            branch = status["git_status"].get("branch", "N/A")
            changes = status["git_status"].get("uncommitted_changes", False)
            print(f"  • Branch: {branch}")
            print(f"  • Uncommitted changes: {changes}")

        # Dependencies
        dep_icon = "✓" if status["dependencies_installed"] else "✗"
        print(f"\nDependencies:")
        print(f"  {dep_icon} Core modules installed: {status['dependencies_installed']}")

        print("\n" + "=" * 70 + "\n")

    async def setup_wizard(self):
        """Interactive setup wizard"""
        self.print_banner()

        print("Welcome to GATE Administrator Setup!")
        print("\nThis wizard will configure GATE with full administrative access.")
        print("\n" + "-" * 70 + "\n")

        # Step 1: Check current status
        print("[Step 1/5] Checking system status...")
        status = self.check_system_status()
        self.display_status(status)

        # Step 2: Setup administrator
        if not status["admin_configured"]:
            print("[Step 2/5] Setting up GATE administrator...")
            print("\nGATE needs administrator credentials.")
            print("Options:")
            print("  1. Auto-generate secure password (recommended)")
            print("  2. Set custom password")

            choice = input("\nChoice (1-2): ").strip()

            if choice == "1":
                result = self.auth.setup_admin()
            else:
                password = input("Enter password for GATE: ")
                result = self.auth.setup_admin(password=password)

            print(f"\n{result['message']}")

            if "password" in result:
                print("\n" + "=" * 70)
                print("GATE Administrator Credentials")
                print("=" * 70)
                print(f"Username: {result['username']}")
                print(f"Password: {result['password']}")
                print("=" * 70)
                print("\n⚠️  SAVE THIS PASSWORD! It cannot be recovered.")
                print("=" * 70 + "\n")

                input("Press Enter after saving the password...")
        else:
            print("[Step 2/5] Administrator already configured ✓")

        # Step 3: Configure Git
        if not status["git_configured"]:
            print("\n[Step 3/5] Configuring Git...")
            self.admin.setup_git_config()
            print("✓ Git configured for GATE")
        else:
            print("\n[Step 3/5] Git already configured ✓")

        # Step 4: Run initial patrol
        print("\n[Step 4/5] Running initial system patrol...")
        problems = await self.admin.patrol_system()

        if problems:
            print(f"\nFound {len(problems)} issues:")
            for i, problem in enumerate(problems[:5], 1):
                print(f"  {i}. [{problem['severity']}] {problem['description']}")

            fix_now = input("\nFix these issues now? (y/n): ").strip().lower()
            if fix_now == "y":
                resolved, failed = await self.admin.resolve_problems(problems)
                print(f"\n✓ Resolved {resolved} issues, {failed} failed")

        # Step 5: Setup complete
        print("\n[Step 5/5] Setup complete!")
        print("\n" + "=" * 70)
        print("  GATE ADMINISTRATOR READY")
        print("=" * 70)

        print("\nGATE can now:")
        print("  ✓ Monitor the system continuously")
        print("  ✓ Detect and resolve problems automatically")
        print("  ✓ Manage source control (commits, branches)")
        print("  ✓ Fix code issues and conflicts")
        print("  ✓ Run tests and validate integration")

        print("\nNext steps:")
        print("  1. Run one-time patrol: python gate_autonomous_admin.py")
        print("  2. Start continuous daemon: python gate_daemon.py")
        print("  3. Manual problem solving: python gate_problem_solver.py")

        print("\n" + "=" * 70 + "\n")

    def control_menu(self):
        """Control menu for GATE operations"""
        while True:
            self.print_banner()

            status = self.check_system_status()
            self.display_status(status)

            print("GATE Administrator Control Menu:")
            print("\nPatrol & Monitoring:")
            print("  1. Run single patrol")
            print("  2. Start continuous patrol (5 min interval)")
            print("  3. Start 24/7 daemon")

            print("\nSource Control:")
            print("  4. Check Git status")
            print("  5. Commit all changes")
            print("  6. Push to remote")

            print("\nProblem Solving:")
            print("  7. Run comprehensive code fix")
            print("  8. Test code integration")
            print("  9. Find and fix conflicts")

            print("\nSystem:")
            print("  10. View authentication status")
            print("  11. Re-authenticate")
            print("  0. Exit")

            choice = input("\nChoice (0-11): ").strip()

            if choice == "0":
                print("\nExiting...")
                break
            elif choice == "1":
                asyncio.run(self.single_patrol())
            elif choice == "2":
                asyncio.run(self.continuous_patrol())
            elif choice == "3":
                self.start_daemon()
            elif choice == "4":
                self.show_git_status()
            elif choice == "5":
                self.commit_changes()
            elif choice == "6":
                self.push_to_remote()
            elif choice == "7":
                asyncio.run(self.comprehensive_fix())
            elif choice == "8":
                self.test_integration()
            elif choice == "9":
                self.fix_conflicts()
            elif choice == "10":
                self.show_auth_status()
            elif choice == "11":
                self.authenticate()

            if choice != "0":
                input("\nPress Enter to continue...")

    async def single_patrol(self):
        """Run single patrol"""
        print("\n" + "=" * 70)
        print("  RUNNING SINGLE PATROL")
        print("=" * 70 + "\n")

        problems = await self.admin.patrol_system()

        if problems:
            print(f"\nResolving {len(problems)} problems...")
            resolved, failed = await self.admin.resolve_problems(problems)
            print(f"\n✓ Resolved: {resolved}, Failed: {failed}")

    async def continuous_patrol(self):
        """Start continuous patrol"""
        print("\n" + "=" * 70)
        print("  CONTINUOUS PATROL ACTIVE")
        print("=" * 70)
        print("\nPress Ctrl+C to stop\n")

        await self.admin.start_continuous_patrol()

    def start_daemon(self):
        """Start daemon"""
        print("\n" + "=" * 70)
        print("  STARTING GATE DAEMON")
        print("=" * 70)
        print("\nThe daemon will run in continuous mode.")
        print("Run this in a separate terminal:")
        print("\n  python gate_daemon.py\n")

    def show_git_status(self):
        """Show Git status"""
        status = self.admin.check_git_status()
        print("\n" + json.dumps(status, indent=2))

    def commit_changes(self):
        """Commit changes"""
        print("\n" + "=" * 70)
        print("  COMMITTING CHANGES")
        print("=" * 70 + "\n")

        message = input("Commit message (or Enter for auto): ").strip()
        self.admin.auto_commit_changes(message if message else None)

    def push_to_remote(self):
        """Push to remote"""
        print("\n" + "=" * 70)
        print("  PUSHING TO REMOTE")
        print("=" * 70 + "\n")

        self.admin.push_to_remote()

    async def comprehensive_fix(self):
        """Run comprehensive fix"""
        print("\n" + "=" * 70)
        print("  COMPREHENSIVE CODE FIX")
        print("=" * 70 + "\n")

        results = await self.solver.comprehensive_fix()

        print(f"\nResults:")
        print(f"  Syntax fixes: {results['syntax_fixes']}")
        print(f"  Import optimizations: {results['import_optimizations']}")
        print(f"  Conflicts resolved: {results['conflicts_resolved']}")
        print(f"  Issues: {len(results['issues'])}")

    def test_integration(self):
        """Test code integration"""
        import glob

        py_files = [Path(f) for f in glob.glob("*.py")]
        success, issues = self.solver.test_code_integration(py_files)

        print(f"\nIntegration: {'✓ PASS' if success else '✗ FAIL'}")
        if issues:
            for issue in issues:
                print(f"  - {issue}")

    def fix_conflicts(self):
        """Find and fix conflicts"""
        import glob

        py_files = [Path(f) for f in glob.glob("**/*.py", recursive=True)][:50]
        conflicts = self.solver.find_code_conflicts(py_files)

        print(f"\nFound {len(conflicts)} conflicts")
        for conflict in conflicts:
            print(f"  - {conflict['type']}: {conflict['name']}")

    def show_auth_status(self):
        """Show authentication status"""
        status = self.auth.get_status()
        print("\n" + json.dumps(status, indent=2))

    def authenticate(self):
        """Authenticate"""
        username = input("Username: ")
        password = input("Password: ")

        success, session = self.auth.authenticate(username, password)

        if success:
            print(f"\n✓ Authenticated as {session['username']} ({session['role']})")
        else:
            print(f"\n✗ Authentication failed: {session.get('error')}")


async def main():
    """Main entry point"""
    setup = GateSetup()

    if len(sys.argv) > 1 and sys.argv[1] == "--wizard":
        await setup.setup_wizard()
    else:
        setup.control_menu()


if __name__ == "__main__":
    asyncio.run(main())
