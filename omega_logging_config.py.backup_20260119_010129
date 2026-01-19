#!/usr/bin/env python3
"""
Omega Logging Configuration
============================
Structured logging configuration for Omega system.
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Try to import structlog
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("[Logging] structlog not available. Install with: pip install structlog")

def configure_logging(log_level: str = "INFO", log_file: Optional[Path] = None):
    """
    Configure structured logging for Omega.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    # Configure standard logging
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file) if log_file else logging.StreamHandler(),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Configure structlog if available
    if STRUCTLOG_AVAILABLE:
        processors = [
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
        ]
        
        if log_file:
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        print(f"[Logging] Structured logging configured (level: {log_level})")
    else:
        print(f"[Logging] Standard logging configured (level: {log_level})")

def get_logger(name: str = "omega"):
    """Get a logger instance"""
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)

def main():
    """Main function"""
    print("\n" + "=" * 80)
    print(" " * 25 + "OMEGA LOGGING CONFIG")
    print("=" * 80)
    print()
    
    configure_logging()
    logger = get_logger()
    
    print("[OK] Logging configuration complete")
    print(f"  - Structured logging available: {STRUCTLOG_AVAILABLE}")
    print()
    print("Usage:")
    print("  from omega_logging_config import get_logger")
    print("  logger = get_logger('my_module')")
    print("  logger.info('Event occurred', key='value')")
    print()
    print("=" * 80)
    print()

if __name__ == "__main__":
    main()
