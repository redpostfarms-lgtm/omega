#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GATE Comprehensive Dependency Installer
Installs ALL dependencies - required AND optional
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")


class GateInstaller:
    """Comprehensive installer for all GATE dependencies"""

    def __init__(self):
        self.root = Path(__file__).parent
        self.dependencies = {
            "core": {
                "description": "Core system dependencies (REQUIRED)",
                "packages": [
                    "websockets>=12.0",
                    "aiofiles",
                    "aiohttp",
                    "psutil>=5.9.0",
                    "cryptography>=41.0.0",
                    "python-dotenv>=1.0.0",
                    "structlog>=23.2.0",
                    "prometheus-client>=0.19.0",
                ],
                "required": True
            },
            "ai_ml": {
                "description": "AI/ML dependencies (REQUIRED for AI features)",
                "packages": [
                    "torch==2.5.1",
                    "torchaudio==2.5.1",
                    "transformers>=4.21.0,<4.36.0",
                    "TTS==0.22.0",
                    "faster-whisper",
                    "speechbrain",
                    "SpeechRecognition",
                ],
                "required": True
            },
            "audio": {
                "description": "Audio processing (REQUIRED for voice)",
                "packages": [
                    "sounddevice",
                    "soundfile",
                    "librosa",
                    "noisereduce",
                    "pydub",
                    "pyaudio>=0.2.11",
                    "webrtcvad",
                ],
                "required": True
            },
            "llm_apis": {
                "description": "LLM API clients (OPTIONAL but recommended)",
                "packages": [
                    "openai>=1.0.0",
                    "anthropic>=0.7.0",
                    "google-generativeai",
                ],
                "required": False
            },
            "development": {
                "description": "Development tools (OPTIONAL)",
                "packages": [
                    "pytest>=7.4.0",
                    "pytest-asyncio>=0.21.0",
                    "pytest-cov>=4.1.0",
                    "pytest-mock>=3.12.0",
                    "black>=23.0.0",
                    "ruff>=0.1.0",
                    "mypy>=1.0.0",
                    "autoflake",
                ],
                "required": False
            },
            "data_science": {
                "description": "Data science & ML tools (OPTIONAL)",
                "packages": [
                    "pandas>=1.3.0",
                    "numpy",
                    "scipy",
                    "matplotlib>=3.5.0",
                    "plotly>=5.0.0",
                    "datasets>=2.0.0",
                    "accelerate>=0.20.0",
                ],
                "required": False
            },
            "web": {
                "description": "Web frameworks (OPTIONAL)",
                "packages": [
                    "fastapi",
                    "uvicorn[standard]",
                    "jinja2",
                    "beautifulsoup4>=4.12.0",
                    "requests>=2.28.0",
                ],
                "required": False
            },
            "database": {
                "description": "Database connectors (OPTIONAL)",
                "packages": [
                    "redis>=4.0.0",
                    "sqlalchemy",
                    "psycopg2-binary",
                ],
                "required": False
            },
            "security": {
                "description": "Security & auth tools (OPTIONAL)",
                "packages": [
                    "pyjwt[crypto]>=2.8.0",
                    "passlib[bcrypt]",
                    "python-jose[cryptography]",
                ],
                "required": False
            },
            "hardware": {
                "description": "Hardware control (OPTIONAL)",
                "packages": [
                    "pyautogui>=0.9.54",
                    "pynput>=1.7.6",
                    "WMI; platform_system=='Windows'",
                    "openrgb-python>=0.2.0",
                ],
                "required": False
            },
            "image_processing": {
                "description": "Image & vision (OPTIONAL)",
                "packages": [
                    "Pillow>=10.0.0",
                    "opencv-python",
                ],
                "required": False
            },
            "nlp": {
                "description": "Advanced NLP (OPTIONAL)",
                "packages": [
                    "outlines>=0.0.1",
                    "pydantic>=2.0.0",
                    "mauve-text>=0.1.0",
                    "tqdm>=4.64.0",
                ],
                "required": False
            },
            "ide_integration": {
                "description": "IDE integrations (OPTIONAL)",
                "packages": [
                    "jupyterlab",
                    "ipython",
                    "python-language-server[all]",
                ],
                "required": False
            }
        }

    def run_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """Execute pip command"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                encoding="utf-8",
                errors="replace"
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def install_package(self, package: str) -> Tuple[bool, str]:
        """Install single package"""
        print(f"  Installing {package}...")

        cmd = [sys.executable, "-m", "pip", "install", package]
        success, output = self.run_command(cmd)

        if success:
            print(f"    ✓ Installed {package}")
        else:
            print(f"    ✗ Failed to install {package}")
            if "error" in output.lower()[:200]:
                print(f"      Error: {output[:200]}")

        return success, output

    def install_category(self, category: str, packages: List[str]) -> Dict:
        """Install all packages in a category"""
        results = {
            "total": len(packages),
            "succeeded": 0,
            "failed": 0,
            "errors": []
        }

        for package in packages:
            success, output = self.install_package(package)

            if success:
                results["succeeded"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "package": package,
                    "error": output[:200]
                })

        return results

    def install_all(self, include_optional: bool = False):
        """Install all dependencies"""
        print("\n" + "=" * 70)
        print("  GATE COMPREHENSIVE DEPENDENCY INSTALLER")
        print("=" * 70 + "\n")

        total_installed = 0
        total_failed = 0

        for category, info in self.dependencies.items():
            # Skip optional if not requested
            if not info["required"] and not include_optional:
                print(f"\n[SKIP] {category}: {info['description']}")
                continue

            required_text = "REQUIRED" if info["required"] else "OPTIONAL"
            print(f"\n[{required_text}] {category}: {info['description']}")
            print("-" * 70)

            results = self.install_category(category, info["packages"])

            print(f"\n  Results: {results['succeeded']}/{results['total']} succeeded, {results['failed']} failed")

            total_installed += results["succeeded"]
            total_failed += results["failed"]

            if results["errors"]:
                print(f"  Errors:")
                for error in results["errors"][:3]:  # Show first 3 errors
                    print(f"    - {error['package']}: {error['error'][:100]}")

        print("\n" + "=" * 70)
        print("  INSTALLATION COMPLETE")
        print("=" * 70)
        print(f"\nTotal packages installed: {total_installed}")
        print(f"Total packages failed: {total_failed}")

        if total_failed == 0:
            print("\n✓ All packages installed successfully!")
        else:
            print(f"\n⚠  {total_failed} packages failed to install")
            print("  Review errors above for details")

        print("\n" + "=" * 70 + "\n")

    def interactive_install(self):
        """Interactive installation wizard"""
        print("\n" + "=" * 70)
        print("  GATE INTERACTIVE INSTALLER")
        print("=" * 70 + "\n")

        print("This installer will set up ALL dependencies for GATE.\n")

        print("Dependency Categories:")
        for i, (category, info) in enumerate(self.dependencies.items(), 1):
            required_text = "REQUIRED" if info["required"] else "OPTIONAL"
            print(f"  {i}. [{required_text}] {category}")
            print(f"     {info['description']}")
            print(f"     Packages: {len(info['packages'])}\n")

        print("\nInstallation Options:")
        print("  1. Install REQUIRED dependencies only (recommended for quick start)")
        print("  2. Install ALL dependencies (required + optional)")
        print("  3. Custom selection (choose categories)")
        print("  4. Exit")

        choice = input("\nChoice (1-4): ").strip()

        if choice == "1":
            print("\nInstalling REQUIRED dependencies only...")
            self.install_all(include_optional=False)

        elif choice == "2":
            print("\nInstalling ALL dependencies (this may take a while)...")
            self.install_all(include_optional=True)

        elif choice == "3":
            print("\nCustom selection:")
            print("Enter category numbers separated by spaces (e.g., '1 2 5')")
            print("Available categories:")
            categories_list = list(self.dependencies.keys())
            for i, cat in enumerate(categories_list, 1):
                print(f"  {i}. {cat}")

            selection = input("\nCategories to install: ").strip().split()

            for num in selection:
                try:
                    idx = int(num) - 1
                    if 0 <= idx < len(categories_list):
                        category = categories_list[idx]
                        info = self.dependencies[category]

                        print(f"\n[{category}] {info['description']}")
                        print("-" * 70)

                        self.install_category(category, info["packages"])

                except (ValueError, IndexError):
                    print(f"Invalid selection: {num}")

        elif choice == "4":
            print("\nExiting installer...")
            return

    def verify_installation(self) -> Dict:
        """Verify which dependencies are installed"""
        print("\n" + "=" * 70)
        print("  VERIFYING INSTALLATIONS")
        print("=" * 70 + "\n")

        verification = {}

        for category, info in self.dependencies.items():
            print(f"\n{category}:")

            verified = []
            missing = []

            for package_spec in info["packages"]:
                # Extract package name (remove version specifiers)
                package_name = package_spec.split(">")[0].split("=")[0].split("<")[0].split("[")[0].strip()

                # Handle platform-specific packages
                if "platform_system" in package_spec:
                    if sys.platform != "win32" and "Windows" in package_spec:
                        continue

                try:
                    __import__(package_name.replace("-", "_"))
                    verified.append(package_name)
                    print(f"  ✓ {package_name}")
                except ImportError:
                    missing.append(package_name)
                    print(f"  ✗ {package_name} (not installed)")

            verification[category] = {
                "verified": verified,
                "missing": missing,
                "total": len(info["packages"]),
                "installed": len(verified)
            }

        return verification


def main():
    """Main entry point"""
    installer = GateInstaller()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            installer.install_all(include_optional=True)
        elif sys.argv[1] == "--required":
            installer.install_all(include_optional=False)
        elif sys.argv[1] == "--verify":
            installer.verify_installation()
        else:
            print("Usage:")
            print("  python gate_comprehensive_installer.py           # Interactive mode")
            print("  python gate_comprehensive_installer.py --all     # Install everything")
            print("  python gate_comprehensive_installer.py --required # Required only")
            print("  python gate_comprehensive_installer.py --verify  # Verify installations")
    else:
        installer.interactive_install()


if __name__ == "__main__":
    main()
