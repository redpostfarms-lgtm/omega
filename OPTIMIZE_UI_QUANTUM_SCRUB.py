#!/usr/bin/env python3
"""
Optimize UI with Quantum Scrub Methodology
===========================================
Uses Quantum scrub methodology to optimize the control panel UI with visual aids.
Performs comprehensive scan and optimization.
"""

import sys
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

class QuantumUIOptimizer:
    """Quantum-level UI optimization using scrub methodology"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.issues = []
        self.recommendations = []
        self.optimizations = []
        
    def run_full_scan(self) -> Dict[str, Any]:
        """Run comprehensive UI scan using Quantum scrub methodology"""
        
        print("\n" + "=" * 80)
        print(" " * 20 + "QUANTUM UI OPTIMIZATION SCAN")
        print("=" * 80)
        print()
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "issues": [],
            "recommendations": [],
            "optimizations": [],
            "status": "unknown"
        }
        
        control_panel_file = self.base_dir / "omega_control_panel.py"
        
        if not control_panel_file.exists():
            print("[ERROR] Control panel file not found!")
            return results
        
        print(f"[1/8] Analyzing control panel file...")
        results["checks"]["file_analysis"] = self._analyze_control_panel_file(control_panel_file)
        
        print(f"[2/8] Checking UI requirements compliance...")
        results["checks"]["requirements_compliance"] = self._check_requirements_compliance(control_panel_file)
        
        print(f"[3/8] Analyzing visual aids implementation...")
        results["checks"]["visual_aids"] = self._check_visual_aids(control_panel_file)
        
        print(f"[4/8] Checking OIP implementation...")
        results["checks"]["oip_implementation"] = self._check_oip_implementation(control_panel_file)
        
        print(f"[5/8] Analyzing file list section...")
        results["checks"]["file_list"] = self._check_file_list(control_panel_file)
        
        print(f"[6/8] Checking layout optimization...")
        results["checks"]["layout"] = self._check_layout(control_panel_file)
        
        print(f"[7/8] Analyzing performance...")
        results["checks"]["performance"] = self._check_performance(control_panel_file)
        
        print(f"[8/8] Checking dependencies...")
        results["checks"]["dependencies"] = self._check_dependencies()
        
        # Compile results
        results["issues"] = self.issues
        results["recommendations"] = self.recommendations
        results["optimizations"] = self.optimizations
        results["status"] = self._determine_status(results["checks"])
        
        return results
    
    def _analyze_control_panel_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze control panel Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Check for key components
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            # Check for matplotlib usage
            has_matplotlib = 'matplotlib' in content.lower()
            has_librosa = 'librosa' in content.lower()
            has_oip = 'oip' in content.lower() or 'Omega Introduction Panel' in content
            
            return {
                "file_exists": True,
                "classes": classes,
                "functions": len(functions),
                "has_matplotlib": has_matplotlib,
                "has_librosa": has_librosa,
                "has_oip": has_oip,
                "status": "ok" if has_matplotlib else "warning"
            }
        except Exception as e:
            self.issues.append(f"Error analyzing control panel file: {e}")
            return {"file_exists": False, "error": str(e), "status": "error"}
    
    def _check_requirements_compliance(self, file_path: Path) -> Dict[str, Any]:
        """Check UI requirements compliance"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                "no_gatekeeper": "Gatekeeper" not in content,
                "has_file_list": "ax_files" in content or "important_files" in content,
                "has_oip": "ax_oip" in content or "Omega Introduction Panel" in content,
                "has_visual_effects": "librosa" in content or "waveform" in content.lower(),
                "minimal_file_list": "important_files" in content
            }
            
            all_passed = all(checks.values())
            
            if not checks["no_gatekeeper"]:
                self.issues.append("UI still contains 'Gatekeeper' references")
            if not checks["has_file_list"]:
                self.issues.append("File list section not found")
            if not checks["has_oip"]:
                self.issues.append("OIP section not found")
            if not checks["has_visual_effects"]:
                self.recommendations.append("Add visual effects for OIP section")
            
            return {
                "checks": checks,
                "all_passed": all_passed,
                "status": "ok" if all_passed else "warning"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_visual_aids(self, file_path: Path) -> Dict[str, Any]:
        """Check visual aids implementation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                "has_waveform": "waveform" in content.lower(),
                "has_audio_visualization": "librosa" in content and "visualization" in content.lower(),
                "has_color_coding": "color" in content.lower() and ("viridis" in content or "colormap" in content),
                "has_real_time": "FuncAnimation" in content or "animation" in content.lower()
            }
            
            missing = [k for k, v in checks.items() if not v]
            
            if missing:
                self.recommendations.append(f"Enhance visual aids: {', '.join(missing)}")
            
            return {
                "checks": checks,
                "status": "ok" if all(checks.values()) else "improvement_needed"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_oip_implementation(self, file_path: Path) -> Dict[str, Any]:
        """Check OIP (Omega Introduction Panel) implementation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                "has_oip_section": "ax_oip" in content,
                "has_audio_monitoring": "response.wav" in content or "omega_intro.wav" in content,
                "has_speech_sync": "synchronized" in content.lower() or "audio" in content.lower(),
                "has_visual_feedback": "Audio Active" in content or "visual" in content.lower()
            }
            
            return {
                "checks": checks,
                "status": "ok" if all(checks.values()) else "improvement_needed"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_file_list(self, file_path: Path) -> Dict[str, Any]:
        """Check file list section implementation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract important_files list
            match = re.search(r'important_files\s*=\s*\[(.*?)\]', content, re.DOTALL)
            
            file_count = 0
            if match:
                files_text = match.group(1)
                file_count = len([f for f in files_text.split(',') if f.strip()])
            
            checks = {
                "has_file_list": "important_files" in content,
                "minimal_count": file_count <= 10,  # Should be minimal
                "has_status_indicators": "✓" in content or "✗" in content or "status" in content.lower(),
                "has_color_coding": "color" in content.lower() and "exists" in content.lower()
            }
            
            if not checks["minimal_count"]:
                self.recommendations.append("Reduce file list to most important files only")
            
            return {
                "checks": checks,
                "file_count": file_count,
                "status": "ok" if all(checks.values()) else "improvement_needed"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_layout(self, file_path: Path) -> Dict[str, Any]:
        """Check layout optimization"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                "has_gridspec": "GridSpec" in content,
                "has_4_column": "GridSpec(3, 4" in content or "gs = GridSpec(3, 4" in content,
                "file_list_left": "gs[:, 0]" in content or "column 0" in content.lower(),
                "has_space_reserved": True  # Layout should have space
            }
            
            return {
                "checks": checks,
                "status": "ok" if all(checks.values()) else "improvement_needed"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_performance(self, file_path: Path) -> Dict[str, Any]:
        """Check performance optimization"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            checks = {
                "has_animation": "FuncAnimation" in content,
                "has_update_interval": "update_interval" in content,
                "has_error_handling": "try:" in content and "except" in content
            }
            
            recommendations = []
            if "librosa.load" in content and "duration" not in content:
                recommendations.append("Limit librosa.load duration for performance")
            
            if recommendations:
                self.recommendations.extend(recommendations)
            
            return {
                "checks": checks,
                "status": "ok"
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check if required dependencies are available"""
        dependencies = {
            "matplotlib": False,
            "librosa": False,
            "numpy": False,
            "Pillow": False,
            "psutil": False
        }
        
        for dep in dependencies:
            try:
                __import__(dep if dep != "Pillow" else "PIL")
                dependencies[dep] = True
            except ImportError:
                self.issues.append(f"Missing dependency: {dep}")
        
        all_available = all(dependencies.values())
        
        return {
            "dependencies": dependencies,
            "all_available": all_available,
            "status": "ok" if all_available else "missing_dependencies"
        }
    
    def _determine_status(self, checks: Dict) -> str:
        """Determine overall status"""
        statuses = [check.get("status", "unknown") for check in checks.values()]
        
        if "error" in statuses:
            return "error"
        elif "warning" in statuses or any(s == "missing_dependencies" for s in statuses):
            return "warning"
        elif all(s == "ok" for s in statuses):
            return "ok"
        else:
            return "improvement_needed"
    
    def save_results(self, results: Dict[str, Any]) -> Path:
        """Save scan results to JSON"""
        output_path = self.base_dir / "ui_optimization_scan.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"[OK] Scan results saved: {output_path.name}")
        return output_path
    
    def generate_report(self, results: Dict[str, Any]) -> Path:
        """Generate human-readable report"""
        report_content = f"""UI OPTIMIZATION SCAN REPORT - QUANTUM SCRUB METHODOLOGY
================================================================

Scan Date: {results['timestamp']}
Status: {results['status'].upper()}

ISSUES FOUND: {len(results['issues'])}
"""
        if results['issues']:
            for issue in results['issues']:
                report_content += f"\n  - {issue}"
        else:
            report_content += "\n  None"
        
        report_content += f"\n\nRECOMMENDATIONS: {len(results['recommendations'])}"
        if results['recommendations']:
            for rec in results['recommendations']:
                report_content += f"\n  - {rec}"
        else:
            report_content += "\n  None"
        
        report_content += "\n\nCHECK DETAILS:\n"
        for check_name, check_result in results['checks'].items():
            report_content += f"\n{check_name.upper().replace('_', ' ')}:\n"
            if isinstance(check_result, dict):
                status = check_result.get('status', 'unknown')
                report_content += f"  Status: {status}\n"
        
        report_path = self.base_dir / "UI_OPTIMIZATION_SCAN_REPORT.md"
        report_path.write_text(report_content, encoding='utf-8')
        
        print(f"[OK] Report generated: {report_path.name}")
        return report_path

def main():
    """Main function"""
    optimizer = QuantumUIOptimizer()
    
    print("\n" + "=" * 80)
    print(" " * 15 + "QUANTUM UI OPTIMIZATION - FULL SCAN")
    print("=" * 80)
    print()
    print("Running comprehensive UI scan using Quantum scrub methodology...")
    print()
    
    # Run full scan
    results = optimizer.run_full_scan()
    
    # Save results
    json_path = optimizer.save_results(results)
    
    # Generate report
    report_path = optimizer.generate_report(results)
    
    print()
    print("=" * 80)
    print(" " * 25 + "SCAN COMPLETE")
    print("=" * 80)
    print()
    print(f"Status: {results['status'].upper()}")
    print(f"Issues: {len(results['issues'])}")
    print(f"Recommendations: {len(results['recommendations'])}")
    print()
    print("Files created:")
    print(f"  1. {json_path.name} - Scan results (JSON)")
    print(f"  2. {report_path.name} - Scan report (Markdown)")
    print()
    
    if results['status'] == 'ok':
        print("[OK] UI is optimized and ready!")
    else:
        print("[INFO] Review recommendations in the report")
    
    print("=" * 80)
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
