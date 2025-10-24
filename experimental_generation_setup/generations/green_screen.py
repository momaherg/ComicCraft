"""
Green Screen Generation for Character Composition

Generates a solid color background that can be easily removed via chroma keying.
"""
from PIL import Image
import io


# Green screen color (bright green for easy chroma keying)
GREEN_SCREEN_HEX = "#00FF00"
GREEN_SCREEN_RGB = (0, 255, 0)


def create_green_screen_image(width: int, height: int, format: str = "PNG") -> bytes:
    """
    Create a solid green screen image

    Args:
        width: Image width in pixels
        height: Image height in pixels
        format: Image format (default: PNG)

    Returns:
        Image bytes
    """
    # Create solid green image
    img = Image.new('RGB', (width, height), GREEN_SCREEN_RGB)

    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)

    return img_bytes.getvalue()


def get_green_screen_pil_image(width: int, height: int) -> Image.Image:
    """
    Create a solid green screen PIL Image

    Args:
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        PIL Image object
    """
    return Image.new('RGB', (width, height), GREEN_SCREEN_RGB)
