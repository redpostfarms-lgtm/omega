#!/usr/bin/env python3
"""
Gatekeeper Deep Scan - Comprehensive System Analysis
====================================================
Scans for gaps, holes, missing dependencies, and issues.
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime


class DeepScanner:
    """Comprehensive deep scan for gaps, dependencies, and issues."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.issues = []
        self.warnings = []
        self.missing_deps = set()
        self.bare_excepts = []
        self.imports = defaultdict(set)
        self.undefined_vars = []
        self.todos = []
        
    def scan_file(self, file_path: Path) -> Dict[str, Any]:
        """Scan a single Python file."""
        results = {
            'file': str(file_path.relative_to(self.base_dir)),
            'imports': [],
            'bare_excepts': [],
            'todos': [],
            'undefined_vars': [],
            'errors': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                results['errors'].append(f"Syntax error: {e}")
                return results
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        results['imports'].append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        results['imports'].append(node.module.split('.')[0])
            
            # Find bare except clauses
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    lineno = node.lineno
                    results['bare_excepts'].append({
                        'line': lineno,
                        'context': self._get_line_context(content, lineno)
                    })
            
            # Find TODO/FIXME comments
            for i, line in enumerate(content.split('\n'), 1):
                if re.search(r'\b(TODO|FIXME|XXX|HACK|BUG|FIXME)\b', line, re.IGNORECASE):
                    results['todos'].append({
                        'line': i,
                        'content': line.strip()
                    })
            
            # Check for undefined variables (basic check)
            defined_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    defined_names.add(node.name)
                    for arg in node.args.args:
                        defined_names.add(arg.arg)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    defined_names.add(node.id)
            
        except Exception as e:
            results['errors'].append(f"Scan error: {e}")
        
        return results
    
    def _get_line_context(self, content: str, lineno: int, context_lines: int = 3) -> str:
        """Get context around a line number."""
        lines = content.split('\n')
        start = max(0, lineno - context_lines - 1)
        end = min(len(lines), lineno + context_lines)
        return '\n'.join(lines[start:end])
    
    def scan_all(self) -> Dict[str, Any]:
        """Scan all Python files in the directory."""
        print("Scanning Python files...")
        
        python_files = list(self.base_dir.rglob('*.py'))
        # Exclude common directories
        exclude_dirs = {'__pycache__', '.git', 'node_modules', 'venv', 'env', '.venv'}
        python_files = [f for f in python_files if not any(ex in str(f) for ex in exclude_dirs)]
        
        all_results = []
        all_imports = set()
        total_bare_excepts = 0
        total_todos = 0
        
        for py_file in python_files:
            result = self.scan_file(py_file)
            all_results.append(result)
            all_imports.update(result['imports'])
            total_bare_excepts += len(result['bare_excepts'])
            total_todos += len(result['todos'])
        
        # Check dependencies
        requirements_file = self.base_dir / 'requirements.txt'
        required_deps = set()
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        dep = re.split(r'[>=<!=]', line)[0].strip()
                        if dep:
                            required_deps.add(dep.lower())
        
        # Find missing dependencies
        standard_lib = {
            'sys', 'os', 'json', 'time', 'datetime', 'pathlib', 'typing',
            'collections', 'threading', 'subprocess', 'ast', 're', 'math',
            'random', 'hashlib', 'base64', 'urllib', 'http', 'email',
            'sqlite3', 'csv', 'io', 'pickle', 'copy', 'functools', 'itertools',
            'tkinter', 'unittest', 'logging', 'warnings', 'traceback'
        }
        
        missing_deps = []
        for imp in all_imports:
            imp_lower = imp.lower()
            if imp_lower not in standard_lib and imp_lower not in required_deps:
                # Check if it's a known package
                known_packages = {
                    'pygame', 'numpy', 'pyaudio', 'psutil', 'matplotlib',
                    'pandas', 'requests', 'yaml', 'pyyaml', 'pillow', 'pil',
                    'torch', 'transformers', 'speechbrain', 'librosa',
                    'scipy', 'sounddevice', 'pydub', 'soundfile',
                    'win32gui', 'win32con', 'win32api', 'wmi',
                    'pyautogui', 'pynput', 'dnspython', 'cryptography',
                    'openrgb', 'redis', 'aiofiles', 'aiohttp', 'tqdm',
                    'outlines', 'pydantic', 'mauve', 'datasets', 'accelerate',
                    'plotly', 'pyjwt', 'beautifulsoup4', 'bs4', 'scapy'
                }
                if imp_lower in known_packages:
                    missing_deps.append(imp_lower)
        
        # Compile report
        report = {
            'timestamp': datetime.now().isoformat(),
            'files_scanned': len(all_results),
            'total_bare_excepts': total_bare_excepts,
            'total_todos': total_todos,
            'missing_dependencies': sorted(set(missing_deps)),
            'files_with_bare_excepts': [
                r for r in all_results if r['bare_excepts']
            ],
            'files_with_todos': [
                r for r in all_results if r['todos']
            ],
            'files_with_errors': [
                r for r in all_results if r['errors']
            ],
            'all_imports': sorted(all_imports),
        }
        
        return report
    
    def generate_fix_plan(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a plan to fix identified issues."""
        fix_plan = {
            'missing_dependencies': [],
            'bare_except_fixes': [],
            'priority': []
        }
        
        # Missing dependencies
        for dep in report['missing_dependencies']:
            fix_plan['missing_dependencies'].append({
                'package': dep,
                'action': 'add_to_requirements',
                'priority': 'high' if dep in ['numpy', 'psutil', 'pygame', 'pyaudio'] else 'medium'
            })
        
        # Bare except fixes
        for file_result in report['files_with_bare_excepts']:
            for bare_except in file_result['bare_excepts']:
                fix_plan['bare_except_fixes'].append({
                    'file': file_result['file'],
                    'line': bare_except['line'],
                    'action': 'replace_with_except_exception',
                    'priority': 'high'
                })
        
        # Priority list
        fix_plan['priority'] = [
            'Fix bare except clauses (prevents proper shutdown)',
            'Add missing dependencies to requirements.txt',
            'Review TODO/FIXME comments',
            'Fix syntax errors if any'
        ]
        
        return fix_plan


def main():
    """Main scan function."""
    base_dir = Path(__file__).parent
    scanner = DeepScanner(base_dir)
    
    print("=" * 80)
    print(" " * 25 + "GATEKEEPER DEEP SCAN")
    print("=" * 80)
    print()
    
    report = scanner.scan_all()
    fix_plan = scanner.generate_fix_plan(report)
    
    # Print summary
    print(f"Files Scanned: {report['files_scanned']}")
    print(f"Bare Except Clauses: {report['total_bare_excepts']}")
    print(f"TODO/FIXME Comments: {report['total_todos']}")
    print(f"Missing Dependencies: {len(report['missing_dependencies'])}")
    print()
    
    if report['missing_dependencies']:
        print("Missing Dependencies:")
        for dep in report['missing_dependencies']:
            print(f"  - {dep}")
        print()
    
    if report['files_with_bare_excepts']:
        print("Files with Bare Except Clauses:")
        for file_result in report['files_with_bare_excepts'][:10]:  # Show first 10
            print(f"  - {file_result['file']}: {len(file_result['bare_excepts'])} instances")
        print()
    
    # Save report
    report_file = base_dir / 'deep_scan_report.json'
    with open(report_file, 'w') as f:
        json.dump({
            'report': report,
            'fix_plan': fix_plan
        }, f, indent=2)
    
    print(f"Report saved to: {report_file}")
    
    return report, fix_plan


if __name__ == "__main__":
    main()
