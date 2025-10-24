"""
Gradio Web UI for ComicCraft AI Testing

A comprehensive testing interface for character, location, and panel generation.
Run with: python ui/gradio_app.py
"""
import os
import sys
from pathlib import Path
from typing import Optional, List, Tuple
import gradio as gr
from dotenv import load_dotenv

# Add parent directory to path and adjust for experimental_generation_setup
sys.path.insert(0, str(Path(__file__).parent.parent / 'experimental_generation_setup'))

from generations import CharacterGenerator, LocationGenerator, PanelGenerator


# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

# Initialize generators (reused across requests)
char_gen = CharacterGenerator(GEMINI_API_KEY)
loc_gen = LocationGenerator(GEMINI_API_KEY)
panel_gen = PanelGenerator(GEMINI_API_KEY)


# ============================================================================
# CHARACTER GENERATION TAB
# ============================================================================

def generate_character_ui(
    character_name: str,
    height_cm: int,
    art_style: str,
    input_mode: str,
    text_prompt: Optional[str],
    photo_upload: Optional[str],
    comic_upload: Optional[str],
    style_ref_upload: Optional[str]
) -> Tuple[Optional[str], Optional[str], str]:
    """
    Handle character generation from UI inputs

    Returns:
        (initial_image_path, internal_image_path, status_message)
    """
    try:
        # Validate required inputs
        if not character_name or not character_name.strip():
            return None, None, "Error: Character name is required"

        if height_cm < 50 or height_cm > 250:
            return None, None, "Error: Height must be between 50-250 cm"

        # Determine inputs based on mode
        photo_path = None
        comic_path = None
        prompt = None
        style_ref = None

        if input_mode == "Text Description":
            if not text_prompt or not text_prompt.strip():
                return None, None, "Error: Text prompt is required for this mode"
            prompt = text_prompt
            style_ref = style_ref_upload if style_ref_upload else None

        elif input_mode == "Photo Transform":
            if not photo_upload:
                return None, None, "Error: Photo upload is required for this mode"
            photo_path = photo_upload
            prompt = text_prompt if text_prompt and text_prompt.strip() else "Transform into comic character"

        elif input_mode == "Comic Image (Skip Generation)":
            if not comic_upload:
                return None, None, "Error: Comic image upload is required for this mode"
            comic_path = comic_upload
            # No prompt or photo for skip mode

        elif input_mode == "Comic Image + Transform":
            if not comic_upload:
                return None, None, "Error: Comic image upload is required for this mode"
            if not text_prompt or not text_prompt.strip():
                return None, None, "Error: Text prompt is required to transform comic image"
            comic_path = comic_upload
            prompt = text_prompt

        # Generate character
        result = char_gen.generate_character(
            character_name=character_name.strip(),
            height_cm=int(height_cm),
            art_style=art_style,
            photo_path=photo_path,
            comic_image_path=comic_path,
            text_prompt=prompt,
            style_ref_image_path=style_ref,
            output_dir="outputs/characters/ui_test"
        )

        initial_path = result.get('character_image_path')
        internal_path = result.get('internal_character_image_path')

        status = f"✓ Character '{character_name}' generated successfully!\n"
        status += f"Initial design: {initial_path}\n"
        status += f"Internal reference: {internal_path}"

        return initial_path, internal_path, status

    except Exception as e:
        return None, None, f"✗ Error: {str(e)}"


# ============================================================================
# LOCATION GENERATION TAB
# ============================================================================

def generate_location_ui(
    location_name: str,
    art_style: str,
    input_mode: str,
    text_prompt: Optional[str],
    photo_upload: Optional[str]
) -> Tuple[Optional[str], str]:
    """
    Handle location generation from UI inputs

    Returns:
        (location_image_path, status_message)
    """
    try:
        # Validate required inputs
        if not location_name or not location_name.strip():
            return None, "Error: Location name is required"

        # Determine inputs based on mode
        photo_path = None
        prompt = None

        if input_mode == "Text Description":
            if not text_prompt or not text_prompt.strip():
                return None, "Error: Text prompt is required for this mode"
            prompt = text_prompt

        elif input_mode == "Photo Transform":
            if not photo_upload:
                return None, "Error: Photo upload is required for this mode"
            photo_path = photo_upload
            prompt = text_prompt if text_prompt and text_prompt.strip() else "Transform into comic background"

        # Generate location
        result = loc_gen.generate_location(
            location_name=location_name.strip(),
            art_style=art_style,
            photo_path=photo_path,
            text_prompt=prompt,
            output_dir="outputs/locations/ui_test"
        )

        location_path = result.get('location_image_path')

        status = f"✓ Location '{location_name}' generated successfully!\n"
        status += f"Location image: {location_path}"

        return location_path, status

    except Exception as e:
        return None, f"✗ Error: {str(e)}"


