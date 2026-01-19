#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE Problem Solver with Resource Access
Searches for solutions, rewrites code, and ensures smooth integration
"""

import ast
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")


class GateProblemSolver:
    """
    Advanced problem solver with:
    - Web search for solutions
    - Code rewriting authority
    - Integration testing
    - Smooth code merging
    """

    def __init__(self, root_path: Optional[Path] = None):
        self.root = root_path or Path(__file__).parent
        self.solutions_cache = self.root / "data" / "cache" / "solutions.json"
        self.solutions_cache.parent.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log messages"""
        print(f"[{level}] {message}")

    # ============================================
    # CODE ANALYSIS
    # ============================================

    def analyze_python_file(self, file_path: Path) -> Dict:
        """Analyze Python file for issues"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content, filename=str(file_path))

            analysis = {
                "file": str(file_path),
                "valid_syntax": True,
                "imports": [],
                "functions": [],
                "classes": [],
                "issues": [],
            }

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis["imports"].append(node.module)

                elif isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(node.name)

                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(node.name)

            return analysis

        except SyntaxError as e:
            return {
                "file": str(file_path),
                "valid_syntax": False,
                "error": str(e),
                "line": e.lineno,
                "issues": [{"type": "syntax_error", "message": str(e), "line": e.lineno}],
            }
        except Exception as e:
            return {
                "file": str(file_path),
                "valid_syntax": False,
                "error": str(e),
                "issues": [{"type": "parse_error", "message": str(e)}],
            }

    def find_code_conflicts(self, file_paths: List[Path]) -> List[Dict]:
        """Find conflicts between code files"""
        conflicts = []

        # Analyze all files
        analyses = {fp: self.analyze_python_file(fp) for fp in file_paths}

        # Check for duplicate function/class names
        all_functions = {}
        all_classes = {}

        for fp, analysis in analyses.items():
            if not analysis.get("valid_syntax"):
                continue

            for func in analysis.get("functions", []):
                if func in all_functions:
                    conflicts.append(
                        {
                            "type": "duplicate_function",
                            "name": func,
                            "files": [all_functions[func], str(fp)],
                        }
                    )
                else:
                    all_functions[func] = str(fp)

            for cls in analysis.get("classes", []):
                if cls in all_classes:
                    conflicts.append(
                        {
                            "type": "duplicate_class",
                            "name": cls,
                            "files": [all_classes[cls], str(fp)],
                        }
                    )
                else:
                    all_classes[cls] = str(fp)

        return conflicts

    # ============================================
    # CODE REWRITING
    # ============================================

    def fix_syntax_errors(self, file_path: Path) -> Tuple[bool, str]:
        """Attempt to fix common syntax errors"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            fixed = False

            # Fix common issues
            fixes = [
                # Fix missing colons
                (r"(if|elif|else|for|while|def|class)\s+[^:\n]+\n", lambda m: m.group(0).rstrip() + ":\n"),
                # Fix indentation (basic)
                (r"\n( +)(if|elif|else|for|while|def|class)", lambda m: "\n" + " " * (len(m.group(1)) // 4 * 4) + m.group(2)),
            ]

            for pattern, replacement in fixes:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    fixed = True

            if fixed:
                # Verify the fix
                try:
                    ast.parse(content)

                    # Save fixed version
                    backup_path = file_path.with_suffix(".py.bak")
                    with open(backup_path, "w", encoding="utf-8") as f:
                        f.write(original_content)

                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    return True, "Fixed syntax errors"

                except SyntaxError:
                    return False, "Auto-fix failed - manual intervention required"

            return False, "No fixable syntax errors found"

        except Exception as e:
            return False, f"Error fixing syntax: {str(e)}"

    def merge_duplicate_functions(
        self, files: List[Path], function_name: str
    ) -> Tuple[bool, str]:
        """Merge duplicate function implementations"""
        implementations = []

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        # Extract function source
                        func_lines = content.split("\n")[
                            node.lineno - 1 : node.end_lineno
                        ]
                        implementations.append(
                            {
                                "file": file_path,
                                "source": "\n".join(func_lines),
                                "lineno": node.lineno,
                            }
                        )

            except Exception:
                continue

        if len(implementations) <= 1:
            return False, "No duplicates to merge"

        # Keep the most complete implementation (longest)
        best_impl = max(implementations, key=lambda x: len(x["source"]))

        self.log(f"Keeping implementation from: {best_impl['file']}")

        # Comment out duplicates in other files
        for impl in implementations:
            if impl["file"] != best_impl["file"]:
                try:
                    with open(impl["file"], "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    # Comment out the duplicate function
                    for i in range(
                        impl["lineno"] - 1,
                        min(impl["lineno"] + len(impl["source"].split("\n")), len(lines)),
                    ):
                        if not lines[i].strip().startswith("#"):
                            lines[i] = "# DUPLICATE: " + lines[i]

                    with open(impl["file"], "w", encoding="utf-8") as f:
                        f.writelines(lines)

                    self.log(f"Commented out duplicate in: {impl['file']}")

                except Exception as e:
                    self.log(f"Error processing {impl['file']}: {e}", "ERROR")

        return True, f"Merged {len(implementations)} implementations"

    def optimize_imports(self, file_path: Path) -> Tuple[bool, str]:
        """Remove unused imports and organize"""
        try:
            # Use autoflake if available
            try:
                import autoflake
            except ImportError:
                return False, "autoflake not installed"

            # Remove unused imports
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return True, "Optimized imports"
            else:
                return False, result.stderr

        except Exception as e:
            return False, f"Error optimizing imports: {str(e)}"

    # ============================================
    # INTEGRATION TESTING
    # ============================================

    def test_code_integration(self, files: List[Path]) -> Tuple[bool, List[str]]:
        """Test if code integrates smoothly"""
        self.log("Testing code integration...")

        issues = []

        # 1. Syntax check all files
        for file_path in files:
            if file_path.suffix == ".py":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    ast.parse(content)
                except SyntaxError as e:
                    issues.append(f"{file_path.name}:{e.lineno}: {e.msg}")

        # 2. Check for import errors
        for file_path in files:
            if file_path.suffix == ".py":
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(file_path)],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    issues.append(f"{file_path.name}: Import/compilation error")

        # 3. Find conflicts
        conflicts = self.find_code_conflicts(files)
        for conflict in conflicts:
            issues.append(
                f"Conflict: {conflict['type']} '{conflict['name']}' in {', '.join(conflict['files'])}"
            )

        if issues:
            self.log(f"✗ Integration test failed: {len(issues)} issues")
            for issue in issues:
                self.log(f"  - {issue}")
            return False, issues
        else:
            self.log("✓ Integration test passed")
            return True, []

    def run_quick_tests(self) -> Tuple[bool, str]:
        """Run quick test suite"""
        test_file = self.root / "tests" / "test_basic.py"

        if not test_file.exists():
            return True, "No basic tests found"

        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            return True, "Tests passed"
        else:
            return False, f"Tests failed:\n{result.stdout[-500:]}"

    # ============================================
    # SOLUTION SEARCH
    # ============================================

    def search_solution_cache(self, problem: str) -> Optional[str]:
        """Search cached solutions"""
        if not self.solutions_cache.exists():
            return None

        try:
            with open(self.solutions_cache, "r") as f:
                cache = json.load(f)

            # Simple keyword matching
            for cached_problem, solution in cache.items():
                if problem.lower() in cached_problem.lower():
                    return solution

        except Exception:
            pass

        return None

    def cache_solution(self, problem: str, solution: str):
        """Cache a successful solution"""
        try:
            cache = {}
            if self.solutions_cache.exists():
                with open(self.solutions_cache, "r") as f:
                    cache = json.load(f)

            cache[problem] = solution

            with open(self.solutions_cache, "w") as f:
                json.dump(cache, f, indent=2)

        except Exception as e:
            self.log(f"Error caching solution: {e}", "ERROR")

    def generate_solution_prompt(self, problem: Dict) -> str:
        """Generate search prompt for problem"""
        prompts = {
            "syntax_error": f"Python syntax error fix: {problem.get('error', '')}",
            "import_error": f"Python import error solution: {problem.get('module', '')}",
            "duplicate_function": f"Python merge duplicate functions: {problem.get('name', '')}",
            "test_failure": "Python test failure debugging",
        }

        return prompts.get(problem.get("type", ""), "Python error fix")

    # ============================================
    # COMPREHENSIVE FIX
    # ============================================

    async def comprehensive_fix(self, files: Optional[List[Path]] = None) -> Dict:
        """Run comprehensive fix on all Python files"""
        if files is None:
            files = list(self.root.rglob("*.py"))
            files = [
                f for f in files if "__pycache__" not in str(f) and "venv" not in str(f)
            ]

        self.log(f"Running comprehensive fix on {len(files)} files...")

        results = {
            "total_files": len(files),
            "syntax_fixes": 0,
            "import_optimizations": 0,
            "conflicts_resolved": 0,
            "issues": [],
        }

        # 1. Fix syntax errors
        for file_path in files:
            analysis = self.analyze_python_file(file_path)
            if not analysis.get("valid_syntax"):
                success, message = self.fix_syntax_errors(file_path)
                if success:
                    results["syntax_fixes"] += 1
                    self.log(f"✓ Fixed syntax in {file_path.name}")
                else:
                    results["issues"].append(f"{file_path.name}: {message}")

        # 2. Optimize imports
        for file_path in files:
            success, message = self.optimize_imports(file_path)
            if success:
                results["import_optimizations"] += 1

        # 3. Resolve conflicts
        conflicts = self.find_code_conflicts(files)
        for conflict in conflicts:
            if conflict["type"] == "duplicate_function":
                conflict_files = [Path(f) for f in conflict["files"]]
                success, message = self.merge_duplicate_functions(
                    conflict_files, conflict["name"]
                )
                if success:
                    results["conflicts_resolved"] += 1

        # 4. Test integration
        integration_ok, integration_issues = self.test_code_integration(files)
        if not integration_ok:
            results["issues"].extend(integration_issues)

        # 5. Run tests
        tests_ok, test_message = self.run_quick_tests()
        if not tests_ok:
            results["issues"].append(f"Tests: {test_message}")

        return results


async def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("  GATE PROBLEM SOLVER")
    print("=" * 70 + "\n")

    solver = GateProblemSolver()

    print("Options:")
    print("  1. Run comprehensive fix")
    print("  2. Analyze specific file")
    print("  3. Test code integration")
    print("  4. Find and resolve conflicts")

    choice = input("\nChoice (1-4): ").strip()

    if choice == "1":
        results = await solver.comprehensive_fix()
        print("\n" + "=" * 70)
        print("COMPREHENSIVE FIX RESULTS")
        print("=" * 70)
        print(f"Total files: {results['total_files']}")
        print(f"Syntax fixes: {results['syntax_fixes']}")
        print(f"Import optimizations: {results['import_optimizations']}")
        print(f"Conflicts resolved: {results['conflicts_resolved']}")
        print(f"Issues: {len(results['issues'])}")
        if results["issues"]:
            print("\nRemaining issues:")
            for issue in results["issues"][:10]:
                print(f"  - {issue}")

    elif choice == "2":
        file_path = input("Enter file path: ")
        analysis = solver.analyze_python_file(Path(file_path))
        print(json.dumps(analysis, indent=2))

    elif choice == "3":
        import glob

        py_files = [Path(f) for f in glob.glob("*.py")]
        success, issues = solver.test_code_integration(py_files)
        print(f"\nIntegration: {'✓ PASS' if success else '✗ FAIL'}")
        if issues:
            for issue in issues:
                print(f"  - {issue}")

    elif choice == "4":
        import glob

        py_files = [Path(f) for f in glob.glob("**/*.py", recursive=True)]
        conflicts = solver.find_code_conflicts(py_files[:50])  # Limit to 50 files
        print(f"\nFound {len(conflicts)} conflicts:")
        for conflict in conflicts:
            print(f"  - {conflict['type']}: {conflict['name']}")


if __name__ == "__main__":
    asyncio.run(main())
