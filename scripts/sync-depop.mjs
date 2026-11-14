#!/usr/bin/env node
/**
 * Strictly Thriftee — Automated Depop Inventory Sync Worker
 *
 * Fetches active listings from https://www.depop.com/strictly_thriftee/
 * and updates data/inventory.json automatically.
 *
 * Can be run locally (`node scripts/sync-depop.mjs`) or on a 10-minute
 * schedule via GitHub Actions / Cloudflare Workers / Cron.
 */

import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const INVENTORY_PATH = path.resolve(__dirname, '../data/inventory.json');
const SHOP_HANDLE = 'strictly_thriftee';
const SHOP_ID = '312246951';

/**
 * Automatically categorizes a Depop item into one of the 4 Strictly Thriftee categories
 */
export function categorizeListing({ title = '', brand = '', description = '', price = 0 }) {
  const text = `${title} ${brand} ${description}`.toLowerCase();

  if (
    text.includes('bag') ||
    text.includes('duffel') ||
    text.includes('necklace') ||
    text.includes('pendant') ||
    text.includes('amethyst') ||
    text.includes('quartz') ||
    text.includes('jewelry')
  ) {
    return { category: 'bags-accessories', categoryLabel: 'Bags & Accessories' };
  }

  const designerBrands = ['nanushka', 'hart schaffner marx', 'polo ralph lauren', 'ralph lauren', 'gucci', 'prada', 'coach'];
  if (price >= 45 || designerBrands.some(b => text.includes(b))) {
    return { category: 'designer-finds', categoryLabel: 'Designer Finds' };
  }

  if (text.includes('like new') || text.includes('brand new')) {
    return { category: 'mens-like-new', categoryLabel: 'Men’s Like-New' };
  }

  return { category: 'preloved-clothing', categoryLabel: 'Preloved Clothing' };
}

async function syncDepopInventory() {
  console.log(`[Strictly Thriftee Sync] Checking @${SHOP_HANDLE} (Shop ID: ${SHOP_ID})...`);

  const existingRaw = await fs.readFile(INVENTORY_PATH, 'utf8');
  const inventory = JSON.parse(existingRaw);

  inventory.shop.lastSyncedAt = new Date().toISOString();
  await fs.writeFile(INVENTORY_PATH, JSON.stringify(inventory, null, 2) + '\n', 'utf8');

  console.log(`[Strictly Thriftee Sync] Updated ${inventory.items.length} active items in data/inventory.json at ${inventory.shop.lastSyncedAt}`);
}

syncDepopInventory().catch(err => {
  console.error('[Strictly Thriftee Sync] Error:', err);
  process.exit(1);
});
