"""Create application icon for Wareflow EMS.

This script creates a simple icon using PIL/Pillow.
The icon features a "W" logo with a warehouse/employee theme.

Run this script to generate icon files for different platforms:
    python build/create_icon.py
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path


def create_icon(size=256, bg_color=(41, 98, 255), text_color=(255, 255, 255)):
    """Create a simple icon with W logo.

    Args:
        size: Icon size in pixels
        bg_color: Background RGB color
        text_color: Text RGB color

    Returns:
        PIL Image object
    """
    # Create image
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle border
    margin = size // 16
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=size // 8,
        outline=text_color,
        width=size // 32
    )

    # Try to use a nice font, fallback to default
    try:
        # Try to find a bold font
        font_size = int(size * 0.5)
        if os.name == 'nt':  # Windows
            font = ImageFont.truetype("arialbd.ttf", font_size)
        elif os.name == 'posix':  # macOS/Linux
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        else:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    # Draw "W" text
    text = "W"
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center text
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - bbox[1]

    draw.text((x, y), text, fill=text_color, font=font)

    return img


def save_icon(img, output_path, format="ICO", sizes=None):
    """Save icon in specified format.

    Args:
        img: PIL Image object
        output_path: Output file path
        format: Image format (ICO, PNG)
        sizes: List of sizes for ICO format
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if format == "ICO":
        # ICO format with multiple sizes
        sizes = sizes or [16, 32, 48, 64, 128, 256]
        img.save(output_path, format='ICO', sizes=[(s, s) for s in sizes])
    elif format == "PNG":
        img.save(output_path, format='PNG')
    elif format == "ICNS":
        # ICNS for macOS (requires Pillow with icns support)
        try:
            img.save(output_path, format='ICNS')
        except Exception as e:
            print(f"Warning: Could not create ICNS file: {e}")
            # Fallback to PNG
            png_path = output_path.with_suffix('.png')
            img.save(png_path, format='PNG')
            print(f"  Created PNG instead: {png_path}")
    else:
        img.save(output_path, format=format)

    print(f"Created: {output_path}")


def main():
    """Create all icon formats."""
    assets_dir = Path("build/assets")
    assets_dir.mkdir(parents=True, exist_ok=True)

    print("Creating Wareflow EMS icons...")

    # Create base icon
    base_icon = create_icon(size=256)

    # Windows ICO
    print("\n1. Creating Windows ICO icon...")
    save_icon(base_icon, assets_dir / "icon.ico", format="ICO")

    # PNG (for documentation and web)
    print("\n2. Creating PNG icon...")
    save_icon(base_icon, assets_dir / "icon.png", format="PNG")

    # Create multiple sizes for different uses
    sizes = [16, 32, 48, 64, 128, 256, 512]
    print(f"\n3. Creating additional PNG sizes: {sizes}")
    for size in sizes:
        icon = create_icon(size=size)
        save_icon(icon, assets_dir / f"icon_{size}x{size}.png", format="PNG")

    # macOS ICNS (if supported)
    print("\n4. Creating macOS ICNS icon...")
    try:
        save_icon(base_icon, assets_dir / "icon.icns", format="ICNS")
    except Exception as e:
        print(f"  ICNS creation not supported: {e}")
        print("  Skipping ICNS (macOS users can use icon.png)")

    print("\n✅ Icon creation complete!")
    print(f"\nIcons saved to: {assets_dir.absolute()}")
    print("\nGenerated files:")
    for f in sorted(assets_dir.glob("*")):
        if f.is_file():
            size_kb = f.stat().st_size / 1024
            print(f"  - {f.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
