import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent.parent / "site"
HTML = (SITE / "index.html").read_text(encoding="utf-8")
PAGES = {"vi": HTML, "en": (SITE / "en" / "index.html").read_text(encoding="utf-8")}
LANGS = list(PAGES)
CSS = (SITE / "style.css").read_text(encoding="utf-8")


class Tree(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.svgs = []  # dict(attrs, has_title)
        self.headings = []
        self.names = []  # (tag, attrs, text)
        self.svg_cur = None
        self.in_title = False
        self.cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "svg":
            self.svg_cur = {"attrs": a, "title": False}
            self.svgs.append(self.svg_cur)
        elif tag == "title" and self.svg_cur is not None:
            self.svg_cur["title"] = True
        elif re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        elif tag in ("a", "button"):
            self.cur = {"tag": tag, "attrs": a, "text": ""}
            self.names.append(self.cur)

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg_cur = None
        elif tag in ("a", "button"):
            self.cur = None

    def handle_data(self, data):
        if self.cur is not None:
            self.cur["text"] += data


def parse(html=HTML):
    t = Tree()
    t.feed(html)
    return t


def strip_comments(css):
    return re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)


def rules(css):
    return re.findall(r"([^{}]+)\{([^{}]*)\}", strip_comments(css))


def outline_removed(css):
    return [
        sel.strip()
        for sel, body in rules(css)
        if re.search(r"outline\s*:\s*(none|0)\b(?!\.)", body)
        or re.search(r"outline-style\s*:\s*none", body)
    ]


def check_outline(css):
    bad = outline_removed(css)
    has_fv = any(
        ":focus-visible" in s and re.search(r"outline\s*:\s*[^;]*\d+px", b)
        for s, b in rules(css)
    )
    return bad, has_fv


def check_headings(levels):
    prev = 0
    for lv in levels:
        if lv > prev + 1:
            return False
        prev = lv
    return bool(levels) and levels[0] == 1


def svg_ok(s):
    a = s["attrs"]
    return a.get("aria-hidden") == "true" or (a.get("role") == "img" and s["title"])


def name_ok(n):
    a = n["attrs"]
    return bool(
        n["text"].strip() or a.get("aria-label", "").strip() or a.get("title", "").strip()
    )


def test_focus_visible_cho_link_va_nut():
    _bad, has_fv = check_outline(CSS)
    assert has_fv
    sels = " ".join(s for s, _ in rules(CSS) if ":focus-visible" in s)
    assert "a:focus-visible" in sels and "button:focus-visible" in sels


def test_khong_go_outline_neu_thieu_focus_visible():
    bad, has_fv = check_outline(CSS)
    assert not bad or has_fv


def test_bo_kiem_outline_bat_loi():
    assert check_outline("a{outline:none}")[0] == ["a"]
    assert check_outline("a{outline:0}")[0] == ["a"]
    assert check_outline("a:focus-visible{outline:3px solid red}") == ([], True)


@pytest.mark.parametrize("lang", LANGS)
def test_moi_svg_co_aria_hidden_hoac_role_img_title(lang):
    svgs = parse(PAGES[lang]).svgs
    assert len(svgs) >= 5
    assert all(svg_ok(s) for s in svgs)
    assert not svg_ok({"attrs": {"role": "img"}, "title": False})
    assert not svg_ok({"attrs": {}, "title": True})


@pytest.mark.parametrize("lang", LANGS)
def test_heading_khong_nhay_cap(lang):
    levels = parse(PAGES[lang]).headings
    assert levels and levels[0] == 1
    assert check_headings(levels)
    assert not check_headings([1, 3])
    assert not check_headings([2, 3])
    assert check_headings([1, 2, 3, 2, 3])


@pytest.mark.parametrize("lang", LANGS)
def test_link_va_nut_co_ten_doc_duoc(lang):
    names = parse(PAGES[lang]).names
    assert any(n["tag"] == "a" for n in names)
    assert any(n["tag"] == "button" for n in names)
    assert all(name_ok(n) for n in names)
    assert not name_ok({"tag": "a", "attrs": {}, "text": " "})
    assert name_ok({"tag": "a", "attrs": {"aria-label": "x"}, "text": ""})


# --- ca âm trên HTML bản Anh có lỗi (R15 dev-04) ---


def test_en_svg_thieu_aria_hidden_bi_bat():
    bad = PAGES["en"].replace(' aria-hidden="true"', "")
    svgs = parse(bad).svgs
    assert svgs and not all(svg_ok(s) for s in svgs)


def test_en_svg_hero_thieu_title_bi_bat():
    bad = re.sub(r"<title[^>]*>.*?</title>", "", PAGES["en"], flags=re.DOTALL)
    svgs = parse(bad).svgs
    assert not all(svg_ok(s) for s in svgs)


def test_en_heading_nhay_cap_bi_bat():
    bad = PAGES["en"].replace("<h2>", "<h4>").replace("</h2>", "</h4>")
    assert not check_headings(parse(bad).headings)


def test_en_link_khong_ten_bi_bat():
    bad = PAGES["en"].replace("Email me</a>", "</a>")
    assert not all(name_ok(n) for n in parse(bad).names)
