"""
Character Generation Module

Generates comic character images from photos, comic images, or text descriptions.
Uses Google Gemini 2.5 Flash Image for all generation.
"""
import os
import io
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
from .utils import (
    save_debug_info,
    save_image,
    get_generation_metadata,
    remove_green_screen,
    crop_to_content,
    create_compact_character_reference
)
from .green_screen import get_green_screen_pil_image
from .prompts import get_character_generation_prompt, get_character_internal_prompt


class CharacterGenerator:
    """
    Handles character generation using Google Gemini 2.5 Flash Image
    """

    def __init__(self, api_key: str):
        """
        Initialize character generator

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-image')

    def generate_character(
        self,
        character_name: str,
        height_cm: int,
        art_style: str,
        photo_path: Optional[str] = None,
        comic_image_path: Optional[str] = None,
        text_prompt: Optional[str] = None,
        style_ref_image_path: Optional[str] = None,
        output_dir: str = "outputs/characters"
    ) -> Dict[str, Any]:
        """
        Generate a character from photo, comic image, or text description

        Args:
            character_name: Name of the character
            height_cm: Height of character (90, 130, 180, etc.)
            art_style: Art style selection (one of 5 preset options)
            photo_path: Optional path to photo of real person
            comic_image_path: Optional path to existing comic character image
            text_prompt: Optional text description of character
            style_ref_image_path: Optional inspiring image for style reference
            output_dir: Directory to save outputs

        Behavior:
            - If ONLY comic_image_path is provided: Skips generation, uses image directly
            - If comic_image_path + other inputs: ERROR - not supported
            - Otherwise: Generates from scratch (text or photo)

        Returns:
            Dictionary containing:
                - character_image_path: Path to initial character design
                - internal_character_image_path: Path to character with ruler
                - metadata: Character metadata
        """
        print(f"\n{'='*60}")
        print(f"GENERATING CHARACTER: {character_name}")
        print(f"{'='*60}")

        # Validate inputs
        if not any([photo_path, comic_image_path, text_prompt]):
            raise ValueError("Must provide at least one: photo_path, comic_image_path, or text_prompt")

        os.makedirs(output_dir, exist_ok=True)
        timestamp = get_generation_metadata("character")["timestamp"]

        # Check if we have a ready comic character image (skip generation)
        skip_generation = (
            comic_image_path is not None and
            photo_path is None and
            text_prompt is None
        )

        if skip_generation:
            print("\n[STEP 1] Using existing comic character image (skipping generation)...")
            print(f"  Using image: {comic_image_path}")
            character_image_path = comic_image_path

            # Save debug info
            save_debug_info(
                "character",
                "using_existing_image",
                {
                    "character_name": character_name,
                    "comic_image_path": comic_image_path,
                    "skipped_generation": True
                }
            )
        else:
            # Step 1: Generate initial character design
            print("\n[STEP 1] Generating initial character design...")
            character_image_path = self._generate_initial_character(
                character_name=character_name,
                art_style=art_style,
                photo_path=photo_path,
                comic_image_path=comic_image_path,
                text_prompt=text_prompt,
                style_ref_image_path=style_ref_image_path,
                output_dir=output_dir,
                timestamp=timestamp
            )

        # Step 2: Generate internal character image with ruler
        print("\n[STEP 2] Generating internal character image with ruler...")
        internal_image_path = self._generate_internal_character_image(
            character_name=character_name,
            character_image_path=character_image_path,
            height_cm=height_cm,
            output_dir=output_dir,
            timestamp=timestamp
        )

        # Create metadata
        metadata = get_generation_metadata(
            "character",
            name=character_name,
            height_cm=height_cm,
            art_style=art_style,
            has_photo=photo_path is not None,
            has_comic_image=comic_image_path is not None,
            has_text_prompt=text_prompt is not None,
            has_style_ref=style_ref_image_path is not None,
            skipped_generation=skip_generation,
            character_image=character_image_path,
            internal_image=internal_image_path
        )

        # Save metadata
        metadata_path = os.path.join(
            output_dir,
            f"{character_name}_{timestamp}_metadata.json"
        )
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n{'='*60}")
        print(f"CHARACTER GENERATION COMPLETE!")
        print(f"Character Image: {character_image_path}")
        print(f"Internal Image: {internal_image_path}")
        print(f"Metadata: {metadata_path}")
        print(f"{'='*60}\n")

        return {
            "character_image_path": character_image_path,
            "internal_character_image_path": internal_image_path,
            "metadata": metadata
        }

    def _generate_initial_character(
        self,
        character_name: str,
        art_style: str,
        photo_path: Optional[str],
        comic_image_path: Optional[str],
        text_prompt: Optional[str],
        style_ref_image_path: Optional[str],
        output_dir: str,
        timestamp: str
    ) -> str:
        """
        Generate initial character design using Gemini 2.5 Flash Image
        """
        # Build the prompt using centralized prompts
        prompt = get_character_generation_prompt(
            character_name=character_name,
            art_style=art_style,
            text_prompt=text_prompt,
            is_from_photo=photo_path is not None
        )

        # Prepare input images
        input_parts = [prompt]

        if photo_path:
            print(f"  Using photo: {photo_path}")
            photo_img = Image.open(photo_path)
            input_parts.append(photo_img)

        # Note: comic_image_path should never reach here due to skip logic
        # If it does, it's an error - we don't transform comic images
        if comic_image_path:
            raise ValueError(
                "Comic image should not be passed to generation. "
                "This indicates the skip logic failed. "
                "Comic images should skip generation entirely."
            )

        if style_ref_image_path:
            print(f"  Using style reference: {style_ref_image_path}")
            style_img = Image.open(style_ref_image_path)
            input_parts.append(style_img)

        # Save debug info
        save_debug_info(
            "character",
            "initial_design_request",
            {
                "character_name": character_name,
                "art_style": art_style,
                "has_photo": photo_path is not None,
                "has_comic_image": comic_image_path is not None,
                "text_prompt": text_prompt,
                "has_style_ref": style_ref_image_path is not None,
                "prompt": prompt
            }
        )

        # Generate image using Gemini with portrait aspect ratio (3:4)
        print("  Calling Gemini 2.5 Flash Image for character generation...")
        response = self.model.generate_content(input_parts)

        # Extract and save the generated image
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]

            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        # Extract image data
                        image_data = part.inline_data.data

                        # Save the image
                        output_filename = f"{character_name}_{timestamp}_initial.png"
                        output_path = os.path.join(output_dir, output_filename)
                        save_image(image_data, output_filename, output_dir)

                        # Save debug info
                        save_debug_info(
                            "character",
                            "initial_design_response",
                            {
                                "character_name": character_name,
                                "output_path": output_path,
                                "image_generated": True
                            }
                        )

                        return output_path

        raise ValueError("No image was generated in the response")

    def _generate_internal_character_image(
        self,
        character_name: str,
        character_image_path: str,
        height_cm: int,
        output_dir: str,
        timestamp: str
    ) -> str:
        """
        Generate internal character reference using compact layout (no ruler visuals)

        Workflow:
        1. Create green screen background
        2. Generate full-body character on green screen
        3. Remove green background via chroma keying
        4. Crop to content bounds (accurate height measurement)
        5. Create compact reference (character + name, tight-fit width)

        The character is scaled using a standard resolution (10 px/cm) ensuring
        accurate relative heights when references are concatenated.
        """
        print("  [STEP 1] Creating green screen background...")

        # Create green screen image (portrait, ~2000x2700 for 3:4 ratio at high res)
        green_screen = get_green_screen_pil_image(width=2000, height=2700)

        # Build prompt using centralized prompts
        prompt = get_character_internal_prompt(
            character_name=character_name,
            height_cm=height_cm
        )

        # Load character image
        character_img = Image.open(character_image_path)

        # Save debug info
        save_debug_info(
            "character",
            "internal_image_request",
            {
                "character_name": character_name,
                "height_cm": height_cm,
                "character_image": character_image_path,
                "green_screen_size": f"{green_screen.width}x{green_screen.height}",
                "prompt": prompt
            }
        )

        print("  [STEP 2] Generating full-body character on green screen...")

        # Generate character on green screen
        response = self.model.generate_content([prompt, character_img, green_screen])

        # Extract the generated image
        generated_image_data = None
        if hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]

            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        generated_image_data = part.inline_data.data
                        break

        if generated_image_data is None:
            raise ValueError("No character image was generated on green screen")

        # Save the green screen version for debugging
        greenscreen_filename = f"{character_name}_{timestamp}_greenscreen.png"
        greenscreen_path = os.path.join(output_dir, greenscreen_filename)
        save_image(generated_image_data, greenscreen_filename, output_dir)

        print("  [STEP 3] Removing green screen background...")

        # Load the generated image and remove green screen
        generated_img = Image.open(io.BytesIO(generated_image_data))
        character_no_bg = remove_green_screen(generated_img, green_rgb=(0, 255, 0))

        # Save character with transparent background for debugging
        transparent_filename = f"{character_name}_{timestamp}_transparent_uncropped.png"
        transparent_path = os.path.join(output_dir, transparent_filename)
        character_no_bg.save(transparent_path, 'PNG')
        print(f"[DEBUG] Saved transparent (uncropped) character to {transparent_path}")

        print("  [STEP 3.5] Cropping to content bounds...")

        # Crop to remove empty transparent space for accurate height measurement
        character_cropped = crop_to_content(character_no_bg)

        # Save cropped version for debugging
        cropped_filename = f"{character_name}_{timestamp}_transparent.png"
        cropped_path = os.path.join(output_dir, cropped_filename)
        character_cropped.save(cropped_path, 'PNG')
        print(f"[DEBUG] Saved cropped character to {cropped_path}")

        print("  [STEP 4] Creating compact character reference...")

        # Create compact reference with accurate height
        output_filename = f"{character_name}_{timestamp}_internal.png"
        output_path = os.path.join(output_dir, output_filename)

        final_path = create_compact_character_reference(
            character_image=character_cropped,  # Use cropped image for accurate height
            character_height_cm=height_cm,
            character_name=character_name,
            output_path=output_path,
            pixels_per_cm=10.0  # Standard resolution: 10 pixels per cm
        )

        # Save debug info
        save_debug_info(
            "character",
            "internal_image_complete",
            {
                "character_name": character_name,
                "height_cm": height_cm,
                "greenscreen_path": greenscreen_path,
                "transparent_uncropped_path": transparent_path,
                "transparent_cropped_path": cropped_path,
                "final_path": final_path,
                "workflow": "green_screen -> chroma_key -> crop_to_content -> compact_reference",
                "pixels_per_cm": 10.0
            }
        )

        return final_path
