"""screenshot.py --url dưới đường con (H-16)."""

import functools
import http.server
import threading
from pathlib import Path

import pytest

from scripts import screenshot as sh

SITE = Path(__file__).resolve().parent.parent / "site"
PREFIX = "/autodev-sandbox/"


def test_page_url_giu_duong_con():
    base = "https://x.github.io/autodev-sandbox/"
    assert sh.page_url(base, "/index.html", 1280, 800) == base + "index.html"
    assert sh.page_url(base, "/en/", 1280, 800) == base + "en/"
    assert sh.page_url(base.rstrip("/"), "en/index.html", 1280, 800) == base + "en/index.html"


def test_page_url_nho_khong_dung_frame_va_khong_ve_goc():
    base = "https://x.github.io/autodev-sandbox/"
    u = sh.page_url(base, "/index.html", 360, 800)
    assert "__frame__" not in u
    assert u.startswith("data:text/html")
    assert "https%3A%2F%2Fx.github.io%2Fautodev-sandbox%2Findex.html" in u


def test_page_url_noi_bo_van_dung_frame():
    u = sh.page_url("http://127.0.0.1:1234", "/index.html", 360, 800)
    assert u.startswith("http://127.0.0.1:1234/__frame__.html?src=")


def test_frame_html_escape():
    h = sh.frame_html('/a"><script>x</script>', 360, 800)
    assert '"><script>x' not in h.split("<pre")[0]
    assert "&quot;" in h


@pytest.fixture
def subpath_server():
    class H(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            if not path.startswith(PREFIX):
                return str(SITE / "__khong_co__")
            return super().translate_path("/" + path[len(PREFIX):])

        def log_message(self, *a):
            pass

    srv = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(H, directory=str(SITE))
    )
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_port}{PREFIX}"
    srv.shutdown()
    srv.server_close()
    t.join(timeout=5)


def test_url_360_chup_duoc(subpath_server, tmp_path):
    rc = sh.main(["--url", subpath_server, "--widths", "360", "--modes", "light", "--out", str(tmp_path)])
    assert rc == 0
    png = tmp_path / "360-light.png"
    assert png.exists()
    assert sh.png_size(png)[0] == 360


def test_url_1280_chup_duoc_lap_lai(subpath_server, tmp_path):
    for _ in range(2):
        assert sh.main(["--url", subpath_server, "--widths", "1280", "--modes", "light", "--out", str(tmp_path)]) == 0


def test_trang_thieu_exit_khac_0(subpath_server, tmp_path):
    rc = sh.main(["--url", subpath_server, "--pages", "/khong-co.html", "--widths", "360",
                  "--modes", "light", "--out", str(tmp_path)])
    assert rc != 0
    assert not list(tmp_path.glob("*.png"))
