#!/usr/bin/env python3
"""
QUANTUM FULL SCAN - Master Developer Analysis
Comprehensive code analysis, dependency checking, integration testing, and stress testing.
"""

import os
import ast
import sys
import subprocess
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Set
import json
from collections import defaultdict

REPO_DIR = Path(__file__).parent
BRAIN_DIR = Path(r"D:\RPF_BRAIN")
OUTPUT_DIR = BRAIN_DIR / "Analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class QuantumFullScan:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.dependencies = defaultdict(set)
        self.files_analyzed = []
        self.integration_points = []
        self.breaking_points = []
        
    def scan_all_python_files(self) -> List[Path]:
        """Discover all Python files in the system."""
        python_files = []
        for py_file in REPO_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test" in str(py_file).lower():
                continue
            python_files.append(py_file)
        return sorted(python_files)
    
    def check_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """Check Python syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"SyntaxError: {e.msg} at line {e.lineno}"
        except Exception as e:
            return False, f"Parse error: {str(e)}"
    
    def extract_imports(self, file_path: Path) -> Set[str]:
        """Extract all imports from a Python file."""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except:
            pass
        return imports
    
    def check_file_paths(self, file_path: Path) -> List[str]:
        """Check if file paths in code exist."""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Look for common path patterns
            import re
            path_patterns = [
                r'Path\(r?["\']([^"\']+)["\']\)',
                r'["\']([D-Z]:\\[^"\']+)["\']',
                r'["\'](/[^"\']+)["\']',
            ]
            for pattern in path_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if os.path.isabs(match) or match.startswith('D:'):
                        test_path = Path(match)
                        if not test_path.exists() and not test_path.parent.exists():
                            issues.append(f"Path may not exist: {match}")
        except Exception as e:
            issues.append(f"Error checking paths: {e}")
        return issues
    
    def analyze_dependencies(self, files: List[Path]) -> Dict[str, Set[str]]:
        """Analyze dependencies between files."""
        dep_map = {}
        for file_path in files:
            rel_path = str(file_path.relative_to(REPO_DIR))
            imports = self.extract_imports(file_path)
            dep_map[rel_path] = imports
        return dep_map
    
    def check_circular_dependencies(self, dep_map: Dict[str, Set[str]]) -> List[str]:
        """Detect circular dependencies."""
        cycles = []
        # Simple cycle detection (would need more sophisticated algo for full detection)
        for file1, deps1 in dep_map.items():
            for file2, deps2 in dep_map.items():
                if file1 != file2:
                    module1 = Path(file1).stem
                    module2 = Path(file2).stem
                    if module1 in deps2 and module2 in deps1:
                        cycles.append(f"Circular: {file1} <-> {file2}")
        return cycles
    
    def analyze_worldmemory_integration(self) -> List[str]:
        """Analyze WorldMemory integration points."""
        issues = []
        try:
            # Check if WorldMemory can be imported
            sys.path.insert(0, str(REPO_DIR))
            from WorldMemory import WorldMemory
            wm = WorldMemory()
            
            # Test basic operations
            test_fact = "Quantum scan test fact"
            wm.add_fact(test_fact)
            result = wm.query("quantum scan test")
            if not result:
                issues.append("WorldMemory query returned empty")
            
            # Check stats
            stats = wm.stats()
            if not isinstance(stats, dict):
                issues.append("WorldMemory.stats() returned invalid type")
                
        except Exception as e:
            issues.append(f"WorldMemory integration error: {str(e)}")
        return issues
    
    def stress_test_worldmemory(self) -> List[str]:
        """Stress test WorldMemory with extreme loads."""
        issues = []
        try:
            from WorldMemory import WorldMemory
            wm = WorldMemory()
            
            # Test 1: Large fact addition
            large_fact = "X" * 100000  # 100KB fact
            try:
                wm.add_fact(large_fact)
                issues.append("Large fact added (may cause issues)")
            except Exception as e:
                issues.append(f"Large fact failed: {e}")
            
            # Test 2: Many facts
            for i in range(100):
                wm.add_fact(f"Stress test fact {i}")
            
            # Test 3: Query performance
            import time
            start = time.time()
            wm.query("stress test")
            elapsed = time.time() - start
            if elapsed > 5.0:
                issues.append(f"Query too slow: {elapsed:.2f}s")
                
        except Exception as e:
            issues.append(f"Stress test error: {e}")
        return issues
    
    def check_omega_systems(self) -> List[str]:
        """Check Omega system files for issues."""
        issues = []
        omega_files = list(REPO_DIR.rglob("*Omega*.py"))
        omega_files.extend(list(REPO_DIR.rglob("*SANDBOX*.py")))
        
        for file_path in omega_files:
            # Check syntax
            valid, error = self.check_syntax(file_path)
            if not valid:
                issues.append(f"{file_path.name}: {error}")
            
            # Check for required dependencies
            imports = self.extract_imports(file_path)
            if 'qiskit' in imports:
                try:
                    import qiskit
                except ImportError:
                    issues.append(f"{file_path.name}: qiskit not installed")
            
            if 'httpx' in imports:
                try:
                    import httpx
                except ImportError:
                    issues.append(f"{file_path.name}: httpx not installed")
        
        return issues
    
    def run_full_scan(self) -> Dict:
        """Run complete quantum scan."""
        print("=" * 80)
        print("QUANTUM FULL SCAN - MASTER DEVELOPER ANALYSIS")
        print("=" * 80)
        print()
        
        # Step 1: Discover all files
        print("Step 1: Discovering all Python files...")
        all_files = self.scan_all_python_files()
        print(f"Found {len(all_files)} Python files")
        print()
        
        # Step 2: Syntax checking
        print("Step 2: Syntax checking...")
        syntax_errors = []
        for file_path in all_files:
            valid, error = self.check_syntax(file_path)
            if not valid:
                syntax_errors.append((str(file_path.relative_to(REPO_DIR)), error))
        print(f"Syntax errors: {len(syntax_errors)}")
        if syntax_errors:
            for file, error in syntax_errors[:10]:
                print(f"  ERROR: {file}: {error}")
        print()
        
        # Step 3: Dependency analysis
        print("Step 3: Analyzing dependencies...")
        dep_map = self.analyze_dependencies(all_files)
        cycles = self.check_circular_dependencies(dep_map)
        print(f"Dependencies analyzed: {len(dep_map)} files")
        print(f"Circular dependencies: {len(cycles)}")
        if cycles:
            for cycle in cycles[:5]:
                print(f"  WARNING: {cycle}")
        print()
        
        # Step 4: Integration points
        print("Step 4: Checking integration points...")
        wm_issues = self.analyze_worldmemory_integration()
        print(f"WorldMemory integration issues: {len(wm_issues)}")
        if wm_issues:
            for issue in wm_issues[:5]:
                print(f"  ISSUE: {issue}")
        print()
        
        # Step 5: Omega systems
        print("Step 5: Checking Omega systems...")
        omega_issues = self.check_omega_systems()
        print(f"Omega system issues: {len(omega_issues)}")
        if omega_issues:
            for issue in omega_issues[:5]:
                print(f"  ISSUE: {issue}")
        print()
        
        # Step 6: Stress testing
        print("Step 6: Stress testing WorldMemory...")
        stress_issues = self.stress_test_worldmemory()
        print(f"Stress test issues: {len(stress_issues)}")
        if stress_issues:
            for issue in stress_issues[:5]:
                print(f"  STRESS: {issue}")
        print()
        
        # Compile report
        report = {
            'total_files': len(all_files),
            'syntax_errors': len(syntax_errors),
            'syntax_error_details': syntax_errors,
            'circular_dependencies': cycles,
            'worldmemory_issues': wm_issues,
            'omega_issues': omega_issues,
            'stress_issues': stress_issues,
            'dependency_map': {k: list(v) for k, v in dep_map.items()},
        }
        
        # Save report
        report_file = OUTPUT_DIR / f"quantum_scan_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("=" * 80)
        print("QUANTUM SCAN COMPLETE")
        print("=" * 80)
        print(f"Report saved to: {report_file}")
        print()
        print("SUMMARY:")
        print(f"  Files analyzed: {len(all_files)}")
        print(f"  Syntax errors: {len(syntax_errors)}")
        print(f"  Integration issues: {len(wm_issues) + len(omega_issues)}")
        print(f"  Stress test issues: {len(stress_issues)}")
        print(f"  Total issues: {len(syntax_errors) + len(wm_issues) + len(omega_issues) + len(stress_issues)}")
        print()
        
        return report

if __name__ == "__main__":
    import time
    scanner = QuantumFullScan()
    report = scanner.run_full_scan()

