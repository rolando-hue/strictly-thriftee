#!/usr/bin/env bash
# Revert Strictly_Thriftee branding back to the original primary logo
# Scheduled for: December 29th

set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Reverting strictlythriftee.com to original primary branding..."

# Update index.html hero logo back to original primary logo
sed -i '' 's|src="./assets/strictly-thriftee-christmas[^"]*" width="[0-9]*" height="[0-9]*"|src="./assets/strictly-thriftee-logo.png" width="1536" height="1024"|g' "$DIR/index.html"

echo "✅ Branding successfully reverted to original primary logo (assets/strictly-thriftee-logo.png)."
