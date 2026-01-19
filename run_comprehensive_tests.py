#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Test Runner
Executes forensic scan, integration tests, and resource monitoring
Generates detailed reports with resource usage metrics
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

# Add tests directory to path
sys.path.insert(0, str(Path(__file__).parent / "tests"))

try:
    from test_forensics_integrity import ForensicScanner
    from test_integration_suite import IntegrationTester
    from test_resource_monitor import ResourceMonitor
except ImportError as e:
    print(f"⚠️  Warning: Could not import test modules: {e}")
    print("Some features may be limited. Install dependencies with:")
    print("  pip install pytest pytest-asyncio psutil")
    ForensicScanner = None
    IntegrationTester = None
    ResourceMonitor = None


class ComprehensiveTestRunner:
    """Master test runner for all system tests"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.reports_dir = root_path / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.start_time = time.time()
        self.results: Dict = {
            "timestamp": datetime.now().isoformat(),
            "forensic_scan": None,
            "integration_tests": None,
            "resource_monitoring": None,
            "pytest_results": None,
            "summary": {},
        }

    def print_banner(self, title: str):
        """Print formatted banner"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70 + "\n")

    async def run_forensic_scan(self) -> Dict:
        """Run forensic security and integrity scan"""
        self.print_banner("🔍 FORENSIC SCAN")

        if ForensicScanner is None:
            return {"status": "SKIPPED", "reason": "ForensicScanner not available"}

        scanner = ForensicScanner(self.root_path)
        results = scanner.run_full_scan()

        # Save report
        report_file = self.reports_dir / "forensic_scan_report.json"
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"✅ Forensic scan complete!")
        print(f"   Report: {report_file}")
        print(f"\n   Summary:")
        for key, value in results.get("summary", {}).items():
            print(f"     • {key}: {value}")

        return {"status": "COMPLETED", "results": results, "report_file": str(report_file)}

    async def run_integration_tests(self) -> Dict:
        """Run integration test suite"""
        self.print_banner("🧪 INTEGRATION TESTS")

        if IntegrationTester is None:
            return {"status": "SKIPPED", "reason": "IntegrationTester not available"}

        tester = IntegrationTester(self.root_path)
        results = await tester.run_all_tests()

        # Save report
        report_file = self.reports_dir / "integration_test_report.json"
        with open(report_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"✅ Integration tests complete!")
        print(f"   Report: {report_file}")

        return {"status": "COMPLETED", "results": results, "report_file": str(report_file)}

    def run_resource_monitoring(self) -> Dict:
        """Run resource monitoring and analysis"""
        self.print_banner("📊 RESOURCE MONITORING")

        if ResourceMonitor is None:
            return {"status": "SKIPPED", "reason": "ResourceMonitor not available"}

        monitor = ResourceMonitor()

        # Collect initial metrics
        print("Collecting system metrics...")
        metrics = monitor.get_current_metrics()

        # Wait a bit and collect again for average
        time.sleep(2)
        metrics2 = monitor.get_current_metrics()

        # Generate comprehensive report
        report = monitor.generate_report(metrics2)

        # Calculate averages
        avg_cpu = (metrics.cpu_percent + metrics2.cpu_percent) / 2
        avg_mem = (metrics.memory_percent + metrics2.memory_percent) / 2

        report["averages"] = {"cpu_percent": avg_cpu, "memory_percent": avg_mem}

        # Save report
        report_file = self.reports_dir / "resource_monitoring_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Resource monitoring complete!")
        print(f"   Report: {report_file}")
        print(f"\n   Current Usage:")
        print(f"     • CPU: {avg_cpu:.1f}% (Limit: {monitor.limits.cpu_percent}%)")
        print(f"     • Memory: {avg_mem:.1f}% (Limit: {monitor.limits.memory_percent}%)")
        print(f"     • GPU: {'Available' if metrics2.gpu_available else 'Not Available'}")
        print(f"     • AI Processes: {len(monitor.get_ai_processes())}")

        return {"status": "COMPLETED", "results": report, "report_file": str(report_file)}

    def run_pytest_suite(self) -> Dict:
        """Run pytest test suite"""
        self.print_banner("🧪 PYTEST SUITE")

        try:
            # Run pytest with coverage
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-v",
                "--tb=short",
                "-m",
                "not slow",
                "--color=yes",
            ]

            print(f"Running: {' '.join(cmd)}\n")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            # Save output
            output_file = self.reports_dir / "pytest_output.txt"
            with open(output_file, "w") as f:
                f.write(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")

            print(result.stdout)
            if result.stderr:
                print("Errors/Warnings:", result.stderr)

            return {
                "status": "COMPLETED" if result.returncode == 0 else "FAILED",
                "return_code": result.returncode,
                "output_file": str(output_file),
            }

        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "error": "Pytest execution timed out"}
        except FileNotFoundError:
            return {"status": "SKIPPED", "reason": "pytest not installed"}
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

    async def run_all_tests(self) -> Dict:
        """Run complete test suite"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  COMPREHENSIVE TEST SUITE - THE GATEKEEPER OMEGA".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)

        # Run forensic scan
        self.results["forensic_scan"] = await self.run_forensic_scan()

        # Run integration tests
        self.results["integration_tests"] = await self.run_integration_tests()

        # Run resource monitoring
        self.results["resource_monitoring"] = self.run_resource_monitoring()

        # Run pytest suite
        self.results["pytest_results"] = self.run_pytest_suite()

        # Calculate summary
        elapsed_time = time.time() - self.start_time

        self.results["summary"] = {
            "total_duration_seconds": elapsed_time,
            "forensic_status": self.results["forensic_scan"]["status"],
            "integration_status": self.results["integration_tests"]["status"],
            "resource_status": self.results["resource_monitoring"]["status"],
            "pytest_status": self.results["pytest_results"]["status"],
        }

        # Save master report
        master_report = self.reports_dir / "master_test_report.json"
        with open(master_report, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        # Print final summary
        self.print_banner("📋 FINAL SUMMARY")

        print(f"Total Duration: {elapsed_time:.2f} seconds")
        print(f"\nTest Results:")
        print(f"  • Forensic Scan: {self.results['forensic_scan']['status']}")
        print(f"  • Integration Tests: {self.results['integration_tests']['status']}")
        print(f"  • Resource Monitoring: {self.results['resource_monitoring']['status']}")
        print(f"  • Pytest Suite: {self.results['pytest_results']['status']}")

        print(f"\n📁 Reports Directory: {self.reports_dir}")
        print(f"   Master Report: {master_report}")

        # Resource usage summary
        if self.results["resource_monitoring"]["status"] == "COMPLETED":
            res_data = self.results["resource_monitoring"]["results"]
            print(f"\n💻 Resource Usage During Tests:")
            print(f"   • CPU: {res_data.get('averages', {}).get('cpu_percent', 0):.1f}%")
            print(
                f"   • Memory: {res_data.get('averages', {}).get('memory_percent', 0):.1f}%"
            )
            print(f"   • Health: {res_data.get('health_status', 'UNKNOWN')}")

        print("\n" + "=" * 70)
        print("✅ All tests completed!")
        print("=" * 70 + "\n")

        return self.results


async def main():
    """Main entry point"""
    root_path = Path(__file__).parent
    runner = ComprehensiveTestRunner(root_path)

    try:
        results = await runner.run_all_tests()

        # Exit with error code if critical tests failed
        if results["pytest_results"]["status"] == "FAILED":
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Test runner error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
