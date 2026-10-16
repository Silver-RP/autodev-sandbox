import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts import screenshot as sh

try:
    sh.chrome_path()
    HAVE_CHROME = True
except RuntimeError:
    HAVE_CHROME = False

needs_chrome = pytest.mark.skipif(not HAVE_CHROME, reason="không có Chrome")

SAMPLE = """<!doctype html><meta charset=utf-8><title>t</title>
<body><pre id="out"></pre>
<script>
document.getElementById('out').textContent = JSON.stringify({
  innerWidth: window.innerWidth,
  dark: window.matchMedia('(prefers-color-scheme: dark)').matches});
</script></body>"""


@pytest.fixture
def sample_site(tmp_path):
    (tmp_path / "index.html").write_text(SAMPLE, encoding="utf-8")
    return tmp_path


def measure(site, width, mode):
    with sh.serve(site) as base:
        url = sh.page_url(base, "/index.html", width, 600)
        dom = sh.dump_dom(url, width, 600, mode)
    ids = "frame-out" if width < 1000 else "out"
    m = re.search(rf'<pre id="{ids}">(.*?)</pre>', dom, re.DOTALL)
    assert m, dom
    text = m.group(1).replace("&quot;", '"')
    return json.loads(text)


def test_png_size_rejects_non_png(tmp_path):
    p = tmp_path / "x.png"
    p.write_bytes(b"hello world, definitely not a png file")
    with pytest.raises(ValueError):
        sh.png_size(p)
    empty = tmp_path / "e.png"
    empty.write_bytes(b"")
    with pytest.raises(ValueError):
        sh.png_size(empty)


@needs_chrome
def test_four_pngs_with_exact_widths(sample_site, tmp_path, capsys):
    out = tmp_path / "shots"
    assert sh.main(["--site", str(sample_site), "--out", str(out)]) == 0
    printed = capsys.readouterr().out.split()
    assert len(printed) == 4
    for w in (360, 1280):
        for m in ("light", "dark"):
            assert sh.png_size(out / f"{w}-{m}.png")[0] == w
    # gọi lặp lại: ghi đè, vẫn đúng
    assert sh.main(["--site", str(sample_site), "--out", str(out), "--widths", "360", "--modes", "dark"]) == 0
    assert sh.png_size(out / "360-dark.png")[0] == 360


@needs_chrome
def test_360_viewport_inside_iframe_is_360(sample_site):
    assert measure(sample_site, 360, "light")["innerWidth"] == 360
    assert measure(sample_site, 1280, "light")["innerWidth"] == 1280


@needs_chrome
@pytest.mark.parametrize("width", [360, 1280])
def test_dark_mode_applied_only_in_dark(sample_site, width):
    assert measure(sample_site, width, "dark")["dark"] is True
    assert measure(sample_site, width, "light")["dark"] is False


def test_chrome_path_env_and_missing(monkeypatch):
    monkeypatch.setenv("CHROME", "/custom/chrome")
    assert sh.chrome_path() == "/custom/chrome"
    monkeypatch.delenv("CHROME")
    monkeypatch.setattr(sh.os.path, "exists", lambda p: False)
    monkeypatch.setattr(sh.shutil, "which", lambda n: None)
    with pytest.raises(RuntimeError):
        sh.chrome_path()


def test_default_main_rejects_bad_mode(sample_site, tmp_path):
    with pytest.raises(SystemExit):
        sh.main(["--site", str(sample_site), "--out", str(tmp_path), "--modes", "blue"])


# ---- page_metrics (dev-02) ----
from scripts import page_metrics as pm

METRIC_OK = """<!doctype html><meta charset=utf-8><title>t</title>
<style>h1{font-size:48px;font-family:Georgia,serif}body{font-family:Arial,sans-serif;margin:0}</style>
<body><section id="hero"><h1>Hi</h1><svg width="10" height="10"></svg><svg width="10" height="10"></svg></section>
<section id="b"><p>text</p></section></body>"""

METRIC_WIDE = """<!doctype html><meta charset=utf-8><title>t</title>
<style>body{overflow-x:hidden;margin:0}</style>
<body><div id="wide" style="width:600px">x</div></body>"""


def _site(tmp_path, content):
    d = tmp_path / "s"
    d.mkdir()
    (d / "index.html").write_text(content, encoding="utf-8")
    return d


