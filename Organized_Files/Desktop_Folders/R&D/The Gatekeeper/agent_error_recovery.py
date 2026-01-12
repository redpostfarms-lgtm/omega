# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved

"""
Agent Error Recovery System
Automatic error detection and recovery for agents
"""

import json
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

BRAIN = Path(r'D:\RPF_BRAIN')
ARCHIVED = BRAIN / 'Archived'
ERROR_DIR = ARCHIVED / 'agent_errors'
ERROR_DIR.mkdir(parents=True, exist_ok=True)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AgentErrorRecovery:
    """Automatic error detection and recovery for agents."""
    
    def __init__(self):
        self.error_history = []
        self.recovery_strategies = {}
        self.max_retries = 3
        self.retry_delays = [1, 2, 5]  # seconds
    
    def detect_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect and categorize an error.
        
        Args:
            error: Exception object
            context: Additional context about the error
        
        Returns:
            Error record
        """
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Determine severity based on error type
        severity = self._determine_severity(error_type, error_message)
        
        error_record = {
            'id': f"err_{int(time.time() * 1000)}",
            'type': error_type,
            'message': error_message,
            'traceback': error_traceback,
            'severity': severity.value,
            'context': context or {},
            'timestamp': time.time(),
            'recovered': False
        }
        
        self.error_history.append(error_record)
        
        # Keep last 1000 errors
        if len(self.error_history) > 1000:
            self.error_history = self.error_history[-1000:]
        
        # Save error record
        self._save_error_record(error_record)
        
        return error_record
    
    def _determine_severity(self, error_type: str, error_message: str) -> ErrorSeverity:
        """Determine error severity based on type and message."""
        critical_errors = ['SystemExit', 'KeyboardInterrupt', 'MemoryError', 'SystemError']
        high_errors = ['KeyError', 'AttributeError', 'ImportError', 'ValueError']
        medium_errors = ['TypeError', 'IOError', 'FileNotFoundError']
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif error_type in medium_errors:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def recover_from_error(self, error_record: Dict[str, Any], operation: Callable, *args, **kwargs) -> Any:
        """
        Attempt to recover from an error by retrying the operation.
        
        Args:
            error_record: Error record from detect_error
            operation: Function to retry
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
        
        Returns:
            Result of operation if successful
        
        Raises:
            Exception: If recovery fails after all retries
        """
        error_id = error_record['id']
        error_type = error_record['type']
        
        # Check for custom recovery strategy
        if error_type in self.recovery_strategies:
            strategy = self.recovery_strategies[error_type]
            try:
                result = strategy(error_record, operation, *args, **kwargs)
                error_record['recovered'] = True
                error_record['recovery_strategy'] = error_type
                return result
            except Exception as recovery_error:
                # Custom strategy failed, fall back to retry
                pass
        
        # Default recovery: retry with exponential backoff
        return self.retry_with_backoff(operation, *args, **kwargs)
    
    def retry_with_backoff(self, operation: Callable, *args, **kwargs) -> Any:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Function to retry
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result of operation
        
        Raises:
            Exception: Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                result = operation(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[min(attempt, len(self.retry_delays) - 1)]
                    time.sleep(delay)
                else:
                    # All retries failed
                    raise last_exception
        
        raise last_exception
    
    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """
        Register a custom recovery strategy for a specific error type.
        
        Args:
            error_type: Exception type name
            strategy: Recovery function (error_record, operation, *args, **kwargs) -> result
        """
        self.recovery_strategies[error_type] = strategy
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        errors_by_type = {}
        errors_by_severity = {}
        
        for error in self.error_history:
            error_type = error['type']
            severity = error['severity']
            
            errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
            errors_by_severity[severity] = errors_by_severity.get(severity, 0) + 1
        
        recovered_count = sum(1 for err in self.error_history if err.get('recovered', False))
        
        return {
            'total_errors': len(self.error_history),
            'recovered_errors': recovered_count,
            'recovery_rate': (recovered_count / len(self.error_history) * 100) if self.error_history else 0,
            'errors_by_type': errors_by_type,
            'errors_by_severity': errors_by_severity,
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }
    
    def _save_error_record(self, error_record: Dict[str, Any]):
        """Save error record to disk."""
        timestamp = int(error_record['timestamp'])
        date_str = time.strftime('%Y%m%d', time.gmtime(timestamp))
        error_file = ERROR_DIR / f"errors_{date_str}.json"
        
        # Load existing errors for this date
        errors = []
        if error_file.exists():
            try:
                with open(error_file, 'r', encoding='utf-8') as f:
                    errors = json.load(f)
            except:
                errors = []
        
        errors.append(error_record)
        
        # Keep last 1000 errors per day
        errors = errors[-1000:]
        
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(errors, f, indent=2, ensure_ascii=False)

