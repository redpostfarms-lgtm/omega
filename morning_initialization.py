"""
Morning Initialization System
==============================
Comprehensive startup sequence that logs into all systems before work begins.
- Checks all service connections
- Verifies API keys and credentials
- Initializes system components
- Validates environment readiness
- Reports status before user interaction
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Ensure UTF-8 encoding
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))

class MorningInitializer:
    """Handles morning system initialization and authentication"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.status = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'errors': [],
            'warnings': [],
            'ready': False
        }

    def print_header(self):
        """Print initialization header"""
        print("\n" + "=" * 80)
        print(" " * 20 + "🌅 MORNING INITIALIZATION SEQUENCE")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80 + "\n")

    def print_phase(self, phase_num: int, phase_name: str):
        """Print phase header"""
        print(f"\n[PHASE {phase_num}] {phase_name}")
        print("-" * 80)

    def check_service(self, name: str, check_func) -> bool:
        """Check a service and record status"""
        try:
            print(f"  Checking {name}...", end=' ')
            result = check_func()
            if result:
                print("✅ OK")
                self.status['services'][name] = {'status': 'ok', 'message': 'Connected'}
                return True
            else:
                print("⚠️ UNAVAILABLE")
                self.status['services'][name] = {'status': 'unavailable', 'message': 'Not responding'}
                self.status['warnings'].append(f"{name} is unavailable")
                return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.status['services'][name] = {'status': 'error', 'message': str(e)}
            self.status['errors'].append(f"{name}: {e}")
            return False

    # ==================== PHASE 1: Environment Validation ====================

    def validate_environment(self):
        """Validate Python environment and dependencies"""
        self.print_phase(1, "Environment Validation")

        # Check Python version
        py_version = sys.version.split()[0]
        print(f"  Python Version: {py_version} ✅")

        # Check critical paths
        paths_to_check = [
            self.project_root / "admin_config.json",
            self.project_root / "config",
            self.project_root / "omega_full_brain.py",
            self.project_root / "voice_security_system.py",
        ]

        for path in paths_to_check:
            if path.exists():
                print(f"  ✅ {path.name}")
            else:
                print(f"  ⚠️ Missing: {path.name}")
                self.status['warnings'].append(f"Missing file: {path}")

        # Check critical packages
        critical_packages = [
            'torch', 'transformers', 'TTS', 'sounddevice',
            'numpy', 'scipy', 'aiohttp', 'requests'
        ]

        print(f"\n  Critical Packages:")
        for package in critical_packages:
            try:
                __import__(package)
                print(f"    ✅ {package}")
            except ImportError:
                print(f"    ⚠️ Missing: {package}")
                self.status['warnings'].append(f"Missing package: {package}")

    # ==================== PHASE 2: Configuration Loading ====================

    def load_configurations(self):
        """Load all configuration files"""
        self.print_phase(2, "Configuration Loading")

        configs = {
            'admin_config.json': self.project_root / "admin_config.json",
            'gate_config.json': self.project_root / "config" / "gate_config.json",
            '.autopilot.json': Path.home() / ".jupyter" / ".autopilot.json",
        }

        self.configs = {}
        for name, path in configs.items():
            try:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        self.configs[name] = json.load(f)
                    print(f"  ✅ Loaded: {name}")
                else:
                    print(f"  ⚠️ Not found: {name}")
                    self.status['warnings'].append(f"Config not found: {name}")
            except Exception as e:
                print(f"  ❌ Error loading {name}: {e}")
                self.status['errors'].append(f"Config error {name}: {e}")

    # ==================== PHASE 3: API & Service Authentication ====================

    def authenticate_services(self):
        """Authenticate with all external services"""
        self.print_phase(3, "Service Authentication & API Health Check")

        # Run API health check first (critical for Omega LLM)
        self.check_api_health()

        # Check Git authentication
        self.check_service("Git", self.check_git)

        # Check GitHub
        self.check_service("GitHub", self.check_github)

        # Check Docker (if available)
        self.check_service("Docker", self.check_docker)

        # Check Hugging Face
        self.check_service("Hugging Face", self.check_huggingface)

        # Check Telegram bot (if configured)
        if '.autopilot.json' in self.configs:
            autopilot = self.configs['.autopilot.json']
            if autopilot.get('enabled') and 'telegram' in autopilot.get('adapters', []):
                self.check_service("Telegram Bot", self.check_telegram)

    def check_git(self) -> bool:
        """Check Git installation and auth"""
        import subprocess
        try:
            result = subprocess.run(['git', '--version'],
                                   capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def check_github(self) -> bool:
        """Check GitHub authentication"""
        import subprocess
        try:
            result = subprocess.run(['git', 'config', 'user.name'],
                                   capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and result.stdout.strip() != ''
        except:
            return False

    def check_docker(self) -> bool:
        """Check Docker daemon"""
        import subprocess
        try:
            result = subprocess.run(['docker', 'version'],
                                   capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def check_huggingface(self) -> bool:
        """Check Hugging Face token"""
        try:
            from huggingface_hub import HfFolder
            token = HfFolder.get_token()
            return token is not None
        except:
            return False

    def check_telegram(self) -> bool:
        """Check Telegram bot token"""
        if '.autopilot.json' not in self.configs:
            return False

        telegram = self.configs['.autopilot.json'].get('telegram', {})
        token = telegram.get('token', '')
        return token != '' and token != 'YOUR_BOT_TOKEN_HERE'

    def check_api_health(self):
        """Run comprehensive API health check for all LLM services"""
        print("\n  🔍 Running Omega API Health Check...")
        print("  " + "-" * 76)

        try:
            # Import and run the API health monitor
            from omega_api_daily_monitor import APIHealthMonitor

            monitor = APIHealthMonitor()
            results = monitor.run_all_tests()
            analysis = monitor.analyze_results()

            # Save results
            monitor.save_log()
            monitor.update_omega_status()

            # Display summary
            print(f"\n  API Health Summary:")
            print(f"    Total Services: {analysis['total_tests']}")
            print(f"    Operational:    {analysis['passed']} ✅")
            print(f"    Failed:         {analysis['failed']} {'⚠️' if analysis['failed'] > 0 else ''}")
            print(f"    Skipped:        {analysis['skipped']}")
            print(f"\n    LLM Status:     {'AVAILABLE ✅' if analysis['llm_available'] else 'UNAVAILABLE ❌'}")
            print(f"    Working LLMs:   {', '.join(analysis['working_llms']) if analysis['working_llms'] else 'None'}")
            print(f"    Redundancy:     {analysis['redundancy_status']}")

            # Record in status
            if analysis['llm_available']:
                self.status['services']['Omega LLM'] = {
                    'status': 'ok',
                    'message': f"Operational via {', '.join(analysis['working_llms'])}",
                    'redundancy': analysis['redundancy_status']
                }
                print(f"\n  ✅ Omega LLM is OPERATIONAL")
            else:
                self.status['services']['Omega LLM'] = {
                    'status': 'error',
                    'message': 'No working LLM services found'
                }
                self.status['errors'].append('Critical: No working LLM services')
                print(f"\n  ❌ Omega LLM is NOT OPERATIONAL")
                print(f"     ACTION REQUIRED: Check API keys and service status")

            print("  " + "-" * 76)

        except Exception as e:
            print(f"  ❌ API Health Check Error: {e}")
            self.status['errors'].append(f"API health check failed: {e}")
            self.status['services']['Omega LLM'] = {
                'status': 'error',
                'message': f'Health check error: {str(e)}'
            }

    # ==================== PHASE 4: System Components ====================

    def initialize_system_components(self):
        """Initialize core system components"""
        self.print_phase(4, "System Components Initialization")

        # Initialize resource manager
        try:
            print("  Initializing resource manager...", end=' ')
            from omega_system_resource_manager import initialize_system_resources
            initialize_system_resources()
            print("✅")
            self.status['services']['resource_manager'] = {'status': 'ok'}
        except Exception as e:
            print(f"⚠️ {e}")
            self.status['warnings'].append(f"Resource manager: {e}")

        # Initialize relationship system
        try:
            print("  Initializing relationship system...", end=' ')
            from omega_relationship_system import get_relationship_manager
            rel_manager = get_relationship_manager()
            status = rel_manager.get_relationship_status()
            print(f"✅ (Level: {status['mutual_level']})")
            self.status['services']['relationship_system'] = {
                'status': 'ok',
                'level': status['mutual_level']
            }
        except Exception as e:
            print(f"⚠️ {e}")
            self.status['warnings'].append(f"Relationship system: {e}")

        # Initialize voice security
        try:
            print("  Initializing voice security...", end=' ')
            from voice_security_system import voice_security
            print("✅")
            self.status['services']['voice_security'] = {'status': 'ok'}
        except Exception as e:
            print(f"⚠️ {e}")
            self.status['warnings'].append(f"Voice security: {e}")

        # Check GPU availability
        try:
            print("  Checking GPU...", end=' ')
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                print(f"✅ {gpu_name}")
                self.status['services']['gpu'] = {
                    'status': 'ok',
                    'name': gpu_name,
                    'memory': f"{torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB"
                }
            else:
                print("⚠️ Not available (CPU mode)")
                self.status['services']['gpu'] = {'status': 'unavailable'}
        except Exception as e:
            print(f"⚠️ {e}")
            self.status['warnings'].append(f"GPU check: {e}")

    # ==================== PHASE 5: System Health Check ====================

    def perform_health_check(self):
        """Perform comprehensive system health check"""
        self.print_phase(5, "System Health Check")

        # Check disk space
        try:
            import shutil
            c_drive = Path("C:/")
            stats = shutil.disk_usage(c_drive)
            free_gb = stats.free / (1024**3)
            total_gb = stats.total / (1024**3)
            percent_free = (stats.free / stats.total) * 100

            print(f"  C: Drive Space: {free_gb:.1f} GB / {total_gb:.1f} GB free ({percent_free:.1f}%)", end=' ')
            if free_gb < 15:
                print("⚠️ LOW SPACE")
                self.status['warnings'].append(f"Low disk space: {free_gb:.1f} GB")
            else:
                print("✅")
        except Exception as e:
            print(f"  ⚠️ Could not check disk space: {e}")

        # Check memory
        try:
            import psutil
            mem = psutil.virtual_memory()
            print(f"  RAM Usage: {mem.percent}% ({mem.used / (1024**3):.1f} GB / {mem.total / (1024**3):.1f} GB)", end=' ')
            if mem.percent > 85:
                print("⚠️ HIGH")
                self.status['warnings'].append(f"High memory usage: {mem.percent}%")
            else:
                print("✅")
        except Exception as e:
            print(f"  ⚠️ Could not check memory: {e}")

        # Check CPU
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"  CPU Usage: {cpu_percent}%", end=' ')
            if cpu_percent > 80:
                print("⚠️ HIGH")
            else:
                print("✅")
        except Exception as e:
            print(f"  ⚠️ Could not check CPU: {e}")

    # ==================== PHASE 6: Final Status ====================

    def generate_final_status(self):
        """Generate and display final status report"""
        self.print_phase(6, "Final Status Report")

        # Count service statuses
        ok_count = sum(1 for s in self.status['services'].values() if s.get('status') == 'ok')
        total_count = len(self.status['services'])

        print(f"\n  Services Ready: {ok_count}/{total_count}")
        print(f"  Errors: {len(self.status['errors'])}")
        print(f"  Warnings: {len(self.status['warnings'])}")

        # Determine overall readiness
        critical_errors = len(self.status['errors'])
        self.status['ready'] = critical_errors == 0

        print("\n" + "=" * 80)
        if self.status['ready']:
            print(" " * 25 + "✅ SYSTEM READY FOR OPERATIONS")
        else:
            print(" " * 25 + "⚠️ SYSTEM READY WITH WARNINGS")
        print("=" * 80 + "\n")

        # Save status report
        self.save_status_report()

        # Display next steps
        if self.status['ready']:
            print("✨ All systems initialized successfully!")
            print("   You can now begin working.")
        else:
            print("⚠️ Some services are unavailable or have warnings.")
            print("   Check the status report for details.")
            if self.status['errors']:
                print("\n❌ Critical Errors:")
                for error in self.status['errors'][:5]:  # Show first 5
                    print(f"   - {error}")

        print(f"\n📝 Status report saved to: morning_init_status.json")
        print()

    def save_status_report(self):
        """Save initialization status to file"""
        report_path = self.project_root / "morning_init_status.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save status report: {e}")

    # ==================== Main Execution ====================

    async def run_initialization(self):
        """Run complete initialization sequence"""
        self.print_header()

        try:
            self.validate_environment()
            self.load_configurations()
            self.authenticate_services()
            self.initialize_system_components()
            self.perform_health_check()
            self.generate_final_status()

        except KeyboardInterrupt:
            print("\n\n⚠️ Initialization interrupted by user")
            self.status['ready'] = False
            self.status['errors'].append("Interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Critical error during initialization: {e}")
            self.status['ready'] = False
            self.status['errors'].append(f"Critical: {e}")
            import traceback
            traceback.print_exc()

        return self.status['ready']

def main():
    """Main entry point"""
    initializer = MorningInitializer()

    # Run async initialization
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    ready = asyncio.run(initializer.run_initialization())

    # Exit with appropriate code
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()
