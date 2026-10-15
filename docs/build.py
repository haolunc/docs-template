"""Small static documentation builder: Markdown in, portable HTML out."""
from __future__ import annotations

import html
import json
import posixpath
import re
import shutil
import tempfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from string import Template
from urllib.parse import unquote, urlsplit

import mistune

ROOT = Path(__file__).resolve().parent


@dataclass
class Page:
    slug: str
    section: str
    title: str
    description: str
    body: str


def load_site(source: Path) -> dict[str, str]:
    """Site-wide settings from site.json; every key is optional."""
    path = source / 'site.json'
    settings = json.loads(path.read_text()) if path.exists() else {}
    return {'name': settings.get('name', 'Docs'), 'tagline': settings.get('tagline', '')}


def load_pages(source: Path) -> tuple[list[dict], list[Page]]:
    sections = json.loads((source / 'navigation.json').read_text())
    pages = []
    seen = set()
    for section in sections:
        for slug in section['pages']:
            if slug in seen or '..' in Path(slug).parts or slug.startswith('/'):
                raise ValueError(f'Invalid or duplicate page: {slug}')
            seen.add(slug)
            text = (source / f'{slug}.md').read_text()
            heading, _, rest = text.partition('\n')
            if not heading.startswith('# '):
                raise ValueError(f'{slug}: first line must be a title beginning with #')
            description, _, body = rest.strip().partition('\n\n')
            pages.append(Page(slug, section['title'], heading[2:].strip(),
                              description.replace('\n', ' '), body))
    return sections, pages


def relative_url(page: str, target: str) -> str:
    return posixpath.relpath(target, posixpath.dirname(page) or '.')


class Renderer(mistune.HTMLRenderer):
    def __init__(self, source: Path, page: Page, slugs: set[str]):
        super().__init__(escape=True)
        self.source, self.page, self.slugs = source, page, slugs
        self.headings: list[tuple[int, str, str]] = []
        self.ids: set[str] = set()

    def heading(self, text: str, level: int, **attrs) -> str:
        label = html.unescape(re.sub(r'<[^>]+>', '', text))
        base = re.sub(r'[^\w\s-]', '', label.lower())
        base = re.sub(r'[\s_]+', '-', base).strip('-') or 'section'
        anchor, suffix = base, 2
        while anchor in self.ids:
            anchor, suffix = f'{base}-{suffix}', suffix + 1
        self.ids.add(anchor)
        if level in (2, 3):
            self.headings.append((level, anchor, label))
        return (f'<h{level} id="{anchor}">{text}'
                f'<a class="heading-anchor" href="#{anchor}" '
                f'aria-label="Link to {html.escape(label, quote=True)}">#</a></h{level}>\n')

    def local_url(self, url: str) -> str:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return url
        if parsed.path.startswith('/'):
            path = parsed.path.lstrip('/')
        else:
            path = posixpath.normpath(posixpath.join(posixpath.dirname(self.page.slug), parsed.path))
        slug = path[:-3] if path.endswith('.md') else path
        if slug in self.slugs:
            path = slug + '.html'
        target = relative_url(self.page.slug, path)
        if parsed.query:
            target += '?' + parsed.query
        if parsed.fragment:
            target += '#' + parsed.fragment
        return target

    def link(self, text: str, url: str, title: str | None = None) -> str:
        return super().link(text, self.local_url(url), title)

    def image(self, text: str, url: str, title: str | None = None) -> str:
        # Repository-owned SVGs are inline so typography and theme colors inherit.
        if url.startswith('/assets/') and url.endswith('.svg'):
            path = (self.source / url.lstrip('/')).resolve()
            if not path.is_relative_to((self.source / 'assets').resolve()):
                raise ValueError(f'Image outside assets: {url}')
            svg = path.read_text()
            label = html.unescape(re.sub(r'<[^>]+>', '', text))
            return f'<span class="diagram" role="img" aria-label="{html.escape(label, quote=True)}">{svg}</span>'
        return super().image(text, self.local_url(url), title)


