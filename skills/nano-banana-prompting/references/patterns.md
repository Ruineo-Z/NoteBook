# Task Patterns

Use these patterns to map the request to the right prompt structure.

## Text Rendering, Infographics, and Visual Synthesis

Use when the image needs readable text, sectioning, charts, labels, or visual explanations.

Include:

- what information to compress or summarize
- visual style, such as editorial, technical, or whiteboard
- exact section names or label text
- readability requirements

Prompt pattern:

```text
Create a clean [style] infographic for [audience/use case]. Summarize [source topic].
Include sections for [section 1], [section 2], and [section 3].
Render the text clearly and legibly. Use [chart or diagram types].
Maintain a [tone] layout with [color or typography direction].
```

## Character Consistency and Viral Thumbnails

Use when a reference character or person must stay recognizable across new situations.

Include:

- what must stay identical
- what expression or action changes
- layout of subject, secondary object, graphics, and title
- exact overlay text if any

Prompt pattern:

```text
Use the person from Image 1 as the exact identity anchor. Keep the face, hair, and key facial features unchanged.
Change only the expression to [emotion] and the pose to [action].
Place the person on the [left/right] side and [secondary subject] on the [left/right] side.
Add [graphic element] and render the text "[exact text]" in a bold, readable [font feel] style.
Use a [background] background with [color/contrast direction].
```

## Search-Grounded or Current-Data Visuals

Use only if the target product supports live grounding or search.

Include:

- what current facts or trends should guide the image
- what should be visualized
- what explanation or labels should appear in the output

Do not imply live data if the target model cannot actually access it.

## Editing, Restoration, Localization, and Seasonal Changes

Use when the user wants to modify an existing image instead of regenerate.

Include:

- what must remain unchanged
- what must change
- how the new content should blend with the original

Prompt pattern:

```text
Keep the original composition, subject identity, and camera angle exactly the same.
Change only [target change].
Match the surrounding lighting, texture, and perspective.
Do not alter [must-keep elements].
```

Good fit for:

- object removal and in-painting
- colorization
- localization
- weather or season changes
- lighting swaps

## 2D to 3D or Layout-to-Render Translation

Use when the input is a floor plan, sketch, schematic, or rough layout.

Include:

- which layout features must remain fixed
- what final style to translate into
- whether the output is a single hero render, a board, or multiple panels

Prompt pattern:

```text
Follow the uploaded layout exactly.
Translate it into a [style] final image for [use case].
Keep the spatial arrangement, panel structure, and placement of major elements fixed.
Render the result with [materials], [lighting], and [quality level].
```

## High-Resolution and Texture-Heavy Scenes

Use when realism, print quality, or material fidelity matters.

Include:

- resolution expectation if the product supports it
- small surface details
- lighting interaction with materials

Prompt pattern:

```text
Create a high-detail [scene type] with visible [texture details].
Emphasize [surface qualities] and [lighting behavior].
The result should feel suitable for [4K wallpaper / print / close-up inspection].
```

## Reasoning, Educational, and Whiteboard Visuals

Use when the image must explain a system or show logical structure.

Include:

- what concept is being explained
- diagram style
- exact labels
- audience level

Prompt pattern:

```text
Explain [concept] as a [whiteboard / technical diagram / classroom visual] for [audience].
Label [important parts] clearly and legibly.
Use a [clean / hand-drawn / technical] style and make the relationships between parts obvious.
```

## Storyboards and Concept Art Sequences

Use when the user wants a multi-image narrative or consistent campaign sequence.

Include:

- number of frames
- continuity requirements
- emotional arc
- output format

Prompt pattern:

```text
Create a [number]-part storyboard featuring [subject].
Keep the character identity, wardrobe, and overall art direction consistent across all frames.
Vary camera angle, distance, and expression to create narrative movement.
End on [desired final beat].
Generate one frame at a time in [aspect ratio].
```

## Structural Control and Layout Guidance

Use when the user has a sketch, grid, wireframe, or strict placement requirement.

Include:

- exact instruction to follow the structure
- what can be stylized freely
- what cannot move

Prompt pattern:

```text
Follow the structure of the attached [sketch / wireframe / grid] exactly.
Do not move the placement of the major blocks.
Replace placeholder content with [desired content] while preserving the original layout logic.
Render it in a [style] style with [quality direction].
```
