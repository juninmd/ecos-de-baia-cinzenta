#!/usr/bin/env python3
"""
Generate PWA icons from source image.
Creates all required sizes for Android/iOS app icons.
"""

import os
from pathlib import Path
from PIL import Image

# Icon sizes needed for PWA/Android
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

def generate_icons(source_image_path: str, output_dir: str):
    """
    Generate app icons in multiple sizes.
    
    Args:
        source_image_path: Path to source image (should be at least 512x512)
        output_dir: Directory to save generated icons
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load source image
    try:
        img = Image.open(source_image_path)
        print(f"✓ Loaded source image: {source_image_path}")
        print(f"  Original size: {img.size}")
        
        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Generate each size
        for size in ICON_SIZES:
            # Resize image
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Save as PNG
            output_file = output_path / f"icon-{size}x{size}.png"
            resized.save(output_file, 'PNG', optimize=True)
            print(f"✓ Generated: {output_file}")
        
        print(f"\n✅ Successfully generated {len(ICON_SIZES)} icon sizes!")
        
    except FileNotFoundError:
        print(f"❌ Error: Source image not found at {source_image_path}")
        print("\n📝 Instructions:")
        print("1. Create a 512x512 PNG image for your app icon")
        print("2. Save it as 'docs/public/app-icon-source.png'")
        print("3. Run this script again")
        
    except Exception as e:
        print(f"❌ Error generating icons: {e}")

if __name__ == "__main__":
    # Use cidade.jpg as source (you can replace with custom icon later)
    source = "docs/public/cidade.jpg"
    output = "docs/public/icons"
    
    print("🎨 Generating PWA/Android App Icons")
    print("=" * 50)
    generate_icons(source, output)
