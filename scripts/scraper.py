#!/usr/bin/env python3
"""
Strictly Thriftee — CLI Scraper & Inventory Inspector
Website: https://strictlythriftee.com
Author: Strictly Thriftee Team

A zero-dependency CLI tool to scrape, query, filter, and export
inventory from strictlythriftee.com (live web, HTML, or local JSON).
"""

import sys
import os
import json
import re
import argparse
import urllib.request
import urllib.error
import urllib.parse
import csv
from typing import List, Dict, Any, Optional

DEFAULT_REMOTE_URL = "https://strictlythriftee.com/data/inventory.json"
LOCAL_INVENTORY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "inventory.json")

# ANSI Color codes (disabled if stdout is redirected)
USE_COLOR = sys.stdout.isatty()

def colorize(text: str, code: str) -> str:
    if not USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

BOLD = "1"
DIM = "2"
GREEN = "32"
YELLOW = "33"
BLUE = "34"
MAGENTA = "35"
CYAN = "36"
RED = "31"
WHITE = "97"
BG_DARK = "40"


def fetch_url(url: str) -> str:
    """Fetches text content from a remote URL with appropriate headers."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "StrictlyThriftee-CLI-Scraper/1.0 (+https://strictlythriftee.com)",
            "Accept": "application/json, text/html, */*"
        }
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        return response.read().decode("utf-8", errors="replace")


def extract_from_html(html_text: str, base_url: str = "https://strictlythriftee.com") -> Dict[str, Any]:
    """
    Parses HTML from strictlythriftee.com:
    - Extracts structured JSON-LD schemas (Store, AggregateOffer, Reviews)
    - Locates inventory references or falls back to data/inventory.json
    """
    inventory_data: Dict[str, Any] = {"shop": {}, "items": []}

    # 1. Search for JSON-LD blocks
    json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html_text, re.DOTALL | re.IGNORECASE)
    for block in json_ld_matches:
        try:
            parsed = json.loads(block.strip())
            if isinstance(parsed, dict):
                if parsed.get("@type") in ("Store", "OnlineStore", "ClothingStore"):
                    inventory_data["shop"].update({
                        "name": parsed.get("name", "Strictly Thriftee"),
                        "bio": parsed.get("description", ""),
                        "url": parsed.get("url", base_url),
                    })
                    if "aggregateRating" in parsed:
                        inventory_data["shop"]["rating"] = parsed["aggregateRating"].get("ratingValue")
                        inventory_data["shop"]["reviewCount"] = parsed["aggregateRating"].get("reviewCount")
        except Exception:
            pass

    # 2. Check for inventory reference in scripts
    inv_rel_match = re.search(r'fetch\([\'"](\.?/?[^\'"]*inventory\.json[^\'"]*)[\'"]\)', html_text)
    inv_path_rel = None
    if inv_rel_match:
        inv_path_rel = inv_rel_match.group(1).split("?")[0].lstrip("./")
    else:
        inv_path_rel = "data/inventory.json"

    # Try local filesystem first if file exists
    local_inv = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), inv_path_rel)
    if os.path.isfile(local_inv):
        try:
            with open(local_inv, "r", encoding="utf-8") as f:
                parsed_json = json.load(f)
                if isinstance(parsed_json, dict):
                    if "items" in parsed_json:
                        inventory_data["items"] = parsed_json["items"]
                    if "shop" in parsed_json:
                        inventory_data["shop"].update(parsed_json["shop"])
                return inventory_data
        except Exception:
            pass

    # Otherwise fetch referenced remote URL
    inv_url = urllib.parse.urljoin(base_url, inv_path_rel)
    try:
        raw_json = fetch_url(inv_url)
        parsed_json = json.loads(raw_json)
        if isinstance(parsed_json, dict):
            if "items" in parsed_json:
                inventory_data["items"] = parsed_json["items"]
            if "shop" in parsed_json:
                inventory_data["shop"].update(parsed_json["shop"])
    except Exception as e:
        sys.stderr.write(f"Warning: Could not fetch referenced inventory {inv_url}: {e}\n")

    return inventory_data


def load_inventory(source: Optional[str] = None) -> Dict[str, Any]:
    """Loads inventory from local file, remote JSON URL, or scraped HTML page."""
    # 1. Local file path provided
    if source and os.path.isfile(source):
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
            if source.endswith(".html") or "<!DOCTYPE" in content or "<html" in content:
                return extract_from_html(content)
            return json.loads(content)

    # 2. Default to local inventory if no custom source specified
    if not source and os.path.isfile(LOCAL_INVENTORY_PATH):
        with open(LOCAL_INVENTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    # 3. Remote URL
    target_url = source or DEFAULT_REMOTE_URL
    try:
        text = fetch_url(target_url)
        # Check if URL returned HTML instead of raw JSON
        if "<!DOCTYPE" in text or "<html" in text or "text/html" in text:
            return extract_from_html(text, base_url=target_url)
        return json.loads(text)
    except urllib.error.URLError as e:
        if os.path.isfile(LOCAL_INVENTORY_PATH):
            sys.stderr.write(f"Warning: Remote fetch failed ({e}). Falling back to local data/inventory.json.\n")
            with open(LOCAL_INVENTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        sys.stderr.write(f"Error fetching from {target_url}: {e}\n")
        sys.exit(1)


def filter_items(
    items: List[Dict[str, Any]],
    query: Optional[str] = None,
    category: Optional[str] = None,
    status: str = "active",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Filters and sorts inventory items based on user criteria."""
    filtered = []
    q = query.lower() if query else None

    for item in items:
        # Status filter
        is_sold = bool(item.get("sold", False))
        if status == "active" and is_sold:
            continue
        elif status == "sold" and not is_sold:
            continue

        # Category filter
        item_cat = (item.get("category") or "").lower()
        if category and category.lower() not in item_cat:
            continue

        # Price range filter
        price = float(item.get("price") or 0.0)
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue

        # Text query filter
        if q:
            title = (item.get("title") or "").lower()
            brand = (item.get("brand") or "").lower()
            desc = (item.get("description") or "").lower()
            cat_label = (item.get("categoryLabel") or "").lower()
            if q not in title and q not in brand and q not in desc and q not in cat_label:
                continue

        filtered.append(item)

    # Sorting
    if sort_by == "price-asc":
        filtered.sort(key=lambda x: float(x.get("price") or 0.0))
    elif sort_by == "price-desc":
        filtered.sort(key=lambda x: float(x.get("price") or 0.0), reverse=True)
    elif sort_by == "title":
        filtered.sort(key=lambda x: (x.get("title") or "").lower())

    if limit and limit > 0:
        filtered = filtered[:limit]

    return filtered


