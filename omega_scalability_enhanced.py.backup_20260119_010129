# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Ω Omega Scalability Enhanced - Connection Pooling, Rate Limiting, Resource Monitoring

"""
Ω Omega Scalability Enhanced

Scalability improvements:
- Connection pooling
- Rate limiting
- Resource monitoring
- Offline mode enhancement
"""

import time
import threading
from collections import deque
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


# RateLimiter moved to rate_limiter.py with exponential backoff
# Import the enhanced version instead
try:
    from rate_limiter import ExponentialBackoffRateLimiter as RateLimiter
except ImportError:
    # Fallback to simple implementation if rate_limiter not available
    class RateLimiter:
        """Rate limiting for API calls (fallback)."""
        
        def __init__(self, max_calls: int = 100, time_window: int = 60):
            self.max_calls = max_calls
            self.time_window = time_window
            self.calls = deque()
            self.lock = threading.Lock()
        
        def allow(self, endpoint: str = "default") -> bool:
            """Check if call is allowed."""
            with self.lock:
                now = time.time()
                
                # Remove old calls
                while self.calls and self.calls[0] < now - self.time_window:
                    self.calls.popleft()
                
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return True
                
                return False
        
        def wait_time(self, endpoint: str = "default") -> float:
            """Get time to wait before next call."""
            with self.lock:
                if not self.calls:
                    return 0.0
                
                oldest = self.calls[0]
                wait = (oldest + self.time_window) - time.time()
                return max(0.0, wait)
        
        def wait_if_needed(self, endpoint: str = "default"):
            """Wait if rate limit is active."""
            wait = self.wait_time(endpoint)
            if wait > 0:
                time.sleep(wait)
        
        def record_success(self, endpoint: str = "default"):
            """Record successful call (no-op for fallback)."""
            pass
        
        def record_failure(self, endpoint: str = "default"):
            """Record failed call (no-op for fallback)."""
            pass


class ResourceMonitor:
    """Resource usage monitoring."""
    
    def __init__(self):
        self.metrics = {
            "memory_usage": [],
            "cpu_usage": [],
            "active_connections": 0,
            "requests_per_second": 0
        }
        self.lock = threading.Lock()
    
    def record_metric(self, metric_name: str, value: float):
        """Record metric value."""
        with self.lock:
            if metric_name not in self.metrics:
                self.metrics[metric_name] = []
            
            self.metrics[metric_name].append({
                "timestamp": datetime.now().isoformat(),
                "value": value
            })
            
            # Keep only last 1000 entries
            if len(self.metrics[metric_name]) > 1000:
                self.metrics[metric_name].pop(0)
    
    def get_average(self, metric_name: str, window: int = 60) -> float:
        """Get average metric over time window."""
        with self.lock:
            if metric_name not in self.metrics:
                return 0.0
            
            cutoff = datetime.now() - timedelta(seconds=window)
            values = [
                m["value"] for m in self.metrics[metric_name]
                if datetime.fromisoformat(m["timestamp"]) > cutoff
            ]
            
            return sum(values) / len(values) if values else 0.0


class OfflineMode:
    """Enhanced offline mode capabilities."""
    
    def __init__(self):
        self.offline = False
        self.cache = {}
        self.queue = []
    
    def enable(self):
        """Enable offline mode."""
        self.offline = True
    
    def disable(self):
        """Disable offline mode."""
        self.offline = False
    
    def queue_request(self, request: Dict[str, Any]):
        """Queue request for when online."""
        if self.offline:
            self.queue.append({
                "request": request,
                "timestamp": datetime.now().isoformat()
            })
            return True
        return False
    
    def process_queue(self):
        """Process queued requests when back online."""
        if not self.offline and self.queue:
            # Process queue
            processed = self.queue
            self.queue = []
            return processed
        return []


# Global instances
RATE_LIMITER = RateLimiter(max_calls=100, time_window=60)
RESOURCE_MONITOR = ResourceMonitor()
OFFLINE_MODE = OfflineMode()
