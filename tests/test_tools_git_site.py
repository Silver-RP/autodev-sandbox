import subprocess

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
