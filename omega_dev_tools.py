"""
Omega Development Tools Integration
Automates code quality, testing, and development workflows
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class OmegaDevTools:
    """
    Integrates development tools for code quality and automation
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tools = {
            'pytest': 'Testing framework',
            'black': 'Code formatter',
            'flake8': 'Linting',
            'mypy': 'Type checking',
            'pip': 'Package management'
        }

    def run_tests(self, path: str = ".") -> Tuple[bool, str]:
        """Run pytest tests"""
        try:
            result = subprocess.run(
                ['pytest', path, '-v'],
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, f"Error running tests: {e}"

    def format_code(self, file_path: str) -> Tuple[bool, str]:
        """Format code with black"""
        try:
            result = subprocess.run(
                ['black', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, f"Error formatting: {e}"

    def lint_code(self, path: str = ".") -> List[Dict]:
        """Lint code with flake8"""
        issues = []
        try:
            result = subprocess.run(
                ['flake8', path],
                capture_output=True,
                text=True,
                timeout=30
            )

            for line in result.stdout.split('\n'):
                if line.strip():
                    issues.append({'message': line})
        except Exception as e:
            issues.append({'error': str(e)})

        return issues

    def check_types(self, file_path: str) -> List[Dict]:
        """Check types with mypy"""
        issues = []
        try:
            result = subprocess.run(
                ['mypy', file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            for line in result.stdout.split('\n'):
                if 'error:' in line:
                    issues.append({'message': line})
        except Exception as e:
            issues.append({'error': str(e)})

        return issues

    def run_full_check(self, file_path: str) -> Dict:
        """Run all checks on a file"""
        return {
            'formatting': self.format_code(file_path),
            'linting': self.lint_code(file_path),
            'type_checking': self.check_types(file_path)
        }

if __name__ == '__main__':
    tools = OmegaDevTools()
    print("Omega Development Tools Ready")
    print("Available:", list(tools.tools.keys()))
