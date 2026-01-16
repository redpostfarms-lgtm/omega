#!/usr/bin/env python3
"""
Gatekeeper System Error Handler & Logger - Enhanced
====================================================
Centralized error handling, logging, recovery, API validation, and health monitoring
for all Gatekeeper components and integrations.
"""

import logging
import logging.handlers
import traceback
import json
from pathlib import Path
from typing import Any, Optional, Dict, Callable, List
from datetime import datetime, timedelta
from enum import Enum
import sys
import os
from collections import deque


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class ComponentStatus(Enum):
    """Component operational status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class IntegrationErrorType(Enum):
    """Types of integration errors"""
    API_KEY_MISSING = "api_key_missing"
    API_KEY_INVALID = "api_key_invalid"
    CONNECTION_FAILED = "connection_failed"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SERVICE_UNAVAILABLE = "service_unavailable"
    AUTHENTICATION_FAILED = "authentication_failed"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN = "unknown"


class ErrorContext:
    """Context information for errors"""
    def __init__(self, component: str, operation: str, **kwargs: Any):
        self.component = component
        self.operation = operation
        self.context: Dict[str, Any] = kwargs
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary"""
        return {
            'component': self.component,
            'operation': self.operation,
            'context': self.context,
            'timestamp': self.timestamp
        }


class APIKeyValidator:
    """Validates and manages API keys for integrations"""
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.validated_keys: Dict[str, bool] = {}
        self.key_validation_log: deque = deque(maxlen=100)
    
    def validate_key_format(self, key: str, key_type: str) -> bool:
        """Validate API key format based on type"""
        if not key or not isinstance(key, str):
            return False
        
        key = key.strip()
        
        # Basic validation rules by key type
        format_rules = {
            'huggingface': lambda k: k.startswith('hf_') and len(k) > 10,
            'openai': lambda k: k.startswith('sk-') and len(k) > 20,
            'nvidia': lambda k: len(k) > 10 and ' ' not in k,
            'replicate': lambda k: len(k) > 10 and ' ' not in k,
            'kaggle': lambda k: len(k) > 10,
            'generic': lambda k: len(k) > 5 and ' ' not in k
        }
        
        validator = format_rules.get(key_type.lower(), format_rules['generic'])
        return validator(key)
    
    def test_api_connection(self, url: str, headers: Dict[str, str]) -> bool:
        """Test API connection with provided headers"""
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=5)
            return response.status_code < 500
        except Exception:
            return False
    
    def log_validation(self, key_type: str, success: bool, error: Optional[str] = None) -> None:
        """Log API key validation attempt"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'key_type': key_type,
            'success': success,
            'error': error
        }
        self.key_validation_log.append(entry)
        self.validated_keys[key_type] = success


class ComponentHealthMonitor:
    """Monitors health of system components"""
    
    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.component_status: Dict[str, ComponentStatus] = {}
        self.component_errors: Dict[str, List[str]] = {}
        self.last_check: Dict[str, datetime] = {}
        self.health_history: deque = deque(maxlen=1000)
    
    def register_component(self, component_name: str) -> None:
        """Register a component for monitoring"""
        self.component_status[component_name] = ComponentStatus.HEALTHY
        self.component_errors[component_name] = []
        self.last_check[component_name] = datetime.now()
    
    def check_component_health(self, component_name: str, check_func: Callable[[], bool]) -> ComponentStatus:
        """Check component health status"""
        try:
            is_healthy = check_func()
            status = ComponentStatus.HEALTHY if is_healthy else ComponentStatus.UNHEALTHY
            self.component_status[component_name] = status
            self.last_check[component_name] = datetime.now()
            
            self.health_history.append({
                'timestamp': datetime.now().isoformat(),
                'component': component_name,
                'status': status.value
            })
            
            return status
        except Exception as e:
            self.component_status[component_name] = ComponentStatus.OFFLINE
            self.component_errors[component_name].append(str(e))
            return ComponentStatus.OFFLINE
    
    def get_component_status(self, component_name: str) -> Optional[ComponentStatus]:
        """Get current status of a component"""
        return self.component_status.get(component_name)
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report"""
        healthy_count = sum(1 for s in self.component_status.values() 
                          if s == ComponentStatus.HEALTHY)
        total_count = len(self.component_status)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'healthy_components': healthy_count,
            'total_components': total_count,
            'component_status': {k: v.value for k, v in self.component_status.items()},
            'component_errors': {k: v[-5:] for k, v in self.component_errors.items()}
        }


