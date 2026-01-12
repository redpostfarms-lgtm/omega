#!/usr/bin/env python3
"""
Copy UI Screenshots for Sharing
================================
This script copies UI screenshots and images to a shared location for easy sharing.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

def copy_ui_images():
    """Copy UI images to desktop for sharing"""
    base_dir = Path(__file__).parent.absolute()
    images_dir = base_dir / "images"
    desktop = Path.home() / "Desktop"
    
    # Create Omega UI Images folder on desktop
    share_folder = desktop / "Omega_UI_Images"
    share_folder.mkdir(exist_ok=True)
    
    print("=" * 80)
    print(" " * 20 + "COPYING UI SCREENSHOTS FOR SHARING")
    print("=" * 80)
    print()
    print(f"Source: {images_dir}")
    print(f"Destination: {share_folder}")
    print()
    
    # List of images to copy
    images_to_copy = [
        "CONTROL PANEL FOR omega.png",
        "omega_logo_red_gold_wreath.png",
        "omega_logo_red_gold_wreath.ico",
        "OIP.jpg",
        "OIP.jfif",
        "omega symbol.jfif"
    ]
    
    copied = []
    not_found = []
    
    for image_file in images_to_copy:
        source = images_dir / image_file
        if source.exists():
            try:
                dest = share_folder / image_file
                shutil.copy2(source, dest)
                size = source.stat().st_size / 1024  # Size in KB
                print(f"✓ Copied: {image_file} ({size:.1f} KB)")
                copied.append(image_file)
            except Exception as e:
                print(f"✗ Error copying {image_file}: {e}")
                not_found.append(image_file)
        else:
            print(f"✗ Not found: {image_file}")
            not_found.append(image_file)
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Copied: {len(copied)} files")
    print(f"Not found: {len(not_found)} files")
    print()
    print(f"All images copied to: {share_folder}")
    print()
    print("You can now:")
    print("  1. Share the folder directly")
    print("  2. Create a zip file of the folder")
    print("  3. Send individual files via email")
    print()
    
    # Create a README in the shared folder
    readme_file = share_folder / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("Omega Control Panel - UI Screenshots\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Copied: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("Files:\n")
        for img in copied:
            f.write(f"  - {img}\n")
        f.write("\n")
        f.write("These images are design references for the Omega Control Panel UI.\n")
        f.write("See UI_REQUIREMENTS_SPECIFICATION.md for details.\n")
    
    print(f"✓ Created README.txt in shared folder")
    print()
    
    return len(copied) > 0

if __name__ == "__main__":
    try:
        success = copy_ui_images()
        if success:
            print("✓ Done! Images are ready for sharing.")
        else:
            print("⚠ No images were copied. Check if images exist in images/ directory.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
