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

now = datetime.now(timezone.utc)

for game in epic_data["data"]["Catalog"]["searchStore"]["elements"]:
    promos = game.get("promotions")
    if not promos:
        continue

    promo_offers = promos.get("promotionalOffers", [])
    if not promo_offers:
        continue

    offer = promo_offers[0]["promotionalOffers"][0]

    start = datetime.fromisoformat(offer["startDate"].replace("Z", "+00:00"))
    end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))

    if not (start <= now <= end):
        continue

    discount = offer["discountSetting"].get("discountPercentage")
    if discount != 0:
        continue

    guid = f"epic-free-{game['id']}"
    if guid in existing_guids:
        continue

    slug = (
        game.get("productSlug")
        or game.get("urlSlug")
        or game.get("offerMappings", [{}])[0].get("pageSlug")
    )

    if not slug:
        continue

    link = f"https://store.epicgames.com/p/{slug}"

    add_item(
        channel,
        f"Epic Free: {game['title']}",
        link,
        "Free on Epic Games Store (limited time)",
        guid
    )


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
