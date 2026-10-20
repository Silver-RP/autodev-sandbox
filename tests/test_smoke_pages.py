import functools
import http.server
import shutil
import threading
from pathlib import Path

import pytest

from scripts import smoke_pages

SITE = Path(__file__).resolve().parent.parent / "site"


def _serve(directory):
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(directory)
    )
    handler.log_message = lambda *a, **k: None
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


@pytest.fixture
def make_site(tmp_path):
    servers = []

    def make(remove_og=False):
        d = tmp_path / f"site{len(servers)}"
        shutil.copytree(SITE, d)
        idx = d / "index.html"
        idx.write_text(
            idx.read_text(encoding="utf-8").replace(
                'name="version" content="dev"', 'name="version" content="abc123"'
            ),
            encoding="utf-8",
        )
        if remove_og:
            (d / "og.png").unlink()
        s = _serve(d)
        servers.append(s)
        return f"http://127.0.0.1:{s.server_port}/"

    yield make
    for s in servers:
        s.shutdown()
        s.server_close()


def _run(url, sha):
    return smoke_pages.main(
        ["--url", url, "--sha", sha, "--retries", "2", "--interval", "0"]
    )


def test_matching_sha_passes(make_site):
    assert _run(make_site(), "abc123") == 0


def test_wrong_sha_fails(make_site):
    assert _run(make_site(), "khac") == 1


def test_missing_og_png_fails(make_site):
    assert _run(make_site(remove_og=True), "abc123") == 1


def test_repeated_calls_do_not_leak_state(make_site):
    url = make_site()
    assert _run(url, "khac") == 1
    assert _run(url, "abc123") == 0


def test_check_content_lists_errors(make_site):
    assert smoke_pages.check_content(make_site(), "abc123") == []
    assert smoke_pages.check_content(make_site(remove_og=True), "abc123")


def test_url_without_trailing_slash(make_site):
    assert smoke_pages.check_content(make_site().rstrip("/"), "abc123") == []


def test_unreachable_server_fails():
    assert _run("http://127.0.0.1:1/", "abc123") == 1
