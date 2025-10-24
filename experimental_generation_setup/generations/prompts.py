"""
Centralized Prompts for Comic Generation

All prompts used across character, location, and panel generation.
Modify these to adjust generation behavior across the entire system.

═══════════════════════════════════════════════════════════════════
IMAGE FLOW OVERVIEW
═══════════════════════════════════════════════════════════════════

Each prompt function defines how TEXT prompts and IMAGE inputs combine
to guide the AI model. Here's how images flow through the system:

1. CHARACTER GENERATION:
   Option A - Generate from text/photo:
     Input:  [Text prompt] + [Optional: photo OR style ref]
     Output: Character portrait (3:4 ratio)
     ↓
     Input:  [Character portrait] + [Ruler image]
     Output: Internal character reference (character + ruler + name)

   Option B - Use ready comic image (SKIP generation):
     Input:  [Ready comic image] + [Ruler image]
     Output: Internal character reference (character + ruler + name)

2. LOCATION GENERATION:
   Input:  [Text prompt] + [Optional: photo of location]
   Output: Background scene (16:9 ratio)

3. PANEL GENERATION (with critic loop):
   Input:  [Scene description] + [Character references] + [Location image]
   Output: Complete panel
   ↓
   Input:  [Panel] + [Original scene description]
   Output: Critique (ACCEPTABLE: YES/NO + FEEDBACK)
   ↓ (if NO)
   Input:  [Scene description] + [Images] + [Previous feedback]
   Output: Improved panel
   ... (repeat up to 5 times)

═══════════════════════════════════════════════════════════════════
PROMPT STRUCTURE
═══════════════════════════════════════════════════════════════════

Each prompt function has two types of inputs:

TEXT INPUTS (via parameters):
  - Passed as function arguments
  - Used to build the text prompt string
  - Example: character_name, art_style, scene_prompt

IMAGE INPUTS (passed to model separately):
  - Passed to the AI model along with the prompt
  - Marked as [Required] or [Optional] in docstrings
  - Example: photo, comic_image, character_references

The generation modules (character_gen.py, location_gen.py, panel_gen.py)
handle loading and passing images to the model.

═══════════════════════════════════════════════════════════════════
"""

# ==============================================================================
# CHARACTER GENERATION PROMPTS
# ==============================================================================

def get_character_generation_prompt(
    character_name: str,
    art_style: str,
    text_prompt: str = None,
    is_from_photo: bool = False
) -> str:
    """
    Prompt for generating initial character design

    TEXT INPUTS (via parameters):
    - character_name: Name of the character (e.g., "Luna", "Detective Morgan")
    - art_style: Visual style (e.g., "Manga", "American Comic", "Film Noir")
    - text_prompt: Optional description of character appearance
    - is_from_photo: True if transforming from a real photo

    IMAGE INPUTS (passed to model separately):
    - [Optional] Photo of real person (if is_from_photo=True)
    - [Optional] Style reference image (for inspiration)

    USAGE SCENARIOS:
    1. Text only: text_prompt only → Generate from description
    2. Photo transform: photo image + text_prompt → Transform photo to comic
    3. With style ref: Any above + style reference image → Match specific style

    IMPORTANT: Comic character images are NOT transformed!
    If you have a ready comic character image, skip this function entirely
    and use it directly with get_character_internal_prompt() to add the ruler.

    OUTPUT: Portrait-oriented character illustration (3:4 ratio)
    """
    prompt_parts = [
        f"Create an image of a character design for a comic book in {art_style} style."
    ]

    if text_prompt:
        prompt_parts.append(f"\nCharacter Description: {text_prompt}")

    if is_from_photo:
        prompt_parts.append("\nThe character should be similar to the person in the photo, maintaining facial features and proportions, but in a comic book style.")

    prompt_parts.extend([
        "\nRequirements:",
        "- Portrait orientation",
        "- Character centered and clearly visible",
        "- Clean, professional comic book illustration",
        "- High quality, detailed artwork",
        "- Consistent with the art style"
    ])

    return "\n".join(prompt_parts)


