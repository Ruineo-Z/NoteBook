# YouTube Tracker Skill

## Overview
This skill allows users to track specific YouTube channels and check for new video uploads directly from the command line. It uses a local JSON configuration to store channel details and fetches updates via YouTube's RSS feeds. This eliminates the need for a complex YouTube API setup for simple tracking needs.

## Workflow
1.  **Manage Channels**: Users build their tracking list by adding channel URLs. The system automatically extracts the Channel ID.
2.  **Check Updates**: The user requests an update check (e.g., "What's new today?").
3.  **Fetch & Parse**: The system fetches RSS feeds for all tracked channels and filters videos based on the publication time.
4.  **Display**: New videos are presented to the user with titles, links, and publication timestamps.

## Usage

### Commands

#### Add Channel
Add a new YouTube channel to your tracking list.
```bash
/yt-add <url> [--name "Custom Name"]
```
**Examples:**
- `/yt-add https://www.youtube.com/@JeffSu`
- `/yt-add https://www.youtube.com/@OpenAI --name "OpenAI Official"`

#### List Channels
List all currently tracked channels and their IDs.
```bash
/yt-list
```

#### Remove Channel
Remove a channel from the tracking list using its URL or ID.
```bash
/yt-remove <url_or_id>
```

#### Check Updates
Check for new videos published within the last N hours.
```bash
/yt-check [hours]
```
**Examples:**
- `/yt-check` (defaults to last 24 hours)
- `/yt-check 48` (last 2 days)
- `/yt-check --json` (output raw JSON)

### Dependencies
- Python 3.x
- `curl` (used for making network requests to avoid some blocking issues)

## Constraints
- **Network**: Requires an active internet connection to fetch RSS feeds.
- **Platform**: Relies on `curl` and `subprocess`, so it works best in Unix-like environments (Linux/macOS).
- **Latency**: YouTube RSS feeds are generally up-to-date but might have a slight delay compared to the web interface.
- **Storage**: Channel list is stored locally in `config/channels.json`.
