"""
Intelligent Security Remediation System
Quarantines actual threats while preserving legitimate operations
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set


class IntelligentRemediator:
    """Smart remediation that distinguishes real threats from false positives"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.quarantine_dir = self.project_root / "SECURITY_QUARANTINE"
        self.safe_dir = self.project_root / "SAFE_VERSIONS"
        self.report_file = self.project_root / "SECURITY_FORENSIC_REPORT_20260119_010442.json"

        # Create directories
        self.quarantine_dir.mkdir(exist_ok=True)
        self.safe_dir.mkdir(exist_ok=True)

        # Known safe patterns
        self.safe_patterns = {
            "sys.exit": ['if __name__ == "__main__"', "except", "KeyboardInterrupt"],
            "subprocess.run": [
                "pip install",
                "choco install",
                "brew install",
                "apt install",
                "mvn",
                "gradle",
                "java -version",
                "python",
            ],
            "requests.post": ["api.x.ai", "api.openai.com", "api.anthropic.com"],
            "requests.get": ["api.", "freesound.org", "github.com"],
        }

        # Actual dangerous patterns
        self.dangerous_patterns = {
            "shutdown": ["-s", "-r", "-f"],
            "delete": ["rm -rf /", "del /f /q /s", "rmdir /s /q"],
            "format": ["format c:", "mkfs."],
            "malicious_urls": ["pastebin.com", "bit.ly", "suspicious"],
        }

    def load_scan_results(self) -> Dict:
        """Load forensic scan results"""
        if not self.report_file.exists():
            print("[ERROR] Scan report not found. Run omega_forensic_security.py first.")
            return {}

        with open(self.report_file, "r") as f:
            return json.load(f)

    def is_false_positive(self, threat: Dict, file_content: str) -> bool:
        """Determine if a threat is a false positive"""
        threat_type = threat.get("type", "")
        function = threat.get("function", "")
        context = threat.get("context", "")

        # Check sys.exit - usually safe in __main__ or error handlers
        if "exit" in function.lower():
            if any(safe in context for safe in self.safe_patterns["sys.exit"]):
                return True

        # Check subprocess.run - safe if using package managers
        if "subprocess" in function:
            if any(safe in context for safe in self.safe_patterns["subprocess.run"]):
                return True

        # Check requests - safe if calling known APIs
        if "requests" in function:
            if threat_type == "DANGEROUS_FUNCTION":
                matched = threat.get("matched", "")
                if any(
                    safe in context
                    for safe in self.safe_patterns["requests.post"]
                    + self.safe_patterns["requests.get"]
                ):
                    return True

        # Network bind() - check if it's Tkinter (GUI) not socket (network)
        if threat_type == "NETWORK_ACTIVITY":
            matched = threat.get("matched", "")
            if "bind(" in matched and (
                "Button" in context or "widget" in context.lower() or "tkinter" in context.lower()
            ):
                return True

        return False

    def is_real_threat(self, threat: Dict, file_content: str) -> bool:
        """Identify actual security threats"""
        context = threat.get("context", "").lower()

        # Check for actual dangerous patterns
        for pattern_type, patterns in self.dangerous_patterns.items():
            if any(danger in context for danger in patterns):
                return True

        # Check for encoded/obfuscated malicious code
        if "EVAL_ENCODED" in threat.get("type", ""):
            return True

        # Check for actual shutdown commands
        if "SHUTDOWN_PATTERN" in threat.get("type", ""):
            return True

        # Check for time bombs with destructive actions
        if "TIME_BOMB" in threat.get("type", ""):
            if any(danger in context for danger in ["shutdown", "delete", "remove", "format"]):
                return True

        return False

    def analyze_file(self, file_result: Dict) -> Dict:
        """Analyze a single file for real threats"""
        file_path = Path(file_result["file"])

        if not file_path.exists():
            return {"status": "missing", "action": "skip"}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            return {"status": "unreadable", "action": "skip"}

        real_threats = []
        false_positives = []

        for threat in file_result.get("threats", []):
            if self.is_real_threat(threat, content):
                real_threats.append(threat)
            elif self.is_false_positive(threat, content):
                false_positives.append(threat)
            else:
                # Unknown - mark for manual review
                threat["review_needed"] = True
                real_threats.append(threat)

        analysis = {
            "file": str(file_path),
            "real_threats": real_threats,
            "false_positives": false_positives,
            "status": "safe" if not real_threats else "threat",
            "action": "keep" if not real_threats else "quarantine",
        }

        return analysis

    def create_safe_version(self, file_path: Path, threats: List[Dict]) -> bool:
        """Create a safe version of a file with threats removed"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Track modified lines
            modified_lines = set()

            for threat in threats:
                line_num = threat.get("line", 0)
                if 0 < line_num <= len(lines):
                    modified_lines.add(line_num - 1)
                    # Comment out the threat
                    original = lines[line_num - 1]
                    lines[line_num - 1] = f"# SECURITY-DISABLED: {original}"

            # Save safe version
            safe_file = self.safe_dir / file_path.name
            with open(safe_file, "w", encoding="utf-8") as f:
                f.writelines(lines)

            # Create a report
            report = {
                "original_file": str(file_path),
                "safe_version": str(safe_file),
                "modified_lines": sorted(modified_lines),
                "threats_disabled": len(threats),
                "timestamp": datetime.now().isoformat(),
            }

            report_file = safe_file.with_suffix(".json")
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)

            return True

        except Exception as e:
            print(f"[ERROR] Failed to create safe version: {e}")
            return False

    def quarantine_file(self, file_path: Path, analysis: Dict) -> bool:
        """Move a file to quarantine with analysis report"""
        try:
            # Copy file to quarantine
            dest = self.quarantine_dir / file_path.name
            shutil.copy2(file_path, dest)

            # Save analysis report
            report_file = dest.with_suffix(".analysis.json")
            with open(report_file, "w") as f:
                json.dump(analysis, f, indent=2)

            print(f"[+] Quarantined: {file_path.name}")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to quarantine {file_path.name}: {e}")
            return False

    def run_remediation(self):
        """Execute intelligent remediation"""
        print("=" * 80)
        print("INTELLIGENT SECURITY REMEDIATION")
        print("=" * 80)
        print()

        # Load scan results
        results = self.load_scan_results()
        if not results:
            return

        print(f"[*] Analyzing {len(results.get('files_scanned', []))} files...")
        print()

        stats = {
            "total_files": 0,
            "files_with_threats": 0,
            "false_positives": 0,
            "real_threats": 0,
            "files_quarantined": 0,
            "safe_versions_created": 0,
        }

        files_needing_review = []
        files_to_quarantine = []

        # Analyze each high-risk file
        for file_result in results.get("high_risk_files", []):
            stats["total_files"] += 1

            analysis = self.analyze_file(file_result)

            if analysis["status"] == "threat":
                stats["files_with_threats"] += 1
                stats["real_threats"] += len(analysis["real_threats"])

                # Check if manual review needed
                if any(t.get("review_needed") for t in analysis["real_threats"]):
                    files_needing_review.append(analysis)
                else:
                    files_to_quarantine.append(analysis)

            stats["false_positives"] += len(analysis.get("false_positives", []))

        # Display results
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print()
        print(f"📊 Total Files Analyzed: {stats['total_files']}")
        print(f"✅ False Positives (Safe): {stats['false_positives']}")
        print(f"⚠️  Potential Threats: {stats['real_threats']}")
        print(f"📋 Files Needing Review: {len(files_needing_review)}")
        print(f"🔒 Files To Quarantine: {len(files_to_quarantine)}")
        print()

        # Take action
        if files_to_quarantine:
            print("=" * 80)
            print("QUARANTINE RECOMMENDATIONS")
            print("=" * 80)
            print()

            for analysis in files_to_quarantine:
                file_path = Path(analysis["file"])
                print(f"⚠️  {file_path.name}")
                print(f"   Real Threats: {len(analysis['real_threats'])}")
                for threat in analysis["real_threats"][:3]:
                    print(f"   - Line {threat.get('line')}: {threat.get('type')}")
                print()

            choice = input("Quarantine these files? (y/n): ").strip().lower()

            if choice == "y":
                for analysis in files_to_quarantine:
                    file_path = Path(analysis["file"])
                    if self.quarantine_file(file_path, analysis):
                        stats["files_quarantined"] += 1

                    if self.create_safe_version(file_path, analysis["real_threats"]):
                        stats["safe_versions_created"] += 1

        # Manual review recommendations
        if files_needing_review:
            print()
            print("=" * 80)
            print("⚠️  MANUAL REVIEW REQUIRED")
            print("=" * 80)
            print()

            for analysis in files_needing_review:
                file_path = Path(analysis["file"])
                print(f"📋 {file_path.name}")
                print(f"   Location: {file_path}")
                print(
                    f"   Uncertain Threats: {len([t for t in analysis['real_threats'] if t.get('review_needed')])}"
                )
                print()

        # Final summary
        print()
        print("=" * 80)
        print("REMEDIATION SUMMARY")
        print("=" * 80)
        print()
        print(f"✅ Files Quarantined: {stats['files_quarantined']}")
        print(f"✅ Safe Versions Created: {stats['safe_versions_created']}")
        print(f"⚠️  Files Needing Review: {len(files_needing_review)}")
        print()

        if stats["files_quarantined"] == 0 and len(files_needing_review) == 0:
            print("✅ NO REAL THREATS DETECTED")
            print("✅ ALL HIGH-RISK DETECTIONS WERE FALSE POSITIVES")
            print("✅ SYSTEM IS SECURE")
        elif len(files_needing_review) > 0:
            print("⚠️  SOME FILES NEED MANUAL REVIEW")
            print("📋 Check the files listed above")
        else:
            print("✅ THREATS HAVE BEEN QUARANTINED")
            print("✅ SAFE VERSIONS CREATED")

        print()
        print("=" * 80)

        # Save final report
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "files_quarantined": [a["file"] for a in files_to_quarantine],
            "files_needing_review": [a["file"] for a in files_needing_review],
        }

        report_file = (
            self.project_root
            / f"REMEDIATION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"[+] Remediation report saved: {report_file.name}")
        print()


def main():
    """Main execution"""
    remediator = IntelligentRemediator()
    remediator.run_remediation()


if __name__ == "__main__":
    main()
