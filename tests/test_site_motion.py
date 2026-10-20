import base64
import hashlib
import html as htmllib
import json
import re
import shutil
import socket
import sys
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _policy import check

from scripts import screenshot as sh

SITE = Path(__file__).parent.parent / "site"
HTML = (SITE / "index.html").read_text(encoding="utf-8")
CSS = (SITE / "style.css").read_text(encoding="utf-8")
GSAP_TAG = re.search(r"<script[^>]*gsap[^>]*>", HTML).group(0)
GSAP_URL = re.search(r'src="([^"]+)"', GSAP_TAG).group(1)

# Bảng tham số theo trang (vi, en): tệp, mã HTML, đường dẫn main.js.
LANGS = ["vi", "en"]
PAGE_FILE = {"vi": "index.html", "en": "en/index.html"}
PAGE_HTML = {
    "vi": HTML,
    "en": (SITE / "en" / "index.html").read_text(encoding="utf-8"),
}
MAIN_SRC = {"vi": "main.js", "en": "../main.js"}

PROBE = """<pre id="out"></pre><script>
document.addEventListener('DOMContentLoaded', function () { setTimeout(function () {
  var s = document.querySelectorAll('section');
  document.getElementById('out').textContent = JSON.stringify({
    js: document.documentElement.classList.contains('js'),
    gsap: !!window.gsap,
    sections: s.length,
    opacity: Array.prototype.map.call(s, function (e) { return +getComputedStyle(e).opacity; })
  });
}, 300); });
</script>
"""


OFF_PAGE = """<!doctype html><meta charset=utf-8><body>
<iframe id="f" src="/@@PAGE@@" sandbox="allow-same-origin" width="1280" height="800"></iframe>
<pre id="out"></pre><script>
document.getElementById('f').addEventListener('load', function () {
  var d = this.contentDocument, s = d.querySelectorAll('section');
  document.getElementById('out').textContent = JSON.stringify({
    js: d.documentElement.classList.contains('js'),
    gsap: !!this.contentWindow.gsap,
    sections: s.length,
    opacity: Array.prototype.map.call(s, function (e) {
      return +this.contentWindow.getComputedStyle(e).opacity; }, this)
  });
});
</script>
"""


def _chrome():
    try:
        sh.chrome_path()
        return True
    except RuntimeError:
        return False


def _online():
    try:
        socket.create_connection(("cdn.jsdelivr.net", 443), timeout=3).close()
        return True
    except OSError:
        return False


needs_chrome = pytest.mark.skipif(not _chrome(), reason="không có Chrome")
needs_net = pytest.mark.skipif(not _online(), reason="không có mạng")


def probe(tmp_path, html_edit=lambda h: h, js_enabled=True, lang="vi"):
    site = tmp_path / "site"
    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    page = site / PAGE_FILE[lang]
    text = html_edit(page.read_text(encoding="utf-8"))
    if js_enabled:
        page.write_text(text.replace("</body>", PROBE + "</body>"), encoding="utf-8")
        entry = "/" + PAGE_FILE[lang]
    else:
        # iframe sandbox không có allow-scripts = tắt JS thật; trang cha (có JS) đo style
        page.write_text(text, encoding="utf-8")
        (site / "off.html").write_text(
            OFF_PAGE.replace("@@PAGE@@", PAGE_FILE[lang]), encoding="utf-8"
        )
        entry = "/off.html"
    with sh.serve(site) as base:
        return sh.dump_dom(base + entry, 1280, 800, "light")


def read(dom):
    m = re.search(r'<pre id="out"[^>]*>(.*?)</pre>', dom, re.DOTALL)
    assert m and m.group(1).strip(), "probe không chạy"
    return json.loads(htmllib.unescape(m.group(1)))


# --- SRI ---


def _gsap_tag(html):
    return re.search(r"<script[^>]*gsap[^>]*>", html).group(0)


@pytest.mark.parametrize("lang", LANGS)
def test_gsap_tag_attributes(lang):
    html = PAGE_HTML[lang]
    tag = _gsap_tag(html)
    url = re.search(r'src="([^"]+)"', tag).group(1)
    assert "crossorigin" in tag and "defer" in tag
    assert re.search(r'integrity="sha384-[A-Za-z0-9+/]{64}"', tag)
    assert re.search(r"gsap@\d+\.\d+\.\d+/", url)
    assert re.search(
        r'<script[^>]*src="' + re.escape(MAIN_SRC[lang]) + r'"[^>]*\bdefer\b', html
    )
    assert check(html=html) == []


