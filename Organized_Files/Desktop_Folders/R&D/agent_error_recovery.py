# -*- coding: utf-8 -*-
# ADVANCED ERROR RECOVERY - Self-healing with error classification
# Learns from failures, adapts recovery strategies

import os
import sys
import json
import time
import hashlib
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict


class ErrorType(Enum):
    """Error classification types."""
    NETWORK = "network"
    FILE_IO = "file_io"
    PERMISSION = "permission"
    RESOURCE = "resource"
    LOGIC = "logic"
    DEPENDENCY = "dependency"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategies."""
    RETRY = "retry"
    BACKOFF = "backoff"
    FALLBACK = "fallback"
    SKIP = "skip"
    RESTART = "restart"
    DEGRADE = "degrade"
    ALERT = "alert"


@dataclass
class ErrorPattern:
    """Learned error pattern."""
    error_type: ErrorType
    pattern: str  # Error message pattern
    count: int = 0
    last_seen: float = 0.0
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    success_rate: float = 0.0
    recovery_time: float = 0.0


class AdvancedErrorRecovery:
    """
    Advanced error recovery system.
    
    Features:
    - Error classification
    - Adaptive recovery strategies
    - Learning from failures
    - Pattern recognition
    - Self-healing
    """
    
    def __init__(self, log_file: str = '.error_recovery_log.json'):
        """Initialize error recovery system."""
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        self.log_file = Path(log_file)
        
        # Recovery strategies
        self.strategy_handlers = {
            RecoveryStrategy.RETRY: self._retry_strategy,
            RecoveryStrategy.BACKOFF: self._backoff_strategy,
            RecoveryStrategy.FALLBACK: self._fallback_strategy,
            RecoveryStrategy.SKIP: self._skip_strategy,
            RecoveryStrategy.RESTART: self._restart_strategy,
            RecoveryStrategy.DEGRADE: self._degrade_strategy,
            RecoveryStrategy.ALERT: self._alert_strategy
        }
        
        # Load learned patterns
        self._load_patterns()
    
    def classify_error(self, error: Exception) -> ErrorType:
        """Classify error type."""
        error_msg = str(error).lower()
        error_type = type(error).__name__
        
        # Network errors
        if any(keyword in error_msg for keyword in ['connection', 'timeout', 'network', 'socket', 'http']):
            return ErrorType.NETWORK
        
        # File I/O errors
        if any(keyword in error_msg for keyword in ['file', 'directory', 'not found', 'permission denied', 'access denied']):
            if 'permission' in error_msg or 'access' in error_msg:
                return ErrorType.PERMISSION
            return ErrorType.FILE_IO
        
        # Resource errors
        if any(keyword in error_msg for keyword in ['memory', 'disk', 'resource', 'out of']):
            return ErrorType.RESOURCE
        
        # Timeout errors
        if 'timeout' in error_msg or 'timed out' in error_msg:
            return ErrorType.TIMEOUT
        
        # Dependency errors
        if any(keyword in error_msg for keyword in ['import', 'module', 'package', 'dependency']):
            return ErrorType.DEPENDENCY
        
        # Logic errors (syntax, type, value)
        if error_type in ['SyntaxError', 'TypeError', 'ValueError', 'KeyError', 'AttributeError']:
            return ErrorType.LOGIC
        
        return ErrorType.UNKNOWN
    
    def get_recovery_strategy(self, error: Exception) -> RecoveryStrategy:
        """Get recovery strategy for error."""
        error_type = self.classify_error(error)
        error_msg = str(error)
        
        # Check for learned pattern
        pattern_key = self._get_pattern_key(error_type, error_msg)
        if pattern_key in self.error_patterns:
            pattern = self.error_patterns[pattern_key]
            # Use learned strategy if success rate > 50%
            if pattern.success_rate > 0.5:
                return pattern.recovery_strategy
        
        # Default strategies by error type
        default_strategies = {
            ErrorType.NETWORK: RecoveryStrategy.BACKOFF,
            ErrorType.FILE_IO: RecoveryStrategy.RETRY,
            ErrorType.PERMISSION: RecoveryStrategy.FALLBACK,
            ErrorType.RESOURCE: RecoveryStrategy.DEGRADE,
            ErrorType.LOGIC: RecoveryStrategy.ALERT,  # Can't auto-recover
            ErrorType.DEPENDENCY: RecoveryStrategy.ALERT,
            ErrorType.TIMEOUT: RecoveryStrategy.BACKOFF,
            ErrorType.UNKNOWN: RecoveryStrategy.RETRY
        }
        
        return default_strategies.get(error_type, RecoveryStrategy.RETRY)
    
    def _get_pattern_key(self, error_type: ErrorType, error_msg: str) -> str:
        """Generate pattern key from error."""
        # Extract key words from error message
        words = error_msg.lower().split()
        key_words = [w for w in words if len(w) > 4][:3]  # Top 3 significant words
        return f"{error_type.value}:{':'.join(key_words)}"
    
    def recover(self, error: Exception, context: Dict[str, Any] = None,
                task: Optional[Callable] = None) -> Any:
        """
        Attempt to recover from error.
        
        Args:
            error: The error that occurred
            context: Context information
            task: Task function to retry
            
        Returns:
            Recovery result or None if failed
        """
        error_type = self.classify_error(error)
        strategy = self.get_recovery_strategy(error)
        
        print(f"[Error Recovery] Error: {error_type.value}, Strategy: {strategy.value}")
        
        # Record error
        pattern_key = self._get_pattern_key(error_type, str(error))
        if pattern_key not in self.error_patterns:
            self.error_patterns[pattern_key] = ErrorPattern(
                error_type=error_type,
                pattern=pattern_key,
                recovery_strategy=strategy
            )
        
        pattern = self.error_patterns[pattern_key]
        pattern.count += 1
        pattern.last_seen = time.time()
        
        # Execute recovery strategy
        start_time = time.time()
        result = None
        
        try:
            handler = self.strategy_handlers.get(strategy)
            if handler:
                result = handler(error, context, task)
            
            # Record success
            recovery_time = time.time() - start_time
            pattern.recovery_time = (pattern.recovery_time + recovery_time) / 2
            pattern.success_rate = (pattern.success_rate * (pattern.count - 1) + 1.0) / pattern.count
            
            self.recovery_history.append({
                'timestamp': time.time(),
                'error_type': error_type.value,
                'strategy': strategy.value,
                'success': True,
                'recovery_time': recovery_time
            })
            
            print(f"[Error Recovery] Recovered successfully in {recovery_time:.2f}s")
            
        except Exception as recovery_error:
            # Recovery failed
            recovery_time = time.time() - start_time
            pattern.success_rate = (pattern.success_rate * (pattern.count - 1) + 0.0) / pattern.count
            
            self.recovery_history.append({
                'timestamp': time.time(),
                'error_type': error_type.value,
                'strategy': strategy.value,
                'success': False,
                'recovery_time': recovery_time,
                'recovery_error': str(recovery_error)
            })
            
            print(f"[Error Recovery] Recovery failed: {recovery_error}")
        
        # Save patterns
        self._save_patterns()
        
        return result
    
    def _retry_strategy(self, error: Exception, context: Dict, task: Callable) -> Any:
        """Simple retry strategy."""
        if task:
            max_retries = context.get('max_retries', 3)
            for attempt in range(max_retries):
                try:
                    return task()
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(0.5)
        return None
    
    def _backoff_strategy(self, error: Exception, context: Dict, task: Callable) -> Any:
        """Exponential backoff retry."""
        if task:
            max_retries = context.get('max_retries', 5)
            for attempt in range(max_retries):
                try:
                    return task()
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = 2 ** attempt  # Exponential: 1s, 2s, 4s, 8s...
                    time.sleep(wait_time)
        return None
    
    def _fallback_strategy(self, error: Exception, context: Dict, task: Callable) -> Any:
        """Try fallback method."""
        fallback = context.get('fallback')
        if fallback and callable(fallback):
            return fallback()
        return None
    
    def _skip_strategy(self, error: Exception, context: Dict, task: Callable) -> Any:
        """Skip task and continue."""
        print("[Error Recovery] Skipping task")
        return None
    
    def _restart_strategy(self, error: Exception, context: Dict, task: Callable) -> Any:
        """Restart task/resource."""
        # Would restart relevant component
        print("[Error Recovery] Restarting...")
        time.sleep(1)
        if task:
            return task()
        return None
    
    def _degrade_strategy(self, error: Exception, context: Dict, task: Callable) -> Any:
        """Degrade to simpler operation."""
        degraded = context.get('degraded')
        if degraded and callable(degraded):
            return degraded()
        return None
    
    def _alert_strategy(self, error: Exception, context: Dict, task: Callable) -> Any:
        """Alert - can't auto-recover."""
        print(f"[Error Recovery] ALERT: Cannot auto-recover from {error}")
        # Would send alert/notification
        return None
    
    def _load_patterns(self):
        """Load learned error patterns."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, pattern_data in data.get('patterns', {}).items():
                        self.error_patterns[key] = ErrorPattern(**pattern_data)
            except:
                pass
    
    def _save_patterns(self):
        """Save learned error patterns."""
        data = {
            'patterns': {key: asdict(pattern) for key, pattern in self.error_patterns.items()},
            'last_updated': time.time()
        }
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except:
            pass
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        by_type = defaultdict(int)
        by_strategy = defaultdict(int)
        
        for pattern in self.error_patterns.values():
            by_type[pattern.error_type.value] += pattern.count
            by_strategy[pattern.recovery_strategy.value] += pattern.count
        
        return {
            'total_patterns': len(self.error_patterns),
            'total_recoveries': len(self.recovery_history),
            'successful_recoveries': sum(1 for r in self.recovery_history if r.get('success')),
            'errors_by_type': dict(by_type),
            'strategies_used': dict(by_strategy)
        }


# Decorator for automatic error recovery
def with_error_recovery(recovery: AdvancedErrorRecovery, 
                       context: Dict[str, Any] = None):
    """Decorator for automatic error recovery."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            max_attempts = (context or {}).get('max_attempts', 3)
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        # Last attempt - try recovery
                        result = recovery.recover(e, context, lambda: func(*args, **kwargs))
                        if result is not None:
                            return result
                        raise
                    else:
                        # Retry with recovery
                        result = recovery.recover(e, context, lambda: func(*args, **kwargs))
                        if result is not None:
                            return result
            
            raise Exception("All recovery attempts failed")
        
        return wrapper
    return decorator


if __name__ == '__main__':
    print("=" * 60)
    print("ADVANCED ERROR RECOVERY - Test")
    print("=" * 60)
    
    recovery = AdvancedErrorRecovery()
    
    # Test error classification
    test_errors = [
        FileNotFoundError("File not found: data.txt"),
        PermissionError("Permission denied"),
        TimeoutError("Connection timeout"),
        ImportError("No module named 'missing'")
    ]
    
    for error in test_errors:
        error_type = recovery.classify_error(error)
        strategy = recovery.get_recovery_strategy(error)
        print(f"{type(error).__name__}: {error_type.value} -> {strategy.value}")
    
    stats = recovery.get_error_stats()
    print(f"\nStats: {stats}")
    
    print("\n[OK] Advanced error recovery ready")

