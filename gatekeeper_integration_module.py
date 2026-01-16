#!/usr/bin/env python3
"""
Gatekeeper Unified Integration Module
=====================================
Comprehensive integration system combining:
- Gatekeeper security & threat detection
- Omega AI voice system  
- Control panel web interface
- System health monitoring & diagnostics
- Error handling & recovery
- Wazuh SIEM integration

This is the main entry point for all Gatekeeper-Omega system functionality.
"""

import logging
import logging.handlers
import traceback
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
from functools import wraps
import sys
import os

# Optional imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ============================================================================
# CONFIGURATION & ENUMERATIONS
# ============================================================================

class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class SystemStatus(Enum):
    """System health status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


# ============================================================================
# ERROR HANDLING & LOGGING
# ============================================================================

class ErrorContext:
    """Context information for errors"""
    def __init__(self, component: str, operation: str, **kwargs):
        self.component = component
        self.operation = operation
        self.context = kwargs
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            'component': self.component,
            'operation': self.operation,
            'context': self.context,
            'timestamp': self.timestamp
        }


class SystemErrorHandler:
    """Centralized error handling for all system components"""
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging with rotation
        self.logger = logging.getLogger('GatekeeperSystem')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        log_file = self.log_dir / 'gatekeeper_system.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Error tracking
        self.errors = deque(maxlen=100)
        self.recovery_handlers: Dict[str, Callable] = {}
        self.lock = threading.RLock()
    
    def register_recovery_handler(self, component: str, handler: Callable):
        """Register custom recovery handler for component"""
        with self.lock:
            self.recovery_handlers[component] = handler
            self.logger.info(f"Registered recovery handler for {component}")
    
    def handle_error(
        self, 
        error: Exception, 
        context: ErrorContext,
        recover: bool = True
    ) -> Dict[str, Any]:
        """
        Handle error with context and attempt recovery
        
        Args:
            error: The exception that occurred
            context: ErrorContext with component/operation info
            recover: Whether to attempt recovery (default: True)
            
        Returns:
            Dictionary with error info and recovery status
        """
        with self.lock:
            error_info = {
                'timestamp': datetime.now().isoformat(),
                'severity': ErrorSeverity.ERROR.value,
                'error_type': type(error).__name__,
                'error_message': str(error),
                'context': context.to_dict(),
                'traceback': traceback.format_exc()
            }
            
            self.errors.append(error_info)
            
            # Log the error
            self.logger.error(
                f"[{context.component}] {context.operation}: {str(error)}",
                exc_info=True
            )
            
            # Attempt recovery if enabled
            recovery_info = None
            if recover and context.component in self.recovery_handlers:
                try:
                    recovery_handler = self.recovery_handlers[context.component]
                    recovery_info = recovery_handler(error, context)
                    error_info['recovered'] = True
                    error_info['recovery_info'] = recovery_info
                    self.logger.info(f"Recovery attempted for {context.component}")
                except Exception as recovery_error:
                    error_info['recovery_failed'] = True
                    error_info['recovery_error'] = str(recovery_error)
                    self.logger.error(f"Recovery failed: {recovery_error}", exc_info=True)
            
            return error_info
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent errors"""
        with self.lock:
            return list(self.errors)[-count:]
    
    def clear_errors(self):
        """Clear error log"""
        with self.lock:
            self.errors.clear()
            self.logger.info("Error log cleared")


# ============================================================================
# HEALTH MONITORING & METRICS
# ============================================================================

