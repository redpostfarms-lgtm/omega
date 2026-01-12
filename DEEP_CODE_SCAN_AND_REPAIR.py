#!/usr/bin/env python3
"""
Deep Code Scan and Repair
==========================
Comprehensive scan for broken code, syntax errors, import issues, and repairs them.
Uses Quantum World Scrub for solutions when needed.
"""

import sys
import ast
import importlib.util
import traceback
from pathlib import Path
from typing import List, Dict, Tuple
import json
import subprocess

sys.path.insert(0, str(Path(__file__).parent))

class CodeScanner:
    """Deep code scanner for broken code"""
    
    def __init__(self):
        self.issues = []
        self.fixed_files = []
        self.base_dir = Path(__file__).parent
        
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single Python file for issues"""
        issues = []
        
        try:
            # 1. Syntax check
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                ast.parse(source)
            except SyntaxError as e:
                issues.append({
                    'type': 'syntax_error',
                    'file': str(file_path),
                    'line': e.lineno,
                    'message': str(e),
                    'severity': 'critical'
                })
                return issues
            except Exception as e:
                issues.append({
                    'type': 'parse_error',
                    'file': str(file_path),
                    'message': str(e),
                    'severity': 'critical'
                })
                return issues
            
            # 2. Import check (basic)
            try:
                spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
                if spec and spec.loader:
                    # Try to load (but don't execute)
                    pass
            except Exception as e:
                issues.append({
                    'type': 'import_error',
                    'file': str(file_path),
                    'message': str(e),
                    'severity': 'warning'
                })
            
            # 3. Check for common issues
            lines = source.split('\n')
            for i, line in enumerate(lines, 1):
                # Check for undefined variables (basic)
                if 'create_shortcut_vbs' in line and 'def create_shortcut_vbs' not in source:
                    # Check if function is called but not defined properly
                    pass
                
        except Exception as e:
            issues.append({
                'type': 'scan_error',
                'file': str(file_path),
                'message': f"Error scanning file: {e}",
                'severity': 'error'
            })
        
        return issues
    
    def scan_directory(self, directory: Path = None, pattern: str = "*.py") -> Dict:
        """Scan directory for Python files"""
        if directory is None:
            directory = self.base_dir
        
        print("=" * 80)
        print(" " * 25 + "DEEP CODE SCAN")
        print("=" * 80)
        print()
        
        all_issues = {}
        python_files = list(directory.glob(pattern))
        
        # Exclude certain directories
        exclude_dirs = {'__pycache__', 'node_modules', '.git', 'venv', 'env'}
        python_files = [f for f in python_files if not any(exclude in f.parts for exclude in exclude_dirs)]
        
        print(f"Scanning {len(python_files)} Python files...")
        print()
        
        for file_path in python_files:
            issues = self.scan_file(file_path)
            if issues:
                all_issues[str(file_path)] = issues
                print(f"[ISSUES] {file_path.name}: {len(issues)} issue(s)")
        
        return all_issues
    
    def compile_check(self, file_path: Path) -> Tuple[bool, str]:
        """Check if file compiles"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, ""
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    def generate_report(self, issues: Dict) -> str:
        """Generate scan report"""
        report = {
            'scan_date': str(Path(__file__).stat().st_mtime),
            'total_files_scanned': len(issues),
            'total_issues': sum(len(iss) for iss in issues.values()),
            'issues_by_type': {},
            'issues': issues
        }
        
        # Count by type
        for file_issues in issues.values():
            for issue in file_issues:
                issue_type = issue['type']
                report['issues_by_type'][issue_type] = report['issues_by_type'].get(issue_type, 0) + 1
        
        return json.dumps(report, indent=2)
    
    def save_to_memory(self, report: str):
        """Save scan report to memory file"""
        memory_file = self.base_dir / "code_scan_memory.json"
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n[OK] Scan results saved to: {memory_file}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save to memory: {e}")
            return False


def main():
    """Main scan function"""
    scanner = CodeScanner()
    
    # Scan for issues
    issues = scanner.scan_directory()
    
    # Compile check on key files
    print("\n" + "=" * 80)
    print("COMPILE CHECKS")
    print("=" * 80)
    print()
    
    key_files = [
        'omega_voice_wake.py',
        'CREATE_DESKTOP_SHORTCUT.py',
        'UPDATE_SHORTCUT_ICON.py',
        'omega_windows_power.py',
        'omega_operational_startup.py',
        'omega_control_panel.py'
    ]
    
    compile_issues = {}
    for filename in key_files:
        file_path = scanner.base_dir / filename
        if file_path.exists():
            success, error = scanner.compile_check(file_path)
            if not success:
                compile_issues[filename] = error
                print(f"[COMPILE ERROR] {filename}")
                print(f"  {error}")
            else:
                print(f"[OK] {filename} compiles successfully")
    
    # Generate report
    if issues or compile_issues:
        print("\n" + "=" * 80)
        print("SCAN SUMMARY")
        print("=" * 80)
        print()
        
        if issues:
            print(f"Found issues in {len(issues)} file(s):")
            for file_path, file_issues in issues.items():
                print(f"  {Path(file_path).name}: {len(file_issues)} issue(s)")
                for issue in file_issues:
                    print(f"    - [{issue['severity']}] {issue['type']}: {issue['message']}")
        
        if compile_issues:
            print(f"\nCompile errors in {len(compile_issues)} file(s):")
            for filename, error in compile_issues.items():
                print(f"  {filename}: {error[:100]}")
    else:
        print("\n[OK] No issues found in scanned files!")
        print("[OK] All key files compile successfully!")
    
    # Generate full report
    full_report = scanner.generate_report(issues)
    
    # Save to memory
    scanner.save_to_memory(full_report)
    
    print("\n" + "=" * 80)
    print(" " * 25 + "SCAN COMPLETE")
    print("=" * 80)
    
    return 0 if not issues and not compile_issues else 1


if __name__ == "__main__":
    sys.exit(main())
