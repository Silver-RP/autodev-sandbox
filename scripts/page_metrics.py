"""Đo số liệu trang qua Chrome headless: tràn ngang, SVG theo section, font, màu."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import screenshot as sh

ROOT = sh.ROOT
PAGE = "/index.html"

MEASURE_JS = r"""
<pre id="out" style="display:none"></pre>
<script>
window.addEventListener('load', function () {
  function sel(e) {
    var s = e.tagName.toLowerCase();
    if (e.id) s += '#' + e.id;
    if (typeof e.className === 'string' && e.className.trim())
      s += '.' + e.className.trim().split(/\s+/).join('.');
    return s;
  }
  function bg(e) {
    for (; e; e = e.parentElement) {
      var c = getComputedStyle(e).backgroundColor;
      if (c && c !== 'transparent' && !/rgba\(\s*\d+,\s*\d+,\s*\d+,\s*0\s*\)/.test(c)) return c;
    }
    return 'rgb(255, 255, 255)';
  }
  var iw = window.innerWidth, overflow = [], svg = {}, colors = {};
  var all = document.querySelectorAll('body, body *');
  for (var i = 0; i < all.length; i++) {
    var e = all[i];
    if (e.id === 'out') continue;
    var r = e.getBoundingClientRect();
    if (r.width > 0 && r.right > iw + 1) overflow.push(sel(e));
    var cs = getComputedStyle(e);
    var own = '';
    for (var n = e.firstChild; n; n = n.nextSibling)
      if (n.nodeType === 3) own += n.nodeValue;
    if (own.trim() && cs.display !== 'none') {
      var k = cs.color + '|' + bg(e);
      colors[k] = {color: cs.color, background: bg(e)};
    }
  }
  document.querySelectorAll('section[id]').forEach(function (s) {
    svg[s.id] = s.querySelectorAll('svg').length;
  });
  var h1 = document.querySelector('h1'), h = null;
  if (h1) {
    var hs = getComputedStyle(h1);
    h = {font_family: hs.fontFamily, font_size: parseFloat(hs.fontSize)};
  }
  document.getElementById('out').textContent = JSON.stringify({
    innerWidth: iw,
    scrollWidth: document.documentElement.scrollWidth,
    overflow: overflow,
    svg_by_section: svg,
    h1: h,
    body_font: getComputedStyle(document.body).fontFamily,
    colors: Object.keys(colors).map(function (k) { return colors[k]; })
  });
});
</script>
"""


def inject(page_html: str) -> str:
    m = list(re.finditer(r"</body\s*>", page_html, re.IGNORECASE))
    if m:
        i = m[-1].start()
        return page_html[:i] + MEASURE_JS + page_html[i:]
    return page_html + MEASURE_JS


def measure(base: str, width: int, mode: str, height: int = 800) -> dict:
    dom = sh.dump_dom(sh.page_url(base, PAGE, width, height), width, height, mode)
    pid = "frame-out" if width < 1000 else "out"
    m = re.search(rf'<pre id="{pid}"[^>]*>(.*?)</pre>', dom, re.DOTALL)
    if not m or not m.group(1).strip():
        raise RuntimeError(f"không đọc được số liệu ở {width}/{mode}")
    data = json.loads(html.unescape(m.group(1)))
    return {"width": width, "mode": mode, **data}


def collect(site, widths, modes, height: int = 800) -> list[dict]:
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / "site"
        shutil.copytree(site, copy)
        page = copy / PAGE.lstrip("/")
        page.write_text(inject(page.read_text(encoding="utf-8")), encoding="utf-8")
        with sh.serve(copy) as base:
            for w in widths:
                for mode in modes:
                    results.append(measure(base, w, mode, height))
    return results


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--site", default=str(ROOT / "site"))
    ap.add_argument("--widths", default="360,1280")
    ap.add_argument("--modes", default="light,dark")
    ap.add_argument("--check-overflow", action="store_true")
    a = ap.parse_args(argv)
    widths = [int(w) for w in a.widths.split(",") if w]
    modes = [m for m in a.modes.split(",") if m]
    for m in modes:
        if m not in ("light", "dark"):
            ap.error(f"chế độ không hợp lệ: {m}")
    results = collect(a.site, widths, modes)
    for r in results:
        print(json.dumps(r, ensure_ascii=False))
    if a.check_overflow:
        bad = [r for r in results if r["overflow"]]
        for r in bad:
            print(f"TRÀN {r['width']}/{r['mode']}: {', '.join(r['overflow'])}", file=sys.stderr)
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
