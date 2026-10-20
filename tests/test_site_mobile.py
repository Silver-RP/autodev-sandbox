"""R15 dev-01 (H-03): ở 360 giữ chấm dẫn menu và nút "Gửi thư" ở header."""

import html as htmllib
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from test_tools import needs_chrome

from scripts import page_metrics as pm
from scripts import screenshot as sh

SITE = Path(__file__).parent.parent / "site"
PAGES = ["/index.html", "/en/index.html"]
IDS = ["vi", "en"]

PROBE_JS = r"""
<pre id="out" style="display:none"></pre>
<script>
window.addEventListener('load', function () {
  function box(e) {
    var r = e.getBoundingClientRect(), cs = getComputedStyle(e);
    return {display: cs.display, width: r.width, height: r.height, top: r.top,
            left: r.left, right: r.right, line: parseFloat(cs.lineHeight) || r.height,
            border: cs.borderBottomStyle};
  }
  var cham = [];
  document.querySelectorAll('#dich-vu .mon-dong').forEach(function (row) {
    var c = row.querySelector('.cham'), g = row.querySelector('.gia');
    cham.push({cham: box(c), gia: box(g)});
  });
  var nut = document.querySelector('header a.nut');
  document.getElementById('out').textContent = JSON.stringify({
    rows: cham,
    nut: nut ? box(nut) : null,
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth
  });
});
</script>
"""


def probe(tmp_path, page, css_extra=""):
    site = tmp_path / "site"
    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    if css_extra:
        css = site / "style.css"
        css.write_text(css.read_text(encoding="utf-8") + "\n" + css_extra, encoding="utf-8")
    f = site / page.lstrip("/")
    h = f.read_text(encoding="utf-8")
    i = h.lower().rfind("</body>")
    f.write_text(h[:i] + PROBE_JS + h[i:], encoding="utf-8")
    with sh.serve(site) as base:
        dom = sh.dump_dom(sh.page_url(base, page, 360, 800), 360, 800, "light")
    m = re.search(r'<pre id="frame-out"[^>]*>(.*?)</pre>', dom, re.DOTALL)
    assert m and m.group(1).strip(), "không đọc được số đo"
    return json.loads(htmllib.unescape(m.group(1)))


def check_cham(data):
    assert data["rows"], "không có món nào"
    for row in data["rows"]:
        c, g = row["cham"], row["gia"]
        assert c["display"] != "none", "chấm dẫn bị ẩn"
        assert c["width"] >= 16, f"chấm dẫn quá hẹp: {c['width']}"
        assert c["border"] == "dotted", c["border"]
        assert abs(c["top"] - g["top"]) < g["line"], (c["top"], g["top"], g["line"])


def check_nut(data):
    n = data["nut"]
    assert n, "không có header a.nut"
    assert n["display"] != "none", "nút header bị ẩn"
    assert n["width"] > 0 and n["height"] > 0
    assert n["left"] >= 0 and n["right"] <= 360, (n["left"], n["right"])


@needs_chrome
@pytest.mark.parametrize("page", PAGES, ids=IDS)
def test_360_dotted_leader_same_row_as_price(tmp_path, page):
    check_cham(probe(tmp_path, page))


@needs_chrome
@pytest.mark.parametrize("page", PAGES, ids=IDS)
def test_360_header_button_visible_in_viewport(tmp_path, page):
    check_nut(probe(tmp_path, page))


@needs_chrome
@pytest.mark.parametrize("page", PAGES, ids=IDS)
def test_360_no_horizontal_scroll(tmp_path, page):
    d = probe(tmp_path, page)
    assert d["innerWidth"] == 360
    assert d["scrollWidth"] <= 360, d["scrollWidth"]


@needs_chrome
@pytest.mark.parametrize("page", PAGES, ids=IDS)
def test_negative_hidden_leader_is_caught(tmp_path, page):
    d = probe(tmp_path, page, "@media (max-width: 40rem){.cham{display:none}}")
    with pytest.raises(AssertionError):
        check_cham(d)


@needs_chrome
@pytest.mark.parametrize("page", PAGES, ids=IDS)
def test_negative_hidden_button_is_caught(tmp_path, page):
    d = probe(tmp_path, page, "@media (max-width: 40rem){header .nut{display:none}}")
    with pytest.raises(AssertionError):
        check_nut(d)


def test_page_metrics_default_pages_cover_both():
    assert pm.default_pages(SITE) == PAGES
