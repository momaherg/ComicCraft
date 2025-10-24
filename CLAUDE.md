# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ComicCraft AI is a Python-based AI comic generation system that creates comic book elements (characters, locations, and complete panels) using Google's Gemini models. The project generates professional-quality comic assets with an iterative quality control system for panel composition.

## Environment Setup

### Virtual Environment
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in project root:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Note: Legacy code references `OPENAI_API_KEY` but the system now exclusively uses Gemini models.

### Output Directories
The system auto-creates these directories:
- `outputs/characters/` - Generated character images
- `outputs/locations/` - Generated location/background images
- `outputs/panels/` - Generated comic panels
- `outputs/debug/` - Debug logs with timestamped JSON files

## Running Tests

```bash
# Test character generation (text, photo, comic image inputs)
python examples/test_character_generation.py

# Test location generation (text and photo inputs)
python examples/test_location_generation.py

# Test panel generation (combines characters + location + scene description)
python examples/test_panel_generation.py

# Quick start example
python examples/quick_start.py
```

All test scripts are interactive and will prompt for optional file uploads.

## Architecture

### Three-Stage Generation Pipeline

#### 1. Character Generation (`src/generations/character_gen.py`)
- **Model**: `gemini-2.5-flash-image`
- **Two-step process**:
  1. **Initial Design** (portrait 3:4): Generate or use existing comic character
  2. **Internal Reference** (portrait 3:4): Add height ruler and name label
- **Critical "Skip Generation" Feature**:
  - If ONLY `comic_image_path` is provided (no text_prompt or photo_path), skips step 1 entirely
  - Directly creates internal reference with ruler
  - Saves 50% API calls and time when reusing existing character designs
  - See `docs/technical/skip-generation.md` for details

#### 2. Location Generation (`src/generations/location_gen.py`)
- **Model**: `gemini-2.5-flash-image`
- **Single-step process**: Generate landscape background (16:9)
- **No characters allowed** in location images (explicitly filtered)
- Can transform from photo or generate from text

#### 3. Panel Generation (`src/generations/panel_gen.py`)
- **Generator Model**: `gemini-2.5-flash-image`
- **Critic Model**: `gemini-2.0-flash-exp`
- **Generator-Critic Feedback Loop** (max 5 iterations):
  1. Generator creates panel from scene prompt + character references + location
  2. Critic evaluates quality against 6 criteria (scene accuracy, composition, character placement, background, visual quality, professional polish)
  3. If not acceptable, critic provides specific feedback
  4. Feedback added to history and passed to next iteration
  5. Loop continues until acceptable or max iterations reached
- **Input Preparation**: Character reference images are concatenated horizontally before generation
- **Aspect Ratio**: Controlled via native API `ImageConfig`, not text prompts

### Centralized Prompts System

**ALL generation prompts are centralized in `src/generations/prompts.py`**. This file contains:
- Detailed documentation of text inputs (function parameters) vs image inputs (passed to model separately)
- Complete image flow diagrams showing how images move through the pipeline
- 5 main prompt functions:
  - `get_character_generation_prompt()` - Initial character design
  - `get_character_internal_prompt()` - Character + ruler reference
  - `get_location_generation_prompt()` - Background scenes
  - `get_panel_generation_prompt()` - Complete panel composition with feedback history
  - `get_panel_critique_prompt()` - Quality evaluation

**To modify generation behavior, edit prompts in this single file rather than scattered across modules.**

### Utilities (`src/generations/utils.py`)

Key functions:
- `save_debug_info()` - Timestamped JSON debug logs for every generation step
- `save_image()` - Image persistence with path tracking
- `concatenate_character_images()` - Horizontal stacking of character references for panel generation
- `get_ruler_image_path()` - Locates `ruler_image.png` in project root (critical for character height scaling)
- `get_generation_metadata()` - Standardized metadata structure

### Image Naming Convention

All generated images follow this pattern:
```
{name}_{timestamp}_{type}.png
```
- Characters: `Luna_20251023_193721_initial.png`, `Luna_20251023_193721_internal.png`
- Locations: `Forest_20251023_193733.png`
- Panels: `panel_20251023_193742_iter1.png`
- Debug: `{type}_{step}_{timestamp}.json`