class HealthMetric:
    """Single health metric with history"""
    
    def __init__(self, name: str, max_history: int = 100):
        self.name = name
        self.history = deque(maxlen=max_history)
        self.latest = None
        self.threshold_warning = None
        self.threshold_critical = None
    
    def record(self, value: Any, timestamp: Optional[datetime] = None) -> None:
        """Record a metric value"""
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
        """Get status: healthy, warning, or critical"""
        if not self.latest:
            return 'unknown'
        
        value = self.latest['value']
        
        if self.threshold_critical and value > self.threshold_critical:
            return 'critical'
        if self.threshold_warning and value > self.threshold_warning:
            return 'warning'
        
        return 'healthy'
    
    def get_average(self) -> Optional[float]:
        """Calculate average value from history"""
        if not self.history:
            return None
        
        numeric_values = []
        for entry in self.history:
            if isinstance(entry['value'], (int, float)):
                numeric_values.append(entry['value'])
        
        return sum(numeric_values) / len(numeric_values) if numeric_values else None


class ComponentHealthChecker:
    """Checks health of individual components"""
    
    def __init__(self, error_handler: SystemErrorHandler):
        self.error_handler = error_handler
    
    def check_gatekeeper(self, gatekeeper) -> Dict[str, Any]:
        """Check Gatekeeper component health"""
        if not gatekeeper:
            return {'status': 'unavailable', 'component': 'gatekeeper'}
        
        try:
            status = gatekeeper.get_status() if hasattr(gatekeeper, 'get_status') else {}
            return {
                'status': 'healthy',
                'component': 'gatekeeper',
                'modules': status.get('modules', {})
            }
        except Exception as e:
            ctx = ErrorContext('gatekeeper', 'health_check')
            self.error_handler.handle_error(e, ctx)
            return {'status': 'error', 'component': 'gatekeeper', 'error': str(e)}
    
    def check_omega(self, omega) -> Dict[str, Any]:
        """Check Omega voice system health"""
        if not omega:
            return {'status': 'unavailable', 'component': 'omega_voice'}
        
        try:
            return {
                'status': 'healthy',
                'component': 'omega_voice',
                'available': True
            }
        except Exception as e:
            ctx = ErrorContext('omega_voice', 'health_check')
            self.error_handler.handle_error(e, ctx)
            return {'status': 'error', 'component': 'omega_voice', 'error': str(e)}
    
    def check_control_panel(self, control_panel) -> Dict[str, Any]:
        """Check Control Panel availability"""
        if not control_panel:
            return {'status': 'unavailable', 'component': 'control_panel'}
        
        return {'status': 'healthy', 'component': 'control_panel', 'available': True}
    
    def check_wazuh(self, wazuh) -> Dict[str, Any]:
        """Check Wazuh SIEM integration"""
        if not wazuh:
            return {'status': 'unavailable', 'component': 'wazuh_siem'}
        
        return {'status': 'healthy', 'component': 'wazuh_siem', 'available': True}


