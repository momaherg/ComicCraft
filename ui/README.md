# ComicCraft AI - Testing UI

A Gradio-based web interface for testing all ComicCraft AI generation capabilities.

## Quick Start

```bash
# 1. Ensure virtual environment is activated
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Ensure .env file has GEMINI_API_KEY
# Create .env file with:
# GEMINI_API_KEY=your_api_key_here

# 4. Run the UI
python ui/gradio_app.py
```

## Access

Once running, open your browser to:
- **Local**: http://localhost:7860

## Features

### Tab 1: Character Generation

Test all character generation input modes:

1. **Text Description**
   - Enter character name, height, art style
   - Provide text description
   - Optional: Upload style reference image

2. **Photo Transform**
   - Upload a photo of a real person
   - Provide transformation prompt
   - System converts to comic character

3. **Comic Image (Skip Generation)**
   - Upload existing comic character image
   - System directly adds ruler reference
   - Saves API calls and time

4. **Comic Image + Transform**
   - Upload existing comic character
   - Provide transformation prompt
   - Modifies the character design

**Outputs:**
- Initial character design (3:4 portrait)
- Internal reference with height ruler

---

### Tab 2: Location Generation

Generate comic backgrounds/locations:

1. **Text Description**
   - Enter location name and art style
   - Describe the scene

2. **Photo Transform**
   - Upload a photo of a real location
   - System converts to comic background

**Output:**
- Location image (16:9 landscape, no characters)

---

### Tab 3: Panel Generation

Create complete comic panels:

**Inputs:**
- **Scene Prompt** (10-500 chars): Describe the action and composition
- **Character Images** (0-7): Upload internal character references (with rulers)
- **Location Background** (optional): Upload location image
- **Aspect Ratio**: Choose panel dimensions (3:4, 16:9, etc.)
- **Max Iterations**: Generator-critic feedback loop limit (1-5)

**Output:**
- Final panel image with all elements composed
- Iteration count and status

---

## Workflow Examples

### Example 1: Create Character and Use in Panel

1. Go to **Character Generation** tab
2. Create character "Luna" with text description
3. Download the **internal reference** image (with ruler)
4. Go to **Panel Generation** tab
5. Upload Luna's internal reference
6. Write scene: "Luna standing confidently in magical forest"
7. Generate panel

### Example 2: Build Complete Scene

1. **Character Tab**: Generate 2-3 characters, download internal refs
2. **Location Tab**: Generate background location
3. **Panel Tab**:
   - Upload all character internal references
   - Upload location image
   - Describe interaction scene
   - Generate composite panel

### Example 3: Quick Character Reference from Existing Art

1. **Character Tab**
2. Select "Comic Image (Skip Generation)" mode
3. Upload existing character art
4. System adds ruler without re-generating
5. Use directly in panel

---

## Output Locations

All generated assets are saved to:

```
outputs/
├── characters/
│   └── ui_test/           # Character generations from UI
├── locations/
│   └── ui_test/           # Location generations from UI
├── panels/
│   └── ui_test/           # Panel generations from UI
└── debug/                 # JSON debug logs with timestamps
```

---

## Tips

- **Character Height**: Common values are 90cm (child), 130cm (teen), 180cm (adult)
- **Art Styles**: Manga, American Comic, Webtoon, European BD, Indie
- **Scene Prompts**: Refer to characters by name (auto-extracted from images)
- **Panel Iterations**: Higher = better quality but slower (3 is good default)
- **Debug Logs**: Check `outputs/debug/` for troubleshooting

---

## Error Handling

The UI displays clear error messages for:
- Missing required fields
- Invalid file formats
- API failures
- Content policy violations

All errors are logged to debug files with full context.

---

## Architecture

The UI is a **pure testing layer** that calls the core generation modules:
- `src/generations/character_gen.py` - CharacterGenerator
- `src/generations/location_gen.py` - LocationGenerator
- `src/generations/panel_gen.py` - PanelGenerator

No core generation code is modified or duplicated.

---

## Shutting Down

Press `Ctrl+C` in the terminal to stop the Gradio server.
