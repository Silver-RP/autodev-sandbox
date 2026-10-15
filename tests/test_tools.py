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
