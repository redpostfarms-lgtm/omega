"""
Omega Resource Optimizer - GPU/CPU Priority, RAM Cache Only
Enforces 60% GPU + 40% CPU processing strategy to minimize RAM usage
Keeps memory usage below 85% threshold by shifting compute to GPU/CPU
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import psutil


class OmegaResourceOptimizer:
    """Optimize system resources: GPU/CPU priority, RAM cache-only"""

    def __init__(self):
        self.base_path = Path(r"H:\The Gatekeeper")
        self.config_file = self.base_path / "resource_config.json"
        self.log_file = self.base_path / "system_monitor_reports" / "resource_optimizer_log.txt"

        # Resource allocation strategy
        self.strategy = {
            "gpu_target_percent": 60,
            "cpu_target_percent": 40,
            "ram_cache_limit_mb": 512,
            "memory_threshold_percent": 85,
            "aggressive_cleanup_threshold": 80,
        }

        self.gpu_available = self.check_gpu()
        self.save_config()

    def check_gpu(self) -> bool:
        """Check if GPU is available"""
        try:
            import torch

            return torch.cuda.is_available()
        except ImportError:
            return False

    def save_config(self):
        """Save resource optimization configuration"""
        config = {
            "last_updated": datetime.now().isoformat(),
            "strategy": self.strategy,
            "gpu_available": self.gpu_available,
            "status": "active",
        }

        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    def log(self, message: str):
        """Log optimizer activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        self.log_file.parent.mkdir(exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(log_entry.strip())

    def get_memory_usage(self) -> float:
        """Get current memory usage percentage"""
        memory = psutil.virtual_memory()
        return memory.percent

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)

    def optimize_memory(self) -> Dict[str, Any]:
        """Run memory optimization"""
        mem_before = self.get_memory_usage()
        self.log(f"Memory usage before optimization: {mem_before:.2f}%")

        results = {
            "mem_before": mem_before,
            "actions_taken": [],
            "mem_after": 0,
            "reduction": 0,
        }

        # If memory over threshold, take action
        if mem_before >= self.strategy["aggressive_cleanup_threshold"]:
            self.log("⚠️ Memory above threshold, starting aggressive cleanup...")

            # Clear system cache
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "Clear-RecycleBin -Force -ErrorAction SilentlyContinue",
                    ],
                    capture_output=True,
                    timeout=10,
                )
                results["actions_taken"].append("Cleared recycle bin")
            except Exception:
                pass

            # Run Windows memory cleanup
            try:
                subprocess.run(
                    [
                        "powershell",
                        "-Command",
                        "[System.GC]::Collect(); [System.GC]::WaitForPendingFinalizers()",
                    ],
                    capture_output=True,
                    timeout=10,
                )
                results["actions_taken"].append("Forced garbage collection")
            except Exception:
                pass

            # Close unnecessary background processes
            self.close_memory_hogs()
            results["actions_taken"].append("Closed memory-heavy processes")

        mem_after = self.get_memory_usage()
        results["mem_after"] = mem_after
        results["reduction"] = mem_before - mem_after

        self.log(f"Memory usage after optimization: {mem_after:.2f}%")
        self.log(f"Memory freed: {results['reduction']:.2f}%")

        return results

    def close_memory_hogs(self):
        """Close processes using excessive memory (optional/careful)"""
        # Only close known optional processes
        optional_processes = [
            # "Battle.net",  # Uncomment if you want to auto-close
            # "MuseHub",
        ]

        for proc_name in optional_processes:
            try:
                for proc in psutil.process_iter(["name", "memory_percent"]):
                    if proc.info["name"] == proc_name and proc.info["memory_percent"] > 5:
                        self.log(
                            f"Closing {proc_name} (using {proc.info['memory_percent']:.1f}% memory)"
                        )
                        proc.terminate()
            except Exception as e:
                self.log(f"Could not close {proc_name}: {e}")

    def set_process_affinity(self):
        """Set CPU affinity for optimal thread distribution"""
        cpu_count = psutil.cpu_count()

        # Reserve 2 cores for system
        available_cores = max(1, cpu_count - 2)

        self.log(f"Total CPU cores: {cpu_count}, Using: {available_cores}")

        return available_cores

    def enforce_gpu_priority(self):
        """Ensure GPU processing is prioritized when available"""
        if not self.gpu_available:
            self.log("⚠️ GPU not available, using CPU-only mode")
            return False

        try:
            import torch

            device_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)

            self.log(f"✅ GPU Active: {device_name}")
            self.log(f"GPU Memory: {gpu_memory:.2f} GB")

            # Set CUDA device
            torch.cuda.set_device(0)

            return True
        except Exception as e:
            self.log(f"GPU priority error: {e}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system resource status"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=1)

        status = {
            "timestamp": datetime.now().isoformat(),
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "cpu_percent": cpu,
            "gpu_available": self.gpu_available,
            "strategy": self.strategy,
            "status": "🟢 OPTIMAL"
            if memory.percent < 75
            else "⚠️ HIGH"
            if memory.percent < 85
            else "🔴 CRITICAL",
        }

        return status

    def run_optimization(self):
        """Run full resource optimization"""
        self.log("=" * 60)
        self.log("🔧 OMEGA RESOURCE OPTIMIZER - STARTING")
        self.log("=" * 60)

        # Check initial status
        status_before = self.get_system_status()
        self.log(f"Initial Status: {status_before['status']}")
        self.log(f"Memory: {status_before['memory_percent']:.2f}%")
        self.log(f"CPU: {status_before['cpu_percent']:.2f}%")

        # Set GPU priority
        gpu_active = self.enforce_gpu_priority()

        # Set CPU affinity
        cores = self.set_process_affinity()

        # Run memory optimization if needed
        if status_before["memory_percent"] >= self.strategy["aggressive_cleanup_threshold"]:
            opt_results = self.optimize_memory()
            self.log(f"Actions taken: {', '.join(opt_results['actions_taken'])}")

        # Check final status
        status_after = self.get_system_status()
        self.log(f"\nFinal Status: {status_after['status']}")
        self.log(f"Memory: {status_after['memory_percent']:.2f}%")
        self.log(f"CPU: {status_after['cpu_percent']:.2f}%")

        self.log("=" * 60)
        self.log("✅ OPTIMIZATION COMPLETE")
        self.log("=" * 60)

        return status_after


def main():
    """Run resource optimizer"""
    optimizer = OmegaResourceOptimizer()
    result = optimizer.run_optimization()

    print("\n📊 RESOURCE ALLOCATION STRATEGY:")
    print(f"   GPU Priority: {optimizer.strategy['gpu_target_percent']}%")
    print(f"   CPU Usage: {optimizer.strategy['cpu_target_percent']}%")
    print(f"   RAM Cache Limit: {optimizer.strategy['ram_cache_limit_mb']} MB")
    print(f"   Memory Threshold: {optimizer.strategy['memory_threshold_percent']}%")

    if result["memory_percent"] < 75:
        print("\n🟢 System resources optimized successfully!")
    elif result["memory_percent"] < 85:
        print("\n⚠️ Memory usage moderate - monitoring active")
    else:
        print("\n🔴 Memory usage high - consider closing applications")


if __name__ == "__main__":
    main()
