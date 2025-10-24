# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComicCraft AI is a Python-based AI comic generation system that creates characters, locations, and complete comic panels using Google Gemini AI models. This is an experimental implementation focused on core AI generation capabilities.

## Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API keys (create .env file)
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### Running the Application
```bash
# Launch the Gradio testing UI
python ui/gradio_app.py

# Access at http://localhost:7860
```

### Development
```bash
# Run the Python interpreter with correct imports
python3 -c "import sys; sys.path.insert(0, 'experimental_generation_setup'); from generations import CharacterGenerator"
```

## Architecture

### Core Generation Pipeline

The system implements three primary generation workflows:

#### 1. Character Generation (`experimental_generation_setup/generations/character_gen.py`)
- **Input modes**: Photo transformation, comic image reuse, or text description
- **Skip generation mode**: When only `comic_image_path` is provided (no `text_prompt` or `photo_path`), the system skips initial generation and proceeds directly to creating the internal character reference
- **Two-stage process**:
  1. Initial character design (3:4 portrait, unless skipped)
  2. Internal reference creation with green screen workflow:
     - Generate full-body character on green screen background
     - Chroma key to remove green and create transparent PNG
     - Crop to content bounds for accurate height measurement
     - Create compact reference with character name label
     - Scale using standard resolution (10 pixels/cm) for accurate relative heights
- **Model**: Google Gemini 2.5 Flash Image for both stages
- **Output**: Two images - initial design + internal reference (with transparent background and name label)

#### 2. Location Generation (`experimental_generation_setup/generations/location_gen.py`)
- **Input modes**: Photo transformation or text description
- **Single-stage process**: Generates 16:9 landscape comic background
- **Model**: Google Gemini 2.5 Flash Image
- **Output**: Location image (no characters, suitable for foreground composition)

#### 3. Panel Generation (`experimental_generation_setup/generations/panel_gen.py`)
- **Generator-Critic Loop Architecture** (max 5 iterations):
  1. **Input preparation**: Concatenate internal character images horizontally (bottom-aligned)
  2. **Generator**: Creates panel from scene prompt + character lineup + location background
  3. **Critic**: Evaluates quality and provides specific feedback
  4. **Iteration**: Loop continues until acceptable or max iterations reached
- **Models**:
  - Generator: Gemini 2.5 Flash Image (creates panels)
  - Critic: Gemini 2.0 Flash Exp (text-only evaluation)
- **Character handling**: Names are referenced in prompts; relative heights preserved through standardized scaling (10 px/cm)
- **Output**: Final panel image + concatenated character lineup + iteration metadata

### Code Organization

```
experimental_generation_setup/
└── generations/                     # Core generation package
    ├── __init__.py                  # Exports: CharacterGenerator, LocationGenerator, PanelGenerator
    ├── character_gen.py             # Character generation with skip logic
    ├── location_gen.py              # Location generation
    ├── panel_gen.py                 # Panel generation with critic loop
    ├── prompts.py                   # Centralized prompt templates
    ├── utils.py                     # Image processing utilities (concatenation, cropping, debug)
    └── green_screen.py              # Green screen generation for character extraction

ui/
├── gradio_app.py                    # Web testing interface (3 tabs)
└── README.md                        # UI usage instructions

docs/
├── product/
│   └── user-stories.md              # 18 MVP user stories (simplified from 33)
└── technical/
    ├── ai-generations.md            # Technical specifications for each generation type
    └── skip-generation.md           # Documentation on character skip mode
```

**Important**: The UI imports use `from src.generations import ...` but the actual code path is `experimental_generation_setup/generations/`. The UI adds the parent directory to `sys.path` to enable imports.

### Image Processing Utilities (`experimental_generation_setup/generations/utils.py`)

Key utilities that are heavily used:
- `concatenate_character_images()`: Horizontally concatenates character references with bottom alignment (preserves relative heights)
- `remove_green_screen()`: Chroma key implementation for background removal
- `crop_to_content()`: Removes transparent padding for accurate height measurement
- `create_compact_character_reference()`: Creates final character reference with name label and tight-fit width
- `save_debug_info()`: Saves timestamped JSON debug logs to `outputs/debug/`
- `save_image()`: Handles image saving with proper format conversion

### Centralized Prompts (`experimental_generation_setup/generations/prompts.py`)

