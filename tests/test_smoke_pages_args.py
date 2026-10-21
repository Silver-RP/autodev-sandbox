import functools
import http.server
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

from scripts import smoke_pages

SITE = Path(__file__).resolve().parent.parent / "site"


@pytest.mark.parametrize(
    "argv",
    [
        ["--url", "foo", "--sha", "x"],
        ["--url", "ftp://h/", "--sha", "x"],
        ["--url", "http://", "--sha", "x"],
        ["--sha", "x", "--interval", "-1"],
        ["--sha", "x", "--retries", "0"],
        ["--sha", "x", "--retries", "-1"],
    ],
)
def test_tham_so_sai_exit_2(argv, monkeypatch, capsys):
    def no_net(*a, **k):
        raise AssertionError("không được gọi mạng")

    monkeypatch.setattr(smoke_pages, "fetch", no_net)
    monkeypatch.setattr(smoke_pages, "_git", no_net)
    assert smoke_pages.main(argv) == 2
    err = capsys.readouterr().err
    assert "Lỗi:" in err
    assert "Traceback" not in err


def test_interval_0_hop_le(monkeypatch):
    monkeypatch.setattr(smoke_pages, "check_content", lambda u, s: [])
    assert smoke_pages.main(["--sha", "x", "--interval", "0"]) == 0


def test_incomplete_read_thu_lai(tmp_path, capsys):
    d = tmp_path / "site"
    shutil.copytree(SITE, d)
    idx = d / "index.html"
    idx.write_text(
        idx.read_text(encoding="utf-8").replace(
            'name="version" content="dev"', 'name="version" content="abc123"'
        ),
        encoding="utf-8",
    )
    count = {"n": 0}
    base = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(d)
    )

    class H(base.func):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(d), **k)

        def log_message(self, *a, **k):
            pass

        def do_GET(self):
            count["n"] += 1
            if count["n"] == 1:
                self.send_response(200)
                self.send_header("Content-Length", "100000")
                self.end_headers()
                self.wfile.write(b"ngan")
                self.wfile.flush()
                self.close_connection = True
                return
            super().do_GET()

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/"
        rc = smoke_pages.main(
            ["--url", url, "--sha", "abc123", "--retries", "2",
             "--interval", "0"]
        )
    finally:
        server.shutdown()
        server.server_close()
    assert rc == 0
    assert "Traceback" not in capsys.readouterr().err


def test_git_timeout_exit_2(monkeypatch, capsys):
    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="git", timeout=1)

    monkeypatch.setattr(subprocess, "run", boom)
    assert smoke_pages.main(["--url", "http://127.0.0.1:9/"]) == 2
    err = capsys.readouterr().err
    assert "Lỗi:" in err and "timeout" in err.lower()
    assert "Traceback" not in err


def test_git_kwargs_timeout_va_env(monkeypatch):
    seen = {}

    def fake(cmd, **kw):
        seen.update(kw)
        return subprocess.CompletedProcess(cmd, 0, stdout="abc\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake)
    assert smoke_pages._git("rev-parse", "HEAD") == "abc"
    assert seen["timeout"] > 0
    assert seen["env"]["GIT_TERMINAL_PROMPT"] == "0"
    # gọi lặp không rò trạng thái
    seen.clear()
    smoke_pages._git("rev-parse", "HEAD")
    assert seen["env"]["GIT_TERMINAL_PROMPT"] == "0"
