import functools
import http.server
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent.parent / "site"


@pytest.fixture
def base_url():
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(SITE)
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_index_served(base_url):
    with urllib.request.urlopen(base_url + "/", timeout=5) as r:
        assert r.status == 200
        assert "Lười Code Studio" in r.read().decode("utf-8")


def test_style_css_served(base_url):
    with urllib.request.urlopen(base_url + "/style.css", timeout=5) as r:
        assert r.status == 200
        assert r.headers["Content-Type"].startswith("text/css")


def test_missing_path_is_404(base_url):
    with pytest.raises(urllib.error.HTTPError) as exc:
        urllib.request.urlopen(base_url + "/khong-co.html", timeout=5)
    assert exc.value.code == 404
