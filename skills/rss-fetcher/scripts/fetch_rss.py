#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/feeds.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        return {"feeds": []}

def fetch_feed(url):
    try:
        # Use curl to fetch the feed content
        result = subprocess.check_output(['curl', '-s', '-L', url], timeout=30)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # Try RFC 822 (standard RSS)
        return parsedate_to_datetime(date_str)
    except Exception:
        pass

    try:
        # Try ISO 8601 (Atom)
        # Python 3.7+ supports fromisoformat, but it might be picky about 'Z'
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        return datetime.fromisoformat(date_str)
    except Exception:
        pass

    return None

def parse_feed(xml_content, hours):
    items = []
    if not xml_content:
        return items

    try:
        root = ET.fromstring(xml_content)

        # Handle namespaces - remove them for simpler parsing
        # This is a bit of a hack but effective for simple scraping
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}', 1)[1]

        cutoff_date = datetime.now(parsedate_to_datetime('Mon, 1 Jan 1900 00:00:00 +0000').tzinfo) - timedelta(hours=hours)

        # Handle RSS (channel/item)
        channel = root.find('channel')
        if channel is not None:
            for item in channel.findall('item'):
                title = item.find('title').text if item.find('title') is not None else "No Title"
                link = item.find('link').text if item.find('link') is not None else ""

                # Try pubDate first, then dc:date or others if needed (but we stripped namespaces)
                pub_date_str = None
                if item.find('pubDate') is not None:
                    pub_date_str = item.find('pubDate').text
                elif item.find('date') is not None:
                    pub_date_str = item.find('date').text

                if pub_date_str:
                    pub_date = parse_date(pub_date_str)
                    if pub_date and pub_date >= cutoff_date:
                        items.append({
                            "title": title,
                            "link": link,
                            "published": pub_date_str,
                            "source": "RSS"
                        })

        # Handle Atom (feed/entry)
        # Since we stripped namespaces, root.tag should be 'feed'
        if root.tag == 'feed':
            for entry in root.findall('entry'):
                title = entry.find('title').text if entry.find('title') is not None else "No Title"

                # Atom links often have href attribute
                link = ""
                link_elem = entry.find('link')
                if link_elem is not None:
                    link = link_elem.get('href', "")
                    if not link and link_elem.text:
                        link = link_elem.text

                updated_str = None
                if entry.find('updated') is not None:
                    updated_str = entry.find('updated').text
                elif entry.find('published') is not None:
                    updated_str = entry.find('published').text

                if updated_str:
                    pub_date = parse_date(updated_str)
                    if pub_date and pub_date >= cutoff_date:
                        items.append({
                            "title": title,
                            "link": link,
                            "published": updated_str,
                            "source": "Atom"
                        })

    except Exception as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)

    return items

def main():
    # Default to 24 hours if not specified
    hours = 24
    if len(sys.argv) > 1:
        try:
            hours = float(sys.argv[1])
        except ValueError:
            print("Invalid hours argument, using default 24", file=sys.stderr)

    config = load_config()
    all_items = []

    for feed in config.get('feeds', []):
        url = feed.get('url')
        if url:
            xml_content = fetch_feed(url)
            items = parse_feed(xml_content, hours)
            for item in items:
                item['feed_name'] = feed.get('name', 'Unknown')
            all_items.extend(items)

    # Output JSON to stdout
    print(json.dumps(all_items, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
