# Deploy Strictly Thriftee to GitHub Pages & Connect GoDaddy

### Step 1: Push to GitHub
Run the following in your terminal (or authorize the CLI with `gh auth login`):

```bash
# 1. Authenticate with your GitHub account
gh auth login

# 2. Create the repository on your GitHub account and push
cd /Users/Tracey/.gemini/antigravity/scratch/strictly-thriftee
gh repo create strictly-thriftee --public --source=. --remote=origin --push
```

*(Or create an empty repository named `strictly-thriftee` on https://github.com/new, and run:)*
```bash
git remote add origin https://github.com/<YOUR-GITHUB-USERNAME>/strictly-thriftee.git
git branch -M main
git push -u origin main
```

---

### Step 2: Enable GitHub Pages in Repository Settings
1. Go to your repo: `https://github.com/<YOUR-GITHUB-USERNAME>/strictly-thriftee/settings/pages`
2. Under **Build and deployment > Source**, select **GitHub Actions**.
3. Under **Custom domain**, enter: `strictlythriftee.com` (already set up in your `CNAME` file).
4. Check **Enforce HTTPS**.

---

### Step 3: Connect GoDaddy DNS (Point strictlythriftee.com)
Log in to your **GoDaddy Domain Portfolio** at https://dcc.godaddy.com/:
1. Click on **strictlythriftee.com** > **DNS**.
2. **Add / Update the 4 GitHub Pages Apex `A` Records** (pointing `@`):
   - **Type:** `A` | **Name:** `@` | **Value:** `185.199.108.153` | **TTL:** 1 Hour
   - **Type:** `A` | **Name:** `@` | **Value:** `185.199.109.153` | **TTL:** 1 Hour
   - **Type:** `A` | **Name:** `@` | **Value:** `185.199.110.153` | **TTL:** 1 Hour
   - **Type:** `A` | **Name:** `@` | **Value:** `185.199.111.153` | **TTL:** 1 Hour
3. **Add / Update the `CNAME` record for `www`**:
   - **Type:** `CNAME` | **Name:** `www` | **Value:** `<YOUR-GITHUB-USERNAME>.github.io.` | **TTL:** 1 Hour

---

### Step 4: Automated Depop Sync
The repository includes `.github/workflows/deploy-and-sync.yml` which automatically:
- Checks `@strictly_thriftee` every 15 minutes.
- Ingests new items, updates prices, and marks sold items with your on-brand "SOLD" stamp.
- Deploys the latest live inventory instantly.
