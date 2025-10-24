"""
Location Generation Module

Generates comic location/background images from photos or text descriptions.
Uses Google Gemini 2.5 Flash Image for all generation.
"""
import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
from .utils import (
    save_debug_info,
    save_image,
    get_generation_metadata
)
from .prompts import get_location_generation_prompt


class LocationGenerator:
    """
    Handles location generation using Google Gemini 2.5 Flash Image
    """

    def __init__(self, api_key: str):
        """
        Initialize location generator

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-image')

    def generate_location(
        self,
        location_name: str,
        art_style: str,
        photo_path: Optional[str] = None,
        text_prompt: Optional[str] = None,
        output_dir: str = "outputs/locations"
    ) -> Dict[str, Any]:
        """
        Generate a location from photo or text description

        Args:
            location_name: Name of the location
            art_style: Art style selection (one of 5 preset options)
            photo_path: Optional path to photo of real location/scenery
            text_prompt: Optional text description of location
            output_dir: Directory to save outputs

        Returns:
            Dictionary containing:
                - location_image_path: Path to generated location image
                - metadata: Location metadata
        """
        print(f"\n{'='*60}")
        print(f"GENERATING LOCATION: {location_name}")
        print(f"{'='*60}")

        # Validate inputs
        if not any([photo_path, text_prompt]):
            raise ValueError("Must provide at least one: photo_path or text_prompt")

        os.makedirs(output_dir, exist_ok=True)
        timestamp = get_generation_metadata("location")["timestamp"]

        # Generate location image
        print("\n[STEP 1] Generating location image...")
        location_image_path = self._generate_location_image(
            location_name=location_name,
            art_style=art_style,
            photo_path=photo_path,
            text_prompt=text_prompt,
            output_dir=output_dir,
            timestamp=timestamp
        )

        # Create metadata
        metadata = get_generation_metadata(
            "location",
            name=location_name,
            art_style=art_style,
            has_photo=photo_path is not None,
            has_text_prompt=text_prompt is not None,
            location_image=location_image_path
        )

        # Save metadata
        metadata_path = os.path.join(
            output_dir,
            f"{location_name}_{timestamp}_metadata.json"
        )
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"\n{'='*60}")
        print(f"LOCATION GENERATION COMPLETE!")
        print(f"Location Image: {location_image_path}")
        print(f"Metadata: {metadata_path}")
        print(f"{'='*60}\n")

        return {
            "location_image_path": location_image_path,
            "metadata": metadata
        }

    def _generate_location_image(
        self,
        location_name: str,
        art_style: str,
        photo_path: Optional[str],
        text_prompt: Optional[str],
        output_dir: str,
        timestamp: str
    ) -> str:
        """
        Generate location image using Gemini 2.5 Flash Image
        """
        # Build the prompt using centralized prompts
        prompt = get_location_generation_prompt(
            location_name=location_name,
            art_style=art_style,
            text_prompt=text_prompt,
            is_from_photo=photo_path is not None
        )

        # Prepare input parts
        input_parts = [prompt]

        if photo_path:
            print(f"  Using photo: {photo_path}")
            photo_img = Image.open(photo_path)
            input_parts.append(photo_img)

        print(f"  Art Style: {art_style}")
        if text_prompt:
            print(f"  Using text: {text_prompt}")

        # Save debug info
        save_debug_info(
            "location",
            "generation_request",
            {
                "location_name": location_name,
                "art_style": art_style,
                "has_photo": photo_path is not None,
                "text_prompt": text_prompt,
                "prompt": prompt
            }
        )

        print("  Calling Gemini 2.5 Flash Image for location generation...")

        # Generate image using Gemini with landscape aspect ratio (16:9)
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
                        output_filename = f"{location_name}_{timestamp}.png"
                        output_path = os.path.join(output_dir, output_filename)
                        save_image(image_data, output_filename, output_dir)

                        # Save debug info
                        save_debug_info(
                            "location",
                            "generation_response",
                            {
                                "location_name": location_name,
                                "output_path": output_path,
                                "image_generated": True
                            }
                        )

                        return output_path

        raise ValueError("No location image was generated in the response")
