---
name: sync-depop
description: >-
  Sync Strictly Thriftee inventory with the live Depop storefront (@strictly_thriftee),
  update data/inventory.json and index.html in-stock counts, and deploy to GitHub Pages.
---

# Strictly Thriftee Depop Inventory Sync

Follow this runbook when synchronizing inventory between the live Depop shop and the static storefront.

## Procedure

### Step 1: Storefront Inspection via Browser Subagent
- Delegate inspection of `https://www.depop.com/strictly_thriftee/` to the browser subagent in the user's open Hub window.
- Extract:
  - Total item count
  - Active listings (titles, prices, URLs, images)
  - Sold items (verified against the profile's sold badge)

### Step 2: Compare Against Local Inventory
- Compare extracted listings against `data/inventory.json`.
- If an active item in `data/inventory.json` is marked Sold on Depop, set `"sold": true`.
- If a new listing is detected, categorize it using the project's taxonomy:
  - `bags-accessories`: Bags, duffels, jewelry, pendants, crystals, amethyst, quartz.
  - `designer-finds`: Price >= $45 or designer brands (Nanushka, Hart Schaffner Marx, Polo Ralph Lauren, Gucci, Prada, Coach).
  - `mens-like-new`: Items marked "like new" or "brand new".
  - `preloved-clothing`: Standard pre-owned apparel.
- Ingest the item with its title, price, thumbnail, full images array, size, and category.

### Step 3: Update Metadata & Static Counts
- In `data/inventory.json`, update:
  - `shop.soldCount`
  - `shop.activeCount`
  - `shop.lastSyncedAt` (current ISO timestamp)
- In `index.html`, verify and update the static count badges:
  - `#count-all`
  - `#count-sold`
  - `#count-preloved-clothing`
  - `#count-designer-finds`
  - `#count-mens-like-new`
  - `#count-bags-accessories`

### Step 4: Rebase & Deploy
1. Commit changes to `data/inventory.json` and `index.html`.
2. Run `git pull --rebase origin main` (resolving any `lastSyncedAt` conflicts with automated cron runs).
3. Push to `origin main` to trigger GitHub Actions deployment to `https://strictlythriftee.com/`.
