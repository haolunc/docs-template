#!/usr/bin/env bash
# Screenshot local HTML pages (built documentation) in headless Chromium, as a browser shows them:
#   bash tools/screenshot/screenshot.sh OUTDIR [--width PIXELS] PAGE.html[#ANCHOR]...
# Each page becomes OUTDIR/<path with / as _>.png: the full page, or with #ANCHOR the one 1000-pixel screen at that
# heading (_ANCHOR in the name); a width under 800 (phones: 390) adds -mobile. One line per page reports its
# JavaScript errors and whether it scrolls sideways; the exit status is 1 when any page has either.
# Playwright comes from .browser/ at the repository's root, installed by tools/screenshot/setup.sh.
set -euo pipefail
if [[ $# -lt 2 ]]; then
    sed -n '2,7p' "$0" >&2
    exit 2
fi
here=$(dirname "${BASH_SOURCE[0]}")
install=$(dirname "$(git -C "$here" rev-parse --path-format=absolute --git-common-dir)")/.browser
if [[ ! -d $install/node_modules/playwright ]]; then
    echo "no browser in $install: run bash tools/screenshot/setup.sh" >&2
    exit 2
fi
PW=$install/node_modules/playwright PLAYWRIGHT_BROWSERS_PATH=$install/browsers exec node "$here/screenshot.cjs" "$@"
