# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Defensive Security Scanner - For Your Own Code Only
#
# Purpose: Scan your own code for security vulnerabilities
# Use for: Your own applications, authorized security assessments

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class DefensiveSecurityScanner:
    """Security scanner for your own code.
    
    Use for:
    - Scanning your own applications
    - Security code reviews
    - Secure coding practices
    
    NOT for:
    - Scanning unauthorized systems
    - Automated exploitation
    - Unauthorized security testing
    """
    
    def __init__(self, target_directory: Path):
        """Initialize security scanner.
        
        Args:
            target_directory: Directory containing your own code to scan
        """
        self.target_directory = Path(target_directory)
        if not self.target_directory.exists():
            raise ValueError(f"Directory does not exist: {target_directory}")
    
    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a single file for security issues.
        
        Args:
            file_path: Path to file to scan
        
        Returns:
            List of vulnerability dictionaries
        """
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check for hardcoded credentials
            vulns = self._check_hardcoded_credentials(lines, file_path)
            vulnerabilities.extend(vulns)
            
            # Check for SQL injection risks
            vulns = self._check_sql_injection(lines, file_path)
            vulnerabilities.extend(vulns)
            
            # Check for unsafe deserialization
            vulns = self._check_deserialization(lines, file_path)
            vulnerabilities.extend(vulns)
            
            # Check for command injection
            vulns = self._check_command_injection(lines, file_path)
            vulnerabilities.extend(vulns)
            
            # Check for path traversal
            vulns = self._check_path_traversal(lines, file_path)
            vulnerabilities.extend(vulns)
            
            # AST-based checks
            vulns = self._check_ast_security(content, file_path)
            vulnerabilities.extend(vulns)
        
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            vulnerabilities.append({
                "type": "scan_error",
                "severity": "low",
                "line": 0,
                "message": f"Error scanning file: {e}",
                "file": str(file_path)
            })
        
        return vulnerabilities
    
    def _check_hardcoded_credentials(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        """Check for hardcoded credentials."""
        vulnerabilities = []
        patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\']([^"\']+)["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\']([^"\']+)["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\']([^"\']+)["\']', "Hardcoded token"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, vuln_type in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Check if it's using environment variables
                    if 'os.getenv' not in line and 'os.environ' not in line:
                        vulnerabilities.append({
                            "type": vuln_type,
                            "severity": "high",
                            "line": i,
                            "message": f"{vuln_type} detected. Use environment variables instead.",
                            "file": str(file_path),
                            "code": line.strip()
                        })
        
        return vulnerabilities
    
    def _check_sql_injection(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        """Check for SQL injection risks."""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            # Check for string formatting in SQL queries
            if re.search(r'execute\s*\([^)]*%', line) or re.search(r'execute\s*\([^)]*\+', line):
                if '?' not in line and '%s' not in line:
                    vulnerabilities.append({
                        "type": "SQL Injection Risk",
                        "severity": "high",
                        "line": i,
                        "message": "SQL query uses string formatting. Use parameterized queries.",
                        "file": str(file_path),
                        "code": line.strip()
                    })
        
        return vulnerabilities
    
    def _check_deserialization(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        """Check for unsafe deserialization."""
        vulnerabilities = []
        unsafe_patterns = [
            (r'pickle\.loads\s*\(', "Unsafe pickle deserialization"),
            (r'yaml\.load\s*\(', "Unsafe YAML deserialization (use yaml.safe_load)"),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, vuln_type in unsafe_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        "type": vuln_type,
                        "severity": "high",
                        "line": i,
                        "message": f"{vuln_type} detected. Use safe alternatives.",
                        "file": str(file_path),
                        "code": line.strip()
                    })
        
        return vulnerabilities
    
    def _check_command_injection(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        """Check for command injection risks."""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            # Check for os.system with user input
            if 'os.system(' in line or 'subprocess.call(' in line:
                if any(var in line for var in ['input(', 'argv', 'user_input', 'request.']):
                    vulnerabilities.append({
                        "type": "Command Injection Risk",
                        "severity": "high",
                        "line": i,
                        "message": "Command execution with user input. Sanitize input or use subprocess with shell=False.",
                        "file": str(file_path),
                        "code": line.strip()
                    })
        
        return vulnerabilities
    
    def _check_path_traversal(self, lines: List[str], file_path: Path) -> List[Dict[str, Any]]:
        """Check for path traversal risks."""
        vulnerabilities = []
        
        for i, line in enumerate(lines, 1):
            if 'open(' in line and '../' in line:
                if 'os.path.abspath' not in line and 'os.path.join' not in line:
                    vulnerabilities.append({
                        "type": "Path Traversal Risk",
                        "severity": "medium",
                        "line": i,
                        "message": "File operation with relative path. Validate and sanitize paths.",
                        "file": str(file_path),
                        "code": line.strip()
                    })
        
        return vulnerabilities
    
    def _check_ast_security(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """AST-based security checks."""
        vulnerabilities = []
        
        try:
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                # Check for eval usage
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id == 'eval':
                            vulnerabilities.append({
                                "type": "Unsafe eval() usage",
                                "severity": "high",
                                "line": node.lineno if hasattr(node, 'lineno') else 0,
                                "message": "eval() is dangerous with user input. Use safer alternatives.",
                                "file": str(file_path)
                            })
        except SyntaxError:
            pass  # Skip if syntax error
        
        return vulnerabilities
    
    def scan_directory(self) -> Dict[str, Any]:
        """Scan entire directory for security issues.
        
        Returns:
            Dictionary with scan results
        """
        all_vulnerabilities = []
        files_scanned = 0
        
        # Find all Python files
        for py_file in self.target_directory.rglob("*.py"):
            if '__pycache__' in str(py_file):
                continue
            
            vulns = self.scan_file(py_file)
            all_vulnerabilities.extend(vulns)
            files_scanned += 1
        
        # Categorize by severity
        high_severity = [v for v in all_vulnerabilities if v.get('severity') == 'high']
        medium_severity = [v for v in all_vulnerabilities if v.get('severity') == 'medium']
        low_severity = [v for v in all_vulnerabilities if v.get('severity') == 'low']
        
        return {
            "total_vulnerabilities": len(all_vulnerabilities),
            "high_severity": len(high_severity),
            "medium_severity": len(medium_severity),
            "low_severity": len(low_severity),
            "files_scanned": files_scanned,
            "vulnerabilities": all_vulnerabilities,
            "summary": {
                "high": high_severity,
                "medium": medium_severity,
                "low": low_severity
            }
        }


def main():
    """Example usage (scan your own code)."""
    print("Defensive Security Scanner - For Your Own Code Only")
    print("=" * 60)
    
    # Example: Scan current directory (your own code)
    scanner = DefensiveSecurityScanner(Path.cwd())
    
    print(f"Scanning: {scanner.target_directory}")
    print("Scanning for security vulnerabilities...\n")
    
    results = scanner.scan_directory()
    
    print(f"Scan Results:")
    print(f"  Files scanned: {results['files_scanned']}")
    print(f"  Total vulnerabilities: {results['total_vulnerabilities']}")
    print(f"  High severity: {results['high_severity']}")
    print(f"  Medium severity: {results['medium_severity']}")
    print(f"  Low severity: {results['low_severity']}")
    
    if results['high_severity'] > 0:
        print("\n⚠️  High Severity Issues:")
        for vuln in results['summary']['high'][:5]:  # Show first 5
            print(f"  - {vuln['type']} in {vuln['file']}:{vuln.get('line', '?')}")
            print(f"    {vuln['message']}")
    
    print("\n✅ Security scan complete (your own code only)")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