All AI prompts are defined in this single module:
- `get_character_generation_prompt()`: Initial character design prompt
- `get_character_internal_prompt()`: Full-body character on green screen prompt
- `get_location_generation_prompt()`: Location background prompt
- `get_panel_generation_prompt()`: Panel composition prompt with feedback history
- `get_panel_critique_prompt()`: Critic evaluation instructions

**When modifying AI behavior**: Edit prompts here rather than in the generator classes.

### Output Structure

All generated assets are saved to timestamped files:

```
outputs/
├── characters/           # Character generations
│   └── ui_test/         # UI-generated characters
├── locations/           # Location backgrounds
│   └── ui_test/         # UI-generated locations
├── panels/              # Complete panels
│   └── ui_test/         # UI-generated panels
└── debug/               # JSON debug logs (timestamped)
```

Debug logs include full request parameters, API responses, and workflow metadata for troubleshooting.

## Key Technical Details

### Character Height System
- Characters are generated with specific heights (e.g., 90cm, 130cm, 180cm)
- Internal references use **10 pixels/cm** standard resolution
- Green screen workflow ensures accurate height measurement:
  1. Generate on green screen → 2. Remove background → 3. **Crop to content** → 4. Scale to target height
- When concatenated for panels, relative heights are automatically preserved

### Skip Generation Feature
The character generator has an optimization where if only `comic_image_path` is provided (without `text_prompt` or `photo_path`), it skips the initial generation step and proceeds directly to creating the internal reference. This:
- Saves 50% of API calls and generation time
- Useful for pre-designed characters or batch processing
- See `docs/technical/skip-generation.md` for detailed usage

### Generator-Critic Loop
The panel generation uses a feedback loop (max 5 iterations):
- **Generator** creates the panel based on inputs + previous feedback
- **Critic** evaluates if panel is acceptable or provides specific improvements
- Feedback history accumulates in chat context across iterations
- Loop exits early if panel is approved
- If max iterations reached, returns last generated panel

### Error Handling
All generators handle:
- API timeouts and network errors
- Content policy violations
- Invalid input formats
- Missing required parameters

Failed generations are logged to `outputs/debug/` with full error context. The system is designed to fail gracefully and provide clear error messages.

## Development Notes

### API Keys
- Requires `GEMINI_API_KEY` in `.env` file
- Google Gemini models used:
  - **Gemini 2.5 Flash Image**: Character, location, and panel generation
  - **Gemini 2.0 Flash Exp**: Panel critique (text-only)

### Import Patterns
When importing the generation modules, use:
```python
import sys
sys.path.insert(0, 'experimental_generation_setup')
from generations import CharacterGenerator, LocationGenerator, PanelGenerator
```

Or run from the project root with adjusted paths.

### Testing
The Gradio UI (`ui/gradio_app.py`) provides comprehensive testing:
- **Character Tab**: Test all input modes (text, photo, comic image, skip generation)
- **Location Tab**: Test text and photo transformation
- **Panel Tab**: Test full composition with 0-7 characters + optional location

All outputs are saved to `outputs/*/ui_test/` directories.

### Product Context
- MVP scope: 18 user stories (Phase 1)
- Credit-based system (5 credits per generation)
- Focus: Character/location asset creation → Panel composition → PNG export
- Target users: Comic creators needing AI-assisted generation
- See `docs/product/user-stories.md` for complete requirements

## Important Constraints

1. **Character limit in panels**: 0-7 characters maximum
2. **Prompt length**: 10-500 characters for scene descriptions
3. **Art styles**: 5 preset options (Manga, American Comic, Webtoon, European BD, Indie)
4. **Aspect ratios**: Configurable for panels (3:4, 16:9, 4:3, 1:1, 9:16)
5. **Max iterations**: 5 for generator-critic loop (configurable)

## Common Pitfalls

1. **Import confusion**: Code is in `experimental_generation_setup/generations/` but README examples show `src/generations/`
2. **Comic image transformation**: If you provide both `comic_image_path` and `text_prompt`, it will attempt transformation (not skip generation)
3. **Green screen RGB**: Must use exact RGB(0, 255, 0) for chroma keying to work correctly
4. **Character concatenation**: Uses bottom alignment to preserve relative heights when characters have different heights
5. **Cropping importance**: Must crop to content bounds before scaling to target height, otherwise transparent padding affects height calculations
