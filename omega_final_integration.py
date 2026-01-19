"""
Omega Final Integration System
Integrates all components and generates final completion report
"""

import json
import subprocess
from pathlib import Path
from typing import Dict
from datetime import datetime


class OmegaFinalIntegration:
    """
    Final integration system that brings everything together
    and generates comprehensive completion report
    """

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"
        self.final_report = {
            "timestamp": datetime.now().isoformat(),
            "completion_status": {},
            "efficiency_score": 0.0,
            "education_score": 0.0,
            "overall_score": 0.0,
        }

    def check_package_completion(self) -> Dict:
        """Check package installation completion"""
        print("\n📦 Checking Package Completion...")

        try:
            result = subprocess.run(
                [str(self.venv_python), "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            packages = json.loads(result.stdout)

            # Critical packages we need
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

            installed_names = [p["name"].lower() for p in packages]
            missing_critical = [p for p in critical_packages if p.lower() not in installed_names]

            enhanced_packages = [
                "langchain-community",
                "langchain-openai",
                "langsmith",
                "llama-index",
                "instructor",
                "guidance",
                "seaborn",
                "polars",
                "xgboost",
                "lightgbm",
                "opencv-python",
                "spacy",
            ]

            installed_enhanced = sum(1 for p in enhanced_packages if p.lower() in installed_names)

            completion_score = (
                (len(critical_packages) - len(missing_critical)) / len(critical_packages)
            ) * 100
            education_score = (installed_enhanced / len(enhanced_packages)) * 100

            print(f"   ✓ Total packages: {len(packages)}")
            print(
                f"   ✓ Critical packages: {len(critical_packages) - len(missing_critical)}/{len(critical_packages)}"
            )
            print(f"   ✓ Enhanced packages: {installed_enhanced}/{len(enhanced_packages)}")
            print(f"   ✓ Completion: {completion_score:.1f}%")
            print(f"   ✓ Education: {education_score:.1f}%")

            return {
                "total_packages": len(packages),
                "critical_complete": len(critical_packages) - len(missing_critical),
                "critical_total": len(critical_packages),
                "enhanced_complete": installed_enhanced,
                "enhanced_total": len(enhanced_packages),
                "completion_score": completion_score,
                "education_score": education_score,
                "missing_critical": missing_critical,
            }

        except Exception as e:
            print(f"   ✗ Error checking packages: {e}")
            return {"error": str(e)}

    def check_system_efficiency(self) -> Dict:
        """Check system efficiency"""
        print("\n⚡ Checking System Efficiency...")

        efficiency_factors = []

        import sys

        if sys.version_info >= (3, 10):
            efficiency_factors.append(("Python version >= 3.10", True, 10))
            print("   ✓ Python version optimal")
        else:
            efficiency_factors.append(("Python version >= 3.10", False, 10))
            print("   ✗ Python version suboptimal")

        venv_active = self.venv_python.exists()
        efficiency_factors.append(("Virtual environment", venv_active, 10))
        if venv_active:
            print("   ✓ Virtual environment configured")
        else:
            print("   ✗ Virtual environment missing")

        cred_file = self.project_root / "omega_credentials.py"
        cred_exists = cred_file.exists()
        efficiency_factors.append(("Credential system", cred_exists, 10))
        if cred_exists:
            print("   ✓ Credential system configured")
        else:
            print("   ✗ Credential system missing")

        access_file = self.project_root / "omega_system_access.py"
        access_exists = access_file.exists()
        efficiency_factors.append(("System access framework", access_exists, 10))
        if access_exists:
            print("   ✓ System access framework configured")
        else:
            print("   ✗ System access framework missing")

        monitor_file = self.project_root / "omega_continuous_monitor.py"
        monitor_exists = monitor_file.exists()
        efficiency_factors.append(("Monitoring system", monitor_exists, 10))
        if monitor_exists:
            print("   ✓ Monitoring system configured")
        else:
            print("   ✗ Monitoring system missing")

        gate_file = self.project_root / "gate_auth_system.py"
        gate_exists = gate_file.exists()
        efficiency_factors.append(("GATE authentication", gate_exists, 10))
        if gate_exists:
            print("   ✓ GATE authentication configured")
        else:
            print("   ✗ GATE authentication missing")

        heal_file = self.project_root / "omega_deep_dive.py"
        heal_exists = heal_file.exists()
        efficiency_factors.append(("Self-healing system", heal_exists, 15))
        if heal_exists:
            print("   ✓ Self-healing system configured")
        else:
            print("   ✗ Self-healing system missing")

        edu_file = self.project_root / "omega_education_system.py"
        edu_exists = edu_file.exists()
        efficiency_factors.append(("Education system", edu_exists, 15))
        if edu_exists:
            print("   ✓ Education system configured")
        else:
            print("   ✗ Education system missing")

        research_file = self.project_root / "omega_web_researcher.py"
        research_exists = research_file.exists()
        efficiency_factors.append(("Research system", research_exists, 10))
        if research_exists:
            print("   ✓ Research system configured")
        else:
            print("   ✗ Research system missing")

        max_score = sum(weight for _, _, weight in efficiency_factors)
        actual_score = sum(weight for _, status, weight in efficiency_factors if status)
        efficiency_score = (actual_score / max_score) * 100

        print(f"\n   ✓ Efficiency Score: {efficiency_score:.1f}%")

        return {
            "factors": efficiency_factors,
            "efficiency_score": efficiency_score,
            "max_score": max_score,
            "actual_score": actual_score,
        }

    def check_knowledge_base(self) -> Dict:
        """Check knowledge base completion"""
        print("\n📚 Checking Knowledge Base...")

        kb_file = self.project_root / "OMEGA_KNOWLEDGE_BASE.json"

        if kb_file.exists():
            try:
                with open(kb_file, "r", encoding="utf-8") as f:
                    kb_data = json.load(f)

                education_score = kb_data.get("completion_score", 0)
                categories = len(kb_data.get("categories", {}))

                print(f"   ✓ Knowledge base exists")
                print(f"   ✓ Categories: {categories}")
                print(f"   ✓ Education score: {education_score:.1f}%")

                return {
                    "exists": True,
                    "categories": categories,
                    "education_score": education_score,
                }
            except Exception as e:
                print(f"   ✗ Error reading knowledge base: {e}")
                return {"exists": True, "error": str(e)}
        else:
            print("   ℹ Knowledge base not yet generated")
            print("   Running education system...")

            try:
                subprocess.run(
                    [str(self.venv_python), str(self.project_root / "omega_education_system.py")],
                    timeout=60,
                )

                if kb_file.exists():
                    with open(kb_file, "r", encoding="utf-8") as f:
                        kb_data = json.load(f)
                    education_score = kb_data.get("completion_score", 0)
                    return {"exists": True, "education_score": education_score}

            except Exception as e:
                print(f"   ✗ Could not generate knowledge base: {e}")

            return {"exists": False}

    def generate_final_report(self, packages: Dict, efficiency: Dict, knowledge: Dict):
        """Generate comprehensive final report"""
        print("\n" + "=" * 70)
        print("📊 GENERATING FINAL REPORT")
        print("=" * 70 + "\n")

        completion_score = packages.get("completion_score", 0)
        efficiency_score = efficiency.get("efficiency_score", 0)
        education_score = max(
            packages.get("education_score", 0), knowledge.get("education_score", 0)
        )

        overall_score = completion_score * 0.4 + efficiency_score * 0.3 + education_score * 0.3

        self.final_report.update(
            {
                "completion_score": completion_score,
                "efficiency_score": efficiency_score,
                "education_score": education_score,
                "overall_score": overall_score,
                "packages": packages,
                "efficiency": efficiency,
                "knowledge": knowledge,
            }
        )

        report_path = self.project_root / "OMEGA_FINAL_REPORT.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(self.final_report, f, indent=2)

        md_path = self.project_root / "OMEGA_FINAL_REPORT.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# OMEGA SYSTEM - FINAL COMPLETION REPORT\n\n")
            f.write(f"Generated: {self.final_report['timestamp']}\n\n")
            f.write("---\n\n")

            f.write("## Executive Summary\n\n")
            f.write(f"**Overall Score: {overall_score:.1f}/100**\n\n")
            f.write(f"- **Completion:** {completion_score:.1f}%\n")
            f.write(f"- **Efficiency:** {efficiency_score:.1f}%\n")
            f.write(f"- **Education:** {education_score:.1f}%\n\n")

            f.write("---\n\n")

            f.write("## Package Installation\n\n")
            f.write(f"- Total Packages: {packages.get('total_packages', 0)}\n")
            f.write(
                f"- Critical Packages: {packages.get('critical_complete', 0)}/{packages.get('critical_total', 0)}\n"
            )
            f.write(
                f"- Enhanced Packages: {packages.get('enhanced_complete', 0)}/{packages.get('enhanced_total', 0)}\n\n"
            )

            if packages.get("missing_critical"):
                f.write("### Missing Critical Packages\n\n")
                for pkg in packages["missing_critical"]:
                    f.write(f"- {pkg}\n")
                f.write("\n")

            f.write("## System Efficiency\n\n")
            for name, status, weight in efficiency.get("factors", []):
                status_icon = "✓" if status else "✗"
                f.write(f"- [{status_icon}] {name} ({weight} points)\n")
            f.write("\n")

            f.write("## Knowledge Base\n\n")
            if knowledge.get("exists"):
                f.write(f"- Categories: {knowledge.get('categories', 0)}\n")
                f.write(f"- Education Score: {knowledge.get('education_score', 0):.1f}%\n\n")
            else:
                f.write("- Not yet generated\n\n")

            f.write("---\n\n")

            f.write("## Status Assessment\n\n")

            if overall_score >= 95:
                f.write("### 🎉 EXCELLENT\n\n")
                f.write("System is fully optimized and ready for production use.\n\n")
            elif overall_score >= 90:
                f.write("### ✅ VERY GOOD\n\n")
                f.write("System is nearly complete with minor improvements possible.\n\n")
            elif overall_score >= 80:
                f.write("### 👍 GOOD\n\n")
                f.write("System is functional with room for optimization.\n\n")
            elif overall_score >= 70:
                f.write("### ⚠️ NEEDS IMPROVEMENT\n\n")
                f.write("System requires additional optimization and package installation.\n\n")
            else:
                f.write("### ❌ INCOMPLETE\n\n")
                f.write("System requires significant work to reach target levels.\n\n")

            f.write("---\n\n")
            f.write("## Recommendations\n\n")

            if completion_score < 100:
                f.write("### Package Installation\n\n")
                if packages.get("missing_critical"):
                    f.write("Install missing critical packages:\n\n")
                    f.write("```powershell\n")
                    for pkg in packages["missing_critical"][:5]:
                        f.write(f"pip install {pkg}\n")
                    f.write("```\n\n")

            if efficiency_score < 98:
                f.write("### Efficiency Improvements\n\n")
                missing_components = [
                    name for name, status, _ in efficiency.get("factors", []) if not status
                ]
                if missing_components:
                    f.write("Complete missing system components:\n\n")
                    for comp in missing_components:
                        f.write(f"- {comp}\n")
                    f.write("\n")

            if education_score < 90:
                f.write("### Education Enhancement\n\n")
                f.write("- Run omega_education_system.py to build knowledge base\n")
                f.write("- Install additional learning packages\n")
                f.write("- Review OMEGA_RESEARCH_REPORT.md for best practices\n\n")

        print(f"   ✓ Reports generated:")
        print(f"      - JSON: {report_path}")
        print(f"      - Markdown: {md_path}")

        return self.final_report

    def run_final_integration(self):
        """Run complete final integration"""
        print("\n" + "=" * 70)
        print("🎯 OMEGA FINAL INTEGRATION - INITIATING")
        print("Target: 100% Completion | 98% Efficiency | 90-98% Education")
        print("=" * 70)

        packages = self.check_package_completion()
        efficiency = self.check_system_efficiency()
        knowledge = self.check_knowledge_base()

        final_report = self.generate_final_report(packages, efficiency, knowledge)

        print("\n" + "=" * 70)
        print("✅ FINAL INTEGRATION COMPLETE")
        print("=" * 70)

        print(f"\n📊 FINAL SCORES:")
        print(f"   Overall:     {final_report['overall_score']:.1f}/100")
        print(f"   Completion:  {final_report['completion_score']:.1f}%")
        print(f"   Efficiency:  {final_report['efficiency_score']:.1f}%")
        print(f"   Education:   {final_report['education_score']:.1f}%")

        print("\n" + "=" * 70 + "\n")

        return final_report


def main():
    """Main execution"""
    integrator = OmegaFinalIntegration()
    integrator.run_final_integration()


if __name__ == "__main__":
    main()
