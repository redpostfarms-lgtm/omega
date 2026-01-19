"""
Omega GPU Load Balancer
=======================
Intelligent load balancing between CPU, GPU, and RAM for optimal performance.
Automatically offloads tasks to GPU when available and beneficial.
"""

import psutil
import threading
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import json
from pathlib import Path

try:
    import torch
    TORCH_AVAILABLE = True
    CUDA_AVAILABLE = torch.cuda.is_available()
except ImportError:
    TORCH_AVAILABLE = False
    CUDA_AVAILABLE = False


class GPULoadBalancer:
    """Intelligent GPU/CPU load balancing"""
    
    def __init__(self):
        self.gpu_available = CUDA_AVAILABLE
        self.use_gpu = CUDA_AVAILABLE
        self.cpu_count = psutil.cpu_count(logical=True)
        self.ram_total_gb = psutil.virtual_memory().total / (1024**3)
        
        self.cpu_threshold = 80  # %
        self.ram_threshold = 75  # %
        self.gpu_threshold = 85  # %
        
        self.metrics = {
            'cpu_avg': 0,
            'ram_avg': 0,
            'gpu_avg': 0,
            'decisions': []
        }
        
        self.history = []
        self.max_history = 100
        
        self.monitor_thread = None
        self.monitoring = False
        
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        stats = {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'percent': cpu_percent,
                'count': self.cpu_count,
                'threshold': self.cpu_threshold
            },
            'ram': {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent,
                'threshold': self.ram_threshold
            },
            'gpu': None
        }
        
        if self.gpu_available:
            try:
                gpu_stats = {
                    'available': True,
                    'memory_allocated_gb': torch.cuda.memory_allocated(0) / (1024**3),
                    'memory_reserved_gb': torch.cuda.memory_reserved(0) / (1024**3),
                    'memory_total_gb': torch.cuda.get_device_properties(0).total_memory / (1024**3),
                    'device_name': torch.cuda.get_device_name(0),
                    'threshold': self.gpu_threshold
                }
                
                total_mem = gpu_stats['memory_total_gb']
                used_mem = gpu_stats['memory_allocated_gb']
                gpu_stats['percent'] = (used_mem / total_mem * 100) if total_mem > 0 else 0
                
                stats['gpu'] = gpu_stats
            except Exception as e:
                stats['gpu'] = {'available': False, 'error': str(e)}
        else:
            stats['gpu'] = {'available': False}
        
        return stats
    
    def should_use_gpu(self, task_size_mb: float = 0) -> bool:
        """Decide if GPU should be used for a task"""
        if not self.gpu_available:
            return False
        
        stats = self.get_system_stats()
        
        if stats['ram']['percent'] > self.ram_threshold:
            return True
        
        if stats['cpu']['percent'] > self.cpu_threshold:
            return True
        
        if stats['gpu']['available']:
            gpu_available_gb = (
                stats['gpu']['memory_total_gb'] - 
                stats['gpu']['memory_allocated_gb']
            )
            
            if task_size_mb > 0:
                task_size_gb = task_size_mb / 1024
                if gpu_available_gb < task_size_gb * 2:  # Need 2x for safety margin
                    return False
            
            if gpu_available_gb > 1.0:  # At least 1GB free
                return True
        
        return False
    
    def should_offload_to_cpu(self) -> bool:
        """Decide if GPU tasks should be offloaded to CPU"""
        if not self.gpu_available:
            return True
        
        stats = self.get_system_stats()
        
        if not stats['gpu']['available']:
            return True
        
        if stats['gpu']['percent'] > self.gpu_threshold:
            return True
        
        if (stats['cpu']['percent'] < 40 and 
            stats['gpu']['percent'] > 60):
            return False  # Keep on GPU
        
        return False
    
    def get_load_distribution(self) -> Dict[str, float]:
        """Get recommended load distribution"""
        stats = self.get_system_stats()
        
        distribution = {
            'cpu': 100.0,
            'gpu': 0.0,
            'memory_reserved': 0.0
        }
        
        if not self.gpu_available:
            return distribution
        
        cpu_stress = stats['cpu']['percent']
        ram_stress = stats['ram']['percent']
        gpu_stress = stats['gpu']['percent'] if stats['gpu']['available'] else 100
        
        if ram_stress > 70:
            gpu_ratio = min(0.8, (ram_stress - 50) / 50)
            distribution['cpu'] = 100 * (1 - gpu_ratio)
            distribution['gpu'] = 100 * gpu_ratio
        
        elif cpu_stress > 70:
            gpu_ratio = min(0.6, (cpu_stress - 50) / 50)
            distribution['cpu'] = 100 * (1 - gpu_ratio)
            distribution['gpu'] = 100 * gpu_ratio
        
        else:
            distribution['cpu'] = 100.0
            distribution['gpu'] = 0.0
        
        return distribution
    
    def record_decision(self, task_name: str, used_gpu: bool, 
                       cpu_percent: float, ram_percent: float, 
                       gpu_percent: float = 0):
        """Record a load balancing decision"""
        decision = {
            'timestamp': datetime.now().isoformat(),
            'task': task_name,
            'used_gpu': used_gpu,
            'cpu_percent': cpu_percent,
            'ram_percent': ram_percent,
            'gpu_percent': gpu_percent
        }
        
        self.metrics['decisions'].append(decision)
        
        self.history.append(decision)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations"""
        stats = self.get_system_stats()
        recommendations = []
        
        if stats['ram']['percent'] > 85:
            recommendations.append({
                'priority': 'critical',
                'type': 'memory',
                'message': 'RAM usage critical. Consider offloading to GPU or closing applications.',
                'action': 'offload_to_gpu'
            })
        elif stats['ram']['percent'] > 75:
            recommendations.append({
                'priority': 'high',
                'type': 'memory',
                'message': 'RAM usage high. Offload processing to GPU if available.',
                'action': 'consider_gpu'
            })
        
        if stats['cpu']['percent'] > 85:
            recommendations.append({
                'priority': 'critical',
                'type': 'cpu',
                'message': 'CPU overloaded. Reduce workload or use GPU acceleration.',
                'action': 'reduce_load'
            })
        elif stats['cpu']['percent'] > 75:
            recommendations.append({
                'priority': 'high',
                'type': 'cpu',
                'message': 'CPU usage high. Consider distributing load to GPU.',
                'action': 'distribute_load'
            })
        
        if stats['gpu']['available']:
            if stats['gpu']['percent'] < 30:
                recommendations.append({
                    'priority': 'info',
                    'type': 'gpu',
                    'message': 'GPU underutilized. Consider offloading more tasks.',
                    'action': 'increase_gpu_load'
                })
            elif stats['gpu']['percent'] > 85:
                recommendations.append({
                    'priority': 'high',
                    'type': 'gpu',
                    'message': 'GPU overloaded. Reduce GPU workload.',
                    'action': 'reduce_gpu_load'
                })
        
        return {
            'recommendations': recommendations,
            'distribution': self.get_load_distribution(),
            'stats': stats
        }
    
    def start_monitoring(self, interval: float = 5.0):
        """Start background monitoring thread"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    stats = self.get_system_stats()
                    self.metrics['cpu_avg'] = stats['cpu']['percent']
                    self.metrics['ram_avg'] = stats['ram']['percent']
                    
                    if stats['gpu']['available']:
                        self.metrics['gpu_avg'] = stats['gpu']['percent']
                    
                    time.sleep(interval)
                except Exception as e:
                    print(f"[GPU Load Balancer] Monitoring error: {e}")
                    time.sleep(interval)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
    
    def save_metrics(self, filepath: Path):
        """Save metrics to file"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'history': self.history[-50:],  # Last 50 entries
            'configuration': {
                'cpu_threshold': self.cpu_threshold,
                'ram_threshold': self.ram_threshold,
                'gpu_threshold': self.gpu_threshold,
                'gpu_available': self.gpu_available
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def get_balanced_config(self) -> Dict[str, Any]:
        """Get balanced system configuration"""
        stats = self.get_system_stats()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'status': 'balanced' if all([
                stats['cpu']['percent'] < self.cpu_threshold,
                stats['ram']['percent'] < self.ram_threshold,
                (not stats['gpu']['available'] or 
                 stats['gpu']['percent'] < self.gpu_threshold)
            ]) else 'imbalanced',
            'resource_stats': stats,
            'recommendations': self.get_recommendations(),
            'use_gpu': self.should_use_gpu(),
            'distribution': self.get_load_distribution()
        }


def get_load_balancer() -> GPULoadBalancer:
    """Factory function to get or create load balancer instance"""
    if not hasattr(get_load_balancer, '_instance'):
        get_load_balancer._instance = GPULoadBalancer()
    return get_load_balancer._instance


if __name__ == '__main__':
    balancer = get_load_balancer()
    
    print("\n" + "="*70)
    print("OMEGA GPU LOAD BALANCER")
    print("="*70)
    
    config = balancer.get_balanced_config()
    
    print(f"\nStatus: {config['status'].upper()}")
    print(f"\nResource Statistics:")
    print(f"  CPU:  {config['resource_stats']['cpu']['percent']:.1f}% (threshold: {balancer.cpu_threshold}%)")
    print(f"  RAM:  {config['resource_stats']['ram']['percent']:.1f}% (threshold: {balancer.ram_threshold}%)")
    
    if config['resource_stats']['gpu']['available']:
        print(f"  GPU:  {config['resource_stats']['gpu']['percent']:.1f}% (threshold: {balancer.gpu_threshold}%)")
    else:
        print(f"  GPU:  Not available")
    
    print(f"\nLoad Distribution:")
    dist = config['distribution']
    print(f"  CPU:  {dist['cpu']:.1f}%")
    print(f"  GPU:  {dist['gpu']:.1f}%")
    
    print(f"\nUse GPU: {config['use_gpu']}")
    
    print(f"\nRecommendations: {len(config['recommendations'])}")
    for rec in config['recommendations']:
        print(f"  [{rec['priority'].upper()}] {rec['message']}")
    
    print("\n" + "="*70)
