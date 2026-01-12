# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# GATEKEEPER - Quality Improvements
# Adds error handling, logging, and validation to all components

import sys
import io
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BRAIN = Path(r'D:\RPF_BRAIN')
LOG_DIR = BRAIN / 'Archived' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / f'gatekeeper_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('Gatekeeper')

def error_handler(func):
    """Decorator for error handling and logging."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"File not found in {func.__name__}: {e}")
            return None
        except PermissionError as e:
            logger.error(f"Permission error in {func.__name__}: {e}")
            return None
        except ValueError as e:
            logger.error(f"Value error in {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            return None
    return wrapper

def validate_path(path):
    """Validate that a path exists and is accessible."""
    try:
        path = Path(path)
        if not path.exists():
            logger.warning(f"Path does not exist: {path}")
            return False
        if not path.is_file() and not path.is_dir():
            logger.warning(f"Path is not file or directory: {path}")
            return False
        return True
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return False

def validate_json(data):
    """Validate JSON structure."""
    try:
        import json
        if isinstance(data, str):
            json.loads(data)
        elif isinstance(data, dict):
            json.dumps(data)
        return True
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"JSON validation error: {e}")
        return False

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retrying failed operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts in {func.__name__}: {e}")
                        raise
                    logger.warning(f"Attempt {attempt + 1} failed in {func.__name__}, retrying...")
                    import time
                    time.sleep(delay)
        return wrapper
    return decorator

def validate_input(value, expected_type, min_val=None, max_val=None):
    """Validate function input."""
    if not isinstance(value, expected_type):
        logger.error(f"Invalid type: expected {expected_type}, got {type(value)}")
        return False
    
    if min_val is not None and value < min_val:
        logger.error(f"Value below minimum: {value} < {min_val}")
        return False
    
    if max_val is not None and value > max_val:
        logger.error(f"Value above maximum: {value} > {max_val}")
        return False
    
    return True

class QualityChecker:
    """Quality checking utilities."""
    
    @staticmethod
    def check_file_integrity(file_path):
        """Check file integrity."""
        try:
            path = Path(file_path)
            if not path.exists():
                return False, "File does not exist"
            
            # Check if file is readable
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    f.read(1)
            except:
                return False, "File is not readable"
            
            # Check file size (not empty)
            if path.stat().st_size == 0:
                return False, "File is empty"
            
            return True, "File integrity OK"
        except Exception as e:
            return False, f"Error checking file: {e}"
    
    @staticmethod
    def check_directory_structure():
        """Check that all required directories exist."""
        required_dirs = [
            BRAIN / 'Archived',
            BRAIN / 'Archived' / 'voiceprint',
            BRAIN / 'Archived' / 'voiceprint' / 'tuned',
            BRAIN / 'Archived' / 'learning',
            BRAIN / 'Archived' / 'voice_log',
            BRAIN / 'Archived' / 'scraped_data',
            BRAIN / 'Archived' / 'logs',
        ]
        
        missing = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing.append(str(dir_path))
                dir_path.mkdir(parents=True, exist_ok=True)
        
        if missing:
            logger.warning(f"Created missing directories: {missing}")
        
        return len(missing) == 0
    
    @staticmethod
    def check_dependencies():
        """Check that required Python packages are installed."""
        required = {
            'pyttsx3': 'text-to-speech',
            'numpy': 'calculations',
            'speech_recognition': 'voice input',
            'requests': 'web scraping',
        }
        
        missing = []
        for package, purpose in required.items():
            try:
                __import__(package)
            except ImportError:
                missing.append(f"{package} ({purpose})")
        
        if missing:
            logger.warning(f"Missing dependencies: {', '.join(missing)}")
        
        return len(missing) == 0

def improve_error_messages():
    """Add better error messages throughout system."""
    error_messages = {
        'file_not_found': "File not found. Check path and permissions.",
        'permission_denied': "Permission denied. Run as administrator if needed.",
        'invalid_input': "Invalid input. Check format and try again.",
        'network_error': "Network error. Check internet connection.",
        'rate_limit': "Rate limit exceeded. Wait and try again.",
        'missing_dependency': "Missing dependency. Install required package.",
    }
    return error_messages

if __name__ == '__main__':
    print("=" * 60)
    print("GATEKEEPER QUALITY CHECKER")
    print("=" * 60)
    
    checker = QualityChecker()
    
    print("\n[1/3] Checking directory structure...")
    dirs_ok = checker.check_directory_structure()
    print(f"  {'✅' if dirs_ok else '⚠️'} Directories: {'OK' if dirs_ok else 'Created missing'}")
    
    print("\n[2/3] Checking dependencies...")
    deps_ok = checker.check_dependencies()
    print(f"  {'✅' if deps_ok else '⚠️'} Dependencies: {'OK' if deps_ok else 'Some missing'}")
    
    print("\n[3/3] Quality improvements loaded...")
    print("  ✅ Error handling decorators")
    print("  ✅ Logging system")
    print("  ✅ Validation functions")
    print("  ✅ Retry mechanisms")
    
    print("\n" + "=" * 60)
    print("Quality improvements ready.")
    print("=" * 60)

