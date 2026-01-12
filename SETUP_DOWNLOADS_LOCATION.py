#!/usr/bin/env python3
"""
Setup Optimal Downloads Location
=================================
Creates organized directory structure for development downloads (CUDA, tools, etc.)
"""

import os
import sys
from pathlib import Path
import json

# Base downloads location (on D: drive for optimal performance)
DOWNLOADS_BASE = Path("D:/RPF_BRAIN/Development_Downloads")

# Directory structure
DIRECTORIES = {
    "CUDA": "CUDA Toolkit and related tools",
    "GPU_Tools": "GPU development tools and libraries",
    "Development_Tools": "General development tools",
    "Installers": "Software installers",
    "Archives": "Archive/extracted files",
    "Completed": "Completed/installed downloads",
    "Temp": "Temporary download files",
    "Omega_Resources": "Omega-specific resources and dependencies"
}

def create_downloads_structure():
    """Create organized downloads directory structure"""
    print("=" * 80)
    print(" " * 20 + "SETUP OPTIMAL DOWNLOADS LOCATION")
    print("=" * 80)
    print()
    
    print(f"Base location: {DOWNLOADS_BASE}")
    print()
    
    # Create base directory
    DOWNLOADS_BASE.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Base directory: {DOWNLOADS_BASE}")
    print()
    
    # Create subdirectories
    print("[Creating directory structure...]")
    print("-" * 80)
    
    created_dirs = []
    for dir_name, description in DIRECTORIES.items():
        dir_path = DOWNLOADS_BASE / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)
        created_dirs.append({
            "name": dir_name,
            "path": str(dir_path),
            "description": description
        })
        print(f"  [OK] {dir_name:20s} - {description}")
    
    # Create README file
    readme_path = DOWNLOADS_BASE / "README.md"
    readme_content = f"""# Development Downloads Directory

**Location:** `{DOWNLOADS_BASE}`

## Directory Structure

"""
    for dir_info in created_dirs:
        readme_content += f"### {dir_info['name']}\n"
        readme_content += f"**Path:** `{dir_info['path']}`\n"
        readme_content += f"**Purpose:** {dir_info['description']}\n\n"
    
    readme_content += f"""## Usage

- **CUDA/** - CUDA Toolkit installers and related GPU tools
- **GPU_Tools/** - GPU development tools and libraries
- **Development_Tools/** - General development software
- **Installers/** - Software installers (save for reinstallation)
- **Archives/** - Extracted/archived files
- **Completed/** - Files that have been installed/processed
- **Temp/** - Temporary download files
- **Omega_Resources/** - Omega-specific resources

## Recommended Download Locations

### CUDA Toolkit
Download to: `CUDA/`
Installer type: **EXE-local** (recommended)

### Development Tools
Download to: `Development_Tools/`

### GPU Tools
Download to: `GPU_Tools/`

## Organization Tips

1. Keep original installers in `Installers/` for reinstallation
2. Move completed downloads to `Completed/` after installation
3. Extract archives to `Archives/` folder
4. Clean up `Temp/` folder regularly
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print()
    print(f"[OK] Created README: {readme_path.name}")
    
    # Create configuration file
    config_path = DOWNLOADS_BASE / "downloads_config.json"
    config_data = {
        "base_path": str(DOWNLOADS_BASE),
        "directories": created_dirs,
        "recommended_paths": {
            "cuda": "CUDA/",
            "gpu_tools": "GPU_Tools/",
            "development_tools": "Development_Tools/",
            "installers": "Installers/",
            "archives": "Archives/",
            "completed": "Completed/",
            "temp": "Temp/",
            "omega_resources": "Omega_Resources/"
        },
        "setup_date": str(Path(__file__).stat().st_mtime)
    }
    
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"[OK] Created config: {config_path.name}")
    print()
    
    print("=" * 80)
    print(" " * 25 + "SETUP COMPLETE")
    print("=" * 80)
    print()
    print(f"Downloads location ready: {DOWNLOADS_BASE}")
    print()
    print("Next steps:")
    print(f"  1. Download CUDA Toolkit to: {DOWNLOADS_BASE / 'CUDA'}")
    print(f"  2. Choose EXE-local installer type")
    print(f"  3. Save installer in CUDA/ directory")
    print()
    print("=" * 80)

if __name__ == "__main__":
    create_downloads_structure()