@needs_net
@pytest.mark.parametrize("lang", LANGS)
def test_sri_hash_matches_cdn_file(lang):
    tag = _gsap_tag(PAGE_HTML[lang])
    url = re.search(r'src="([^"]+)"', tag).group(1)
    try:
        body = urllib.request.urlopen(url, timeout=15).read()
    except OSError:
        pytest.skip("không tải được CDN")
    digest = "sha384-" + base64.b64encode(hashlib.sha384(body).digest()).decode()
    assert digest in tag


def test_en_gsap_unpinned_version_is_caught():
    bad = PAGE_HTML["en"].replace("gsap@3.12.5", "gsap@latest")
    assert not re.search(r"gsap@\d+\.\d+\.\d+/", _gsap_tag(bad))


def test_en_gsap_without_sri_is_caught():
    bad = re.sub(r'\sintegrity="[^"]*"', "", PAGE_HTML["en"])
    assert not re.search(r'integrity="sha384-', _gsap_tag(bad))
    assert check(html=bad) != []


# --- làm nền tăng dần ---


def _hiding_rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    bad = []
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        hides = re.search(r"opacity\s*:\s*0(?:\.0+)?\s*(?:;|!|$)|visibility\s*:\s*hidden", body)
        if hides and not all(s.strip().startswith(".js") for s in sel.split(",")):
            bad.append(sel.strip())
    return bad


def test_css_hides_nothing_outside_js_selector():
    assert _hiding_rules(CSS) == []


def test_hiding_rules_detector_catches_violations():
    assert _hiding_rules("h1{opacity:0}") == ["h1"]
    assert _hiding_rules("a{visibility: hidden}") == ["a"]
    assert _hiding_rules(".js h1{opacity:0}") == []
    assert _hiding_rules(".js a, b{opacity:0}") == [".js a, b"]
    assert _hiding_rules("p{opacity:.5}") == []


def test_main_js_adds_js_class_only_with_gsap():
    js = (SITE / "main.js").read_text(encoding="utf-8")
    assert re.search(r"if\s*\(\s*!\s*window\.gsap\s*\)\s*return", js)
    assert 'classList.add("js")' in js


@needs_chrome
@pytest.mark.parametrize("lang", LANGS)
def test_js_disabled_sections_visible(tmp_path, lang):
    for _ in range(2):  # gọi lặp lại
        d = read(probe(tmp_path, js_enabled=False, lang=lang))
        assert d["js"] is False and d["gsap"] is False
        assert d["sections"] >= 4
        assert d["opacity"] == [1] * d["sections"]


@needs_chrome
@pytest.mark.parametrize("lang", LANGS)
def test_broken_cdn_sections_visible(tmp_path, lang):
    bad = lambda h: h.replace("gsap@3.12.5", "gsap@0.0.1")
    d = read(probe(tmp_path, bad, lang=lang))
    assert d["gsap"] is False and d["js"] is False
    assert d["sections"] >= 4
    assert d["opacity"] == [1] * d["sections"]


@needs_chrome
@needs_net
@pytest.mark.parametrize("lang", LANGS)
def test_with_cdn_gsap_present_and_sections_visible(tmp_path, lang):
    d = read(probe(tmp_path, lang=lang))
    if not d["gsap"]:
        pytest.skip("CDN không tải được")
    assert d["js"] is True
    assert d["opacity"] == [1] * d["sections"]


# --- dev-02: timeline lúc tải trang ---

JS = (SITE / "main.js").read_text(encoding="utf-8")

