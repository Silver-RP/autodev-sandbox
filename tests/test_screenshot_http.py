"""screenshot.py kiểm HTTP trước khi chụp, lỗi tham số exit 2 (H-23, H-29)."""

import pytest

from scripts import screenshot as sh

try:
    sh.chrome_path()
    HAVE_CHROME = True
except RuntimeError:
    HAVE_CHROME = False

needs_chrome = pytest.mark.skipif(not HAVE_CHROME, reason="không có Chrome")

SVG = "<svg xmlns='http://www.w3.org/2000/svg' width='40' height='40'><rect width='40' height='40' fill='red'/></svg>"


@pytest.fixture
def site(tmp_path):
    d = tmp_path / "site"
    d.mkdir()
    (d / "index.html").write_text("<!doctype html><title>t</title><p>x</p>")
    (d / "og.svg").write_text(SVG)
    return d


@pytest.fixture
def no_chrome(monkeypatch):
    """Chrome giả: nếu bị gọi thì test đỏ (404 phải chặn trước khi chụp)."""

    def boom(*a, **k):
        raise AssertionError("không được chụp khi trang 404")

    monkeypatch.setattr(sh, "shoot", boom)


def test_site_pages_404_exit_2_khong_png(site, tmp_path, capsys, no_chrome):
    out = tmp_path / "o"
    rc = sh.main(["--site", str(site), "--pages", "/khong-co.html", "--out", str(out)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "HTTP 404" in err and "Traceback" not in err
    assert not list(out.glob("*.png")) if out.exists() else True


def test_site_pages_404_xoa_png_cu(site, tmp_path, no_chrome):
    out = tmp_path / "o"
    out.mkdir()
    cu = out / "khong-co.html-360-light.png"
    cu.write_bytes(b"cu")
    assert sh.main(["--site", str(site), "--pages", "/khong-co.html", "--out", str(out)]) == 2
    assert not cu.exists()


@pytest.mark.parametrize("mode", ["site", "url"])
def test_page_404_exit_2_khong_tao_file(site, tmp_path, capsys, no_chrome, mode):
    f = tmp_path / "x.png"
    f.write_bytes(b"cu")
    if mode == "site":
        argv = ["--site", str(site)]
        rc = sh.main(argv + ["--page", "/khong-co.svg", "--file", str(f)])
    else:
        with sh.serve(site) as base:
            rc = sh.main(["--url", base, "--page", "/khong-co.svg", "--file", str(f)])
    assert rc == 2
    assert "HTTP 404" in capsys.readouterr().err
    assert not f.exists()


@needs_chrome
def test_page_url_khong_ghi_source_sha(site, tmp_path):
    f = tmp_path / "og.png"
    with sh.serve(site) as base:
        assert sh.main(["--url", base, "--page", "/og.svg", "--size", "100x100", "--file", str(f)]) == 0
    assert "source-sha256" not in sh.png_text(f)


@needs_chrome
def test_page_site_ghi_source_sha(site, tmp_path):
    f = tmp_path / "og.png"
    assert sh.main(["--site", str(site), "--page", "/og.svg", "--size", "100x100", "--file", str(f)]) == 0
    assert sh.png_text(f)["source-sha256"] == sh.sha256_file(site / "og.svg")


@pytest.mark.parametrize(
    "extra",
    [
        ["--widths", "abc"],
        ["--widths", "0"],
        ["--widths", "-5"],
        ["--widths", ""],
        ["--height", "0"],
        ["--pages", "../x"],
        ["--pages", "/a/../../x"],
        ["--modes", "xanh"],
        ["--out", "FILE"],
    ],
)
def test_loi_tham_so_exit_2(site, tmp_path, capsys, no_chrome, extra):
    argv = ["--site", str(site)]
    for x in extra:
        if x == "FILE":
            f = tmp_path / "tep"
            f.write_text("x")
            x = str(f)
        argv.append(x)
    with pytest.raises(SystemExit) as e:
        rc = sh.main(argv)
        raise SystemExit(rc)
    assert e.value.code == 2
    err = capsys.readouterr().err
    assert "Traceback" not in err
    assert err.startswith(("Lỗi:", "usage:"))


def test_page_thoat_site_exit_2(site, tmp_path, capsys, no_chrome):
    with pytest.raises(SystemExit) as e:
        sh.main(["--site", str(site), "--page", "/../x", "--file", str(tmp_path / "a.png")])
    assert e.value.code == 2
