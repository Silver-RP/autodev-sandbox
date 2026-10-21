import functools
import http.server
import re
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

from scripts import lh_check, smoke_pages

GOOD = {"performance": 99, "accessibility": 100, "best-practices": 100, "seo": 100,
        "total-byte-weight": 1000}


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
                        "PATH": __import__("os").environ["PATH"],
                        "HOME": str(cwd)})


def test_lh_missing_index_exit2(tmp_path, capsys):
    calls = []
    rc = lh_check.main(["--site", str(tmp_path)],
                       runner=lambda *a, **k: calls.append(1) or GOOD)
    assert rc == 2 and calls == []
    assert "index.html" in capsys.readouterr().err


def test_lh_missing_index_with_pages_exit2(tmp_path):
    calls = []
    rc = lh_check.main(["--site", str(tmp_path), "--pages", "/"],
                       runner=lambda *a, **k: calls.append(1) or GOOD)
    assert rc == 2 and calls == []


def test_lh_site_not_exists(tmp_path, capsys):
    rc = lh_check.main(["--site", str(tmp_path / "nope")], runner=lambda *a, **k: GOOD)
    err = capsys.readouterr().err
    assert rc == 2 and "Traceback" not in err and err.startswith("Lỗi:")


def test_lh_site_is_file(tmp_path):
    f = tmp_path / "f"
    f.write_text("x")
    assert lh_check.main(["--site", str(f)], runner=lambda *a, **k: GOOD) == 2


def test_lh_ok_with_index(tmp_path):
    (tmp_path / "index.html").write_text("<html></html>")
    assert lh_check.main(["--site", str(tmp_path)], runner=lambda *a, **k: GOOD) == 0


def test_git_sha_fetches_first(tmp_path, monkeypatch):
    bare = tmp_path / "remote.git"
    work = tmp_path / "work"
    other = tmp_path / "other"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)], check=True,
                   capture_output=True)
    for d in (work, other):
        d.mkdir()
        _git(d, "init", "-b", "main")
        _git(d, "remote", "add", "origin", str(bare))
    (work / "a").write_text("1")
    _git(work, "add", "a")
    _git(work, "commit", "-m", "c1")
    _git(work, "push", "origin", "main")
    _git(work, "fetch", "origin", "main")
    _git(other, "pull", "origin", "main")
    (other / "a").write_text("2")
    _git(other, "commit", "-am", "c2")
    _git(other, "push", "origin", "main")
    new = subprocess.run(["git", "rev-parse", "HEAD"], cwd=other, capture_output=True,
                         text=True, check=True).stdout.strip()
    monkeypatch.chdir(work)
    assert smoke_pages.git_sha() == new


def _rev(cwd, ref="HEAD"):
    return subprocess.run(["git", "rev-parse", ref], cwd=cwd, capture_output=True,
                          text=True, check=True).stdout.strip()


def _bare_and_work(tmp_path):
    bare = tmp_path / "remote.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "--bare", "-b", "main", str(bare)], check=True,
                   capture_output=True)
    work.mkdir()
    _git(work, "init", "-b", "main")
    _git(work, "remote", "add", "origin", str(bare))
    (work / "a").write_text("1")
    _git(work, "add", "a")
    _git(work, "commit", "-m", "c1")
    _git(work, "push", "origin", "main")
    return bare, work


def _push_new_commit(work, text):
    (work / "a").write_text(text)
    _git(work, "commit", "-am", text)
    _git(work, "push", "origin", "main")
    return _rev(work)


class Site:
    """Server cục bộ phục vụ bản sao của site/ với version đặt được."""

    def __init__(self, tmp_path, sha):
        self.dir = tmp_path / "srv"
        shutil.copytree(Path(__file__).resolve().parent.parent / "site", self.dir)
        handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                    directory=str(self.dir))
        handler.log_message = lambda *a, **k: None
        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}/"
        self.set_sha(sha)

    def set_sha(self, sha, en=None):
        for rel, v in (("index.html", sha), ("en/index.html", en or sha)):
            f = self.dir / rel
            text = f.read_text(encoding="utf-8")
            text = re.sub(r'(name="version" content=")[^"]*', rf"\g<1>{v}", text)
            f.write_text(text, encoding="utf-8")

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def test_sha_recomputed_each_attempt_passes_when_site_catches_up(tmp_path, monkeypatch):
    _bare, work = _bare_and_work(tmp_path)
    old = _rev(work)
    site = Site(tmp_path, old)
    monkeypatch.chdir(work)
    state = {"n": 0}

    def fake_sleep(_):
        state["n"] += 1
        new = _push_new_commit(work, "2")
        site.set_sha(new)

    monkeypatch.setattr(smoke_pages.time, "sleep", fake_sleep)
    try:
        site.set_sha("cu-hon")  # lần 1 trượt; sau sleep main đi tiếp, trang bắt kịp
        rc = smoke_pages.main(["--url", site.url, "--retries", "3", "--interval", "0"])
    finally:
        site.close()
    assert rc == 0 and state["n"] == 1


