# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Rate Limiter with Exponential Backoff for API Calls

"""
Rate Limiter with Exponential Backoff

Features:
- Rate limiting per API endpoint
- Exponential backoff on failures
- Thread-safe operations
- Configurable retry strategies
"""

import time
import threading
import random
from collections import deque
from typing import Optional, Callable, Any, Dict
from functools import wraps
from datetime import datetime, timedelta


class ExponentialBackoffRateLimiter:
    """Rate limiter with exponential backoff for API calls."""
    
    def __init__(
        self,
        max_calls: int = 100,
        time_window: int = 60,
        initial_backoff: float = 1.0,
        max_backoff: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed in time_window
            time_window: Time window in seconds
            initial_backoff: Initial backoff time in seconds
            max_backoff: Maximum backoff time in seconds
            backoff_multiplier: Multiplier for exponential backoff
            jitter: Add random jitter to backoff times
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        
        self.calls = deque()
        self.failure_count = {}  # Track failures per endpoint
        self.last_failure_time = {}  # Track last failure time per endpoint
        self.lock = threading.Lock()
    
    def _calculate_backoff(self, endpoint: str) -> float:
        """Calculate backoff time with exponential backoff."""
        failures = self.failure_count.get(endpoint, 0)
        
        # Exponential backoff: initial * (multiplier ^ failures)
        backoff = self.initial_backoff * (self.backoff_multiplier ** failures)
        backoff = min(backoff, self.max_backoff)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            jitter_amount = backoff * 0.1 * random.random()
            backoff += jitter_amount
        
        return backoff
    
    def record_success(self, endpoint: str = "default"):
        """Record successful API call."""
        with self.lock:
            if endpoint in self.failure_count:
                # Reset failure count on success
                self.failure_count[endpoint] = 0
                if endpoint in self.last_failure_time:
                    del self.last_failure_time[endpoint]
    
    def record_failure(self, endpoint: str = "default"):
        """Record failed API call and update backoff."""
        with self.lock:
            self.failure_count[endpoint] = self.failure_count.get(endpoint, 0) + 1
            self.last_failure_time[endpoint] = time.time()
    
    def allow(self, endpoint: str = "default") -> bool:
        """Check if API call is allowed."""
        with self.lock:
            now = time.time()
            
            # Check if we're in backoff period
            if endpoint in self.last_failure_time:
                last_failure = self.last_failure_time[endpoint]
                backoff_time = self._calculate_backoff(endpoint)
                
                if now - last_failure < backoff_time:
                    return False
            
            # Remove old calls outside time window
            while self.calls and self.calls[0] < now - self.time_window:
                self.calls.popleft()
            
            # Check rate limit
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            
            return False
    
    def wait_time(self, endpoint: str = "default") -> float:
        """Get time to wait before next call is allowed."""
        with self.lock:
            wait_times = []
            
            # Check backoff wait time
            if endpoint in self.last_failure_time:
                last_failure = self.last_failure_time[endpoint]
                backoff_time = self._calculate_backoff(endpoint)
                backoff_wait = max(0.0, backoff_time - (time.time() - last_failure))
                wait_times.append(backoff_wait)
            
            # Check rate limit wait time
            if self.calls:
                oldest = self.calls[0]
                rate_wait = max(0.0, (oldest + self.time_window) - time.time())
                wait_times.append(rate_wait)
            
            return max(wait_times) if wait_times else 0.0
    
    def wait_if_needed(self, endpoint: str = "default"):
        """Wait if rate limit or backoff is active."""
        wait = self.wait_time(endpoint)
        if wait > 0:
            time.sleep(wait)


def rate_limited(
    max_calls: int = 100,
    time_window: int = 60,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    max_retries: int = 3,
    endpoint: str = "default"
):
    """
    Decorator for rate-limited API calls with exponential backoff.
    
    Usage:
        @rate_limited(max_calls=10, time_window=60, endpoint="google_speech")
        def call_api():
            # API call here
            pass
    """
    limiter = ExponentialBackoffRateLimiter(
        max_calls=max_calls,
        time_window=time_window,
        initial_backoff=initial_backoff,
        max_backoff=max_backoff
    )
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            retries = 0
            
            while retries <= max_retries:
                # Wait if needed
                limiter.wait_if_needed(endpoint)
                
                # Check if allowed
                if not limiter.allow(endpoint):
                    wait = limiter.wait_time(endpoint)
                    if wait > 0:
                        time.sleep(wait)
                    continue
                
                try:
                    result = func(*args, **kwargs)
                    limiter.record_success(endpoint)
                    return result
                except Exception as e:
                    limiter.record_failure(endpoint)
                    retries += 1
                    
                    if retries > max_retries:
                        raise
                    
                    # Wait with exponential backoff
                    backoff = limiter._calculate_backoff(endpoint)
                    time.sleep(backoff)
            
            raise RuntimeError(f"Max retries ({max_retries}) exceeded for {endpoint}")
        
        return wrapper
    return decorator


# Global rate limiter instances for common APIs
GOOGLE_SPEECH_LIMITER = ExponentialBackoffRateLimiter(
    max_calls=50,  # Google Speech API: 50 requests per minute
    time_window=60,
    initial_backoff=1.0,
    max_backoff=30.0
)

GENERIC_API_LIMITER = ExponentialBackoffRateLimiter(
    max_calls=100,
    time_window=60,
    initial_backoff=1.0,
    max_backoff=60.0
)
