#!/usr/bin/env python3
"""
Update Omega Logo Design - Red Omega with Gold Wreath
======================================================
Updates logo creation to match the new design:
- Red glossy Omega symbol (Ω)
- Golden laurel wreath
- Dark/black background
"""

from pathlib import Path
import sys

def update_logo_specification():
    """Update logo specification documentation"""
    
    print("\n" + "=" * 80)
    print(" " * 20 + "OMEGA LOGO DESIGN SPECIFICATION")
    print("=" * 80)
    print()
    
    print("Logo Design:")
    print("-" * 80)
    print("  - Central Element: Red glossy Omega symbol (Ω)")
    print("    * Color: Vibrant deep red (#C41E3A or similar)")
    print("    * Finish: Highly reflective, glossy/metallic")
    print("    * Style: Bold, thick, sans-serif")
    print("    * 3D Depth: Volumetric with highlights and shadows")
    print()
    print("  - Surrounding Element: Golden laurel wreath")
    print("    * Color: Rich lustrous gold (#FFD700 or similar)")
    print("    * Finish: Polished metal appearance")
    print("    * Form: Symmetrical circular arrangement")
    print("    * Detail: Individual overlapping leaves")
    print("    * 3D Depth: Highlights and shadows")
    print()
    print("  - Background: Dark/black textured")
    print("    * Color: Very dark charcoal/black")
    print("    * Texture: Subtle vertical brushed texture")
    print()
    
    print("Usage:")
    print("-" * 80)
    print("  1. BIOS Boot Logo:")
    print("     - File: boot_logo/omega_logo.bmp")
    print("     - Size: 1024x768 pixels")
    print("     - Format: BMP")
    print()
    print("  2. Desktop Shortcut Icon:")
    print("     - File: omega_icon.ico")
    print("     - Sizes: 16x16, 32x32, 48x48, 256x256")
    print("     - Format: ICO")
    print()
    
    print("Note:")
    print("-" * 80)
    print("  The logo image provided shows the correct design.")
    print("  This specification document describes the design elements.")
    print("  The actual logo files should be created from the provided image.")
    print()
    
    print("=" * 80)
    print()

def create_icon_conversion_script():
    """Create script to convert logo to ICO format"""
    
    script_content = '''#!/usr/bin/env python3
"""
Convert Omega Logo to ICO Format for Desktop Shortcut
======================================================
Converts the Omega logo image to Windows ICO format.
"""

from pathlib import Path

def create_icon_from_logo():
    """Create ICO file from logo image"""
    try:
        from PIL import Image
        
        # Logo image path (user should provide the actual image file)
        logo_path = Path("omega_logo_source.png")  # User should replace with actual image
        
        if not logo_path.exists():
            print(f"[ERROR] Logo source image not found: {logo_path}")
            print("Please place the Omega logo image file in the current directory.")
            print("Supported formats: PNG, BMP, JPG")
            return False
        
        # Load image
        img = Image.open(logo_path)
        
        # Create ICO with multiple sizes
        ico_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
        ico_images = []
        
        for size in ico_sizes:
            resized = img.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(resized)
        
        # Save as ICO
        ico_path = Path("omega_icon.ico")
        img.save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in ico_images])
        
        print(f"[OK] Icon created: {ico_path}")
        print(f"     Sizes: {', '.join([f'{w}x{h}' for w, h in ico_sizes])}")
        return True
        
    except ImportError:
        print("[ERROR] Pillow (PIL) not available")
        print("Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to create icon: {e}")
        return False

if __name__ == "__main__":
    create_icon_from_logo()
'''
    
    script_path = Path("CREATE_OMEGA_ICON.py")
    script_path.write_text(script_content)
    print(f"[OK] Created icon conversion script: {script_path.name}")

def main():
    """Main function"""
    update_logo_specification()
    create_icon_conversion_script()
    
    print("\nNext Steps:")
    print("-" * 80)
    print("1. Use the provided Omega logo image (red Ω with gold wreath)")
    print("2. Save as: omega_logo_source.png (or .bmp/.jpg)")
    print("3. Run: python CREATE_OMEGA_ICON.py (to create .ico file)")
    print("4. Update desktop shortcut icon using the .ico file")
    print("5. Update boot logo using the source image")
    print()

if __name__ == "__main__":
    main()
