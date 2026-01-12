#!/usr/bin/env python3
"""
Omega Monitoring Infrastructure
================================
Monitoring and logging infrastructure for Omega system.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from collections import defaultdict

# Try to import monitoring libraries
try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("[Monitoring] Prometheus not available. Install with: pip install prometheus-client")

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("[Monitoring] structlog not available. Install with: pip install structlog")

class OmegaMonitor:
    """Monitoring infrastructure for Omega"""
    
    def __init__(self, metrics_file: Optional[Path] = None):
        self.base_dir = Path(__file__).parent.absolute()
        self.metrics_file = metrics_file or (self.base_dir / "metrics.json")
        
        # Metrics storage
        self.metrics = {
            "counters": defaultdict(int),
            "histograms": defaultdict(list),
            "gauges": defaultdict(float),
            "timestamps": defaultdict(list)
        }
        
        # Prometheus metrics (if available)
        self.prometheus_counters = {}
        self.prometheus_histograms = {}
        self.prometheus_gauges = {}
        
        # Structured logger (if available)
        self.logger = None
        
        # Initialize Prometheus metrics
        if PROMETHEUS_AVAILABLE:
            self._initialize_prometheus()
        
        # Initialize structured logging
        if STRUCTLOG_AVAILABLE:
            self._initialize_logging()
    
    def _initialize_prometheus(self):
        """Initialize Prometheus metrics"""
        try:
            # Speech recognition metrics
            self.prometheus_counters["speech_recognition_total"] = Counter(
                'omega_speech_recognition_total',
                'Total number of speech recognition requests'
            )
            self.prometheus_counters["speech_recognition_errors"] = Counter(
                'omega_speech_recognition_errors_total',
                'Total number of speech recognition errors'
            )
            
            # TTS metrics
            self.prometheus_counters["tts_generation_total"] = Counter(
                'omega_tts_generation_total',
                'Total number of TTS generations'
            )
            self.prometheus_histograms["tts_generation_duration"] = Histogram(
                'omega_tts_generation_duration_seconds',
                'TTS generation duration in seconds'
            )
            
            # Voice security metrics
            self.prometheus_counters["voice_verification_total"] = Counter(
                'omega_voice_verification_total',
                'Total number of voice verifications'
            )
            self.prometheus_counters["voice_verification_authorized"] = Counter(
                'omega_voice_verification_authorized_total',
                'Total number of authorized voice verifications'
            )
            
            # Confidence metrics
            self.prometheus_histograms["confidence_scores"] = Histogram(
                'omega_confidence_scores',
                'Confidence scores distribution',
                buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            )
            
            print("[Monitoring] Prometheus metrics initialized")
        except Exception as e:
            print(f"[Monitoring] Prometheus initialization failed: {e}")
    
    def _initialize_logging(self):
        """Initialize structured logging"""
        try:
            structlog.configure(
                processors=[
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.add_log_level,
                    structlog.processors.JSONRenderer()
                ],
                wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
                context_class=dict,
                logger_factory=structlog.PrintLoggerFactory(),
                cache_logger_on_first_use=True,
            )
            self.logger = structlog.get_logger()
            print("[Monitoring] Structured logging initialized")
        except Exception as e:
            print(f"[Monitoring] Logging initialization failed: {e}")
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        self.metrics["counters"][name] += value
        
        if name in self.prometheus_counters:
            if labels:
                self.prometheus_counters[name].labels(**labels).inc(value)
            else:
                self.prometheus_counters[name].inc(value)
    
    def record_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a histogram value"""
        self.metrics["histograms"][name].append(value)
        self.metrics["timestamps"][name].append(datetime.now().isoformat())
        
        if name in self.prometheus_histograms:
            if labels:
                self.prometheus_histograms[name].labels(**labels).observe(value)
            else:
                self.prometheus_histograms[name].observe(value)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge value"""
        self.metrics["gauges"][name] = value
        
        if name in self.prometheus_gauges:
            if labels:
                self.prometheus_gauges[name].labels(**labels).set(value)
            else:
                self.prometheus_gauges[name].set(value)
    
    def log_event(self, event: str, level: str = "info", **kwargs):
        """Log an event with structured logging"""
        if self.logger:
            log_func = getattr(self.logger, level, self.logger.info)
            log_func(event, **kwargs)
        else:
            # Fallback to print
            print(f"[{level.upper()}] {event} {kwargs if kwargs else ''}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return {
            "counters": dict(self.metrics["counters"]),
            "histograms": {
                name: {
                    "count": len(values),
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                    "mean": sum(values) / len(values) if values else 0,
                    "values": values[-100:]  # Last 100 values
                }
                for name, values in self.metrics["histograms"].items()
            },
            "gauges": dict(self.metrics["gauges"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            metrics_data = self.get_metrics()
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2)
        except Exception as e:
            print(f"[Monitoring] Error saving metrics: {e}")
    
    def start_prometheus_server(self, port: int = 8000):
        """Start Prometheus HTTP server"""
        if PROMETHEUS_AVAILABLE:
            try:
                start_http_server(port)
                print(f"[Monitoring] Prometheus server started on port {port}")
            except Exception as e:
                print(f"[Monitoring] Error starting Prometheus server: {e}")

# Global monitor instance
_monitor = None

def get_monitor() -> OmegaMonitor:
    """Get global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = OmegaMonitor()
    return _monitor

def increment_counter(name: str, value: int = 1, labels: Optional[Dict[str, str]] = None):
    """Increment a counter"""
    get_monitor().increment_counter(name, value, labels)

def record_histogram(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Record a histogram value"""
    get_monitor().record_histogram(name, value, labels)

def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Set a gauge value"""
    get_monitor().set_gauge(name, value, labels)

def log_event(event: str, level: str = "info", **kwargs):
    """Log an event"""
    get_monitor().log_event(event, level, **kwargs)

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 20 + "OMEGA MONITORING INFRASTRUCTURE")
    print("=" * 80)
    print()
    
    monitor = OmegaMonitor()
    print("[OK] Monitoring infrastructure initialized")
    print(f"  - Prometheus available: {PROMETHEUS_AVAILABLE}")
    print(f"  - Structured logging available: {STRUCTLOG_AVAILABLE}")
    print()
    print("Usage:")
    print("  from omega_monitoring import increment_counter, record_histogram, log_event")
    print("  increment_counter('speech_recognition_total')")
    print("  record_histogram('tts_generation_duration', 1.5)")
    print("  log_event('user_interaction', level='info', user_id='123')")
    print()
    print("Start Prometheus server:")
    print("  monitor = get_monitor()")
    print("  monitor.start_prometheus_server(port=8000)")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
