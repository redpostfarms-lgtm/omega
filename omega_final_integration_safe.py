"""
Omega Final Integration System (UTF-8 Safe)
Integrates all components and generates final completion report
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict
from datetime import datetime

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


class OmegaFinalIntegration:
    """Final integration system"""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"

    def check_packages(self):
        """Check package installation"""
        print("\n[*] Checking Package Completion...")

        result = subprocess.run(
            [str(self.venv_python), "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        packages = json.loads(result.stdout)

        critical_packages = [
            "langchain",
            "openai",
            "anthropic",
            "transformers",
            "fastapi",
            "flask",
            "streamlit",
            "gradio",
            "pandas",
            "numpy",
            "matplotlib",
            "plotly",
            "redis",
            "pymongo",
            "psycopg2-binary",
            "chromadb",
            "cryptography",
            "pyjwt",
            "pytest",
        ]

        installed = [p["name"].lower() for p in packages]
        missing = [p for p in critical_packages if p not in installed]

        completion = ((len(critical_packages) - len(missing)) / len(critical_packages)) * 100

        print(f"   [+] Total packages: {len(packages)}")
        print(f"   [+] Critical: {len(critical_packages) - len(missing)}/{len(critical_packages)}")
        print(f"   [+] Completion: {completion:.1f}%")

        return {"total": len(packages), "completion_score": completion, "missing": missing}

    def check_efficiency(self):
        """Check system efficiency"""
        print("\n[*] Checking System Efficiency...")

        files_to_check = [
            ("omega_credentials.py", 10),
            ("omega_system_access.py", 15),
            ("gate_auth_system.py", 10),
            ("omega_deep_dive.py", 15),
            ("omega_education_system.py", 15),
            ("omega_web_researcher.py", 10),
            ("omega_continuous_monitor.py", 15),
            ("omega_advanced_installer.py", 10),
        ]

        score = 0
        max_score = sum(s for _, s in files_to_check)

        for file, points in files_to_check:
            if (self.project_root / file).exists():
                score += points
                print(f"   [+] {file}: OK")
            else:
                print(f"   [-] {file}: Missing")

        efficiency = (score / max_score) * 100
        print(f"\n   [+] Efficiency Score: {efficiency:.1f}%")

        return {"efficiency_score": efficiency, "score": score, "max": max_score}

    def check_education(self):
        """Check education score"""
        print("\n[*] Checking Education System...")

        kb_file = self.project_root / "OMEGA_KNOWLEDGE_BASE.json"

        if kb_file.exists():
            with open(kb_file, "r", encoding="utf-8") as f:
                kb_data = json.load(f)
            score = kb_data.get("completion_score", 0)
            print(f"   [+] Knowledge Base: {score:.1f}%")
            return {"education_score": score, "exists": True}
        else:
            print("   [-] Knowledge Base: Not generated")
            return {"education_score": 0, "exists": False}

    def generate_report(self, packages, efficiency, education):
        """Generate final report"""
        print("\n" + "=" * 70)
        print("GENERATING FINAL REPORT")
        print("=" * 70)

        completion = packages["completion_score"]
        eff_score = efficiency["efficiency_score"]
        edu_score = education["education_score"]
        overall = completion * 0.4 + eff_score * 0.3 + edu_score * 0.3

        report = {
            "timestamp": datetime.now().isoformat(),
            "completion_score": completion,
            "efficiency_score": eff_score,
            "education_score": edu_score,
            "overall_score": overall,
            "packages": packages,
            "efficiency": efficiency,
            "education": education,
        }

        json_path = self.project_root / "OMEGA_FINAL_REPORT.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        md_path = self.project_root / "OMEGA_FINAL_REPORT.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# OMEGA SYSTEM - FINAL COMPLETION REPORT\n\n")
            f.write(f"Generated: {report['timestamp']}\n\n")
            f.write("---\n\n")

            f.write("## Executive Summary\n\n")
            f.write(f"**Overall Score: {overall:.1f}/100**\n\n")
            f.write(f"- Completion: {completion:.1f}%\n")
            f.write(f"- Efficiency: {eff_score:.1f}%\n")
            f.write(f"- Education: {edu_score:.1f}%\n\n")

            f.write("---\n\n")

            f.write("## Package Installation\n\n")
            f.write(f"- Total Packages: {packages['total']}\n")
            f.write(f"- Completion: {completion:.1f}%\n\n")

            if packages["missing"]:
                f.write("### Missing Critical Packages\n\n")
                for pkg in packages["missing"]:
                    f.write(f"- {pkg}\n")
                f.write("\n")

            f.write("## System Efficiency\n\n")
            f.write(f"- Score: {eff_score:.1f}%\n")
            f.write(f"- Components: {efficiency['score']}/{efficiency['max']}\n\n")

            f.write("## Education System\n\n")
            f.write(f"- Score: {edu_score:.1f}%\n")
            f.write(
                f"- Knowledge Base: {'Generated' if education['exists'] else 'Not Generated'}\n\n"
            )

            f.write("---\n\n")

            f.write("## Status Assessment\n\n")

            if overall >= 95:
                f.write("### EXCELLENT\n\n")
                f.write("System is fully optimized and ready.\n\n")
            elif overall >= 90:
                f.write("### VERY GOOD\n\n")
                f.write("System is nearly complete.\n\n")
            elif overall >= 80:
                f.write("### GOOD\n\n")
                f.write("System is functional.\n\n")
            else:
                f.write("### NEEDS IMPROVEMENT\n\n")
                f.write("System requires additional work.\n\n")

        print(f"\n   [+] Reports generated:")
        print(f"       - JSON: {json_path}")
        print(f"       - Markdown: {md_path}")

        return report

    def run(self):
        """Run complete integration"""
        print("\n" + "=" * 70)
        print("OMEGA FINAL INTEGRATION - INITIATING")
        print("Target: 100% Completion | 98% Efficiency | 90-98% Education")
        print("=" * 70)

        packages = self.check_packages()
        efficiency = self.check_efficiency()
        education = self.check_education()

        report = self.generate_report(packages, efficiency, education)

        print("\n" + "=" * 70)
        print("FINAL INTEGRATION COMPLETE")
        print("=" * 70)

        print(f"\nFINAL SCORES:")
        print(f"   Overall:     {report['overall_score']:.1f}/100")
        print(f"   Completion:  {report['completion_score']:.1f}%")
        print(f"   Efficiency:  {report['efficiency_score']:.1f}%")
        print(f"   Education:   {report['education_score']:.1f}%")

        print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    integrator = OmegaFinalIntegration()
    integrator.run()
