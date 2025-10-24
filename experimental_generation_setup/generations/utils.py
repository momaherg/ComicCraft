"""
Utility functions for AI generations
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import base64
from io import BytesIO


def save_debug_info(
    generation_type: str,
    step: str,
    data: Dict[str, Any],
    output_dir: str = "outputs/debug"
) -> str:
    """
    Save debug information for a generation step

    Args:
        generation_type: Type of generation (character, location, panel)
        step: Description of the step
        data: Data to save
        output_dir: Directory to save debug info

    Returns:
        Path to saved debug file
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{generation_type}_{step}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # Convert any non-serializable data
    serializable_data = {}
    for key, value in data.items():
        if isinstance(value, (str, int, float, bool, dict, list, type(None))):
            serializable_data[key] = value
        else:
            serializable_data[key] = str(value)

    with open(filepath, 'w') as f:
        json.dump(serializable_data, f, indent=2)

    print(f"[DEBUG] Saved {step} to {filepath}")
    return filepath


def save_image(
    image_data: bytes,
    filename: str,
    output_dir: str
) -> str:
    """
    Save image data to file

    Args:
        image_data: Image bytes
        filename: Name for the file
        output_dir: Directory to save image

    Returns:
        Path to saved image
    """
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, 'wb') as f:
        f.write(image_data)

    print(f"[OUTPUT] Saved image to {filepath}")
    return filepath


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode image file to base64 string

    Args:
        image_path: Path to image file

    Returns:
        Base64 encoded string
    """
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    Convert PIL Image to base64 string

    Args:
        image: PIL Image object
        format: Image format (PNG, JPEG, etc.)

    Returns:
        Base64 encoded string
    """
    buffered = BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def concatenate_character_images(
    character_images: list[str],
    output_path: Optional[str] = None,
    alignment: str = "bottom"
) -> str:
    """
    Concatenate multiple character images horizontally

    Args:
        character_images: List of paths to character images
        output_path: Optional path to save concatenated image
        alignment: Vertical alignment ("bottom", "top", "center"). Default: "bottom"

    Returns:
        Path to concatenated image
    """
    if not character_images:
        raise ValueError("No character images provided")

    images = [Image.open(img_path).convert('RGBA') for img_path in character_images]

    # Get max height and total width
    max_height = max(img.height for img in images)
    total_width = sum(img.width for img in images)

    # Create new image with white background
    concatenated = Image.new('RGBA', (total_width, max_height), (255, 255, 255, 255))

    # Paste images side by side
    x_offset = 0
    for img in images:
        # Calculate vertical offset based on alignment
        if alignment == "bottom":
            # Bottom-align (character feet at same level)
            y_offset = max_height - img.height
        elif alignment == "top":
            # Top-align
            y_offset = 0
        else:  # center
            # Center vertically
            y_offset = (max_height - img.height) // 2

        concatenated.paste(img, (x_offset, y_offset), img)
        x_offset += img.width

    # Save
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/debug/concatenated_characters_{timestamp}.png"

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    concatenated.save(output_path)

    print(f"[DEBUG] Concatenated {len(images)} character images ({alignment}-aligned) to {output_path}")
    return output_path


def get_ruler_image_path() -> str:
    """
    Get the path to the ruler reference image

    Returns:
        Path to ruler_image.png in project root
    """
    # Get project root (3 levels up from this file)
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    ruler_path = project_root / "ruler_image.png"

    if not ruler_path.exists():
        raise FileNotFoundError(
            f"ruler_image.png not found at {ruler_path}. "
            "Please ensure ruler_image.png exists in the project root."
        )

    print(f"[DEBUG] Using ruler image: {ruler_path}")
    return str(ruler_path)


