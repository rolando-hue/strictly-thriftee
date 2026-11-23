# Strictly Thriftee — CLI Scraper & Inventory Explorer

A fast, zero-dependency command-line interface for querying, searching, analyzing, and exporting the inventory of **[strictlythriftee.com](https://strictlythriftee.com)**.

---

## Quick Start

Run the scraper directly using the `./strictly-scraper` executable (or `python3 scripts/scraper.py`):

```bash
# 1. View live storefront metrics & category breakdown
./strictly-scraper --summary

# 2. Search active inventory by keyword
./strictly-scraper --search "amethyst"

# 3. Filter by category
./strictly-scraper --category designer-finds --sort price-desc

# 4. Filter by price range ($10 - $25)
./strictly-scraper --min-price 10 --max-price 25

# 5. Inspect sold items
./strictly-scraper --status sold

# 6. Export filtered listings to CSV
./strictly-scraper --status active --export-csv active_listings.csv

# 7. Pipe JSON to jq or another script
./strictly-scraper --category bags-accessories --json
```

---

## CLI Options

| Flag | Description | Options / Example |
| :--- | :--- | :--- |
| `--summary` | Displays shop metrics, rating, totals, and category breakdown | |
| `-s`, `--search` | Case-insensitive keyword search (title, brand, description) | `--search "pendant"` |
| `-c`, `--category` | Filter by category slug | `bags-accessories`, `designer-finds`, `mens-like-new`, `preloved-clothing` |
| `--status` | Item availability status | `active` (default), `sold`, `all` |
| `--min-price` | Minimum price filter (USD) | `--min-price 15` |
| `--max-price` | Maximum price filter (USD) | `--max-price 50` |
| `--sort` | Sort results | `price-asc`, `price-desc`, `title` |
| `-n`, `--limit` | Maximum results to display (default: 25) | `-n 10` |
| `--remote` | Force live fetch from `https://strictlythriftee.com/data/inventory.json` | |
| `--source` | Custom JSON URL or local path | `--source data/inventory.json` |
| `--json` | Output raw filtered JSON | |
| `--export-csv` | Export output directly to a CSV file | `--export-csv items.csv` |

---

## Scraping strictlythriftee.com vs Depop (@strictly_thriftee)

- **strictlythriftee.com**: Fully open and CLI-friendly. All inventory is served via GitHub Pages at `https://strictlythriftee.com/data/inventory.json` with no anti-bot challenges. `scripts/scraper.py` connects to this directly or reads local workspace files.
- **Depop (depop.com/strictly_thriftee)**: Depop protects storefronts and API endpoints using Cloudflare edge anti-bot management (returning `HTTP 403 Forbidden` on standard CLI tools like `curl`, `requests`, or `axios`). To sync newly dropped or sold items from Depop into strictlythriftee.com, use the built-in Antigravity **browser subagent** via the `/sync-depop` skill.
