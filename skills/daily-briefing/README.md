# Daily Briefing Skill

Automates the daily workflow of collecting AI news from YouTube and RSS feeds and processing them into Google NotebookLM for insights.

## Features

- **Multi-Source Collection**: Triggers `youtube-tracker` and `rss-fetcher` to find new content.
- **Smart Filtering**: Aggregates updates from the last N hours (default: 24h).
- **Automated Processing**: Feeds URLs directly into NotebookLM.
- **Insight Generation**: Triggers Mind Map or Audio Overview generation.

## Usage

```bash
/daily-briefing [hours]
```

Example: `/daily-briefing 48` to process the last 2 days of news.
