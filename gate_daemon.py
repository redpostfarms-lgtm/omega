#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE Continuous Monitoring Daemon
Runs 24/7 to patrol, detect, and resolve issues automatically
"""

import asyncio
import json
import os
import signal
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

try:
    from gate_autonomous_admin import GateAutonomousAdmin
    from gate_problem_solver import GateProblemSolver
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure gate_autonomous_admin.py and gate_problem_solver.py exist")
    sys.exit(1)


class GateDaemon:
    """
    GATE Continuous Monitoring Daemon
    Combines autonomous admin and problem solver for 24/7 operation
    """

    def __init__(self):
        self.root = Path(__file__).parent
        self.admin = GateAutonomousAdmin(self.root)
        self.solver = GateProblemSolver(self.root)

        self.running = False
        self.patrol_count = 0

        # Configuration
        self.patrol_interval = 300  # 5 minutes
        self.auto_commit = True
        self.auto_fix = True

        # Status file
        self.status_file = self.root / "data" / "gate_daemon_status.json"
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Centralized logging"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}"
        print(log_line)

        # Also log to daemon log file
        log_file = self.root / "logs" / "gate_daemon.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_line + "\n")

    def save_status(self, status: Dict):
        """Save daemon status"""
        try:
            with open(self.status_file, "w") as f:
                json.dump(status, f, indent=2, default=str)
        except Exception as e:
            self.log(f"Error saving status: {e}", "ERROR")

    def load_status(self) -> Dict:
        """Load daemon status"""
        try:
            if self.status_file.exists():
                with open(self.status_file) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    async def patrol_cycle(self):
        """Single patrol cycle"""
        self.patrol_count += 1

        self.log("=" * 70)
        self.log(f"PATROL CYCLE #{self.patrol_count}")
        self.log("=" * 70)

        cycle_results = {
            "cycle_number": self.patrol_count,
            "timestamp": datetime.now().isoformat(),
            "problems_detected": 0,
            "problems_resolved": 0,
            "fixes_applied": 0,
            "commits_made": 0,
        }

        try:
            # 1. Run autonomous patrol
            self.log("\n[1/4] Running autonomous patrol...")
            problems = await self.admin.patrol_system()
            cycle_results["problems_detected"] = len(problems)

            # 2. Attempt resolutions
            if problems and self.auto_fix:
                self.log("\n[2/4] Resolving detected problems...")
                resolved, failed = await self.admin.resolve_problems(problems)
                cycle_results["problems_resolved"] = resolved

            # 3. Run comprehensive code fix
            if self.auto_fix:
                self.log("\n[3/4] Running comprehensive code fix...")
                fix_results = await self.solver.comprehensive_fix()
                cycle_results["fixes_applied"] = (
                    fix_results["syntax_fixes"]
                    + fix_results["import_optimizations"]
                    + fix_results["conflicts_resolved"]
                )

            # 4. Commit changes if any
            if self.auto_commit:
                self.log("\n[4/4] Committing changes...")
                git_status = self.admin.check_git_status()

                if git_status.get("uncommitted_changes"):
                    commit_msg = (
                        f"GATE Daemon Auto-maintenance - Cycle #{self.patrol_count}\n\n"
                    )
                    commit_msg += f"Problems detected: {cycle_results['problems_detected']}\n"
                    commit_msg += f"Problems resolved: {cycle_results['problems_resolved']}\n"
                    commit_msg += f"Code fixes applied: {cycle_results['fixes_applied']}\n"
                    commit_msg += f"\nTimestamp: {cycle_results['timestamp']}"

                    if self.admin.auto_commit_changes(commit_msg):
                        cycle_results["commits_made"] = 1
                        self.log("✓ Changes committed")

        except Exception as e:
            self.log(f"Error in patrol cycle: {e}", "ERROR")
            cycle_results["error"] = str(e)

        # Save cycle results
        self.save_status(
            {
                "daemon_status": "running",
                "last_patrol": cycle_results,
                "total_patrols": self.patrol_count,
                "uptime_seconds": (
                    datetime.now() - self.start_time
                ).total_seconds() if hasattr(self, "start_time") else 0,
            }
        )

        self.log("\n" + "=" * 70)
        self.log(f"Patrol cycle #{self.patrol_count} complete")
        self.log(f"  Problems detected: {cycle_results['problems_detected']}")
        self.log(f"  Problems resolved: {cycle_results['problems_resolved']}")
        self.log(f"  Fixes applied: {cycle_results['fixes_applied']}")
        self.log(f"  Commits made: {cycle_results['commits_made']}")
        self.log("=" * 70)

        return cycle_results

    async def run(self):
        """Run continuous monitoring daemon"""
        self.running = True
        self.start_time = datetime.now()

        self.log("=" * 70)
        self.log("GATE DAEMON - STARTING")
        self.log("=" * 70)
        self.log(f"Patrol interval: {self.patrol_interval} seconds")
        self.log(f"Auto-commit: {self.auto_commit}")
        self.log(f"Auto-fix: {self.auto_fix}")
        self.log("=" * 70)

        # Set up Git
        self.admin.setup_git_config()

        try:
            while self.running:
                # Run patrol cycle
                await self.patrol_cycle()

                # Wait for next cycle
                self.log(f"\nNext patrol in {self.patrol_interval} seconds...\n")
                await asyncio.sleep(self.patrol_interval)

        except KeyboardInterrupt:
            self.log("\n\nDaemon stopped by user (Ctrl+C)")
        except Exception as e:
            self.log(f"\n\nDaemon error: {e}", "ERROR")
            raise
        finally:
            self.running = False
            self.save_status(
                {
                    "daemon_status": "stopped",
                    "total_patrols": self.patrol_count,
                    "stopped_at": datetime.now().isoformat(),
                }
            )
            self.log("GATE Daemon stopped")

    def stop(self):
        """Stop daemon gracefully"""
        self.log("Stopping daemon...")
        self.running = False


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n\nReceived shutdown signal, stopping daemon...")
    sys.exit(0)


async def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    daemon = GateDaemon()

    print("\n" + "=" * 70)
    print("  GATE CONTINUOUS MONITORING DAEMON")
    print("=" * 70)
    print("\nThis daemon will:")
    print("  • Patrol the system every 5 minutes")
    print("  • Detect and resolve problems automatically")
    print("  • Fix code issues and conflicts")
    print("  • Commit changes with detailed messages")
    print("\nPress Ctrl+C to stop")
    print("=" * 70 + "\n")

    input("Press Enter to start daemon... ")

    await daemon.run()


if __name__ == "__main__":
    asyncio.run(main())