def get_character_internal_prompt(
    character_name: str,
    height_cm: int
) -> str:
    """
    Prompt for generating internal character reference with green screen

    TEXT INPUTS (via parameters):
    - character_name: Name of the character
    - height_cm: Character height in centimeters (e.g., 90, 130, 180)

    IMAGE INPUTS (passed to model separately):
    - [Required] character_image: The initial character design (portrait)
    - [Required] green_screen_image: Solid bright green background (#00FF00)

    USAGE:
    This prompt creates a full-body character on green screen background.
    The green background will later be removed via chroma keying and the
    character will be composited onto a ruler reference image.

    WORKFLOW:
    1. Model generates full-body character on provided green background
    2. Green background is removed via chroma keying (background removal)
    3. Character is scaled to match height_cm
    4. Character is composited onto ruler reference image

    OUTPUT: Full-body character on bright green background
    - Character must be FULL BODY (head to toe visible)
    - Character should fill most of the vertical space
    - Top of head near top of image, feet near bottom
    - Background must remain SOLID BRIGHT GREEN (#00FF00) - do not modify it
    - Portrait orientation
    """
    return f"""Put this character in this green screen background. The character must be full body, head to toe visible, The character must fill the vertical space (head near top, feet near bottom."""


# ==============================================================================
# LOCATION GENERATION PROMPTS
# ==============================================================================

def get_location_generation_prompt(
    location_name: str,
    art_style: str,
    text_prompt: str = None,
    is_from_photo: bool = False
) -> str:
    """
    Prompt for generating location/background images

    TEXT INPUTS (via parameters):
    - location_name: Name of the location (e.g., "Mystic Forest", "Coffee Shop")
    - art_style: Visual style (e.g., "Manga", "Fantasy Art", "Sci-Fi")
    - text_prompt: Optional description of location details
    - is_from_photo: True if transforming from a real photo

    IMAGE INPUTS (passed to model separately):
    - [Optional] Photo of real location/scenery (if is_from_photo=True)

    USAGE SCENARIOS:
    1. Text only: text_prompt only → Generate from description
    2. Photo transform: photo image + text_prompt → Transform photo to comic style

    OUTPUT: Landscape-oriented background scene (16:9 ratio)
    - No characters or people
    - Suitable for placing characters in foreground
    - Professional comic book background
    """
    prompt_parts = [
        f"Generate a comic book background scene: {location_name} in {art_style} style."
    ]

    if text_prompt:
        prompt_parts.append(f"\nLocation Description: {text_prompt}")

    if is_from_photo:
        prompt_parts.append("\nTransform real scenery into comic art style, maintaining layout and key features.")

    prompt_parts.extend([
        "\nRequirements:",
        "- Landscape orientation",
        "- Clean, professional comic book background",
        "- Suitable for placing characters in the foreground",
        "- Detailed environment with depth and atmosphere",
        "- NO characters or people in the scene",
        "- NO speech bubbles or text",
        "- High quality comic book illustration",
        "- Consistent with the art style"
    ])

    return "\n".join(prompt_parts)


# ==============================================================================
# PANEL GENERATION PROMPTS
# ==============================================================================

def get_panel_generation_prompt(
    scene_prompt: str,
    character_count: int,
    has_location: bool,
    feedback_history: list = None
) -> str:
    """
    Prompt for generating complete comic panels

    TEXT INPUTS (via parameters):
    - scene_prompt: Description of the scene/action (10-500 characters)
    - character_count: Number of characters (0-7)
    - has_location: True if location background is provided
    - feedback_history: Optional list of previous iteration feedback from critic

    NOTE: Aspect ratio is now controlled via native API ImageConfig, not in text prompt

    IMAGE INPUTS (passed to model separately):
    - [Optional] character_images: 0-7 concatenated character reference images
      * These are the internal reference sheets (with ruler and name)
      * Concatenated horizontally into one image
      * Shows character heights and names for accurate placement
    - [Optional] location_image: Background location image
      * Landscape-oriented background scene
      * Characters will be placed in foreground

    USAGE SCENARIOS:
    1. Text only: scene_prompt only → Generate scene from description
    2. With characters: character_images + scene_prompt → Place characters in scene
    3. With location: location_image + scene_prompt → Use background
    4. Full panel: character_images + location_image + scene_prompt → Complete panel
    5. With feedback: Any above + feedback_history → Improve based on critic

    GENERATOR-CRITIC LOOP:
    This prompt is used iteratively. After each generation:
    1. Critic evaluates the panel
    2. If not acceptable, adds feedback to feedback_history
    3. Generator tries again with feedback
    4. Repeat up to max_iterations (usually 5)

    OUTPUT: Complete comic panel with:
    - Scene matching description
    - Characters positioned correctly (if provided)
    - Background integrated (if provided)
    - Professional quality
    - No text or speech bubbles
    """


    prompt_parts = [
        "Generate a comic panel image with the following description: ",
        f"\n{scene_prompt}",
        "\nStyle guidelines:",
        "- Comic book art style",
        "- Bold, clear lineart",
        "- Vibrant colors",
        "- Dynamic composition",
        "- Professional comic book quality",
        "- Clear visual storytelling",
        "\nUse the provided reference images for character/location consistency where applicable."
    ]

    # Add location guidance
    if has_location:
        prompt_parts.append(
            "\n\nUse the location image provided as the background"
        )

    # Add previous feedback if any
    if feedback_history:
        prompt_parts.append("\n\nPrevious Feedback (address these issues):")
        for fb in feedback_history:
            prompt_parts.append(f"- Iteration {fb['iteration']}: {fb['feedback']}")

    # Add quality requirements
    prompt_parts.append(
        "\n\nQuality Requirements:"
        "\n- Follow the scene description accurately"
        "\n- Proper composition and character placement"
        "\n- Maintain consistent art style across all elements"
        "\n- Clear visual storytelling"
        "\n- Professional polish and finish"
        "\n- No text or speech bubbles (will be added later)"
        "\n- Appropriate lighting and atmosphere"
    )

    return "\n".join(prompt_parts)


