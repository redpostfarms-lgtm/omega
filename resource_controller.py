#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Resource Controller - Interactive CLI for Managing AI Resource Usage
Allows real-time monitoring and adjustment of CPU, RAM, and GPU allocation
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")

try:
    import psutil
except ImportError:
    print("Warning: psutil not installed. Install with: pip install psutil")
    psutil = None


class ResourceController:
    """Interactive resource controller for AI components"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent / "resource_config.json"
        self.config = self.load_config()

    def load_config(self) -> Dict:
        """Load resource configuration"""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return json.load(f)
        return self.get_default_config()

    def save_config(self):
        """Save resource configuration"""
        self.config["last_updated"] = datetime.now().isoformat()
        with open(self.config_path, "w") as f:
            json.dump(self.config, f, indent=2)
        print(f"\n[SAVED] Configuration saved to: {self.config_path}")

    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "resource_limits": {
                "cpu_percent": 80.0,
                "memory_percent": 70.0,
                "gpu_percent": 90.0,
            },
            "active_profile": "balanced",
            "performance_profiles": {
                "maximum_performance": {
                    "cpu_percent": 95.0,
                    "memory_percent": 85.0,
                    "gpu_percent": 95.0,
                },
                "balanced": {
                    "cpu_percent": 70.0,
                    "memory_percent": 60.0,
                    "gpu_percent": 80.0,
                },
                "power_saver": {
                    "cpu_percent": 40.0,
                    "memory_percent": 40.0,
                    "gpu_percent": 50.0,
                },
                "background": {
                    "cpu_percent": 20.0,
                    "memory_percent": 30.0,
                    "gpu_percent": 30.0,
                },
            },
        }

    def get_current_usage(self) -> Dict:
        """Get current system resource usage"""
        if psutil is None:
            return {"error": "psutil not available"}

        cpu_percent = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()

        usage = {
            "cpu_percent": cpu_percent,
            "memory_percent": mem.percent,
            "memory_used_gb": mem.used / (1024**3),
            "memory_total_gb": mem.total / (1024**3),
        }

        # Try to get GPU info
        try:
            import subprocess

            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                parts = [p.strip() for p in result.stdout.strip().split(",")]
                usage["gpu_percent"] = float(parts[0])
                usage["gpu_memory_mb"] = float(parts[1])
                usage["gpu_total_mb"] = float(parts[2])
                usage["gpu_available"] = True
            else:
                usage["gpu_available"] = False
        except Exception:
            usage["gpu_available"] = False

        return usage

    def print_current_status(self):
        """Print current resource status"""
        print("\n" + "=" * 70)
        print("  RESOURCE USAGE STATUS")
        print("=" * 70)

        usage = self.get_current_usage()
        limits = self.config.get("resource_limits", {})
        profile = self.config.get("active_profile", "balanced")

        print(f"\nActive Profile: {profile.upper()}")

        # CPU
        cpu_usage = usage.get("cpu_percent", 0)
        cpu_limit = limits.get("cpu_percent", 100)
        cpu_bar = self.get_progress_bar(cpu_usage, cpu_limit)
        print(f"\nCPU Usage:    {cpu_bar} {cpu_usage:.1f}% / {cpu_limit:.0f}%")

        # Memory
        mem_usage = usage.get("memory_percent", 0)
        mem_limit = limits.get("memory_percent", 100)
        mem_bar = self.get_progress_bar(mem_usage, mem_limit)
        print(
            f"Memory Usage: {mem_bar} {mem_usage:.1f}% / {mem_limit:.0f}% "
            f"({usage.get('memory_used_gb', 0):.1f}/{usage.get('memory_total_gb', 0):.1f} GB)"
        )

        # GPU
        if usage.get("gpu_available"):
            gpu_usage = usage.get("gpu_percent", 0)
            gpu_limit = limits.get("gpu_percent", 100)
            gpu_bar = self.get_progress_bar(gpu_usage, gpu_limit)
            print(
                f"GPU Usage:    {gpu_bar} {gpu_usage:.1f}% / {gpu_limit:.0f}% "
                f"({usage.get('gpu_memory_mb', 0):.0f}/{usage.get('gpu_total_mb', 0):.0f} MB)"
            )
        else:
            print("GPU Usage:    [NOT AVAILABLE]")

    def get_progress_bar(self, value: float, limit: float, width: int = 20) -> str:
        """Generate progress bar"""
        percentage = min(value / max(limit, 1), 1.0)
        filled = int(percentage * width)
        bar = "█" * filled + "░" * (width - filled)

        # Color based on usage
        if value > limit:
            return f"[{bar}] <!>"
        elif value > limit * 0.8:
            return f"[{bar}] /!\\"
        else:
            return f"[{bar}] OK"

    def set_profile(self, profile_name: str):
        """Set active performance profile"""
        if profile_name not in self.config.get("performance_profiles", {}):
            print(f"[ERROR] Unknown profile: {profile_name}")
            return

        profile = self.config["performance_profiles"][profile_name]
        self.config["resource_limits"] = profile.copy()
        self.config["active_profile"] = profile_name
        self.save_config()

        print(f"\n[SUCCESS] Profile set to: {profile_name.upper()}")
        print(f"  CPU Limit: {profile['cpu_percent']}%")
        print(f"  Memory Limit: {profile['memory_percent']}%")
        print(f"  GPU Limit: {profile['gpu_percent']}%")

    def adjust_limits(
        self,
        cpu: Optional[float] = None,
        memory: Optional[float] = None,
        gpu: Optional[float] = None,
    ):
        """Manually adjust resource limits"""
        if "resource_limits" not in self.config:
            self.config["resource_limits"] = {}

        changed = []

        if cpu is not None:
            cpu = max(10.0, min(100.0, cpu))
            self.config["resource_limits"]["cpu_percent"] = cpu
            changed.append(f"CPU: {cpu}%")

        if memory is not None:
            memory = max(10.0, min(100.0, memory))
            self.config["resource_limits"]["memory_percent"] = memory
            changed.append(f"Memory: {memory}%")

        if gpu is not None:
            gpu = max(10.0, min(100.0, gpu))
            self.config["resource_limits"]["gpu_percent"] = gpu
            changed.append(f"GPU: {gpu}%")

        if changed:
            self.config["active_profile"] = "custom"
            self.save_config()
            print(f"\n[SUCCESS] Resource limits adjusted:")
            for change in changed:
                print(f"  • {change}")

    def interactive_menu(self):
        """Interactive menu for resource control"""
        while True:
            self.print_current_status()

            print("\n" + "=" * 70)
            print("  RESOURCE CONTROLLER MENU")
            print("=" * 70)
            print("\nProfiles:")
            print("  1. Maximum Performance (95% CPU, 85% RAM, 95% GPU)")
            print("  2. Balanced (70% CPU, 60% RAM, 80% GPU)")
            print("  3. Power Saver (40% CPU, 40% RAM, 50% GPU)")
            print("  4. Background (20% CPU, 30% RAM, 30% GPU)")
            print("\nCustom Adjustments:")
            print("  5. Set CPU Limit")
            print("  6. Set Memory Limit")
            print("  7. Set GPU Limit")
            print("\nOther:")
            print("  8. Refresh Status")
            print("  9. Save & Exit")
            print("  0. Exit Without Saving")

            try:
                choice = input("\nEnter choice: ").strip()

                if choice == "1":
                    self.set_profile("maximum_performance")
                elif choice == "2":
                    self.set_profile("balanced")
                elif choice == "3":
                    self.set_profile("power_saver")
                elif choice == "4":
                    self.set_profile("background")
                elif choice == "5":
                    cpu = float(input("Enter CPU limit (10-100%): "))
                    self.adjust_limits(cpu=cpu)
                elif choice == "6":
                    memory = float(input("Enter Memory limit (10-100%): "))
                    self.adjust_limits(memory=memory)
                elif choice == "7":
                    gpu = float(input("Enter GPU limit (10-100%): "))
                    self.adjust_limits(gpu=gpu)
                elif choice == "8":
                    continue
                elif choice == "9":
                    self.save_config()
                    print("\n[EXIT] Configuration saved. Goodbye!")
                    break
                elif choice == "0":
                    print("\n[EXIT] Exiting without saving. Goodbye!")
                    break
                else:
                    print("\n[ERROR] Invalid choice")

            except KeyboardInterrupt:
                print("\n\n[EXIT] Interrupted by user. Goodbye!")
                break
            except ValueError as e:
                print(f"\n[ERROR] Invalid input: {e}")
            except Exception as e:
                print(f"\n[ERROR] {e}")


def main():
    """Main entry point"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  OMEGA RESOURCE CONTROLLER".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)

    controller = ResourceController()

    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            controller.print_current_status()
        elif command == "profile" and len(sys.argv) > 2:
            controller.set_profile(sys.argv[2])
            controller.print_current_status()
        elif command == "set" and len(sys.argv) > 3:
            # Format: resource_controller.py set cpu 80
            resource = sys.argv[2].lower()
            value = float(sys.argv[3])
            if resource == "cpu":
                controller.adjust_limits(cpu=value)
            elif resource in ["memory", "ram", "mem"]:
                controller.adjust_limits(memory=value)
            elif resource == "gpu":
                controller.adjust_limits(gpu=value)
            controller.print_current_status()
        else:
            print("\nUsage:")
            print("  python resource_controller.py               # Interactive mode")
            print("  python resource_controller.py status        # Show current status")
            print("  python resource_controller.py profile <name> # Set profile")
            print("  python resource_controller.py set cpu 80    # Set CPU limit")
            print("  python resource_controller.py set memory 70 # Set memory limit")
            print("  python resource_controller.py set gpu 90    # Set GPU limit")
    else:
        # Interactive mode
        controller.interactive_menu()


if __name__ == "__main__":
    main()
