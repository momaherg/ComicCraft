# ComicCraft AI - Generation Functions

Python implementation of AI-powered comic generation functions for the ComicCraft AI project.

## Overview

This repository contains the core AI generation logic for creating comic book elements:

- **Character Generation**: Create comic characters from photos, comic images, or text descriptions
- **Location Generation**: Generate comic backgrounds from photos or text descriptions
- **Panel Generation**: Compose complete comic panels with characters and locations using a generator-critic feedback loop

## Project Structure

```
comicare/
├── docs/
│   ├── product/
│   │   └── user-stories.md          # Product requirements
│   └── technical/
│       ├── ai-generations.md        # Technical specifications
│       └── skip-generation.md       # Skip generation feature docs
├── experimental_generation_setup/
│   └── generations/
│       ├── __init__.py              # Package initialization
│       ├── character_gen.py         # Character generation
│       ├── location_gen.py          # Location generation
│       ├── panel_gen.py             # Panel generation with critic loop
│       ├── prompts.py               # Centralized prompt templates
│       ├── utils.py                 # Image processing utilities
│       └── green_screen.py          # Green screen generation
├── ui/
│   ├── gradio_app.py                # Web testing interface
│   └── README.md                    # UI usage instructions
├── outputs/
│   ├── characters/                  # Generated character images
│   ├── locations/                   # Generated location images
│   ├── panels/                      # Generated comic panels
│   └── debug/                       # Debug logs and intermediate files
├── .env                             # API keys (not in git)
├── requirements.txt                 # Python dependencies
├── CLAUDE.md                        # Guide for Claude Code
└── README.md                        # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 3. Create Output Directories

The scripts will create these automatically, but you can pre-create them:

```bash
mkdir -p outputs/{characters,locations,panels,debug}
```

## Usage

### Character Generation

```python
import sys
sys.path.insert(0, 'experimental_generation_setup')
from generations import CharacterGenerator

generator = CharacterGenerator(api_key="your_gemini_api_key")

# From text description
result = generator.generate_character(
    character_name="Luna",
    height_cm=130,
    art_style="Manga",
    text_prompt="A young girl with silver hair and purple eyes, magical girl outfit"
)

# From photo
result = generator.generate_character(
    character_name="Alex",
    height_cm=180,
    art_style="American Comic",
    photo_path="path/to/photo.jpg"
)

# From comic image
result = generator.generate_character(
    character_name="Shadow",
    height_cm=180,
    art_style="Dark Comic",
    comic_image_path="path/to/comic.jpg"
)
```

**Outputs:**
- `character_image_path`: Initial character design
- `internal_character_image_path`: Character with height ruler (for panel generation)
- `metadata`: Character information

### Location Generation

```python
import sys
sys.path.insert(0, 'experimental_generation_setup')
from generations import LocationGenerator

generator = LocationGenerator(api_key="your_gemini_api_key")

# From text description
result = generator.generate_location(
    location_name="Mystic_Forest",
    art_style="Fantasy Art",
    text_prompt="A magical forest with glowing mushrooms and ancient trees"
)

# From photo
result = generator.generate_location(
    location_name="Coffee_Shop",
    art_style="Comic Book",
    photo_path="path/to/photo.jpg"
)
```

**Outputs:**
- `location_image_path`: Generated location image
- `metadata`: Location information

### Panel Generation

```python
import sys
sys.path.insert(0, 'experimental_generation_setup')
from generations import PanelGenerator

generator = PanelGenerator(api_key="your_gemini_api_key")

result = generator.generate_panel(
    scene_prompt="Two characters talking in a coffee shop, friendly conversation",
    character_images=["path/to/char1_internal.png", "path/to/char2_internal.png"],
    location_image="path/to/location.png",
    aspect_ratio="3:4",
    max_iterations=5
)
```

**Outputs:**
- `panel_image_path`: Final generated panel
- `iterations`: Number of generator-critic iterations used
- `metadata`: Panel information

## Testing

### Run the Gradio UI

```bash
# Launch web testing interface
python ui/gradio_app.py

# Access at http://localhost:7860
```

The Gradio UI provides comprehensive testing for:
- Character generation (all input modes)
- Location generation
- Panel generation with multiple characters and locations

See `ui/README.md` for detailed usage instructions.

## Technical Details

### Character Generation Pipeline

1. **Initial Design** (Gemini 2.5 Flash Image) - **Can be skipped**
   - Input: Photo, comic image, or text + art style
   - Output: Character design in portrait orientation (3:4)
   - Skip mode: If only comic_image_path provided, skips to step 2

2. **Internal Character Image** (Gemini 2.5 Flash Image)
   - Green screen workflow:
     1. Generate full-body character on green screen
     2. Chroma key to remove background
     3. Crop to content bounds (accurate height)
     4. Create compact reference with name label
   - Output: Character with transparent background, scaled to exact height (10 px/cm)
   - Used for: Reference in panel generation

### Location Generation Pipeline

1. **Location Image** (Gemini 2.5 Flash Image)
   - Input: Photo or text + art style
   - Output: Comic background in landscape orientation (16:9)
   - Features: No characters, suitable for foreground composition

### Panel Generation Pipeline

1. **Input Preparation**
   - Concatenate character internal references horizontally (bottom-aligned)
   - Load location background

2. **Generator-Critic Loop** (max 5 iterations)
   - Generator (Gemini 2.5 Flash Image) creates panel based on prompt + assets
   - Critic (Gemini 2.0 Flash Exp) evaluates quality and provides feedback
   - Loop continues until acceptable or max iterations reached

3. **Output**
   - Final panel image
   - Concatenated character lineup
   - Iteration count and feedback history

### Debug Information

All generation steps save debug information to `outputs/debug/`:
- Request parameters
- API responses
- Intermediate images
- Critic feedback

JSON files are timestamped for easy tracking.

## Art Styles

Supported art styles (customizable):
- Manga
- American Comic
- European Comic
- Fantasy Art
- Sci-Fi
- Watercolor
- Realistic
- Dark Comic
- Custom (with style reference image)

## Limitations & Notes

1. **Image Generation**: Uses Google Gemini models exclusively:
   - Gemini 2.5 Flash Image: Character, location, and panel generation
   - Gemini 2.0 Flash Exp: Panel critique (text-only)

2. **API Costs**:
   - Gemini 2.5 Flash Image: Check Google AI pricing
   - Gemini 2.0 Flash Exp: Free tier available

3. **Generation Times**:
   - Characters: 15-45 seconds (with skip mode: ~20 seconds)
   - Locations: 20-50 seconds
   - Panels: 30-90 seconds per iteration (up to 5 iterations)

4. **Credit System**: Not implemented in these functions (handled by application layer)

5. **Character Limits**: Maximum 7 characters per panel for optimal composition

## Error Handling

All generators handle common errors:
- API timeouts
- Content policy violations
- Network errors
- Invalid input formats

Failed generations are logged to debug directory with error details.

## Future Enhancements

- [ ] Batch generation support
- [ ] Style consistency across multiple generations
- [ ] Character pose library
- [ ] Panel layout templates
- [ ] Advanced composition controls
- [ ] Multi-panel story generation
- [ ] Export to comic book formats (CBZ, PDF)

## Contributing

When adding new features:
1. Follow the existing code structure
2. Add comprehensive debug logging
3. Include example usage in test scripts
4. Update this README

## License

See LICENSE file for details.

## Support

For issues or questions:
- Check the debug logs in `outputs/debug/`
- Review the technical documentation in `docs/technical/`
- Open an issue with error logs and generation parameters

