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
<iframe id="f" src="/index.html" sandbox="allow-same-origin" width="1280" height="800"></iframe>
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


def probe(tmp_path, html_edit=lambda h: h, js_enabled=True):
    site = tmp_path / "site"
    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    page = site / "index.html"
    text = html_edit(page.read_text(encoding="utf-8"))
    if js_enabled:
        page.write_text(text.replace("</body>", PROBE + "</body>"), encoding="utf-8")
        entry = "/index.html"
    else:
        # iframe sandbox không có allow-scripts = tắt JS thật; trang cha (có JS) đo style
        page.write_text(text, encoding="utf-8")
        (site / "off.html").write_text(OFF_PAGE, encoding="utf-8")
        entry = "/off.html"
    with sh.serve(site) as base:
        return sh.dump_dom(base + entry, 1280, 800, "light")


def read(dom):
    m = re.search(r'<pre id="out"[^>]*>(.*?)</pre>', dom, re.DOTALL)
    assert m and m.group(1).strip(), "probe không chạy"
    return json.loads(htmllib.unescape(m.group(1)))


# --- SRI ---


def test_gsap_tag_attributes():
    assert "crossorigin" in GSAP_TAG and "defer" in GSAP_TAG
    assert re.search(r'integrity="sha384-[A-Za-z0-9+/]{64}"', GSAP_TAG)
    assert re.search(r"gsap@\d+\.\d+\.\d+/", GSAP_URL)
    assert re.search(r'<script[^>]*src="main\.js"[^>]*\bdefer\b', HTML)
    assert check(html=HTML) == []


@needs_net
def test_sri_hash_matches_cdn_file():
    try:
        body = urllib.request.urlopen(GSAP_URL, timeout=15).read()
    except OSError:
        pytest.skip("không tải được CDN")
    digest = "sha384-" + base64.b64encode(hashlib.sha384(body).digest()).decode()
    assert digest in GSAP_TAG


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
def test_js_disabled_sections_visible(tmp_path):
    for _ in range(2):  # gọi lặp lại
        d = read(probe(tmp_path, js_enabled=False))
        assert d["js"] is False and d["gsap"] is False
        assert d["sections"] == 4
        assert d["opacity"] == [1, 1, 1, 1]


@needs_chrome
def test_broken_cdn_sections_visible(tmp_path):
    bad = lambda h: h.replace("gsap@3.12.5", "gsap@0.0.1")
    d = read(probe(tmp_path, bad))
    assert d["gsap"] is False and d["js"] is False
    assert d["sections"] == 4
    assert d["opacity"] == [1, 1, 1, 1]


@needs_chrome
@needs_net
def test_with_cdn_gsap_present_and_sections_visible(tmp_path):
    d = read(probe(tmp_path))
    if not d["gsap"]:
        pytest.skip("CDN không tải được")
    assert d["js"] is True
    assert d["opacity"] == [1, 1, 1, 1]
