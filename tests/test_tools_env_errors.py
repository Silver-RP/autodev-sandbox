"""R19 dev-01: công cụ đo lỗi môi trường/danh sách rỗng -> exit 2, không Traceback (H-43, H-44)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_tools import needs_chrome

from scripts import contrast as ct
from scripts import page_metrics as pm
from scripts import screenshot as sh

PAGE_OK = "<!doctype html><meta charset=utf-8><title>t</title><body><p>xin chao</p></body>"


@pytest.fixture
def site(tmp_path):
    s = tmp_path / "s"
    s.mkdir()
    (s / "index.html").write_text(PAGE_OK, encoding="utf-8")
    (s / "og.svg").write_text("<svg xmlns='http://www.w3.org/2000/svg'/>")
    return s


def _clean(capsys, rc, want=2):
    err = capsys.readouterr().err
    assert rc == want
    assert "Traceback" not in err
    return err


@pytest.mark.parametrize("extra", [["--modes", ""], ["--pages", ""], ["--pages", ","]])
def test_screenshot_danh_sach_rong_exit_2(site, tmp_path, capsys, extra):
    out = tmp_path / "o"
    rc = sh.main(["--site", str(site), "--out", str(out), *extra])
    err = _clean(capsys, rc)
    assert err.startswith("Lỗi:")
    assert not out.exists() or not list(out.glob("*.png"))


@pytest.mark.parametrize("mod", [sh, pm, ct], ids=["screenshot", "page_metrics", "contrast"])
def test_chrome_khong_co_exit_2(mod, site, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("CHROME", str(tmp_path / "khong-co"))
    argv = ["--site", str(site), "--widths", "1280", "--modes", "light"]
    if mod is sh:
        argv += ["--out", str(tmp_path / "o")]
    rc = mod.main(argv)
    err = _clean(capsys, rc)
    assert err.startswith("Lỗi:")


def test_screenshot_file_duoi_tep_exit_2(site, tmp_path, capsys):
    tep = tmp_path / "tep.txt"
    tep.write_text("x")
    rc = sh.main(["--site", str(site), "--page", "/og.svg", "--file", str(tep / "x.png")])
    assert _clean(capsys, rc).startswith("Lỗi:")


def test_screenshot_file_la_thu_muc_exit_2(site, tmp_path, capsys):
    d = tmp_path / "dir"
    d.mkdir()
    rc = sh.main(["--site", str(site), "--page", "/og.svg", "--file", str(d)])
    assert _clean(capsys, rc).startswith("Lỗi:")


def test_screenshot_out_duoi_tep_exit_2(site, tmp_path, capsys):
    tep = tmp_path / "tep.txt"
    tep.write_text("x")
    rc = sh.main(["--site", str(site), "--out", str(tep / "sub"), "--widths", "1280",
                  "--modes", "light"])
    assert _clean(capsys, rc).startswith("Lỗi:")


def test_screenshot_url_khong_scheme_exit_2(tmp_path, capsys):
    rc = sh.main(["--url", "foo", "--out", str(tmp_path / "o")])
    assert _clean(capsys, rc).startswith("Lỗi:")


@pytest.mark.parametrize("dom", ['<pre id="out">{hỏng</pre>', '<pre id="out">\udcff\ud800{</pre>'])
@pytest.mark.parametrize("mod", [pm, ct], ids=["page_metrics", "contrast"])
def test_dom_hong_exit_2_nen_ten_trang(mod, dom, site, monkeypatch, capsys):
    monkeypatch.setattr(sh, "dump_dom", lambda *a, **k: dom)
    rc = mod.main(["--site", str(site), "--widths", "1280", "--modes", "light"])
    err = _clean(capsys, rc)
    assert err.startswith("Lỗi:")
    assert "/index.html" in err and "1280" in err and "light" in err


def test_goi_lap_khong_ro_trang_thai(site, tmp_path, capsys):
    for _ in range(2):
        rc = sh.main(["--site", str(site), "--pages", ",", "--out", str(tmp_path / "o")])
        _clean(capsys, rc)


def _site_with(tmp_path, body, style=""):
    s = tmp_path / "s2"
    s.mkdir()
    (s / "index.html").write_text(
        f"<!doctype html><meta charset=utf-8><title>t</title><style>{style}</style>"
        f"<body>{body}</body>", encoding="utf-8")
    return s


@needs_chrome
def test_trang_tran_ngang_van_exit_1(tmp_path, capsys):
    s = _site_with(tmp_path, "<div style='width:2000px;height:20px;background:red'>x</div>")
    rc = pm.main(["--site", str(s), "--widths", "360", "--modes", "light", "--check-overflow"])
    assert _clean(capsys, rc, want=1)


@needs_chrome
def test_tuong_phan_thap_van_exit_1(tmp_path, capsys):
    s = _site_with(tmp_path, "<p>chu kho doc</p>",
                   "body{background:#888;color:#777;margin:0}")
    rc = ct.main(["--site", str(s), "--modes", "light"])
    capsys.readouterr()
    assert rc == 1


def test_screenshot_docstring_co_bang_ma_thoat():
    doc = sh.__doc__
    for k in ("0 =", "1 =", "2 ="):
        assert k in doc
