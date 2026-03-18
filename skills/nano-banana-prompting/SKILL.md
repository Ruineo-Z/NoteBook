---
name: nano-banana-prompting
description: Methodology for drafting, diagnosing, and iterating Nano-Banana image prompts. Use when the user wants stronger prompts for generation or editing, especially for infographics, text-heavy images, character consistency, thumbnails, restorations, storyboards, layout-controlled outputs, or when an existing prompt or result needs improvement.
---

# Nano Banana Prompting

## Overview

Turn a visual goal, weak prompt, or disappointing result into a copy-ready Nano-Banana prompt. Default to producing one strong prompt first, then a short rationale and optional variants only when they materially help.

## Workflow

1. Classify the request:
   - `draft` from scratch
   - `rewrite` an existing prompt
   - `iterate` after a weak output
2. Identify the task family. If the request is non-obvious, read [references/patterns.md](references/patterns.md).
3. Fill the prompt dimensions using [references/principles.md](references/principles.md):
   - goal and use case
   - subject
   - scene and background
   - style
   - composition and layout
   - text to render
   - references or identity constraints
   - materials and lighting
   - explicit constraints
   - output format and aspect ratio
4. Write in natural language and full sentences. Avoid tag soup.
5. Run a self-check:
   - Is the prompt specific enough?
   - Are text, layout, identity, and output constraints explicit?
   - Did unnecessary ambiguity get removed?
   - If this is an iteration, did the prompt edit instead of reroll when possible?
6. Return the result using the output contract.

## Modes

### Draft

Use when the user starts from an idea only.

- Make reasonable assumptions for missing non-critical details.
- State assumptions briefly after the prompt.
- Prefer one strong prompt over many average ones.

### Rewrite

Use when the user already has a prompt.

- Diagnose the existing prompt before rewriting.
- Preserve the user's actual goal.
- Upgrade specificity, composition, constraints, and use-case context.

### Iterate

Use when the user describes a bad output or partial success.

- Keep what is already working.
- Change only the failing dimensions.
- Write the next prompt as an edit instruction, not a full reroll, unless the composition is fundamentally wrong.
- Read [references/iteration.md](references/iteration.md) when the failure mode is unclear.

## Output Contract

Default to this shape:

1. `Primary prompt:` one copy-ready prompt
2. `Why this should work:` 2 to 4 short bullets only if helpful
3. `Optional variants:` include only when the user would benefit from alternative directions or tighter controls

For rewrite and iterate tasks, also include:

- `Main issues:` concise diagnosis
- `Revised prompt:` or `Next-round prompt:`

Optimize for useful prompts, not theory dumps.

## Task Family Routing

Read the matching reference only when needed:

- [references/patterns.md](references/patterns.md) for infographics, text rendering, character consistency, thumbnails, edits, restorations, 2D or 3D translation, high-resolution scenes, storyboards, and layout-controlled outputs
- [references/iteration.md](references/iteration.md) for fixing weak outputs and targeted edit prompts
- [references/templates.md](references/templates.md) for reusable scaffolds when the request is underspecified
- [references/principles.md](references/principles.md) for prompt anatomy and the core methods derived from the source guide

## Rules

- Prefer natural language and complete instructions.
- Be concrete about text, layout, identity, and output format.
- Include the reason or use case when it changes artistic choices.
- Use editing language for partial fixes.
- Do not imply live search grounding unless the target product supports it or the user explicitly wants that mode.
- Avoid contradictory style adjectives.
- If you provide variants, vary one axis at a time.

## Common Failure Patterns

- Generic image: add purpose, style, materials, lighting, and composition
- Bad text rendering: specify exact copy, placement, font feel, and readability requirement
- Identity drift: anchor the face, attire, and must-keep traits to the reference
- Layout drift: describe spatial arrangement and explicitly mention what must stay fixed
- Over-editing: state what to keep unchanged
