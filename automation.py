import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import requests

FEED_FILE = "feed.xml"

def load_existing_guids(root):
    return {
        item.find("guid").text
        for item in root.findall("./channel/item")
        if item.find("guid") is not None
    }

def add_item(channel, title, link, description, guid):
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "description").text = description
    ET.SubElement(item, "guid").text = guid
    ET.SubElement(item, "pubDate").text = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

tree = ET.parse(FEED_FILE)
root = tree.getroot()
channel = root.find("./channel")

if channel is None:
    raise RuntimeError("No <channel> element found in feed.xml")

existing_guids = load_existing_guids(root)

# ---- EPIC GAMES ----
epic_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions"
epic_data = requests.get(epic_url, timeout=10).json()

elements = (
    epic_data
    .get("data", {})
    .get("Catalog", {})
    .get("searchStore", {})
    .get("elements", [])
)

for game in elements:
    if not game.get("promotions"):
        continue

    guid = f"epic-{game['id']}"
    if guid in existing_guids:
        continue

    slug = game.get("productSlug") or game.get("urlSlug")
    if not slug:
        continue

    title = f"Epic Free: {game['title']}"
    link = f"https://store.epicgames.com/p/{slug}"
    desc = "Free on Epic Games Store"

    add_item(channel, title, link, desc, guid)

# ---- STEAM FREE PROMOTIONS (100% OFF ONLY) ----
steam_url = "https://store.steampowered.com/api/storesearch"
params = {
    "filter": "specials",
    "specials": 1,
    "cc": "us",
    "l": "en",
}

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(steam_url, params=params, headers=headers, timeout=10)

if response.headers.get("Content-Type", "").startswith("application/json"):
    steam_data = response.json()
else:
    steam_data = {}

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
