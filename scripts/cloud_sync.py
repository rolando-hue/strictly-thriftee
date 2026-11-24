#!/usr/bin/env python3
"""
Strictly Thriftee — Automated Cloud Depop Sync Worker
Designed to run on GitHub Actions 24/7 (with laptop closed/asleep)
using a scraping gateway (e.g. ScraperAPI / ZenRows) to bypass Cloudflare.
"""

import sys
import os
import json
import re
import urllib.request
import urllib.parse
import datetime

WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVENTORY_FILE = os.path.join(WORKSPACE_DIR, "data", "inventory.json")
INDEX_FILE = os.path.join(WORKSPACE_DIR, "index.html")

SCRAPER_API_KEY = os.environ.get("SCRAPER_API_KEY", "").strip()
ZENROWS_API_KEY = os.environ.get("ZENROWS_API_KEY", "").strip()
DEPOP_URL = "https://www.depop.com/strictly_thriftee/"


def fetch_rendered_depop_html() -> str:
    """Fetches rendered Depop HTML via residential gateway to bypass Cloudflare."""
    if not SCRAPER_API_KEY and not ZENROWS_API_KEY:
        sys.stderr.write("Error: Neither SCRAPER_API_KEY nor ZENROWS_API_KEY is configured.\n")
        sys.stderr.write("Set SCRAPER_API_KEY in your GitHub Repository Secrets.\n")
        sys.exit(1)

    if SCRAPER_API_KEY:
        print("[Cloud Sync] Fetching via ScraperAPI with residential JS rendering...")
        params = {
            "api_key": SCRAPER_API_KEY,
            "url": DEPOP_URL,
            "render": "true",
            "country_code": "us",
        }
        gateway_url = "https://api.scraperapi.com/?" + urllib.parse.urlencode(params)
    else:
        print("[Cloud Sync] Fetching via ZenRows gateway...")
        params = {
            "apikey": ZENROWS_API_KEY,
            "url": DEPOP_URL,
            "js_render": "true",
            "premium_proxy": "true",
        }
        gateway_url = "https://api.zenrows.com/v1/?" + urllib.parse.urlencode(params)

    req = urllib.request.Request(
        gateway_url,
        headers={"User-Agent": "StrictlyThriftee-CloudSync/1.0"}
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read().decode("utf-8", errors="replace")


def clean_title_from_slug(slug: str) -> str:
    parts = slug.strip("/").split("/")[-1].split("-")
    if len(parts) > 2:
        words = parts[1:-1]
    else:
        words = parts
    title = " ".join(words).title()
    replacements = {
        "Hm": "H&M",
        "Jcrew": "J.Crew",
        "Ut Kaws": "UT KAWS",
        "T Shirt": "T-Shirt",
        "Zip Up": "Zip-Up",
        "Full Zip": "Full-Zip",
        "Xl": "XL",
        "And": "&",
        "Levis": "Levi's",
    }
    for k, v in replacements.items():
        title = re.sub(rf"\b{k}\b", v, title, flags=re.IGNORECASE)
    return title


def extract_brand_from_title(title: str) -> str:
    known_brands = [
        "Coach", "Michael Kors", "Kenneth Cole", "Levi's", "Brooks Brothers",
        "Banana Republic", "Umbro", "H&M", "Polo Ralph Lauren", "Ralph Lauren",
        "Novamen", "Fashion Nova", "Cotton On", "Primark", "Hollister",
        "Fanatics", "RSQ", "Supreme", "AllSaints", "Uniqlo", "Nike", "Adidas",
        "Zara", "Tommy Hilfiger", "Calvin Klein", "Champion", "Under Armour",
        "Southpole", "G-Star RAW", "Cole Haan", "Alexander Del Rossa"
    ]
    for b in known_brands:
        if re.search(rf"\b{re.escape(b)}\b", title, re.IGNORECASE):
            return b
    return "Other"


def categorize(title: str, price: float = 0.0) -> tuple:
    text = title.lower()
    if any(k in text for k in ['bag', 'backpack', 'hobo', 'tote', 'duffel', 'necklace', 'pendant', 'amethyst', 'quartz', 'jewelry', 'jade', 'watch', 'wallet']):
        return "bags-accessories", "Bags & Accessories"
    designer_brands = ['nanushka', 'hart schaffner marx', 'polo ralph lauren', 'ralph lauren', 'gucci', 'prada', 'coach', 'supreme', 'brooks brothers', 'comme des garcons', 'diesel', 'allsaints']
    if (price and price >= 45.0) or any(b in text for b in designer_brands):
        return "designer-finds", "Designer Finds"
    if 'like new' in text or 'brand new' in text:
        return "mens-like-new", "Men’s Like-New"
    return "preloved-clothing", "Preloved Clothing"


def extract_listings_from_html(html: str) -> list:
    """Extracts product listings from rendered Depop storefront HTML."""
    listings = []
    # Pattern for product links: href="/products/<slug>/"
    product_link_pattern = re.compile(r'href=["\'](/products/[^"\']+)["\']')
    matches = product_link_pattern.findall(html)
    seen_hrefs = set()

    for href in matches:
        if href in seen_hrefs or not href.endswith("/"):
            continue
        seen_hrefs.add(href)
        slug = href.strip("/").split("/")[-1]
        
        # Check if item is marked sold
        # Depop sold items typically have class or badge or text containing 'Sold' near the item
        is_sold = False
        idx = html.find(href)
        if idx != -1:
            snippet = html[max(0, idx - 500):min(len(html), idx + 1000)]
            if re.search(r'\bSold\b', snippet, re.IGNORECASE) or 'aria-label="Sold"' in snippet or 'P8.jpg' in snippet:
                is_sold = True

        # Extract price snippet
        price = None
        orig_price = None
        if idx != -1:
            snippet = html[max(0, idx - 200):min(len(html), idx + 800)]
            prices_found = re.findall(r'\$\s*([0-9]+(?:\.[0-9]{2})?)', snippet)
            if prices_found:
                try:
                    price = float(prices_found[-1])
                    if len(prices_found) > 1:
                        orig_price = float(prices_found[0])
                except ValueError:
                    pass

        # Extract main image (always upgrade to full-resolution P0.jpg)
        img_url = ""
        if idx != -1:
            snippet = html[max(0, idx - 400):min(len(html), idx + 600)]
            img_match = re.search(r'src=["\'](https://media-photos\.depop\.com/[^"\']+)["\']', snippet)
            if img_match:
                img_url = re.sub(r'/P\d+\.jpg', '/P0.jpg', img_match.group(1))

        listings.append({
            "href": href,
            "slug": slug,
            "price": price,
            "originalPrice": orig_price,
            "sold": is_sold,
            "img": img_url,
        })

    return listings


def main():
    html = fetch_rendered_depop_html()
    extracted = extract_listings_from_html(html)
    print(f"[Cloud Sync] Extracted {len(extracted)} listings from Depop storefront.")

    if not extracted:
        print("[Cloud Sync] Warning: No listings parsed from HTML, preserving current inventory.")
        return

    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_items = data.get("items", [])
    items_by_slug = {it.get("slug"): it for it in existing_items if it.get("slug")}

    updated_items = []
    seen_slugs = set()

    for item in extracted:
        slug = item["slug"]
        seen_slugs.add(slug)
        existing = items_by_slug.get(slug)
        if existing:
            existing["sold"] = item["sold"]
            if item.get("price") is not None:
                existing["price"] = item["price"]
            if item.get("originalPrice") is not None:
                existing["originalPrice"] = item["originalPrice"]
            if item["img"] and not existing.get("image"):
                existing["image"] = item["img"]
            # Ensure existing images are upgraded to P0
            if existing.get("image"):
                existing["image"] = re.sub(r'/P\d+\.jpg', '/P0.jpg', existing["image"])
            if existing.get("thumbnail"):
                existing["thumbnail"] = re.sub(r'/P\d+\.jpg', '/P0.jpg', existing["thumbnail"])
            if existing.get("images"):
                existing["images"] = [re.sub(r'/P\d+\.jpg', '/P0.jpg', x) for x in existing["images"]]
            updated_items.append(existing)
        else:
            title = clean_title_from_slug(slug)
            brand = extract_brand_from_title(title)
            cat, cat_label = categorize(title, price=item["price"] or 0.0)
            item_id = slug.split("-")[-1] if "-" in slug else slug[:6]
            full_url = f"https://www.depop.com{item['href']}"
            raw_img = item["img"] or "https://strictlythriftee.com/assets/strictly-thriftee-logo.png"
            img = re.sub(r'/P\d+\.jpg', '/P0.jpg', raw_img)
            new_item = {
                "id": item_id,
                "slug": slug,
                "title": title,
                "brand": brand,
                "price": item["price"],
                "originalPrice": item["originalPrice"],
                "currency": "USD",
                "size": "Regular",
                "condition": "Pre-owned",
                "category": cat,
                "categoryLabel": cat_label,
                "sold": item["sold"],
                "url": full_url,
                "image": img,
                "images": [img],
                "thumbnail": img,
                "description": f"{title}. Sourced by Strictly Thriftee. Available on Depop with Buyer Protection."
            }
            updated_items.append(new_item)

    # Retain existing items not present in current page snapshot
    for it in existing_items:
        if it.get("slug") not in seen_slugs:
            updated_items.append(it)

    total_count = len(updated_items)
    sold_count = sum(1 for i in updated_items if i.get("sold"))
    active_count = total_count - sold_count

    cat_counts = {
        "preloved-clothing": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "preloved-clothing"),
        "designer-finds": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "designer-finds"),
        "mens-like-new": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "mens-like-new"),
        "bags-accessories": sum(1 for i in updated_items if not i.get("sold") and i.get("category") == "bags-accessories"),
    }

    data["shop"]["soldCount"] = sold_count
    data["shop"]["activeCount"] = active_count
    data["shop"]["totalCount"] = total_count
    data["shop"]["lastSyncedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    data["items"] = updated_items

    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    # Update index.html count badges
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        idx_html = f.read()

    idx_html = re.sub(r'(<span id="count-all">)\d+(</span>)', rf'\g<1>{active_count}\g<2>', idx_html)
    idx_html = re.sub(r'(<span id="count-sold">)\d+(</span>)', rf'\g<1>{sold_count}\g<2>', idx_html)
    idx_html = re.sub(r'(<span id="count-preloved-clothing">)\d+(</span>)', rf'\g<1>{cat_counts["preloved-clothing"]}\g<2>', idx_html)
    idx_html = re.sub(r'(<span id="count-designer-finds">)\d+(</span>)', rf'\g<1>{cat_counts["designer-finds"]}\g<2>', idx_html)
    idx_html = re.sub(r'(<span id="count-mens-like-new">)\d+(</span>)', rf'\g<1>{cat_counts["mens-like-new"]}\g<2>', idx_html)
    idx_html = re.sub(r'(<span id="count-bags-accessories">)\d+(</span>)', rf'\g<1>{cat_counts["bags-accessories"]}\g<2>', idx_html)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(idx_html)

    print(f"[Cloud Sync] Completed successfully. Total: {total_count} (Active: {active_count}, Sold: {sold_count})")


if __name__ == "__main__":
    main()
