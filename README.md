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
