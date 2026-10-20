"""R15 dev-03 (H-20): bấm nút thì cả ly (thân, vạch trà, đá, ống hút) dịch nguyên khối."""

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_site_motion import REDUCE, SITE, needs_chrome, needs_net, read

from scripts import screenshot as sh

PAGES = [("/index.html", "vi"), ("/en/index.html", "en")]
PAGE_IDS = [p[1] for p in PAGES]

# Thân ly, vạch trà, hai viên đá, ống hút: chọn theo vị trí trong svg ban, không theo nhóm.
PARTS_JS = """
function parts() {
  var ban = document.querySelector('#hero .ban');
  var q = function (s) { return ban.querySelector(s); };
  var da = ban.querySelectorAll('rect.da');
  var tra = q('path[d="M188 162H216"]'), ong = q('path[d="M208 148L224 120"]');
  return {
    than: q('path.ly'), tra: tra, da1: da[0], da2: da[1], ong: ong
  };
}
function rects() {
  var p = parts(), o = {};
  Object.keys(p).forEach(function (k) {
    var r = p[k].getBoundingClientRect();
    o[k] = [r.left, r.top];
  });
  return o;
}
"""

CLICK = (
    "<script>"
    + PARTS_JS
    + """
setTimeout(function () {
  var b = document.getElementById('luoi-nut'), r = {};
  gsap.globalTimeline.time(gsap.globalTimeline.time() + 5);  // chốt tween vào trang
  setTimeout(function () {
  r.r0 = rects();
  b.click();
  gsap.globalTimeline.time(gsap.globalTimeline.time() + 2);
  setTimeout(function () {
    r.r1 = rects();
    b.click();
    gsap.globalTimeline.time(gsap.globalTimeline.time() + 2);
    setTimeout(function () {
      gsap.getTweensOf(document.querySelector('#hero .ly-tra')).forEach(function (t) {
        t.progress(1);  // ticker Chrome headless đứng yên: chốt nốt tween chiều về
      });
      r.r2 = rects();
      document.getElementById('out').textContent = JSON.stringify(r);
    }, 300);
  }, 300);
  }, 300);
}, 1200);
</script><pre id="out"></pre>
"""
)

# Reduced-motion: không đẩy timeline, đo ngay sau click đồng bộ.
CLICK_INSTANT = (
    "<script>"
    + PARTS_JS
    + """
setTimeout(function () {
  var b = document.getElementById('luoi-nut'), r = {};
  r.r0 = rects();
  b.click();
  r.r1 = rects();
  document.getElementById('out').textContent = JSON.stringify(r);
}, 1500);
</script><pre id="out"></pre>
"""
)

FILL_JS = (
    "<script>"
    + PARTS_JS
    + """
setTimeout(function () {
  var p = parts(), r = {};
  Object.keys(p).forEach(function (k) { r[k] = getComputedStyle(p[k]).fill; });
  r.tuong = getComputedStyle(document.documentElement)
    .getPropertyValue('--color-tuong-voi').trim();
  r.group = !!document.querySelector('#hero svg g.ly-tra');
  r.members = document.querySelector('#hero svg g.ly-tra')
    ? Array.prototype.map.call(
        document.querySelectorAll('#hero svg g.ly-tra *'),
        function (e) { return e.getAttribute('class') || e.getAttribute('d'); })
    : [];
  document.getElementById('out').textContent = JSON.stringify(r);
}, 800);
</script><pre id="out"></pre>
"""
)


def run(tmp_path, entry, script, edit=lambda h: h):
    site = tmp_path / "site"
    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    page = site / entry.lstrip("/")
    page.write_text(edit(page.read_text(encoding="utf-8")).replace("</body>", script + "</body>"),
                    encoding="utf-8")
    with sh.serve(site) as base:
        return read(sh.dump_dom(base + entry, 1280, 800, "light"))


def deltas(a, b):
    return {k: (b[k][0] - a[k][0], b[k][1] - a[k][1]) for k in a}


