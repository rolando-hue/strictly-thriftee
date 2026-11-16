# Strictly Thriftee Project Rules

## Depop Storefront Sync & Inspection
- **Cloudflare Edge Protection**: Depop (`www.depop.com` and `webapi.depop.com`) enforces Cloudflare anti-bot management. CLI HTTP requests (curl, python, node) will fail with HTTP 403 Forbidden. Do not attempt direct script scraping against Depop.
- **Hub Window Browser Subagent**: Always use the browser subagent in the user's open Antigravity Hub window to inspect `https://www.depop.com/strictly_thriftee/`.
- **Git Push Operations**: Repository writes and git network operations (rebase/pull/push) require elevated permissions (`BypassSandbox: true`). Always pull/rebase before pushing to avoid conflicts with automated cron sync commits from GitHub Actions.