def print_summary(shop: Dict[str, Any], items: List[Dict[str, Any]]) -> None:
    """Prints a styled overview of the shop and inventory breakdown."""
    total = len(items)
    sold = sum(1 for i in items if i.get("sold"))
    active = total - sold
    prices = [float(i.get("price") or 0.0) for i in items if not i.get("sold")]
    avg_price = (sum(prices) / len(prices)) if prices else 0.0

    cats: Dict[str, Dict[str, int]] = {}
    for i in items:
        cat = i.get("categoryLabel") or i.get("category") or "Uncategorized"
        if cat not in cats:
            cats[cat] = {"total": 0, "active": 0, "sold": 0}
        cats[cat]["total"] += 1
        if i.get("sold"):
            cats[cat]["sold"] += 1
        else:
            cats[cat]["active"] += 1

    header_border = colorize("=" * 68, CYAN)
    divider = colorize("-" * 68, DIM)

    print("\n" + header_border)
    print(colorize("  ✨ STRICTLY THRIFTEE STOREFRONT OVERVIEW ✨", BOLD))
    print(header_border)
    print(f"  {colorize('Store Name:', BOLD)}   {shop.get('name', 'Strictly Thriftee')}")
    print(f"  {colorize('Handle:', BOLD)}       @{shop.get('handle', 'strictly_thriftee')}")
    print(f"  {colorize('Website:', BOLD)}      {colorize(shop.get('url', 'https://strictlythriftee.com'), BLUE)}")
    try:
        rating = int(float(shop.get('rating', 5) or 5))
    except (ValueError, TypeError):
        rating = 5
    print(f"  {colorize('Rating:', BOLD)}       {'⭐' * rating} ({shop.get('reviewCount', 0)} reviews)")
    if shop.get('bio'):
        print(f"  {colorize('Bio:', BOLD)}          {colorize(shop.get('bio'), DIM)}")
    if shop.get('lastSyncedAt'):
        print(f"  {colorize('Last Synced:', BOLD)}  {shop.get('lastSyncedAt')}")
    print(divider)
    print(f"  {colorize('Total Items:', BOLD)}  {colorize(str(total), WHITE):<5} | "
          f"{colorize('Active:', BOLD)} {colorize(str(active), GREEN):<5} | "
          f"{colorize('Sold:', BOLD)} {colorize(str(sold), RED):<5}")
    if prices:
        print(f"  {colorize('Active Prices:', BOLD)} ${min(prices):.2f} - ${max(prices):.2f} "
              f"(Avg: {colorize(f'${avg_price:.2f}', YELLOW)})")
    print(divider)
    print(colorize("  Category Breakdown:", BOLD))
    for cat, counts in sorted(cats.items()):
        print(f"    • {cat:<24} Active: {colorize(str(counts['active']), GREEN):<4} "
              f"Sold: {colorize(str(counts['sold']), RED):<4} Total: {counts['total']}")
    print(header_border + "\n")


