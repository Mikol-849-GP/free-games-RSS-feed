import requests
from datetime import datetime
import xml.etree.ElementTree as ET

FEED_FILE = 'feed.xml'
YOUR_SITE_LINK = 'https://yourusername.github.io/free-games-rss/'

ITCH_FREE_RSS = 'https://itch.io/games/free/rss'
EPIC_FREE_RSS = 'https://epicgamesfreebies.com/feed/'
STEAMDB_FREE_RSS = 'https://steamdb.info/rss/'

RSS_SOURCES = [ITCH_FREE_RSS, EPIC_FREE_RSS, STEAMDB_FREE_RSS]

def fetch_items_from_rss(url):
    resp = requests.get(url)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items = []
    for item in root.findall('.//item'):
        title = item.find('title').text
        link = item.find('link').text
        description = item.find('description').text if item.find('description') is not None else ''
        pubDate = item.find('pubDate').text if item.find('pubDate') is not None else datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        items.append({'title': title, 'link': link, 'description': description, 'pubDate': pubDate})
    return items

def generate_feed(items):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = 'My Automated Free Games Feed'
    ET.SubElement(channel, 'link').text = YOUR_SITE_LINK
    ET.SubElement(channel, 'description').text = 'Automatically updated feed of free games from Itch.io, Epic, and SteamDB'
    for item in items:
        item_el = ET.SubElement(channel, 'item')
        ET.SubElement(item_el, 'title').text = item['title']
        ET.SubElement(item_el, 'link').text = item['link']
        ET.SubElement(item_el, 'description').text = item['description']
        ET.SubElement(item_el, 'pubDate').text = item['pubDate']
    return ET.tostring(rss, encoding='utf-8', xml_declaration=True).decode('utf-8')

all_items = []
for rss_url in RSS_SOURCES:
    try:
        all_items.extend(fetch_items_from_rss(rss_url))
    except Exception as e:
        print(f"Failed to fetch from {rss_url}: {e}")

all_items.sort(key=lambda x: datetime.strptime(x['pubDate'], '%a, %d %b %Y %H:%M:%S GMT'), reverse=True)

feed_content = generate_feed(all_items)

with open(FEED_FILE, 'w', encoding='utf-8') as f:
    f.write(feed_content)

print(f"feed.xml updated with {len(all_items)} items!")