# ============================================================================
# PANEL GENERATION TAB
# ============================================================================

def generate_panel_ui(
    scene_prompt: str,
    character_uploads: Optional[List[str]],
    location_upload: Optional[str],
    aspect_ratio: str,
    max_iterations: int
) -> Tuple[Optional[str], Optional[str], str]:
    """
    Handle panel generation from UI inputs

    Returns:
        (panel_image_path, concatenated_chars_path, status_message)
    """
    try:
        # Validate scene prompt
        if not scene_prompt or not scene_prompt.strip():
            return None, None, "Error: Scene prompt is required"

        if len(scene_prompt) < 10:
            return None, None, "Error: Scene prompt must be at least 10 characters"

        if len(scene_prompt) > 500:
            return None, None, "Error: Scene prompt must be at most 500 characters"

        # Validate character count
        if character_uploads and len(character_uploads) > 7:
            return None, None, "Error: Maximum 7 characters allowed per panel"

        # Generate panel
        result = panel_gen.generate_panel(
            scene_prompt=scene_prompt.strip(),
            character_images=character_uploads if character_uploads else None,
            location_image=location_upload if location_upload else None,
            aspect_ratio=aspect_ratio,
            max_iterations=int(max_iterations),
            output_dir="outputs/panels/ui_test"
        )

        panel_path = result.get('panel_image_path')
        concatenated_chars_path = result.get('concatenated_characters_path')
        iterations = result.get('iterations', 0)

        status = f"✓ Panel generated successfully!\n"
        status += f"Iterations used: {iterations}/{max_iterations}\n"
        status += f"Panel image: {panel_path}\n"
        if concatenated_chars_path:
            status += f"Character lineup: {concatenated_chars_path}\n"
        status += f"Characters: {len(character_uploads) if character_uploads else 0}\n"
        status += f"Location: {'Yes' if location_upload else 'No'}"

        return panel_path, concatenated_chars_path, status

    except Exception as e:
        return None, None, f"✗ Error: {str(e)}"


# ============================================================================
# GRADIO INTERFACE
# ============================================================================

