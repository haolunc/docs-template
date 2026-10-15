# Documentation rules

- Rebuild after every docs change (`python docs/build.py`); the build must pass its link and anchor checks.

- Short, structured pages: one topic per page, with a heading every screen or so. Split a page before it passes about 400 lines (at about 80 columns); a long subject becomes a group of pages with an overview page.

- Show rather than narrate: equations, code snippets, tables and small flowcharts (a `text` block, or an SVG in `docs/assets/` linked as `![alt](/assets/<name>.svg)` and colored like `docs/assets/diagram.svg`) carry the content. Prose is mostly short bullets; no paragraph or bullet runs past two or three sentences.

- Docs are tutorials, not outlines: derive every result step by step, showing the intermediate algebra, one display per step with a short bullet on what changed, and add worked examples. Do not state only the key formulas.

- Define notation at first use on each page, or link to a notation table.

- Every page starts with `# Title`, then a one-paragraph summary, then `##` sections; list it in `docs/navigation.json`.
