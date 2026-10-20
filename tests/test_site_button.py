import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest
from test_site_motion import (
    CSS,
    JS,
    LANGS,
    PAGE_HTML,
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


@pytest.mark.parametrize("lang", LANGS)
def test_exactly_one_button_with_type(lang):
    b = buttons(PAGE_HTML[lang])
    assert len(b) == 1
    assert b[0].get("type") == "button"
    assert b[0].get("aria-pressed") == "false"


@pytest.mark.parametrize("lang", LANGS)
def test_button_in_hero_and_hidden_without_js(lang):
    html = PAGE_HTML[lang]
    b = buttons(html)[0]
    assert "hidden" in b  # không JS: ẩn, không là nút chết
    hero = re.search(r'<section id="hero">.*?</section>', html, re.DOTALL).group(0)
    assert "<button" in hero
    assert "hidden = false" in JS or "removeAttribute(\"hidden\")" in JS


def test_hidden_button_stays_hidden_in_css():
    assert re.search(r"button\.nut\[hidden\]\s*\{[^}]*display\s*:\s*none", CSS)


def test_buttons_detector_negative():
    assert buttons("<p>x</p>") == []
    assert len(buttons("<button>a</button><button type=button>b</button>")) == 2


def test_en_button_without_type_or_hidden_is_caught():
    bad = PAGE_HTML["en"].replace(' type="button"', "", 1).replace(" hidden>", ">", 1)
    b = buttons(bad)[0]
    assert b.get("type") != "button" and "hidden" not in b


def test_en_second_button_is_caught():
    bad = PAGE_HTML["en"].replace("</header>", "<button>x</button></header>", 1)
    assert len(buttons(bad)) == 2


def test_en_button_moved_out_of_hero_is_caught():
    html = PAGE_HTML["en"]
    btn = re.search(r"<button.*?</button>", html, re.DOTALL).group(0)
    bad = html.replace(btn, "", 1).replace("</main>", btn + "</main>", 1)
    hero = re.search(r'<section id="hero">.*?</section>', bad, re.DOTALL).group(0)
    assert "<button" not in hero


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
@pytest.mark.parametrize("lang", LANGS)
def test_click_toggles_aria_pressed(tmp_path, lang):
    for _ in range(2):  # gọi lặp lại, không rò trạng thái
        d = read(probe(tmp_path, lambda h: h.replace("</body>", CLICK + "</body>"), lang=lang))
        if d["hidden0"]:
            raise AssertionError("gsap không nạp hoặc JS không bỏ hidden")
        assert (d["p0"], d["p1"], d["p2"], d["p3"]) == ("false", "true", "false", "true")
        assert d["t0"] != d["t1"] and d["t2"] == d["t0"]
        assert "translate" in d["xanh"] or "matrix" in d["xanh"]


@needs_chrome
@needs_net
@pytest.mark.parametrize("lang", LANGS)
def test_click_reduced_motion_instant(tmp_path, lang):
    def edit(h):
        h = h.replace('<script src="https://cdn', REDUCE + '<script src="https://cdn', 1)
        return h.replace("</body>", CLICK + "</body>")

    d = read(probe(tmp_path, edit, lang=lang))
    assert d["hidden0"] is False
    assert d["p1"] == "true"
