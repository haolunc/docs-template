"""Regression checks for portable documentation and failure handling."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from docs import build as build_docs


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.source = Path(self.temporary.name) / 'docs'
        self.source.mkdir()
        self.output = Path(self.temporary.name) / 'site'
        shutil.copyfile(ROOT / 'docs/page.html', self.source / 'page.html')
        for name in ['site.css', 'site.js', 'katex/katex.min.css', 'katex/katex.min.js']:
            path = self.source / 'assets' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('')
        (self.source / 'navigation.json').write_text(json.dumps([
            {'title': 'Guide', 'pages': ['index', 'nested/page']},
        ]))
        (self.source / 'index.md').write_text(
            '# Overview\n\nSummary.\n\n[Details](/nested/page#details)\n'
            '[Markdown](nested/page.md?view=full#details)\n')
        (self.source / 'nested').mkdir()
        self.page = self.source / 'nested/page.md'
        self.page.write_text('# A page\n\nSummary.\n\n## Details\n\n[Home](../index.md)\n[Here](#details)\n')

    def test_local_links_use_relative_html_paths(self):
        build_docs.build(self.source, self.output)
        text = (self.output / 'nested/page.html').read_text()
        self.assertIn('<a href="../index.html">Home</a>', text)
        self.assertIn('<a href="#details">Here</a>', text)
        self.assertIn('href="../assets/site.css"', text)
        home = (self.output / 'index.html').read_text()
        self.assertIn('<a href="nested/page.html#details">Details</a>', home)
        self.assertIn('<a href="nested/page.html?view=full#details">Markdown</a>', home)

    def test_failed_build_preserves_last_good_output(self):
        def snapshot():
            return {path.relative_to(self.output): path.read_bytes()
                    for path in self.output.rglob('*') if path.is_file()}

        build_docs.build(self.source, self.output)
        previous = snapshot()
        (self.source / 'assets/site.css').write_text('body { color: red; }')
        for body, error in (
            ('[Missing](/absent)', ValueError),
            ('![Missing](/assets/missing.svg)', FileNotFoundError),
        ):
            with self.subTest(body=body):
                self.page.write_text(f'# Changed page\n\nSummary.\n\n## Details\n\n{body}\n')
                with self.assertRaises(error):
                    build_docs.build(self.source, self.output)
                self.assertEqual(previous, snapshot())

    def test_missing_heading_anchor_is_rejected(self):
        self.page.write_text('# Page\n\nSummary.\n\n## Renamed\n')
        with self.assertRaisesRegex(ValueError, 'missing anchor'):
            build_docs.build(self.source, self.output)

    def test_math_is_preserved_but_code_is_not_rendered_as_math(self):
        page = build_docs.Page('index', 'Guide', 'Title', 'Summary',
                              '$x < y$\n\n$$\n\\frac{a}{b}\n$$\n\n```text\n$x$\n```\n')
        text, _ = build_docs.render_body(self.source, page, {'index'})
        self.assertEqual(text.count('class="math"'), 2)
        self.assertIn('<span class="math" data-display="false">x &lt; y</span>', text)
        self.assertIn('<div class="math" data-display="true">\\frac{a}{b}</div>', text)
        self.assertIn('<code class="language-text">$x$', text)

    def test_duplicate_headings_have_distinct_targets(self):
        page = build_docs.Page('index', 'Guide', 'Title', 'Summary', '## Notes\n\n## Notes\n')
        text, headings = build_docs.render_body(self.source, page, {'index'})
        self.assertEqual([h[1] for h in headings], ['notes', 'notes-2'])
        for anchor in ('notes', 'notes-2'):
            self.assertIn(f'<h2 id="{anchor}">Notes', text)
            self.assertIn(f'href="#{anchor}"', text)

    def test_svg_is_inlined_with_accessible_label(self):
        (self.source / 'assets/example.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg"><text>Example</text></svg>')
        with self.page.open('a') as page:
            page.write('\n![**A** & "B"](/assets/example.svg)\n')
        build_docs.build(self.source, self.output)
        text = (self.output / 'nested/page.html').read_text()
        self.assertIn('role="img" aria-label="A &amp; &quot;B&quot;"><svg ', text)
        self.assertIn('<text>Example</text></svg>', text)

    def test_site_name_comes_from_settings(self):
        build_docs.build(self.source, self.output)
        self.assertIn('<title>Overview · Docs</title>', (self.output / 'index.html').read_text())
        (self.source / 'site.json').write_text(json.dumps({'name': 'A & B', 'tagline': 'Notes.'}))
        build_docs.build(self.source, self.output)
        text = (self.output / 'index.html').read_text()
        self.assertIn('<title>Overview · A &amp; B</title>', text)
        self.assertIn('A &amp; B documentation <span>·</span> Notes.', text)

    def test_missing_local_font_is_rejected(self):
        (self.source / 'assets/site.css').write_text('@font-face{src:url(missing.woff2)}')
        with self.assertRaisesRegex(ValueError, 'broken CSS asset'):
            build_docs.build(self.source, self.output)


if __name__ == '__main__':
    unittest.main()