@needs_chrome
def test_metrics_svg_h1_font_and_repeat(tmp_path):
    site = _site(tmp_path, METRIC_OK)
    for _ in range(2):
        res = pm.collect(site, [360, 1280], ["light", "dark"])
        assert len(res) == 4
        for r in res:
            assert r["svg_by_section"] == {"hero": 2, "b": 0}
            assert r["h1"]["font_size"] == 48
            assert "Georgia" in r["h1"]["font_family"]
            assert "Arial" in r["body_font"]
            assert r["overflow"] == []
            assert r["colors"]
        assert [r["innerWidth"] for r in res] == [360, 360, 1280, 1280]


@needs_chrome
def test_metrics_overflow_caught_despite_overflow_hidden(tmp_path, capsys):
    site = _site(tmp_path, METRIC_WIDE)
    res = pm.collect(site, [360], ["light"])
    assert "div#wide" in res[0]["overflow"]
    assert pm.main(["--site", str(site), "--check-overflow"]) == 1


@needs_chrome
def test_metrics_no_overflow_exit_0(tmp_path, capsys):
    site = _site(tmp_path, METRIC_OK)
    assert pm.main(["--site", str(site), "--check-overflow"]) == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 4
    assert all(json.loads(ln)["width"] in (360, 1280) for ln in lines)


# ---- contrast (R8/dev-01) ----
from scripts import contrast as ct


def _page(style, body):
    return f"<!doctype html><meta charset=utf-8><title>t</title><style>{style}</style><body>{body}</body>"


def test_contrast_ratio_known_values():
    assert ct.ratio("#000", "#fff") == pytest.approx(21)
    assert ct.ratio("#777", "#fff") == pytest.approx(4.48, abs=0.01)
    assert ct.ratio("rgb(255, 255, 255)", "rgb(0, 0, 0)") == pytest.approx(21)


def test_contrast_thresholds_pure():
    assert ct.threshold(24, 400) == 3.0
    assert ct.threshold(19, 700) == 3.0
    assert ct.threshold(19, 400) == 4.5
    assert ct.threshold(16, 700) == 4.5
    mid = [{"width": 1, "mode": "light", "colors": [
        {"color": "#777", "background": "#fff", "font_size": 16, "font_weight": 400},
        {"color": "#777", "background": "#fff", "font_size": 24, "font_weight": 400}]}]
    assert len(ct.failures(mid)) == 1
    assert ct.failures([]) == []


@needs_chrome
def test_contrast_low_contrast_page_fails(tmp_path, capsys):
    site = _site(tmp_path, _page("body{background:#888;color:#777;margin:0}", "<p>xin chao</p>"))
    assert ct.main(["--site", str(site), "--modes", "light"]) == 1
    assert "p" in capsys.readouterr().out


@needs_chrome
def test_contrast_transparent_block_uses_ancestor_bg(tmp_path):
    site = _site(tmp_path, _page(
        "body{background:#fff;margin:0}div{background:transparent;color:#eee}",
        "<div><p>chu sang</p></div>"))
    assert ct.main(["--site", str(site), "--modes", "light"]) == 1


@needs_chrome
def test_contrast_good_page_passes_and_repeatable(tmp_path):
    site = _site(tmp_path, _page("body{background:#fff;color:#111;margin:0}", "<p>ok</p>"))
    for _ in range(2):
        assert ct.main(["--site", str(site), "--modes", "light"]) == 0


@needs_chrome
def test_contrast_large_text_uses_3_to_1(tmp_path):
    css = "body{background:#fff;margin:0}p{color:#777}"
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    small = _site(tmp_path / "a", _page(css + "p{font-size:16px}", "<p>nho</p>"))
    large = _site(tmp_path / "b", _page(css + "p{font-size:24px}", "<p>lon</p>"))
    assert ct.main(["--site", str(small), "--modes", "light"]) == 1
    assert ct.main(["--site", str(large), "--modes", "light"]) == 0


def test_shot_prefix_and_default_pages(tmp_path):
    from scripts import page_metrics as pm2
    from scripts import screenshot as sh2

    assert sh2.shot_prefix("/index.html") == ""
    assert sh2.shot_prefix("/en/index.html") == "en-"
    assert sh2.shot_prefix("/en/") == "en-"
    assert pm2.default_pages(tmp_path) == ["/index.html"]  # rỗng -> mặc định
    (tmp_path / "index.html").write_text("x")
    (tmp_path / "en").mkdir()
    (tmp_path / "en" / "index.html").write_text("x")
    assert pm2.default_pages(tmp_path) == ["/index.html", "/en/index.html"]