def create_ui():
    """Create the Gradio interface"""

    with gr.Blocks(title="ComicCraft AI - Testing Interface", theme=gr.themes.Soft()) as app:

        gr.Markdown(
            """
            # ComicCraft AI - Testing Interface

            Test character, location, and panel generation with different input modes and configurations.
            **Note:** All outputs are saved to `outputs/` directories with debug logs.
            """
        )

        with gr.Tabs():

            # ================================================================
            # TAB 1: CHARACTER GENERATION
            # ================================================================
            with gr.Tab("Character Generation"):
                gr.Markdown("### Generate comic characters from text, photos, or existing comic images")

                with gr.Row():
                    with gr.Column(scale=1):
                        char_name = gr.Textbox(
                            label="Character Name",
                            placeholder="e.g., Luna, Alex, Shadow",
                            value="TestCharacter"
                        )
                        char_height = gr.Number(
                            label="Height (cm)",
                            value=130,
                            minimum=50,
                            maximum=250
                        )
                        char_style = gr.Dropdown(
                            label="Art Style",
                            choices=["Manga", "American Comic", "Webtoon", "European BD", "Indie"],
                            value="Manga"
                        )

                        char_input_mode = gr.Radio(
                            label="Input Mode",
                            choices=[
                                "Text Description",
                                "Photo Transform",
                                "Comic Image (Skip Generation)",
                                "Comic Image + Transform"
                            ],
                            value="Text Description"
                        )

                        char_text_prompt = gr.Textbox(
                            label="Text Prompt",
                            placeholder="Describe the character or transformation...",
                            lines=3,
                            value="A young girl with silver hair and purple eyes, wearing a magical outfit"
                        )

                        char_photo = gr.Image(
                            label="Photo Upload (for Photo Transform mode)",
                            type="filepath"
                        )

                        char_comic = gr.Image(
                            label="Comic Image Upload (for Comic Image modes)",
                            type="filepath"
                        )

                        char_style_ref = gr.Image(
                            label="Style Reference (optional)",
                            type="filepath"
                        )

                        char_generate_btn = gr.Button("Generate Character", variant="primary")

                    with gr.Column(scale=1):
                        char_status = gr.Textbox(
                            label="Status",
                            lines=5,
                            interactive=False
                        )

                        with gr.Row():
                            char_initial_output = gr.Image(
                                label="Initial Design",
                                type="filepath"
                            )
                            char_internal_output = gr.Image(
                                label="Internal Reference (with ruler)",
                                type="filepath"
                            )

                # Character generation handler
                char_generate_btn.click(
                    fn=generate_character_ui,
                    inputs=[
                        char_name,
                        char_height,
                        char_style,
                        char_input_mode,
                        char_text_prompt,
                        char_photo,
                        char_comic,
                        char_style_ref
                    ],
                    outputs=[char_initial_output, char_internal_output, char_status]
                )

            # ================================================================
            # TAB 2: LOCATION GENERATION
            # ================================================================
            with gr.Tab("Location Generation"):
                gr.Markdown("### Generate comic backgrounds/locations from text or photos")

                with gr.Row():
                    with gr.Column(scale=1):
                        loc_name = gr.Textbox(
                            label="Location Name",
                            placeholder="e.g., Forest, City Street, Spaceship",
                            value="TestLocation"
                        )
                        loc_style = gr.Dropdown(
                            label="Art Style",
                            choices=["Manga", "American Comic", "Webtoon", "European BD", "Indie"],
                            value="Manga"
                        )

                        loc_input_mode = gr.Radio(
                            label="Input Mode",
                            choices=["Text Description", "Photo Transform"],
                            value="Text Description"
                        )

                        loc_text_prompt = gr.Textbox(
                            label="Text Prompt",
                            placeholder="Describe the location...",
                            lines=4,
                            value="A mystical forest with glowing mushrooms and ethereal light"
                        )

                        loc_photo = gr.Image(
                            label="Photo Upload (for Photo Transform mode)",
                            type="filepath"
                        )

                        loc_generate_btn = gr.Button("Generate Location", variant="primary")

                    with gr.Column(scale=1):
                        loc_status = gr.Textbox(
                            label="Status",
                            lines=5,
                            interactive=False
                        )

                        loc_output = gr.Image(
                            label="Generated Location (16:9)",
                            type="filepath"
                        )

                # Location generation handler
                loc_generate_btn.click(
                    fn=generate_location_ui,
                    inputs=[
                        loc_name,
                        loc_style,
                        loc_input_mode,
                        loc_text_prompt,
                        loc_photo
                    ],
                    outputs=[loc_output, loc_status]
                )

            # ================================================================
            # TAB 3: PANEL GENERATION
            # ================================================================
            with gr.Tab("Panel Generation"):
                gr.Markdown("### Generate complete comic panels with characters and locations")

                with gr.Row():
                    with gr.Column(scale=1):
                        panel_scene = gr.Textbox(
                            label="Scene Prompt",
                            placeholder="Describe the scene, character actions, and composition...",
                            lines=5,
                            value="Luna standing in the foreground with a confident pose, mystical forest in background"
                        )

                        panel_characters = gr.File(
                            label="Character Images (upload internal references, 0-7 max)",
                            file_count="multiple",
                            type="filepath"
                        )

                        panel_location = gr.Image(
                            label="Location Background (optional)",
                            type="filepath"
                        )

                        panel_aspect = gr.Dropdown(
                            label="Aspect Ratio",
                            choices=["3:4", "16:9", "4:3", "1:1", "9:16"],
                            value="3:4"
                        )

                        panel_iterations = gr.Slider(
                            label="Max Iterations",
                            minimum=1,
                            maximum=5,
                            step=1,
                            value=3
                        )

                        panel_generate_btn = gr.Button("Generate Panel", variant="primary")

                    with gr.Column(scale=1):
                        panel_status = gr.Textbox(
                            label="Status",
                            lines=5,
                            interactive=False
                        )

                        panel_concat_chars = gr.Image(
                            label="Character Lineup (Concatenated)",
                            type="filepath"
                        )

                        panel_output = gr.Image(
                            label="Generated Panel",
                            type="filepath"
                        )

                # Panel generation handler
                panel_generate_btn.click(
                    fn=generate_panel_ui,
                    inputs=[
                        panel_scene,
                        panel_characters,
                        panel_location,
                        panel_aspect,
                        panel_iterations
                    ],
                    outputs=[panel_output, panel_concat_chars, panel_status]
                )

        gr.Markdown(
            """
            ---
            **Tips:**
            - All generations are saved to `outputs/` with timestamped filenames
            - Debug logs are saved to `outputs/debug/` for troubleshooting
            - For panel generation, use the internal character references (with rulers)
            - Character names in scene prompts are automatically extracted from uploaded images
            """
        )

    return app


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ComicCraft AI - Testing Interface")
    print("="*70)
    print(f"API Key loaded: {GEMINI_API_KEY[:20]}...")
    print("\nStarting Gradio interface...")
    print("Access the UI at: http://localhost:7860")
    print("="*70 + "\n")

    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
