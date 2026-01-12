# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Status & Health Monitor - Complete System Check
# Master Developer - Full System Analytics

"""
Ω Omega Status & Health Monitor

Comprehensive system status check:
- All modules availability
- Integration status
- Voice system status
- Enhanced modules status
- System health metrics
- Ready state verification
"""

import sys
import io
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Set UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Find GATE directory - check multiple locations
GATE = None
possible_gates = [
    Path(r'D:\RPF_BRAIN\The Gatekeeper'),
    Path.cwd() / 'The Gatekeeper',
    Path.cwd() if Path.cwd().name == 'The Gatekeeper' else None,
    Path(r'C:\Users\Drakalich\Desktop\R&D\The Gatekeeper')
]

for gate_path in possible_gates:
    if gate_path and gate_path.exists():
        GATE = gate_path
        break

if GATE is None:
    GATE = Path.cwd()  # Fallback to current directory

# Add enhanced path
_enhanced_path = Path(r'D:\RPF_BRAIN\The Gatekeeper')
if _enhanced_path.exists() and str(_enhanced_path) not in sys.path:
    sys.path.insert(0, str(_enhanced_path))


class OmegaStatusMonitor:
    """Comprehensive Omega system status monitor."""
    
    def __init__(self):
        self.status = {
            "timestamp": datetime.now().isoformat(),
            "omega_version": "1.0",
            "system_status": "unknown",
            "modules": {},
            "integrations": {},
            "health": {},
            "ready": False
        }
    
    def check_all(self) -> Dict[str, Any]:
        """Run complete system check."""
        print("=" * 80)
        print("Ω OMEGA STATUS & HEALTH MONITOR")
        print("=" * 80)
        print()
        
        # Check core modules
        self._check_core_modules()
        
        # Check enhanced modules
        self._check_enhanced_modules()
        
        # Check voice system
        self._check_voice_system()
        
        # Check integrations
        self._check_integrations()
        
        # Check system health
        self._check_system_health()
        
        # Determine overall status
        self._determine_status()
        
        # Print summary
        self._print_summary()
        
        return self.status
    
    def _check_core_modules(self):
        """Check core Omega modules."""
        print("Checking Core Modules...")
        
        modules = {
            "deep_system_test": False,
            "omega_autonomous_core": False,
            "omega_voice": False,
            "omega_self_autopsy": False,
            "omega_master_upgrade": False
        }
        
        for module_name in modules:
            try:
                # Check multiple possible locations
                possible_paths = [
                    GATE / f"{module_name}.py",
                    Path.cwd() / f"{module_name}.py",
                    Path.cwd() / "The Gatekeeper" / f"{module_name}.py"
                ]
                
                found = False
                for module_path in possible_paths:
                    if module_path.exists():
                        modules[module_name] = True
                        print(f"  ✓ {module_name} ({module_path})")
                        found = True
                        break
                
                if not found:
                    print(f"  ✗ {module_name} (file not found in {GATE})")
            except Exception as e:
                print(f"  ✗ {module_name} (error: {e})")
        
        self.status["modules"]["core"] = modules
        print()
    
    def _check_enhanced_modules(self):
        """Check enhanced modules."""
        print("Checking Enhanced Modules...")
        
        enhanced = {
            "security": False,
            "speed": False,
            "scalability": False,
            "quantum": False
        }
        
        # Security
        try:
            from omega_security_enhanced import SANITIZER, KILLSWITCH, AUDIT_LOGGER  # type: ignore
            enhanced["security"] = True
            print("  ✓ Security Enhanced")
        except ImportError:
            print("  ✗ Security Enhanced (not available)")
        
        # Speed
        try:
            from omega_speed_enhanced import lru_cache, CONNECTION_POOL, PARALLEL_EXECUTOR  # type: ignore
            enhanced["speed"] = True
            print("  ✓ Speed Enhanced")
        except ImportError:
            print("  ✗ Speed Enhanced (not available)")
        
        # Scalability
        try:
            from omega_scalability_enhanced import RATE_LIMITER, RESOURCE_MONITOR  # type: ignore
            enhanced["scalability"] = True
            print("  ✓ Scalability Enhanced")
        except ImportError:
            print("  ✗ Scalability Enhanced (not available)")
        
        # Quantum
        try:
            from omega_quantum_enhanced import HARDWARE_ENTROPY, CRYPTO_RNG  # type: ignore
            enhanced["quantum"] = True
            print("  ✓ Quantum Enhanced")
        except ImportError:
            print("  ✗ Quantum Enhanced (not available)")
        
        self.status["modules"]["enhanced"] = enhanced
        print()
    
    def _check_voice_system(self):
        """Check voice system components."""
        print("Checking Voice System...")
        
        voice_components = {
            "omega_voice": False,
            "omega_voice_recorder": False,
            "omega_voice_learner": False,
            "omega_voice_modulator": False,
            "omega_soundboard": False,
            "omega_voice_collector": False,
            "omega_free_tts_apis": False
        }
        
        for component in voice_components:
            try:
                # Check multiple possible locations
                possible_paths = [
                    GATE / f"{component}.py",
                    Path.cwd() / f"{component}.py",
                    Path.cwd() / "The Gatekeeper" / f"{component}.py"
                ]
                
                found = False
                for component_path in possible_paths:
                    if component_path.exists():
                        voice_components[component] = True
                        print(f"  ✓ {component}")
                        found = True
                        break
                
                if not found:
                    print(f"  ✗ {component} (file not found)")
            except Exception as e:
                print(f"  ✗ {component} (error: {e})")
        
        # Check TTS availability
        tts_status = {
            "pyttsx3": False,
            "edge_tts": False,
            "coqui_tts": False,
            "piper_tts": False
        }
        
        try:
            import pyttsx3
            tts_status["pyttsx3"] = True
            print("  ✓ pyttsx3 available")
        except ImportError:
            print("  ✗ pyttsx3 not available")
        
        try:
            import edge_tts
            tts_status["edge_tts"] = True
            print("  ✓ edge-tts available")
        except ImportError:
            print("  ✗ edge-tts not available")
        
        try:
            from TTS.api import TTS
            tts_status["coqui_tts"] = True
            print("  ✓ Coqui TTS available")
        except ImportError:
            print("  ✗ Coqui TTS not available")
        
        self.status["modules"]["voice"] = voice_components
        self.status["modules"]["tts"] = tts_status
        print()
    
    def _check_integrations(self):
        """Check system integrations."""
        print("Checking Integrations...")
        
        integrations = {
            "voice_in_core": False,
            "autonomous_in_core": False,
            "enhanced_in_core": False,
            "enhanced_in_voice": False
        }
        
        # Check if voice is integrated in core
        content = None
        try:
            with open(GATE / "deep_system_test.py", 'r', encoding='utf-8') as f:
                content = f.read()
                if "from omega_voice import" in content:
                    integrations["voice_in_core"] = True
                    print("  ✓ Voice integrated in core")
                else:
                    print("  ✗ Voice not integrated in core")
        except Exception:
            print("  ✗ Cannot check voice integration")
        
        # Check if autonomous is integrated
        if content:
            try:
                if "from omega_autonomous_core import" in content:
                    integrations["autonomous_in_core"] = True
                    print("  ✓ Autonomous core integrated")
                else:
                    print("  ✗ Autonomous core not integrated")
            except Exception:
                print("  ✗ Cannot check autonomous integration")
        else:
            print("  ✗ Cannot check autonomous integration (file not read)")
        
        # Check if enhanced modules are integrated
        if content:
            if "from omega_security_enhanced import" in content:
                integrations["enhanced_in_core"] = True
                print("  ✓ Enhanced modules integrated in core")
            else:
                print("  ✗ Enhanced modules not integrated in core")
        else:
            print("  ✗ Cannot check enhanced modules integration (file not read)")
        
        # Check if quantum RNG is in voice
        try:
            with open(GATE / "omega_voice.py", 'r', encoding='utf-8') as f:
                voice_content = f.read()
                if "CRYPTO_RNG" in voice_content or "from omega_quantum_enhanced" in voice_content:
                    integrations["enhanced_in_voice"] = True
                    print("  ✓ Quantum enhancements in voice")
                else:
                    print("  ✗ Quantum enhancements not in voice")
        except Exception:
            print("  ✗ Cannot check voice enhancements")
        
        self.status["integrations"] = integrations
        print()
    
    def _check_system_health(self):
        """Check system health metrics."""
        print("Checking System Health...")
        
        health = {
            "files_exist": 0,
            "files_total": 0,
            "directories_accessible": True,
            "memory_usage": "unknown",
            "disk_space": "unknown"
        }
        
        # Check critical files
        critical_files = [
            "deep_system_test.py",
            "omega_voice.py",
            "omega_autonomous_core.py",
            "omega_security_enhanced.py",
            "omega_speed_enhanced.py",
            "omega_scalability_enhanced.py",
            "omega_quantum_enhanced.py"
        ]
        
        health["files_total"] = len(critical_files)
        for file in critical_files:
            if (GATE / file).exists():
                health["files_exist"] += 1
        
        print(f"  Critical files: {health['files_exist']}/{health['files_total']}")
        
        # Check directories
        critical_dirs = [
            GATE / "omega_voice",
            GATE.parent if GATE.parent.exists() else None
        ]
        
        dirs_ok = True
        for dir_path in critical_dirs:
            if dir_path and not dir_path.exists():
                dirs_ok = False
                break
        
        health["directories_accessible"] = dirs_ok
        print(f"  Directories accessible: {dirs_ok}")
        
        self.status["health"] = health
        print()
    
    def _determine_status(self):
        """Determine overall system status."""
        core_ok = all(self.status["modules"]["core"].values())
        enhanced_ok = all(self.status["modules"]["enhanced"].values())
        voice_ok = all(self.status["modules"]["voice"].values())
        integrations_ok = all(self.status["integrations"].values())
        health_ok = (
            self.status["health"]["files_exist"] == self.status["health"]["files_total"] and
            self.status["health"]["directories_accessible"]
        )
        
        if core_ok and enhanced_ok and voice_ok and integrations_ok and health_ok:
            self.status["system_status"] = "operational"
            self.status["ready"] = True
        elif core_ok and enhanced_ok:
            self.status["system_status"] = "partial"
            self.status["ready"] = True
        else:
            self.status["system_status"] = "degraded"
            self.status["ready"] = False
    
    def _print_summary(self):
        """Print status summary."""
        print("=" * 80)
        print("OMEGA STATUS SUMMARY")
        print("=" * 80)
        print()
        print(f"System Status: {self.status['system_status'].upper()}")
        print(f"Ready: {'✓ YES' if self.status['ready'] else '✗ NO'}")
        print()
        
        print("Module Status:")
        print(f"  Core: {sum(self.status['modules']['core'].values())}/{len(self.status['modules']['core'])}")
        print(f"  Enhanced: {sum(self.status['modules']['enhanced'].values())}/{len(self.status['modules']['enhanced'])}")
        print(f"  Voice: {sum(self.status['modules']['voice'].values())}/{len(self.status['modules']['voice'])}")
        print()
        
        print("Integration Status:")
        for key, value in self.status["integrations"].items():
            status = "✓" if value else "✗"
            print(f"  {status} {key}")
        print()
        
        print("Health:")
        health = self.status["health"]
        print(f"  Files: {health['files_exist']}/{health['files_total']}")
        print(f"  Directories: {'✓' if health['directories_accessible'] else '✗'}")
        print()
        
        print("=" * 80)
        
        # Save status
        status_file = GATE / "omega_status.json"
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, indent=2)
            print(f"Status saved to: {status_file}")
        except Exception as e:
            print(f"Could not save status: {e}")
        
        print("=" * 80)


def main():
    """Main entry point."""
    monitor = OmegaStatusMonitor()
    status = monitor.check_all()
    
    if status["ready"]:
        print("\n✓ OMEGA IS READY")
        return 0
    else:
        print("\n⚠ OMEGA IS NOT FULLY READY")
        return 1


if __name__ == '__main__':
    sys.exit(main())

