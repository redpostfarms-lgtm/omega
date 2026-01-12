#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PROPRIETARY SOFTWARE - RED POST FARMS, LLC
# Copyright (c) 2025-2026 Red Post Farms, LLC
# All Rights Reserved
# NO COPYING. NO SHARING. NO DISTRIBUTION.
# Explicit written permission required.
#
# SALES UTILITIES - Shared code for all Sales modules
# Eliminates code duplication and improves maintainability

import sys
import io
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sales_system.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Constants
ROOT_DIR = Path(r'D:\RPF_BRAIN\Sales')
ROOT_DIR.mkdir(parents=True, exist_ok=True)

# TTS Configuration
TTS_RATE = 165
TTS_VOICE_PREFERENCE = 'zira'

# Retry Configuration
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2

def safe_file_operation(operation_name: str = "file operation"):
    """Decorator for safe file operations with error handling."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FileNotFoundError as e:
                logger.error(f"{operation_name} failed: File not found - {e}")
                return None
            except PermissionError as e:
                logger.error(f"{operation_name} failed: Permission denied - {e}")
                return None
            except IOError as e:
                logger.error(f"{operation_name} failed: I/O error - {e}")
                return None
            except Exception as e:
                logger.error(f"{operation_name} failed: Unexpected error - {e}")
                return None
        return wrapper
    return decorator

def initialize_tts():
    """Initialize TTS engine with proper error handling."""
    try:
        import pyttsx3
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', TTS_RATE)
        
        voices = tts_engine.getProperty('voices')
        if not voices:
            logger.warning("No TTS voices available")
            return None
        
        # Try to find preferred voice
        preferred_voice = next(
            (v.id for v in voices if TTS_VOICE_PREFERENCE in v.name.lower()),
            None
        )
        
        if preferred_voice:
            tts_engine.setProperty('voice', preferred_voice)
        else:
            tts_engine.setProperty('voice', voices[0].id)
            logger.info(f"Using default voice: {voices[0].name}")
        
        return tts_engine
    except ImportError:
        logger.warning("pyttsx3 not installed. TTS disabled.")
        return None
    except Exception as e:
        logger.error(f"TTS initialization failed: {e}")
        return None

def load_json_file(file_path: Path, default: Any = None) -> Any:
    """Safely load JSON file with error handling."""
    if not file_path.exists():
        logger.debug(f"File not found: {file_path}, using default")
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return default

def save_json_file(file_path: Path, data: Any, indent: int = 2) -> bool:
    """Safely save JSON file with error handling."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving {file_path}: {e}")
        return False

def load_jsonl_file(file_path: Path) -> list:
    """Safely load JSONL file."""
    if not file_path.exists():
        return []
    
    try:
        items = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    items.append(json.loads(line))
        return items
    except Exception as e:
        logger.error(f"Error loading JSONL {file_path}: {e}")
        return []

def save_jsonl_file(file_path: Path, items: list) -> bool:
    """Safely save JSONL file."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        return True
    except Exception as e:
        logger.error(f"Error saving JSONL {file_path}: {e}")
        return False

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not isinstance(text, str):
        return ""
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return text.strip()

def validate_path(path: Path, must_exist: bool = False) -> bool:
    """Validate file path for security."""
    try:
        # Resolve to absolute path
        resolved = path.resolve()
        
        # Check if must exist
        if must_exist and not resolved.exists():
            return False
        
        # Check for path traversal attempts
        if '..' in str(resolved):
            logger.warning(f"Potential path traversal detected: {path}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Path validation failed: {e}")
        return False

# Import json here to avoid circular imports
import json

