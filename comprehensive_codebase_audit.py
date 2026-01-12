#!/usr/bin/env python3
"""
Comprehensive Codebase Audit Script
===================================
Deep analysis of The Gatekeeper project for gaps, missing dependencies, and issues.
"""

import os
import sys
import ast
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime
import importlib.util

# Color codes
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

class CodebaseAuditor:
    """Comprehensive codebase auditor."""
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.issues = []
        self.missing_deps = set()
        self.bare_excepts = []
        self.imports = defaultdict(int)
        self.file_stats = defaultdict(int)
        self.test_files = []
        self.config_files = []
        self.skip_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache', '.venv', 'venv', 'env'}
        
        # Standard library modules (should not be in requirements)
        self.stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'pathlib', 'collections',
            'threading', 'multiprocessing', 'asyncio', 'logging', 'configparser',
            'argparse', 'subprocess', 'shutil', 'tempfile', 'pickle', 'csv',
            'hashlib', 'base64', 'random', 'math', 'functools', 'itertools',
            'typing', 'dataclasses', 'enum', 'abc', 'contextlib', 'unittest',
            'urllib', 'http', 'socket', 'ssl', 'email', 'html', 'xml', 'sqlite3',
            'tkinter', 'queue', 'copy', 'weakref', 'gc', 'traceback', 'warnings'
        }
        
        # Critical dependencies to check for
        self.critical_deps = {
            'logging': 'structured logging',
            'prometheus_client': 'metrics collection',
            'structlog': 'structured logging',
            'python-dotenv': 'environment variables',
            'pydantic-settings': 'configuration management',
            'tenacity': 'retry with backoff',
            'click': 'CLI framework',
            'typer': 'modern CLI',
            'rich': 'rich terminal output',
            'pytest': 'testing framework',
            'pytest-asyncio': 'async testing',
            'pytest-cov': 'coverage reporting',
            'pytest-mock': 'mocking',
            'bandit': 'security scanning',
            'safety': 'dependency vulnerability scanning',
            'mypy': 'type checking',
            'black': 'code formatting',
            'flake8': 'linting',
            'isort': 'import sorting'
        }
    
    def audit(self) -> Dict[str, Any]:
        """Run comprehensive audit."""
        print_header("COMPREHENSIVE CODEBASE AUDIT")
        
        print_info("Starting audit...")
        print_info(f"Root directory: {self.root_dir}")
        print()
        
        # Get all Python files
        python_files = self._get_python_files()
        print_info(f"Found {len(python_files)} Python files")
        print()
        
        # Analyze files
        print_header("ANALYZING FILES")
        for py_file in python_files[:200]:  # Limit to first 200 for performance
            self._analyze_file(py_file)
        
        # Check requirements.txt
        print_header("ANALYZING DEPENDENCIES")
        self._analyze_requirements()
        
        # Check for standard files
        print_header("CHECKING STANDARD FILES")
        self._check_standard_files()
        
        # Generate report
        print_header("GENERATING REPORT")
        report = self._generate_report()
        
        return report
    
    def _get_python_files(self) -> List[Path]:
        """Get all Python files in project."""
        python_files = []
        for root, dirs, files in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    py_file = Path(root) / file
                    python_files.append(py_file)
        return python_files
    
    def _analyze_file(self, file_path: Path):
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for bare except
            if re.search(r'except\s*:', content):
                self.bare_excepts.append(str(file_path))
            
            # Parse AST to extract imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module = alias.name.split('.')[0]
                            if module not in self.stdlib_modules:
                                self.imports[module] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split('.')[0]
                            if module not in self.stdlib_modules:
                                self.imports[module] += 1
            except SyntaxError:
                pass  # Skip files with syntax errors
            
            # Check file type
            if 'test' in file_path.name.lower():
                self.test_files.append(str(file_path))
            if 'config' in file_path.name.lower():
                self.config_files.append(str(file_path))
                
        except Exception as e:
            self.issues.append({
                'file': str(file_path),
                'type': 'read_error',
                'message': str(e)
            })
    
    def _analyze_requirements(self):
        """Analyze requirements.txt for missing dependencies."""
        req_file = self.root_dir / 'requirements.txt'
        if not req_file.exists():
            self.issues.append({
                'file': 'requirements.txt',
                'type': 'missing_file',
                'message': 'requirements.txt not found'
            })
            return
        
        # Read requirements
        installed_deps = set()
        try:
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        pkg = re.split(r'[>=<!=]', line)[0].strip()
                        installed_deps.add(pkg.lower())
        except Exception as e:
            self.issues.append({
                'file': 'requirements.txt',
                'type': 'read_error',
                'message': str(e)
            })
        
        # Check for missing critical dependencies
        for dep, description in self.critical_deps.items():
            if dep.lower() not in installed_deps:
                self.missing_deps.add((dep, description))
    
    def _check_standard_files(self):
        """Check for standard project files."""
        standard_files = {
            'setup.py': 'Package installation',
            'pyproject.toml': 'Modern packaging',
            'LICENSE': 'License file',
            'README.md': 'Documentation',
            '.env.example': 'Environment template',
            'CONTRIBUTING.md': 'Contribution guidelines',
            'CHANGELOG.md': 'Version history',
            'pytest.ini': 'Pytest configuration',
            '.pre-commit-config.yaml': 'Pre-commit hooks',
            'Makefile': 'Build automation'
        }
        
        for filename, description in standard_files.items():
            filepath = self.root_dir / filename
            if not filepath.exists():
                self.issues.append({
                    'file': filename,
                    'type': 'missing_standard_file',
                    'message': f'Missing {description}',
                    'description': description
                })
            else:
                print_success(f"{filename} exists")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_python_files': len(self._get_python_files()),
                'bare_except_count': len(self.bare_excepts),
                'missing_deps_count': len(self.missing_deps),
                'issues_count': len(self.issues),
                'test_files_count': len(self.test_files),
                'config_files_count': len(self.config_files)
            },
            'bare_excepts': self.bare_excepts[:50],  # Limit for report
            'missing_dependencies': list(self.missing_deps),
            'top_imports': dict(sorted(self.imports.items(), key=lambda x: x[1], reverse=True)[:30]),
            'issues': self.issues,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        if self.bare_excepts:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Code Quality',
                'issue': f'{len(self.bare_excepts)} files with bare except: clauses',
                'recommendation': 'Replace bare except: with specific exception types'
            })
        
        if self.missing_deps:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Dependencies',
                'issue': f'{len(self.missing_deps)} potentially missing dependencies',
                'recommendation': 'Review and add missing dependencies to requirements.txt'
            })
        
        if not (self.root_dir / 'setup.py').exists() and not (self.root_dir / 'pyproject.toml').exists():
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Project Structure',
                'issue': 'Missing setup.py or pyproject.toml',
                'recommendation': 'Add modern Python packaging configuration'
            })
        
        if not (self.root_dir / 'LICENSE').exists():
            recommendations.append({
                'priority': 'LOW',
                'category': 'Project Structure',
                'issue': 'Missing LICENSE file',
                'recommendation': 'Add LICENSE file'
            })
        
        if len(self.test_files) < 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Testing',
                'issue': 'Limited test coverage',
                'recommendation': 'Add more comprehensive test suite'
            })
        
        return recommendations

