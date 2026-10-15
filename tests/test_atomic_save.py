import os

import pytest

from todo import store


def test_failed_save_keeps_old_file_and_leaves_no_temp(tmp_path, monkeypatch):
    path = tmp_path / "todo.json"
    store.add(path, "cu")
    before = path.read_text(encoding="utf-8")

    def boom(*_):
        raise OSError("giả lập chết giữa chừng")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        store.add(path, "moi")

    assert path.read_text(encoding="utf-8") == before
    assert [p.name for p in tmp_path.iterdir()] == ["todo.json"]


def test_save_leaves_only_target_file(tmp_path):
    path = tmp_path / "todo.json"
    store.add(path, "a")
    store.add(path, "b")
    assert [p.name for p in tmp_path.iterdir()] == ["todo.json"]
    assert [i["title"] for i in store.load(path)] == ["a", "b"]


def test_save_keeps_normal_file_mode(tmp_path):
    path = tmp_path / "todo.json"
    umask = os.umask(0o022)
    try:
        store.add(path, "a")
    finally:
        os.umask(umask)
    assert path.stat().st_mode & 0o777 == 0o644
