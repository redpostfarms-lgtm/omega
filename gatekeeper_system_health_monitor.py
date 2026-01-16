#!/usr/bin/env python3
"""
Gatekeeper System Health Monitor
===============================
Real-time monitoring and diagnostics for the complete Gatekeeper-Omega system.
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import deque
import psutil


class HealthMetric:
    """Single health metric with history."""
    
    def __init__(self, name: str, max_history: int = 100):
        self.name = name
        self.history = deque(maxlen=max_history)
        self.latest = None
        self.threshold_warning = None
        self.threshold_critical = None
    
    def record(self, value: Any, timestamp: Optional[datetime] = None) -> None:
        """Record a metric value."""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.history.append({
            'value': value,
            'timestamp': timestamp.isoformat()
        })
        self.latest = {
            'value': value,
            'timestamp': timestamp.isoformat()
        }
    
    def get_status(self) -> str:
        """Get status: healthy, warning, or critical."""
        if not self.latest:
            return 'unknown'
        
        value = self.latest['value']
        
        if self.threshold_critical and value > self.threshold_critical:
            return 'critical'
        if self.threshold_warning and value > self.threshold_warning:
            return 'warning'
        
        return 'healthy'
    
    def get_average(self) -> Optional[float]:
        """Get average of numeric values."""
        if not self.history:
            return None
        
        try:
            values = [h['value'] for h in self.history if isinstance(h['value'], (int, float))]
            return sum(values) / len(values) if values else None
        except:
            return None


class SystemHealthMonitor:
    """Comprehensive system health monitoring."""
    
    def __init__(self):
        """Initialize health monitor."""
        self.metrics = {}
        self.component_status = {}
        self.alerts = deque(maxlen=100)
        self.running = False
        self.monitor_thread = None
        self.update_interval = 5  # seconds
        
        self._initialize_metrics()
    
    def _initialize_metrics(self) -> None:
        """Initialize all health metrics."""
        # System metrics
        self.metrics['cpu_percent'] = HealthMetric('CPU %')
        self.metrics['cpu_percent'].threshold_warning = 70
        self.metrics['cpu_percent'].threshold_critical = 90
        
        self.metrics['memory_percent'] = HealthMetric('Memory %')
        self.metrics['memory_percent'].threshold_warning = 75
        self.metrics['memory_percent'].threshold_critical = 90
        
        self.metrics['disk_usage'] = HealthMetric('Disk Usage %')
        self.metrics['disk_usage'].threshold_warning = 80
        self.metrics['disk_usage'].threshold_critical = 95
        
        # Process metrics
        self.metrics['process_count'] = HealthMetric('Process Count')
        self.metrics['open_files'] = HealthMetric('Open Files')
        
        # Network metrics
        self.metrics['network_bytes_sent'] = HealthMetric('Network Sent')
        self.metrics['network_bytes_recv'] = HealthMetric('Network Received')
        
        # Component health
        self.component_status = {
            'gatekeeper': 'unknown',
            'omega_voice': 'unknown',
            'control_panel': 'unknown',
            'wazuh_siem': 'unknown',
            'database': 'unknown'
        }
    
    def start_monitoring(self) -> None:
        """Start background health monitoring."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name='HealthMonitor'
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """Stop background health monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                self._collect_metrics()
                self._check_alerts()
                time.sleep(self.update_interval)
            except Exception as e:
                self.add_alert('ERROR', f'Monitor loop error: {e}')
    
    def _collect_metrics(self) -> None:
        """Collect all system metrics."""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics['cpu_percent'].record(cpu_percent)
            
            # Memory
            memory = psutil.virtual_memory()
            self.metrics['memory_percent'].record(memory.percent)
            
            # Disk
            disk = psutil.disk_usage('/')
            self.metrics['disk_usage'].record(disk.percent)
            
            # Processes
            self.metrics['process_count'].record(len(psutil.pids()))
            
            # Open files
            try:
                proc = psutil.Process()
                open_files = len(proc.open_files())
                self.metrics['open_files'].record(open_files)
            except:
                pass
            
            # Network
            net_io = psutil.net_io_counters()
            self.metrics['network_bytes_sent'].record(net_io.bytes_sent)
            self.metrics['network_bytes_recv'].record(net_io.bytes_recv)
        
        except Exception as e:
            self.add_alert('WARNING', f'Metric collection error: {e}')
    
    def _check_alerts(self) -> None:
        """Check metrics for alert conditions."""
        for metric_name, metric in self.metrics.items():
            status = metric.get_status()
            
            if status == 'critical':
                self.add_alert(
                    'CRITICAL',
                    f'{metric_name}: {metric.latest["value"]:.2f}'
                )
            elif status == 'warning':
                self.add_alert(
                    'WARNING',
                    f'{metric_name}: {metric.latest["value"]:.2f}'
                )
    
    def add_alert(self, level: str, message: str) -> None:
        """Add an alert."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.alerts.append(alert)
    
    def update_component_status(self, component: str, status: str) -> None:
        """Update component health status."""
        if component in self.component_status:
            self.component_status[component] = status
            
            if status == 'error':
                self.add_alert('ERROR', f'Component {component} failed')
            elif status == 'warning':
                self.add_alert('WARNING', f'Component {component} has issues')
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        # Calculate overall status
        metric_statuses = [m.get_status() for m in self.metrics.values()]
        component_statuses = list(self.component_status.values())
        
        # Determine overall health
        if 'critical' in metric_statuses or 'error' in component_statuses:
            overall_status = 'CRITICAL'
        elif 'warning' in metric_statuses or 'warning' in component_statuses:
            overall_status = 'WARNING'
        else:
            overall_status = 'HEALTHY'
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': overall_status,
            'metrics': {
                name: {
                    'latest': metric.latest,
                    'average': metric.get_average(),
                    'status': metric.get_status(),
                    'history_size': len(metric.history)
                }
                for name, metric in self.metrics.items()
            },
            'components': self.component_status,
            'recent_alerts': list(self.alerts)[-20:],
            'alert_count': len(self.alerts)
        }
    
    def get_metric(self, name: str) -> Optional[HealthMetric]:
        """Get a specific metric."""
        return self.metrics.get(name)
    
    def export_report(self, filename: str = 'health_report.json') -> str:
        """Export health report to file."""
        try:
            report = self.get_health_report()
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return filename
        except Exception as e:
            print(f"Error exporting report: {e}")
            return None


