"""
Omega Forensic Security Analyzer
Deep security scan for logic bombs, backdoors, and malicious code
Protects against hidden shutdown mechanisms and security threats
"""

import os
import sys
import ast
import re
import json
import base64
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from datetime import datetime
import subprocess


class ForensicSecurityAnalyzer:
    """Deep forensic analysis for security threats"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.threats_found = []
        self.suspicious_patterns = []
        self.safe_files = []

        # Dangerous function patterns
        self.dangerous_functions = [
            "os.system",
            "subprocess.call",
            "subprocess.run",
            "subprocess.Popen",
            "eval",
            "exec",
            "compile",
            "__import__",
            "os.remove",
            "os.rmdir",
            "shutil.rmtree",
            "sys.exit",
            "os._exit",
            "quit",
            "exit",
            "socket.socket",
            "urllib.request",
            "requests.get",
            "requests.post",
            "pickle.loads",
            "marshal.loads",
            "shelve.open",
        ]

        # Shutdown/destroy patterns
        self.shutdown_patterns = [
            r"shutdown\s*-[sr]",  # Windows/Linux shutdown
            r"rm\s+-rf\s+/",  # Recursive delete
            r"format\s+[c-z]:",  # Format drive
            r"del\s+/[fqsa]",  # Delete files
            r"rmdir\s+/[sq]",  # Remove directory
            r"wmic\s+.*\s+delete",  # WMIC deletion
            r"powershell\s+.*Remove-Item",  # PowerShell deletion
            r"os\.system.*shutdown",  # OS shutdown
            r"sys\.exit\(-1\)",  # Abnormal exit
        ]

        # Time bomb patterns
        self.time_bomb_patterns = [
            r"datetime\.now\(\)",
            r"time\.time\(\)",
            r"if.*datetime.*[<>]",  # Time-based conditionals
            r"if.*time\.time.*[<>]",
            r"trigger_date",
            r"expiry",
            r"deadline",
        ]

        # Obfuscation patterns
        self.obfuscation_patterns = [
            r"base64\.b64decode",
            r"codecs\.decode",
            r'\.decode\(["\'].*["\']\)',
            r"chr\(.*\)",  # Character encoding
            r"\\x[0-9a-f]{2}",  # Hex encoding
            r"eval\(.*decode",  # Eval with decode
        ]

        # Network/backdoor patterns
        self.network_patterns = [
            r"socket\.(AF_INET|SOCK_STREAM)",
            r"bind\(.*\)",
            r"listen\(.*\)",
            r"connect\(.*\)",
            r"http[s]?://(?!(?:localhost|127\.0\.0\.1|api\.))",  # External URLs
        ]

    def scan_file(self, file_path: Path) -> Dict:
        """Deep scan of single file"""
        print(f"[*] Scanning: {file_path.name}")

        result = {
            "file": str(file_path),
            "threats": [],
            "suspicious": [],
            "warnings": [],
            "risk_level": "SAFE",
        }

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # 1. Check for dangerous functions
            dangerous = self._check_dangerous_functions(content, file_path.name)
            if dangerous:
                result["threats"].extend(dangerous)

            # 2. Check for shutdown patterns
            shutdowns = self._check_shutdown_patterns(content)
            if shutdowns:
                result["threats"].extend(shutdowns)

            # 3. Check for time bombs
            time_bombs = self._check_time_bombs(content)
            if time_bombs:
                result["suspicious"].extend(time_bombs)

            # 4. Check for obfuscation
            obfuscated = self._check_obfuscation(content)
            if obfuscated:
                result["warnings"].extend(obfuscated)

            # 5. Check for network backdoors
            network = self._check_network_activity(content, file_path.name)
            if network:
                result["warnings"].extend(network)

            # 6. AST analysis for hidden logic
            ast_threats = self._ast_analysis(content, file_path.name)
            if ast_threats:
                result["threats"].extend(ast_threats)

            # 7. Check for hardcoded credentials
            credentials = self._check_hardcoded_credentials(content)
            if credentials:
                result["warnings"].extend(credentials)

            # Determine risk level
            if result["threats"]:
                result["risk_level"] = "HIGH"
            elif len(result["suspicious"]) > 3:
                result["risk_level"] = "MEDIUM"
            elif result["warnings"]:
                result["risk_level"] = "LOW"

        except Exception as e:
            result["error"] = str(e)
            result["risk_level"] = "UNKNOWN"

        return result

    def _check_dangerous_functions(self, content: str, filename: str) -> List[Dict]:
        """Check for dangerous function calls"""
        threats = []

        for func in self.dangerous_functions:
            pattern = re.escape(func) + r"\s*\("
            matches = list(re.finditer(pattern, content))

            if matches:
                # Check context - some uses are legitimate
                for match in matches:
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]

                    # Check if it's in a safe context
                    safe_context = False

                    # Legitimate uses
                    if filename in [
                        "omega_smart_integrator.py",
                        "omega_auto_integration_monitor.py",
                    ]:
                        if "subprocess.run" in func and "pip install" in context:
                            safe_context = True

                    if filename.startswith("omega_") and "subprocess" in func:
                        if any(
                            safe in context for safe in ["python", ".py", "pip", "check", "version"]
                        ):
                            safe_context = True

                    if not safe_context:
                        line_num = content[: match.start()].count("\n") + 1
                        threats.append(
                            {
                                "type": "DANGEROUS_FUNCTION",
                                "function": func,
                                "line": line_num,
                                "context": context.strip()[:200],
                            }
                        )

        return threats

    def _check_shutdown_patterns(self, content: str) -> List[Dict]:
        """Check for shutdown/destruction patterns"""
        threats = []

        for pattern in self.shutdown_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))

            if matches:
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]

                    threats.append(
                        {
                            "type": "SHUTDOWN_PATTERN",
                            "pattern": pattern,
                            "line": line_num,
                            "matched": match.group(),
                            "context": context.strip()[:200],
                        }
                    )

        return threats

    def _check_time_bombs(self, content: str) -> List[Dict]:
        """Check for time-based triggers"""
        suspicious = []

        # Look for time-based conditionals
        time_conditionals = re.finditer(
            r"if\s+.*(?:datetime|time).*(?:[<>]=?|==).*:", content, re.MULTILINE
        )

        for match in time_conditionals:
            line_num = content[: match.start()].count("\n") + 1

            # Check what happens after the condition
            start = match.end()
            end = min(len(content), start + 200)
            after_condition = content[start:end]

            # Look for dangerous actions after time check
            if any(
                danger in after_condition for danger in ["exit", "shutdown", "delete", "remove"]
            ):
                suspicious.append(
                    {
                        "type": "TIME_BOMB",
                        "line": line_num,
                        "condition": match.group().strip(),
                        "action": after_condition.strip()[:100],
                    }
                )

        return suspicious

    def _check_obfuscation(self, content: str) -> List[Dict]:
        """Check for code obfuscation"""
        warnings = []

        for pattern in self.obfuscation_patterns:
            matches = list(re.finditer(pattern, content))

            if matches:
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end]

                    warnings.append(
                        {
                            "type": "OBFUSCATION",
                            "pattern": pattern,
                            "line": line_num,
                            "context": context.strip()[:200],
                        }
                    )

        return warnings

    def _check_network_activity(self, content: str, filename: str) -> List[Dict]:
        """Check for network connections"""
        warnings = []

        # Skip known network files
        if filename in ["omega_web_researcher.py", "omega_api.py", "gate_enhanced_system.py"]:
            return warnings

        for pattern in self.network_patterns:
            matches = list(re.finditer(pattern, content))

            if matches:
                for match in matches:
                    line_num = content[: match.start()].count("\n") + 1
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end]

                    warnings.append(
                        {
                            "type": "NETWORK_ACTIVITY",
                            "pattern": pattern,
                            "line": line_num,
                            "matched": match.group(),
                            "context": context.strip()[:200],
                        }
                    )

        return warnings

    def _ast_analysis(self, content: str, filename: str) -> List[Dict]:
        """AST-based analysis for hidden logic"""
        threats = []

        try:
            tree = ast.parse(content)

            # Look for suspicious patterns in AST
            for node in ast.walk(tree):
                # Check for hidden conditionals with sys.exit
                if isinstance(node, ast.If):
                    # Check if body contains exit/shutdown
                    for body_node in ast.walk(node):
                        if isinstance(body_node, ast.Call):
                            if isinstance(body_node.func, ast.Name):
                                if body_node.func.id in ["exit", "quit"]:
                                    threats.append(
                                        {
                                            "type": "CONDITIONAL_EXIT",
                                            "line": node.lineno,
                                            "function": body_node.func.id,
                                        }
                                    )
                            elif isinstance(body_node.func, ast.Attribute):
                                if body_node.func.attr in ["exit", "system", "remove", "rmtree"]:
                                    threats.append(
                                        {
                                            "type": "CONDITIONAL_DANGEROUS_CALL",
                                            "line": node.lineno,
                                            "function": body_node.func.attr,
                                        }
                                    )

                # Check for encoded strings that get executed
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["eval", "exec"]:
                            # Check if argument is decoded
                            if node.args:
                                arg = node.args[0]
                                if isinstance(arg, ast.Call):
                                    if isinstance(arg.func, ast.Attribute):
                                        if "decode" in arg.func.attr:
                                            threats.append(
                                                {
                                                    "type": "EVAL_ENCODED",
                                                    "line": node.lineno,
                                                    "function": node.func.id,
                                                }
                                            )

        except:
            pass

        return threats

    def _check_hardcoded_credentials(self, content: str) -> List[Dict]:
        """Check for hardcoded passwords/tokens"""
        warnings = []

        # Patterns for credentials
        cred_patterns = [
            r'password\s*=\s*["\'][^"\']{8,}["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']',
            r'token\s*=\s*["\'][^"\']{20,}["\']',
            r'secret\s*=\s*["\'][^"\']{20,}["\']',
        ]

        for pattern in cred_patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))

            for match in matches:
                matched_text = match.group()

                # Skip obvious placeholders
                if any(
                    placeholder in matched_text.lower()
                    for placeholder in ["your_", "placeholder", "example", "xxx", "***", "test"]
                ):
                    continue

                line_num = content[: match.start()].count("\n") + 1
                warnings.append(
                    {
                        "type": "HARDCODED_CREDENTIAL",
                        "line": line_num,
                        "matched": matched_text[:50] + "...",
                    }
                )

        return warnings

    def scan_all_files(self) -> Dict:
        """Scan all Python files in project"""
        print("\n" + "=" * 70)
        print("OMEGA FORENSIC SECURITY SCAN")
        print("=" * 70)
        print("\n[*] Starting comprehensive security analysis...")

        # Get all Python files
        python_files = list(self.project_root.glob("*.py"))

        print(f"[*] Found {len(python_files)} Python files to scan\n")

        results = {
            "scan_time": datetime.now().isoformat(),
            "total_files": len(python_files),
            "files_scanned": [],
            "high_risk_files": [],
            "medium_risk_files": [],
            "low_risk_files": [],
            "safe_files": [],
            "summary": {},
        }

        # Scan each file
        for file_path in python_files:
            scan_result = self.scan_file(file_path)
            results["files_scanned"].append(scan_result)

            # Categorize by risk
            if scan_result["risk_level"] == "HIGH":
                results["high_risk_files"].append(scan_result)
            elif scan_result["risk_level"] == "MEDIUM":
                results["medium_risk_files"].append(scan_result)
            elif scan_result["risk_level"] == "LOW":
                results["low_risk_files"].append(scan_result)
            else:
                results["safe_files"].append(scan_result)

        # Generate summary
        results["summary"] = {
            "high_risk_count": len(results["high_risk_files"]),
            "medium_risk_count": len(results["medium_risk_files"]),
            "low_risk_count": len(results["low_risk_files"]),
            "safe_count": len(results["safe_files"]),
            "total_threats": sum(len(f["threats"]) for f in results["files_scanned"]),
            "total_suspicious": sum(len(f["suspicious"]) for f in results["files_scanned"]),
            "total_warnings": sum(len(f["warnings"]) for f in results["files_scanned"]),
        }

        # Save detailed report
        self._save_report(results)

        # Display summary
        self._display_summary(results)

        return results

    def _save_report(self, results: Dict):
        """Save detailed security report"""
        report_file = (
            self.project_root
            / f"SECURITY_FORENSIC_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n[+] Detailed report saved: {report_file.name}")

    def _display_summary(self, results: Dict):
        """Display security scan summary"""
        summary = results["summary"]

        print("\n" + "=" * 70)
        print("SECURITY SCAN SUMMARY")
        print("=" * 70)

        print(f"\n📊 Files Scanned: {results['total_files']}")
        print(f"\n🔴 HIGH RISK:   {summary['high_risk_count']} files")
        print(f"🟡 MEDIUM RISK: {summary['medium_risk_count']} files")
        print(f"🟠 LOW RISK:    {summary['low_risk_count']} files")
        print(f"🟢 SAFE:        {summary['safe_count']} files")

        print(f"\n⚠️  Total Threats:    {summary['total_threats']}")
        print(f"⚡ Suspicious Items: {summary['total_suspicious']}")
        print(f"⚠️  Warnings:        {summary['total_warnings']}")

        # Display high-risk files
        if results["high_risk_files"]:
            print("\n" + "=" * 70)
            print("⚠️  HIGH RISK FILES - IMMEDIATE ATTENTION REQUIRED")
            print("=" * 70)

            for file_result in results["high_risk_files"]:
                filename = Path(file_result["file"]).name
                print(f"\n🔴 {filename}")
                print(f"   Threats: {len(file_result['threats'])}")

                for threat in file_result["threats"][:3]:  # Show first 3
                    print(f"   - Line {threat.get('line', '?')}: {threat['type']}")
                    if "matched" in threat:
                        print(f"     Matched: {threat['matched'][:50]}")

        # Display medium-risk files
        if results["medium_risk_files"]:
            print("\n" + "=" * 70)
            print("🟡 MEDIUM RISK FILES - REVIEW RECOMMENDED")
            print("=" * 70)

            for file_result in results["medium_risk_files"][:5]:  # Show first 5
                filename = Path(file_result["file"]).name
                print(f"\n🟡 {filename}")
                print(f"   Suspicious: {len(file_result['suspicious'])}")

        print("\n" + "=" * 70)

        if summary["high_risk_count"] == 0 and summary["total_threats"] == 0:
            print("✅ NO LOGIC BOMBS OR MALICIOUS CODE DETECTED")
            print("✅ SYSTEM IS SECURE")
        else:
            print("⚠️  SECURITY ISSUES DETECTED - REVIEW REQUIRED")

        print("=" * 70 + "\n")


class ThreatRemediator:
    """Automatically fix or quarantine security threats"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.quarantine_dir = self.project_root / "quarantine"
        self.quarantine_dir.mkdir(exist_ok=True)

    def quarantine_file(self, file_path: Path) -> bool:
        """Move high-risk file to quarantine"""
        try:
            dest = self.quarantine_dir / file_path.name
            file_path.rename(dest)
            print(f"[+] Quarantined: {file_path.name} -> quarantine/")
            return True
        except Exception as e:
            print(f"[!] Failed to quarantine {file_path.name}: {e}")
            return False

    def create_safe_version(self, file_path: Path, threats: List[Dict]) -> bool:
        """Create sanitized version of file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.split("\n")

            # Comment out threat lines
            for threat in threats:
                line_num = threat.get("line", 0)
                if 0 < line_num <= len(lines):
                    lines[line_num - 1] = f"# SECURITY: Disabled - {lines[line_num - 1]}"

            # Save safe version
            safe_content = "\n".join(lines)
            safe_file = file_path.with_suffix(".safe.py")

            with open(safe_file, "w", encoding="utf-8") as f:
                f.write(safe_content)

            print(f"[+] Created safe version: {safe_file.name}")
            return True

        except Exception as e:
            print(f"[!] Failed to create safe version: {e}")
            return False


def main():
    """Main execution"""
    analyzer = ForensicSecurityAnalyzer()

    # Run comprehensive scan
    results = analyzer.scan_all_files()

    # Offer remediation for high-risk files
    if results["high_risk_files"]:
        print("\n[?] High-risk files detected. Remediation options:")
        print("1. Quarantine high-risk files")
        print("2. Create safe versions")
        print("3. Exit (manual review)")

        choice = input("\nSelect option (1-3): ").strip()

        remediator = ThreatRemediator()

        if choice == "1":
            for file_result in results["high_risk_files"]:
                file_path = Path(file_result["file"])
                remediator.quarantine_file(file_path)

        elif choice == "2":
            for file_result in results["high_risk_files"]:
                file_path = Path(file_result["file"])
                remediator.create_safe_version(file_path, file_result["threats"])


if __name__ == "__main__":
    main()
