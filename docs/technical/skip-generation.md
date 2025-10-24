# Skip Character Generation Feature

## Overview

When you already have a ready comic character image, you can skip the generation step and jump directly to creating the internal character reference with the ruler.

## How It Works

### Automatic Detection

The system automatically detects when to skip generation based on inputs:

```python
skip_generation = (
    comic_image_path is not None and
    photo_path is None and
    text_prompt is None
)
```

### Three Scenarios

#### 1. **Ready Comic Character** (Skips Generation)
```python
gen.generate_character(
    character_name="Luna",
    height_cm=130,
    art_style="Manga",  # Ignored when skipping
    comic_image_path="path/to/ready_character.png"
)
```
**Result:** Uses existing image directly, only creates internal reference with ruler

#### 2. **Transform Comic Image** (Generates)
```python
gen.generate_character(
    character_name="Luna",
    height_cm=130,
    art_style="Manga",
    comic_image_path="path/to/existing.png",
    text_prompt="Make her wear a wizard hat"  # Additional transformation
)
```
**Result:** Transforms the comic image according to text_prompt

#### 3. **Generate From Scratch** (Generates)
```python
gen.generate_character(
    character_name="Luna",
    height_cm=130,
    art_style="Manga",
    text_prompt="Young girl with silver hair"
)
```
**Result:** Generates new character from text description

## Benefits

### Time Savings
- **Without Skip**: ~40 seconds (20s generation + 20s internal)
- **With Skip**: ~20 seconds (only internal reference)
- **Savings**: 50% faster!

### Cost Savings
- **Without Skip**: 2 API calls (generation + internal)
- **With Skip**: 1 API call (only internal)
- **Savings**: 50% fewer API calls!

### Use Cases

1. **Pre-designed Characters**
   - You hired an artist to create character designs
   - You have existing character art from another project
   - You want to reuse characters across multiple comics

2. **Batch Processing**
   - Generate initial designs separately
   - Create internal references in bulk
   - Separate design approval from technical processing

3. **Testing & Development**
   - Quickly test panel generation with existing characters
   - Iterate on ruler positioning without regenerating
   - Debug internal reference creation

## Example Workflow

### Step 1: Generate Initial Character (Once)
```python
from src.generations import CharacterGenerator

gen = CharacterGenerator(api_key)

# Generate the initial design
result = gen.generate_character(
    character_name="Hero",
    height_cm=180,
    art_style="American Comic",
    text_prompt="Muscular superhero with red cape"
)

character_image = result['character_image_path']
# Save this path for reuse!
```

### Step 2: Create Multiple Internal References (Fast)
```python
# Different height for same character
result_tall = gen.generate_character(
    character_name="Hero_Tall",
    height_cm=200,  # Taller version
    art_style="N/A",  # Ignored
    comic_image_path=character_image  # Reuse same design!
)

result_short = gen.generate_character(
    character_name="Hero_Short",
    height_cm=160,  # Shorter version
    art_style="N/A",
    comic_image_path=character_image
)
```

## Debug Logs

When generation is skipped, check debug logs:

```json
{
  "character_name": "Luna",
  "comic_image_path": "path/to/ready.png",
  "skipped_generation": true
}
```

Metadata will include:
```json
{
  "type": "character",
  "skipped_generation": true,
  "character_image": "path/to/ready.png",
  "internal_image": "path/to/internal.png"
}
```

## Console Output

### With Skip:
```
============================================================
GENERATING CHARACTER: Luna
============================================================

[STEP 1] Using existing comic character image (skipping generation)...
  Using image: ready_character.png

[STEP 2] Generating internal character image with ruler...
  Calling Gemini 2.5 Flash Image for internal character image...
...
```

### Without Skip:
```
============================================================
GENERATING CHARACTER: Luna
============================================================

[STEP 1] Generating initial character design...
  Calling Gemini 2.5 Flash Image for character generation...
...

[STEP 2] Generating internal character image with ruler...
  Calling Gemini 2.5 Flash Image for internal character image...
...
```

## Testing

Run the test script to verify:
```bash
.venv/bin/python test_skip_generation.py
```

Expected output:
```
✅ SUCCESS: Generation was skipped as expected!
```

## API Reference

```python
CharacterGenerator.generate_character(
    character_name: str,           # Required
    height_cm: int,                # Required (90-200)
    art_style: str,                # Ignored if skipping
    photo_path: str = None,        # Don't provide if skipping
    comic_image_path: str = None,  # Provide ONLY this to skip
    text_prompt: str = None,       # Don't provide if skipping
    style_ref_image_path: str = None,
    output_dir: str = "outputs/characters"
) -> dict
```

## Best Practices

### ✅ DO:
- Use skip when you have final character designs
- Save generated character images for reuse
- Create multiple internal references from one design
- Test with existing images before generating new ones

### ❌ DON'T:
- Provide text_prompt when you want to skip (will transform instead)
- Provide photo_path when you want to skip (will transform instead)
- Skip if you need to modify the character design
- Use low-quality input images (min 512x512 recommended)

## Troubleshooting

**Q: Generation didn't skip even though I provided comic_image_path?**
A: Make sure photo_path and text_prompt are both None/not provided

**Q: Can I change the art style when skipping?**
A: No, the art_style parameter is ignored when skipping. Use the original design as-is.

**Q: Can I skip for photo_path too?**
A: No, photos always need to be transformed into comic style first.

**Q: What if my comic image isn't the right size?**
A: The system will use it as-is. Make sure it's good quality (min 512x512).

---

**Last Updated:** 2025-10-23
**Feature Status:** ✅ Implemented & Tested
