#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Standalone Requirements Analyzer
Analyzes The Gatekeeper Omega system to determine what's needed for standalone deployment
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

# Fix Windows encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")


class StandaloneAnalyzer:
    """Analyze system for standalone deployment requirements"""

    def __init__(self, root_path: Path):
        self.root = root_path
        self.analysis = {
            "python_files": [],
            "dependencies": set(),
            "config_files": [],
            "data_directories": [],
            "missing_directories": [],
            "external_services": set(),
            "required_models": [],
            "startup_scripts": [],
            "core_modules": [],
        }

    def analyze_directory_structure(self) -> Dict:
        """Analyze current vs required directory structure"""
        required_dirs = {
            "data": ["credentials", "sessions", "logs", "cache", "models"],
            "config": ["profiles", "auth", "system"],
            "models": ["tts", "speech", "llm", "embeddings"],
            "output": ["audio", "reports", "exports"],
            "backups": ["config", "data", "sessions"],
            "logs": ["system", "security", "performance"],
            "static": ["audio", "icons", "scripts", "css"],
            "templates": ["web", "reports"],
        }

        existing = set()
        missing = []

        for root, dirs, files in os.walk(self.root):
            rel_path = Path(root).relative_to(self.root)
            if rel_path != Path("."):
                existing.add(str(rel_path))

        for parent, children in required_dirs.items():
            parent_path = self.root / parent
            if not parent_path.exists():
                missing.append(parent)
            for child in children:
                child_path = parent_path / child
                if not child_path.exists():
                    missing.append(f"{parent}/{child}")

        return {"existing": list(existing)[:20], "missing": missing}

    def analyze_python_modules(self) -> Dict:
        """Analyze Python modules and categorize by function"""
        categories = defaultdict(list)

        core_keywords = ["omega_core", "gate_", "gatekeeper_"]
        auth_keywords = ["auth", "credential", "login", "session"]
        ai_keywords = ["voice", "speech", "tts", "llm", "model"]
        system_keywords = ["monitor", "system", "resource", "health"]
        integration_keywords = ["api", "integration", "bridge", "developer"]

        for py_file in self.root.rglob("*.py"):
            if "Organized_Files" in str(py_file) or "__pycache__" in str(py_file):
                continue

            name = py_file.stem

            if any(kw in name for kw in core_keywords):
                categories["core"].append(py_file.name)
            elif any(kw in name for kw in auth_keywords):
                categories["authentication"].append(py_file.name)
            elif any(kw in name for kw in ai_keywords):
                categories["ai_ml"].append(py_file.name)
            elif any(kw in name for kw in system_keywords):
                categories["system_monitoring"].append(py_file.name)
            elif any(kw in name for kw in integration_keywords):
                categories["integrations"].append(py_file.name)
            elif "test_" in name:
                categories["testing"].append(py_file.name)
            else:
                categories["utilities"].append(py_file.name)

        return {k: v[:10] for k, v in categories.items()}  # Limit to 10 per category

    def analyze_dependencies(self) -> Dict:
        """Analyze all dependencies from requirements files"""
        dependencies = {
            "core": set(),
            "ai_ml": set(),
            "web": set(),
            "dev": set(),
            "optional": set(),
        }

        # Core dependencies
        core_deps = [
            "websockets",
            "aiofiles",
            "aiohttp",
            "psutil",
            "cryptography",
            "python-dotenv",
            "structlog",
        ]

        # AI/ML dependencies
        ai_deps = ["torch", "transformers", "TTS", "faster-whisper", "speechbrain"]

        # Web dependencies
        web_deps = ["fastapi", "uvicorn", "jinja2", "flask"]

        # Dev dependencies
        dev_deps = ["pytest", "pytest-asyncio", "black", "ruff", "mypy"]

        # Read all requirements files
        for req_file in self.root.glob("requirements*.txt"):
            try:
                content = req_file.read_text()
                for line in content.split("\n"):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    # Extract package name
                    pkg = line.split("==")[0].split(">=")[0].split("<=")[0].split("<")[0]
                    pkg = pkg.strip()

                    if pkg in core_deps:
                        dependencies["core"].add(line)
                    elif pkg in ai_deps:
                        dependencies["ai_ml"].add(line)
                    elif pkg in web_deps:
                        dependencies["web"].add(line)
                    elif pkg in dev_deps:
                        dependencies["dev"].add(line)
                    else:
                        dependencies["optional"].add(line)
            except Exception:
                continue

        return {k: sorted(list(v))[:15] for k, v in dependencies.items()}

    def analyze_external_services(self) -> List[str]:
        """Identify required external services"""
        services = {
            "Required": [
                "NVIDIA GPU (optional but recommended for AI acceleration)",
                "Internet connection (for initial setup and model downloads)",
            ],
            "Optional": [
                "GitHub (for integration features)",
                "Gmail API (for email integration)",
                "Redis (for caching)",
                "PostgreSQL (for data persistence)",
            ],
        }
        return services

    def identify_core_modules(self) -> List[str]:
        """Identify absolutely essential modules for standalone operation"""
        core_files = [
            "omega_core.py",
            "gate_admin_auth.py",
            "resource_controller.py",
            "run_comprehensive_tests.py",
        ]

        found = []
        for core_file in core_files:
            if (self.root / core_file).exists():
                found.append(core_file)

        return found

    def create_startup_script(self) -> str:
        """Generate startup script content"""
        script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