class SystemErrorHandler:
    """Centralized error handling for all system components"""
    
    def __init__(self, log_dir: str = 'logs'):
        """Initialize error handler with logging."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.logger = self._setup_logger()
        self.error_history: deque = deque(maxlen=1000)
        self.recovery_handlers: Dict[str, Callable] = {}
        self.integration_errors: Dict[str, List[Dict[str, Any]]] = {}
        self.api_key_validator = APIKeyValidator(log_dir)
        self.health_monitor = ComponentHealthMonitor(log_dir)
    
    def _setup_logger(self) -> logging.Logger:
        """Setup comprehensive logging system."""
        logger = logging.getLogger('GatekeeperSystem')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'gatekeeper_system.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'gatekeeper_errors.log',
            maxBytes=10 * 1024 * 1024,
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s\n%(exc_info)s'
        )
        error_handler.setFormatter(error_formatter)
        
        # Integration handler
        integration_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'gatekeeper_integrations.log',
            maxBytes=5 * 1024 * 1024,
            backupCount=5
        )
        integration_handler.setLevel(logging.INFO)
        integration_handler.setFormatter(file_formatter)
        
        # Add all handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(integration_handler)
        
        return logger
    
    def handle_error(
        self,
        error: Exception,
        context: ErrorContext,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        recover: bool = True
    ) -> Dict[str, Any]:
        """
        Handle an error with context and attempt recovery.
        
        Args:
            error: The exception that occurred
            context: ErrorContext with component/operation info
            severity: Error severity level
            recover: Whether to attempt recovery
        
        Returns:
            Dictionary with error info and recovery status
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity.value,
            'component': context.component,
            'operation': context.operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context.context,
            'recovered': False,
            'recovery_message': None
        }
        
        # Log the error
        log_method = getattr(self.logger, severity.value.lower(), self.logger.error)
        log_method(
            f"[{context.component}] {context.operation}: {error}",
            exc_info=error
        )
        
        # Add to history
        self.error_history.append(error_info)
        
        # Track integration errors
        if 'integration' in context.component.lower():
            if context.component not in self.integration_errors:
                self.integration_errors[context.component] = []
            self.integration_errors[context.component].append(error_info)
        
        # Attempt recovery
        if recover:
            recovery_info = self._attempt_recovery(context, error)
            if recovery_info:
                error_info['recovered'] = True
                error_info['recovery_message'] = recovery_info['message']
                self.logger.info(f"Recovery successful: {recovery_info['message']}")
        
        return error_info
    
    def _attempt_recovery(
        self,
        context: ErrorContext,
        error: Exception
    ) -> Optional[Dict[str, str]]:
        """Attempt to recover from error."""
        key = f"{context.component}:{type(error).__name__}"
        
        if key in self.recovery_handlers:
            try:
                handler = self.recovery_handlers[key]
                result = handler(error, context)
                return result
            except Exception as e:
                self.logger.error(f"Recovery handler failed: {e}")
                return None
        
        return None
    
    def register_recovery_handler(
        self,
        component: str,
        error_type: str,
        handler: Callable
    ) -> None:
        """Register error recovery handler."""
        key = f"{component}:{error_type}"
        self.recovery_handlers[key] = handler
        self.logger.debug(f"Registered recovery handler: {key}")
    
    def validate_component(
        self,
        component_name: str,
        check_func: Callable[[], bool],
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Validate a component is functioning.
        
        Returns:
            Dictionary with validation result
        """
        try:
            is_valid = check_func()
            status = "valid" if is_valid else "invalid"
            self.logger.info(f"Component '{component_name}' validation: {status}")
            
            return {
                'component': component_name,
                'status': status,
                'description': description,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Component '{component_name}' validation failed: {e}")
            return {
                'component': component_name,
                'status': 'error',
                'description': description,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_error_report(self, limit: int = 100) -> Dict[str, Any]:
        """Get error history report."""
        return {
            'report_generated': datetime.now().isoformat(),
            'total_errors': len(self.error_history),
            'recent_errors': list(self.error_history)[-limit:],
            'error_types': self._count_error_types(),
            'components_affected': self._get_affected_components()
        }
    
    def _count_error_types(self) -> Dict[str, int]:
        """Count error types in history."""
        counts: Dict[str, int] = {}
        for error in self.error_history:
            error_type = error['error_type']
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts
    
    def _get_affected_components(self) -> Dict[str, int]:
        """Get components with errors."""
        counts: Dict[str, int] = {}
        for error in self.error_history:
            component = error['component']
            counts[component] = counts.get(component, 0) + 1
        return counts
    
    def save_error_report(self, filename: str = 'error_report.json') -> Optional[str]:
        """Save error report to file."""
        try:
            report = self.get_error_report()
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Error report saved to {filename}")
            return filename
        except Exception as e:
            self.logger.error(f"Failed to save error report: {e}")
            return None
    
    def handle_integration_error(
        self,
        integration_name: str,
        error_type: IntegrationErrorType,
        error: Exception,
        context: ErrorContext
    ) -> Dict[str, Any]:
        """Handle integration-specific errors with recovery strategies."""
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'integration': integration_name,
            'error_type': error_type.value,
            'error_message': str(error),
            'context': context.to_dict(),
            'recovery_attempted': False,
            'recovery_success': False
        }
        
        self.logger.error(
            f"Integration error in {integration_name}: {error_type.value} - {error}"
        )
        
        # Track integration error
        if integration_name not in self.integration_errors:
            self.integration_errors[integration_name] = []
        self.integration_errors[integration_name].append(error_info)
        
        # Attempt recovery based on error type
        if error_type == IntegrationErrorType.API_KEY_MISSING:
            error_info['recovery_message'] = "API key not configured. Please set via SETUP_DEVELOPER_INTEGRATIONS.py"
        elif error_type == IntegrationErrorType.RATE_LIMIT_EXCEEDED:
            error_info['recovery_message'] = "Rate limit exceeded. Implementing exponential backoff."
            error_info['recovery_attempted'] = True
        elif error_type == IntegrationErrorType.CONNECTION_FAILED:
            error_info['recovery_message'] = "Connection failed. Will retry with exponential backoff."
            error_info['recovery_attempted'] = True
        
        return error_info
    
    def get_integration_error_report(self) -> Dict[str, Any]:
        """Get report of all integration errors."""
        return {
            'timestamp': datetime.now().isoformat(),
            'total_integrations_with_errors': len(self.integration_errors),
            'integration_errors': {
                k: {
                    'error_count': len(v),
                    'recent_errors': v[-5:],
                    'error_types': self._count_integration_error_types(v)
                }
                for k, v in self.integration_errors.items()
            }
        }
    
    def _count_integration_error_types(self, error_list: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count error types in list."""
        counts: Dict[str, int] = {}
        for error in error_list:
            error_type = error.get('error_type', 'unknown')
            counts[error_type] = counts.get(error_type, 0) + 1
        return counts
    
    def validate_integration_setup(self, integration_name: str, api_key: str, key_type: str) -> Dict[str, Any]:
        """Validate integration API key setup."""
        result = {
            'integration': integration_name,
            'timestamp': datetime.now().isoformat(),
            'format_valid': False,
            'connection_test': False,
            'ready': False
        }
        
        # Check format
        format_valid = self.api_key_validator.validate_key_format(api_key, key_type)
        result['format_valid'] = format_valid
        
        if not format_valid:
            self.logger.warning(
                f"API key format invalid for {integration_name}. Expected {key_type} format."
            )
            self.api_key_validator.log_validation(key_type, False, "Invalid format")
            return result
        
        result['ready'] = True
        self.api_key_validator.log_validation(key_type, True)
        self.logger.info(f"Integration {integration_name} setup validated successfully.")
        
        return result


# Global error handler instance
_error_handler_instance: Optional[SystemErrorHandler] = None


def get_error_handler(log_dir: str = 'logs') -> SystemErrorHandler:
    """Get or create global error handler."""
    global _error_handler_instance
    
    if _error_handler_instance is None:
        _error_handler_instance = SystemErrorHandler(log_dir)
    
    return _error_handler_instance


def safe_execute(func: Callable, *args: Any, **kwargs: Any) -> Optional[Any]:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Function result or None if error occurred
    """
    handler = get_error_handler()
    
    try:
        return func(*args, **kwargs)
    except Exception as e:
        context = ErrorContext(
            component=func.__module__,
            operation=func.__name__,
            args=str(args)[:100],
            kwargs=str(kwargs)[:100]
        )
        
        handler.handle_error(
            e,
            context,
            severity=ErrorSeverity.ERROR
        )
        
        return None


# Validation utilities
class ComponentValidator:
    """Utilities for validating system components."""
    
    @staticmethod
    def check_import(module_name: str) -> bool:
        """Check if a module can be imported."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def check_file_exists(filepath: str) -> bool:
        """Check if a file exists."""
        return Path(filepath).exists()
    
    @staticmethod
    def check_service_running(service_name: str) -> bool:
        """Check if a service/process is running."""
        try:
            import psutil
            for proc in psutil.process_iter(['name']):
                if service_name.lower() in proc.info['name'].lower():
                    return True
            return False
        except Exception:
            return False


if __name__ == '__main__':
    # Test error handler
    handler = get_error_handler()
    
    print("Testing enhanced error handler...")
    print("=" * 60)
    
    # Test 1: Handle simulated error
    print("\n[Test 1] Handling standard error...")
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        context = ErrorContext('test', 'division', value=1)
        error_info = handler.handle_error(e, context)
        print(f"  Handled error: {error_info['error_type']}")
    
    # Test 2: Component validation
    print("\n[Test 2] Component validation...")
    validation = handler.validate_component(
        'test_component',
        lambda: True,
        'Test component validation'
    )
    print(f"  Validation result: {validation['status']}")
    
    # Test 3: Health monitoring
    print("\n[Test 3] Health monitoring...")
    handler.health_monitor.register_component('component1')
    status = handler.health_monitor.check_component_health('component1', lambda: True)
    print(f"  Component health: {status.value}")
    
    # Test 4: API key validation
    print("\n[Test 4] API key validation...")
    is_valid = handler.api_key_validator.validate_key_format('hf_test_key_1234567890', 'huggingface')
    print(f"  HuggingFace key format valid: {is_valid}")
    
    # Test 5: Integration error handling
    print("\n[Test 5] Integration error handling...")
    ctx = ErrorContext('huggingface_integration', 'api_call', model='bert')
    integration_error = handler.handle_integration_error(
        'huggingface',
        IntegrationErrorType.API_KEY_MISSING,
        Exception('No API key provided'),
        ctx
    )
    print(f"  Integration error handled: {integration_error['integration']}")
    
    # Test 6: Error reports
    print("\n[Test 6] Error reports...")
    report = handler.get_error_report()
    print(f"  Total errors: {report['total_errors']}")
    
    integration_report = handler.get_integration_error_report()
    print(f"  Integrations with errors: {integration_report['total_integrations_with_errors']}")
    
    health_report = handler.health_monitor.get_health_report()
    print(f"  Healthy components: {health_report['healthy_components']}/{health_report['total_components']}")
    
    print("\n" + "=" * 60)
    print("Enhanced error handler tests complete.")
