import re
from html.parser import HTMLParser
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
HTML = (SITE / "index.html").read_text(encoding="utf-8")
CSS = (SITE / "style.css").read_text(encoding="utf-8")
DRAW = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}


class Sections(HTMLParser):
    def __init__(self, sid):
        super().__init__()
        self.sid = sid
        self.on = False
        self.in_svg = 0
        self.svgs = []
        self.ol_items = 0
        self.in_ol = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "section":
            self.on = a.get("id") == self.sid
        if not self.on:
            return
        if tag == "svg":
            self.svgs.append({"attrs": a, "draw": 0, "title": False})
            self.in_svg += 1
        elif self.in_svg and tag in DRAW:
            self.svgs[-1]["draw"] += 1
        elif self.in_svg and tag == "title":
            self.svgs[-1]["title"] = True
        elif tag == "ol":
            self.in_ol = True
        elif tag == "li" and self.in_ol:
            self.ol_items += 1

    def handle_endtag(self, tag):
        if tag == "svg" and self.on:
            self.in_svg -= 1
        if tag == "ol":
            self.in_ol = False
        if tag == "section":
            self.on = False


def parse(sid):
    p = Sections(sid)
    p.feed(HTML)
    return p


def rule(selector):
    css = re.sub(r"/\*.*?\*/", "", CSS, flags=re.DOTALL)
    bodies = [
        m.group(2)
        for m in re.finditer(r"([^{}@]+)\{([^{}]*)\}", css)
        if selector in [s.strip() for s in m.group(1).split(",")]
    ]
    return "\n".join(bodies)


def test_menu_has_three_icons_with_enough_shapes():
    svgs = parse("dich-vu").svgs
    assert len(svgs) >= 3
    for s in svgs:
        assert s["draw"] >= 3
        assert s["title"] or s["attrs"].get("aria-hidden") == "true"


def test_menu_items_have_name_leader_and_price():
    for cls in ("ten", "cham", "gia"):
        assert len(re.findall(rf'class="[^"]*\b{cls}\b', HTML)) >= 3, cls


def test_menu_is_single_board_with_3px_border_6px_radius():
    body = rule("#dich-vu ul")
    assert re.search(r"border:\s*3px solid var\(--color-muc-bang\)", body)
    assert re.search(r"border-radius:\s*6px", body)


def test_price_is_red_and_leader_is_dotted():
    assert "var(--color-ghe-do)" in rule(".gia")
    assert "dotted" in rule(".cham")


def test_menu_items_not_separate_shadow_cards():
    body = rule("#dich-vu li")
    assert "box-shadow" not in body
    assert "box-shadow" not in CSS


def test_steps_are_three_numbered_in_tra_da_circle():
    assert parse("cach-lam").ol_items == 3
    body = rule("#cach-lam li::before")
    assert "counter(" in body
    assert "var(--color-tra-da)" in body
    assert "border-radius: 50%" in body


def test_mobile_price_wraps_below_name():
    assert re.search(r"@media[^{]*max-width[^{]*\{[^@]*\.gia", CSS) or "flex-wrap: wrap" in rule(
        ".mon-dong"
    )
