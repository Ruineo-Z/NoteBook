import argparse
import json
import xml.etree.ElementTree as ET
import os
import sys
import urllib.request
import subprocess
from datetime import datetime, timedelta, timezone

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'channels.json')

def load_channels():
    if not os.path.exists(CONFIG_PATH):
        return []
    try:
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            return data.get('channels', [])
    except:
        return []

def get_updates(hours=24):
    channels = load_channels()
    new_videos = []

    # Calculate cutoff time (UTC)
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    for channel in channels:
        channel_id = channel.get('id')
        if not channel_id:
            continue

        rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        try:
            # Use curl via subprocess as urllib is unreliable/blocked in this environment
            content = subprocess.check_output(['curl', '-s', '-L', rss_url], timeout=30)

            # req = urllib.request.Request(
            #     rss_url,
            #     headers={
            #         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            #     }
            # )
            # with urllib.request.urlopen(req, timeout=30) as response:
            #     content = response.read()

            root = ET.fromstring(content)
            # Namespace for Atom feed
            ns = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

            for entry in root.findall('atom:entry', ns):
                published_str = entry.find('atom:published', ns).text
                # Format: 2023-10-27T14:00:13+00:00
                published_dt = datetime.fromisoformat(published_str)

                if published_dt > cutoff_time:
                    video_id = entry.find('yt:videoId', ns).text
                    title = entry.find('atom:title', ns).text
                    link_elem = entry.find('atom:link', ns)
                    link = link_elem.attrib['href'] if link_elem is not None else f"https://www.youtube.com/watch?v={video_id}"

                    new_videos.append({
                        'channel': channel.get('name'),
                        'title': title,
                        'url': link,
                        'published': published_str,
                        'video_id': video_id
                    })

        except Exception as e:
            print(f"Error processing {channel.get('name')}: {e}", file=sys.stderr)
            pass

    return new_videos

def main():
    parser = argparse.ArgumentParser(description='Check for new YouTube videos')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    updates = get_updates(args.hours)

    if args.json:
        print(json.dumps(updates, indent=2, ensure_ascii=False))
    else:
        if not updates:
            print(f"No new videos found in the last {args.hours} hours.")
        else:
            print(f"Found {len(updates)} new videos in the last {args.hours} hours:")
            for video in updates:
                print(f"- [{video['channel']}] {video['title']}")
                print(f"  {video['url']}")
                print(f"  Published: {video['published']}")
                print("")

if __name__ == '__main__':
    main()
