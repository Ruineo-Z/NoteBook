---
name: daily-briefing
description: Automates the daily collection and processing of AI news from YouTube and RSS feeds into NotebookLM.
---
# Daily Briefing Skill

## Overview
Automates the daily collection and processing of AI news from YouTube and RSS feeds. It orchestrates the `youtube-tracker`, `rss-fetcher`, and `notebooklm` skills to build a comprehensive daily briefing in Google NotebookLM.

## Configuration
- **Default Notebook ID**: `8b129704-1f76-48f2-9938-46e9f5a7b402` (每日资讯)

## Commands

### Run Daily Briefing
Run the full daily briefing workflow.
Usage: `/daily-briefing [hours]`

- **Default**: 24 hours (if no argument provided)
- **Example**: `/daily-briefing 48` (Check last 48 hours)

## Workflow

When `/daily-briefing` is invoked:

1.  **Step 1: Collect Video Updates**
    -   Call `youtube-tracker` with the specified hours (e.g., `/yt-check 24`).
    -   Capture the list of new video URLs found.

2.  **Step 2: Collect Article Updates**
    -   Call `rss-fetcher` with the specified hours (e.g., `/rss-check 24`).
    -   Capture the list of new article URLs found.

3.  **Step 3: Aggregate & Filter**
    -   Combine all found URLs.
    -   Remove duplicates if any.
    -   If no new content is found, stop and report "No updates found".

4.  **Step 4: Upload to NotebookLM**
    -   For each unique URL, call `notebooklm source add` to add it to the default notebook (`8b129704-1f76-48f2-9938-46e9f5a7b402`).
    -   Wait for each source to be processed (status: ready).

5.  **Step 5: Generate Briefing**
    -   Once all sources are added, call `notebooklm generate mind-map` to create a visual summary of the day's news.
    -   (Optional) Ask user if they want an Audio Overview generated as well.

## Constraints
-   Do not proceed to generation if source addition fails.
-   Respect the 50-source limit of NotebookLM notebooks (warn user if approaching limit).
