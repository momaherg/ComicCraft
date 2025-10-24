"""
Panel Generation Module

Generates comic panels by combining locations, characters, and scene descriptions.
Uses Google Gemini 2.5 Flash Image for generation with critic feedback loop.
"""
import os
from typing import Optional, List, Dict, Any
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
import io
from .utils import (
    save_debug_info,
    save_image,
    concatenate_character_images,
    get_generation_metadata
)
from .prompts import get_panel_generation_prompt, get_panel_critique_prompt


class PanelGenerator:
    """
    Handles panel generation using Gemini 2.5 Flash Image with critic loop
    """

    def __init__(self, api_key: str):
        """
        Initialize panel generator

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.generator_model = genai.GenerativeModel('gemini-2.5-flash-image')
        self.critic_model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def generate_panel(
        self,
        scene_prompt: str,
        character_images: Optional[List[str]] = None,
        location_image: Optional[str] = None,
        aspect_ratio: str = "3:4",
        max_iterations: int = 5,
        output_dir: str = "outputs/panels"
    ) -> Dict[str, Any]:
        """
        Generate a comic panel with characters and location

        Args:
            scene_prompt: Text description of the scene (10-500 chars)
            character_images: List of paths to internal character images (0-7)
            location_image: Optional path to location background image
            aspect_ratio: Aspect ratio for the panel (default: 3:4)
            max_iterations: Maximum iterations for generator-critic loop (default: 5)
            output_dir: Directory to save outputs

        Returns:
            Dictionary containing:
                - panel_image_path: Path to final panel image
                - iterations: Number of iterations used
                - metadata: Panel metadata including all inputs
        """
        print(f"\n{'='*60}")
        print(f"GENERATING PANEL")
        print(f"{'='*60}")
        print(f"Scene: {scene_prompt}")

        os.makedirs(output_dir, exist_ok=True)
        timestamp = get_generation_metadata("panel")["timestamp"]

        # Step 1: Prepare input images
        print("\n[STEP 1] Preparing input images...")
        prepared_images = self._prepare_input_images(
            character_images=character_images,
            location_image=location_image,
            output_dir=output_dir,
            timestamp=timestamp
        )

        # Step 2: Generation loop with critic feedback
        print("\n[STEP 2] Running generation loop with critic feedback...")
        final_panel_path, iterations_used = self._generation_critic_loop(
            scene_prompt=scene_prompt,
            prepared_images=prepared_images,
            aspect_ratio=aspect_ratio,
            max_iterations=max_iterations,
            output_dir=output_dir,
            timestamp=timestamp
        )

        # Create metadata
        metadata = get_generation_metadata(
            "panel",
            scene_prompt=scene_prompt,
            character_count=len(character_images) if character_images else 0,
            has_location=location_image is not None,
            aspect_ratio=aspect_ratio,
            iterations_used=iterations_used,
            panel_image=final_panel_path
        )

        # Save metadata
        metadata_path = os.path.join(
            output_dir,
            f"panel_{timestamp}_metadata.json"
        )
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Get concatenated character path if it exists
        concatenated_char_path = prepared_images.get("concatenated_character_path")

        print(f"\n{'='*60}")
        print(f"PANEL GENERATION COMPLETE!")
        print(f"Panel Image: {final_panel_path}")
        if concatenated_char_path:
            print(f"Character Lineup: {concatenated_char_path}")
        print(f"Iterations: {iterations_used}")
        print(f"Metadata: {metadata_path}")
        print(f"{'='*60}\n")

        result = {
            "panel_image_path": final_panel_path,
            "iterations": iterations_used,
            "metadata": metadata
        }

        # Add concatenated characters path if available
        if concatenated_char_path:
            result["concatenated_characters_path"] = concatenated_char_path

        return result

    def _prepare_input_images(
        self,
        character_images: Optional[List[str]],
        location_image: Optional[str],
        output_dir: str,
        timestamp: str
    ) -> Dict[str, Any]:
        """
        Prepare and concatenate input images for panel generation
        """
        prepared = {}

        # Concatenate character images if provided
        if character_images and len(character_images) > 0:
            print(f"  Concatenating {len(character_images)} character image(s)...")

            # Save to both main output dir and debug dir
            concatenated_filename = f"panel_{timestamp}_characters_concatenated.png"
            concatenated_path = os.path.join(output_dir, concatenated_filename)

            concatenated_path = concatenate_character_images(
                character_images,
                output_path=concatenated_path,
                alignment="bottom"
            )

            print(f"  [OUTPUT] Character lineup saved: {concatenated_path}")

            prepared["characters_image"] = concatenated_path
            prepared["character_count"] = len(character_images)
            prepared["concatenated_character_path"] = concatenated_path  # For return value
        else:
            prepared["characters_image"] = None
            prepared["character_count"] = 0
            prepared["concatenated_character_path"] = None

        # Location image
        if location_image:
            print(f"  Using location: {location_image}")
            prepared["location_image"] = location_image
        else:
            prepared["location_image"] = None

        return prepared

    def _generation_critic_loop(
        self,
        scene_prompt: str,
        prepared_images: Dict[str, Any],
        aspect_ratio: str,
        max_iterations: int,
        output_dir: str,
        timestamp: str
    ) -> tuple[str, int]:
        """
        Run the generator-critic feedback loop

        Returns:
            Tuple of (final_panel_path, iterations_used)
        """
        feedback_history = []
        final_panel_path = None

        for iteration in range(1, max_iterations + 1):
            print(f"\n  --- Iteration {iteration}/{max_iterations} ---")

            # Generate panel
            print(f"  [Generator] Creating panel...")
            panel_path = self._generate_panel_image(
                scene_prompt=scene_prompt,
                prepared_images=prepared_images,
                aspect_ratio=aspect_ratio,
                feedback_history=feedback_history,
                iteration=iteration,
                output_dir=output_dir,
                timestamp=timestamp
            )

            # Critique the generated panel
            print(f"  [Critic] Evaluating panel...")
            critique_result = self._critique_panel(
                panel_path=panel_path,
                scene_prompt=scene_prompt,
                iteration=iteration
            )

            # Check if panel is acceptable
            if critique_result["is_acceptable"]:
                print(f"  ✓ Panel approved by critic!")
                final_panel_path = panel_path
                return final_panel_path, iteration

            # Add feedback to history
            print(f"  ✗ Issues found: {critique_result['feedback']}")
            feedback_history.append({
                "iteration": iteration,
                "feedback": critique_result["feedback"],
                "panel_path": panel_path
            })

        # If we exhausted all iterations, use the last generated panel
        print(f"\n  ⚠ Reached max iterations. Using last generated panel.")
        if not final_panel_path and feedback_history:
            final_panel_path = feedback_history[-1]["panel_path"]

        return final_panel_path, max_iterations

    def _generate_panel_image(
        self,
        scene_prompt: str,
        prepared_images: Dict[str, Any],
        aspect_ratio: str,
        feedback_history: List[Dict[str, Any]],
        iteration: int,
        output_dir: str,
        timestamp: str
    ) -> str:
        """
        Generate a panel image using Gemini
        """
        # Build prompt using centralized prompts (aspect_ratio now handled by API config)
        prompt = get_panel_generation_prompt(
            scene_prompt=scene_prompt,
            character_count=prepared_images["character_count"],
            has_location=prepared_images["location_image"] is not None,
            feedback_history=feedback_history
        )

        # Save debug info
        save_debug_info(
            "panel",
            f"generation_iteration_{iteration}",
            {
                "scene_prompt": scene_prompt,
                "aspect_ratio": aspect_ratio,
                "character_count": prepared_images["character_count"],
                "has_location": prepared_images["location_image"] is not None,
                "feedback_count": len(feedback_history),
                "prompt": prompt
            }
        )

        # Prepare images for the model
        image_parts = []

        if prepared_images["characters_image"]:
            char_img = Image.open(prepared_images["characters_image"])
            image_parts.append(char_img)

        if prepared_images["location_image"]:
            loc_img = Image.open(prepared_images["location_image"])
            image_parts.append(loc_img)

        # Generate image using Gemini 2.5 Flash Image with specified aspect ratio
        print(f"    Calling Gemini 2.5 Flash Image for panel generation (aspect ratio: {aspect_ratio})...")
        try:
            # Gemini 2.5 Flash Image can generate images directly
            response = self.generator_model.generate_content([prompt] + image_parts)

            # Check if we got an image in the response
            if hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]

                # Look for image parts in the response
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # Extract image data
                            image_data = part.inline_data.data

                            # Save the image
                            filename = f"panel_{timestamp}_iter{iteration}.png"
                            output_path = os.path.join(output_dir, filename)
                            save_image(image_data, filename, output_dir)

                            # Save debug info
                            save_debug_info(
                                "panel",
                                f"generation_response_{iteration}",
                                {
                                    "iteration": iteration,
                                    "image_generated": True,
                                    "output_path": output_path
                                }
                            )

                            return output_path

            # If no image was generated, raise an error
            raise ValueError("No image was generated in the response")

        except Exception as e:
            print(f"    Error during generation: {e}")
            save_debug_info(
                "panel",
                f"generation_error_{iteration}",
                {"error": str(e), "iteration": iteration}
            )
            raise

    def _critique_panel(
        self,
        panel_path: str,
        scene_prompt: str,
        iteration: int
    ) -> Dict[str, Any]:
        """
        Critique a generated panel using Gemini

        Returns:
            Dictionary with:
                - is_acceptable: Boolean
                - feedback: String with specific issues
        """
        panel_img = Image.open(panel_path)

        # Use centralized critique prompt
        critique_prompt = get_panel_critique_prompt(scene_prompt=scene_prompt)

        try:
            response = self.critic_model.generate_content([critique_prompt, panel_img])
            response_text = response.text

            # Parse the response
            is_acceptable = "ACCEPTABLE: YES" in response_text
            feedback_start = response_text.find("FEEDBACK:") + len("FEEDBACK:")
            feedback = response_text[feedback_start:].strip()

            # Save debug info
            save_debug_info(
                "panel",
                f"critique_iteration_{iteration}",
                {
                    "iteration": iteration,
                    "panel_path": panel_path,
                    "is_acceptable": is_acceptable,
                    "feedback": feedback,
                    "full_response": response_text
                }
            )

            return {
                "is_acceptable": is_acceptable,
                "feedback": feedback
            }

        except Exception as e:
            print(f"    Error during critique: {e}")
            save_debug_info(
                "panel",
                f"critique_error_{iteration}",
                {"error": str(e), "iteration": iteration}
            )
            # If critique fails, accept the panel
            return {
                "is_acceptable": True,
                "feedback": f"Critique failed: {e}"
            }