def get_panel_critique_prompt(scene_prompt: str) -> str:
    """
    Prompt for critiquing generated panels

    TEXT INPUTS (via parameters):
    - scene_prompt: The original scene description that was requested

    IMAGE INPUTS (passed to model separately):
    - [Required] panel_image: The generated panel to evaluate

    USAGE:
    This prompt is used by the CRITIC in the generator-critic loop.
    After the generator creates a panel, the critic:
    1. Receives this prompt
    2. Receives the generated panel image
    3. Evaluates quality on 6 criteria
    4. Returns ACCEPTABLE: YES/NO and specific FEEDBACK

    EVALUATION CRITERIA:
    1. Scene accuracy - Does it match the description?
    2. Composition - Is it clear and effective?
    3. Character placement - Are characters positioned correctly?
    4. Background quality - Is the location appropriate?
    5. Visual quality - Any artifacts or issues?
    6. Professional polish - Publication ready?

    OUTPUT FORMAT (strict):
    ACCEPTABLE: [YES or NO]
    FEEDBACK: [Specific issues if NO, "Approved." if YES]

    The feedback is added to feedback_history and sent back to generator
    for the next iteration.
    """
    return f"""You are an expert comic book editor. Analyze this panel and determine if it is acceptable for publication.

Scene Requirements: {scene_prompt}

Evaluate the panel on these criteria:
1. Does it accurately depict the scene description?
2. Is the composition clear and effective?
3. Are characters (if any) properly placed and recognizable?
4. Is the background/location appropriate?
5. Are there any visual artifacts or quality issues?
6. Is the overall quality professional?

Respond in this EXACT format:
ACCEPTABLE: [YES or NO]
FEEDBACK: [If NO, provide specific issues to fix. If YES, say "Approved."]

Be strict but fair. Only approve panels that are truly publication-ready."""


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_aspect_ratio_dimensions(aspect_ratio: str) -> tuple:
    """
    Convert aspect ratio to pixel dimensions

    Returns: (width, height) in pixels
    """
    aspect_ratios = {
        "3:4": (1024, 1365),    # Portrait (character focus)
        "4:3": (1365, 1024),    # Landscape
        "16:9": (1792, 1008),   # Wide landscape
        "9:16": (1008, 1792),   # Tall portrait
        "1:1": (1024, 1024),    # Square
    }

    return aspect_ratios.get(aspect_ratio, (1024, 1365))


# ==============================================================================
# PROMPT METADATA
# ==============================================================================

PROMPT_METADATA = {
    "version": "1.0.0",
    "last_updated": "2025-10-23",
    "model": "gemini-2.5-flash-image",
    "notes": [
        "All prompts optimized for Gemini 2.5 Flash Image model",
        "Prompts focus on comic book art generation",
        "Supports multiple art styles and customization",
        "Includes character reference sheet generation",
        "Panel generation supports 0-7 characters",
        "Critic loop ensures quality control"
    ]
}