def render_body(source: Path, page: Page, slugs: set[str]) -> tuple[str, list]:
    renderer = Renderer(source, page, slugs)
    markdown = mistune.create_markdown(renderer=renderer, plugins=['table', 'math'])
    renderer.register('table', lambda _, text: f'<div class="table-wrap"><table>{text}</table></div>')
    renderer.register('inline_math', lambda _, text:
                      f'<span class="math" data-display="false">{html.escape(text)}</span>')
    renderer.register('block_math', lambda _, text:
                      f'<div class="math" data-display="true">{html.escape(text)}</div>\n')
    return markdown(page.body), renderer.headings


def nav_link(page: Page, target: Page, *, section: bool = False) -> str:
    active = page.section == target.section if section else page.slug == target.slug
    label = target.section if section else target.title
    current = ' aria-current="page"' if active else ''
    return (f'<a href="{relative_url(page.slug, target.slug + ".html")}"{current}>'
            f'{html.escape(label)}</a>')


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for attr in ('href', 'src'):
            if attrs.get(attr):
                self.refs.append(attrs[attr])


def validate_output(output: Path) -> None:
    documents = {}
    for path in output.rglob('*.html'):
        links = Links()
        links.feed(path.read_text())
        documents[path.resolve()] = links
    for path, links in documents.items():
        for ref in links.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if not target.is_relative_to(output.resolve()) or not target.is_file():
                raise ValueError(f'{path.name}: broken local reference {ref}')
            if url.fragment and target in documents and unquote(url.fragment) not in documents[target].ids:
                raise ValueError(f'{path.name}: missing anchor {ref}')
    for path in output.rglob('*.css'):
        for ref in re.findall(r'url\([\"\']?([^\)\"\']+)', path.read_text()):
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.is_relative_to(output.resolve()) or not target.is_file():
                raise ValueError(f'{path.name}: broken CSS asset {ref}')


def build(source: Path, output: Path) -> int:
    site = load_site(source)
    sections, pages = load_pages(source)
    by_slug = {p.slug: p for p in pages}
    template = Template((source / 'page.html').read_text())
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='docs-', dir=output.parent) as temporary:
        staging = Path(temporary) / 'html'
        staging.mkdir()
        shutil.copytree(source / 'assets', staging / 'assets')
        for index, page in enumerate(pages):
            body, headings = render_body(source, page, set(by_slug))
            topnav = ''.join(nav_link(page, by_slug[s['pages'][0]], section=True) for s in sections)
            sidebar = ''.join(nav_link(page, p) for p in pages if p.section == page.section)
            toc = ''.join(f'<a class="toc-level-{level}" href="#{anchor}">{html.escape(label)}</a>'
                          for level, anchor, label in headings)
            neighbors = []
            for offset, label in ((-1, 'Previous'), (1, 'Next')):
                if 0 <= index + offset < len(pages):
                    target = pages[index + offset]
                    neighbors.append(f'<a class="{label.lower()}" href="{relative_url(page.slug, target.slug + ".html")}">'
                                     f'<span>{label}</span>{html.escape(target.title)}</a>')
            page_html = template.substitute(
                title=html.escape(page.title), description=html.escape(page.description, quote=True),
                section=html.escape(page.section), home=relative_url(page.slug, 'index.html'),
                assets=relative_url(page.slug, 'assets'), topnav=topnav, sidebar=sidebar,
                body=body, toc=toc, neighbors=''.join(neighbors),
                toc_hidden='' if headings else ' hidden',
                site=html.escape(site['name']), tagline=html.escape(site['tagline']),
            )
            target = staging / f'{page.slug}.html'
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page_html)
        validate_output(staging)
        # A failed render/check leaves the previous successful build intact.
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
    return len(pages)


if __name__ == '__main__':
    output = ROOT / '_build/html'
    count = build(ROOT, output)
    print(f'Built and checked {count} pages: {output / "index.html"}')
