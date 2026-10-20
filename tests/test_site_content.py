import re
from html.parser import HTMLParser
from pathlib import Path

import pytest

SITE = Path(__file__).parent.parent / "site"
HTML = (SITE / "index.html").read_text(encoding="utf-8")
CSS = (SITE / "style.css").read_text(encoding="utf-8")
VERBS = ("Gửi", "Nhắn", "Viết")

# Giá trị phụ thuộc ngôn ngữ: theo trang, không nới điều kiện.
LANG = {
    "vi": {
        "html": HTML,
        "verbs": VERBS,
        "example": "ví dụ",
        "banned": ("khách hàng nói", "đánh giá", "testimonial"),
    },
    "en": {
        "html": (SITE / "en" / "index.html").read_text(encoding="utf-8"),
        "verbs": ("Email", "Write", "Message", "Send"),
        "example": "example",
        "banned": ("customers say", "what clients say", "reviews", "testimonial"),
    },
}
LANGS = list(LANG)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.section = None
        self.cur = None
        self.mailto = []  # (section, text)
        self.text = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section":
            self.section = a.get("id")
        elif tag == "a" and (a.get("href") or "").startswith("mailto:"):
            self.cur = [self.section, ""]
        if tag in ("style", "script"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "section":
            self.section = None
        elif tag == "a" and self.cur:
            self.mailto.append((self.cur[0], " ".join(self.cur[1].split())))
            self.cur = None
        if tag in ("style", "script"):
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        self.text.append(data)
        if self.cur:
            self.cur[1] += data


def parse(src):
    p = Links()
    p.feed(src)
    p.close()
    return p


@pytest.mark.parametrize("lang", LANGS)
def test_mailto_buttons_hero_and_contact_start_with_verb(lang):
    links = parse(LANG[lang]["html"]).mailto
    assert len(links) >= 2
    sections = {s for s, _ in links}
    assert {"hero", "lien-he"} <= sections
    for _, text in links:
        assert text.startswith(LANG[lang]["verbs"]), text


def test_mailto_detection_negative():
    assert parse("<p>không có link</p>").mailto == []
    assert parse('<a href="https://x.vn">Gửi</a>').mailto == []


@pytest.mark.parametrize("lang", LANGS)
def test_no_arrow_in_visible_text(lang):
    assert "→" not in "".join(parse(LANG[lang]["html"]).text)


def test_no_uppercase_transform_in_css():
    assert not re.search(r"text-transform\s*:\s*uppercase", CSS, re.IGNORECASE)


class Faq(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_faq = False
        self.items = []  # [summary_text, body_text]
        self.cur = None
        self.in_summary = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section":
            self.in_faq = a.get("id") == "hoi-dap"
        elif self.in_faq and tag == "details":
            self.cur = ["", ""]
            self.items.append(self.cur)
        elif self.in_faq and tag == "summary":
            self.in_summary = True

    def handle_endtag(self, tag):
        if tag == "summary":
            self.in_summary = False
        elif tag == "details":
            self.cur = None
        elif tag == "section":
            self.in_faq = False

    def handle_data(self, data):
        if self.cur is None:
            return
        self.cur[0 if self.in_summary else 1] += data


def faq(src):
    p = Faq()
    p.feed(src)
    p.close()
    return [(" ".join(s.split()), " ".join(b.split())) for s, b in p.items]


@pytest.mark.parametrize("lang", LANGS)
def test_faq_has_at_least_four_details_with_summary_and_body(lang):
    items = faq(LANG[lang]["html"])
    assert len(items) >= 4
    for q, a in items:
        assert q, "summary rỗng"
        assert len(a) >= 30, (q, a)


def test_faq_parser_negative():
    assert faq("<section id='x'><details><summary>a</summary>b</details></section>") == []
    got = faq("<section id='hoi-dap'><details><summary>a</summary>bb</details></section>")
    assert got == [("a", "bb")]
    assert faq("<section id='hoi-dap'><details><summary></summary>bb</details></section>")[0][0] == ""


@pytest.mark.parametrize("lang", LANGS)
def test_faq_is_between_cach_lam_and_lien_he(lang):
    ids = re.findall(r'<section id="([^"]+)"', LANG[lang]["html"])
    assert ids.index("cach-lam") < ids.index("hoi-dap") < ids.index("lien-he")


DRAW = {"path", "circle", "rect", "line", "polyline", "polygon", "ellipse"}


class Projects(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_sec = False
        self.items = []  # dict(text, svgs=[dict(draw, hidden, title)])
        self.cur = None
        self.svg = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section":
            self.in_sec = a.get("id") == "du-an"
        elif self.in_sec and tag == "article":
            self.cur = {"text": "", "svgs": []}
            self.items.append(self.cur)
        elif self.cur is not None and tag == "svg":
            self.svg = {"draw": 0, "hidden": a.get("aria-hidden") == "true", "title": False}
            self.cur["svgs"].append(self.svg)
        elif self.svg is not None and tag == "title":
            self.svg["title"] = True
        elif self.svg is not None and tag in DRAW:
            self.svg["draw"] += 1

    def handle_endtag(self, tag):
        if tag == "svg":
            self.svg = None
        elif tag == "article":
            self.cur = None
        elif tag == "section":
            self.in_sec = False

    def handle_data(self, data):
        if self.cur is not None:
            self.cur["text"] += data


def projects(src):
    p = Projects()
    p.feed(src)
    p.close()
    return p.items


@pytest.mark.parametrize("lang", LANGS)
def test_du_an_has_exactly_three_items_with_vi_du_and_svg(lang):
    items = projects(LANG[lang]["html"])
    assert len(items) == 3
    for it in items:
        assert LANG[lang]["example"] in it["text"].lower()
        good = [s for s in it["svgs"] if s["draw"] >= 3 and (s["hidden"] or s["title"])]
        assert good, it["text"]


@pytest.mark.parametrize("lang", LANGS)
def test_du_an_is_between_cach_lam_and_lien_he(lang):
    ids = re.findall(r'<section id="([^"]+)"', LANG[lang]["html"])
    assert ids.index("cach-lam") < ids.index("du-an") < ids.index("lien-he")


def test_projects_parser_negative():
    assert projects("<section id='x'><article>ví dụ</article></section>") == []
    got = projects("<section id='du-an'><article>a<svg><path/></svg></article></section>")
    assert len(got) == 1 and "ví dụ" not in got[0]["text"] and got[0]["svgs"][0]["draw"] == 1


@pytest.mark.parametrize("lang", LANGS)
def test_no_fake_praise_words_anywhere(lang):
    low = LANG[lang]["html"].lower()
    for w in LANG[lang]["banned"]:
        assert w not in low, w


def test_css_does_not_hide_summary():
    for m in re.finditer(r"([^{}]*summary[^{}]*)\{([^}]*)\}", CSS):
        body = m.group(2)
        assert not re.search(r"display\s*:\s*none|visibility\s*:\s*hidden", body), m.group(0)


# --- ca âm trên HTML bản Anh có lỗi (R15 dev-04) ---


def test_en_mailto_not_starting_with_verb_is_caught():
    bad = LANG["en"]["html"].replace(">Email me</a>", ">Contact</a>")
    texts = [t for _, t in parse(bad).mailto]
    assert texts and not all(t.startswith(LANG["en"]["verbs"]) for t in texts)


def test_en_faq_details_without_summary_is_caught():
    bad = re.sub(r"<summary>.*?</summary>", "<summary></summary>", LANG["en"]["html"])
    assert any(not q for q, _ in faq(bad))


def test_en_project_without_example_marker_is_caught():
    bad = LANG["en"]["html"].replace("(example)", "")
    items = projects(bad)
    assert any(LANG["en"]["example"] not in it["text"].lower() for it in items)


def test_en_fake_praise_is_caught():
    bad = LANG["en"]["html"].replace("<h2>Drop by</h2>", "<h2>What customers say</h2>")
    assert any(w in bad.lower() for w in LANG["en"]["banned"])


def test_en_arrow_in_text_is_caught():
    bad = LANG["en"]["html"].replace(">Email me</a>", ">Email me →</a>", 1)
    assert "→" in "".join(parse(bad).text)