def get_generation_metadata(
    generation_type: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized metadata for a generation

    Args:
        generation_type: Type of generation
        **kwargs: Additional metadata fields

    Returns:
        Metadata dictionary
    """
    metadata = {
        "type": generation_type,
        "created_at": datetime.now().isoformat(),
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
    }
    metadata.update(kwargs)
    return metadata


def remove_green_screen(
    image: Image.Image,
    green_rgb: tuple = (0, 255, 0),
    tolerance: int = 80
) -> Image.Image:
    """
    Remove green screen background from image using conservative chroma keying

    Uses HSV color space to detect only pure bright green backgrounds,
    preserving greenish colors in clothing, eyes, etc.

    Args:
        image: PIL Image with green screen background
        green_rgb: RGB tuple of green screen color (default: bright green)
        tolerance: Color tolerance in HSV space (0-100, default: 80)

    Returns:
        PIL Image with transparent background (RGBA)
    """
    import numpy as np

    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Convert to numpy array for faster processing
    img_array = np.array(image)

    # Extract RGB channels
    r, g, b = img_array[:,:,0], img_array[:,:,1], img_array[:,:,2]

    # Method 1: HSV-based green detection (conservative - only bright saturated greens)
    # Convert RGB to HSV
    img_hsv = image.convert('HSV')
    hsv_array = np.array(img_hsv)
    h, s, v = hsv_array[:,:,0], hsv_array[:,:,1], hsv_array[:,:,2]

    # NARROWER green hue range - pure green only (not yellow-green or cyan-green)
    # Green hue is around 120 degrees = 85 in PIL's 0-255 scale
    green_hue_min = 70   # Narrower range (was 35)
    green_hue_max = 110  # Narrower range (was 140)
    saturation_min = 100  # HIGH saturation required (was 30) - only vivid greens
    value_min = 130       # BRIGHT greens only (was 20) - no dark greens

    # Create mask for green pixels in HSV space (very conservative)
    mask_hsv = (
        (h >= green_hue_min) & (h <= green_hue_max) &
        (s >= saturation_min) &
        (v >= value_min)
    )

    # Method 2: RGB-based green detection (for extremely bright pure greens)
    # Green must DOMINATE red and blue significantly
    mask_rgb = (g > r + 50) & (g > b + 50) & (g > 180)  # Much stricter

    # Combine both masks (AND logic - both must agree for conservative removal)
    final_mask = mask_hsv & mask_rgb

    # Apply mask to alpha channel
    alpha = np.where(final_mask, 0, 255).astype(np.uint8)

    # Create new RGBA array
    result_array = img_array.copy()
    result_array[:,:,3] = alpha

    # Convert back to PIL Image
    result_image = Image.fromarray(result_array, 'RGBA')

    total_pixels = final_mask.size
    transparent_pixels = np.sum(final_mask)
    percentage = (transparent_pixels / total_pixels) * 100

    print(f"[DEBUG] Green screen removal: {transparent_pixels:,} pixels ({percentage:.1f}%) made transparent")

    return result_image


def crop_to_content(image: Image.Image) -> Image.Image:
    """
    Crop image to the bounding box of non-transparent pixels

    This removes empty transparent space around the character, ensuring
    accurate height measurements when scaling.

    Args:
        image: PIL Image with transparency (RGBA)

    Returns:
        Cropped PIL Image with only visible content
    """
    if image.mode != 'RGBA':
        return image

    # Get bounding box of non-transparent pixels
    # getbbox() returns (left, top, right, bottom) or None if all transparent
    bbox = image.getbbox()

    if bbox:
        cropped = image.crop(bbox)
        print(f"[DEBUG] Cropped from {image.width}x{image.height} to {cropped.width}x{cropped.height} (bbox: {bbox})")
        return cropped
    else:
        print("[DEBUG] Warning: Image is completely transparent, cannot crop")
        return image


def create_compact_character_reference(
    character_image: Image.Image,
    character_height_cm: int,
    character_name: str,
    output_path: str,
    pixels_per_cm: float = 10.0,
    max_character_height_cm: int = 200
) -> str:
    """
    Create a compact character reference with FIXED HEIGHT for perfect concatenation

    All character references have the same canvas height, with characters positioned
    at their correct relative heights. This ensures that when concatenated side-by-side,
    they form a uniform landscape image with accurate height relationships.

    Args:
        character_image: PIL Image of character (cropped to content, transparent background)
        character_height_cm: Target height of character in centimeters
        character_name: Name to display at bottom
        output_path: Path to save the final reference image
        pixels_per_cm: Resolution standard for height scaling (default: 10 px/cm)
        max_character_height_cm: Maximum character height for canvas sizing (default: 200cm)

    Returns:
        Path to saved reference image
    """
    from PIL import ImageDraw, ImageFont

    print(f"[DEBUG] Creating compact reference for {character_name} at {character_height_cm}cm")
    print(f"[DEBUG] Input character size: {character_image.width}x{character_image.height}px")

    # Calculate target character height in pixels using standard resolution
    target_character_height_px = int(character_height_cm * pixels_per_cm)

    # Scale character to target height (maintaining aspect ratio)
    char_aspect_ratio = character_image.width / character_image.height
    scaled_char_width = int(target_character_height_px * char_aspect_ratio)
    scaled_char_height = target_character_height_px

    print(f"[DEBUG] Target height: {character_height_cm}cm = {target_character_height_px}px")
    print(f"[DEBUG] Scaled character: {scaled_char_width}x{scaled_char_height}px")

    character_scaled = character_image.resize(
        (scaled_char_width, scaled_char_height),
        Image.Resampling.LANCZOS
    )

    # Fixed name field height (8% of max height, min 60px, max 100px)
    name_field_height_px = max(60, min(100, int(max_character_height_cm * pixels_per_cm * 0.08)))

    # Fixed canvas height for ALL characters (max height + name field)
    canvas_height = int(max_character_height_cm * pixels_per_cm) + name_field_height_px

    # Tight-fit width (character width + padding)
    horizontal_padding = max(10, int(scaled_char_width * 0.05))
    canvas_width = scaled_char_width + (2 * horizontal_padding)

    print(f"[DEBUG] Fixed canvas height: {canvas_height}px (for all characters)")
    print(f"[DEBUG] Canvas width: {canvas_width}px (tight-fit)")
    print(f"[DEBUG] Name field: {name_field_height_px}px")

    # Create white background canvas with FIXED HEIGHT
    canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 255))

    # Position character at BOTTOM (above name field)
    # This ensures shorter characters have empty space above, taller characters fill more space
    char_x = horizontal_padding
    char_y = canvas_height - name_field_height_px - scaled_char_height

    print(f"[DEBUG] Character position: ({char_x}, {char_y})")
    print(f"[DEBUG] Empty space above character: {char_y}px")

    # Paste character onto canvas with alpha blending
    canvas.paste(character_scaled, (char_x, char_y), character_scaled)

    # Add character name label
    draw = ImageDraw.Draw(canvas)

    # Font size: 60% of name field height
    font_size = int(name_field_height_px * 0.6)

    try:
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        if font is None:
            font = ImageFont.load_default()
    except Exception as e:
        print(f"[DEBUG] Could not load custom font: {e}")
        font = ImageFont.load_default()

    # Draw name label
    name_text = f"{character_name}"
    bbox = draw.textbbox((0, 0), name_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center text in name field
    text_x = (canvas_width - text_width) // 2
    text_y = canvas_height - name_field_height_px + (name_field_height_px - text_height) // 2

    # Draw text with black color
    draw.text((text_x, text_y), name_text, fill=(0, 0, 0, 255), font=font)

    print(f"[DEBUG] Name label: '{name_text}' at ({text_x}, {text_y}), font: {font_size}px")

    # Save reference image
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    canvas.save(output_path, 'PNG')

    print(f"[OUTPUT] Compact reference: {canvas_width}x{canvas_height}px (fixed height) saved to {output_path}")

    return output_path


def composite_character_on_ruler(
    character_image: Image.Image,
    ruler_image_path: str,
    character_height_cm: int,
    character_name: str,
    output_path: str
) -> str:
    """
    Composite a character image onto a ruler background at the correct height with name label

    The ruler image is 200cm tall. We create a composite that's larger (ruler + name field).
    For a 1000x2000 ruler, the output is 1000x2200 (200px for name).

    Args:
        character_image: PIL Image of character (should have transparent background, cropped to content)
        ruler_image_path: Path to ruler reference image
        character_height_cm: Target height of character in centimeters
        character_name: Name to display at bottom
        output_path: Path to save the final composited image

    Returns:
        Path to saved composite image
    """
    from PIL import ImageDraw, ImageFont

    # Open ruler image
    ruler = Image.open(ruler_image_path).convert('RGBA')

    # Calculate pixels per cm from ruler image
    # The ruler image is 200cm tall (just the ruler, no name field)
    ruler_height_cm = 200
    pixels_per_cm = ruler.height / ruler_height_cm

    print(f"[DEBUG] Ruler: {ruler.width}x{ruler.height}px, {pixels_per_cm:.2f} px/cm")

    # Calculate name field height (10% of ruler height, min 150px, max 250px)
    name_field_height_px = max(150, min(250, int(ruler.height * 0.10)))

    print(f"[DEBUG] Name field height: {name_field_height_px}px")

    # Create composite image (ruler height + name field)
    composite_height = ruler.height + name_field_height_px
    composite = Image.new('RGBA', (ruler.width, composite_height), (255, 255, 255, 255))

    # Paste ruler onto top portion of composite
    composite.paste(ruler, (0, 0), ruler)

    draw = ImageDraw.Draw(composite)

    # Calculate target character height in pixels
    target_character_height_px = int(character_height_cm * pixels_per_cm)

    print(f"[DEBUG] Target character height: {character_height_cm}cm = {target_character_height_px}px")
    print(f"[DEBUG] Character image size (cropped): {character_image.width}x{character_image.height}px")

    # Scale character to target height (maintaining aspect ratio)
    char_aspect_ratio = character_image.width / character_image.height
    scaled_char_width = int(target_character_height_px * char_aspect_ratio)
    scaled_char_height = target_character_height_px

    print(f"[DEBUG] Scaled character: {scaled_char_width}x{scaled_char_height}px")

    character_scaled = character_image.resize(
        (scaled_char_width, scaled_char_height),
        Image.Resampling.LANCZOS
    )

    # Position character on the ruler
    # Character's feet should be at y = ruler.height (bottom of ruler, top of name field)
    # Character's head should be at y = ruler.height - scaled_char_height
    char_x = ruler.width // 3  # Position character about 1/3 from left (after ruler marks)
    char_y = ruler.height - scaled_char_height

    print(f"[DEBUG] Character position: ({char_x}, {char_y})")
    print(f"[DEBUG] Character spans from {char_y}px to {char_y + scaled_char_height}px")
    print(f"[DEBUG] Character feet at: {char_y + scaled_char_height}px = {(ruler.height - (char_y + scaled_char_height)) / pixels_per_cm:.1f}cm from ruler bottom")

    # Paste character onto composite with alpha blending
    composite.paste(character_scaled, (char_x, char_y), character_scaled)

    # Add character name label at the bottom in the name field
    # Font size should be 60-80% of name field height
    font_size = int(name_field_height_px * 0.65)

    try:
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                break
        if font is None:
            # Fallback to default, but try to make it bigger
            font = ImageFont.load_default()
            print("[DEBUG] Using default font (size may be small)")
    except Exception as e:
        print(f"[DEBUG] Could not load custom font: {e}")
        font = ImageFont.load_default()

    # Draw name label
    name_text = f"Name: {character_name}"
    bbox = draw.textbbox((0, 0), name_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Center text horizontally and vertically in name field
    text_x = (ruler.width - text_width) // 2
    text_y = ruler.height + (name_field_height_px - text_height) // 2

    print(f"[DEBUG] Name label: '{name_text}' at ({text_x}, {text_y}), font size: {font_size}px")

    # Draw text with black color
    draw.text((text_x, text_y), name_text, fill=(0, 0, 0, 255), font=font)

    # Save composite
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    composite.save(output_path, 'PNG')

    print(f"[OUTPUT] Composited character '{character_name}' at {character_height_cm}cm height")
    print(f"[OUTPUT] Final image: {composite.width}x{composite.height}px saved to {output_path}")

    return output_path
