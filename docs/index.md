# Getting started

How to turn this template into the documentation of a new project.

## What it is

- Markdown pages in `docs/` become a static HTML site in `docs/_build/html/`.
- The site works offline: open `index.html` directly, no server needed.
- Every build checks all local links, anchors and CSS assets; a failed build keeps the last good site.

```text
docs/*.md ──build.py──► docs/_build/html/*.html
   │                        ▲
   ├─ navigation.json ──────┤  sections and page order
   ├─ site.json ────────────┤  site name and footer
   ├─ page.html ────────────┤  page layout
   └─ assets/ ──────────────┘  CSS, JS, KaTeX, fonts, SVGs
```

## Build

| Step | Command |
| --- | --- |
| Install | `pip install mistune==3.3.4` |
| Build | `python docs/build.py` |
| Preview | `python -m http.server 8000 --directory docs/_build/html` |
| Test | `python -m unittest discover -s tests` |

## Set the name

`docs/site.json` holds the name in the header, tab title and footer:

```json
{"name": "myproject", "tagline": "Theory, design, and development."}
```

## Add a page

1. Write `docs/<folder>/<page>.md`.
2. Add `"<folder>/<page>"` to a section in `docs/navigation.json`.
3. Rebuild.

Each page starts with a title line and a one-paragraph summary:

```text
# Page title

One-sentence summary, shown under the title and in search results.

## First section
```

- `##` and `###` headings fill the "On this page" list.
- The first section in `navigation.json` holds `index`, the home page.

## Links, math and diagrams

| Write | Result |
| --- | --- |
| `[text](other.md#heading)` | Link to a page, rewritten to `.html` |
| `[text](/folder/page)` | Link from the docs root |
| `$x^2$`, `$$ … $$` | Inline and display math (KaTeX) |
| `![alt](/assets/name.svg)` | SVG inlined, following the theme colors |

- SVGs use `var(--text)`, `var(--line)`, `var(--accent)`… as colors; see `assets/diagram.svg`.
- See the [samples](samples/markdown.md) for every element.

## Restyle

- Colors are CSS variables at the top of `assets/site.css`, for light and dark themes.
- Layout lives in `page.html`; the build fills its `${…}` fields.
