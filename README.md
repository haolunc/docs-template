# docs-template

A small static documentation framework: Markdown in, portable HTML out.

- One Python file (`docs/build.py`), one dependency (`mistune`).
- Offline site: math (KaTeX), fonts and scripts are bundled; open `index.html` directly.
- Light and dark themes, sidebar, section tabs, "On this page" list, mobile menu.
- Every build checks local links, heading anchors and CSS assets; a failed build keeps the last good site.

## Use it

```bash
pip install mistune==3.3.4
python docs/build.py
python -m http.server 8000 --directory docs/_build/html
```

Open <http://localhost:8000>, or `docs/_build/html/index.html` without a server.
Run the builder tests with `python -m unittest discover -s tests`.

## Start a new project

1. Copy `docs/` (and `tests/test_docs.py` if you want the checks) into the project.
2. Set the name in `docs/site.json`.
3. Replace the pages and `docs/navigation.json`; keep `docs/samples/` as a reference or delete it.
4. Add `docs/_build/` to `.gitignore`.

The built site's "Getting started" page (`docs/index.md`) covers pages, links, math, diagrams and styling.
`AGENTS.md` holds the writing rules for people and coding agents.

## Check pages in a browser

`tools/screenshot/` screenshots built pages in headless Chromium (Playwright), on Linux or macOS.
It needs Node.js 18+ (on a Mac, `brew install node`); the first install downloads about 300 MB into `.browser/`.

```bash
bash tools/screenshot/setup.sh
bash tools/screenshot/screenshot.sh docs/_build/screenshots docs/_build/html/index.html
```

- `page.html#heading` shoots one screen at that heading; `--width 390` before the pages shoots a phone.
- Each page prints `ok`, its JavaScript errors, or `OVERFLOW` if it scrolls sideways.
- `.claude/skills/page-screenshots/` teaches Claude Code to do this after docs changes; copy it with `tools/screenshot/`.

## Layout

| Path | Role |
| --- | --- |
| `docs/build.py` | Builder and link checker |
| `docs/page.html` | Page layout, filled by the builder |
| `docs/site.json` | Site name and footer tagline |
| `docs/navigation.json` | Sections and page order |
| `docs/assets/` | CSS, JS, sample SVG, KaTeX 0.16.47 (MIT), Inter font (OFL 1.1) |
| `docs/samples/` | One page per element: text, math, code, diagram |
| `tests/test_docs.py` | Builder tests |
| `tools/screenshot/` | Browser screenshots of built pages |
| `.claude/skills/page-screenshots/` | Claude Code skill for the screenshots |