class ComponentHealthChecker:
    """Check health of individual components."""
    
    @staticmethod
    def check_gatekeeper() -> Dict[str, Any]:
        """Check Gatekeeper component health."""
        try:
            from gatekeeper_omega_bridge import get_bridge
            bridge = get_bridge()
            return {
                'component': 'gatekeeper',
                'status': bridge.status.value,
                'errors': len(bridge.errors),
                'initialized': True
            }
        except Exception as e:
            return {
                'component': 'gatekeeper',
                'status': 'error',
                'error': str(e),
                'initialized': False
            }
    
    @staticmethod
    def check_omega_voice() -> Dict[str, Any]:
        """Check Omega voice system health."""
        try:
            import omega_full_brain
            return {
                'component': 'omega_voice',
                'status': 'healthy',
                'initialized': True
            }
        except ImportError:
            try:
                import omega_simple_final
                return {
                    'component': 'omega_voice',
                    'status': 'degraded',
                    'reason': 'Using simple mode',
                    'initialized': True
                }
            except ImportError:
                return {
                    'component': 'omega_voice',
                    'status': 'error',
                    'error': 'No voice module available',
                    'initialized': False
                }
        except Exception as e:
            return {
                'component': 'omega_voice',
                'status': 'error',
                'error': str(e),
                'initialized': False
            }
    
    @staticmethod
    def check_control_panel() -> Dict[str, Any]:
        """Check control panel health."""
        try:
            from flask import Flask
            return {
                'component': 'control_panel',
                'status': 'healthy',
                'initialized': True
            }
        except ImportError:
            return {
                'component': 'control_panel',
                'status': 'error',
                'error': 'Flask not installed',
                'initialized': False
            }
        except Exception as e:
            return {
                'component': 'control_panel',
                'status': 'error',
                'error': str(e),
                'initialized': False
            }
    
    @staticmethod
    def check_wazuh_siem() -> Dict[str, Any]:
        """Check Wazuh SIEM health."""
        try:
            from gatekeeper_wazuh_integration import WazuhIntegration
            return {
                'component': 'wazuh_siem',
                'status': 'available',
                'initialized': True,
                'note': 'Requires server configuration'
            }
        except ImportError:
            return {
                'component': 'wazuh_siem',
                'status': 'warning',
                'error': 'Wazuh module not available',
                'initialized': False
            }
        except Exception as e:
            return {
                'component': 'wazuh_siem',
                'status': 'error',
                'error': str(e),
                'initialized': False
            }


# Global monitor instance
_monitor_instance = None


def get_health_monitor() -> SystemHealthMonitor:
    """Get or create global health monitor."""
    global _monitor_instance
    
    if _monitor_instance is None:
        _monitor_instance = SystemHealthMonitor()
        _monitor_instance.start_monitoring()
    
    return _monitor_instance


def perform_full_health_check() -> Dict[str, Any]:
    """Perform complete system health check."""
    monitor = get_health_monitor()
    
    # Check components
    checker = ComponentHealthChecker()
    component_checks = {
        'gatekeeper': checker.check_gatekeeper(),
        'omega_voice': checker.check_omega_voice(),
        'control_panel': checker.check_control_panel(),
        'wazuh_siem': checker.check_wazuh_siem()
    }
    
    # Update monitor with component status
    for comp_name, check_result in component_checks.items():
        status = check_result.get('status', 'unknown')
        monitor.update_component_status(comp_name, status)
    
    return {
        'timestamp': datetime.now().isoformat(),
        'system_health': monitor.get_health_report(),
        'component_checks': component_checks
    }


if __name__ == '__main__':
    import sys
    
    print("=" * 60)
    print("SYSTEM HEALTH CHECK - DETAILED REPORT")
    print("=" * 60)
    
    # Perform health check
    health_check = perform_full_health_check()
    
    # Print results
    print(f"\nOverall Status: {health_check['system_health']['overall_status']}")
    print(f"\nMetrics:")
    for metric_name, metric_data in health_check['system_health']['metrics'].items():
        status = metric_data['status'].upper()
        latest = metric_data['latest']['value']
        print(f"  {metric_name}: {latest:.2f} ({status})")
    
    print(f"\nComponents:")
    for comp_name, check in health_check['component_checks'].items():
        status = check.get('status', 'UNKNOWN').upper()
        initialized = "YES" if check.get('initialized') else "NO"
        print(f"  {comp_name}: {status} (Initialized: {initialized})")
    
    print(f"\nAlerts: {health_check['system_health']['alert_count']}")
    for alert in health_check['system_health']['recent_alerts'][-5:]:
        print(f"  [{alert['level']}] {alert['timestamp']}: {alert['message']}")
    
    # Save report
    monitor = get_health_monitor()
    report_file = monitor.export_report()
    print(f"\nDetailed report saved to: {report_file}")
    
    print("\n" + "=" * 60)
