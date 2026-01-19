"""
Omega Package Scanner & Integrator
Scans all installed packages for free extras, CLI tools, and utilities
Analyzes them for syntax errors and integrates into Omega
"""

import os
import sys
import json
import subprocess
import ast
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.metadata
import warnings

warnings.filterwarnings("ignore")


class OmegaPackageScanner:
    """
    Scans installed packages for free extras and integration opportunities
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"
        self.scan_results = {
            "packages": {},
            "cli_tools": [],
            "free_extras": [],
            "syntax_errors": [],
            "integration_opportunities": [],
        }

    def get_all_installed_packages(self) -> Dict[str, Dict]:
        """Get comprehensive info about all installed packages"""
        print("\n[*] Scanning all installed packages...")

        packages = {}

        try:
            for dist in importlib.metadata.distributions():
                name = dist.metadata["Name"]
                version = dist.metadata["Version"]

                package_info = {
                    "version": version,
                    "summary": dist.metadata.get("Summary", ""),
                    "home_page": dist.metadata.get("Home-page", ""),
                    "author": dist.metadata.get("Author", ""),
                    "license": dist.metadata.get("License", ""),
                    "requires": [str(r) for r in (dist.metadata.get_all("Requires-Dist") or [])],
                    "entry_points": {},
                    "cli_scripts": [],
                }

                try:
                    entry_points = dist.entry_points
                    if hasattr(entry_points, "select"):
                        console_scripts = entry_points.select(group="console_scripts")
                    else:
                        console_scripts = entry_points.get("console_scripts", [])

                    for ep in console_scripts:
                        package_info["cli_scripts"].append({"name": ep.name, "value": ep.value})
                except:
                    pass

                packages[name] = package_info

        except Exception as e:
            print(f"[!] Error scanning packages: {e}")

        print(f"[+] Found {len(packages)} installed packages")
        return packages

    def identify_cli_tools(self, packages: Dict) -> List[Dict]:
        """Identify CLI tools from packages"""
        print("\n[*] Identifying CLI tools and extras...")

        cli_tools = []

        for pkg_name, pkg_info in packages.items():
            if pkg_info["cli_scripts"]:
                for script in pkg_info["cli_scripts"]:
                    cli_tools.append(
                        {
                            "package": pkg_name,
                            "tool_name": script["name"],
                            "entry_point": script["value"],
                            "category": self._categorize_tool(pkg_name, script["name"]),
                        }
                    )

        print(f"[+] Found {len(cli_tools)} CLI tools")
        return cli_tools

    def _categorize_tool(self, package: str, tool: str) -> str:
        """Categorize tool by function"""
        categories = {
            "ai": ["langchain", "openai", "anthropic", "llama", "huggingface"],
            "data": ["pandas", "numpy", "jupyter", "notebook"],
            "web": ["streamlit", "gradio", "fastapi", "flask"],
            "dev": ["pip", "pytest", "black", "flake8", "mypy"],
            "monitoring": ["prometheus", "sentry"],
            "security": ["cryptography", "jwt"],
            "system": ["psutil"],
        }

        package_lower = package.lower()
        tool_lower = tool.lower()

        for category, keywords in categories.items():
            if any(kw in package_lower or kw in tool_lower for kw in keywords):
                return category

        return "utility"

    def discover_free_extras(self, packages: Dict) -> List[Dict]:
        """Discover free extras and utilities"""
        print("\n[*] Discovering free extras and utilities...")

        free_extras = []

        extras_map = {
            "langchain": {
                "tools": ["langchain-cli", "langsmith"],
                "features": ["RAG templates", "Agent templates", "LangServe deployment"],
            },
            "gradio": {
                "tools": ["gradio CLI"],
                "features": ["Themes", "Blocks system", "Public sharing"],
            },
            "streamlit": {
                "tools": ["streamlit CLI"],
                "features": ["Cloud deployment", "Components", "Secrets management"],
            },
            "openai": {
                "tools": ["openai CLI"],
                "features": ["Embeddings", "Assistants API", "Vision API"],
            },
            "transformers": {
                "tools": ["transformers-cli"],
                "features": ["Model Hub", "Pipelines", "Tokenizers"],
            },
            "jupyter": {
                "tools": ["jupyter", "jupyter-lab", "jupyter-notebook"],
                "features": ["Extensions", "Kernels", "Widgets"],
            },
            "pytest": {"tools": ["pytest"], "features": ["Fixtures", "Plugins", "Coverage"]},
            "pip": {
                "tools": ["pip", "pip-compile"],
                "features": ["Cache", "Wheel building", "Requirements management"],
            },
        }

        for pkg_name, pkg_info in packages.items():
            pkg_lower = pkg_name.lower()

            for extra_pkg, extra_info in extras_map.items():
                if extra_pkg in pkg_lower:
                    free_extras.append(
                        {
                            "package": pkg_name,
                            "version": pkg_info["version"],
                            "tools": extra_info.get("tools", []),
                            "features": extra_info.get("features", []),
                            "home_page": pkg_info.get("home_page", ""),
                        }
                    )

        print(f"[+] Found {len(free_extras)} packages with free extras")
        return free_extras

    def check_syntax_errors(self) -> List[Dict]:
        """Check all Omega Python files for syntax errors"""
        print("\n[*] Checking Omega files for syntax errors...")

        errors = []
        python_files = list(self.project_root.glob("omega*.py"))

        for py_file in python_files:
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    code = f.read()

                try:
                    ast.parse(code)
                    print(f"   [+] {py_file.name} - OK")
                except SyntaxError as e:
                    error_info = {
                        "file": py_file.name,
                        "line": e.lineno,
                        "offset": e.offset,
                        "message": e.msg,
                        "text": e.text,
                    }
                    errors.append(error_info)
                    print(f"   [!] {py_file.name} - SYNTAX ERROR at line {e.lineno}")

            except Exception as e:
                print(f"   [!] Error reading {py_file.name}: {e}")

        if not errors:
            print(f"[+] All {len(python_files)} Omega files passed syntax check")
        else:
            print(f"[!] Found {len(errors)} files with syntax errors")

        return errors

    def identify_integration_opportunities(
        self, cli_tools: List[Dict], free_extras: List[Dict]
    ) -> List[Dict]:
        """Identify how tools can be integrated into Omega"""
        print("\n[*] Identifying integration opportunities...")

        opportunities = []

        ai_tools = [t for t in cli_tools if t["category"] == "ai"]
        if ai_tools:
            opportunities.append(
                {
                    "category": "AI/ML Enhancement",
                    "tools": [t["tool_name"] for t in ai_tools],
                    "integration": "Extend omega_intelligent_chatbot.py with additional models and providers",
                    "priority": "HIGH",
                }
            )

        data_tools = [t for t in cli_tools if t["category"] == "data"]
        if data_tools:
            opportunities.append(
                {
                    "category": "Data Analysis",
                    "tools": [t["tool_name"] for t in data_tools],
                    "integration": "Create omega_data_analyzer.py for data processing and visualization",
                    "priority": "MEDIUM",
                }
            )

        web_tools = [t for t in cli_tools if t["category"] == "web"]
        if web_tools:
            opportunities.append(
                {
                    "category": "Web Interface",
                    "tools": [t["tool_name"] for t in web_tools],
                    "integration": "Already integrated in chatbot, can expand with dashboards",
                    "priority": "LOW",
                }
            )

        dev_tools = [t for t in cli_tools if t["category"] == "dev"]
        if dev_tools:
            opportunities.append(
                {
                    "category": "Development Tools",
                    "tools": [t["tool_name"] for t in dev_tools],
                    "integration": "Create omega_dev_tools.py for code quality and testing automation",
                    "priority": "HIGH",
                }
            )

        monitoring_tools = [t for t in cli_tools if t["category"] == "monitoring"]
        if monitoring_tools:
            opportunities.append(
                {
                    "category": "Monitoring Enhancement",
                    "tools": [t["tool_name"] for t in monitoring_tools],
                    "integration": "Extend omega_continuous_monitor.py with advanced metrics",
                    "priority": "MEDIUM",
                }
            )

        print(f"[+] Identified {len(opportunities)} integration opportunities")
        return opportunities

    def generate_integration_code(self, opportunities: List[Dict]) -> Dict[str, str]:
        """Generate integration code for identified opportunities"""
        print("\n[*] Generating integration code...")

        integrations = {}

        for opp in opportunities:
            if opp["priority"] == "HIGH":
                if "AI/ML" in opp["category"]:
                    integrations["omega_ai_extras.py"] = self._generate_ai_extras_code(opp)
                elif "Development" in opp["category"]:
                    integrations["omega_dev_tools.py"] = self._generate_dev_tools_code(opp)

        print(f"[+] Generated {len(integrations)} integration modules")
        return integrations

    def _generate_ai_extras_code(self, opportunity: Dict) -> str:
        """Generate AI extras integration code"""
        return '''"""
