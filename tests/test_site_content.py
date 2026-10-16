import re
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
HTML = (SITE / "index.html").read_text(encoding="utf-8")
CSS = (SITE / "style.css").read_text(encoding="utf-8")
VERBS = ("Gửi", "Nhắn", "Viết")


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


def test_mailto_buttons_hero_and_contact_start_with_verb():
    links = parse(HTML).mailto
    assert len(links) >= 2
    sections = {s for s, _ in links}
    assert {"hero", "lien-he"} <= sections
    for _, text in links:
        assert text.startswith(VERBS), text


def test_mailto_detection_negative():
    assert parse("<p>không có link</p>").mailto == []
    assert parse('<a href="https://x.vn">Gửi</a>').mailto == []


def test_no_arrow_in_visible_text():
    assert "→" not in "".join(parse(HTML).text)


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


def test_faq_has_at_least_four_details_with_summary_and_body():
    items = faq(HTML)
    assert len(items) >= 4
    for q, a in items:
        assert q, "summary rỗng"
        assert len(a) >= 30, (q, a)


def test_faq_parser_negative():
    assert faq("<section id='x'><details><summary>a</summary>b</details></section>") == []
    got = faq("<section id='hoi-dap'><details><summary>a</summary>bb</details></section>")
    assert got == [("a", "bb")]
    assert faq("<section id='hoi-dap'><details><summary></summary>bb</details></section>")[0][0] == ""


def test_faq_is_between_cach_lam_and_lien_he():
    ids = re.findall(r'<section id="([^"]+)"', HTML)
    assert ids.index("cach-lam") < ids.index("hoi-dap") < ids.index("lien-he")


def test_css_does_not_hide_summary():
    for m in re.finditer(r"([^{}]*summary[^{}]*)\{([^}]*)\}", CSS):
        body = m.group(2)
        assert not re.search(r"display\s*:\s*none|visibility\s*:\s*hidden", body), m.group(0)
