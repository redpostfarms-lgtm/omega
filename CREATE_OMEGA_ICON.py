#!/usr/bin/env python3
"""
Create Omega Icon - Convert Logo to ICO Format
===============================================
Converts the Omega logo image to Windows ICO format for desktop shortcut.
"""

from pathlib import Path
import sys

def create_icon_from_logo():
    """Create ICO file from logo image"""
    base_dir = Path(__file__).parent.absolute()
    
    print("\n" + "=" * 80)
    print(" " * 25 + "CREATE OMEGA ICON")
    print("=" * 80)
    print()
    
    # Look for logo image
    images_dir = base_dir / "images"
    logo_files = [
        images_dir / "omega_logo_red_gold_wreath.png",
        images_dir / "omega_logo_red_gold_wreath.bmp",
        base_dir / "omega_logo_red_gold_wreath.png",
        base_dir / "omega_logo_red_gold_wreath.bmp",
        base_dir / "omega_logo.png",
        base_dir / "omega_logo.bmp"
    ]
    
    logo_path = None
    for path in logo_files:
        if path.exists():
            logo_path = path
            break
    
    if not logo_path:
        print("[ERROR] Logo image not found!")
        print()
        print("Please save the Omega logo image (red Omega with gold wreath) as:")
        print("  images/omega_logo_red_gold_wreath.png")
        print()
        print("Supported formats: PNG, BMP")
        print()
        return False
    
    print(f"[OK] Found logo image: {logo_path}")
    print()
    
    try:
        from PIL import Image
        
        # Load image
        print("[Loading logo image...]")
        img = Image.open(logo_path)
        print(f"[OK] Image loaded: {img.size[0]}x{img.size[1]} pixels")
        print()
        
        # Create ICO with multiple sizes
        ico_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
        print("[Creating icon sizes...]")
        
        ico_images = []
        for size in ico_sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(resized)
            print(f"  [OK] Created {size[0]}x{size[1]} icon")
        
        print()
        
        # Save as ICO
        ico_path = base_dir / "omega_icon.ico"
        print(f"[Saving icon file...]")
        
        # PIL requires saving with sizes tuple
        img.save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        
        print(f"[OK] Icon created: {ico_path}")
        print(f"     Sizes: {', '.join([f'{w}x{h}' for w, h in ico_sizes])}")
        print()
        
        print("=" * 80)
        print(" " * 25 + "ICON CREATION COMPLETE")
        print("=" * 80)
        print()
        print("Next Steps:")
        print("  1. Update desktop shortcut to use omega_icon.ico")
        print("  2. Or run: UPDATE_DESKTOP_SHORTCUT_ICON.bat (to be created)")
        print()
        print("=" * 80)
        print()
        
        return True
        
    except ImportError:
        print("[ERROR] Pillow (PIL) not available")
        print()
        print("Install with: pip install Pillow")
        print()
        return False
    except Exception as e:
        print(f"[ERROR] Failed to create icon: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    success = create_icon_from_logo()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
