import re
from html.parser import HTMLParser
from pathlib import Path

HTML = (Path(__file__).parent.parent / "site" / "index.html").read_text(encoding="utf-8")
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


def test_hero_svg_structure():
    svgs = hero_svgs()
    assert len(svgs) >= 1
    s = svgs[0]
    assert s["draw"] >= 3
    assert s["title"]
    assert s["attrs"].get("viewbox")  # HTMLParser hạ chữ thường tên thuộc tính


def test_hero_svg_no_wide_fixed_width():
    for s in hero_svgs():
        w = s["attrs"].get("width")
        if w and "%" not in w:
            m = re.match(r"\s*([\d.]+)", w)
            assert not (m and float(m.group(1)) > 360), w


def test_svg_outside_hero_not_counted_and_empty_input():
    assert hero_svgs("<section id='x'><svg viewBox='0 0 1 1'></svg></section>") == []
    assert hero_svgs("") == []
    # gọi lặp lại không rò trạng thái
    assert len(hero_svgs()) == len(hero_svgs())
