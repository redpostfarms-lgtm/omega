"""
OMEGA Icon Generator
====================
Generates placeholder PWA icons with the OMEGA logo.
Run once to create all required icon sizes.

Usage:
    pip install Pillow --break-system-packages
    python generate_icons.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Icon sizes required for PWA
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def create_icon(size):
    """Create a KITT-themed OMEGA icon at the specified size."""
    
    # Create image with black background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw red scanner bar in the middle
    bar_height = size // 6
    bar_y = (size - bar_height) // 2
    
    # Gradient-like effect with multiple rectangles
    for i in range(5):
        alpha = 255 - (i * 40)
        offset = i * (bar_height // 10)
        draw.rectangle(
            [size // 8, bar_y + offset, size * 7 // 8, bar_y + bar_height - offset],
            fill=(255, 0, 0, alpha)
        )
    
    # Draw "Ω" (Omega symbol) or "O" as text
    try:
        # Try to use a font that supports Omega symbol
        font_size = size // 2
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        text = "Ω"
    except:
        # Fallback to default font with "O"
        font_size = size // 3
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        text = "O"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]
    
    # Draw text with red color
    draw.text((x, y), text, font=font, fill=(255, 50, 50, 255))
    
    # Add border
    border_width = max(2, size // 64)
    draw.rectangle(
        [border_width, border_width, size - border_width - 1, size - border_width - 1],
        outline=(255, 0, 0, 180),
        width=border_width
    )
    
    return img

def main():
    # Create icons directory
    icons_dir = 'icons'
    os.makedirs(icons_dir, exist_ok=True)
    
    print("Generating OMEGA PWA icons...")
    print("=" * 40)
    
    for size in SIZES:
        icon = create_icon(size)
        filename = f"{icons_dir}/icon-{size}.png"
        icon.save(filename, 'PNG')
        print(f"  ✓ Created {filename}")
    
    print("=" * 40)
    print(f"Done! Created {len(SIZES)} icons in ./{icons_dir}/")
    print("\nYou can replace these with custom icons later.")

if __name__ == '__main__':
    main()