The Gatekeeper Omega - Standalone Launcher
Initializes and starts the complete system
\"\"\"

import sys
import subprocess
from pathlib import Path

def check_python_version():
    if sys.version_info < (3, 9):
        print("Error: Python 3.9+ required")
        sys.exit(1)

def check_dependencies():
    try:
        import torch
        import transformers
        import websockets
        import aiofiles
        print("✓ Core dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False

def initialize_directories():
    dirs = [
        "data/credentials", "data/sessions", "data/logs", "data/cache",
        "config/profiles", "config/auth",
        "models/tts", "models/speech", "models/llm",
        "output/audio", "output/reports",
        "backups", "logs"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✓ Directories initialized")

def setup_admin():
    from gate_admin_auth import GateAdminAuth
    auth = GateAdminAuth()
    if not auth.get_status()["admin_configured"]:
        print("Setting up GATE administrator...")
        result = auth.setup_admin()
        print(f"✓ Administrator configured: {result['username']}")

def start_system():
    print("\\n" + "="*70)
    print("  THE GATEKEEPER OMEGA - STARTING")
    print("="*70 + "\\n")

    check_python_version()
    if not check_dependencies():
        print("\\nInstall dependencies with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    initialize_directories()
    setup_admin()

    print("\\n✓ System initialized successfully!")
    print("\\nNext steps:")
    print("  1. Configure resources: python resource_controller.py")
    print("  2. Run tests: python run_comprehensive_tests.py")
    print("  3. Start main system: python omega_core.py")

if __name__ == "__main__":
    start_system()
"""
        return script

    def run_analysis(self) -> Dict:
        """Run complete standalone analysis"""
        print("=" * 70)
        print("  STANDALONE DEPLOYMENT ANALYZER")
        print("=" * 70 + "\n")

        print("1. Analyzing directory structure...")
        dir_analysis = self.analyze_directory_structure()

        print("2. Analyzing Python modules...")
        module_analysis = self.analyze_python_modules()

        print("3. Analyzing dependencies...")
        dep_analysis = self.analyze_dependencies()

        print("4. Identifying external services...")
        service_analysis = self.analyze_external_services()

        print("5. Identifying core modules...")
        core_modules = self.identify_core_modules()

        print("\n" + "=" * 70)
        print("  ANALYSIS COMPLETE")
        print("=" * 70 + "\n")

        # Summary
        print("📁 DIRECTORY STRUCTURE")
        print(f"  Missing directories: {len(dir_analysis['missing'])}")
        if dir_analysis["missing"]:
            print("\n  Required directories to create:")
            for d in dir_analysis["missing"][:10]:
                print(f"    • {d}")

        print("\n\n🐍 PYTHON MODULES")
        for category, files in module_analysis.items():
            print(f"  {category}: {len(files)} files")
            for f in files[:3]:
                print(f"    • {f}")

        print("\n\n📦 DEPENDENCIES")
        total_deps = sum(len(v) for v in dep_analysis.values())
        print(f"  Total unique dependencies: {total_deps}")
        for category, deps in dep_analysis.items():
            print(f"  {category}: {len(deps)}")

        print("\n\n🌐 EXTERNAL SERVICES")
        for category, services in service_analysis.items():
            print(f"  {category}:")
            for svc in services:
                print(f"    • {svc}")

        print("\n\n⭐ CORE MODULES FOUND")
        for module in core_modules:
            print(f"  ✓ {module}")

        # Save detailed analysis
        analysis_data = {
            "directories": dir_analysis,
            "modules": {k: list(v) for k, v in module_analysis.items()},
            "dependencies": {k: list(v) for k, v in dep_analysis.items()},
            "services": service_analysis,
            "core_modules": core_modules,
        }

        return analysis_data


def main():
    root = Path(__file__).parent
    analyzer = StandaloneAnalyzer(root)
    analysis = analyzer.run_analysis()

    # Save analysis
    output_file = root / "STANDALONE_ANALYSIS.json"
    with open(output_file, "w") as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"\n\n📄 Full analysis saved to: {output_file}")

    # Create startup script
    startup_script = root / "start_gatekeeper.py"
    with open(startup_script, "w", encoding="utf-8") as f:
        f.write(analyzer.create_startup_script())
    print(f"Startup script created: {startup_script}")

    # Create missing directories
    print("\n\n📁 Creating missing directories...")
    missing = analysis["directories"]["missing"]
    for dir_path in missing:
        full_path = root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created: {dir_path}")

    print("\n\n" + "=" * 70)
    print("  STANDALONE SETUP COMPLETE")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Review analysis: STANDALONE_ANALYSIS.json")
    print("  2. Install dependencies: pip install -r requirements.txt")
    print("  3. Start system: python start_gatekeeper.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
