import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_site_motion import (
    CSS,
    HTML,
    JS,
    REDUCE,
    needs_chrome,
    needs_net,
    probe,
    read,
)


class Buttons(HTMLParser):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.hero_depth = False

    def handle_starttag(self, tag, attrs):
        if tag == "button":
            self.buttons.append(dict(attrs))


def buttons(src):
    p = Buttons()
    p.feed(src)
    return p.buttons


def test_exactly_one_button_with_type():
    b = buttons(HTML)
    assert len(b) == 1
    assert b[0].get("type") == "button"
    assert b[0].get("aria-pressed") == "false"


def test_button_in_hero_and_hidden_without_js():
    b = buttons(HTML)[0]
    assert "hidden" in b  # không JS: ẩn, không là nút chết
    hero = re.search(r'<section id="hero">.*?</section>', HTML, re.DOTALL).group(0)
    assert "<button" in hero
    assert "hidden = false" in JS or "removeAttribute(\"hidden\")" in JS


def test_hidden_button_stays_hidden_in_css():
    assert re.search(r"button\.nut\[hidden\]\s*\{[^}]*display\s*:\s*none", CSS)


def test_buttons_detector_negative():
    assert buttons("<p>x</p>") == []
    assert len(buttons("<button>a</button><button type=button>b</button>")) == 2


def test_focus_visible_has_outline():
    rules = re.findall(r"([^{}]*:focus-visible[^{}]*)\{([^{}]*)\}", CSS)
    assert rules
    ok = [
        r for _, r in rules
        if re.search(r"outline\s*:\s*(?!none|0\b)[^;]+", r)
        or re.search(r"outline-style\s*:\s*(?!none)", r)
    ]
    assert ok


def test_only_one_timeline_still():
    assert len(re.findall(r"gsap\.timeline\(", JS)) == 1


CLICK = """<script>
setTimeout(function () {
  var b = document.getElementById('luoi-nut'), r = {};
  r.hidden0 = b.hidden;
  r.p0 = b.getAttribute('aria-pressed'); r.t0 = b.textContent;
  b.click();
  r.p1 = b.getAttribute('aria-pressed'); r.t1 = b.textContent;
  b.click();
  r.p2 = b.getAttribute('aria-pressed'); r.t2 = b.textContent;
  b.click();
  r.p3 = b.getAttribute('aria-pressed');
  gsap.globalTimeline.time(gsap.globalTimeline.time() + 2);  // ticker Chrome headless đứng yên
  setTimeout(function () {
    r.xanh = document.querySelector('#hero .ghe-xanh').getAttribute('style') || '';
    document.getElementById('out').textContent = JSON.stringify(r);
  }, 900);
}, 1500);
</script><pre id="out"></pre>
"""


@needs_chrome
@needs_net
def test_click_toggles_aria_pressed(tmp_path):
    for _ in range(2):  # gọi lặp lại, không rò trạng thái
        d = read(probe(tmp_path, lambda h: h.replace("</body>", CLICK + "</body>")))
        if d["hidden0"]:
            raise AssertionError("gsap không nạp hoặc JS không bỏ hidden")
        assert (d["p0"], d["p1"], d["p2"], d["p3"]) == ("false", "true", "false", "true")
        assert d["t0"] != d["t1"] and d["t2"] == d["t0"]
        assert "translate" in d["xanh"] or "matrix" in d["xanh"]


@needs_chrome
@needs_net
def test_click_reduced_motion_instant(tmp_path):
    def edit(h):
        h = h.replace('<script src="https://cdn', REDUCE + '<script src="https://cdn', 1)
        return h.replace("</body>", CLICK + "</body>")

    d = read(probe(tmp_path, edit))
    assert d["hidden0"] is False
    assert d["p1"] == "true"
