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
