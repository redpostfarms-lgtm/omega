# -*- coding: utf-8 -*-
# CODE REVIEWER AGENT - Self-improving code analysis
# Inherits from Agent base class, adds AST-based code review capabilities

import os
import ast
import json
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import base Agent class
from agent_anonymous import Agent, AgentConfig

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        # If encoding can't be changed, continue without modification
        pass


class CodeReviewer(Agent):
    """
    Code review agent that analyzes Python code for smells, violations, and improvements.
    Inherits all base Agent capabilities (skill logging, retry logic, self-improvement).
    """
    
    def __init__(self, goal: str = "review code for quality and best practices", config: Optional[AgentConfig] = None):
        """
        Initialize code reviewer agent.
        
        Args:
            goal: Agent's goal (default: code review)
            config: Optional AgentConfig (uses defaults if None)
        """
        super().__init__(goal, config)
        self.review_history: List[Dict[str, Any]] = []
        self.violations_found = 0
        self.code_analyzed = 0
        
        # Initialize review rules (can be extended)
        self.rules = {
            "max_line_length": 80,
            "check_globals": True,
            "check_imports": True,
            "check_naming": True,
            "check_complexity": True
        }
    
    def run_task(self, file_path: str = "./test.py") -> bool:
        """
        Run code review on specified file.
        
        Args:
            file_path: Path to Python file to review
            
        Returns:
            True if review completed successfully, False otherwise
        """
        def review():
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(code, filename=file_path)
                self.history.append(f'Parsed AST clean from {file_path}.')
            except SyntaxError as e:
                error_msg = f'Syntax error in {file_path}: {str(e)} at line {e.lineno}'
                self.history.append(error_msg)
                self.log_run('parse', f'syntax_error_line_{e.lineno}', False)
                raise SyntaxError(error_msg) from e
            
            # Scan for code smells
            violations = self.scan_for_smells(tree, file_path, code)
            
            if violations:
                self.violations_found += len(violations)
                self.history.append(f'Found {len(violations)} code smells in {file_path}.')
                self.report_fixes(violations, file_path)
                self.log_run(
                    'lint',
                    f'{len(violations)} issues found in {file_path}',
                    True
                )
            else:
                self.history.append(f'No issues found in {file_path}.')
                self.log_run('lint', f'clean code in {file_path}', True)
            
            self.code_analyzed += 1
            
            # Store review in history
            self.review_history.append({
                "file": file_path,
                "timestamp": str(datetime.now()),
                "violations": len(violations),
                "issues": violations
            })
            
            return True
        
        return self.run_with_retry(review)
    
    def scan_for_smells(self, tree: ast.AST, file_path: str, code: str) -> List[Dict[str, Any]]:
        """
        Scan AST for code smells and violations.
        
        Args:
            tree: Parsed AST tree
            file_path: Path to file being analyzed
            code: Original source code (for line analysis)
            
        Returns:
            List of violation dictionaries
        """
        issues = []
        lines = code.split('\n')
        
        # Walk through AST nodes
        for node in ast.walk(tree):
            # Check for global state
            if self.rules.get("check_globals", True):
                if isinstance(node, ast.Global):
                    issues.append({
                        "type": "global_state",
                        "line": node.lineno,
                        "severity": "warning",
                        "message": f"Global state at line {node.lineno}. Consider using classes or function parameters instead.",
                        "suggestion": "Refactor to avoid global variables. Pass values as function parameters."
                    })
            
            # Check for import organization
            if self.rules.get("check_imports", True):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    # Check for wildcard imports
                    if isinstance(node, ast.ImportFrom) and node.names and any(n.name == '*' for n in node.names):
                        issues.append({
                            "type": "wildcard_import",
                            "line": node.lineno,
                            "severity": "warning",
                            "message": f"Wildcard import (*) at line {node.lineno}. Be explicit about imports.",
                            "suggestion": "Import specific names instead of using * to avoid namespace pollution."
                        })
        
        # Check line length (need to iterate through lines separately)
        if self.rules.get("max_line_length", 0) > 0:
            max_len = self.rules["max_line_length"]
            for idx, line in enumerate(lines, start=1):
                # Skip comments and docstrings for strict length checking (or adjust as needed)
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and len(line) > max_len:
                    issues.append({
                        "type": "line_length",
                        "line": idx,
                        "severity": "info",
                        "message": f"Line {idx} is {len(line)} characters (max: {max_len}). Consider breaking into multiple lines.",
                        "suggestion": f"Split long line at {idx}. Consider using parentheses for multi-line expressions."
                    })
        
        # Check function complexity (basic)
        if self.rules.get("check_complexity", True):
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:  # Threshold for "complex" function
                        issues.append({
                            "type": "high_complexity",
                            "line": node.lineno,
                            "severity": "warning",
                            "message": f"Function '{node.name}' at line {node.lineno} has high complexity ({complexity}). Consider refactoring.",
                            "suggestion": "Break function into smaller, focused functions. Extract logical sections into separate methods."
                        })
        
        # Check naming conventions (basic)
        if self.rules.get("check_naming", True):
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('_') and not self._is_snake_case(node.name):
                        issues.append({
                            "type": "naming_convention",
                            "line": node.lineno,
                            "severity": "info",
                            "message": f"Function '{node.name}' at line {node.lineno} should use snake_case naming.",
                            "suggestion": f"Rename '{node.name}' to follow PEP 8 snake_case convention."
                        })
                elif isinstance(node, ast.ClassDef):
                    if not self._is_pascal_case(node.name):
                        issues.append({
                            "type": "naming_convention",
                            "line": node.lineno,
                            "severity": "info",
                            "message": f"Class '{node.name}' at line {node.lineno} should use PascalCase naming.",
                            "suggestion": f"Rename '{node.name}' to follow PEP 8 PascalCase convention."
                        })
        
        return issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """
        Calculate basic cyclomatic complexity.
        
        Args:
            node: Function AST node
            
        Returns:
            Complexity score
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case."""
        if not name:
            return False
        # Allow single underscores
        if name.startswith('_') and len(name) > 1:
            name = name[1:]
        return name.islower() or '_' in name and all(c.islower() or c.isdigit() or c == '_' for c in name)
    
    def _is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase."""
        if not name:
            return False
        # Allow single underscores
        if name.startswith('_') and len(name) > 1:
            name = name[1:]
        return name[0].isupper() and (name.replace('_', '').isalnum())
    
    def report_fixes(self, issues: List[Dict[str, Any]], file_path: str):
        """
        Print formatted report of code issues.
        
        Args:
            issues: List of issue dictionaries
            file_path: Path to file being reviewed
        """
        if not issues:
            return
        
        print("\n" + "=" * 60)
        print(f"CODE REVIEW: {file_path}")
        print("=" * 60)
        
        # Group by severity
        by_severity = {"error": [], "warning": [], "info": []}
        for issue in issues:
            severity = issue.get("severity", "info")
            by_severity.get(severity, []).append(issue)
        
        # Print by severity
        for severity in ["error", "warning", "info"]:
            if by_severity[severity]:
                severity_icon = {"error": "🔴", "warning": "⚠️", "info": "ℹ️"}
                print(f"\n{severity_icon.get(severity, '•')} {severity.upper()} ({len(by_severity[severity])}):")
                print("-" * 60)
                
                for issue in by_severity[severity]:
                    print(f"  Line {issue['line']}: {issue['message']}")
                    if 'suggestion' in issue:
                        print(f"    💡 Suggestion: {issue['suggestion']}")
        
        print("\n" + "=" * 60)
        
        # Log summary
        summary = {
            "file": file_path,
            "total_issues": len(issues),
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "timestamp": str(datetime.now())
        }
        
        # Store in agent's improvement notes for learning
        self.log_run(
            'code_review',
            json.dumps(summary, indent=2),
            success=True
        )
    
    def review_directory(self, directory: str = ".", pattern: str = "*.py", recursive: bool = True) -> Dict[str, Any]:
        """
        Review all Python files in a directory.
        
        Args:
            directory: Directory to scan
            pattern: File pattern (default: *.py)
            recursive: Whether to scan subdirectories
            
        Returns:
            Summary dictionary
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all matching files
        if recursive:
            files = list(dir_path.rglob(pattern))
        else:
            files = list(dir_path.glob(pattern))
        
        # Filter out common exclusions
        excluded_dirs = {'.git', '__pycache__', '.venv', 'venv', 'env', 'node_modules', '.skills', 'scripts'}
        files = [f for f in files if not any(excluded in f.parts for excluded in excluded_dirs)]
        
        results = {
            "directory": directory,
            "files_reviewed": 0,
            "files_with_issues": 0,
            "total_issues": 0,
            "files": []
        }
        
        for file_path in files:
            try:
                self.run_task(str(file_path))
                file_issues = len([r for r in self.review_history if r["file"] == str(file_path)])
                
                results["files_reviewed"] += 1
                if file_issues > 0:
                    results["files_with_issues"] += 1
                    results["total_issues"] += file_issues
                
                results["files"].append({
                    "path": str(file_path),
                    "issues": file_issues
                })
                
            except Exception as e:
                self.history.append(f"Error reviewing {file_path}: {str(e)}")
                results["files"].append({
                    "path": str(file_path),
                    "error": str(e)
                })
        
        return results
    
    def get_review_stats(self) -> Dict[str, Any]:
        """Get code review statistics."""
        base_stats = self.get_stats()
        
        return {
            **base_stats,
            "code_analyzed": self.code_analyzed,
            "violations_found": self.violations_found,
            "reviews_performed": len(self.review_history),
            "average_issues_per_file": (
                self.violations_found / max(self.code_analyzed, 1)
            )
        }