def main():
    """Main entry point."""
    root_dir = Path(__file__).parent.absolute()
    
    auditor = CodebaseAuditor(root_dir)
    report = auditor.audit()
    
    # Print summary
    print_header("AUDIT SUMMARY")
    print_info(f"Total Python files: {report['summary']['total_python_files']}")
    print_warning(f"Bare except clauses: {report['summary']['bare_except_count']}")
    print_warning(f"Potentially missing dependencies: {report['summary']['missing_deps_count']}")
    print_error(f"Total issues: {report['summary']['issues_count']}")
    print()
    
    # Print top imports
    print_header("TOP IMPORTS (Non-Standard)")
    for module, count in list(report['top_imports'].items())[:20]:
        print(f"  {module}: {count} files")
    print()
    
    # Print missing dependencies
    if report['missing_dependencies']:
        print_header("POTENTIALLY MISSING DEPENDENCIES")
        for dep, desc in report['missing_dependencies']:
            print_warning(f"{dep} - {desc}")
        print()
    
    # Print recommendations
    print_header("RECOMMENDATIONS")
    for rec in report['recommendations']:
        priority_color = Colors.RED if rec['priority'] == 'HIGH' else Colors.YELLOW if rec['priority'] == 'MEDIUM' else Colors.BLUE
        print(f"{priority_color}[{rec['priority']}]{Colors.RESET} {rec['category']}: {rec['issue']}")
        print(f"  → {rec['recommendation']}")
        print()
    
    # Save report
    report_file = root_dir / 'comprehensive_audit_report.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    print_success(f"Full report saved to: {report_file}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
