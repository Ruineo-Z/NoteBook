# RSS Fetcher Skill

## Overview
This skill fetches and filters RSS feeds to track updates from configured sources. It allows checking for new items within a specified time window.

## Commands

### `/rss-check`
Checks configured RSS feeds for new items published within the last N hours.

**Arguments:**
- `hours` (optional): Number of hours to look back. Defaults to 24.

**Usage:**
```bash
# Check for items in the last 24 hours
/rss-check

# Check for items in the last 48 hours
/rss-check 48
```

## Workflow
1.  **Read Configuration**: Loads feed URLs from `config/feeds.json`.
2.  **Fetch Content**: Uses `curl` to retrieve the XML content from each feed.
3.  **Parse & Filter**: Parses the XML (RSS or Atom) and filters items based on the publication date relative to the specified hours.
4.  **Output**: Returns the matching items in JSON format.

## Constraints
-   Requires internet access to fetch feeds.
-   Depends on `curl` being available in the environment.
-   Feed parsing supports standard RSS and Atom formats but might require adjustments for non-standard feeds.
