# Safe Path Operations & File Handling Guide

## Overview

The system now includes robust path and file handling to prevent errors like the one you encountered in Cursor. All file operations use safe, validated paths.

## Components

### 1. **safe_path_manager.py** - Safe File Operations
Core path management system that handles:
- Directory creation with validation
- Safe JSON read/write with atomic operations
- File backups before modifications
- Path validation (no invalid characters)
- Cross-platform path handling (Windows/Mac/Linux)
- Proper encoding (UTF-8)

### 2. **Updated Tool Managers**
All tool managers now use safe path operations:
- `auto_tool_manager.py` - Uses safe paths for logs and reports
- `tool_access_manager.py` - Integrated SafePathManager for caching
- `auto_tool_launcher.py` - Safe file operations throughout

## Key Features

### Atomic File Operations
```python
from safe_path_manager import SafePathManager

# Write JSON safely (uses temporary file + atomic rename)
data = {'status': 'ok'}
SafePathManager.safe_write_json(data, 'config.json')

# Read JSON with error handling
data = SafePathManager.safe_read_json('config.json')
```

### Automatic Directory Creation
```python
# Automatically creates parent directories
SafePathManager.safe_write_file('content', '/path/to/deep/file.txt')
```

### Path Validation
```python
# Validates path before operations
if SafePathManager.validate_path('/valid/path'):
    # Safe to use
    SafePathManager.safe_write_file('data', '/valid/path')
```

### Backup Operations
```python
# Automatically creates backup before modifying
backup_path = SafePathManager.backup_file('important.json')
# original.json.bak is now created
```

### Platform-Safe Directories
```python
# Get app data directory (Windows: AppData, Linux: ~/.local/share)
app_dir = SafePathManager.get_app_data_dir('GatekeeperTools')

# Get config directory (Windows: AppData/Roaming, Linux: ~/.config)
config_dir = SafePathManager.get_config_dir('GatekeeperTools')

# Get temporary directory (safe temp location)
temp_dir = SafePathManager.get_safe_temp_dir()
```

## Usage Examples

### Initialize Safe Paths
```bash
# Initialize directory structure
python safe_path_manager.py
```

This creates:
```
~/.config/GatekeeperTools/
├── cache/
├── logs/
~/.local/share/GatekeeperTools/  # On Linux/Mac
├── backups/

# On Windows:
%APPDATA%\GatekeeperTools\
├── cache/
├── logs/
%APPDATA%\..\Local\GatekeeperTools\
├── backups/
```

### Safe Tool Manager Integration
```python
from safe_path_manager import SafePathManager, initialize_safe_paths
from tool_access_manager import ToolAccessManager

# Initialize safe paths
paths = initialize_safe_paths()

# Use tool manager with safe paths
manager = ToolAccessManager()
tools = manager.access_tools_for_project('.')
```

### In Scripts
```python
from safe_path_manager import SafePathManager

# Safe config operations
config_dir = SafePathManager.get_config_dir('MyApp')
config_file = config_dir / 'settings.json'

# Save configuration safely
config = {'debug': True, 'version': '1.0'}
SafePathManager.safe_write_json(config, config_file)

# Load configuration with fallback
config = SafePathManager.safe_read_json(config_file)
if config is None:
    config = {}  # Use defaults
```

## Error Handling

The system gracefully handles:
- Missing directories (automatically creates them)
- Permission errors (logs and returns None)
- Invalid paths (detects and prevents)
- File encoding issues (uses UTF-8 with error handling)
- Corrupt JSON files (logs error, returns None)

### Example Error Handling
```python
from safe_path_manager import SafePathManager

# This handles all errors internally
result = SafePathManager.safe_write_json({'data': 'value'}, '/some/path/file.json')

if result:
    print("Successfully saved")
else:
    print("Failed to save (check logs)")

# Loading with fallback
data = SafePathManager.safe_read_json('/path/to/file.json')
if data is None:
    data = {}  # Use default
    print("Using default data")
```

## Path Structure

### Windows
```
C:\Users\{USER}\AppData\Roaming\GatekeeperTools\
├── cache\           (tool cache)
├── logs\            (operation logs)
└── backups\         (file backups)

C:\Users\{USER}\AppData\Local\GatekeeperTools\
└── backups\         (data backups)
```

### macOS/Linux
```
~/.config/GatekeeperTools/
├── cache/           (tool cache)
├── logs/            (operation logs)
└── backups/         (file backups)

~/.local/share/GatekeeperTools/
└── backups/         (data backups)
```

## Why This Matters

### The Cursor Issue You Encountered
The error you saw was caused by:
1. Cursor trying to save to a temporary elevated process directory
2. Path containing spaces or special characters
3. Directory not existing or being inaccessible

**SafePathManager prevents this by:**
- Using standard OS directories that always exist
- Validating paths before operations
- Creating directories automatically
- Using atomic operations (write to temp, then rename)
- Handling permission issues gracefully

## Best Practices

### 1. Always Use Safe Operations
```python
# ✓ Good
SafePathManager.safe_write_json(data, path)

# ✗ Avoid
with open(path, 'w') as f:
    json.dump(data, f)
```

### 2. Validate Paths
```python
# ✓ Good
if SafePathManager.validate_path(user_path):
    SafePathManager.safe_write_file(content, user_path)

# ✗ Avoid
SafePathManager.safe_write_file(content, user_path)  # No validation
```

### 3. Use Platform-Specific Directories
```python
# ✓ Good - Works on all platforms
config_dir = SafePathManager.get_config_dir('MyApp')

# ✗ Avoid - Platform-specific
config_dir = Path.home() / '.config'  # Doesn't exist on Windows
```

### 4. Create Backups for Important Files
```python
# ✓ Good
backup = SafePathManager.backup_file(important_file)
# Now safe to modify original

# ✗ Avoid
# Modify without backup
SafePathManager.safe_write_file(new_content, important_file)
```

## Troubleshooting

### File Not Saving
1. Check if parent directory is writable
2. Validate path: `SafePathManager.validate_path(path)`
3. Check logs in config directory
4. Try with absolute path: `Path(path).resolve()`

### Path Validation Failed
1. Check for invalid characters: `< > : " | ? * \`
2. Use forward slashes: `C:/Users/Name/file` (works on Windows)
3. Use raw strings: `r"C:\Users\Name\file"`
4. Use Path objects: `Path('C:/Users/Name/file')`

### Permissions Issue
1. Ensure directory has write permissions
2. Run as administrator (if needed for system directories)
3. Use user directories instead of system directories
4. Check logs for detailed error messages

## Integration with Auto Tool Manager

The tool managers now automatically use safe paths:

```bash
# All file operations are safe
python auto_tool_launcher.py detect

# Cache is stored safely
cat ~/.config/GatekeeperTools/cache/tool_cache.json

# Logs are accessible
tail ~/.config/GatekeeperTools/logs/auto_tool_manager.log
```

## Summary

SafePathManager ensures:
- ✓ Files save successfully
- ✓ Paths are validated
- ✓ Directories are created automatically
- ✓ Operations are atomic (all-or-nothing)
- ✓ Backups are created before modifications
- ✓ Cross-platform compatibility
- ✓ Proper error handling and logging

Use it everywhere to prevent the errors you encountered!
