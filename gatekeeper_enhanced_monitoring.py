#!/usr/bin/env python3
"""
Gatekeeper Enhanced System Monitoring (Shinken-Inspired)
=========================================================
Enhanced system monitoring with performance tracking and alerting.
Inspired by Shinken monitoring patterns.
"""

import psutil
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: Optional[float] = None
    network_sent_mb: Optional[float] = None
    network_recv_mb: Optional[float] = None
    process_count: Optional[int] = None
    load_average: Optional[float] = None


@dataclass
class PerformanceThreshold:
    """Performance threshold for alerting."""
    metric_name: str
    warning_threshold: float
    critical_threshold: float
    alert_on_high: bool = True  # True = alert when above threshold, False = alert when below


class EnhancedMonitor:
    """
    Enhanced system monitor with performance tracking.
    Shinken-inspired monitoring patterns.
    """
    
    def __init__(self, metrics_file: Optional[Path] = None, history_size: int = 1000):
        """Initialize enhanced monitor."""
        self.metrics_file = metrics_file or Path("system_metrics.json")
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.thresholds: Dict[str, PerformanceThreshold] = {}
        self.alerts: List[Dict] = []
        
        # Initialize default thresholds
        self._initialize_default_thresholds()
        
        # Track network baseline
        self._network_baseline = None
        self._last_network_check = None
    
    def _initialize_default_thresholds(self):
        """Initialize default performance thresholds."""
        self.thresholds = {
            'cpu_percent': PerformanceThreshold(
                metric_name='cpu_percent',
                warning_threshold=70.0,
                critical_threshold=90.0,
                alert_on_high=True
            ),
            'memory_percent': PerformanceThreshold(
                metric_name='memory_percent',
                warning_threshold=80.0,
                critical_threshold=95.0,
                alert_on_high=True
            ),
            'disk_usage_percent': PerformanceThreshold(
                metric_name='disk_usage_percent',
                warning_threshold=85.0,
                critical_threshold=95.0,
                alert_on_high=True
            ),
        }
    
    def collect_metrics(self) -> SystemMetrics:
        """
        Collect current system metrics.
        
        Returns:
            SystemMetrics object
        """
        timestamp = datetime.now().isoformat()
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # Memory
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used_mb = memory.used / (1024 * 1024)
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk
        disk_usage_percent = None
        try:
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
        except Exception:
            # Disk usage not available (e.g., on Windows with different path)
            pass
        
        # Network
        network_sent_mb = None
        network_recv_mb = None
        try:
            net_io = psutil.net_io_counters()
            if self._network_baseline is None:
                self._network_baseline = {
                    'sent': net_io.bytes_sent,
                    'recv': net_io.bytes_recv
                }
                self._last_network_check = time.time()
            else:
                current_time = time.time()
                time_diff = current_time - self._last_network_check
                if time_diff > 0:
                    sent_diff = net_io.bytes_sent - self._network_baseline['sent']
                    recv_diff = net_io.bytes_recv - self._network_baseline['recv']
                    network_sent_mb = (sent_diff / time_diff) / (1024 * 1024)  # MB/s
                    network_recv_mb = (recv_diff / time_diff) / (1024 * 1024)  # MB/s
                    self._network_baseline = {
                        'sent': net_io.bytes_sent,
                        'recv': net_io.bytes_recv
                    }
                    self._last_network_check = current_time
        except Exception:
            # Network I/O not available
            pass
        
        # Process count
        process_count = None
        try:
            process_count = len(psutil.pids())
        except Exception:
            # Process enumeration not available
            pass
        
        # Load average (Unix only)
        load_average = None
        try:
            load_avg = psutil.getloadavg()
            load_average = load_avg[0] if load_avg else None
        except Exception:
            # Load average not available (Windows doesn't support this)
            pass
        
        metrics = SystemMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_used_mb=memory_used_mb,
            memory_available_mb=memory_available_mb,
            disk_usage_percent=disk_usage_percent,
            network_sent_mb=network_sent_mb,
            network_recv_mb=network_recv_mb,
            process_count=process_count,
            load_average=load_average
        )
        
        self.metrics_history.append(metrics)
        self._check_thresholds(metrics)
        
        return metrics
    
    def _check_thresholds(self, metrics: SystemMetrics):
        """Check metrics against thresholds and generate alerts."""
        metrics_dict = asdict(metrics)
        
        for threshold_name, threshold in self.thresholds.items():
            metric_value = metrics_dict.get(threshold_name)
            
            if metric_value is None:
                continue
            
            alert_level = None
            if threshold.alert_on_high:
                if metric_value >= threshold.critical_threshold:
                    alert_level = 'critical'
                elif metric_value >= threshold.warning_threshold:
                    alert_level = 'warning'
            else:
                if metric_value <= threshold.critical_threshold:
                    alert_level = 'critical'
                elif metric_value <= threshold.warning_threshold:
                    alert_level = 'warning'
            
            if alert_level:
                alert = {
                    'timestamp': metrics.timestamp,
                    'metric': threshold_name,
                    'value': metric_value,
                    'threshold': threshold.critical_threshold if alert_level == 'critical' else threshold.warning_threshold,
                    'level': alert_level,
                    'message': f"{threshold_name} is {metric_value:.2f} (threshold: {threshold.critical_threshold if alert_level == 'critical' else threshold.warning_threshold})"
                }
                self.alerts.append(alert)
    
    def get_metrics_summary(self, window_minutes: int = 5) -> Dict[str, Any]:
        """
        Get metrics summary for time window.
        
        Args:
            window_minutes: Time window in minutes
        
        Returns:
            Summary dictionary
        """
        if not self.metrics_history:
            return {'error': 'No metrics collected'}
        
        # Filter by time window
        window_seconds = window_minutes * 60
        cutoff_time = time.time() - window_seconds
        
        recent_metrics = []
        for metric in self.metrics_history:
            try:
                metric_time = datetime.fromisoformat(metric.timestamp).timestamp()
                if metric_time >= cutoff_time:
                    recent_metrics.append(metric)
            except Exception:
                # Invalid timestamp format - skip this metric
                pass
        
        if not recent_metrics:
            recent_metrics = list(self.metrics_history)[-10:]  # Fallback to last 10
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'window_minutes': window_minutes,
            'sample_count': len(recent_metrics),
            'cpu': {
                'current': cpu_values[-1] if cpu_values else 0,
                'average': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0
            },
            'memory': {
                'current': memory_values[-1] if memory_values else 0,
                'average': sum(memory_values) / len(memory_values) if memory_values else 0,
                'min': min(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0
            },
            'recent_alerts': len([a for a in self.alerts[-100:] if a.get('level') == 'critical']),
            'total_alerts': len(self.alerts)
        }
        
        return summary
    
    def save_metrics(self):
        """Save metrics history to file."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'metrics': [asdict(m) for m in self.metrics_history],
                'alerts': self.alerts[-100:],  # Last 100 alerts
                'thresholds': {k: asdict(v) for k, v in self.thresholds.items()}
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving metrics: {e}")
    
    def load_metrics(self):
        """Load metrics history from file."""
        if not self.metrics_file.exists():
            return
        
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            
            # Restore metrics (keep last N)
            metrics_data = data.get('metrics', [])
            for m_data in metrics_data[-self.history_size:]:
                self.metrics_history.append(SystemMetrics(**m_data))
            
            # Restore alerts
            self.alerts = data.get('alerts', [])
            
        except Exception as e:
            print(f"Error loading metrics: {e}")


def test_monitor():
    """Test the enhanced monitor."""
    print("=== Gatekeeper Enhanced Monitoring Module Test ===\n")
    
    monitor = EnhancedMonitor()
    
    print("Collecting metrics (5 samples)...")
    for i in range(5):
        metrics = monitor.collect_metrics()
        print(f"  Sample {i+1}: CPU={metrics.cpu_percent:.1f}%, Memory={metrics.memory_percent:.1f}%")
        time.sleep(0.5)
    
    print("\n=== Metrics Summary ===")
    summary = monitor.get_metrics_summary(window_minutes=1)
    print(f"Sample Count: {summary['sample_count']}")
    print(f"CPU - Current: {summary['cpu']['current']:.1f}%, Average: {summary['cpu']['average']:.1f}%")
    print(f"Memory - Current: {summary['memory']['current']:.1f}%, Average: {summary['memory']['average']:.1f}%")
    print(f"Alerts: {summary['total_alerts']} total, {summary['recent_alerts']} critical")
    
    print("\n=== Saving Metrics ===")
    monitor.save_metrics()
    print(f"Metrics saved to {monitor.metrics_file}")
    
    print("\n✓ Enhanced monitoring module test complete!")


if __name__ == "__main__":
    test_monitor()
