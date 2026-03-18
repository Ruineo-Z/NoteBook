# Nano-Banana Principles

This reference distills the source guide into reusable prompt-writing rules.

## Core Posture

- Treat the model like a reasoning-heavy visual director, not a keyword matcher.
- Write a creative brief, not a bag of tags.
- Optimize for usable output, not maximal prompt length.

## Golden Rules

### 1. Edit, Do Not Reroll

If the current result is close, preserve what works and request the smallest meaningful change.

- Good: "Keep the pose, framing, and face exactly the same. Change the lighting to sunset and make the title neon blue."
- Weak: "Generate a new version of the same thing but better."

### 2. Use Natural Language and Full Sentences

Prefer clean, direct sentences over prompt fragments.

- Weak: `sports car, neon, rain, tokyo, cinematic, 4k`
- Better: "Create a cinematic wide shot of a futuristic sports car speeding through a rainy Tokyo street at night, with neon reflections across the wet pavement."

### 3. Be Specific and Descriptive

Vague prompts produce generic images. Specify:

- subject identity
- clothing or appearance
- scene and setting
- lighting
- materials and textures
- mood
- layout and framing

### 4. Provide Context

Say who the image is for or what the image is doing.

- "for a premium cookbook"
- "for a viral social thumbnail"
- "for a university whiteboard lecture"
- "for a polished investor infographic"

Context improves artistic choices without adding noise.

### 5. Lock Critical Constraints

Spell out the parts that must not drift:

- exact text
- character identity
- key wardrobe details
- layout or wireframe structure
- composition or camera angle
- aspect ratio

### 6. Avoid Contradictory Prompting

Do not stack clashing directions like:

- "minimalist but extremely dense"
- "photorealistic anime watercolor"
- "clean luxury ad with chaotic crowded layout"

Choose one clear art direction and one clear composition direction.

## Prompt Anatomy

Most strong prompts include these dimensions:

1. Objective or use case
2. Subject
3. Scene
4. Style
5. Composition
6. Text to render
7. Reference or identity controls
8. Materials and lighting
9. Constraints and preservation rules
10. Output qualities

You do not need every dimension every time, but missing dimensions explain most weak prompts.

## Default Quality Upgrades

When the user is underspecified, add only the helpful defaults:

- state the aspect ratio when composition matters
- require readable text when copy appears in the image
- mention lighting quality, not just "nice lighting"
- mention materials or textures when realism matters
- mention camera distance or framing when layout matters
- mention use case when the image is commercial or editorial

## Decision Rule

Choose the shortest prompt that still fixes ambiguity.

- If the user needs a concept, keep it tight but directional.
- If the user needs execution fidelity, add precise structure and constraints.

## What Not to Do

- Do not dump five unrelated style systems into one prompt.
- Do not invent reference images or source material.
- Do not promise current-data grounding unless the target model supports it.
- Do not leave text rendering ambiguous if the words matter.