## Key Technical Details

### Height Ruler System
- Character height is enforced using `ruler_image.png` (project root)
- Internal character images include this ruler to ensure consistent scaling in panels
- Heights are specified in centimeters (common values: 90, 130, 180)
- The AI model composites the character against the ruler to match the specified height

### Aspect Ratios
- **Characters**: 3:4 portrait (focus on character design)
- **Locations**: 16:9 landscape (wide backgrounds)
- **Panels**: Configurable (default 3:4), controlled via `ImageConfig` API parameter
- Aspect ratio dimensions defined in `prompts.py::get_aspect_ratio_dimensions()`

### API Models Currently Used
- **Gemini 2.5 Flash Image** (`gemini-2.5-flash-image`): All image generation (characters, locations, panels)
- **Gemini 2.0 Flash Exp** (`gemini-2.0-flash-exp`): Panel critique/evaluation

### Error Handling
All generators handle:
- API timeouts and network errors
- Content policy violations
- Invalid input formats
- Failed generations automatically refund credits (app layer)

Debug information is saved to `outputs/debug/` for all errors with full context.

## Character Generation Input Modes

Three mutually exclusive modes:

1. **Text Description Only**
   ```python
   generate_character(text_prompt="Silver-haired mage...")
   ```

2. **Photo Transformation**
   ```python
   generate_character(photo_path="path.jpg", text_prompt="Transform to superhero")
   ```

3. **Comic Image** (two sub-modes)
   - **Skip Generation** (comic_image_path ONLY): Uses existing design directly, only adds ruler
   - **Transform Comic** (comic_image_path + text_prompt): Modifies existing comic character

## Panel Composition

Characters are referenced by name in scene prompts:
```python
scene_prompt="Sarah talking to John in the foreground, Mike looking surprised in background"
```
- No manual positioning controls - fully AI-driven composition
- Scene prompt (10-500 chars) describes action, composition, and character interactions
- System automatically uses character names from internal reference images
- Supports 0-7 characters per panel

## Product Context

This codebase is the **backend generation engine** for a mobile comic creation app. User stories are in `docs/product/user-stories.md` showing:
- Credit-based monetization (5 credits per generation)
- User asset libraries (characters, locations)
- Multi-panel story projects
- PNG export functionality

The generation functions here are API-ready but do NOT implement:
- Credit system (handled by application layer)
- User authentication
- Asset management/storage
- Multi-panel layout

## Debug and Development

### Debug Logs
Every generation step writes JSON to `outputs/debug/` with timestamp:
- Request parameters
- API responses
- Intermediate steps
- Iteration feedback (for panels)

Example: `character_initial_design_request_20251023_193721_573475.json`

### Typical Generation Times
- Characters: 15-45 seconds (both steps combined)
- Characters (skip mode): ~20 seconds (internal reference only)
- Locations: 20-50 seconds
- Panels: 30-90 seconds per iteration (usually 1-3 iterations)

### Important Files
- `ruler_image.png` (project root) - Height reference for character scaling
- `.env` - API keys (not in git)
- `docs/technical/ai-generations.md` - Generation requirements and flow
- `docs/technical/skip-generation.md` - Skip generation feature documentation

## Common Patterns

### Adding New Prompts
1. Add prompt function to `src/generations/prompts.py`
2. Document text inputs (parameters) and image inputs (passed to model)
3. Update generation module to call new prompt
4. Add debug logging for the new step

### Modifying Generation Behavior
1. Edit prompt text in `prompts.py` (NOT in generator modules)
2. Test with example scripts
3. Check debug logs in `outputs/debug/`

### Creating New Generators
Follow the existing pattern:
1. Create class with `__init__(self, api_key: str)`
2. Configure Gemini model(s) in constructor
3. Implement main public method (returns dict with paths + metadata)
4. Use helper methods for multi-step processes
5. Call `save_debug_info()` at every significant step
6. Use centralized prompts from `prompts.py`

## Known Limitations

- Panel generation uses Gemini for critique but quality depends on generator capabilities
- No batch generation support (each call generates one asset)
- Style consistency across multiple generations not enforced
- Character reference concatenation is simple horizontal stacking (no sophisticated layout)
