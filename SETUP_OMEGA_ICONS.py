#!/usr/bin/env python3
"""
Setup Omega Icons - Organize and Set Icon Files
================================================
Creates Options folder structure and organizes Omega icon files.
"""

import sys
import os
import shutil
from pathlib import Path

def setup_omega_icons():
    """Set up Omega icons in Options folder"""
    
    print("\n" + "=" * 80)
    print(" " * 25 + "OMEGA ICONS SETUP")
    print("=" * 80)
    print()
    
    base_dir = Path(__file__).parent.absolute()
    options_dir = base_dir / "Options"
    images_dir = base_dir / "images"
    
    # Create Options folder if it doesn't exist
    options_dir.mkdir(exist_ok=True)
    print(f"[OK] Options folder: {options_dir}")
    print()
    
    # Look for logo image
    logo_source = images_dir / "omega_logo_red_gold_wreath.png"
    if not logo_source.exists():
        # Try alternative names
        possible_logos = [
            images_dir / "omega 1.png",
            base_dir / "omega_logo_red_gold_wreath.png",
            base_dir / "omega_logo.png"
        ]
        for logo_path in possible_logos:
            if logo_path.exists():
                logo_source = logo_path
                break
    
    if not logo_source.exists():
        print("[ERROR] Logo image not found!")
        print()
        print("Please ensure the Omega logo image exists at:")
        print(f"  {images_dir / 'omega_logo_red_gold_wreath.png'}")
        print()
        return False
    
    print(f"[OK] Found logo: {logo_source}")
    print()
    
    # Create icon file using CREATE_OMEGA_ICON.py
    print("[Creating icon file...]")
    try:
        # Try to import and run icon creation
        sys.path.insert(0, str(base_dir))
        from CREATE_OMEGA_ICON import create_icon_from_logo
        
        icon_created = create_icon_from_logo()
        if not icon_created:
            print("[WARNING] Icon creation failed, but continuing...")
        else:
            print("[OK] Icon file created")
            print()
    except Exception as e:
        print(f"[WARNING] Icon creation failed: {e}")
        print()
    
    # Copy icon files to Options folder
    icon_files_to_copy = [
        ("omega_icon.ico", "Desktop shortcut icon"),
        (str(logo_source.name), "Main logo"),
    ]
    
    copied_files = []
    for file_name, description in icon_files_to_copy:
        source_path = base_dir / file_name
        if not source_path.exists():
            # Try images folder
            source_path = images_dir / file_name
            if not source_path.exists():
                continue
        
        dest_path = options_dir / file_name
        try:
            shutil.copy2(source_path, dest_path)
            copied_files.append((dest_path.name, description))
            print(f"[OK] Copied {description}: {dest_path.name}")
        except Exception as e:
            print(f"[WARNING] Failed to copy {file_name}: {e}")
    
    print()
    
    # Create README in Options folder
    readme_content = f"""OMEGA ICONS
===========

This folder contains all Omega icon files organized for easy access.

ICON FILES:
"""
    for file_name, description in copied_files:
        readme_content += f"\n  - {file_name}\n    {description}\n"
    
    readme_content += f"""

LOCATION:
  {options_dir}

USAGE:
  - Desktop shortcut icon: omega_icon.ico
  - Application icons: Use logo files as needed
  - BIOS logo: Use logo file converted to BMP format

NOTES:
  - All icon files are stored here for centralized management
  - Use CREATE_OMEGA_ICON.py to regenerate icon files from logo
  - Logo source: images/omega_logo_red_gold_wreath.png
"""
    
    readme_path = options_dir / "README.txt"
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"[OK] Created README: {readme_path.name}")
    print()
    
    print("=" * 80)
    print(" " * 25 + "ICON SETUP COMPLETE")
    print("=" * 80)
    print()
    print(f"Icons organized in: {options_dir}")
    print()
    
    return True

if __name__ == "__main__":
    success = setup_omega_icons()
    sys.exit(0 if success else 1)
