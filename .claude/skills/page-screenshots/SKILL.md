---
name: page-screenshots
description: See how the built HTML documentation (docs/_build/html) looks in a browser, by screenshotting it in headless Chromium and reading the PNGs. Use after building or changing docs, to check layout, math, diagrams, mobile width or JavaScript errors, or when the owner asks to see a page.
---

# Page screenshots

Playwright drives a headless Chromium on Linux or macOS; no display or server is needed.

| Piece | Where |
|---|---|
| Screenshot command | `tools/screenshot/screenshot.sh` (calls `tools/screenshot/screenshot.cjs`) |
| Install (Playwright 1.63.0, Chromium shell) | `.browser/` at the repository's root, git-ignored, shared by all worktrees |
| First install or reinstall | `bash tools/screenshot/setup.sh` (needs network and Node.js 18+) |

## Take them

1. Build what you check: `python docs/build.py`.
2. Screenshot from the repository root into `docs/_build/screenshots/` (git-ignored with the build):

```bash
bash tools/screenshot/screenshot.sh docs/_build/screenshots \
  docs/_build/html/index.html docs/_build/html/samples/math.html#display-math
```

- Each page is one PNG named after its path (`samples_math_display-math.png`).
- Without `#anchor`: the full page at 1440 px wide. With `#anchor` (a heading's `id`): one 1440×1000 screen at that heading.
- `--width 390` before the pages: a phone, named `-mobile`.
- It takes a few seconds per page.

## Read them

- Each line prints the PNG path, `ok` or the page's JavaScript errors, and `OVERFLOW` when the page scrolls sideways; the exit status is 1 if any page has either.
- Look at each PNG with the Read tool. A full page taller than about 3000 px is shrunk to fit and small text blurs: take `#anchor` shots of the sections that matter.
- Check what a reader would: math rendered (not raw `$...$`), diagrams drawn, navigation and the table of contents, no clipped tables or code, and both widths for layout changes.

## Show them

- Send the PNGs the owner should see (one caption line on what to look at).
- Screenshots are scratch: never commit them.
