import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import requests
import os

FEED_FILE = "feed.xml"

def load_existing_guids(root):
    return {item.find("guid").text for item in root.findall("./channel/item") if item.find("guid") is not None}

def add_item(channel, title, link, description, guid):
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "description").text = description
    ET.SubElement(item, "guid").text = guid
    ET.SubElement(item, "pubDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

tree = ET.parse(FEED_FILE)
root = tree.getroot()
channel = root.find("channel")

existing_guids = load_existing_guids(root)

# ---- EPIC GAMES ----
epic_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
epic_data = requests.get(epic_url, timeout=10).json()

for game in epic_data["data"]["Catalog"]["searchStore"]["elements"]:
    if not game.get("promotions"):
        continue

    guid = f"epic-{game['id']}"
    if guid in existing_guids:
        continue

    title = f"Epic Free: {game['title']}"
    link = f"https://store.epicgames.com/p/{game['productSlug']}"
    desc = "Free on Epic Games Store"

    add_item(channel, title, link, desc, guid)

# ---- STEAM FREE PROMOTIONS (100% OFF ONLY) ----
steam_search_url = (
    "https://store.steampowered.com/api/storesearch/"
    "?filter=discounted&specials=1&cc=us&l=en"
)

steam_data = requests.get(steam_search_url, timeout=10).json()

for item in steam_data.get("items", []):
    price = item.get("price", {})
    if price.get("discount_percent") != 100:
        continue

    appid = item.get("id")
    guid = f"steam-promo-{appid}"

    if guid in existing_guids:
        continue

    title = f"Steam Free (Promo): {item['name']}"
    link = f"https://store.steampowered.com/app/{appid}"
    desc = "Free on Steam for a limited time (100% discount)"

    add_item(channel, title, link, desc, guid)

tree.write(FEED_FILE, encoding="utf-8", xml_declaration=True)
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