# Example usage and testing
def main():
    """Main entry point for code reviewer when run as script."""
    print("=" * 60)
    print("CODE REVIEWER AGENT - v1")
    print("=" * 60)
    print()
    
    # Create code reviewer agent
    config = AgentConfig(
        skills_dir='./.skills',
        max_retries=2,
        verbose=True
    )
    
    reviewer = CodeReviewer(config=config)
    print(f"🤖 Code Reviewer initialized: {reviewer.name}")
    print(f"📋 Goal: {reviewer.goal}")
    print()
    
    # Test with a file if it exists
    test_file = "./test.py"
    
    if os.path.exists(test_file):
        print(f"Reviewing {test_file}...")
        success = reviewer.run_task(test_file)
        
        if success:
            print(f"✅ Review complete")
        else:
            print(f"❌ Review failed")
    else:
        print(f"⚠️  Test file not found: {test_file}")
        print("Creating sample test file for demonstration...")
        
        # Create a sample file with issues
        sample_code = """# Sample code with issues for testing
import os
from some_module import *

global_variable = "bad"

def badFunctionName():
    x = 1
    if x > 0:
        if x < 10:
            if x == 5:
                if x != 3:
                    return "too nested"
    return "done"

class badClassName:
    def method(self):
        very_long_line_that_exceeds_the_maximum_recommended_line_length_and_should_be_split_into_multiple_lines = "example"
        pass
"""
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(sample_code)
        
        print(f"✅ Created {test_file}")
        print(f"Reviewing {test_file}...")
        success = reviewer.run_task(test_file)
    
    print()
    print("-" * 60)
    print("\n📊 Reviewer Statistics:")
    stats = reviewer.get_review_stats()
    for key, value in stats.items():
        if key not in ['recent_notes']:
            print(f"  {key}: {value}")
    
    print()
    print(f"✅ Code Reviewer ready. Skill log: {reviewer.skill_log}")


if __name__ == '__main__':
    import sys
    
    # Check if running in headless mode (for hub)
    headless = '--headless' in sys.argv or os.environ.get('HEADLESS', '').lower() == 'true'
    
    if headless:
        # Headless mode - output JSON only
        config = AgentConfig(verbose=False)
        reviewer = CodeReviewer(config=config)
        
        # Read project directory from environment or use current
        project_dir = os.environ.get('PROJECT_DIR', '.')
        target_file = os.environ.get('REVIEW_FILE', './test.py')
        
        success = reviewer.run_task(target_file)
        
        # Output JSON for hub
        output = {
            'agent': 'reviewer',
            'timestamp': str(datetime.now()),
            'success': success,
            'violations_found': reviewer.violations_found,
            'code_analyzed': reviewer.code_analyzed
        }
        
        if reviewer.review_history:
            output['last_review'] = reviewer.review_history[-1]
        
        print(json.dumps(output, indent=2))
        exit(0 if success else 1)
    else:
        # Interactive mode - run main function
        main()

