from html.parser import HTMLParser
from pathlib import Path

import pytest

SITE = Path(__file__).parent.parent / "site"
IDS = ["hero", "dich-vu", "cach-lam", "lien-he"]
PAIRED = ["section", "main", "header", "footer"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = None
        self.metas = []
        self.title = ""
        self.opens = {}
        self.closes = {}
        self.section_ids = []
        self.hrefs = []
        self.h1 = 0
        self.scripts = 0
        self.text = []
        self.section_text = []  # list of [id, text]
        self._stack = []
        self._in_title = False
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.opens[tag] = self.opens.get(tag, 0) + 1
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1 += 1
        elif tag == "script":
            self.scripts += 1
        elif tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        elif tag == "section":
            self.section_ids.append(a.get("id"))
            self.section_text.append([a.get("id"), ""])
        if tag in ("style", "script"):
            self._skip += 1

    def handle_endtag(self, tag):
        self.closes[tag] = self.closes.get(tag, 0) + 1
        if tag == "title":
            self._in_title = False
        if tag in ("style", "script"):
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._skip:
            return
        if not self._in_title:
            self.text.append(data)
        if self.opens.get("section", 0) > self.closes.get("section", 0):
            self.section_text[-1][1] += data


def parse(src):
    p = Page()
    p.feed(src)
    p.close()
    return p


def has_sections(src):
    return all(i in parse(src).section_ids for i in IDS)


@pytest.fixture(scope="module")
def src():
    return (SITE / "index.html").read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def page(src):
    return parse(src)


def test_head_meta(src, page):
    assert src.lstrip().lower().startswith("<!doctype html>")
    assert page.lang == "vi"
    assert any(m.get("charset") for m in page.metas)
    assert any(m.get("name") == "viewport" and m.get("content") for m in page.metas)
    assert any(m.get("name") == "description" and m.get("content", "").strip() for m in page.metas)
    assert page.title.strip()


def test_single_h1(page):
    assert page.h1 == 1


def test_four_sections(src):
    assert has_sections(src)


def test_sections_negative_cases():
    in_comment = '<!-- <section id="hero"> --><section id="dich-vu"></section>'
    in_div = "".join(f'<div id="{i}"></div>' for i in IDS)
    assert not has_sections(in_comment)
    assert not has_sections(in_div)
    assert not has_sections("")


def test_section_text_and_no_filler(src, page):
    assert len(page.section_text) >= 4
    for sid, text in page.section_text:
        assert len(" ".join(text.split())) >= 20, sid
    low = src.lower()
    for bad in ("lorem", "todo", "placeholder"):
        assert bad not in low


def test_mailto_and_name(page):
    assert any(h.startswith("mailto:") and len(h) > 7 for h in page.hrefs)
    assert "Lười Code Studio" in " ".join(page.text)


def test_balanced_tags(page):
    for t in PAIRED:
        assert page.opens.get(t, 0) >= 1, t
        assert page.opens.get(t, 0) == page.closes.get(t, 0), t


def test_balance_detects_unclosed():
    p = parse("<main><section id='hero'>x</main>")
    assert p.opens["section"] != p.closes.get("section", 0)


def stylesheet_hrefs(src):
    class L(HTMLParser):
        def __init__(self):
            super().__init__()
            self.found = []

        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == "link" and "stylesheet" in (a.get("rel") or "").lower().split():
                self.found.append(a.get("href"))

    p = L()
    p.feed(src)
    p.close()
    return p.found


def test_single_relative_stylesheet_exists(src):
    hrefs = stylesheet_hrefs(src)
    assert len(hrefs) == 1
    href = hrefs[0]
    assert href and "://" not in href and not href.startswith(("/", "//"))
    assert (SITE / href).is_file()


def test_stylesheet_link_detection_negative():
    assert stylesheet_hrefs("<p>no link</p>") == []
    assert stylesheet_hrefs('<link rel="icon" href="a.ico">') == []


def test_css_content():
    css = (SITE / "style.css").read_text(encoding="utf-8")
    assert "max-width" in css
    assert ":root" in css
