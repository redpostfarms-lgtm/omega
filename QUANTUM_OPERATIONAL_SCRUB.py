#!/usr/bin/env python3
"""
Quantum Operational Scrub - Final Operational Readiness Check
==============================================================
Deep quantum-level scan for optimal options and operational readiness.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json

class QuantumOperationalScrub:
    """Deep quantum-level operational readiness scanner"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.issues = []
        self.recommendations = []
        self.status = {}
        
    def run_full_scrub(self) -> Dict[str, Any]:
        """Run comprehensive operational scrub"""
        print("\n" + "=" * 80)
        print(" " * 20 + "QUANTUM OPERATIONAL SCRUB - DEEP ANALYSIS")
        print("=" * 80)
        print()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "issues": [],
            "recommendations": [],
            "status": "unknown"
        }
        
        # 1. Core System Check
        print("[1/10] Checking core system files...")
        results["checks"]["core_system"] = self._check_core_system()
        
        # 2. Control Panel Check
        print("[2/10] Checking control panel UI...")
        results["checks"]["control_panel"] = self._check_control_panel()
        
        # 3. BIOS Integration Check
        print("[3/10] Checking BIOS integration and boot logo...")
        results["checks"]["bios"] = self._check_bios_integration()
        
        # 4. Desktop Shortcut Check
        print("[4/10] Checking desktop shortcut...")
        results["checks"]["desktop_shortcut"] = self._check_desktop_shortcut()
        
        # 5. Hardware Control Check
        print("[5/10] Checking hardware control...")
        results["checks"]["hardware"] = self._check_hardware_control()
        
        # 6. Developer Integrations Check
        print("[6/10] Checking developer integrations...")
        results["checks"]["integrations"] = self._check_developer_integrations()
        
        # 7. Security Check
        print("[7/10] Checking security systems...")
        results["checks"]["security"] = self._check_security()
        
        # 8. Startup Integration Check
        print("[8/10] Checking startup integration...")
        results["checks"]["startup"] = self._check_startup_integration()
        
        # 9. Dependencies Check
        print("[9/10] Checking dependencies...")
        results["checks"]["dependencies"] = self._check_dependencies()
        
        # 10. Operational Readiness Check
        print("[10/10] Assessing operational readiness...")
        results["checks"]["operational"] = self._assess_operational_readiness()
        
        # Compile results
        results["issues"] = self.issues
        results["recommendations"] = self.recommendations
        results["status"] = self._determine_status(results["checks"])
        
        return results
    
    def _check_core_system(self) -> Dict[str, Any]:
        """Check core Omega system files"""
        core_files = [
            "omega_full_brain.py",
            "omega_operational_startup.py",
            "hands_free_omega_optimized.py",
            "voice_security_system.py"
        ]
        
        found = []
        missing = []
        
        for file in core_files:
            path = self.base_dir / file
            if path.exists():
                found.append(file)
            else:
                missing.append(file)
                self.issues.append(f"Core file missing: {file}")
        
        return {
            "found": found,
            "missing": missing,
            "status": "ok" if not missing else "issues"
        }
    
    def _check_control_panel(self) -> Dict[str, Any]:
        """Check control panel UI"""
        control_panel = self.base_dir / "omega_control_panel.py"
        start_script = self.base_dir / "START_CONTROL_PANEL.py"
        
        status = "ok"
        issues = []
        
        if not control_panel.exists():
            status = "critical"
            issues.append("Control panel not found: omega_control_panel.py")
            self.issues.append("Control panel file missing")
        else:
            # Check if matplotlib is available
            try:
                import matplotlib
                matplotlib_available = True
            except ImportError:
                matplotlib_available = False
                issues.append("matplotlib not available (GUI mode will use text mode)")
                self.recommendations.append("Install matplotlib for GUI: pip install matplotlib")
        
        if not start_script.exists():
            issues.append("Control panel launcher not found: START_CONTROL_PANEL.py")
        
        return {
            "control_panel_exists": control_panel.exists(),
            "launcher_exists": start_script.exists(),
            "matplotlib_available": matplotlib_available if control_panel.exists() else False,
            "status": status,
            "issues": issues
        }
    
    def _check_bios_integration(self) -> Dict[str, Any]:
        """Check BIOS integration and boot logo"""
        bios_file = self.base_dir / "omega_bios_integration.py"
        boot_logo_file = self.base_dir / "omega_boot_logo.py"
        create_logo_file = self.base_dir / "create_omega_boot_logo.py"
        logo_dir = self.base_dir / "boot_logo"
        logo_image = logo_dir / "omega_logo.bmp" if logo_dir.exists() else None
        
        status = "ok"
        issues = []
        
        if not bios_file.exists():
            issues.append("BIOS integration file not found")
        
        if not boot_logo_file.exists():
            status = "warning"
            issues.append("Boot logo manager not found: omega_boot_logo.py")
        
        if not create_logo_file.exists():
            status = "warning"
            issues.append("Logo creation script not found: create_omega_boot_logo.py")
        
        logo_exists = logo_image and logo_image.exists()
        if not logo_exists:
            status = "warning"
            issues.append("Boot logo image not created (run create_omega_boot_logo.py)")
            self.recommendations.append("Create boot logo: python create_omega_boot_logo.py")
        
        return {
            "bios_integration_exists": bios_file.exists(),
            "boot_logo_manager_exists": boot_logo_file.exists(),
            "logo_creator_exists": create_logo_file.exists(),
            "logo_image_exists": logo_exists,
            "status": status,
            "issues": issues
        }
    
    def _check_desktop_shortcut(self) -> Dict[str, Any]:
        """Check desktop shortcut"""
        desktop = Path.home() / "Desktop"
        if not desktop.exists():
            desktop = Path(os.environ.get('PUBLIC', '')) / "Desktop"
        
        shortcut_path = desktop / "Omega.lnk" if desktop.exists() else None
        shortcut_exists = shortcut_path and shortcut_path.exists()
        
        # Check what the shortcut points to
        target_path = None
        if shortcut_exists:
            try:
                import subprocess
                ps_cmd = f'$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut("{shortcut_path}"); $shortcut.TargetPath'
                result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    target_path = result.stdout.strip()
            except:
                pass
        
        # Check if it points to control panel
        points_to_control_panel = False
        if target_path:
            target_file = Path(target_path)
            if "control_panel" in target_file.name.lower() or "START_CONTROL_PANEL" in target_path:
                points_to_control_panel = True
        
        status = "ok"
        issues = []
        
        if not shortcut_exists:
            status = "warning"
            issues.append("Desktop shortcut not found")
            self.recommendations.append("Create desktop shortcut: python CREATE_DESKTOP_SHORTCUT.py")
        elif not points_to_control_panel:
            status = "info"
            issues.append("Desktop shortcut points to operational startup instead of control panel")
            self.recommendations.append("Update desktop shortcut to launch control panel UI")
        
        return {
            "shortcut_exists": shortcut_exists,
            "target_path": str(target_path) if target_path else None,
            "points_to_control_panel": points_to_control_panel,
            "status": status,
            "issues": issues
        }
    
    def _check_hardware_control(self) -> Dict[str, Any]:
        """Check hardware control"""
        hw_file = self.base_dir / "omega_comprehensive_hardware.py"
        
        hw_available = False
        if hw_file.exists():
            try:
                from omega_comprehensive_hardware import get_hardware_controller
                hw_available = True
            except ImportError:
                pass
        
        return {
            "file_exists": hw_file.exists(),
            "module_available": hw_available,
            "status": "ok" if hw_available else "warning"
        }
    
    def _check_developer_integrations(self) -> Dict[str, Any]:
        """Check developer integrations"""
        int_file = self.base_dir / "omega_developer_integrations.py"
        
        int_available = False
        if int_file.exists():
            try:
                from omega_developer_integrations import get_integration_manager
                int_available = True
            except ImportError:
                pass
        
        return {
            "file_exists": int_file.exists(),
            "module_available": int_available,
            "status": "ok" if int_available else "warning"
        }
    
    def _check_security(self) -> Dict[str, Any]:
        """Check security systems"""
        security_files = [
            "omega_api_keys_enhanced.py",
            "omega_vpn_enhanced.py",
            "omega_security_enhanced.py"
        ]
        
        found = []
        for file in security_files:
            if (self.base_dir / file).exists():
                found.append(file)
        
        return {
            "security_files": found,
            "status": "ok" if found else "warning"
        }
    
    def _check_startup_integration(self) -> Dict[str, Any]:
        """Check startup integration"""
        optimizer_file = self.base_dir / "omega_startup_optimizer.py"
        startup_script = Path(os.getenv("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "Omega_Start.bat"
        
        return {
            "optimizer_exists": optimizer_file.exists(),
            "startup_script_exists": startup_script.exists(),
            "status": "ok"
        }
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check Python dependencies"""
        requirements_file = self.base_dir / "requirements.txt"
        
        missing = []
        if requirements_file.exists():
            # Basic check for common dependencies
            common_deps = ["psutil", "matplotlib", "Pillow"]
            for dep in common_deps:
                try:
                    __import__(dep.lower().replace("-", "_"))
                except ImportError:
                    missing.append(dep)
        
        return {
            "requirements_file_exists": requirements_file.exists(),
            "missing_dependencies": missing,
            "status": "ok" if not missing else "warning"
        }
    
    def _assess_operational_readiness(self) -> Dict[str, Any]:
        """Assess overall operational readiness"""
        score = 100
        factors = []
        
        # Factor 1: Core system (30 points)
        core_ok = len(self.issues) == 0 or all("Core file missing" not in issue for issue in self.issues)
        if not core_ok:
            score -= 30
            factors.append("Core system issues")
        
        # Factor 2: Control panel (20 points)
        control_panel_ok = (self.base_dir / "omega_control_panel.py").exists()
        if not control_panel_ok:
            score -= 20
            factors.append("Control panel missing")
        
        # Factor 3: Desktop shortcut (15 points)
        desktop = Path.home() / "Desktop"
        shortcut_exists = (desktop / "Omega.lnk").exists() if desktop.exists() else False
        if not shortcut_exists:
            score -= 15
            factors.append("Desktop shortcut missing")
        
        # Factor 4: BIOS integration (15 points)
        bios_ok = (self.base_dir / "omega_bios_integration.py").exists()
        if not bios_ok:
            score -= 10
            factors.append("BIOS integration missing")
        
        # Factor 5: Hardware control (10 points)
        hw_ok = (self.base_dir / "omega_comprehensive_hardware.py").exists()
        if not hw_ok:
            score -= 10
            factors.append("Hardware control missing")
        
        # Factor 6: Security (10 points)
        security_ok = (self.base_dir / "omega_api_keys_enhanced.py").exists()
        if not security_ok:
            score -= 10
            factors.append("Security system missing")
        
        status = "ready" if score >= 80 else "needs_work" if score >= 60 else "not_ready"
        
        return {
            "score": score,
            "status": status,
            "factors": factors,
            "ready": score >= 80
        }
    
    def _determine_status(self, checks: Dict[str, Any]) -> str:
        """Determine overall status"""
        critical_issues = [k for k, v in checks.items() if v.get("status") == "critical"]
        if critical_issues:
            return "critical"
        
        warnings = [k for k, v in checks.items() if v.get("status") == "warning"]
        if warnings:
            return "warning"
        
        operational = checks.get("operational", {})
        if operational.get("ready"):
            return "ready"
        
        return "needs_work"
    
    def print_report(self, results: Dict[str, Any]):
        """Print comprehensive report"""
        print("\n" + "=" * 80)
        print(" " * 25 + "QUANTUM OPERATIONAL SCRUB REPORT")
        print("=" * 80)
        print()
        
        # Overall status
        status = results["status"]
        status_symbol = {
            "ready": "[OK]",
            "warning": "[!]",
            "needs_work": "[?]",
            "critical": "[X]"
        }.get(status, "[?]")
        
        print(f"Overall Status: {status_symbol} {status.upper()}")
        print()
        
        # Operational readiness
        operational = results["checks"].get("operational", {})
        score = operational.get("score", 0)
        print(f"Operational Readiness Score: {score}/100")
        print(f"Status: {operational.get('status', 'unknown')}")
        if operational.get("factors"):
            print("Factors affecting score:")
            for factor in operational.get("factors", []):
                print(f"  - {factor}")
        print()
        
        # Issues
        if results["issues"]:
            print("Issues Found:")
            for issue in results["issues"]:
                print(f"  [!] {issue}")
            print()
        
        # Recommendations
        if results["recommendations"]:
            print("Recommendations:")
            for rec in results["recommendations"]:
                print(f"  [→] {rec}")
            print()
        
        # Detailed checks
        print("Detailed Checks:")
        print("-" * 80)
        for check_name, check_data in results["checks"].items():
            status = check_data.get("status", "unknown")
            status_symbol = {
                "ok": "[OK]",
                "warning": "[!]",
                "critical": "[X]",
                "info": "[i]"
            }.get(status, "[?]")
            
            print(f"{status_symbol} {check_name.replace('_', ' ').title()}: {status}")
            
            # Show key details
            if check_name == "control_panel":
                if check_data.get("matplotlib_available"):
                    print(f"      - GUI mode available (matplotlib)")
                else:
                    print(f"      - Text mode only (matplotlib not available)")
            
            if check_name == "bios":
                if check_data.get("logo_image_exists"):
                    print(f"      - Boot logo image exists")
                else:
                    print(f"      - Boot logo image not created")
            
            if check_name == "desktop_shortcut":
                if check_data.get("shortcut_exists"):
                    target = check_data.get("target_path", "Unknown")
                    print(f"      - Target: {Path(target).name if target else 'Unknown'}")
                    if check_data.get("points_to_control_panel"):
                        print(f"      - Points to: Control Panel [OK]")
                    else:
                        print(f"      - Points to: Operational Startup [Update recommended]")
        
        print()
        print("=" * 80)

def main():
    """Main function"""
    scrubber = QuantumOperationalScrub()
    results = scrubber.run_full_scrub()
    scrubber.print_report(results)
    
    # Save report
    report_file = Path(__file__).parent / "quantum_operational_scrub_report.json"
    import json
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nReport saved to: {report_file}")
    print()

if __name__ == "__main__":
    main()
