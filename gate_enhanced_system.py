"""
GATE Enhanced System - Screenshot, OCR, and Source Control Integration
Provides screenshot capture, passcode extraction, and GitHub issue management
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import subprocess
import warnings

warnings.filterwarnings("ignore")

# Check for required packages
try:
    from PIL import ImageGrab, Image
    import pytesseract
    import pyautogui
except ImportError as e:
    print(f"[!] Missing package: {e}")
    print("[*] Installing required packages...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pillow", "pytesseract", "pyautogui"])
    from PIL import ImageGrab, Image
    import pytesseract
    import pyautogui


class GateScreenshotSystem:
    """
    GATE Screenshot and OCR System
    Captures screenshots and extracts text (including passcodes)
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.screenshots_dir = self.project_root / "gate_screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        self.ocr_available = self._check_tesseract()

    def _check_tesseract(self) -> bool:
        """Check if Tesseract OCR is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            # Try common Windows installation path
            tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if Path(tesseract_path).exists():
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                return True
            print(
                "[!] Tesseract OCR not found. Install from: https://github.com/UB-Mannheim/tesseract/wiki"
            )
            return False

    def capture_full_screen(self) -> Tuple[bool, str, Optional[str]]:
        """Capture full screen screenshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gate_screenshot_{timestamp}.png"
            filepath = self.screenshots_dir / filename

            # Capture screenshot
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)

            print(f"[+] Screenshot saved: {filename}")
            return True, str(filepath), filename

        except Exception as e:
            print(f"[!] Error capturing screenshot: {e}")
            return False, "", None

    def capture_region(
        self, x: int, y: int, width: int, height: int
    ) -> Tuple[bool, str, Optional[str]]:
        """Capture specific region of screen"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gate_region_{timestamp}.png"
            filepath = self.screenshots_dir / filename

            # Capture region
            screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            screenshot.save(filepath)

            print(f"[+] Region screenshot saved: {filename}")
            return True, str(filepath), filename

        except Exception as e:
            print(f"[!] Error capturing region: {e}")
            return False, "", None

    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image using OCR"""
        if not self.ocr_available:
            print("[!] OCR not available")
            return None

        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"[!] Error extracting text: {e}")
            return None

    def extract_passcodes(self, text: str) -> List[str]:
        """Extract potential passcodes from text"""
        import re

        passcodes = []

        # Common passcode patterns
        patterns = [
            r"\b\d{6}\b",  # 6-digit codes
            r"\b\d{4}\b",  # 4-digit codes
            r"\b[A-Z0-9]{6}\b",  # 6-character alphanumeric
            r"\b[A-Z0-9]{8}\b",  # 8-character alphanumeric
            r"(?:code|passcode|verification|2fa|mfa)[\s:]+([A-Z0-9]{4,8})",  # Labeled codes
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            passcodes.extend(matches)

        # Remove duplicates and sort by length (longer codes first)
        passcodes = list(set(passcodes))
        passcodes.sort(key=len, reverse=True)

        return passcodes

    def capture_and_extract_passcode(self) -> Dict:
        """Capture screenshot and extract passcode"""
        print("\n[*] Capturing screenshot in 3 seconds...")
        print("[*] Switch to the window with the passcode...")

        import time

        time.sleep(3)

        success, filepath, filename = self.capture_full_screen()

        if not success:
            return {"success": False, "error": "Screenshot capture failed"}

        # Extract text
        text = self.extract_text_from_image(filepath)

        if not text:
            return {
                "success": True,
                "screenshot": filepath,
                "text": None,
                "passcodes": [],
                "message": "Screenshot saved but OCR not available",
            }

        # Extract passcodes
        passcodes = self.extract_passcodes(text)

        result = {
            "success": True,
            "screenshot": filepath,
            "text": text,
            "passcodes": passcodes,
            "message": f"Found {len(passcodes)} potential passcode(s)",
        }

        # Save result
        result_file = self.screenshots_dir / f"{filename.replace('.png', '_result.json')}"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        return result

    def interactive_capture(self):
        """Interactive screenshot capture with region selection"""
        print("\n" + "=" * 60)
        print("GATE INTERACTIVE SCREENSHOT CAPTURE")
        print("=" * 60)
        print("\n1. Full screen")
        print("2. Select region (coming soon)")
        print("3. Timed capture (3 seconds)")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            success, filepath, filename = self.capture_full_screen()
            if success:
                print(f"\n[+] Screenshot saved: {filepath}")
        elif choice == "3":
            result = self.capture_and_extract_passcode()
            print(f"\n{json.dumps(result, indent=2)}")
        else:
            print("[!] Invalid option")


class GateGitHubIntegration:
    """
    GATE GitHub Integration
    Manages GitHub issues and source control
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.credentials = self._load_credentials()
        self.github_available = self._check_github_cli()

    def _load_credentials(self) -> Dict[str, str]:
        """Load GitHub credentials from .env"""
        credentials = {}
        env_file = self.project_root / ".env"

        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    if "GITHUB_TOKEN" in line or "GITHUB_USERNAME" in line:
                        key, value = line.strip().split("=", 1)
                        if value and value != "your_github_token_here":
                            credentials[key] = value

        return credentials

    def _check_github_cli(self) -> bool:
        """Check if GitHub CLI is available"""
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def list_issues(self, state: str = "open") -> List[Dict]:
        """List GitHub issues"""
        issues = []

        if not self.github_available:
            print("[!] GitHub CLI not available. Install: winget install GitHub.cli")
            return issues

        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "list",
                    "--state",
                    state,
                    "--json",
                    "number,title,state,labels,updatedAt",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                issues = json.loads(result.stdout)
            else:
                print(f"[!] Error listing issues: {result.stderr}")

        except Exception as e:
            print(f"[!] Error: {e}")

        return issues

    def get_issue_details(self, issue_number: int) -> Optional[Dict]:
        """Get detailed information about an issue"""
        if not self.github_available:
            return None

        try:
            result = subprocess.run(
                [
                    "gh",
                    "issue",
                    "view",
                    str(issue_number),
                    "--json",
                    "number,title,body,state,labels,comments",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                print(f"[!] Error getting issue: {result.stderr}")
                return None

        except Exception as e:
            print(f"[!] Error: {e}")
            return None

    def close_issue(self, issue_number: int, comment: str = "Resolved by GATE") -> bool:
        """Close a GitHub issue"""
        if not self.github_available:
            print("[!] GitHub CLI not available")
            return False

        try:
            # Add comment
            subprocess.run(
                ["gh", "issue", "comment", str(issue_number), "--body", comment],
                capture_output=True,
                timeout=30,
            )

            # Close issue
            result = subprocess.run(
                ["gh", "issue", "close", str(issue_number)],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                print(f"[+] Issue #{issue_number} closed")
                return True
            else:
                print(f"[!] Error closing issue: {result.stderr}")
                return False

        except Exception as e:
            print(f"[!] Error: {e}")
            return False

    def auto_clear_resolved_issues(self) -> Dict:
        """Automatically clear issues that are marked as resolved"""
        print("\n[*] Scanning for resolved issues...")

        issues = self.list_issues(state="open")
        resolved_issues = []

        for issue in issues:
            title = issue.get("title", "").lower()
            labels = [label.get("name", "").lower() for label in issue.get("labels", [])]

            # Check if issue is marked as resolved
            if "resolved" in title or "fixed" in title or "resolved" in labels or "fixed" in labels:
                resolved_issues.append(issue)

        print(f"[+] Found {len(resolved_issues)} resolved issue(s)")

        results = {"total_found": len(resolved_issues), "closed": [], "failed": []}

        for issue in resolved_issues:
            issue_num = issue["number"]
            print(f"[*] Closing issue #{issue_num}: {issue['title']}")

            if self.close_issue(issue_num, "Automatically closed by GATE - marked as resolved"):
                results["closed"].append(issue_num)
            else:
                results["failed"].append(issue_num)

        return results

    def display_pending_issues(self):
        """Display pending issues in readable format"""
        print("\n" + "=" * 70)
        print("GITHUB PENDING ISSUES")
        print("=" * 70)

        issues = self.list_issues(state="open")

        if not issues:
            print("\n✅ No pending issues!")
            return

        for issue in issues:
            print(f"\n#{issue['number']}: {issue['title']}")
            print(f"  State: {issue['state']}")

            labels = issue.get("labels", [])
            if labels:
                label_names = [label["name"] for label in labels]
                print(f"  Labels: {', '.join(label_names)}")

            updated = issue.get("updatedAt", "")
            print(f"  Updated: {updated}")

        print("\n" + "=" * 70)
        print(f"Total: {len(issues)} issue(s)")
        print("=" * 70)


class GateEnhancedSystem:
    """
    Enhanced GATE system with screenshot and GitHub capabilities
    """

    def __init__(self):
        self.screenshot_system = GateScreenshotSystem()
        self.github_integration = GateGitHubIntegration()

    def capture_passcode_from_email(self) -> Dict:
        """Capture and extract passcode from email screenshot"""
        print("\n" + "=" * 70)
        print("GATE PASSCODE CAPTURE SYSTEM")
        print("=" * 70)
        print("\nInstructions:")
        print("1. Open your email with the passcode")
        print("2. Make sure the passcode is visible on screen")
        print("3. Press Enter when ready...")

        input()

        return self.screenshot_system.capture_and_extract_passcode()

    def manage_source_control_issues(self):
        """Manage GitHub source control issues"""
        print("\n" + "=" * 70)
        print("GATE SOURCE CONTROL MANAGER")
        print("=" * 70)

        # Display pending issues
        self.github_integration.display_pending_issues()

        print("\nOptions:")
        print("1. Auto-clear resolved issues")
        print("2. View issue details")
        print("3. Manually close issue")
        print("4. Exit")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            results = self.github_integration.auto_clear_resolved_issues()
            print(f"\n[+] Closed {len(results['closed'])} issue(s)")
            if results["failed"]:
                print(f"[!] Failed to close {len(results['failed'])} issue(s)")

        elif choice == "2":
            issue_num = input("Enter issue number: ").strip()
            if issue_num.isdigit():
                details = self.github_integration.get_issue_details(int(issue_num))
                if details:
                    print(f"\n{json.dumps(details, indent=2)}")

        elif choice == "3":
            issue_num = input("Enter issue number: ").strip()
            if issue_num.isdigit():
                comment = input("Enter closing comment (optional): ").strip() or "Closed by GATE"
                self.github_integration.close_issue(int(issue_num), comment)

    def launch_interactive_menu(self):
        """Launch interactive menu"""
        while True:
            print("\n" + "=" * 70)
            print("GATE ENHANCED SYSTEM")
            print("=" * 70)
            print("\n1. Capture passcode from email")
            print("2. Take screenshot")
            print("3. Manage GitHub issues")
            print("4. Auto-clear resolved issues")
            print("5. View pending issues")
            print("6. Exit")

            choice = input("\nSelect option (1-6): ").strip()

            if choice == "1":
                result = self.capture_passcode_from_email()
                if result.get("passcodes"):
                    print(f"\n[+] Extracted passcodes:")
                    for code in result["passcodes"]:
                        print(f"    {code}")

            elif choice == "2":
                self.screenshot_system.interactive_capture()

            elif choice == "3":
                self.manage_source_control_issues()

            elif choice == "4":
                results = self.github_integration.auto_clear_resolved_issues()
                print(f"\n[+] Closed {len(results['closed'])} issue(s)")

            elif choice == "5":
                self.github_integration.display_pending_issues()

            elif choice == "6":
                print("\n[*] Exiting GATE Enhanced System")
                break

            else:
                print("[!] Invalid option")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="GATE Enhanced System")
    parser.add_argument("--screenshot", action="store_true", help="Capture screenshot")
    parser.add_argument("--passcode", action="store_true", help="Capture and extract passcode")
    parser.add_argument("--issues", action="store_true", help="View GitHub issues")
    parser.add_argument("--clear-issues", action="store_true", help="Auto-clear resolved issues")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive menu")

    args = parser.parse_args()

    gate = GateEnhancedSystem()

    if args.screenshot:
        gate.screenshot_system.capture_full_screen()
    elif args.passcode:
        result = gate.capture_passcode_from_email()
        print(json.dumps(result, indent=2))
    elif args.issues:
        gate.github_integration.display_pending_issues()
    elif args.clear_issues:
        results = gate.github_integration.auto_clear_resolved_issues()
        print(f"Closed: {results['closed']}")
    elif args.interactive:
        gate.launch_interactive_menu()
    else:
        # Default: interactive menu
        gate.launch_interactive_menu()


if __name__ == "__main__":
    main()
