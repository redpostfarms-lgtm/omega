"""
Omega Auto-Sync - Git Batch Wrapper
Every pending change gets auto-wrapped in one git batch.
One command, five lines: add, commit, push.
No red squiggles. No merge hell. No 404 ghosts.
Queen says 'push,' swarm breathes.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import json


class AutoSync:
    """Automatic git synchronization wrapper"""

    def __init__(self, git_root: Optional[Path] = None):
        self.git_root = git_root or Path(__file__).parent
        self.branch = self.get_current_branch()

    def get_current_branch(self) -> str:
        """Get current git branch"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.git_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"

    def git_status(self) -> Dict[str, Any]:
        """Get git status as JSON"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.git_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            status_lines = result.stdout.strip().split('\n')
            modified: List[str] = []
            untracked: List[str] = []
            
            for line in status_lines:
                if not line:
                    continue
                status_code = line[:2]
                filename = line[3:]
                
                if status_code.strip() == 'M' or status_code.strip().startswith('M'):
                    modified.append(filename)
                elif status_code.strip() == '??':
                    untracked.append(filename)
                elif status_code.strip() in ['A', 'AM']:
                    modified.append(filename)
            
            return {
                "branch": self.branch,
                "modified": modified,
                "untracked": untracked,
                "clean": len(modified) == 0 and len(untracked) == 0,
                "total_changes": len(modified) + len(untracked)
            }
        except subprocess.CalledProcessError as e:
            return {"error": str(e)}

    def sync(self, reason: Optional[str] = None, force: bool = False, files: Optional[List[str]] = None) -> bool:
        """
        Sync all changes in one git batch
        
        Args:
            reason: Reason for sync (appears in commit message)
            force: Force sync even if no changes detected
            files: Specific files to sync (None = all files)
        
        Returns:
            True if sync successful, False otherwise
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reason = reason or "manual sync"
        
        print(f"  AUTO-SYNC: {reason}")
        print(f"  Branch: {self.branch}")
        print(f"  Time: {timestamp}")
        print()

        try:
            status = self.git_status()
            if status.get("clean") and not force:
                print("  [OK] No changes to sync - branch already clean")
                return True

            if files:
                for file in files:
                    subprocess.run(
                        ["git", "add", file],
                        cwd=self.git_root,
                        check=True,
                        capture_output=True
                    )
                print(f"  [1/5] git add {' '.join(files)}")
            else:
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=self.git_root,
                    check=True,
                    capture_output=True
                )
                print("  [1/5] git add -A")

            commit_msg = f"sync: swarm healed - {reason}"
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.git_root,
                check=True,
                capture_output=True
            )
            print(f"  [2/5] git commit -m \"{commit_msg}\"")

            subprocess.run(
                ["git", "push", "origin", self.branch],
                cwd=self.git_root,
                check=True,
                capture_output=True,
                timeout=60
            )
            print(f"  [3/5] git push origin {self.branch}")

            print()
            print("  [OK] Swarm breathes - branch clean")
            print(f"  No red squiggles. No merge hell. No 404 ghosts.")
            return True

        except subprocess.TimeoutExpired:
            print()
            print("  [FAIL] Git push timeout (60s)")
            return False
        except subprocess.CalledProcessError as e:
            print()
            print(f"  [FAIL] Git operation failed: {e}")
            if e.stderr:
                print(f"  Error: {e.stderr.decode()}")
            return False

    def status_json(self) -> str:
        """Get status as JSON string"""
        status = self.git_status()
        return json.dumps(status, indent=2)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Omega Auto-Sync - Git Batch Wrapper")
    parser.add_argument("command", choices=["sync", "status"], help="Command to execute")
    parser.add_argument("-r", "--reason", default="manual sync", help="Reason for sync")
    parser.add_argument("-f", "--force", action="store_true", help="Force sync even if no changes")
    parser.add_argument("files", nargs="*", help="Specific files to sync (default: all)")

    args = parser.parse_args()

    syncer = AutoSync()

    if args.command == "status":
        print(syncer.status_json())
        return 0

    elif args.command == "sync":
        files = args.files if args.files else None
        success = syncer.sync(args.reason, args.force, files)
        return 0 if success else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
