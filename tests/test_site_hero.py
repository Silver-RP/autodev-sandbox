import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

HTML = (Path(__file__).parent.parent / "site" / "index.html").read_text(encoding="utf-8")
PAGES = {
    "vi": HTML,
    "en": (Path(__file__).parent.parent / "site" / "en" / "index.html").read_text(encoding="utf-8"),
}
LANGS = list(PAGES)
DRAW = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}


class Hero(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_hero = False
        self.in_svg = 0
        self.svgs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section":
            self.in_hero = a.get("id") == "hero"
        if not self.in_hero:
            return
        if tag == "svg":
            self.svgs.append({"attrs": a, "draw": 0, "title": False})
            self.in_svg += 1
        elif self.in_svg and tag in DRAW:
            self.svgs[-1]["draw"] += 1
        elif self.in_svg and tag == "title":
            self.svgs[-1]["title"] = True

    def handle_endtag(self, tag):
        if tag == "svg" and self.in_hero:
            self.in_svg -= 1
        if tag == "section":
            self.in_hero = False


def hero_svgs(src=HTML):
    p = Hero()
    p.feed(src)
    return p.svgs


@pytest.mark.parametrize("lang", LANGS)
def test_hero_svg_structure(lang):
    svgs = hero_svgs(PAGES[lang])
    assert len(svgs) >= 1
    s = svgs[0]
    assert s["draw"] >= 3
    assert s["title"]
    assert s["attrs"].get("viewbox")  # HTMLParser hạ chữ thường tên thuộc tính


@pytest.mark.parametrize("lang", LANGS)
def test_hero_svg_no_wide_fixed_width(lang):
    for s in hero_svgs(PAGES[lang]):
        w = s["attrs"].get("width")
        if w and "%" not in w:
            m = re.match(r"\s*([\d.]+)", w)
            assert not (m and float(m.group(1)) > 360), w


def lien_he_svgs(src=HTML):
    m = re.search(r'<section id="lien-he">(.*?)</section>', src, re.DOTALL)
    if not m:
        return []
    return re.findall(r"<svg\b(.*?)</svg>", m.group(1), re.DOTALL)


@pytest.mark.parametrize("lang", LANGS)
def test_lien_he_empty_chair_svg(lang):
    svgs = lien_he_svgs(PAGES[lang])
    assert len(svgs) == 1
    s = svgs[0]
    assert len(re.findall(r"<(?:path|rect|circle|ellipse|line)\b", s)) >= 3
    assert "aria-hidden" in s or "<title" in s
    assert "viewBox" in s
    assert "stroke-width=\"2.5\"" in s
    assert "currentColor" in s and "#" not in s.replace("&#", "")
    assert "gradient" not in s.lower()
    w = re.search(r'\swidth="([\d.]+)"', s)
    assert not w or float(w.group(1)) <= 360
    css = (Path(__file__).parent.parent / "site" / "style.css").read_text(encoding="utf-8")
    assert re.search(r"#lien-he \.ghe-trong\s*\{[^}]*var\(--color-muc-bang\)", css)


def test_lien_he_svg_absent_cases():
    assert lien_he_svgs("") == []
    assert lien_he_svgs('<section id="lien-he"><p>x</p></section>') == []
    assert len(lien_he_svgs()) == len(lien_he_svgs())


def test_svg_outside_hero_not_counted_and_empty_input():
    assert hero_svgs("<section id='x'><svg viewBox='0 0 1 1'></svg></section>") == []
    assert hero_svgs("") == []
    # gọi lặp lại không rò trạng thái
    assert len(hero_svgs()) == len(hero_svgs())


# --- ca âm trên HTML bản Anh có lỗi (R15 dev-04) ---


def test_en_hero_svg_without_title_is_caught():
    bad = re.sub(r"<title[^>]*>.*?</title>", "", PAGES["en"], flags=re.DOTALL)
    assert not hero_svgs(bad)[0]["title"]


def test_en_hero_svg_with_too_few_shapes_is_caught():
    bad = re.sub(r"<(?:path|rect|circle|ellipse|line)\b[^>]*/>", "", PAGES["en"])
    assert hero_svgs(bad)[0]["draw"] < 3


def test_en_empty_chair_with_hex_paint_is_caught():
    bad = PAGES["en"].replace('class="ghe-trong"', 'class="ghe-trong" stroke="#ff0000"', 1)
    svgs = lien_he_svgs(bad)
    assert len(svgs) == 1 and "#" in svgs[0]
