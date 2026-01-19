#!/usr/bin/env python3
"""
Omega Resource Manager
======================
Manages CPU, GPU, and RAM resources for optimal performance.
Implements adaptive loading patterns for improved speed over time.
"""

import sys
import os
import psutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

# Try GPU detection
try:
    import torch
    TORCH_AVAILABLE = True
    CUDA_AVAILABLE = torch.cuda.is_available() if TORCH_AVAILABLE else False
    if CUDA_AVAILABLE:
        GPU_COUNT = torch.cuda.device_count()
        GPU_NAME = torch.cuda.get_device_name(0)
    else:
        GPU_COUNT = 0
        GPU_NAME = None
except ImportError:
    TORCH_AVAILABLE = False
    CUDA_AVAILABLE = False
    GPU_COUNT = 0
    GPU_NAME = None

class ResourceManager:
    """Manages system resources (CPU, GPU, RAM) for optimal performance"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count(logical=True)
        self.cpu_freq = psutil.cpu_freq()
        self.ram_total = psutil.virtual_memory().total / (1024**3)  # GB
        self.ram_available = psutil.virtual_memory().available / (1024**3)  # GB
        self.gpu_available = CUDA_AVAILABLE
        self.gpu_count = GPU_COUNT
        self.gpu_name = GPU_NAME
        
        # Resource usage tracking
        self.resource_history = []
        self.loading_patterns = {}
        self.optimal_settings = {}
        
        # Performance profiles
        self.performance_profile = self._detect_performance_profile()
        
    def _detect_performance_profile(self) -> str:
        """Detect system performance profile"""
        # CPU cores
        if self.cpu_count >= 8:
            cpu_score = "high"
        elif self.cpu_count >= 4:
            cpu_score = "medium"
        else:
            cpu_score = "low"
        
        # RAM
        if self.ram_total >= 16:
            ram_score = "high"
        elif self.ram_total >= 8:
            ram_score = "medium"
        else:
            ram_score = "low"
        
        # GPU
        gpu_score = "high" if self.gpu_available else "low"
        
        # Overall profile
        if cpu_score == "high" and ram_score == "high" and gpu_score == "high":
            return "high_performance"
        elif cpu_score == "medium" and ram_score == "medium":
            return "medium_performance"
        else:
            return "low_performance"
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_ram_usage(self) -> Dict[str, float]:
        """Get current RAM usage"""
        mem = psutil.virtual_memory()
        return {
            "total_gb": mem.total / (1024**3),
            "available_gb": mem.available / (1024**3),
            "used_gb": mem.used / (1024**3),
            "percent": mem.percent
        }
    
    def get_gpu_usage(self) -> Optional[Dict[str, Any]]:
        """Get GPU usage if available"""
        if not self.gpu_available:
            return None
        
        try:
            import torch
            return {
                "device_count": torch.cuda.device_count(),
                "current_device": torch.cuda.current_device(),
                "device_name": torch.cuda.get_device_name(0),
                "memory_allocated_gb": torch.cuda.memory_allocated(0) / (1024**3),
                "memory_reserved_gb": torch.cuda.memory_reserved(0) / (1024**3),
                "memory_total_gb": torch.cuda.get_device_properties(0).total_memory / (1024**3)
            }
        except:
            return None
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get comprehensive resource status"""
        return {
            "cpu": {
                "count": self.cpu_count,
                "usage_percent": self.get_cpu_usage(),
                "frequency_mhz": self.cpu_freq.current if self.cpu_freq else None
            },
            "ram": self.get_ram_usage(),
            "gpu": self.get_gpu_usage(),
            "performance_profile": self.performance_profile
        }
    
    def can_use_gpu(self) -> bool:
        """Check if GPU can be used"""
        return self.gpu_available and self.gpu_count > 0
    
    def should_use_multiprocessing(self, task_complexity: str = "medium") -> bool:
        """Determine if multiprocessing should be used"""
        cpu_usage = self.get_cpu_usage()
        
        if task_complexity == "high":
            return self.cpu_count >= 4 and cpu_usage < 70
        elif task_complexity == "medium":
            return self.cpu_count >= 2 and cpu_usage < 80
        else:
            return False
    
    def get_optimal_workers(self, task_complexity: str = "medium") -> int:
        """Get optimal number of worker threads/processes"""
        cpu_usage = self.get_cpu_usage()
        available_cores = self.cpu_count
        
        if task_complexity == "high":
            # Use more cores for complex tasks
            workers = min(available_cores - 1, 8)
        elif task_complexity == "medium":
            # Use fewer cores for medium tasks
            workers = min(available_cores // 2, 4)
        else:
            workers = 1
        
        # Adjust based on CPU usage
        if cpu_usage > 70:
            workers = max(1, workers // 2)
        
        return max(1, workers)
    
    def track_loading_time(self, component: str, load_time: float):
        """Track loading time for a component"""
        if component not in self.loading_patterns:
            self.loading_patterns[component] = []
        
        self.loading_patterns[component].append({
            "timestamp": datetime.now().isoformat(),
            "load_time": load_time,
            "resources": self.get_resource_status()
        })
        
        # Keep last 20 entries
        if len(self.loading_patterns[component]) > 20:
            self.loading_patterns[component] = self.loading_patterns[component][-20:]
    
    def get_optimal_load_order(self) -> List[str]:
        """Get optimal loading order based on history"""
        if not self.loading_patterns:
            # Default order
            return [
                "ui_framework",
                "caching",
                "scanner",
                "buttons",
                "monitoring"
            ]
        
        # Sort by average load time (fastest first)
        component_times = {}
        for component, history in self.loading_patterns.items():
            if history:
                avg_time = sum(h["load_time"] for h in history) / len(history)
                component_times[component] = avg_time
        
        # Sort by load time (fastest first)
        sorted_components = sorted(component_times.items(), key=lambda x: x[1])
        return [comp for comp, _ in sorted_components]
    
    def save_loading_patterns(self, filepath: Path):
        """Save loading patterns to file"""
        data = {
            "loading_patterns": self.loading_patterns,
            "optimal_settings": self.optimal_settings,
            "performance_profile": self.performance_profile,
            "resource_info": {
                "cpu_count": self.cpu_count,
                "ram_total_gb": self.ram_total,
                "gpu_available": self.gpu_available,
                "gpu_name": self.gpu_name
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def load_loading_patterns(self, filepath: Path):
        """Load loading patterns from file"""
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.loading_patterns = data.get("loading_patterns", {})
            self.optimal_settings = data.get("optimal_settings", {})
        except Exception as e:
            print(f"[Resource Manager] Error loading patterns: {e}")

class GradualLoader:
    """Gradual loading system that learns optimal loading patterns"""
    
    def __init__(self, resource_manager: ResourceManager):
        self.resource_manager = resource_manager
        self.base_dir = Path(__file__).parent.absolute()
        self.patterns_file = self.base_dir / ".omega_loading_patterns.json"
        
        # Load existing patterns
        self.resource_manager.load_loading_patterns(self.patterns_file)
        
        # Gradual loading settings
        self.gradual_load = True
        self.delay_between_components = 0.1  # Initial delay (will adapt)
        
    def load_component(self, component_name: str, load_func, *args, **kwargs):
        """Load a component with timing and resource tracking"""
        start_time = time.time()
        
        try:
            # Check if we should delay
            if self.gradual_load:
                # Use adaptive delay based on CPU usage
                cpu_usage = self.resource_manager.get_cpu_usage()
                if cpu_usage > 70:
                    time.sleep(self.delay_between_components * 2)
                else:
                    time.sleep(self.delay_between_components)
            
            # Load component
            result = load_func(*args, **kwargs)
            
            # Track loading time
            load_time = time.time() - start_time
            self.resource_manager.track_loading_time(component_name, load_time)
            
            return result
            
        except Exception as e:
            print(f"[Gradual Loader] Error loading {component_name}: {e}")
            raise
    
    def load_all_components(self, components: Dict[str, Tuple[callable, tuple, dict]]):
        """Load all components in optimal order"""
        # Get optimal load order
        optimal_order = self.resource_manager.get_optimal_load_order()
        
        # Sort components by optimal order
        ordered_components = []
        for comp_name in optimal_order:
            if comp_name in components:
                ordered_components.append((comp_name, components[comp_name]))
        
        # Add remaining components
        for comp_name, comp_data in components.items():
            if comp_name not in optimal_order:
                ordered_components.append((comp_name, comp_data))
        
        # Load components
        results = {}
        for comp_name, (load_func, args, kwargs) in ordered_components:
            print(f"[Gradual Loader] Loading {comp_name}...")
            result = self.load_component(comp_name, load_func, *args, **kwargs)
            results[comp_name] = result
        
        # Save patterns
        self.resource_manager.save_loading_patterns(self.patterns_file)
        
        return results
    
    def optimize_delay(self):
        """Optimize delay based on loading patterns"""
        if not self.resource_manager.loading_patterns:
            return
        
        # Calculate average load time
        all_times = []
        for history in self.resource_manager.loading_patterns.values():
            all_times.extend([h["load_time"] for h in history])
        
        if all_times:
            avg_time = sum(all_times) / len(all_times)
            # Adjust delay based on average time (faster systems need less delay)
            if avg_time < 0.1:
                self.delay_between_components = 0.05
            elif avg_time < 0.5:
                self.delay_between_components = 0.1
            else:
                self.delay_between_components = 0.2

def get_resource_manager() -> ResourceManager:
    """Get global resource manager instance"""
    global _resource_manager
    if '_resource_manager' not in globals():
        _resource_manager = ResourceManager()
    return _resource_manager

_resource_manager = None

def main():
    """Test resource manager"""
    print("=" * 80)
    print(" " * 25 + "OMEGA RESOURCE MANAGER")
    print("=" * 80)
    print()
    
    rm = ResourceManager()
    status = rm.get_resource_status()
    
    print("Resource Status:")
    print(f"  CPU: {status['cpu']['count']} cores, {status['cpu']['usage_percent']:.1f}% usage")
    print(f"  RAM: {status['ram']['used_gb']:.1f}/{status['ram']['total_gb']:.1f} GB ({status['ram']['percent']:.1f}%)")
    
    if status['gpu']:
        print(f"  GPU: {status['gpu']['device_name']}")
        print(f"       Memory: {status['gpu']['memory_allocated_gb']:.2f}/{status['gpu']['memory_total_gb']:.2f} GB")
    else:
        print("  GPU: Not available")
    
    print(f"  Performance Profile: {status['performance_profile']}")
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