def check_block(r0, r1, tol=0.5):
    """Trả danh sách lỗi: 5 phần phải dịch cùng một dy khác 0, dx ≈ 0."""
    d = deltas(r0, r1)
    errs = []
    dy = d["than"][1]
    if abs(dy) <= tol:
        errs.append("thân ly không dịch")
    for k, (dx, dyk) in d.items():
        if abs(dx) > tol:
            errs.append(f"{k} lệch dx={dx}")
        if abs(dyk - dy) > tol:
            errs.append(f"{k} dy={dyk} khác thân ly dy={dy}")
    return errs


def make(than=0.0, other=0.0):
    base = {"than": [10.0, 100.0], "tra": [10.0, 110.0], "da1": [11.0, 105.0],
            "da2": [12.0, 106.0], "ong": [20.0, 90.0]}
    moved = {k: [v[0], v[1] + (than if k == "than" else other)] for k, v in base.items()}
    return base, moved


def test_checker_accepts_block_move():
    r0, r1 = make(-8, -8)
    assert check_block(r0, r1) == []


def test_checker_negative_only_glass_body_moves():
    r0, r1 = make(than=-8, other=0)
    errs = check_block(r0, r1)
    assert errs and any("da1" in e for e in errs)


def test_checker_negative_nothing_moves():
    r0, r1 = make(0, 0)
    assert "thân ly không dịch" in check_block(r0, r1)


@needs_chrome
@needs_net
@pytest.mark.parametrize("entry", [p[0] for p in PAGES], ids=PAGE_IDS)
def test_cup_moves_as_one_block(tmp_path, entry):
    for _ in range(2):  # gọi lặp lại, không rò trạng thái
        r = run(tmp_path, entry, CLICK)
        assert check_block(r["r0"], r["r1"]) == []
        assert deltas(r["r0"], r["r1"])["than"][1] < 0
        back = deltas(r["r0"], r["r2"])
        for k, (dx, dy) in back.items():
            assert abs(dx) <= 0.5 and abs(dy) <= 0.5, k


@needs_chrome
@needs_net
@pytest.mark.parametrize("entry", [p[0] for p in PAGES], ids=PAGE_IDS)
def test_cup_negative_only_ly_path_moves(tmp_path, entry):
    """Ca âm trên trang thật: main.js cũ chỉ dịch path.ly thì phép đo phải bắt được."""
    orig = (SITE / "main.js").read_text(encoding="utf-8")
    bad = orig.replace('document.querySelector("#hero .ly-tra")', 'document.querySelector("#hero path.ly")')
    assert bad != orig, "main.js phải chọn nhóm #hero .ly-tra"
    site = tmp_path / "site"
    if site.exists():
        shutil.rmtree(site)
    shutil.copytree(SITE, site)
    (site / "main.js").write_text(bad, encoding="utf-8")
    page = site / entry.lstrip("/")
    page.write_text(page.read_text(encoding="utf-8").replace("</body>", CLICK + "</body>"),
                    encoding="utf-8")
    with sh.serve(site) as base:
        r = read(sh.dump_dom(base + entry, 1280, 800, "light"))
    assert check_block(r["r0"], r["r1"]) != []


@needs_chrome
@pytest.mark.parametrize("entry", [p[0] for p in PAGES], ids=PAGE_IDS)
def test_cup_group_keeps_fills(tmp_path, entry):
    r = run(tmp_path, entry, FILL_JS)
    assert r["group"], "thiếu g.ly-tra trong hero SVG"
    assert len(r["members"]) == 5
    assert r["da1"] == r["da2"] == "rgb(242, 245, 240)"  # --color-tuong-voi sáng #F2F5F0
    assert r["tuong"].lower() == "#f2f5f0"
    assert r["tra"] == "none" and r["ong"] == "none"
    assert r["than"] != "none"


@needs_chrome
@needs_net
@pytest.mark.parametrize("entry", [p[0] for p in PAGES], ids=PAGE_IDS)
def test_cup_reduced_motion_block_instant(tmp_path, entry):
    def edit(h):
        return h.replace('<script src="https://cdn', REDUCE + '<script src="https://cdn', 1)

    d = run(tmp_path, entry, CLICK_INSTANT, edit)
    assert check_block(d["r0"], d["r1"]) == []
    assert json.dumps(d)  # đo ngay sau click, không đẩy timeline: đã ở vị trí mới
