---
name: opencode-command-creator
description: Create custom commands for OpenCode TUI.
---

# OpenCode Command Creator

This skill helps you create custom commands for OpenCode TUI.

## When to Use

When you need to create a custom command that can be run with `/command-name` in the OpenCode TUI.

## Quick Start

### Step 1: Create Command File

Create a markdown file in `.opencode/commands/` directory:

```bash
mkdir -p .opencode/commands
touch .opencode/commands/your-command.md
```

### Step 2: Add Frontmatter and Template

Edit the markdown file with the following format:

```markdown
---
description: Brief description of what this command does
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Your prompt here. This will be sent to the LLM when the command runs.
```

The filename `your-command.md` becomes the command name `/your-command`.

## Configuration Options

| Option | Required | Description |
|--------|----------|-------------|
| `description` | Yes | Shown in TUI when typing commands |
| `agent` | No | Agent to use (defaults to current) |
| `model` | No | Override default model |
| `subtask` | No | Force subagent invocation (true/false) |

## Examples

### Example 1: Simple Test Command

`.opencode/commands/test.md`

```markdown
---
description: Run tests with coverage
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

Run the full test suite with coverage report. Show any failures and suggest fixes.
```

Usage: `/test`

### Example 2: Command with Arguments

`.opencode/commands/component.md`

```markdown
---
description: Create a new React component
---

Create a new React component named $ARGUMENTS with TypeScript support.
Include proper typing and basic structure.
```

Usage: `/component Button`

`$ARGUMENTS` will be replaced with `Button`.

### Example 3: Positional Arguments

`.opencode/commands/create-file.md`

```markdown
---
description: Create a new file
---

Create a file named $1 in the $2 directory with the following content:
$3
```

Usage: `/create-file config.json src "{\"key\": \"value\"}"`

Replaces:
- `$1` → `config.json`
- `$2` → `src`
- `$3` → `{"key": "value"}`

### Example 4: Shell Output in Prompt

`.opencode/commands/review-changes.md`

```markdown
---
description: Review recent changes
---

Recent git commits:
!`git log --oneline -10`

Review these changes and suggest improvements.
```

`!`command`` runs the shell command and includes output in the prompt.

### Example 5: Include File Content

`.opencode/commands/review-component.md`

```markdown
---
description: Review a component
---

Review the component in @src/components/Button.tsx.
Check for performance issues and suggest improvements.
```

`@filename` includes the file content in the prompt.

## Command Location (Project-level)

For project-level commands, create files in:

```
.opencode/commands/your-command.md
```

This directory is relative to your project root.

## Workflow

1. Ask user for command name and description
2. Ask if the command needs arguments
3. Create the markdown file in `.opencode/commands/`
4. Add frontmatter with description (and optionally agent/model)
5. Write the prompt template
6. Optionally add special syntax (arguments, shell output, file references)

## Available Agents

- `general` - General purpose agent
- `build` - Build/debug agent
- `plan` - Planning agent
- `explore` - Code exploration agent
