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

# ---- STEAM FREE-TO-PLAY ----
steam_url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
steam_apps = requests.get(steam_url, timeout=10).json()["applist"]["apps"]

for app in steam_apps[:2000]:
    name = app["name"].lower()
    if "free" not in name:
        continue

    guid = f"steam-{app['appid']}"
    if guid in existing_guids:
        continue

    title = f"Steam Free: {app['name']}"
    link = f"https://store.steampowered.com/app/{app['appid']}"
    desc = "Free game on Steam"

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