def test_stale_deploy_not_accepted_when_main_moves_on(tmp_path, monkeypatch):
    _bare, work = _bare_and_work(tmp_path)
    site = Site(tmp_path, _rev(work))  # server giữ SHA ban đầu
    monkeypatch.chdir(work)
    _push_new_commit(work, "1b")  # main đi tiếp, server vẫn giữ SHA ban đầu
    n = iter(range(2, 100))
    monkeypatch.setattr(smoke_pages.time, "sleep",
                        lambda _: _push_new_commit(work, str(next(n))))
    try:
        rc = smoke_pages.main(["--url", site.url, "--retries", "3", "--interval", "0"])
    finally:
        site.close()
    assert rc == 1


def test_initial_sha_site_not_ok_after_main_advances(tmp_path, monkeypatch):
    _bare, work = _bare_and_work(tmp_path)
    initial = _rev(work)
    site = Site(tmp_path, initial)
    monkeypatch.chdir(work)
    _push_new_commit(work, "2")  # main đi tiếp trước khi smoke chạy
    try:
        rc = smoke_pages.main(["--url", site.url, "--retries", "2", "--interval", "0"])
    finally:
        site.close()
    assert rc == 1


def test_git_sha_single_branch_clone_other_branch(tmp_path, monkeypatch):
    bare, work = _bare_and_work(tmp_path)
    _git(work, "branch", "khac")
    _git(work, "push", "origin", "khac")
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "--single-branch", "--branch", "khac",
                    str(bare), str(clone)], check=True, capture_output=True)
    new = _push_new_commit(work, "2")
    monkeypatch.chdir(clone)
    assert smoke_pages.git_sha() == new
    assert smoke_pages.git_sha() == new  # gọi lặp vẫn đúng


@pytest.mark.parametrize("missing", ["main.js", "robots.txt", "sitemap.xml"])
def test_missing_resource_reported(tmp_path, missing):
    site = Site(tmp_path, "abc")
    try:
        assert smoke_pages.check_content(site.url, "abc") == []
        (site.dir / missing).unlink()
        errors = smoke_pages.check_content(site.url, "abc")
        assert len(errors) == 1 and missing in errors[0]
        assert smoke_pages.main(["--url", site.url, "--sha", "abc",
                                 "--retries", "1", "--interval", "0"]) == 1
    finally:
        site.close()


def test_en_version_mismatch_or_missing(tmp_path):
    site = Site(tmp_path, "abc")
    try:
        assert smoke_pages.check_content(site.url, "abc") == []
        site.set_sha("abc", en="khac")
        errors = smoke_pages.check_content(site.url, "abc")
        assert errors and all("en/" in e for e in errors)
        en = site.dir / "en" / "index.html"
        en.write_text(re.sub(r'<meta name="version"[^>]*>', "",
                             en.read_text(encoding="utf-8")), encoding="utf-8")
        errors = smoke_pages.check_content(site.url, "abc")
        assert errors and all("en/" in e for e in errors)
    finally:
        site.close()


def test_main_not_a_repo_exit2(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
    rc = smoke_pages.main(["--url", "http://127.0.0.1:9/", "--retries", "1"])
    err = capsys.readouterr().err
    assert rc == 2 and err.startswith("Lỗi:") and "Traceback" not in err


def test_main_no_git_binary(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("PATH", str(tmp_path))
    rc = smoke_pages.main(["--url", "http://127.0.0.1:9/", "--retries", "1"])
    assert rc == 2 and capsys.readouterr().err.startswith("Lỗi:")


def test_sha_given_no_git(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("gọi git")

    monkeypatch.setattr(smoke_pages.subprocess, "run", boom)
    monkeypatch.setattr(smoke_pages, "check_content", lambda url, sha: [])
    assert smoke_pages.main(["--url", "http://x/", "--sha", "abc"]) == 0
