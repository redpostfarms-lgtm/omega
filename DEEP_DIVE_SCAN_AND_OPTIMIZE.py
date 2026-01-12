#!/usr/bin/env python3
"""
Deep Dive Scan and Optimization System
=======================================
Performs comprehensive scan for errors, redundancies, and optimization opportunities.
"""

import sys
import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict

class DeepDiveScanner:
    """Deep dive scanner for errors, redundancies, and optimization"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.issues = []
        self.redundancies = []
        self.optimizations = []
        self.config_files = []
        self.duplicate_code = defaultdict(list)
        
    def scan_all(self) -> Dict[str, Any]:
        """Perform comprehensive scan"""
        print("\n" + "=" * 80)
        print(" " * 20 + "DEEP DIVE SCAN - COMPREHENSIVE ANALYSIS")
        print("=" * 80)
        print()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "redundancies": [],
            "optimizations": [],
            "duplicate_code": [],
            "config_files": [],
            "errors": []
        }
        
        # 1. Scan for config files
        print("[1/7] Scanning for configuration files...")
        results["config_files"] = self.scan_config_files()
        print(f"[OK] Found {len(results['config_files'])} config files")
        
        # 2. Scan for duplicate code
        print("[2/7] Scanning for duplicate code...")
        results["duplicate_code"] = self.scan_duplicate_code()
        print(f"[OK] Found {len(results['duplicate_code'])} duplicate patterns")
        
        # 3. Scan for redundancies
        print("[3/7] Scanning for redundancies...")
        results["redundancies"] = self.scan_redundancies()
        print(f"[OK] Found {len(results['redundancies'])} redundancies")
        
        # 4. Scan for errors
        print("[4/7] Scanning for errors...")
        results["errors"] = self.scan_errors()
        print(f"[OK] Found {len(results['errors'])} errors")
        
        # 5. Scan for issues
        print("[5/7] Scanning for issues...")
        results["issues"] = self.scan_issues()
        print(f"[OK] Found {len(results['issues'])} issues")
        
        # 6. Identify optimizations
        print("[6/7] Identifying optimizations...")
        results["optimizations"] = self.identify_optimizations()
        print(f"[OK] Found {len(results['optimizations'])} optimization opportunities")
        
        # 7. Generate report
        print("[7/7] Generating report...")
        report = self.generate_report(results)
        print("[OK] Report generated")
        print()
        
        return results
    
    def scan_config_files(self) -> List[Dict[str, Any]]:
        """Scan for configuration files and identify duplicates"""
        config_files = []
        config_patterns = [
            "*config*.json",
            "*.settings.json",
            "*.config.json",
            "*_config.json"
        ]
        
        for pattern in config_patterns:
            for file_path in self.base_dir.rglob(pattern):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            try:
                                config_data = json.loads(content)
                            except:
                                config_data = None
                        
                        config_files.append({
                            "path": str(file_path.relative_to(self.base_dir)),
                            "size": file_path.stat().st_size,
                            "has_json": config_data is not None,
                            "keys": list(config_data.keys()) if config_data else []
                        })
                    except:
                        pass
        
        return config_files
    
    def scan_duplicate_code(self) -> List[Dict[str, Any]]:
        """Scan for duplicate code patterns"""
        duplicates = []
        
        # Get all Python files
        python_files = list(self.base_dir.rglob("*.py"))
        
        # Simple duplicate detection based on function/class signatures
        signatures = defaultdict(list)
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Find function definitions
                    func_pattern = r'def\s+(\w+)\s*\([^)]*\):'
                    for match in re.finditer(func_pattern, content):
                        func_name = match.group(1)
                        signatures[func_name].append(str(py_file.relative_to(self.base_dir)))
                    
                    # Find class definitions
                    class_pattern = r'class\s+(\w+)[\s(:]'
                    for match in re.finditer(class_pattern, content):
                        class_name = match.group(1)
                        signatures[class_name].append(str(py_file.relative_to(self.base_dir)))
            
            except:
                pass
        
        # Find duplicates
        for name, files in signatures.items():
            if len(files) > 1:
                duplicates.append({
                    "name": name,
                    "files": files,
                    "count": len(files)
                })
        
        return duplicates
    
    def scan_redundancies(self) -> List[Dict[str, Any]]:
        """Scan for redundancies"""
        redundancies = []
        
        # Check for duplicate config files
        config_files = self.scan_config_files()
        config_contents = {}
        
        for cfg in config_files:
            path = cfg["path"]
            if cfg["has_json"]:
                try:
                    with open(self.base_dir / path, 'r', encoding='utf-8') as f:
                        content = json.dumps(json.load(f), sort_keys=True)
                        if content in config_contents:
                            redundancies.append({
                                "type": "duplicate_config",
                                "file1": config_contents[content],
                                "file2": path,
                                "issue": "Duplicate configuration content"
                            })
                        else:
                            config_contents[content] = path
                except:
                    pass
        
        # Check for redundant imports
        python_files = list(self.base_dir.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    imports = []
                    for i, line in enumerate(lines):
                        if line.strip().startswith('import ') or line.strip().startswith('from '):
                            if line.strip() in imports:
                                redundancies.append({
                                    "type": "duplicate_import",
                                    "file": str(py_file.relative_to(self.base_dir)),
                                    "line": i + 1,
                                    "import": line.strip(),
                                    "issue": "Duplicate import statement"
                                })
                            else:
                                imports.append(line.strip())
            except:
                pass
        
        return redundancies
    
    def scan_errors(self) -> List[Dict[str, Any]]:
        """Scan for errors"""
        errors = []
        
        # Check for common error patterns
        python_files = list(self.base_dir.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for syntax issues
                    if 'import json' in content and 'import json' in content.split('\n')[0:5]:
                        # Check if json is used but might not be imported correctly
                        pass
                    
                    # Check for common error patterns
                    error_patterns = [
                        (r'UnboundLocalError', 'Potential unbound local variable'),
                        (r'NameError', 'Potential name error'),
                        (r'TypeError', 'Potential type error'),
                        (r'AttributeError', 'Potential attribute error'),
                    ]
                    
                    for pattern, description in error_patterns:
                        if re.search(pattern, content):
                            errors.append({
                                "type": "error_pattern",
                                "file": str(py_file.relative_to(self.base_dir)),
                                "pattern": pattern,
                                "issue": description
                            })
            except:
                pass
        
        return errors
    
    def scan_issues(self) -> List[Dict[str, Any]]:
        """Scan for general issues"""
        issues = []
        
        # Check for large files
        python_files = list(self.base_dir.rglob("*.py"))
        for py_file in python_files:
            size = py_file.stat().st_size
            if size > 100000:  # 100KB
                issues.append({
                    "type": "large_file",
                    "file": str(py_file.relative_to(self.base_dir)),
                    "size": size,
                    "issue": f"Large file ({size} bytes) - consider splitting"
                })
        
        # Check for files with many lines
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    if lines > 1000:
                        issues.append({
                            "type": "many_lines",
                            "file": str(py_file.relative_to(self.base_dir)),
                            "lines": lines,
                            "issue": f"File has {lines} lines - consider refactoring"
                        })
            except:
                pass
        
        return issues
    
    def identify_optimizations(self) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        optimizations = []
        
        # Check for inefficient patterns
        python_files = list(self.base_dir.rglob("*.py"))
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for multiple file opens
                    if content.count('open(') > 10:
                        optimizations.append({
                            "type": "multiple_file_opens",
                            "file": str(py_file.relative_to(self.base_dir)),
                            "count": content.count('open('),
                            "suggestion": "Consider using context managers or caching file handles"
                        })
                    
                    # Check for repeated string concatenations
                    if content.count('+') > 50 and 'str' in content:
                        optimizations.append({
                            "type": "string_concatenation",
                            "file": str(py_file.relative_to(self.base_dir)),
                            "suggestion": "Consider using f-strings or join()"
                        })
            except:
                pass
        
        return optimizations
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate scan report"""
        report_lines = [
            "# Deep Dive Scan Report",
            "=" * 80,
            f"Generated: {results['timestamp']}",
            "",
            "## Summary",
            f"- Configuration Files: {len(results['config_files'])}",
            f"- Duplicate Code Patterns: {len(results['duplicate_code'])}",
            f"- Redundancies: {len(results['redundancies'])}",
            f"- Errors: {len(results['errors'])}",
            f"- Issues: {len(results['issues'])}",
            f"- Optimizations: {len(results['optimizations'])}",
            "",
            "## Details",
            ""
        ]
        
        # Add details for each category
        if results['redundancies']:
            report_lines.append("### Redundancies")
            for red in results['redundancies'][:20]:  # Limit to 20
                report_lines.append(f"- {red.get('type', 'unknown')}: {red.get('issue', 'N/A')}")
                if 'file' in red:
                    report_lines.append(f"  File: {red['file']}")
                if 'file1' in red and 'file2' in red:
                    report_lines.append(f"  Files: {red['file1']} <-> {red['file2']}")
            report_lines.append("")
        
        if results['duplicate_code']:
            report_lines.append("### Duplicate Code")
            for dup in results['duplicate_code'][:20]:  # Limit to 20
                report_lines.append(f"- {dup['name']}: Found in {dup['count']} files")
                for file in dup['files'][:5]:  # Limit to 5 files
                    report_lines.append(f"  - {file}")
            report_lines.append("")
        
        report_path = self.base_dir / "DEEP_DIVE_SCAN_REPORT.md"
        report_content = "\n".join(report_lines)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)

def main():
    """Main function"""
    base_dir = Path(__file__).parent.absolute()
    scanner = DeepDiveScanner(base_dir)
    
    results = scanner.scan_all()
    
    # Save results
    results_file = base_dir / "deep_dive_scan_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print("=" * 80)
    print(" " * 25 + "SCAN COMPLETE")
    print("=" * 80)
    print()
    print(f"Results saved to: {results_file.name}")
    print(f"Report saved to: DEEP_DIVE_SCAN_REPORT.md")
    print()
    print("Summary:")
    print(f"  - Configuration Files: {len(results['config_files'])}")
    print(f"  - Duplicate Code: {len(results['duplicate_code'])}")
    print(f"  - Redundancies: {len(results['redundancies'])}")
    print(f"  - Errors: {len(results['errors'])}")
    print(f"  - Issues: {len(results['issues'])}")
    print(f"  - Optimizations: {len(results['optimizations'])}")
    print()

if __name__ == "__main__":
    main()
