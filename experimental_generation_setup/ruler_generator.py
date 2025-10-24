#!/usr/bin/env python3
"""
Generate a high-resolution transparent PNG ruler image
Portrait orientation with ruler on the left side (0-200 cm)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Configuration
CM_COUNT = 200  # 0 to 200 cm
DPI = 300  # High resolution
CM_TO_INCH = 0.393701
PIXELS_PER_CM = DPI * CM_TO_INCH  # pixels per cm at 300 DPI

# Image dimensions
RULER_WIDTH = int(3 * PIXELS_PER_CM)  # 3 cm wide ruler
IMAGE_HEIGHT = int(CM_COUNT * PIXELS_PER_CM)  # 200 cm tall
IMAGE_WIDTH = int(100 * PIXELS_PER_CM)  # Total width: 100 cm (wide canvas for character)

print(f"Creating image: {IMAGE_WIDTH}x{IMAGE_HEIGHT} pixels")
print(f"Pixels per cm: {PIXELS_PER_CM:.2f}")

# Create transparent image (RGBA mode)
img = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT), (255, 255, 255, 0))
draw = ImageDraw.Draw(img)

# Colors
BLACK = (0, 0, 0, 255)
GRAY = (100, 100, 100, 255)

# Line widths
THICK_LINE = 3
MEDIUM_LINE = 2
THIN_LINE = 1

# Try to load a font, fallback to default if not available
try:
    # Try to use a common system font
    font_size = int(PIXELS_PER_CM * 2)  # About 2 cm tall - much bigger!
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
            break
    if font is None:
        font = ImageFont.load_default()
except Exception as e:
    print(f"Could not load custom font: {e}")
    font = ImageFont.load_default()

# Draw ruler (remember: y=0 is at top, so we need to flip our coordinates)
for cm in range(CM_COUNT + 1):
    # Calculate y position (flip so 0 is at bottom)
    y = IMAGE_HEIGHT - int(cm * PIXELS_PER_CM)
    
    # Determine line length and thickness based on cm value
    if cm % 20 == 0:  # Every 20 cm - longest line with label
        line_length = int(PIXELS_PER_CM * 3)  # 3 cm long
        line_width = THICK_LINE
        
        # Draw the line
        draw.line([(0, y), (line_length, y)], fill=BLACK, width=line_width)
        
        # Add text label
        text = f"{cm}"
        # Get text bounding box for positioning
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Position text to the right of the line
        text_x = line_length + int(PIXELS_PER_CM * 0.3)
        text_y = y - text_height // 2
        
        draw.text((text_x, text_y), text, fill=BLACK, font=font)
        
    elif cm % 10 == 0:  # Every 10 cm - medium line (no label)
        line_length = int(PIXELS_PER_CM * 2)  # 2 cm long
        line_width = MEDIUM_LINE
        draw.line([(0, y), (line_length, y)], fill=BLACK, width=line_width)
        
    elif cm % 5 == 0:  # Every 5 cm - shorter line
        line_length = int(PIXELS_PER_CM * 1.2)  # 1.2 cm long
        line_width = MEDIUM_LINE
        draw.line([(0, y), (line_length, y)], fill=GRAY, width=line_width)
        
    else:  # Every 1 cm - short line
        line_length = int(PIXELS_PER_CM * 0.6)  # 0.6 cm long
        line_width = THIN_LINE
        draw.line([(0, y), (line_length, y)], fill=GRAY, width=line_width)

# Draw vertical line along the ruler edge
draw.line([(0, 0), (0, IMAGE_HEIGHT)], fill=BLACK, width=THICK_LINE)

# Save the image
output_path = '/mnt/user-data/outputs/ruler_0-200cm.png'
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path, 'PNG', dpi=(DPI, DPI))

print(f"\nRuler image created successfully!")
print(f"Saved to: {output_path}")
print(f"Image size: {IMAGE_WIDTH}x{IMAGE_HEIGHT} pixels")
print(f"Resolution: {DPI} DPI")
print(f"Physical size when printed: {IMAGE_WIDTH/PIXELS_PER_CM:.1f} x {IMAGE_HEIGHT/PIXELS_PER_CM:.1f} cm")
