# YouTube Tracker Skill

Track new videos from your favorite YouTube channels directly from the command line.

## Configuration

Channels are stored in `skills/youtube-tracker/config/channels.json`.

## Commands

### Add Channel
Add a YouTube channel to your tracking list.
Usage: `/yt-add <url>`

Example:
`/yt-add https://www.youtube.com/@JeffSu`

### List Channels
List all currently tracked channels.
Usage: `/yt-list`

### Check Updates
Check for new videos published in the last 24 hours (or specified duration).
Usage: `/yt-check [hours]`

Example:
`/yt-check` (defaults to 24h)
`/yt-check 48` (last 48h)

## Scripts

- `scripts/manage_channels.py`: Python script to manage the channels list.
- `scripts/check_updates.py`: Python script to fetch RSS feeds and identify new videos.
