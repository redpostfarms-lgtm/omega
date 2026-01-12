#!/usr/bin/env python3
"""
Deep Worldwide Scrub - Comprehensive Codebase Audit
===================================================
Scans entire codebase for:
- Incomplete code (TODO, FIXME, pass, NotImplementedError)
- Missing formulas/equations
- Missing API keys/addresses/URLs
- Incomplete functions
- Configuration issues
- GitHub setup problems
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import ast
import sys

@dataclass
class Issue:
    """Issue found in codebase"""
    file_path: str
    line_number: int
    issue_type: str  # 'todo', 'incomplete', 'missing_api', 'missing_formula', 'github', etc.
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    code_snippet: str = ""
    suggestion: str = ""

@dataclass
class ScrubReport:
    """Comprehensive scrub report"""
    total_files_scanned: int = 0
    total_issues: int = 0
    issues_by_type: Dict[str, int] = field(default_factory=dict)
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues: List[Issue] = field(default_factory=list)
    github_status: Dict[str, any] = field(default_factory=dict)
    missing_apis: List[str] = field(default_factory=list)
    incomplete_functions: List[str] = field(default_factory=list)

class DeepScrubber:
    """Deep codebase scrubber"""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.report = ScrubReport()
        self.exclude_dirs = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            'venv', 'env', '.venv', '.env', 'dist', 'build',
            'Organized_Files', '.cache', '.matplotlib', '.ollama'
        }
        self.exclude_files = {'.pyc', '.pyo', '.pyd', '.so', '.dll'}
        
        # Patterns to search for
        self.todo_patterns = [
            r'TODO[:\s]+(.+)',
            r'FIXME[:\s]+(.+)',
            r'XXX[:\s]+(.+)',
            r'HACK[:\s]+(.+)',
            r'BUG[:\s]+(.+)',
            r'INCOMPLETE',
            r'NOT IMPLEMENTED',
            r'MISSING',
            r'PLACEHOLDER',
        ]
        
        self.api_patterns = [
            r'api_key\s*=\s*["\']([^"\']*)["\']',
            r'API_KEY\s*=\s*["\']([^"\']*)["\']',
            r'api_key\s*=\s*["\']\s*["\']',
            r'API_KEY\s*=\s*["\']\s*["\']',
            r'api_key\s*=\s*os\.getenv\(["\']([^"\']+)["\']\s*,\s*["\']\s*["\']\)',
            r'address\s*=\s*["\']\s*["\']',
            r'url\s*=\s*["\']\s*["\']',
            r'endpoint\s*=\s*["\']\s*["\']',
        ]
        
        self.formula_patterns = [
            r'#.*formula.*missing',
            r'#.*equation.*missing',
            r'#.*calculate.*missing',
            r'#.*TODO.*formula',
            r'#.*TODO.*equation',
            r'#.*TODO.*math',
        ]
    
    def scan_file(self, file_path: Path) -> List[Issue]:
        """Scan a single file for issues"""
        issues = []
        
        if not file_path.exists():
            return issues
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            return issues
        
        file_str = ''.join(lines)
        file_rel_path = str(file_path.relative_to(self.root_dir))
        
        # Check for TODO/FIXME comments
        for line_num, line in enumerate(lines, 1):
            # TODO/FIXME patterns
            for pattern in self.todo_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        file_path=file_rel_path,
                        line_number=line_num,
                        issue_type='todo',
                        severity='medium',
                        description=f"TODO/FIXME found: {line.strip()}",
                        code_snippet=line.strip(),
                        suggestion="Complete implementation or remove TODO"
                    ))
            
            # Incomplete functions (pass, ..., NotImplementedError)
            if re.search(r'def\s+\w+.*:\s*$', line) and line_num < len(lines):
                next_line = lines[line_num].strip() if line_num < len(lines) else ""
                if next_line in ['pass', '...'] or 'NotImplementedError' in next_line:
                    issues.append(Issue(
                        file_path=file_rel_path,
                        line_number=line_num,
                        issue_type='incomplete',
                        severity='high',
                        description=f"Incomplete function: {line.strip()}",
                        code_snippet=f"{line.strip()}\n{next_line}",
                        suggestion="Implement function body"
                    ))
            
            # Missing API keys/addresses
            for pattern in self.api_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    value = match.group(1) if match.lastindex else ""
                    if not value or value.strip() == "":
                        issues.append(Issue(
                            file_path=file_rel_path,
                            line_number=line_num,
                            issue_type='missing_api',
                            severity='high',
                            description=f"Missing API key/address/URL: {line.strip()}",
                            code_snippet=line.strip(),
                            suggestion="Add API key or configuration"
                        ))
            
            # Missing formulas
            for pattern in self.formula_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(Issue(
                        file_path=file_rel_path,
                        line_number=line_num,
                        issue_type='missing_formula',
                        severity='high',
                        description=f"Missing formula/equation: {line.strip()}",
                        code_snippet=line.strip(),
                        suggestion="Implement formula or equation"
                    ))
        
        # Parse AST for incomplete functions
        try:
            tree = ast.parse(file_str)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function body is just pass or raise NotImplementedError
                    if len(node.body) == 1:
                        if isinstance(node.body[0], ast.Pass):
                            issues.append(Issue(
                                file_path=file_rel_path,
                                line_number=node.lineno,
                                issue_type='incomplete',
                                severity='high',
                                description=f"Function '{node.name}' has only 'pass'",
                                code_snippet=f"def {node.name}(...): pass",
                                suggestion="Implement function body"
                            ))
                        elif isinstance(node.body[0], ast.Raise):
                            if isinstance(node.body[0].exc, ast.Call):
                                if isinstance(node.body[0].exc.func, ast.Name):
                                    if node.body[0].exc.func.id == 'NotImplementedError':
                                        issues.append(Issue(
                                            file_path=file_rel_path,
                                            line_number=node.lineno,
                                            issue_type='incomplete',
                                            severity='high',
                                            description=f"Function '{node.name}' raises NotImplementedError",
                                            code_snippet=f"def {node.name}(...): raise NotImplementedError",
                                            suggestion="Implement function body"
                                        ))
        except SyntaxError:
            # Skip files with syntax errors
            pass
        
        return issues
    
    def scan_directory(self) -> ScrubReport:
        """Scan entire directory tree"""
        print("=" * 80)
        print("DEEP WORLDWIDE SCRUB - COMPREHENSIVE CODEBASE AUDIT")
        print("=" * 80)
        print()
        
        # Scan all Python files
        python_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # Exclude directories
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    python_files.append(file_path)
        
        self.report.total_files_scanned = len(python_files)
        print(f"Scanning {len(python_files)} Python files...")
        print()
        
        # Scan each file
        for file_path in python_files:
            issues = self.scan_file(file_path)
            self.report.issues.extend(issues)
        
        # Check GitHub status
        self.check_github_status()
        
        # Generate statistics
        self.generate_statistics()
        
        return self.report
    
    def check_github_status(self):
        """Check GitHub repository status"""
        print("Checking GitHub status...")
        
        try:
            # Check if git is initialized
            result = subprocess.run(['git', 'status'], capture_output=True, text=True, timeout=5)
            self.report.github_status['initialized'] = result.returncode == 0
            
            # Check remote
            result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                remotes = result.stdout.strip()
                self.report.github_status['remotes'] = remotes
                self.report.github_status['has_remote'] = bool(remotes)
                
                # Check if remote is accessible
                if 'origin' in remotes:
                    result = subprocess.run(['git', 'fetch', 'origin', '--dry-run'], 
                                           capture_output=True, text=True, timeout=10)
                    self.report.github_status['remote_accessible'] = result.returncode == 0
                    if result.returncode != 0:
                        self.report.issues.append(Issue(
                            file_path=".git/config",
                            line_number=0,
                            issue_type='github',
                            severity='critical',
                            description=f"GitHub remote not accessible: {result.stderr.strip()}",
                            code_snippet="",
                            suggestion="Fix GitHub authentication or repository URL"
                        ))
            else:
                self.report.github_status['has_remote'] = False
                self.report.issues.append(Issue(
                    file_path=".git/config",
                    line_number=0,
                    issue_type='github',
                    severity='high',
                    description="No Git remote configured",
                    code_snippet="",
                    suggestion="Add GitHub remote: git remote add origin <url>"
                ))
        except Exception as e:
            self.report.github_status['error'] = str(e)
            self.report.issues.append(Issue(
                file_path=".git",
                line_number=0,
                issue_type='github',
                severity='critical',
                description=f"GitHub check failed: {e}",
                code_snippet="",
                suggestion="Check Git installation and configuration"
            ))
    
    def generate_statistics(self):
        """Generate statistics from issues"""
        self.report.total_issues = len(self.report.issues)
        
        # Count by type
        for issue in self.report.issues:
            self.report.issues_by_type[issue.issue_type] = \
                self.report.issues_by_type.get(issue.issue_type, 0) + 1
            self.report.issues_by_severity[issue.severity] = \
                self.report.issues_by_severity.get(issue.severity, 0) + 1
        
        # Collect missing APIs
        for issue in self.report.issues:
            if issue.issue_type == 'missing_api':
                self.report.missing_apis.append(issue.description)
        
        # Collect incomplete functions
        for issue in self.report.issues:
            if issue.issue_type == 'incomplete':
                self.report.incomplete_functions.append(issue.description)
    
    def print_report(self):
        """Print comprehensive report"""
        print("=" * 80)
        print("SCRUB REPORT")
        print("=" * 80)
        print()
        
        print(f"Files Scanned: {self.report.total_files_scanned}")
        print(f"Total Issues Found: {self.report.total_issues}")
        print()
        
        print("Issues by Type:")
        for issue_type, count in sorted(self.report.issues_by_type.items()):
            print(f"  {issue_type}: {count}")
        print()
        
        print("Issues by Severity:")
        for severity, count in sorted(self.report.issues_by_severity.items()):
            print(f"  {severity}: {count}")
        print()
        
        # GitHub Status
        print("GitHub Status:")
        for key, value in self.report.github_status.items():
            if key != 'remotes':  # Skip long remotes output
                print(f"  {key}: {value}")
        print()
        
        # Critical Issues
        critical_issues = [i for i in self.report.issues if i.severity == 'critical']
        if critical_issues:
            print(f"CRITICAL ISSUES ({len(critical_issues)}):")
            print("-" * 80)
            for issue in critical_issues[:20]:  # Show first 20
                print(f"[{issue.issue_type.upper()}] {issue.file_path}:{issue.line_number}")
                print(f"  {issue.description}")
                if issue.suggestion:
                    print(f"  → {issue.suggestion}")
                print()
        
        # High Priority Issues
        high_issues = [i for i in self.report.issues if i.severity == 'high']
        if high_issues:
            print(f"HIGH PRIORITY ISSUES ({len(high_issues)}):")
            print("-" * 80)
            for issue in high_issues[:30]:  # Show first 30
                print(f"[{issue.issue_type.upper()}] {issue.file_path}:{issue.line_number}")
                print(f"  {issue.description}")
                print()
    
    def save_report(self, output_file: Path):
        """Save report to JSON file"""
        report_dict = {
            'timestamp': datetime.now().isoformat(),
            'total_files_scanned': self.report.total_files_scanned,
            'total_issues': self.report.total_issues,
            'issues_by_type': self.report.issues_by_type,
            'issues_by_severity': self.report.issues_by_severity,
            'github_status': self.report.github_status,
            'missing_apis': self.report.missing_apis[:50],  # Limit to 50
            'incomplete_functions': self.report.incomplete_functions[:50],  # Limit to 50
            'issues': [
                {
                    'file_path': i.file_path,
                    'line_number': i.line_number,
                    'issue_type': i.issue_type,
                    'severity': i.severity,
                    'description': i.description,
                    'suggestion': i.suggestion
                }
                for i in self.report.issues
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"\nReport saved to: {output_file}")

def main():
    """Main function"""
    root_dir = Path.cwd()
    scrubber = DeepScrubber(root_dir)
    
    # Run scan
    report = scrubber.scan_directory()
    
    # Print report
    scrubber.print_report()
    
    # Save report
    report_file = root_dir / "deep_scrub_report.json"
    scrubber.save_report(report_file)
    
    # Also save as markdown
    markdown_file = root_dir / "DEEP_SCRUB_REPORT.md"
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write("# Deep Worldwide Scrub Report\n\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Files Scanned:** {report.total_files_scanned}\n\n")
        f.write(f"**Total Issues:** {report.total_issues}\n\n")
        
        f.write("## Issues by Type\n\n")
        for issue_type, count in sorted(report.issues_by_type.items()):
            f.write(f"- **{issue_type}**: {count}\n")
        f.write("\n")
        
        f.write("## Critical Issues\n\n")
        critical = [i for i in report.issues if i.severity == 'critical']
        for issue in critical[:50]:
            f.write(f"### {issue.file_path}:{issue.line_number}\n\n")
            f.write(f"**Type:** {issue.issue_type}\n\n")
            f.write(f"**Description:** {issue.description}\n\n")
            if issue.suggestion:
                f.write(f"**Suggestion:** {issue.suggestion}\n\n")
            f.write("---\n\n")
    
    print(f"\nMarkdown report saved to: {markdown_file}")

if __name__ == "__main__":
    main()
