import fcntl
import multiprocessing
import os

import pytest

from todo import cli, store


def _probe(path):
    """Thử lấy khoá độc quyền qua fd mới mở; True nếu lấy được."""
    fd = os.open(store.lock_path(path), os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except BlockingIOError:
        return False
    finally:
        os.close(fd)


def _make_link(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    box = tmp_path / "box"
    box.mkdir()
    link = box / "link.json"
    link.symlink_to(real / "todo.json")
    return link, real, box


def test_add_through_symlink_keeps_link(tmp_path):
    link, real, box = _make_link(tmp_path)
    target = os.readlink(link)
    store.add(link, "a")
    store.add(link, "b")
    assert link.is_symlink()
    assert os.readlink(link) == target
    assert [i["title"] for i in store.load(real / "todo.json")] == ["a", "b"]
    assert [p.name for p in box.iterdir()] == ["link.json"]
    assert [p.name for p in real.iterdir()] == ["todo.json"]


def test_cli_done_and_due_through_symlink(tmp_path, monkeypatch):
    link, real, box = _make_link(tmp_path)
    monkeypatch.setenv("TODO_FILE", str(link))
    assert cli.main(["add", "a"]) == 0
    assert cli.main(["due", "1", "2026-10-20"]) == 0
    assert cli.main(["done", "1"]) == 0
    assert link.is_symlink()
    (item,) = store.load(real / "todo.json")
    assert item["done"] is True and item["due"] == "2026-10-20"
    assert [p.name for p in box.iterdir()] == ["link.json"]


def _worker(path, tag, barrier, n):
    barrier.wait()
    for k in range(n):
        store.add(path, f"{tag}-{k}")


def test_two_processes_add_in_parallel(tmp_path):
    path = tmp_path / "todo.json"
    ctx = multiprocessing.get_context("fork")
    barrier = ctx.Barrier(2)
    procs = [ctx.Process(target=_worker, args=(path, t, barrier, 20)) for t in "ab"]
    for p in procs:
        p.start()
    for p in procs:
        p.join(60)
        assert p.exitcode == 0
    items = store.load(path)
    assert len(items) == 40
    assert sorted(i["id"] for i in items) == list(range(1, 41))
    assert len({i["title"] for i in items}) == 40


def _spy_load(monkeypatch, path, seen):
    real_load = store.load

    def spy(p):
        seen.append(_probe(path))
        return real_load(p)

    monkeypatch.setattr(store, "load", spy)


def test_mutators_hold_lock_during_load(tmp_path, monkeypatch):
    path = tmp_path / "todo.json"
    store.add(path, "x")
    seen = []
    _spy_load(monkeypatch, path, seen)
    store.add(path, "y")
    store.set_due(path, 1, "2026-10-20")
    store.complete(path, 1)
    store.complete(path, 99)
    store.set_due(path, 99, "2026-10-20")
    assert seen == [False] * 5


def test_load_alone_does_not_lock(tmp_path, monkeypatch):
    path = tmp_path / "todo.json"
    store.add(path, "x")
    seen = []
    _spy_load(monkeypatch, path, seen)
    store.load(path)
    assert seen == [True]


def test_lock_released_after_error(tmp_path):
    path = tmp_path / "todo.json"
    path.write_text("{hỏng", encoding="utf-8")
    with pytest.raises(store.StoreError):
        store.add(path, "a")
    assert _probe(path) is True


def _holder(path, held, release):
    with store.lock(path):
        held.set()
        release.wait(30)


def _hold(tmp_path):
    ctx = multiprocessing.get_context("fork")
    held, release = ctx.Event(), ctx.Event()
    p = ctx.Process(target=_holder, args=(tmp_path / "todo.json", held, release))
    p.start()
    assert held.wait(10)
    return p, release


def _stop(p, release):
    release.set()
    p.join(10)
    assert p.exitcode == 0


@pytest.mark.parametrize(
    "argv", [["add", "x"], ["done", "1"], ["due", "1", "2026-10-20"]], ids=["add", "done", "due"]
)
def test_lock_timeout_exit_2(tmp_path, monkeypatch, capsys, argv):
    import time

    path = tmp_path / "todo.json"
    store.add(path, "a")
    before = (path.read_bytes(), path.stat().st_mtime_ns)
    monkeypatch.setenv("TODO_FILE", str(path))
    monkeypatch.setenv("TODO_LOCK_TIMEOUT", "0.3")
    p, release = _hold(tmp_path)
    try:
        t0 = time.monotonic()
        code = cli.main(argv)
        elapsed = time.monotonic() - t0
    finally:
        _stop(p, release)
    err = capsys.readouterr()
    assert code == 2
    assert elapsed < 2
    assert err.out == ""
    assert "khoá" in err.err and str(tmp_path) in err.err
    assert "Traceback" not in err.err
    assert (path.read_bytes(), path.stat().st_mtime_ns) == before


@pytest.mark.parametrize("bad", ["abc", "-1", "0", "nan", "inf", ""])
def test_bad_lock_timeout_exit_2(tmp_path, monkeypatch, capsys, bad):
    path = tmp_path / "todo.json"
    monkeypatch.setenv("TODO_FILE", str(path))
    monkeypatch.setenv("TODO_LOCK_TIMEOUT", bad)
    assert cli.main(["add", "x"]) == 2
    err = capsys.readouterr()
    assert "TODO_LOCK_TIMEOUT" in err.err and "Traceback" not in err.err
    assert not path.exists()


def test_lock_waits_for_release(tmp_path, monkeypatch):
    import threading

    path = tmp_path / "todo.json"
    monkeypatch.setenv("TODO_FILE", str(path))
    monkeypatch.setenv("TODO_LOCK_TIMEOUT", "5")
    p, release = _hold(tmp_path)
    threading.Timer(0.3, release.set).start()
    try:
        assert cli.main(["add", "x"]) == 0
    finally:
        _stop(p, release)
    assert [i["title"] for i in store.load(path)] == ["x"]
    assert _probe(path) is True


def _selflink(tmp_path, kind):
    if kind == "self":
        a = tmp_path / "a"
        a.symlink_to("a")
        return a, [a]
    a, b = tmp_path / "a", tmp_path / "b"
    a.symlink_to("b")
    b.symlink_to("a")
    return a, [a, b]


@pytest.mark.parametrize("kind", ["self", "loop"])
@pytest.mark.parametrize("argv", [["add", "x"], ["list"], ["done", "1"]])
def test_self_symlink_exit_2(tmp_path, monkeypatch, capsys, kind, argv):
    a, links = _selflink(tmp_path, kind)
    targets = [os.readlink(x) for x in links]
    names = sorted(p.name for p in tmp_path.iterdir())
    monkeypatch.setenv("TODO_FILE", str(a))
    assert cli.main(argv) == 2
    cap = capsys.readouterr()
    assert cap.err.strip() and "Traceback" not in cap.err and cap.out == ""
    assert [os.readlink(x) for x in links] == targets
    assert sorted(p.name for p in tmp_path.iterdir()) == names


def test_unwritable_dir_and_long_name_exit_2(tmp_path, monkeypatch, capsys):
    p = tmp_path / ("n" * 300)
    monkeypatch.setenv("TODO_FILE", str(p))
    assert cli.main(["add", "x"]) == 2
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1 and "Traceback" not in err

    d = tmp_path / "ro"
    d.mkdir()
    (d / "todo.json").write_text("[]", encoding="utf-8")
    d.chmod(0o555)
    try:
        monkeypatch.setenv("TODO_FILE", str(d / "todo.json"))
        assert cli.main(["add", "x"]) == 2
        err = capsys.readouterr().err
        assert len(err.strip().splitlines()) == 1 and "Traceback" not in err
        assert (d / "todo.json").read_text(encoding="utf-8") == "[]"
    finally:
        d.chmod(0o755)
