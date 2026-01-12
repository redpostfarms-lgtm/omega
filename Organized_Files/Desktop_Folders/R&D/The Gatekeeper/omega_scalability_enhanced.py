# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Scalability Enhanced Module

"""
Scalability enhancements for Omega system:
- Rate limiting
- Resource monitoring
- Offline mode
"""

import time
import threading
import psutil
from typing import Dict, List, Optional, Any
from collections import deque
from datetime import datetime
import logging

logger = logging.getLogger('OmegaScalability')

class RateLimiter:
    """Rate limiter for API calls and operations."""
    
    def __init__(self, max_calls: int = 10, period: float = 1.0):
        self.max_calls = max_calls
        self.period = period
        self.calls: deque = deque()
        self.lock = threading.Lock()
    
    def allow(self) -> bool:
        """Check if call is allowed."""
        with self.lock:
            now = time.time()
            
            # Remove old calls
            while self.calls and self.calls[0] < now - self.period:
                self.calls.popleft()
            
            # Check if we can make a call
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Get time to wait before next call."""
        with self.lock:
            if not self.calls:
                return 0.0
            
            oldest = self.calls[0]
            elapsed = time.time() - oldest
            wait = max(0.0, self.period - elapsed)
            return wait

class ResourceMonitor:
    """Monitor system resource usage."""
    
    def __init__(self):
        self.metrics: Dict[str, deque] = {}
        self.lock = threading.Lock()
        self.process = psutil.Process()
    
    def record_metric(self, name: str, value: float, max_history: int = 1000):
        """Record a metric."""
        with self.lock:
            if name not in self.metrics:
                self.metrics[name] = deque(maxlen=max_history)
            self.metrics[name].append((time.time(), value))
    
    def get_average(self, name: str, window_seconds: float = 60.0) -> float:
        """Get average metric over time window."""
        with self.lock:
            if name not in self.metrics:
                return 0.0
            
            now = time.time()
            cutoff = now - window_seconds
            values = [v for t, v in self.metrics[name] if t >= cutoff]
            
            if not values:
                return 0.0
            
            return sum(values) / len(values)
    
    def get_current_usage(self) -> Dict[str, float]:
        """Get current resource usage."""
        try:
            cpu_percent = self.process.cpu_percent(interval=0.1)
            memory_info = self.process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            return {
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.warning(f"Failed to get resource usage: {e}")
            return {
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "timestamp": time.time()
            }

class OfflineMode:
    """Offline mode handler."""
    
    def __init__(self):
        self.offline = False
        self.cached_data: Dict[str, Any] = {}
    
    def set_offline(self, offline: bool = True):
        """Set offline mode."""
        self.offline = offline
        logger.info(f"Offline mode: {offline}")
    
    def is_offline(self) -> bool:
        """Check if offline mode is active."""
        return self.offline
    
    def cache_data(self, key: str, data: Any):
        """Cache data for offline use."""
        self.cached_data[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def get_cached(self, key: str, max_age: float = 3600.0) -> Optional[Any]:
        """Get cached data."""
        if key not in self.cached_data:
            return None
        
        cached = self.cached_data[key]
        age = time.time() - cached["timestamp"]
        
        if age > max_age:
            return None
        
        return cached["data"]

# Global instances
RATE_LIMITER = RateLimiter()
RESOURCE_MONITOR = ResourceMonitor()
OFFLINE_MODE = OfflineMode()
