# Iteration Guide

Use this reference when the user has an unsatisfying result and needs the next prompt, not a full reset.

## Iteration First Principle

When the output is partially correct:

1. Keep the parts that work
2. Name the parts that failed
3. Change the minimum necessary variables
4. Make the next prompt sound like a directed edit

## Diagnose by Symptom

### The Image Feels Generic

Likely missing:

- use case
- art direction
- lighting
- materials
- composition

Repair move:

```text
Turn this into a [specific use case] image. Use a [specific style] direction, [specific lighting], and [specific composition].
```

### The Text Is Wrong or Unreadable

Likely missing:

- exact copy
- placement
- font feel
- readability requirement

Repair move:

```text
Render the exact text "[exact text]" clearly and legibly in a [font feel] style. Place it [location]. Keep the text large and easy to read.
```

### The Face or Character Drifted

Likely missing:

- hard identity lock
- must-keep traits

Repair move:

```text
Keep the face, hairstyle, and defining facial features exactly the same as the reference image. Do not change the identity.
```

### The Layout Drifted

Likely missing:

- fixed placement language
- composition constraints

Repair move:

```text
Keep the composition and spatial arrangement exactly the same. Do not move the subject from the left side or the text block from the center.
```

### The Edit Changed Too Much

Likely missing:

- preservation rules

Repair move:

```text
Keep the original pose, framing, background, and subject identity exactly the same. Change only [single requested change].
```

### The Image Is Detailed but Not the Right Mood

Likely missing:

- mood language
- lighting language
- audience or use-case framing

Repair move:

```text
Keep the scene content the same, but shift the mood to [mood] using [lighting direction], [color direction], and [stylistic tone].
```

## Edit Versus Reroll

Prefer an edit if:

- composition is mostly correct
- identity is mostly correct
- only lighting, text, styling, object presence, or mood is wrong

Prefer a reroll if:

- the core composition is wrong
- the scene concept is wrong
- the image ignored the main brief

## Next-Round Prompt Pattern

```text
Keep [working elements] exactly the same.
Change only [failing elements].
Preserve [critical constraints].
Render the update with [new style or lighting details].
Do not change [must-keep items].
```

## Practical Rule

If you can name the change in one sentence, iterate.
If you need to redefine the whole image concept, reroll.
