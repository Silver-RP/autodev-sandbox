"""R16 dev-02 (H-24, H-29): đo tràn bằng scrollWidth; lỗi tham số exit 2."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_tools import needs_chrome

from scripts import contrast as ct
from scripts import page_metrics as pm

LONG = "x" * 300


def _site(tmp_path, body, style=""):
    s = tmp_path / "s"
    s.mkdir()
    (s / "index.html").write_text(
        f"<!doctype html><html><head><meta charset=utf-8><style>"
        f"body{{margin:0}}{style}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )
    return s


def _run(site, capsys, extra=()):
    code = pm.main(["--site", str(site), "--widths", "360", "--modes", "light",
                    "--check-overflow", *extra])
    return code, capsys.readouterr().err


@needs_chrome
def test_nowrap_text_in_clipped_box_is_overflow(tmp_path, capsys):
    body = ('<div style="width:100%;overflow:visible"><p id="nw" style="white-space:nowrap;'
            f'width:100%;margin:0">{"palavra " * 40}</p></div>')
    code, err = _run(_site(tmp_path, body), capsys)
    assert code == 1
    assert "TRÀN" in err and "p#nw" in err


@needs_chrome
def test_scroll_container_is_not_overflow(tmp_path, capsys):
    body = f'<div style="width:100%"><pre style="overflow-x:auto;margin:0">{LONG}</pre></div>'
    code, err = _run(_site(tmp_path, body), capsys)
    assert code == 0, err
    assert "TRÀN" not in err


@needs_chrome
def test_body_wider_than_viewport_reports(tmp_path, capsys):
    code, err = _run(_site(tmp_path, "<p>hi</p>", "body{width:400px}"), capsys)
    assert code == 1
    assert "html" in err or "body" in err


@needs_chrome
def test_repeat_calls_do_not_leak(tmp_path, capsys):
    s = _site(tmp_path, "<p>hi</p>")
    assert _run(s, capsys)[0] == 0
    assert _run(s, capsys)[0] == 0


@pytest.fixture
def site(tmp_path):
    s = tmp_path / "s"
    (s / "en").mkdir(parents=True)
    (s / "index.html").write_text("<html><body>x</body></html>")
    (s / "en" / "index.html").write_text("<html><body>x</body></html>")
    return s


@pytest.mark.parametrize("mod", [pm, ct], ids=["page_metrics", "contrast"])
@pytest.mark.parametrize("extra", [
    ["--widths", "abc"], ["--widths", "0"], ["--widths", "-5"], ["--widths", "360,x"],
    ["--pages", "../x"], ["--pages", "/../s/index.html"],
])
def test_bad_params_exit2(mod, extra, site, capsys):
    (site.parent / "x").write_text("x")
    code = mod.main(["--site", str(site), *extra])
    err = capsys.readouterr().err
    assert code == 2
    assert err.startswith("Lỗi:") and "Traceback" not in err


def test_normalize_pages_dir_without_slash(site):
    assert pm.normalize_pages(site, ["/en"]) == ["/en/index.html"]
    assert pm.normalize_pages(site, ["/en/"]) == ["/en/index.html"]
    assert pm.normalize_pages(site, ["/"]) == ["/index.html"]


def test_contrast_color_srgb_no_traceback():
    res = [{"page": "/", "width": 1, "mode": "light", "colors": [
        {"color": "color(srgb 1 0 0)", "background": "rgb(255, 255, 255)",
         "font_size": 16, "font_weight": 400, "selector": "p"}]}]
    out = ct.failures(res)
    assert len(out) == 1 and abs(out[0]["ratio"] - ct.ratio("rgb(255,0,0)", "rgb(255,255,255)")) < 0.01


def test_contrast_unreadable_color_main_exit2(monkeypatch, site, capsys):
    res = [{"page": "/", "width": 1, "mode": "light", "colors": [
        {"color": "lab(50 1 1)", "background": "#fff", "selector": "p"}]}]
    monkeypatch.setattr(ct.pm, "collect", lambda *a, **k: res)
    assert ct.main(["--site", str(site)]) == 2
    err = capsys.readouterr().err
    assert err.startswith("Lỗi: không đọc được màu") and "Traceback" not in err
