"""
Generates the DevBuddy AI tray icon PNG programmatically.
Run once: python generate_icon.py
"""
from PIL import Image, ImageDraw, ImageFont
import os

def generate_tray_icon():
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle - DevBuddy Blue gradient effect
    draw.ellipse([2, 2, size - 2, size - 2], fill=(0, 120, 215, 255))
    # Inner highlight ring
    draw.ellipse([6, 6, size - 6, size - 6], outline=(100, 180, 255, 180), width=2)

    # Rocket emoji drawn as shapes
    # Body
    draw.polygon([(32, 10), (42, 28), (32, 38), (22, 28)], fill=(255, 255, 255, 240))
    # Flame
    draw.polygon([(28, 38), (32, 50), (36, 38)], fill=(255, 165, 0, 230))
    # Wing left
    draw.polygon([(22, 28), (14, 40), (24, 34)], fill=(200, 230, 255, 220))
    # Wing right
    draw.polygon([(42, 28), (50, 40), (40, 34)], fill=(200, 230, 255, 220))
    # Porthole
    draw.ellipse([28, 20, 36, 28], fill=(180, 220, 255, 220), outline=(255, 255, 255, 200), width=1)

    output_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(output_dir, exist_ok=True)
    icon_path = os.path.join(output_dir, "tray_icon.png")
    img.save(icon_path)
    print(f"Tray icon saved to: {icon_path}")
    return icon_path

if __name__ == "__main__":
    generate_tray_icon()
