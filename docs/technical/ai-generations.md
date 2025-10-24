# AI Generation Requirements

## Generation Types Checklist

### ☐ 1. Character Generation

**Inputs:**
- [ ] Photo (optional) - image file of real person
- [ ] Comic character image (optional) - image file of existing illustrated/comic character
- [ ] Text prompt for the character (optional)
- [ ] Character name
- [ ] Art style selection - from 5 preset options "Textual"
- [ ] inspiring image for the style (style ref image) - (optional)
- [ ] Height of character from preset options (e.g., 90 cm, 130 cm, 180 cm)

**Outputs:**
- [ ] Character image - [specify format, resolution, aspect ratio]
- [ ] Character metadata - [name, creation date, etc.]

**Steps**
- Given the inputs generate an initial character design using (gpt-5) instructing the model to follow the same style in the style ref image if provided, in a portrait aspect ratio.
  - If photo provided: Transform real person to comic style
  - If comic character image provided: skip to the next step and generate internal character image from existing illustrated character
  - If text prompt: Generate character from description
- Given the generated character, its name and the predefined ruler placeholder image labeled (e.g., 90 cm, 130 cm, ...), the model api generate a new ruler image (internal character image) with the character in it with the right height and transparent background, and the name of the character below it.
- The internal character image is later used in panel generations


---

### ☐ 2. Location Generation

**Inputs:**
- [ ] Photo (optional) - image file
- [ ] Text prompt for the location (optional)
- [ ] Location name
- [ ] Art style selection - from 5 preset options

**Outputs:**
- [ ] Location image - [specify format, resolution, aspect ratio]
- [ ] Location metadata - [name, creation date, etc.]

**Steps**
- Given the inputs generate an initial location design using (gpt-5)
- The location image is later used in panel generations


---

### ☐ 3. Panel Generation

**Inputs:**
- [ ] Location (optional) - reference to saved location asset
- [ ] Characters (0-7) - references to saved character assets with names
- [ ] Text prompt - 10-500 chars describing scene, action, composition
  - Can reference characters by name (e.g., "Sarah talking to John")
- [ ] aspect ratio.


**Outputs:**
- [ ] Panel image - [specify format, resolution, aspect ratio]
- [ ] Panel metadata - [characters used, location used, prompt, creation date]

**Steps**
- input preparation:
   - concatinate all the internal character images to one landscape image, it include their height and there names.
- generation loop (max 5 times)
   1. Given the inputs generate an initial panel design using the generator (nano banana).
   2. Given the generated image, we give it to the critic (nano banana) to criticize it, check if it is acceptable, follows the prompt, doesn't have any weird thing in it, if ok break, if not return to step one with the feedback added to the chat history with the generator, 
- The generated panel is returned.



---

## Technical Implementation Notes

### Image Specifications
- **Format:** _[PNG]_
- **Aspect Ratio:** _[e.g., 1:1, 3:4, 16:9, etc.]_

### AI Model Requirements
- **Provider:** _[e.g., nano banana (models/gemini-2.5-flash-image), gpt-5]_



### Error Handling
- [ ] Generation timeout
- [ ] Content policy violation
- [ ] API/network errors, request per minute limit exceeded.
