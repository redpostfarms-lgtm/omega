#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE MASTER SETUP
Complete setup: LLM, IDE, Dependencies, Memory, and Integration
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")


class GateMasterSetup:
    """Complete GATE system setup"""

    def __init__(self):
        self.root = Path(__file__).parent
        self.setup_log = self.root / "logs" / "gate_setup.log"
        self.setup_log.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Log setup message"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}"
        print(log_line)

        with open(self.setup_log, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

    def print_banner(self):
        """Print setup banner"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  GATE MASTER SETUP - COMPLETE SYSTEM CONFIGURATION".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70 + "\n")

    def run_script(self, script_name: str, *args) -> bool:
        """Run a setup script"""
        try:
            cmd = [sys.executable, str(self.root / script_name)] + list(args)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            return result.returncode == 0
        except Exception as e:
            self.log(f"Error running {script_name}: {e}")
            return False

    async def full_setup(self):
        """Run complete setup"""
        self.print_banner()

        self.log("=" * 70)
        self.log("GATE MASTER SETUP - Starting")
        self.log("=" * 70)

        # Step 1: Administrator Authentication
        self.log("\n[Step 1/7] Setting up Administrator Authentication...")
        print("\n[Step 1/7] Administrator Authentication")
        print("-" * 70)

        try:
            from gate_admin_auth import GateAdminAuth

            auth = GateAdminAuth()
            status = auth.get_status()

            if status["admin_configured"]:
                print("✓ Administrator already configured")
                self.log("Administrator already configured")
            else:
                print("Setting up GATE administrator...")
                result = auth.setup_admin()
                print(f"✓ {result['message']}")

                if "password" in result:
                    print("\n" + "=" * 70)
                    print("GATE ADMINISTRATOR CREDENTIALS")
                    print("=" * 70)
                    print(f"Username: {result['username']}")
                    print(f"Password: {result['password']}")
                    print("=" * 70)
                    print("\n⚠️  SAVE THIS PASSWORD! It cannot be recovered.")
                    print("=" * 70 + "\n")

                    self.log(f"Administrator created: {result['username']}")

                input("Press Enter after saving credentials...")

        except Exception as e:
            self.log(f"Error in Step 1: {e}")
            print(f"✗ Error: {e}")

        # Step 2: Directory Structure
        self.log("\n[Step 2/7] Creating Directory Structure...")
        print("\n[Step 2/7] Directory Structure")
        print("-" * 70)

        try:
            success = self.run_script("analyze_standalone_requirements.py")
            if success:
                print("✓ All directories created")
                self.log("Directory structure complete")
            else:
                print("⚠  Some directories may not be created")
        except Exception as e:
            self.log(f"Error in Step 2: {e}")

        # Step 3: Dependencies Installation
        self.log("\n[Step 3/7] Installing Dependencies...")
        print("\n[Step 3/7] Dependencies Installation")
        print("-" * 70)
        print("\nOptions:")
        print("  1. Install REQUIRED dependencies only (faster)")
        print("  2. Install ALL dependencies (recommended, takes longer)")
        print("  3. Skip dependency installation")

        choice = input("\nChoice (1-3): ").strip()

        if choice == "1":
            print("\nInstalling REQUIRED dependencies...")
            self.run_script("gate_comprehensive_installer.py", "--required")
        elif choice == "2":
            print("\nInstalling ALL dependencies (this will take a while)...")
            self.run_script("gate_comprehensive_installer.py", "--all")
        else:
            print("Skipping dependency installation")

        # Step 4: IDE Integration
        self.log("\n[Step 4/7] Setting up IDE Integration...")
        print("\n[Step 4/7] IDE Integration")
        print("-" * 70)

        try:
            from gate_ide_integration import GateIDEIntegration

            ide = GateIDEIntegration()
            ide.setup_all()
            self.log("IDE integration complete")

        except Exception as e:
            self.log(f"Error in Step 4: {e}")
            print(f"✗ Error: {e}")

        # Step 5: LLM Integration
        self.log("\n[Step 5/7] Configuring LLM Integration...")
        print("\n[Step 5/7] LLM Integration")
        print("-" * 70)

        try:
            from gate_llm_integration import GateLLMIntegration

            llm = GateLLMIntegration()
            llm.save_config()
            llm.save_memory()

            print("✓ LLM integration configured")
            print(f"  Config: {llm.config_file}")
            print(f"  Memory: {llm.memory_file}")

            self.log("LLM integration complete")

        except Exception as e:
            self.log(f"Error in Step 5: {e}")
            print(f"✗ Error: {e}")

        # Step 6: Git Configuration
        self.log("\n[Step 6/7] Configuring Git...")
        print("\n[Step 6/7] Git Configuration")
        print("-" * 70)

        try:
            from gate_autonomous_admin import GateAutonomousAdmin

            admin = GateAutonomousAdmin()
            admin.setup_git_config()

            print("✓ Git configured for GATE")
            self.log("Git configuration complete")

        except Exception as e:
            self.log(f"Error in Step 6: {e}")
            print(f"✗ Error: {e}")

        # Step 7: Initial System Patrol
        self.log("\n[Step 7/7] Running Initial System Patrol...")
        print("\n[Step 7/7] Initial System Patrol")
        print("-" * 70)

        try:
            from gate_autonomous_admin import GateAutonomousAdmin

            admin = GateAutonomousAdmin()
            problems = await admin.patrol_system()

            print(f"\nFound {len(problems)} issues")

            if problems and len(problems) > 0:
                print("\nTop issues:")
                for i, problem in enumerate(problems[:5], 1):
                    print(f"  {i}. [{problem['severity']}] {problem['description']}")

                fix_now = input("\nFix these issues now? (y/n): ").strip().lower()
                if fix_now == "y":
                    resolved, failed = await admin.resolve_problems(problems)
                    print(f"\n✓ Resolved {resolved} issues, {failed} failed")

                    # Commit fixes
                    if resolved > 0:
                        commit_msg = (
                            f"GATE Initial Setup: Fixed {resolved} issues\n\n"
                            f"Setup completed: {datetime.now().isoformat()}"
                        )
                        admin.auto_commit_changes(commit_msg)

            self.log(f"Initial patrol complete: {len(problems)} issues found")

        except Exception as e:
            self.log(f"Error in Step 7: {e}")
            print(f"✗ Error: {e}")

        # Final Summary
        print("\n" + "=" * 70)
        print("  GATE MASTER SETUP COMPLETE")
        print("=" * 70)

        print("\n✓ Setup Complete! GATE is ready for operation.\n")

        print("What's been configured:")
        print("  ✓ Administrator authentication")
        print("  ✓ Directory structure")
        print("  ✓ Dependencies (as selected)")
        print("  ✓ IDE integration (VS Code, PyCharm)")
        print("  ✓ LLM integration (all providers)")
        print("  ✓ Git configuration")
        print("  ✓ Initial system patrol")

        print("\nNext Steps:")
        print("  1. Start 24/7 daemon: python gate_daemon.py")
        print("  2. Control center: python setup_gate_admin.py")
        print("  3. Run tests: python run_comprehensive_tests.py")
        print("  4. View resources: python resource_controller.py status")

        print("\nKey Files:")
        print(f"  • Admin credentials: data/credentials/GATE_ADMIN_CREDENTIALS.txt")
        print(f"  • Setup log: {self.setup_log}")
        print(f"  • LLM config: config/llm_config.json")
        print(f"  • Memory: data/gate_memory.json")

        print("\n" + "=" * 70 + "\n")

        self.log("=" * 70)
        self.log("GATE MASTER SETUP - Complete")
        self.log("=" * 70)

        # Save setup completion status
        completion_status = {
            "setup_complete": True,
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "platform": sys.platform
        }

        status_file = self.root / "data" / "setup_complete.json"
        with open(status_file, "w") as f:
            json.dump(completion_status, f, indent=2)


async def main():
    """Main entry point"""
    setup = GateMasterSetup()
    await setup.full_setup()


if __name__ == "__main__":
    asyncio.run(main())