def print_table(items: List[Dict[str, Any]]) -> None:
    """Prints items in a formatted terminal table."""
    if not items:
        print(colorize("No items matched the given filters.", YELLOW))
        return

    print(f"\nFound {colorize(str(len(items)), BOLD)} item(s):\n")
    header = f"{'#':<4} {'STATUS':<8} {'PRICE':<8} {'SIZE':<11} {'CATEGORY':<20} {'TITLE'}"
    print(colorize(header, BOLD))
    print(colorize("-" * 98, DIM))

    for idx, item in enumerate(items, 1):
        is_sold = bool(item.get("sold", False))
        status_badge = colorize("SOLD  ", RED) if is_sold else colorize("ACTIVE", GREEN)
        price_val = float(item.get("price") or 0.0)
        price_str = colorize(f"${price_val:<6.2f}", YELLOW)
        size = (item.get("size") or "N/A")[:10]
        cat = (item.get("categoryLabel") or item.get("category") or "")[:19]
        title = item.get("title") or "Untitled"
        if len(title) > 42:
            title = title[:39] + "..."

        print(f"{idx:<4} {status_badge}  {price_str} {size:<11} {cat:<20} {title}")

    print(colorize("-" * 98, DIM) + "\n")


def export_csv(items: List[Dict[str, Any]], output_path: Optional[str] = None) -> None:
    """Exports items to CSV."""
    fieldnames = ["id", "title", "brand", "price", "size", "category", "sold", "url", "image"]
    f = open(output_path, "w", newline="", encoding="utf-8") if output_path else sys.stdout

    try:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for item in items:
            writer.writerow({
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "brand": item.get("brand", ""),
                "price": item.get("price", ""),
                "size": item.get("size", ""),
                "category": item.get("category", ""),
                "sold": item.get("sold", False),
                "url": item.get("url", ""),
                "image": item.get("image", ""),
            })
    finally:
        if output_path:
            f.close()
            print(colorize(f"✔ Exported {len(items)} items to {output_path}", GREEN))


def main():
    parser = argparse.ArgumentParser(
        description="Strictly Thriftee (strictlythriftee.com) — CLI Scraper & Inventory Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./strictly-scraper --summary
  ./strictly-scraper --search "amethyst"
  ./strictly-scraper --category designer-finds --max-price 50
  ./strictly-scraper --status sold
  ./strictly-scraper --export-csv inventory.csv
  ./strictly-scraper --source https://strictlythriftee.com
        """,
    )

    parser.add_argument(
        "--summary", action="store_true", help="Display storefront summary, metrics, and category breakdown"
    )
    parser.add_argument(
        "-s", "--search", type=str, help="Search query (matches title, brand, description)"
    )
    parser.add_argument(
        "-c", "--category", type=str,
        choices=["bags-accessories", "designer-finds", "mens-like-new", "preloved-clothing"],
        help="Filter by category slug"
    )
    parser.add_argument(
        "--status", type=str, choices=["active", "sold", "all"], default="active",
        help="Filter by status (default: active)"
    )
    parser.add_argument("--min-price", type=float, help="Minimum price filter (USD)")
    parser.add_argument("--max-price", type=float, help="Maximum price filter (USD)")
    parser.add_argument(
        "--sort", type=str, choices=["price-asc", "price-desc", "title"],
        help="Sort results"
    )
    parser.add_argument("-n", "--limit", type=int, default=25, help="Max results to display (default: 25)")
    parser.add_argument(
        "--remote", action="store_true",
        help="Force fetching directly from live https://strictlythriftee.com"
    )
    parser.add_argument(
        "--source", type=str, help="Custom URL (HTML or JSON) or local file path"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument(
        "--export-csv", type=str, metavar="FILE", help="Export filtered items to a CSV file"
    )

    args = parser.parse_args()

    # Determine source
    source = args.source
    if args.remote and not source:
        source = DEFAULT_REMOTE_URL

    data = load_inventory(source)
    shop = data.get("shop", {})
    all_items = data.get("items", [])

    if args.summary:
        print_summary(shop, all_items)
        return

    # Filter items
    filtered = filter_items(
        items=all_items,
        query=args.search,
        category=args.category,
        status=args.status,
        min_price=args.min_price,
        max_price=args.max_price,
        sort_by=args.sort,
        limit=args.limit if not (args.json or args.export_csv) else None,
    )

    if args.export_csv:
        export_csv(filtered, args.export_csv)
    elif args.json:
        print(json.dumps(filtered, indent=2))
    else:
        print_table(filtered)


if __name__ == "__main__":
    main()
