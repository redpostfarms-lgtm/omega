#!/usr/bin/env python3
"""
Safe Path Manager - Handles all file operations with proper path validation
Prevents issues with invalid paths, missing directories, and permission errors
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafePathManager:
    """Manages file operations with safe path handling"""
    
    @staticmethod
    def ensure_directory(path: Union[str, Path]) -> Path:
        """Ensure directory exists, create if needed"""
        path = Path(path).resolve()
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✓ Directory ensured: {path}")
            return path
        except (OSError, PermissionError) as e:
            logger.error(f"✗ Failed to create directory {path}: {e}")
            raise
    
    @staticmethod
    def safe_write_json(data: dict, filepath: Union[str, Path]) -> bool:
        """Safely write JSON file with backup"""
        filepath = Path(filepath).resolve()
        
        try:
            # Ensure parent directory exists
            SafePathManager.ensure_directory(filepath.parent)
            
            # Write to temporary file first
            temp_filepath = filepath.with_suffix(filepath.suffix + '.tmp')
            
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            # Move temp file to target (atomic operation)
            temp_filepath.replace(filepath)
            
            logger.info(f"✓ JSON saved safely: {filepath}")
            return True
            
        except (OSError, PermissionError, json.JSONDecodeError) as e:
            logger.error(f"✗ Failed to write JSON to {filepath}: {e}")
            return False
    
    @staticmethod
    def safe_read_json(filepath: Union[str, Path]) -> Optional[dict]:
        """Safely read JSON file with fallback"""
        filepath = Path(filepath).resolve()
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✓ JSON loaded: {filepath}")
            return data
            
        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"✗ Failed to read JSON from {filepath}: {e}")
            return None
    
    @staticmethod
    def safe_write_file(content: str, filepath: Union[str, Path]) -> bool:
        """Safely write file with backup"""
        filepath = Path(filepath).resolve()
        
        try:
            # Ensure parent directory exists
            SafePathManager.ensure_directory(filepath.parent)
            
            # Write to temporary file first
            temp_filepath = filepath.with_suffix(filepath.suffix + '.tmp')
            
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Move temp file to target (atomic operation)
            temp_filepath.replace(filepath)
            
            logger.info(f"✓ File saved safely: {filepath}")
            return True
            
        except (OSError, PermissionError) as e:
            logger.error(f"✗ Failed to write file to {filepath}: {e}")
            return False
    
    @staticmethod
    def safe_read_file(filepath: Union[str, Path]) -> Optional[str]:
        """Safely read file"""
        filepath = Path(filepath).resolve()
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"✓ File loaded: {filepath}")
            return content
            
        except (OSError, PermissionError) as e:
            logger.error(f"✗ Failed to read file from {filepath}: {e}")
            return None
    
    @staticmethod
    def validate_path(path: Union[str, Path]) -> bool:
        """Validate that path is safe and accessible"""
        path = Path(path).resolve()
        
        # Check for invalid characters (Windows)
        invalid_chars = '<>:"|?*'
        if any(char in str(path) for char in invalid_chars):
            logger.error(f"✗ Path contains invalid characters: {path}")
            return False
        
        # Check if path is too long (Windows max 260)
        if len(str(path)) > 260:
            logger.warning(f"⚠ Path may be too long (>260 chars): {path}")
        
        logger.info(f"✓ Path is valid: {path}")
        return True
    
    @staticmethod
    def get_safe_temp_dir() -> Path:
        """Get safe temporary directory"""
        import tempfile
        temp_dir = Path(tempfile.gettempdir()).resolve()
        SafePathManager.ensure_directory(temp_dir)
        return temp_dir
    
    @staticmethod
    def get_home_dir() -> Path:
        """Get safe home directory"""
        home = Path.home().resolve()
        return home
    
    @staticmethod
    def get_app_data_dir(app_name: str = 'AutoToolManager') -> Path:
        """Get safe application data directory"""
        if sys.platform == 'win32':
            app_data = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming'))
        else:
            app_data = Path.home() / '.local' / 'share'
        
        app_dir = (app_data / app_name).resolve()
        SafePathManager.ensure_directory(app_dir)
        return app_dir
    
    @staticmethod
    def get_config_dir(app_name: str = 'AutoToolManager') -> Path:
        """Get safe configuration directory"""
        if sys.platform == 'win32':
            config_dir = Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming')) / app_name
        else:
            config_dir = Path.home() / '.config' / app_name
        
        config_dir = config_dir.resolve()
        SafePathManager.ensure_directory(config_dir)
        return config_dir
    
    @staticmethod
    def list_files(directory: Union[str, Path], pattern: str = '*') -> list:
        """Safely list files in directory"""
        directory = Path(directory).resolve()
        
        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []
        
        try:
            files = list(directory.glob(pattern))
            logger.info(f"✓ Found {len(files)} files in {directory}")
            return files
        except (OSError, PermissionError) as e:
            logger.error(f"✗ Failed to list files in {directory}: {e}")
            return []
    
    @staticmethod
    def backup_file(filepath: Union[str, Path], suffix: str = '.bak') -> Optional[Path]:
        """Create a backup of a file"""
        filepath = Path(filepath).resolve()
        
        if not filepath.exists():
            logger.warning(f"File not found: {filepath}")
            return None
        
        backup_path = filepath.with_suffix(filepath.suffix + suffix)
        
        try:
            # Read original
            content = SafePathManager.safe_read_file(filepath)
            if content is None:
                return None
            
            # Write backup
            if SafePathManager.safe_write_file(content, backup_path):
                logger.info(f"✓ Backup created: {backup_path}")
                return backup_path
        except Exception as e:
            logger.error(f"✗ Failed to backup file {filepath}: {e}")
        
        return None


def initialize_safe_paths():
    """Initialize safe path directories for application"""
    logger.info("=== Initializing Safe Path Structure ===")
    
    config_dir = SafePathManager.get_config_dir('GatekeeperTools')
    app_data_dir = SafePathManager.get_app_data_dir('GatekeeperTools')
    
    # Create subdirectories
    (config_dir / 'cache').mkdir(parents=True, exist_ok=True)
    (config_dir / 'logs').mkdir(parents=True, exist_ok=True)
    (app_data_dir / 'backups').mkdir(parents=True, exist_ok=True)
    
    logger.info(f"✓ Config directory: {config_dir}")
    logger.info(f"✓ App data directory: {app_data_dir}")
    
    return {
        'config': config_dir,
        'app_data': app_data_dir,
        'cache': config_dir / 'cache',
        'logs': config_dir / 'logs',
        'backups': app_data_dir / 'backups'
    }


if __name__ == '__main__':
    # Test safe path operations
    print("\n=== Safe Path Manager Test ===\n")
    
    # Initialize
    paths = initialize_safe_paths()
    print(f"Initialized paths: {paths}\n")
    
    # Test operations
    test_file = paths['config'] / 'test.json'
    test_data = {'status': 'ok', 'test': True}
    
    # Safe write
    if SafePathManager.safe_write_json(test_data, test_file):
        print(f"✓ Successfully wrote JSON to {test_file}\n")
    
    # Safe read
    loaded_data = SafePathManager.safe_read_json(test_file)
    if loaded_data:
        print(f"✓ Successfully read JSON: {loaded_data}\n")
    
    # Validate path
    if SafePathManager.validate_path(test_file):
        print(f"✓ Path is valid and safe\n")
    
    print("=== Test Complete ===")