# Chrome --virtual-time-budget gần như không phát khung hình rAF nên ticker của gsap
# gần như đứng yên (đã đo: sau 2900ms tiến độ mới ~0,36). Probe vì vậy đẩy đồng hồ
# gsap thêm 2 giây (globalTimeline.time) rồi mới đo style thật mà gsap đã ghi.
HERO_PROBE = """<pre id="out"></pre><script>
function heroProbe() {
  var r = {gsap: !!window.gsap, tl: null, items: {}}, tries = 0;
  function finish() {
    if (window.gsap) gsap.globalTimeline.time(gsap.globalTimeline.time() + 2);
    if (window.lazySite) {
      r.should = window.lazySite.shouldAnimate();
      r.tl = !!window.lazySite.heroTimeline;
      if (window.lazySite.heroTimeline) { r.dur = window.lazySite.heroTimeline.duration(); r.prog = window.lazySite.heroTimeline.progress(); r.t = performance.now(); }
    } else if (window.gsap) {
      r.error = 'window.lazySite không có mặt sau khi chờ (main.js chưa chạy hoặc lỗi)';
    }
    ['#hero h1', '#hero .hero-hinh'].forEach(function (q) {
      var el = document.querySelector(q);
      if (!el) { r.error = r.error || 'thiếu phần tử ' + q; return; }
      var cs = getComputedStyle(el);
      r.items[q] = {opacity: +cs.opacity, transform: cs.transform};
    });
    document.getElementById('out').textContent = JSON.stringify(r);
  }
  // chờ có giới hạn (10 x 50ms, trong virtual-time-budget 3000) cho window.lazySite; gsap vắng thì không chờ
  (function wait() {
    if (window.lazySite || !window.gsap || ++tries > 10) return finish();
    setTimeout(wait, 50);
  })();
}
setTimeout(heroProbe, 2000);
</script>
"""

REDUCE = "<script>window.matchMedia = function (q) { return {matches: true, media: q}; };</script>"


def _code(js):
    return re.sub(r"//[^\n]*|/\*.*?\*/", "", js, flags=re.DOTALL)


def test_single_timeline_and_no_section_loop():
    code = _code(JS)
    assert len(re.findall(r"gsap\.timeline\(", code)) == 1
    assert not re.search(r"querySelectorAll\(\s*[\"']section", code)
    assert not re.search(r"gsap\.(from|to|set|fromTo)\(\s*[\"'][^\"']*section", code)
    assert not re.search(r"(forEach|for\s*\().*section", code)


def test_should_animate_defined_and_gated():
    code = _code(JS)
    assert "function shouldAnimate" in code
    assert "prefers-reduced-motion" in code
    assert re.search(r"shouldAnimate\(\)\s*\?\s*heroIntro\(\)\s*:\s*null", code)


def _identity(t):
    if t == "none":
        return True
    nums = [float(x) for x in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", t)]
    return t.startswith("matrix(") and nums[:4] == [1, 0, 0, 1] and nums[4:] == [0, 0]


def read_hero(dom):
    d = read(dom)
    assert "error" not in d, d["error"]
    return d


def test_identity_helper():
    assert _identity("none") and _identity("matrix(1, 0, 0, 1, 0, 0)")
    assert not _identity("matrix(1, 0, 0, 1, 0, 24)")


@needs_chrome
@needs_net
@pytest.mark.parametrize("lang", LANGS)
def test_hero_settled_after_2s(tmp_path, lang):
    for _ in range(2):
        d = read_hero(
            probe(tmp_path, lambda h: h.replace("</body>", HERO_PROBE + "</body>"), lang=lang)
        )
        assert d["gsap"] is True, "online mà gsap không nạp"
        assert d["should"] is True and d["tl"] is True
        assert d["dur"] <= 1.5
        for q, v in d["items"].items():
            assert v["opacity"] == 1, q
            assert _identity(v["transform"]), q


@needs_chrome
@needs_net
@pytest.mark.parametrize("lang", LANGS)
def test_reduced_motion_no_timeline(tmp_path, lang):
    def edit(h):
        h = h.replace("<script src=\"https://cdn", REDUCE + "<script src=\"https://cdn", 1)
        return h.replace("</body>", HERO_PROBE + "</body>")

    d = read_hero(probe(tmp_path, edit, lang=lang))
    assert d["gsap"] is True, "online mà gsap không nạp"
    assert d["should"] is False and d["tl"] is False
    for v in d["items"].values():
        assert v["opacity"] == 1 and _identity(v["transform"])


@needs_chrome
@needs_net
@pytest.mark.parametrize("lang", LANGS)
def test_probe_reports_missing_lazysite(tmp_path, lang):
    def edit(h):
        h = re.sub(r'<script[^>]*src="(?:\.\./)?main\.js"[^>]*></script>', "", h)
        return h.replace("</body>", HERO_PROBE + "</body>")

    dom = probe(tmp_path, edit, lang=lang)
    assert read(dom)["gsap"] is True, "online mà gsap không nạp"
    with pytest.raises(AssertionError, match="lazySite"):
        read_hero(dom)
