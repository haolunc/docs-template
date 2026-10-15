#!/usr/bin/env bash
# Install Playwright and its headless Chromium shell for tools/screenshot/screenshot.sh (needs network and
# Node.js 18+; on a Mac, `brew install node`):
#   bash tools/screenshot/setup.sh
# Both go to .browser/ at the repository's root (git-ignored), shared by all its worktrees. Running it again keeps
# what is already installed.
set -euo pipefail
playwright_version=1.63.0
common_dir=$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --path-format=absolute --git-common-dir)
install=$(dirname "$common_dir")/.browser
mkdir -p "$install"
npm install --silent --no-audit --no-fund --prefix "$install" "playwright@$playwright_version"
PLAYWRIGHT_BROWSERS_PATH=$install/browsers "$install/node_modules/.bin/playwright" install chromium-headless-shell
echo "installed Playwright $playwright_version and headless Chromium in $install"