class SystemHealthMonitor:
    """Real-time system health monitoring and diagnostics"""
    
    def __init__(self, error_handler: SystemErrorHandler, check_interval: int = 60):
        self.error_handler = error_handler
        self.check_interval = check_interval
        self.metrics: Dict[str, HealthMetric] = {}
        self.alerts: deque = deque(maxlen=100)
        self.is_running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
        self.component_checker = ComponentHealthChecker(error_handler)
        
        self._initialize_metrics()
    
    def _initialize_metrics(self):
        """Initialize all system metrics"""
        with self.lock:
            # CPU metric
            cpu_metric = HealthMetric('cpu_percent')
            cpu_metric.threshold_warning = 80
            cpu_metric.threshold_critical = 95
            self.metrics['cpu_percent'] = cpu_metric
            
            # Memory metric
            memory_metric = HealthMetric('memory_percent')
            memory_metric.threshold_warning = 80
            memory_metric.threshold_critical = 95
            self.metrics['memory_percent'] = memory_metric
            
            # Disk metric
            disk_metric = HealthMetric('disk_usage_percent')
            disk_metric.threshold_warning = 80
            disk_metric.threshold_critical = 90
            self.metrics['disk_usage_percent'] = disk_metric
            
            # Process count
            self.metrics['process_count'] = HealthMetric('process_count')
            
            # System uptime
            self.metrics['uptime_seconds'] = HealthMetric('uptime_seconds')
    
    def start_monitoring(self):
        """Start background health monitoring"""
        if self.is_running:
            self.error_handler.logger.warning("Monitoring already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.thread.start()
        self.error_handler.logger.info("System health monitoring started")
    
    def stop_monitoring(self):
        """Stop background health monitoring"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.error_handler.logger.info("System health monitoring stopped")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_running:
            try:
                self._collect_metrics()
                time.sleep(self.check_interval)
            except Exception as e:
                ctx = ErrorContext('health_monitor', 'monitoring_loop')
                self.error_handler.handle_error(e, ctx)
    
    def _collect_metrics(self):
        """Collect all system metrics"""
        with self.lock:
            try:
                if not PSUTIL_AVAILABLE:
                    self.error_handler.logger.warning("psutil not available, skipping metrics collection")
                    return
                
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self.metrics['cpu_percent'].record(cpu_percent)
                
                # Memory
                memory = psutil.virtual_memory()
                self.metrics['memory_percent'].record(memory.percent)
                
                # Disk
                disk = psutil.disk_usage('/')
                self.metrics['disk_usage_percent'].record(disk.percent)
                
                # Processes
                self.metrics['process_count'].record(len(psutil.pids()))
                
                # Uptime
                try:
                    uptime = time.time() - psutil.boot_time()
                except:
                    uptime = 0
                self.metrics['uptime_seconds'].record(uptime)
                
                # Check thresholds
                self._check_thresholds()
            
            except Exception as e:
                ctx = ErrorContext('health_monitor', 'collect_metrics')
                self.error_handler.handle_error(e, ctx, recover=False)
    
    def _check_thresholds(self):
        """Check metrics against thresholds and generate alerts"""
        for metric_name, metric in self.metrics.items():
            status = metric.get_status()
            
            if status == 'critical':
                self._generate_alert(metric_name, 'critical', metric.latest)
            elif status == 'warning':
                self._generate_alert(metric_name, 'warning', metric.latest)
    
    def _generate_alert(self, metric_name: str, level: str, value: Dict):
        """Generate system alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric_name,
            'level': level,
            'value': value
        }
        self.alerts.append(alert)
        
        level_str = '⚠️ WARNING' if level == 'warning' else '🚨 CRITICAL'
        self.error_handler.logger.warning(
            f"{level_str}: {metric_name} = {value['value']}"
        )
    
    def get_current_health(self) -> Dict[str, Any]:
        """Get current system health snapshot"""
        with self.lock:
            health = {
                'timestamp': datetime.now().isoformat(),
                'metrics': {}
            }
            
            for name, metric in self.metrics.items():
                health['metrics'][name] = {
                    'current': metric.latest,
                    'average': metric.get_average(),
                    'status': metric.get_status(),
                    'history_count': len(metric.history)
                }
            
            return health
    
    def perform_full_health_check(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive health check of all components"""
        with self.lock:
            health_check = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': self.get_current_health(),
                'components': {}
            }
            
            # Check each component
            if components.get('gatekeeper'):
                health_check['components']['gatekeeper'] = \
                    self.component_checker.check_gatekeeper(components['gatekeeper'])
            
            if components.get('omega_voice'):
                health_check['components']['omega_voice'] = \
                    self.component_checker.check_omega(components['omega_voice'])
            
            if components.get('control_panel'):
                health_check['components']['control_panel'] = \
                    self.component_checker.check_control_panel(components['control_panel'])
            
            if components.get('wazuh'):
                health_check['components']['wazuh'] = \
                    self.component_checker.check_wazuh(components['wazuh'])
            
            return health_check
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get most recent alerts"""
        with self.lock:
            return list(self.alerts)[-count:]


# ============================================================================
# MAIN INTEGRATION ENGINE
# ============================================================================

class GatekeeperIntegration:
    """
    Main integration class for all Gatekeeper-Omega system functionality.
    Combines security, voice, monitoring, error handling, and web interface.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """Initialize Gatekeeper integration system"""
        self.config_file = config_file or Path("gatekeeper_integration_config.json")
        self.config = self._load_config()
        
        # Initialize error handler
        log_dir = self.config.get('log_directory', 'logs')
        self.error_handler = SystemErrorHandler(log_dir)
        
        # Initialize health monitor
        check_interval = self.config.get('health_check_interval', 60)
        self.health_monitor = SystemHealthMonitor(self.error_handler, check_interval)
        
        # Initialize components
        self.components = {}
        self.status = SystemStatus.OFFLINE
        self.errors = []
        self.lock = threading.RLock()
        self.initialized_at = datetime.now()
        
        self.error_handler.logger.info("=" * 60)
        self.error_handler.logger.info("Gatekeeper Integration System Initializing")
        self.error_handler.logger.info("=" * 60)
        
        self._initialize_all_components()
        
        # Start health monitoring if enabled
        if self.config.get('enable_health_monitoring', True):
            self.health_monitor.start_monitoring()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            'enable_threat_simulation': True,
            'enable_forensic_analysis': True,
            'enable_monitoring': True,
            'enable_wazuh': False,
            'enable_health_monitoring': True,
            'log_directory': 'logs',
            'metrics_file': 'system_metrics.json',
            'health_check_interval': 60,
            'auto_collect_metrics': True,
            'wazuh': {
                'host': 'localhost',
                'port': 55000,
                'protocol': 'https',
                'username': 'wazuh-wui',
                'password': None,
                'verify_ssl': False
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.error_handler.logger.info(f"Config saved to {self.config_file}")
        except Exception as e:
            ctx = ErrorContext('integration', 'save_config')
            self.error_handler.handle_error(Exception(str(e)), ctx)
    
    def _initialize_all_components(self):
        """Initialize all system components"""
        components_to_init = [
            ('threat_simulator', self._init_threat_simulator),
            ('forensic_analyzer', self._init_forensic_analyzer),
            ('monitor', self._init_enhanced_monitor),
            ('gatekeeper', self._init_gatekeeper),
            ('omega_voice', self._init_omega_voice),
            ('control_panel', self._init_control_panel),
            ('wazuh', self._init_wazuh),
        ]
        
        successful = 0
        for name, init_func in components_to_init:
            try:
                self.error_handler.logger.info(f"Initializing {name}...")
                component = init_func()
                if component:
                    self.components[name] = component
                    self.error_handler.logger.info(f"✓ {name} initialized successfully")
                    successful += 1
                else:
                    self.error_handler.logger.warning(f"✗ {name} returned None")
            except Exception as e:
                ctx = ErrorContext('integration', f'init_{name}')
                self.error_handler.handle_error(e, ctx, recover=False)
                self.errors.append({
                    'component': name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Determine overall status
        if successful >= 4:
            self.status = SystemStatus.HEALTHY
            self.error_handler.logger.info("✓ INITIALIZATION SUCCESSFUL")
        elif successful >= 2:
            self.status = SystemStatus.WARNING
            self.error_handler.logger.warning("⚠️ INITIALIZATION PARTIAL - Some components failed")
        else:
            self.status = SystemStatus.CRITICAL
            self.error_handler.logger.critical("✗ INITIALIZATION FAILED - Critical components unavailable")
    
    def _init_threat_simulator(self) -> Optional[Any]:
        """Initialize threat simulator"""
        if not self.config.get('enable_threat_simulation'):
            return None
        try:
            from gatekeeper_threat_simulation import ThreatSimulator
            return ThreatSimulator()
        except ImportError:
            return None
    
    def _init_forensic_analyzer(self) -> Optional[Any]:
        """Initialize forensic analyzer"""
        if not self.config.get('enable_forensic_analysis'):
            return None
        try:
            from gatekeeper_forensic_analysis import ForensicAnalyzer
            log_dir = Path(self.config.get('log_directory', 'logs'))
            return ForensicAnalyzer(log_dir)
        except ImportError:
            return None
    
    def _init_enhanced_monitor(self) -> Optional[Any]:
        """Initialize enhanced monitor"""
        if not self.config.get('enable_monitoring'):
            return None
        try:
            from gatekeeper_enhanced_monitoring import EnhancedMonitor
            metrics_file = Path(self.config.get('metrics_file', 'system_metrics.json'))
            monitor = EnhancedMonitor(metrics_file)
            monitor.load_metrics()
            return monitor
        except ImportError:
            return None
    
    def _init_gatekeeper(self) -> Optional[Any]:
        """Initialize Gatekeeper component (self-reference)"""
        return self
    
    def _init_omega_voice(self) -> Optional[Any]:
        """Initialize Omega voice system"""
        try:
            try:
                import omega_full_brain
                return omega_full_brain
            except ImportError:
                try:
                    import omega_simple_final
                    return omega_simple_final
                except ImportError:
                    return None
        except Exception:
            return None
    
    def _init_control_panel(self) -> Optional[Any]:
        """Initialize Control Panel web interface"""
        try:
            from omega_control_panel_web import app
            return app
        except ImportError:
            return None
    
    def _init_wazuh(self) -> Optional[Any]:
        """Initialize Wazuh SIEM integration"""
        if not self.config.get('enable_wazuh'):
            return None
        try:
            from gatekeeper_wazuh_integration import WazuhIntegration
            return WazuhIntegration
        except ImportError:
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        with self.lock:
            return {
                'timestamp': datetime.now().isoformat(),
                'system_status': self.status.value,
                'uptime_seconds': (datetime.now() - self.initialized_at).total_seconds(),
                'components_loaded': len(self.components),
                'modules': {
                    'threat_simulation': {
                        'available': self.components.get('threat_simulator') is not None,
                        'enabled': self.config.get('enable_threat_simulation')
                    },
                    'forensic_analysis': {
                        'available': self.components.get('forensic_analyzer') is not None,
                        'enabled': self.config.get('enable_forensic_analysis')
                    },
                    'monitoring': {
                        'available': self.components.get('monitor') is not None,
                        'enabled': self.config.get('enable_monitoring')
                    },
                    'omega_voice': {
                        'available': self.components.get('omega_voice') is not None
                    },
                    'control_panel': {
                        'available': self.components.get('control_panel') is not None
                    },
                    'wazuh_siem': {
                        'available': self.components.get('wazuh') is not None,
                        'enabled': self.config.get('enable_wazuh')
                    }
                },
                'error_count': len(self.errors),
                'recent_errors': self.errors[-5:]
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        monitor = self.components.get('monitor')
        if not monitor:
            return {'error': 'Monitoring not available'}
        
        try:
            metrics = monitor.collect_metrics()
            return {
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'memory_used_mb': metrics.memory_used_mb,
                'disk_usage_percent': metrics.disk_usage_percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            ctx = ErrorContext('integration', 'get_system_metrics')
            self.error_handler.handle_error(e, ctx)
            return {'error': str(e)}
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        return self.health_monitor.perform_full_health_check(self.components)
    
    def run_threat_simulation(self, scenario_name: Optional[str] = None) -> Dict[str, Any]:
        """Run threat simulation"""
        simulator = self.components.get('threat_simulator')
        if not simulator:
            return {'error': 'Threat simulation not available'}
        
        try:
            if scenario_name:
                result = simulator.simulate_scenario(scenario_name)
            else:
                result = simulator.run_random_simulation()
            return result
        except Exception as e:
            ctx = ErrorContext('threat_simulator', 'run_simulation')
            self.error_handler.handle_error(e, ctx)
            return {'error': str(e)}
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics"""
        self.error_handler.logger.info("Running system diagnostics...")
        
        diagnostics = {
            'timestamp': datetime.now().isoformat(),
            'system_status': self.get_status(),
            'system_health': self.get_system_health(),
            'system_metrics': self.get_system_metrics(),
            'recent_errors': self.error_handler.get_recent_errors(5),
            'recent_alerts': self.health_monitor.get_recent_alerts(5)
        }
        
        self.error_handler.logger.info(f"Diagnostics complete - Status: {diagnostics['system_status']['system_status']}")
        return diagnostics
    
    def save_diagnostics(self, filename: str = 'system_diagnostics.json') -> Optional[str]:
        """Save diagnostics report to file"""
        try:
            diagnostics = self.run_diagnostics()
            with open(filename, 'w') as f:
                json.dump(diagnostics, f, indent=2, default=str)
            self.error_handler.logger.info(f"Diagnostics saved to {filename}")
            return filename
        except Exception as e:
            ctx = ErrorContext('integration', 'save_diagnostics')
            self.error_handler.handle_error(e, ctx)
            return None
    
    def shutdown(self):
        """Gracefully shutdown the system"""
        self.error_handler.logger.info("=" * 60)
        self.error_handler.logger.info("Gatekeeper Integration System Shutting Down")
        self.error_handler.logger.info("=" * 60)
        
        # Stop health monitoring
        self.health_monitor.stop_monitoring()
        
        # Save final diagnostics
        self.save_diagnostics('gatekeeper_final_diagnostics.json')
        
        self.error_handler.logger.info("✓ Shutdown complete")
    
    def run_threat_simulation(self, scenario_name: Optional[str] = None) -> Dict[str, Any]:
        """Run a threat simulation."""
        if not self.threat_simulator:
            return {'error': 'Threat simulation not available'}
        
        if scenario_name:
            try:
                result = self.threat_simulator.simulate_scenario(scenario_name)
            except ValueError as e:
                return {'error': str(e)}
        else:
            result = self.threat_simulator.run_random_simulation()
        
        return result
    
    def analyze_log_file(self, log_file: Path) -> Dict[str, Any]:
        """Analyze a log file for threats."""
        if not self.forensic_analyzer:
            return {'error': 'Forensic analysis not available'}
        
        return self.forensic_analyzer.analyze_log_file(log_file)
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        if not self.monitor:
            return {'error': 'Monitoring not available'}
        
        metrics = self.monitor.collect_metrics()
        summary = self.monitor.get_metrics_summary()
        
        return {
            'current_metrics': {
                'cpu_percent': metrics.cpu_percent,
                'memory_percent': metrics.memory_percent,
                'memory_used_mb': metrics.memory_used_mb,
                'disk_usage_percent': metrics.disk_usage_percent,
            },
            'summary': summary
        }
    
    def get_wazuh_threats(
        self,
        min_level: int = 7,
        hours: int = 1
    ) -> Dict[str, Any]:
        """
        Get recent threats from Wazuh.
        
        Args:
            min_level: Minimum alert level (default: 7)
            hours: Hours to look back (default: 1)
            
        Returns:
            Dictionary with threats or error
        """
        if not self.wazuh_integration:
            return {'error': 'Wazuh integration not available'}
        
        threats = self.wazuh_integration.get_recent_threats(min_level=min_level, hours=hours)
        return {
            'threats': threats,
            'count': len(threats),
            'source': 'wazuh'
        }
    
    def get_wazuh_status(self) -> Dict[str, Any]:
        """Get Wazuh integration status."""
        if not self.wazuh_integration:
            return {'error': 'Wazuh integration not available'}
        
        return self.wazuh_integration.get_status_report()


# ============================================================================
# GLOBAL INTEGRATION INSTANCE & UTILITIES
# ============================================================================

_integration_instance: Optional[GatekeeperIntegration] = None
_integration_lock = threading.Lock()


def get_integration() -> GatekeeperIntegration:
    """Get or create the global integration instance"""
    global _integration_instance
    
    if _integration_instance is None:
        with _integration_lock:
            if _integration_instance is None:
                _integration_instance = GatekeeperIntegration()
    
    return _integration_instance


def integration_component(component_name: str):
    """Decorator to automatically use integration component"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            integration = get_integration()
            component = integration.components.get(component_name)
            if not component:
                raise RuntimeError(f"Component '{component_name}' not available")
            return func(component, *args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point - System status and diagnostics"""
    print("\n" + "=" * 70)
    print("GATEKEEPER UNIFIED INTEGRATION SYSTEM - STATUS REPORT")
    print("=" * 70 + "\n")
    
    try:
        # Initialize system
        integration = get_integration()
        
        # Print status
        status = integration.get_status()
        print(f"System Status: {status['system_status'].upper()}")
        print(f"Components Loaded: {status['components_loaded']}/6")
        print(f"Uptime: {status['uptime_seconds']:.1f} seconds")
        print(f"Errors: {status['error_count']}")
        
        # Print module status
        print("\n" + "-" * 70)
        print("MODULE STATUS:")
        print("-" * 70)
        for module_name, module_status in status['modules'].items():
            available = "✓" if module_status.get('available') else "✗"
            enabled = module_status.get('enabled', 'N/A')
            print(f"  {available} {module_name:20s} - Available: {module_status.get('available')}, Enabled: {enabled}")
        
        # Print system health
        print("\n" + "-" * 70)
        print("SYSTEM HEALTH:")
        print("-" * 70)
        health = integration.get_system_health()
        if health.get('system_metrics'):
            metrics = health['system_metrics'].get('metrics', {})
            for metric_name, metric_data in metrics.items():
                if metric_data['current']:
                    print(f"  {metric_name:20s}: {metric_data['current']['value']:.1f} ({metric_data['status']})")
        
        # Run full diagnostics
        print("\n" + "-" * 70)
        print("RUNNING FULL DIAGNOSTICS...")
        print("-" * 70)
        diagnostics = integration.run_diagnostics()
        report_file = integration.save_diagnostics()
        
        if report_file:
            print(f"✓ Diagnostics saved to: {report_file}\n")
        
        print("=" * 70)
        print("✓ SYSTEM READY FOR OPERATION")
        print("=" * 70 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n✗ SYSTEM INITIALIZATION FAILED: {e}\n")
        traceback.print_exc()
        return 1


def main():
    """Main function for testing integration."""
    print("=== Gatekeeper Integration Module Test ===\n")
    
    integration = GatekeeperIntegration()
    
    print("=== Integration Status ===")
    status = integration.get_status()
    print(f"Threat Simulation: {'✓' if status['modules']['threat_simulation']['enabled'] else '✗'}")
    print(f"Forensic Analysis: {'✓' if status['modules']['forensic_analysis']['enabled'] else '✗'}")
    print(f"Monitoring: {'✓' if status['modules']['monitoring']['enabled'] else '✗'}")
    print(f"Wazuh Integration: {'✓' if status['modules']['wazuh']['enabled'] else '✗'} (Available: {status['modules']['wazuh']['available']})")
    
    if integration.monitor:
        print("\n=== System Metrics ===")
        metrics = integration.get_system_metrics()
        current = metrics['current_metrics']
        print(f"CPU: {current['cpu_percent']:.1f}%")
        print(f"Memory: {current['memory_percent']:.1f}% ({current['memory_used_mb']:.0f} MB used)")
        if current.get('disk_usage_percent'):
            print(f"Disk: {current['disk_usage_percent']:.1f}%")
    
    if integration.threat_simulator:
        print("\n=== Threat Simulation Test ===")
        result = integration.run_threat_simulation()
        if 'error' not in result:
            print(f"Scenario: {result['scenario']['name']}")
            print(f"Events: {result['total_events']}")
            print(f"Status: {result['status']}")
    
    print("\n=== Generating Report ===")
    report_msg = integration.generate_full_report()
    print(f"  {report_msg}")
    
    print("\n✓ Integration module test complete!")


if __name__ == "__main__":
    main()
