#!/usr/bin/env python3
"""
Full Integration Scan and Optimization
======================================
Complete system scan, integration verification, and code optimization.
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import json

class FullIntegrationScanner:
    """Complete integration scanner and optimizer"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.report_dir = self.root_dir / "integration_reports"
        self.report_dir.mkdir(exist_ok=True)
        self.results = {
            "scan_timestamp": datetime.now().isoformat(),
            "files_scanned": 0,
            "issues_found": [],
            "optimizations_applied": [],
            "integration_status": {},
            "space_savings": 0
        }
    
    def scan_imports(self) -> List[Dict]:
        """Scan for import issues"""
        issues = []
        python_files = list(self.root_dir.rglob("*.py"))
        
        for py_file in python_files:
            if '__pycache__' in str(py_file) or '.bak' in py_file.name:
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.splitlines()
                
                # Check for common issues
                for i, line in enumerate(lines, 1):
                    # Unused imports (basic check)
                    if line.strip().startswith('import ') and '#' not in line:
                        imported = line.strip().replace('import ', '').split(' as ')[0].strip()
                        # Check if used (simplified)
                        used_count = content.count(imported)
                        if used_count <= 1:
                            issues.append({
                                "file": str(py_file),
                                "line": i,
                                "type": "potentially_unused_import",
                                "message": f"'{imported}' may be unused"
                            })
                
            except Exception as e:
                issues.append({
                    "file": str(py_file),
                    "type": "scan_error",
                    "message": str(e)
                })
        
        return issues
    
    def scan_syntax(self) -> List[Dict]:
        """Scan for syntax errors"""
        issues = []
        python_files = list(self.root_dir.rglob("*.py"))
        
        for py_file in python_files:
            if '__pycache__' in str(py_file):
                continue
            
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    issues.append({
                        "file": str(py_file),
                        "type": "syntax_error",
                        "message": result.stderr
                    })
            except Exception as e:
                issues.append({
                    "file": str(py_file),
                    "type": "compile_error",
                    "message": str(e)
                })
        
        return issues
    
    def check_integration(self) -> Dict:
        """Check integration status of key components"""
        status = {}
        
        # Check slang integration
        slang_files = [
            "omega_slang_processor_optimized.py",
            "omega_language_enhancer.py",
            "SLANG_AND_TERMINOLOGY_KNOWLEDGE_BASE.md"
        ]
        
        status["slang_integration"] = {
            "files_exist": all((self.root_dir / f).exists() for f in slang_files),
            "files": slang_files
        }
        
        # Check if slang is imported in main files
        main_files = [
            "hands_free_omega_optimized.py",
            "language_improver.py"
        ]
        
        imports_found = {}
        for main_file in main_files:
            file_path = self.root_dir / main_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    imports_found[main_file] = {
                        "slang_processor": "omega_slang_processor" in content or "omega_language_enhancer" in content,
                        "has_imports": "import" in content
                    }
        
        status["main_file_integration"] = imports_found
        
        # Check LLM decoding integration
        llm_files = [
            "DIVERSE_BEAM_SEARCH_CODE_EXAMPLES_2026.md",
            "LLM_DECODING_STRATEGIES_2026.md",
            "CONTRASTIVE_SEARCH_MATH_2026.md"
        ]
        
        status["llm_decoding_integration"] = {
            "files_exist": all((self.root_dir / f).exists() for f in llm_files),
            "files": llm_files
        }
        
        return status
    
    def analyze_space_usage(self) -> Dict:
        """Analyze space usage"""
        analysis = {
            "total_files": 0,
            "total_size_bytes": 0,
            "total_size_mb": 0,
            "largest_files": [],
            "by_extension": {}
        }
        
        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file() and not any(skip in str(file_path) for skip in ['__pycache__', '.git', '.bak']):
                size = file_path.stat().st_size
                ext = file_path.suffix or 'no_ext'
                
                analysis["total_files"] += 1
                analysis["total_size_bytes"] += size
                
                if ext not in analysis["by_extension"]:
                    analysis["by_extension"][ext] = {"count": 0, "size": 0}
                analysis["by_extension"][ext]["count"] += 1
                analysis["by_extension"][ext]["size"] += size
                
                analysis["largest_files"].append((str(file_path), size))
        
        analysis["total_size_mb"] = analysis["total_size_bytes"] / (1024 * 1024)
        analysis["largest_files"].sort(key=lambda x: x[1], reverse=True)
        analysis["largest_files"] = analysis["largest_files"][:20]
        
        return analysis
    
    def run_full_scan(self) -> Dict:
        """Run complete integration scan"""
        print("=" * 80)
        print("FULL INTEGRATION SCAN AND OPTIMIZATION")
        print("=" * 80)
        print(f"Timestamp: {self.results['scan_timestamp']}")
        print()
        
        # Phase 1: Syntax scan
        print("[PHASE 1] Scanning for syntax errors...")
        syntax_issues = self.scan_syntax()
        self.results["issues_found"].extend(syntax_issues)
        print(f"  Found {len(syntax_issues)} syntax issues")
        
        # Phase 2: Import scan
        print("\n[PHASE 2] Scanning for import issues...")
        import_issues = self.scan_imports()
        self.results["issues_found"].extend(import_issues[:10])  # Limit to 10
        print(f"  Found {len(import_issues)} potential import issues (showing first 10)")
        
        # Phase 3: Integration check
        print("\n[PHASE 3] Checking integration status...")
        integration_status = self.check_integration()
        self.results["integration_status"] = integration_status
        
        slang_ok = integration_status.get("slang_integration", {}).get("files_exist", False)
        llm_ok = integration_status.get("llm_decoding_integration", {}).get("files_exist", False)
        print(f"  Slang integration: {'✅' if slang_ok else '❌'}")
        print(f"  LLM decoding integration: {'✅' if llm_ok else '❌'}")
        
        # Phase 4: Space analysis
        print("\n[PHASE 4] Analyzing space usage...")
        space_analysis = self.analyze_space_usage()
        self.results["space_analysis"] = space_analysis
        print(f"  Total files: {space_analysis['total_files']}")
        print(f"  Total size: {space_analysis['total_size_mb']:.2f} MB")
        print(f"  Largest files:")
        for file_path, size in space_analysis["largest_files"][:5]:
            print(f"    {Path(file_path).name}: {size / 1024:.2f} KB")
        
        # Phase 5: Optimization recommendations
        print("\n[PHASE 5] Optimization recommendations...")
        recommendations = []
        
        # Check for large Python files
        py_files = [(f, s) for f, s in space_analysis["largest_files"] if f.endswith('.py')]
        if py_files:
            largest_py = py_files[0]
            if largest_py[1] > 100 * 1024:  # >100KB
                recommendations.append(f"Consider splitting {Path(largest_py[0]).name} ({largest_py[1]/1024:.2f} KB)")
        
        # Check for large data files
        data_files = [(f, s) for f, s in space_analysis["largest_files"] if not f.endswith('.py')]
        if data_files:
            largest_data = data_files[0]
            if largest_data[1] > 500 * 1024:  # >500KB
                recommendations.append(f"Consider compressing {Path(largest_data[0]).name} ({largest_data[1]/1024:.2f} KB)")
        
        self.results["recommendations"] = recommendations
        for rec in recommendations:
            print(f"  - {rec}")
        
        # Generate report
        report_file = self.report_dir / f"integration_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[REPORT] Saved to: {report_file}")
        print("=" * 80)
        print("SCAN COMPLETE")
        print("=" * 80)
        
        return self.results

def main():
    """Main entry point"""
    scanner = FullIntegrationScanner()
    results = scanner.run_full_scan()
    
    # Print summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Issues found: {len(results['issues_found'])}")
    print(f"Integration status:")
    print(f"  - Slang: {'✅' if results['integration_status'].get('slang_integration', {}).get('files_exist') else '❌'}")
    print(f"  - LLM Decoding: {'✅' if results['integration_status'].get('llm_decoding_integration', {}).get('files_exist') else '❌'}")
    print(f"Recommendations: {len(results.get('recommendations', []))}")
    
    return 0 if len(results['issues_found']) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
