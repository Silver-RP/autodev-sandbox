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