Omega AI Extras Integration
Integrates additional AI/ML capabilities from installed packages
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

class OmegaAIExtras:
    """
    Provides access to additional AI/ML tools and features
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.available_tools = {}
        self._discover_tools()

    def _discover_tools(self):
        """Discover available AI tools"""
        tools_to_check = [
            'langchain-cli',
            'transformers-cli',
            'openai',
            'huggingface-cli'
        ]

        for tool in tools_to_check:
            if self._check_tool_available(tool):
                self.available_tools[tool] = True

    def _check_tool_available(self, tool: str) -> bool:
        """Check if tool is available"""
        try:
            result = subprocess.run(
                [tool, '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def get_available_models(self, provider: str = 'all') -> List[str]:
        """Get list of available AI models"""
        models = []

        openai_models = [
            'gpt-4',
            'gpt-4-turbo-preview',
            'gpt-3.5-turbo',
            'text-embedding-ada-002'
        ]

        anthropic_models = [
            'claude-3-opus-20240229',
            'claude-3-sonnet-20240229',
            'claude-3-haiku-20240307'
        ]

        hf_models = [
            'bert-base-uncased',
            'distilbert-base-uncased',
            'sentence-transformers/all-MiniLM-L6-v2',
            'facebook/bart-large-cnn'
        ]

        if provider == 'all':
            models.extend(openai_models)
            models.extend(anthropic_models)
            models.extend(hf_models)
        elif provider == 'openai':
            models = openai_models
        elif provider == 'anthropic':
            models = anthropic_models
        elif provider == 'huggingface':
            models = hf_models

        return models

    def get_free_features(self) -> Dict[str, List[str]]:
        """Get free features available in installed packages"""
        return {
            'langchain': [
                'RAG templates',
                'Agent templates',
                'Memory systems',
                'Tool integrations',
                'LangSmith debugging (free tier)'
            ],
            'transformers': [
                'Model Hub access (50K+ models)',
                'Pipelines for common tasks',
                'Tokenizers',
                'ONNX export',
                'Quantization'
            ],
            'gradio': [
                'Public sharing links',
                'Custom themes',
                'Authentication',
                'File uploads',
                'Real-time updates'
            ],
            'streamlit': [
                'Session state',
                'Caching decorators',
                'Custom components',
                'Secrets management',
                'Multi-page apps'
            ]
        }

    def execute_tool(self, tool: str, args: List[str]) -> str:
        """Execute an AI tool with arguments"""
        if tool not in self.available_tools:
            return f"Tool '{tool}' not available"

        try:
            result = subprocess.run(
                [tool] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            return f"Error executing {tool}: {e}"

if __name__ == '__main__':
    extras = OmegaAIExtras()
    print("Available AI/ML tools:", list(extras.available_tools.keys()))
    print("\\nFree features:", json.dumps(extras.get_free_features(), indent=2))
'''

    def _generate_dev_tools_code(self, opportunity: Dict) -> str:
        """Generate dev tools integration code"""
        return '''"""
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

            for line in result.stdout.split('\\n'):
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

            for line in result.stdout.split('\\n'):
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
'''

    def run_complete_scan(self):
        """Run complete package scan and integration"""
        print("\n" + "=" * 70)
        print("OMEGA PACKAGE SCANNER & INTEGRATOR")
        print("=" * 70)

        packages = self.get_all_installed_packages()
        self.scan_results["packages"] = packages

        cli_tools = self.identify_cli_tools(packages)
        self.scan_results["cli_tools"] = cli_tools

        free_extras = self.discover_free_extras(packages)
        self.scan_results["free_extras"] = free_extras

        syntax_errors = self.check_syntax_errors()
        self.scan_results["syntax_errors"] = syntax_errors

        opportunities = self.identify_integration_opportunities(cli_tools, free_extras)
        self.scan_results["integration_opportunities"] = opportunities

        integrations = self.generate_integration_code(opportunities)

        results_file = self.project_root / "omega_package_scan_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.scan_results, f, indent=2)

        for filename, code in integrations.items():
            filepath = self.project_root / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"[+] Created {filename}")

        print("\n" + "=" * 70)
        print("SCAN COMPLETE")
        print("=" * 70)
        print(f"Total Packages: {len(packages)}")
        print(f"CLI Tools Found: {len(cli_tools)}")
        print(f"Free Extras: {len(free_extras)}")
        print(f"Syntax Errors: {len(syntax_errors)}")
        print(f"Integration Opportunities: {len(opportunities)}")
        print(f"Integration Modules Created: {len(integrations)}")
        print(f"\nResults saved to: omega_package_scan_results.json")
        print("=" * 70 + "\n")

        return self.scan_results


if __name__ == "__main__":
    scanner = OmegaPackageScanner()
    scanner.run_complete_scan()
