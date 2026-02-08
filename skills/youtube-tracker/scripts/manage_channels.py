import argparse
import json
import re
import sys
import os
import subprocess
import urllib.request
from urllib.parse import urlparse

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'channels.json')

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }

def load_channels():
    if not os.path.exists(CONFIG_PATH):
        return {'channels': []}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {'channels': []}

def save_channels(data):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f, indent=2)

def get_channel_id(url):
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.strip('/').split('/') if p]

    # Clean URL for fetching
    if path_parts and path_parts[0].startswith('@'):
        base_url = f"{parsed.scheme}://{parsed.netloc}/{path_parts[0]}"
    elif 'channel' in path_parts:
         return path_parts[path_parts.index('channel') + 1]
    else:
        base_url = url

    print(f"Fetching {base_url}...", file=sys.stderr)

    try:
        # Use curl via subprocess as urllib is unreliable/blocked in this environment
        content = subprocess.check_output(['curl', '-s', '-L', base_url], timeout=30).decode('utf-8', errors='ignore')

        # Strategy 1: <meta itemprop="channelId" content="...">
        match = re.search(r'<meta itemprop="channelId" content="([^"]+)"', content)
        if match:
            return match.group(1)

        # Strategy 2: "externalId":"..."
        match = re.search(r'"externalId":"([^"]+)"', content)
        if match:
            return match.group(1)

        # Strategy 3: look for canonical URL with channel ID
        match = re.search(r'<link rel="canonical" href="https://www.youtube.com/channel/([^"]+)"', content)
        if match:
            return match.group(1)

        return None
    except Exception as e:
        print(f"Error fetching URL {url}: {e}", file=sys.stderr)
        return None

def add_channel(url, name=None):
    data = load_channels()

    # Normalize URL for duplicate check (basic)
    for ch in data.get('channels', []):
        if ch['url'] == url:
            print(f"Channel already exists: {ch.get('name', url)}")
            return

    channel_id = get_channel_id(url)

    if not channel_id:
        print(f"Could not extract channel ID for {url}. Is the URL correct?")
        return

    # Derive name if not provided
    if not name:
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.strip('/').split('/') if p]
        if path_parts and path_parts[0].startswith('@'):
            name = path_parts[0]
        else:
            name = "Unknown Channel"

    new_channel = {
        'url': url,
        'id': channel_id,
        'name': name
    }

    if 'channels' not in data:
        data['channels'] = []

    data['channels'].append(new_channel)
    save_channels(data)
    print(f"Added channel: {new_channel['name']} (ID: {channel_id})")

def list_channels():
    data = load_channels()
    channels = data.get('channels', [])
    if not channels:
        print("No channels tracked.")
    else:
        print(f"Tracking {len(channels)} channels:")
        for ch in channels:
            print(f"- {ch.get('name', 'Unknown')} ({ch.get('id')})")

def remove_channel(url_or_id):
    data = load_channels()
    original_count = len(data.get('channels', []))
    data['channels'] = [ch for ch in data.get('channels', []) if ch['url'] != url_or_id and ch['id'] != url_or_id]

    if len(data['channels']) < original_count:
        save_channels(data)
        print(f"Removed channel: {url_or_id}")
    else:
        print(f"Channel not found: {url_or_id}")

def main():
    parser = argparse.ArgumentParser(description='Manage YouTube channels for tracking')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a channel')
    add_parser.add_argument('url', help='Channel URL')
    add_parser.add_argument('--name', help='Optional friendly name')

    # List command
    subparsers.add_parser('list', help='List tracked channels')

    # Remove command
    rm_parser = subparsers.add_parser('remove', help='Remove a channel')
    rm_parser.add_argument('url', help='Channel URL or ID to remove')

    args = parser.parse_args()

    if args.command == 'add':
        add_channel(args.url, args.name)
    elif args.command == 'list':
        list_channels()
    elif args.command == 'remove':
        remove_channel(args.url)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
