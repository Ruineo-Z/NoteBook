# YouTube Tracker Skill

A lightweight skill to track new videos from your favorite YouTube channels directly from the command line.

## Features

- **Channel Management**: Easily add, remove, and list YouTube channels.
- **Update Checking**: Check for new videos published within a specific time window (e.g., last 24 hours).
- **RSS Integration**: Uses YouTube's native RSS feeds for reliable update detection without API keys.
- **JSON Support**: Option to output results in JSON format for integration with other tools.

## Structure

- `config/`: Stores the `channels.json` configuration file.
- `scripts/`: Contains Python scripts for logic (`manage_channels.py`, `check_updates.py`).
- `SKILL.md`: Detailed documentation and usage guide.
